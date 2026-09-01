from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, resolve_output_path
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl
from idea1_kgr.memory_store import MemoryStore
from idea1_kgr.policies import MemoryActionSelector, RuleRelationRanker
from idea1_kgr.schemas import ActionCandidate


def _actions(rows: Iterable[Dict[str, object]]) -> List[ActionCandidate]:
    return [ActionCandidate(**row) for row in rows]


def _relation_prefix(relation: str) -> str:
    parts = relation.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else relation


def _choose_positive(candidates: List[ActionCandidate], gold_next: str) -> ActionCandidate | None:
    for candidate in candidates:
        if candidate.relation_id == gold_next:
            return candidate
    return None


def _add_negative(
    negatives: List[Tuple[str, ActionCandidate]],
    seen: set[str],
    source: str,
    candidate: ActionCandidate | None,
    gold_next: str,
) -> None:
    if not candidate or candidate.relation_id == gold_next:
        return
    key = candidate.action_id
    if key not in seen:
        seen.add(key)
        negatives.append((source, candidate))


def _choose_negatives(
    question: str,
    candidates: List[ActionCandidate],
    gold_next: str,
    rule_ranker: RuleRelationRanker,
    memory_ranker: MemoryActionSelector,
    max_negatives: int,
) -> List[Tuple[str, ActionCandidate]]:
    negatives: List[Tuple[str, ActionCandidate]] = []
    seen: set[str] = set()

    rule_ranked = rule_ranker.rank(question, candidates)
    memory_ranked = memory_ranker.rank(question, candidates)
    _add_negative(negatives, seen, "rule_top_wrong", rule_ranked[0] if rule_ranked else None, gold_next)
    _add_negative(negatives, seen, "memory_top_wrong", memory_ranked[0] if memory_ranked else None, gold_next)

    gold_prefix = _relation_prefix(gold_next)
    for candidate in rule_ranked:
        if _relation_prefix(candidate.relation_id) == gold_prefix:
            _add_negative(negatives, seen, "same_domain_hard_negative", candidate, gold_next)
        if len(negatives) >= max_negatives:
            return negatives

    for candidate in rule_ranked:
        _add_negative(negatives, seen, "ranked_negative", candidate, gold_next)
        if len(negatives) >= max_negatives:
            return negatives

    return negatives


def _compact_action(action: ActionCandidate) -> Dict[str, object]:
    return {
        "action_id": action.action_id,
        "action_type": action.action_type,
        "entity_id": action.entity_id,
        "relation_id": action.relation_id,
        "target_id": action.target_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/webqsp_eval100.json")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-negatives", type=int, default=4)
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_output_dirs(cfg)
    pref_path = resolve_output_path(cfg, "preferences")
    pref_summary_path = resolve_output_path(cfg, "preferences_summary")
    memory = MemoryStore.load(resolve_output_path(cfg, "memory"))
    rule_ranker = RuleRelationRanker()
    memory_ranker = MemoryActionSelector(memory, top_k=int(cfg.get("memory", {}).get("top_k", 5)))

    pair_rows = []
    skipped = Counter()
    source_counts = Counter()
    relation_counts = Counter()

    for record in iter_jsonl(resolve_output_path(cfg, "subgraphs")):
        gold_chain = record.get("gold_relation_chain") or []
        if not gold_chain:
            skipped["no_gold_chain"] += 1
            continue
        gold_next = gold_chain[0]
        candidates = _actions(record.get("candidate_actions") or [])
        positive = _choose_positive(candidates, gold_next)
        if positive is None:
            skipped["gold_not_in_candidates"] += 1
            continue

        negatives = _choose_negatives(
            question=record["question"],
            candidates=candidates,
            gold_next=gold_next,
            rule_ranker=rule_ranker,
            memory_ranker=memory_ranker,
            max_negatives=args.max_negatives,
        )
        if not negatives:
            skipped["no_negative"] += 1
            continue

        candidate_relations = [candidate.relation_id for candidate in candidates]
        retrieved_memory = memory.retrieve(record["question"], candidates, top_k=int(cfg.get("memory", {}).get("top_k", 5)))
        memory_relations = sorted(
            {
                relation
                for row in retrieved_memory
                for relation in row["item"].relation_template  # type: ignore[index,union-attr]
                if relation in candidate_relations
            }
        )
        for neg_idx, (source, negative) in enumerate(negatives):
            row = {
                "preference_id": f"{record['dataset']}::{record['qid']}::{neg_idx}",
                "dataset": record["dataset"],
                "qid": record["qid"],
                "question": record["question"],
                "seed_entities": record.get("seed_entities", []),
                "gold_next_relation": gold_next,
                "gold_relation_chain": gold_chain,
                "positive_action": _compact_action(positive),
                "negative_action": _compact_action(negative),
                "negative_source": source,
                "candidate_relations": candidate_relations,
                "verified_memory_relations": memory_relations,
                "num_candidate_actions": len(candidates),
                "format": "pairwise_action_preference_v1",
            }
            pair_rows.append(row)
            source_counts[source] += 1
            relation_counts[gold_next] += 1

    summary = {
        "num_preferences": len(pair_rows),
        "num_source_subgraphs": sum(1 for _ in iter_jsonl(resolve_output_path(cfg, "subgraphs"))),
        "skipped": dict(skipped),
        "negative_source_counts": dict(source_counts),
        "top_gold_relations": relation_counts.most_common(20),
        "max_negatives": args.max_negatives,
    }
    write_jsonl(pref_path, pair_rows, overwrite=args.overwrite)
    write_json(pref_summary_path, summary, overwrite=args.overwrite)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
