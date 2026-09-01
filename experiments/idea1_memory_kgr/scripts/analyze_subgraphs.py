from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subgraphs", required=True)
    parser.add_argument("--eval", default="")
    args = parser.parse_args()

    records = []
    with open(args.subgraphs, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    relation_visible = []
    answer_visible = []
    candidate_contains_gold = []
    gold_relation_ranks = []
    num_edges = []
    num_candidates = []
    missing_examples = []

    for record in records:
        gold_chain = record.get("gold_relation_chain") or []
        gold_next = gold_chain[0] if gold_chain else ""
        candidate_relations = [
            action.get("relation_id")
            for action in record.get("candidate_actions", [])
            if action.get("relation_id")
        ]
        edge_relations = [edge.get("relation") for edge in record.get("edges", []) if edge.get("relation")]

        if gold_next:
            relation_visible.append(float(gold_next in edge_relations))
            candidate_contains_gold.append(float(gold_next in candidate_relations))
            if gold_next in candidate_relations:
                gold_relation_ranks.append(candidate_relations.index(gold_next) + 1)
            else:
                missing_examples.append(
                    {
                        "qid": record.get("qid"),
                        "question": record.get("question"),
                        "gold_next_relation": gold_next,
                        "top_candidate_relations": candidate_relations[:10],
                    }
                )

        visible = record.get("oracle", {}).get("gold_answer_visible")
        if visible is not None:
            answer_visible.append(float(bool(visible)))
        num_edges.append(len(record.get("edges", [])))
        num_candidates.append(len(candidate_relations))

    def avg(values):
        return sum(values) / len(values) if values else 0.0

    summary = {
        "num_records": len(records),
        "gold_next_relation_edge_recall": avg(relation_visible),
        "gold_next_relation_candidate_recall": avg(candidate_contains_gold),
        "gold_answer_visible_rate": avg(answer_visible),
        "avg_edges": avg(num_edges),
        "avg_candidate_actions": avg(num_candidates),
        "gold_relation_rank_avg_when_visible": avg(gold_relation_ranks),
        "gold_relation_rank_min_when_visible": min(gold_relation_ranks) if gold_relation_ranks else None,
        "gold_relation_rank_max_when_visible": max(gold_relation_ranks) if gold_relation_ranks else None,
        "most_common_candidate_prefixes": Counter(
            rel.split(".")[0] for record in records for rel in [
                action.get("relation_id", "") for action in record.get("candidate_actions", [])
            ] if rel
        ).most_common(10),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("missing_examples_head=")
    for item in missing_examples[:8]:
        print(json.dumps(item, ensure_ascii=False))


if __name__ == "__main__":
    main()
