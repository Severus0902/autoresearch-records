from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import assert_remote_safety, load_config, output_root
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl
from idea1_kgr.memory_store import MemoryStore
from idea1_kgr.schemas import ActionCandidate


SYSTEM_PROMPT = (
    "You are a knowledge-graph reasoning action selector. "
    "Choose exactly one relation_id from the candidate relations. "
    "Return compact JSON only."
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def ensure_run_dir(root: Path, run_name: str) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = root / "runs" / f"{run_name}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def load_sft_rows(path: Path, max_rows: int) -> List[Dict[str, object]]:
    rows = list(iter_jsonl(path))
    if max_rows and max_rows > 0:
        rows = rows[:max_rows]
    return rows


def action_json(relation_id: str) -> str:
    return json.dumps({"relation_id": relation_id}, ensure_ascii=False)


def compact_candidates(
    candidate_relations: Sequence[str],
    required_relations: Iterable[str],
    max_candidates: int,
) -> List[str]:
    seen = set()
    compact: List[str] = []
    for relation in candidate_relations:
        if relation and relation not in seen:
            compact.append(relation)
            seen.add(relation)
        if len(compact) >= max_candidates:
            break
    for relation in required_relations:
        if relation and relation not in seen:
            if len(compact) >= max_candidates and compact:
                compact[-1] = relation
            else:
                compact.append(relation)
            seen.add(relation)
    return compact


def format_action_prompt(
    question: str,
    seed_entities: object,
    memory_relations: Sequence[str],
    candidate_relations: Sequence[str],
) -> str:
    candidate_text = "\n".join(f"{idx}. {rel}" for idx, rel in enumerate(candidate_relations))
    return (
        f"Question: {question}\n"
        f"Seed entities: {json.dumps(seed_entities, ensure_ascii=False)}\n"
        f"Verified memory relations: {json.dumps(list(memory_relations), ensure_ascii=False)}\n"
        f"Candidate relations:\n{candidate_text}\n\n"
        "Select the best next-hop relation for graph traversal. Return JSON with key relation_id."
    )


def render_prompt(tokenizer, messages: List[Dict[str, str]]) -> str:
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    parts = []
    for message in messages:
        parts.append(f"{message['role'].title()}: {message['content']}")
    parts.append("Assistant:")
    return "\n".join(parts)


def render_full(tokenizer, messages: List[Dict[str, str]]) -> str:
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return "\n".join(f"{message['role'].title()}: {message['content']}" for message in messages)


@dataclass
class EncodedExample:
    input_ids: List[int]
    labels: List[int]


class ActionSFTDataset:
    def __init__(self, rows: Sequence[Dict[str, object]], tokenizer, max_length: int):
        self.examples: List[EncodedExample] = []
        for row in rows:
            messages = row.get("messages")
            if not isinstance(messages, list) or len(messages) < 3:
                continue
            prompt_messages = messages[:-1]
            full_text = render_full(tokenizer, messages)  # type: ignore[arg-type]
            prompt_text = render_prompt(tokenizer, prompt_messages)  # type: ignore[arg-type]
            full_ids = tokenizer(full_text, add_special_tokens=False).input_ids
            prompt_ids = tokenizer(prompt_text, add_special_tokens=False).input_ids
            if len(full_ids) > max_length:
                overflow = len(full_ids) - max_length
                full_ids = full_ids[overflow:]
                prompt_len = max(0, len(prompt_ids) - overflow)
            else:
                prompt_len = len(prompt_ids)
            labels = list(full_ids)
            for idx in range(min(prompt_len, len(labels))):
                labels[idx] = -100
            if any(label != -100 for label in labels):
                self.examples.append(EncodedExample(input_ids=full_ids, labels=labels))

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> EncodedExample:
        return self.examples[index]


def collate_batch(batch: Sequence[EncodedExample], tokenizer):
    import torch

    pad_id = tokenizer.pad_token_id
    max_len = max(len(item.input_ids) for item in batch)
    input_ids, labels, attention_mask = [], [], []
    for item in batch:
        pad_len = max_len - len(item.input_ids)
        input_ids.append(item.input_ids + [pad_id] * pad_len)
        labels.append(item.labels + [-100] * pad_len)
        attention_mask.append([1] * len(item.input_ids) + [0] * pad_len)
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
    }


