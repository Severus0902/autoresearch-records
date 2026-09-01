from __future__ import annotations

from typing import Dict, Iterable, List


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def summarize_selector(rows: List[Dict[str, object]]) -> Dict[str, object]:
    if not rows:
        return {"num_examples": 0}
    return {
        "num_examples": len(rows),
        "rule_next_relation_accuracy": mean(float(row.get("rule_correct", 0.0)) for row in rows),
        "memory_next_relation_accuracy": mean(float(row.get("memory_correct", 0.0)) for row in rows),
        "memory_utility_delta": mean(float(row.get("memory_utility_delta", 0.0)) for row in rows),
        "avg_candidate_actions": mean(float(row.get("num_candidate_actions", 0.0)) for row in rows),
        "avg_memory_hits": mean(float(row.get("num_memory_hits", 0.0)) for row in rows),
    }
