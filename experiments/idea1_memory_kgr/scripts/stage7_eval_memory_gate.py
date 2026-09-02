from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import assert_remote_safety, load_config, output_root
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl
from idea1_kgr.memory_store import relation_tokens, tokenize


SOURCE_KEYS = ("no_memory", "random_memory", "verified_memory")


def ensure_run_dir(root: Path, run_name: str) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = root / "runs" / f"{run_name}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def load_detail_map(root: Path, run_dir: str, detail_file: str) -> Dict[str, Dict[str, Any]]:
    path = root / run_dir / detail_file
    rows = {}
    for row in iter_jsonl(path):
        qid = str(row.get("qid", ""))
        if qid:
            rows[qid] = row
    return rows


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return False


def relation_overlap(question: str, relation: str) -> float:
    q_tokens = tokenize(question)
    r_tokens = relation_tokens(relation)
    if not q_tokens or not r_tokens:
        return 0.0
    return len(q_tokens & r_tokens) / len(r_tokens)


def build_cases(run_maps: Mapping[str, Mapping[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    qids = set(run_maps["no_memory"]) & set(run_maps["random_memory"]) & set(run_maps["verified_memory"])
    cases: List[Dict[str, Any]] = []
    for qid in sorted(qids):
        no = dict(run_maps["no_memory"][qid])
        random_row = dict(run_maps["random_memory"][qid])
        verified = dict(run_maps["verified_memory"][qid])
        memory_relations = list(verified.get("memory_relations", []))
        verified_memory_relations = list(verified.get("verified_memory_relations", memory_relations))
        case = {
            "qid": qid,
            "question": verified.get("question", no.get("question", "")),
            "gold_next_relation": verified.get("gold_next_relation", no.get("gold_next_relation", "")),
            "memory_relations": memory_relations,
            "verified_memory_relations": verified_memory_relations,
            "no_memory": no,
            "random_memory": random_row,
            "verified_memory": verified,
        }
        case["label"] = memory_effect_label(case)
        case["features"] = gate_features(case)
        cases.append(case)
    return cases


def memory_effect_label(case: Mapping[str, Any]) -> str:
    no_correct = as_bool(case["no_memory"].get("correct"))
    verified_correct = as_bool(case["verified_memory"].get("correct"))
    if verified_correct and not no_correct:
        return "memory_helped"
    if no_correct and not verified_correct:
        return "memory_hurt"
    if no_correct and verified_correct:
        return "both_correct"
    return "both_wrong"


def gate_features(case: Mapping[str, Any]) -> Dict[str, Any]:
    question = str(case.get("question", ""))
    no_pred = str(case["no_memory"].get("prediction", ""))
    verified_pred = str(case["verified_memory"].get("prediction", ""))
    random_pred = str(case["random_memory"].get("prediction", ""))
    memory_relations = list(case.get("memory_relations", []))
    memory_set = set(memory_relations)
    no_overlap = relation_overlap(question, no_pred)
    verified_overlap = relation_overlap(question, verified_pred)
    random_overlap = relation_overlap(question, random_pred)
    return {
        "num_memory_relations": len(memory_relations),
        "has_memory": bool(memory_relations),
        "no_prediction_in_memory": no_pred in memory_set,
        "verified_prediction_in_memory": verified_pred in memory_set,
        "random_prediction_in_memory": random_pred in memory_set,
        "no_verified_agree": no_pred == verified_pred,
        "random_verified_agree": random_pred == verified_pred,
        "no_relation_overlap": no_overlap,
        "verified_relation_overlap": verified_overlap,
        "random_relation_overlap": random_overlap,
        "verified_minus_no_overlap": verified_overlap - no_overlap,
        "memory_ambiguous": len(memory_relations) > 1,
    }


def row_for_source(case: Mapping[str, Any], source: str) -> Mapping[str, Any]:
    return case[source]


def choose_strategy(case: Mapping[str, Any], strategy: str) -> str:
    features = case["features"]
    if strategy == "always_no_memory":
        return "no_memory"
    if strategy == "always_random_memory":
        return "random_memory"
    if strategy == "always_verified_memory":
        return "verified_memory"
    if strategy == "verified_if_memory_nonempty":
        return "verified_memory" if features["has_memory"] else "no_memory"
    if strategy == "verified_if_prediction_in_memory":
        return "verified_memory" if features["verified_prediction_in_memory"] else "no_memory"
    if strategy == "verified_if_single_memory":
        return "verified_memory" if features["num_memory_relations"] == 1 else "no_memory"
    if strategy == "agreement_then_verified_if_in_memory":
        if features["no_verified_agree"]:
            return "verified_memory"
        return "verified_memory" if features["verified_prediction_in_memory"] else "no_memory"
    if strategy == "fixed_grm_lite_gate":
        return choose_with_weights(
            case,
            {
                "bias": -0.05,
                "verified_pred_in_memory": 0.35,
                "no_pred_in_memory": -0.15,
                "overlap_delta": 0.70,
                "memory_count": -0.05,
                "memory_ambiguous": -0.05,
            },
        )
    raise ValueError(f"Unknown strategy: {strategy}")


def choose_oracle(case: Mapping[str, Any], sources: Sequence[str]) -> str:
    for source in sources:
        if as_bool(row_for_source(case, source).get("correct")):
            return source
    return sources[0]


def choose_with_weights(case: Mapping[str, Any], weights: Mapping[str, float]) -> str:
    features = case["features"]
    margin = (
        weights.get("bias", 0.0)
        + weights.get("verified_pred_in_memory", 0.0) * float(features["verified_prediction_in_memory"])
        + weights.get("no_pred_in_memory", 0.0) * float(features["no_prediction_in_memory"])
        + weights.get("overlap_delta", 0.0) * float(features["verified_minus_no_overlap"])
        + weights.get("memory_count", 0.0) * min(float(features["num_memory_relations"]), 5.0) / 5.0
        + weights.get("memory_ambiguous", 0.0) * float(features["memory_ambiguous"])
    )
    return "verified_memory" if margin >= 0.0 else "no_memory"


def default_weight_grid() -> Iterable[Dict[str, float]]:
    grid = {
        "bias": [-0.4, -0.2, -0.1, 0.0, 0.1, 0.2],
        "verified_pred_in_memory": [-0.2, 0.0, 0.2, 0.4, 0.6],
        "no_pred_in_memory": [-0.4, -0.2, 0.0, 0.2],
        "overlap_delta": [-1.0, -0.5, 0.0, 0.5, 1.0],
        "memory_count": [-0.2, -0.1, 0.0, 0.1],
        "memory_ambiguous": [-0.2, -0.1, 0.0, 0.1],
    }
    keys = list(grid)
    for values in itertools.product(*(grid[key] for key in keys)):
        yield dict(zip(keys, values))


def evaluate_sources(cases: Sequence[Mapping[str, Any]], choices: Mapping[str, str]) -> Dict[str, Any]:
    correct = 0
    invalid = 0
    source_counts = Counter()
    label_counts = Counter()
    helped_total = 0
    helped_captured = 0
    hurt_total = 0
    hurt_avoided = 0
    details = []
    for case in cases:
        qid = str(case["qid"])
        source = choices[qid]
        row = row_for_source(case, source)
        is_correct = as_bool(row.get("correct"))
        is_valid = as_bool(row.get("valid"))
        correct += int(is_correct)
        invalid += int(not is_valid)
        source_counts[source] += 1
        label = str(case["label"])
        label_counts[label] += 1
        if label == "memory_helped":
            helped_total += 1
            helped_captured += int(source == "verified_memory")
        if label == "memory_hurt":
            hurt_total += 1
            hurt_avoided += int(source == "no_memory")
        details.append(
            {
                "qid": qid,
                "question": case["question"],
                "gold_next_relation": case["gold_next_relation"],
                "label": label,
                "chosen_source": source,
                "chosen_prediction": row.get("prediction", ""),
                "chosen_correct": is_correct,
                "chosen_valid": is_valid,
                "no_prediction": case["no_memory"].get("prediction", ""),
                "random_prediction": case["random_memory"].get("prediction", ""),
                "verified_prediction": case["verified_memory"].get("prediction", ""),
                "memory_relations": case.get("memory_relations", []),
                "features": case["features"],
            }
        )
    n = len(cases)
    return {
        "num_cases": n,
        "accuracy": correct / n if n else 0.0,
        "invalid_rate": invalid / n if n else 0.0,
        "source_counts": dict(source_counts),
        "label_counts": dict(label_counts),
        "memory_help_capture_rate": helped_captured / helped_total if helped_total else None,
        "memory_hurt_avoid_rate": hurt_avoided / hurt_total if hurt_total else None,
        "details": details,
    }


def score_sources(cases: Sequence[Mapping[str, Any]], choices: Mapping[str, str]) -> float:
    if not cases:
        return 0.0
    correct = 0
    for case in cases:
        source = choices[str(case["qid"])]
        correct += int(as_bool(row_for_source(case, source).get("correct")))
    return correct / len(cases)


def choices_for_strategy(cases: Sequence[Mapping[str, Any]], strategy: str) -> Dict[str, str]:
    return {str(case["qid"]): choose_strategy(case, strategy) for case in cases}


def train_best_weights(cases: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    best_weights: Dict[str, float] | None = None
    best_key = (-1.0, -math.inf)
    for weights in default_weight_grid():
        choices = {str(case["qid"]): choose_with_weights(case, weights) for case in cases}
        accuracy = score_sources(cases, choices)
        simplicity = -sum(abs(value) for value in weights.values())
        key = (accuracy, simplicity)
        if key > best_key:
            best_key = key
            best_weights = weights
    if best_weights is None:
        raise RuntimeError("No weights were evaluated")
    return best_weights


def loocv_grm_lite(cases: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    choices = {}
    weights_counter: Counter[str] = Counter()
    for index, case in enumerate(cases):
        train_cases = list(cases[:index]) + list(cases[index + 1 :])
        weights = train_best_weights(train_cases)
        weights_counter[json.dumps(weights, sort_keys=True)] += 1
        choices[str(case["qid"])] = choose_with_weights(case, weights)
    result = evaluate_sources(cases, choices)
    result["weights_vote_top"] = [
        {"weights": json.loads(weights), "count": count}
        for weights, count in weights_counter.most_common(5)
    ]
    return result


def strip_details(result: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in result.items() if key != "details"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    assert_remote_safety(cfg)
    root = output_root(cfg)
    gate_cfg = cfg["gate_eval"]
    run_dir = ensure_run_dir(root, str(cfg["outputs"].get("run_name", "memory_gate_eval")))
    detail_file = str(gate_cfg.get("detail_file", "eval_after_details.jsonl"))

    runs = gate_cfg["runs"]
    run_maps = {
        source: load_detail_map(root, str(runs[source]), detail_file)
        for source in SOURCE_KEYS
    }
    cases = build_cases(run_maps)
    if not cases:
        raise RuntimeError("No overlapping qids found across gate eval runs")

    strategies = [
        "always_no_memory",
        "always_random_memory",
        "always_verified_memory",
        "verified_if_memory_nonempty",
        "verified_if_prediction_in_memory",
        "verified_if_single_memory",
        "agreement_then_verified_if_in_memory",
        "fixed_grm_lite_gate",
    ]
    strategy_results: Dict[str, Dict[str, Any]] = {}
    for strategy in strategies:
        strategy_results[strategy] = evaluate_sources(cases, choices_for_strategy(cases, strategy))

    oracle_no_verified = evaluate_sources(
        cases,
        {str(case["qid"]): choose_oracle(case, ["verified_memory", "no_memory"]) for case in cases},
    )
    oracle_all_three = evaluate_sources(
        cases,
        {
            str(case["qid"]): choose_oracle(case, ["verified_memory", "no_memory", "random_memory"])
            for case in cases
        },
    )
    loocv_result = loocv_grm_lite(cases)
    strategy_results["loocv_grm_lite_gate"] = loocv_result
    strategy_results["oracle_no_vs_verified"] = oracle_no_verified
    strategy_results["oracle_all_three"] = oracle_all_three

    summary = {
        "run_dir": str(run_dir),
        "input_runs": {source: str(runs[source]) for source in SOURCE_KEYS},
        "detail_file": detail_file,
        "num_cases": len(cases),
        "label_counts": dict(Counter(str(case["label"]) for case in cases)),
        "strategies": {name: strip_details(result) for name, result in strategy_results.items()},
        "oracle_gap_vs_verified": oracle_no_verified["accuracy"]
        - strategy_results["always_verified_memory"]["accuracy"],
    }
    write_json(run_dir / "summary.json", summary, overwrite=False)
    write_jsonl(
        run_dir / "case_features.jsonl",
        [
            {
                "qid": case["qid"],
                "question": case["question"],
                "gold_next_relation": case["gold_next_relation"],
                "label": case["label"],
                "features": case["features"],
                "memory_relations": case["memory_relations"],
                "no_prediction": case["no_memory"].get("prediction", ""),
                "random_prediction": case["random_memory"].get("prediction", ""),
                "verified_prediction": case["verified_memory"].get("prediction", ""),
            }
            for case in cases
        ],
        overwrite=False,
    )
    for strategy, result in strategy_results.items():
        write_jsonl(run_dir / f"{strategy}_details.jsonl", result["details"], overwrite=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