def build_eval_rows(cfg: Dict[str, object], root: Path) -> List[Dict[str, object]]:
    eval_cfg = cfg["eval"]  # type: ignore[index]
    subgraph_path = root / str(eval_cfg["subgraphs"])  # type: ignore[index]
    memory_path = root / str(eval_cfg["memory"])  # type: ignore[index]
    memory = MemoryStore.load(memory_path)
    max_eval_samples = int(eval_cfg.get("max_eval_samples", 0))  # type: ignore[union-attr]
    max_candidates = int(eval_cfg.get("max_candidates", 80))  # type: ignore[union-attr]
    rows = []
    for record in iter_jsonl(subgraph_path):
        gold_chain = record.get("gold_relation_chain") or []
        if not gold_chain:
            continue
        gold_next = gold_chain[0]
        actions = [ActionCandidate(**row) for row in record.get("candidate_actions", [])]
        candidate_relations = [action.relation_id for action in actions if action.relation_id]
        if gold_next not in candidate_relations:
            continue
        retrieved = memory.retrieve(record["question"], actions, top_k=5)
        memory_relations = sorted(
            {
                relation
                for row in retrieved
                for relation in row["item"].relation_template  # type: ignore[index,union-attr]
                if relation in candidate_relations
            }
        )
        compact = compact_candidates(candidate_relations, [gold_next], max_candidates=max_candidates)
        rows.append(
            {
                "qid": record["qid"],
                "question": record["question"],
                "seed_entities": record.get("seed_entities", []),
                "candidate_relations": compact,
                "memory_relations": memory_relations,
                "gold_next_relation": gold_next,
            }
        )
        if max_eval_samples and len(rows) >= max_eval_samples:
            break
    return rows


def parse_relation(output_text: str, candidate_relations: Sequence[str]) -> str:
    match = re.search(r'"relation_id"\s*:\s*"([^"]+)"', output_text)
    if match:
        return match.group(1)
    for relation in candidate_relations:
        if relation and relation in output_text:
            return relation
    return ""


