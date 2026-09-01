from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, resolve_output_path
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl


SYSTEM_PROMPT = (
    "You are a knowledge-graph reasoning action selector. "
    "Choose exactly one relation_id from the candidate relations. "
    "Return compact JSON only."
)


def _json_action(relation_id: str) -> str:
    return json.dumps({"relation_id": relation_id}, ensure_ascii=False)


def _compact_candidates(
    candidate_relations: List[str],
    required_relations: Iterable[str],
    max_candidates: int,
) -> List[str]:
    ordered = list(OrderedDict.fromkeys(candidate_relations))
    required = [rel for rel in required_relations if rel]
    compact = ordered[:max_candidates]
    for rel in required:
        if rel not in compact:
            if len(compact) >= max_candidates and compact:
                compact[-1] = rel
            else:
                compact.append(rel)
    return list(OrderedDict.fromkeys(compact))


def _format_prompt(row: Dict[str, object], candidate_relations: List[str]) -> str:
    seeds = row.get("seed_entities", [])
    memory_relations = row.get("verified_memory_relations", [])
    candidates = "\n".join(f"{idx}. {rel}" for idx, rel in enumerate(candidate_relations))
    return (
        f"Question: {row.get('question', '')}\n"
        f"Seed entities: {json.dumps(seeds, ensure_ascii=False)}\n"
        f"Verified memory relations: {json.dumps(memory_relations, ensure_ascii=False)}\n"
        f"Candidate relations:\n{candidates}\n\n"
        "Select the best next-hop relation for graph traversal. "
        "Return JSON with key relation_id."
    )


def _positive_relation(row: Dict[str, object]) -> str:
    return str(row.get("positive_action", {}).get("relation_id", ""))  # type: ignore[union-attr]


def _negative_relation(row: Dict[str, object]) -> str:
    return str(row.get("negative_action", {}).get("relation_id", ""))  # type: ignore[union-attr]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/webqsp_train500.json")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=80)
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_output_dirs(cfg)
    pref_path = resolve_output_path(cfg, "preferences")
    sft_path = resolve_output_path(cfg, "sft_data")
    dpo_path = resolve_output_path(cfg, "dpo_data")
    summary_path = resolve_output_path(cfg, "train_data_summary")

    preferences = list(iter_jsonl(pref_path))
    by_qid: "OrderedDict[str, Dict[str, object]]" = OrderedDict()
    dpo_rows = []
    skipped = Counter()

    for row in preferences:
        positive = _positive_relation(row)
        negative = _negative_relation(row)
        if not positive or not negative:
            skipped["missing_positive_or_negative"] += 1
            continue
        candidate_relations = _compact_candidates(
            list(row.get("candidate_relations", [])),
            required_relations=[positive, negative],
            max_candidates=args.max_candidates,
        )
        prompt = _format_prompt(row, candidate_relations)
        chosen = _json_action(positive)
        rejected = _json_action(negative)
        dpo_rows.append(
            {
                "id": row.get("preference_id"),
                "dataset": row.get("dataset"),
                "qid": row.get("qid"),
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected,
                "positive_relation_id": positive,
                "negative_relation_id": negative,
                "negative_source": row.get("negative_source"),
                "candidate_relations": candidate_relations,
                "format": "compact_relation_pairwise_v1",
            }
        )
        qid = str(row.get("qid", ""))
        if qid and qid not in by_qid:
            by_qid[qid] = {
                "id": qid,
                "dataset": row.get("dataset"),
                "qid": qid,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": chosen},
                ],
                "target_relation_id": positive,
                "candidate_relations": candidate_relations,
                "format": "compact_relation_sft_v1",
            }

    sft_rows = list(by_qid.values())
    summary = {
        "num_preferences_in": len(preferences),
        "num_dpo_rows": len(dpo_rows),
        "num_sft_rows": len(sft_rows),
        "max_candidates": args.max_candidates,
        "skipped": dict(skipped),
        "top_positive_relations": Counter(row["positive_relation_id"] for row in dpo_rows).most_common(20),
        "negative_source_counts": Counter(row["negative_source"] for row in dpo_rows).most_common(),
    }
    write_jsonl(sft_path, sft_rows, overwrite=args.overwrite)
    write_jsonl(dpo_path, dpo_rows, overwrite=args.overwrite)
    write_json(summary_path, summary, overwrite=args.overwrite)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
