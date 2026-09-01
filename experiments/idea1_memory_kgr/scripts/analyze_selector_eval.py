from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval", required=True)
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()

    rows = []
    with open(args.eval, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    positive = [row for row in rows if float(row.get("memory_utility_delta", 0.0)) > 0]
    negative = [row for row in rows if float(row.get("memory_utility_delta", 0.0)) < 0]
    same = [row for row in rows if float(row.get("memory_utility_delta", 0.0)) == 0]
    memory_correct = [row for row in rows if float(row.get("memory_correct", 0.0)) == 1.0]
    rule_correct = [row for row in rows if float(row.get("rule_correct", 0.0)) == 1.0]

    summary = {
        "num_rows": len(rows),
        "positive_delta": len(positive),
        "negative_delta": len(negative),
        "same_delta": len(same),
        "memory_correct": len(memory_correct),
        "rule_correct": len(rule_correct),
        "memory_only_correct": len(positive),
        "rule_only_correct": len(negative),
        "most_common_memory_relations": Counter(row.get("memory_top_relation", "") for row in rows).most_common(10),
        "most_common_gold_relations": Counter(row.get("gold_next_relation", "") for row in rows).most_common(10),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("positive_examples_head=")
    for row in positive[: args.examples]:
        print(json.dumps(row, ensure_ascii=False))

    print("negative_examples_head=")
    for row in negative[: args.examples]:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