def evaluate_model(model, tokenizer, rows: Sequence[Dict[str, object]], device, max_new_tokens: int) -> Dict[str, object]:
    import torch

    model.eval()
    details = []
    correct = 0
    invalid = 0
    for row in rows:
        prompt = format_action_prompt(
            question=str(row["question"]),
            seed_entities=row.get("seed_entities", []),
            memory_relations=row.get("memory_relations", []),  # type: ignore[arg-type]
            candidate_relations=row.get("candidate_relations", []),  # type: ignore[arg-type]
        )
        prompt_text = render_prompt(
            tokenizer,
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        encoded = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False).to(device)
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        new_tokens = generated[0][encoded["input_ids"].shape[1] :]
        output_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        prediction = parse_relation(output_text, row.get("candidate_relations", []))  # type: ignore[arg-type]
        is_valid = prediction in row.get("candidate_relations", [])
        is_correct = prediction == row["gold_next_relation"]
        correct += int(is_correct)
        invalid += int(not is_valid)
        details.append(
            {
                "qid": row["qid"],
                "question": row["question"],
                "gold_next_relation": row["gold_next_relation"],
                "prediction": prediction,
                "valid": bool(is_valid),
                "correct": bool(is_correct),
                "raw_output": output_text,
            }
        )
    return {
        "num_eval": len(rows),
        "accuracy": correct / len(rows) if rows else 0.0,
        "invalid_rate": invalid / len(rows) if rows else 0.0,
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    assert_remote_safety(cfg)
    root = output_root(cfg)
    train_cfg = cfg["train"]
    eval_cfg = cfg["eval"]
    model_cfg = cfg["model"]
    run_name = cfg["outputs"].get("run_name", "qwen3_0p6b_memory_sft_minimal")
    run_dir = ensure_run_dir(root, str(run_name))

    os.environ.setdefault("HF_HOME", str(root / "hf_cache"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(root / "hf_cache" / "transformers"))
    set_seed(int(train_cfg.get("seed", 42)))

    import torch
    from torch.optim import AdamW
    from torch.utils.data import DataLoader
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_path = str(model_cfg["path"])
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=bool(model_cfg.get("trust_remote_code", True)),
        local_files_only=True,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=bool(model_cfg.get("trust_remote_code", True)),
        local_files_only=True,
        torch_dtype=dtype,
    ).to(device)

    lora_cfg = cfg.get("lora", {})
    if lora_cfg.get("enabled", True):
        from peft import LoraConfig, TaskType, get_peft_model

        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=int(lora_cfg.get("r", 8)),
            lora_alpha=int(lora_cfg.get("alpha", 16)),
            lora_dropout=float(lora_cfg.get("dropout", 0.05)),
            target_modules=list(lora_cfg.get("target_modules", [])),
        )
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()

    train_path = root / str(train_cfg["sft_data"])
    rows = load_sft_rows(train_path, int(train_cfg.get("max_train_samples", 0)))
    dataset = ActionSFTDataset(rows, tokenizer, max_length=int(train_cfg.get("max_length", 2048)))
    if len(dataset) == 0:
        raise RuntimeError(f"No trainable examples loaded from {train_path}")

    eval_rows = build_eval_rows(cfg, root)
    write_json(run_dir / "config_snapshot.json", cfg, overwrite=False)
    write_json(run_dir / "train_data_summary.json", {"num_rows": len(rows), "num_encoded": len(dataset)}, overwrite=False)

    if eval_cfg.get("eval_before_training", True):
        before = evaluate_model(
            model,
            tokenizer,
            eval_rows,
            device,
            max_new_tokens=int(eval_cfg.get("max_new_tokens", 32)),
        )
        write_json(run_dir / "eval_before.json", {k: v for k, v in before.items() if k != "details"}, overwrite=False)
        write_jsonl(run_dir / "eval_before_details.jsonl", before["details"], overwrite=False)
        print(f"eval_before_accuracy={before['accuracy']:.4f} invalid_rate={before['invalid_rate']:.4f}")

    loader = DataLoader(
        dataset,
        batch_size=int(train_cfg.get("micro_batch_size", 1)),
        shuffle=True,
        collate_fn=lambda batch: collate_batch(batch, tokenizer),
    )
    optimizer = AdamW((p for p in model.parameters() if p.requires_grad), lr=float(train_cfg.get("learning_rate", 2e-4)))
    grad_accum = int(train_cfg.get("gradient_accumulation_steps", 8))
    max_steps = int(train_cfg.get("max_steps", 30))
    model.train()
    losses = []
    step = 0
    optimizer.zero_grad(set_to_none=True)
    while step < max_steps:
        for batch in loader:
            batch = {key: value.to(device) for key, value in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss / grad_accum
            loss.backward()
            losses.append(float(loss.detach().cpu()) * grad_accum)
            if (len(losses) % grad_accum) == 0:
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                step += 1
                print(f"train_step={step} loss={losses[-1]:.6f}")
                if step >= max_steps:
                    break

    if train_cfg.get("save_adapter", True):
        model.save_pretrained(run_dir / "adapter")
        tokenizer.save_pretrained(run_dir / "adapter")

    after = evaluate_model(
        model,
        tokenizer,
        eval_rows,
        device,
        max_new_tokens=int(eval_cfg.get("max_new_tokens", 32)),
    )
    write_json(run_dir / "eval_after.json", {k: v for k, v in after.items() if k != "details"}, overwrite=False)
    write_jsonl(run_dir / "eval_after_details.jsonl", after["details"], overwrite=False)
    summary = {
        "run_dir": str(run_dir),
        "model_path": model_path,
        "num_train_rows": len(rows),
        "num_encoded_train_rows": len(dataset),
        "num_eval_rows": len(eval_rows),
        "max_steps": max_steps,
        "final_loss": losses[-1] if losses else None,
        "mean_loss": sum(losses) / len(losses) if losses else None,
        "eval_after_accuracy": after["accuracy"],
        "eval_after_invalid_rate": after["invalid_rate"],
    }
    if eval_cfg.get("eval_before_training", True):
        before_meta = json.loads((run_dir / "eval_before.json").read_text(encoding="utf-8"))
        summary["eval_before_accuracy"] = before_meta["accuracy"]
        summary["eval_before_invalid_rate"] = before_meta["invalid_rate"]
        summary["accuracy_delta"] = after["accuracy"] - before_meta["accuracy"]
    write_json(run_dir / "summary.json", summary, overwrite=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
