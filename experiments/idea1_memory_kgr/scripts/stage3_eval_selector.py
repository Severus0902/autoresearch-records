from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, resolve_output_path
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl
from idea1_kgr.memory_store import MemoryStore
from idea1_kgr.metrics import summarize_selector
from idea1_kgr.policies import MemoryActionSelector, RuleRelationRanker
from idea1_kgr.schemas import ActionCandidate
from idea1_kgr.verifier import memory_utility_delta


def _actions(rows):
    return [ActionCandidate(**row) for row in rows]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/webqsp_pilot.json")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_output_dirs(cfg)
    memory = MemoryStore.load(resolve_output_path(cfg, "memory"))
    rule_ranker = RuleRelationRanker()
    memory_ranker = MemoryActionSelector(memory, top_k=int(cfg.get("memory", {}).get("top_k", 5)))

    rows = []
    for record in iter_jsonl(resolve_output_path(cfg, "subgraphs")):
        gold_chain = record.get("gold_relation_chain") or []
        if not gold_chain:
            continue
        candidates = _actions(record.get("candidate_actions") or [])
        if not candidates:
            continue
        rule_top = rule_ranker.rank(record["question"], candidates)[0]
        memory_ranked = memory_ranker.rank(record["question"], candidates)
        memory_top = memory_ranked[0]
        gold_next = gold_chain[0]
        rule_correct = rule_top.relation_id == gold_next
        memory_correct = memory_top.relation_id == gold_next
        rows.append(
            {
                "qid": record["qid"],
                "question": record["question"],
                "gold_next_relation": gold_next,
                "rule_top_relation": rule_top.relation_id,
                "memory_top_relation": memory_top.relation_id,
                "rule_correct": float(rule_correct),
                "memory_correct": float(memory_correct),
                "memory_utility_delta": memory_utility_delta(rule_correct, memory_correct),
                "num_candidate_actions": len(candidates),
                "num_memory_hits": sum(1 for item in memory_ranked if item.meta.get("memory_hit")),
            }
        )

    write_jsonl(resolve_output_path(cfg, "eval"), rows, overwrite=args.overwrite)
    summary = summarize_selector(rows)
    write_json(resolve_output_path(cfg, "summary"), summary, overwrite=args.overwrite)
    print(summary)


if __name__ == "__main__":
    main()
