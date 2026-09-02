from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, output_root, resolve_output_path
from idea1_kgr.io_utils import iter_jsonl, write_json, write_jsonl
from idea1_kgr.memory_store import MemoryStore, relation_tokens, tokenize
from idea1_kgr.policies import MemoryActionSelector, RuleRelationRanker
from idea1_kgr.schemas import ActionCandidate


try:
    import numpy as np
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression

    SKLEARN_AVAILABLE = True
except Exception:  # pragma: no cover - exercised on minimal environments.
    np = None
    DictVectorizer = None
    LogisticRegression = None
    SKLEARN_AVAILABLE = False


EVAL_KS = (1, 3, 5)
RRF_K = 60


def _actions(rows: Iterable[Dict[str, object]]) -> List[ActionCandidate]:
    return [ActionCandidate(**row) for row in rows]


def _relation_prefix(relation: str) -> str:
    parts = relation.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else relation


def _relation_tail(relation: str) -> str:
    return relation.split(".")[-1] if relation else ""


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _safe_mean(values: Sequence[float]) -> float:
    return float(mean(values)) if values else 0.0


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


@dataclass
class RelationStats:
    pos_counts: Counter
    neg_counts: Counter
    prefix_pos_counts: Counter
    prefix_neg_counts: Counter

    @classmethod
    def from_preferences(cls, rows: Sequence[Dict[str, object]]) -> "RelationStats":
        pos_counts: Counter = Counter()
        neg_counts: Counter = Counter()
        prefix_pos_counts: Counter = Counter()
        prefix_neg_counts: Counter = Counter()
        seen_positive_qrels: set[Tuple[str, str]] = set()

        for row in rows:
            qid = str(row.get("qid", ""))
            pos = _row_relation(row, "positive_action")
            neg = _row_relation(row, "negative_action")
            if pos and (qid, pos) not in seen_positive_qrels:
                seen_positive_qrels.add((qid, pos))
                pos_counts[pos] += 1
                prefix_pos_counts[_relation_prefix(pos)] += 1
            if neg:
                neg_counts[neg] += 1
                prefix_neg_counts[_relation_prefix(neg)] += 1

        return cls(pos_counts, neg_counts, prefix_pos_counts, prefix_neg_counts)

    def relation_pos_rate(self, relation: str) -> float:
        pos = self.pos_counts[relation]
        neg = self.neg_counts[relation]
        return (pos + 1.0) / (pos + neg + 2.0)

    def relation_log_odds(self, relation: str) -> float:
        return math.log((self.pos_counts[relation] + 1.0) / (self.neg_counts[relation] + 1.0))

    def prefix_pos_rate(self, relation: str) -> float:
        prefix = _relation_prefix(relation)
        pos = self.prefix_pos_counts[prefix]
        neg = self.prefix_neg_counts[prefix]
        return (pos + 1.0) / (pos + neg + 2.0)

    def prefix_log_odds(self, relation: str) -> float:
        prefix = _relation_prefix(relation)
        return math.log((self.prefix_pos_counts[prefix] + 1.0) / (self.prefix_neg_counts[prefix] + 1.0))


def _row_relation(row: Dict[str, object], key: str) -> str:
    action = row.get(key) or {}
    if isinstance(action, dict):
        return str(action.get("relation_id", ""))
    return ""


def _numeric_features(
    question: str,
    action: ActionCandidate,
    memory_relations: Iterable[str],
    candidate_relations: Sequence[str],
    stats: RelationStats,
) -> Dict[str, float]:
    q_tokens = tokenize(question)
    r_tokens = relation_tokens(action.relation_id)
    overlap = len(q_tokens & r_tokens)
    memory_set = set(memory_relations)
    return {
        "lex_overlap": float(overlap),
        "lex_jaccard": _jaccard(q_tokens, r_tokens),
        "lex_relation_coverage": overlap / max(1, len(r_tokens)),
        "relation_token_count_log": math.log1p(len(r_tokens)),
        "candidate_count_log": math.log1p(len(candidate_relations)),
        "memory_hit": 1.0 if action.relation_id in memory_set else 0.0,
        "memory_count_log": math.log1p(len(memory_set)),
        "relation_train_pos_rate": stats.relation_pos_rate(action.relation_id),
        "relation_train_log_odds": stats.relation_log_odds(action.relation_id),
        "prefix_train_pos_rate": stats.prefix_pos_rate(action.relation_id),
        "prefix_train_log_odds": stats.prefix_log_odds(action.relation_id),
    }


def _dict_features(
    question: str,
    action: ActionCandidate,
    memory_relations: Iterable[str],
    candidate_relations: Sequence[str],
    stats: RelationStats,
) -> Dict[str, float]:
    features = _numeric_features(question, action, memory_relations, candidate_relations, stats)
    features[f"relation={action.relation_id}"] = 1.0
    features[f"prefix={_relation_prefix(action.relation_id)}"] = 1.0
    features[f"tail={_relation_tail(action.relation_id)}"] = 1.0
    return features


def _ordered_relations(candidates: Sequence[ActionCandidate]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for candidate in candidates:
        if candidate.relation_id and candidate.relation_id not in seen:
            seen.add(candidate.relation_id)
            ordered.append(candidate.relation_id)
    return ordered


def _memory_relations_for_record(
    memory: MemoryStore,
    question: str,
    candidates: Sequence[ActionCandidate],
    top_k: int,
) -> List[str]:
    candidate_relations = set(_ordered_relations(candidates))
    retrieved = memory.retrieve(question, candidates, top_k=top_k)
    return sorted(
        {
            relation
            for row in retrieved
            for relation in row["item"].relation_template  # type: ignore[index,union-attr]
            if relation in candidate_relations
        }
    )


class PointwiseLogisticRanker:
    def __init__(self, stats: RelationStats):
        self.stats = stats
        self.vectorizer = None
        self.model = None
        self.available = False

    def fit(self, rows: Sequence[Dict[str, object]]) -> None:
        if not SKLEARN_AVAILABLE:
            return
        features: List[Dict[str, float]] = []
        labels: List[int] = []
        for row in rows:
            candidate_relations = list(row.get("candidate_relations", []))
            memory_relations = list(row.get("verified_memory_relations", []))
            question = str(row.get("question", ""))
            for key, label in (("positive_action", 1), ("negative_action", 0)):
                relation = _row_relation(row, key)
                if not relation:
                    continue
                action = ActionCandidate(
                    action_id=f"{key}::{relation}",
                    action_type="expand",
                    entity_id="",
                    relation_id=relation,
                )
                features.append(_dict_features(question, action, memory_relations, candidate_relations, self.stats))
                labels.append(label)
        if len(set(labels)) < 2:
            return
        self.vectorizer = DictVectorizer(sparse=True)
        x = self.vectorizer.fit_transform(features)
        self.model = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")
        self.model.fit(x, labels)
        self.available = True

    def scores(
        self,
        question: str,
        candidates: Sequence[ActionCandidate],
        memory_relations: Sequence[str],
    ) -> Dict[str, float]:
        if not self.available:
            return {}
        candidate_relations = _ordered_relations(candidates)
        features = [
            _dict_features(question, candidate, memory_relations, candidate_relations, self.stats)
            for candidate in candidates
        ]
        x = self.vectorizer.transform(features)
        probs = self.model.predict_proba(x)[:, 1]
        return {candidate.action_id: float(score) for candidate, score in zip(candidates, probs)}


class PairwiseLogisticRanker:
    def __init__(self, stats: RelationStats):
        self.stats = stats
        self.model = None
        self.available = False

    def fit(self, rows: Sequence[Dict[str, object]]) -> None:
        if not SKLEARN_AVAILABLE or np is None:
            return
        features: List[List[float]] = []
        labels: List[int] = []
        for row in rows:
            candidate_relations = list(row.get("candidate_relations", []))
            memory_relations = list(row.get("verified_memory_relations", []))
            question = str(row.get("question", ""))
            pos_rel = _row_relation(row, "positive_action")
            neg_rel = _row_relation(row, "negative_action")
            if not pos_rel or not neg_rel:
                continue
            pos = ActionCandidate("positive", "expand", "", pos_rel)
            neg = ActionCandidate("negative", "expand", "", neg_rel)
            pos_features = _numeric_feature_vector(question, pos, memory_relations, candidate_relations, self.stats)
            neg_features = _numeric_feature_vector(question, neg, memory_relations, candidate_relations, self.stats)
            diff = [p - n for p, n in zip(pos_features, neg_features)]
            features.append(diff)
            labels.append(1)
            features.append([-value for value in diff])
            labels.append(0)
        if len(set(labels)) < 2:
            return
        self.model = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")
        self.model.fit(np.asarray(features, dtype=float), labels)
        self.available = True

    def scores(
        self,
        question: str,
        candidates: Sequence[ActionCandidate],
        memory_relations: Sequence[str],
    ) -> Dict[str, float]:
        if not self.available or np is None:
            return {}
        candidate_relations = _ordered_relations(candidates)
        vectors = {
            candidate.action_id: _numeric_feature_vector(question, candidate, memory_relations, candidate_relations, self.stats)
            for candidate in candidates
        }
        pair_features = []
        pair_owner_ids = []
        for candidate in candidates:
            current = vectors[candidate.action_id]
            for other in candidates:
                if other.action_id == candidate.action_id:
                    continue
                other_vector = vectors[other.action_id]
                pair_features.append([left - right for left, right in zip(current, other_vector)])
                pair_owner_ids.append(candidate.action_id)
        if not pair_features:
            return {candidate.action_id: 0.0 for candidate in candidates}

        margins = self.model.decision_function(np.asarray(pair_features, dtype=float))
        wins_by_action: Dict[str, List[float]] = defaultdict(list)
        for action_id, margin in zip(pair_owner_ids, margins):
            wins_by_action[action_id].append(_sigmoid(float(margin)))
        scores = {
            candidate.action_id: _safe_mean(wins_by_action.get(candidate.action_id, []))
            for candidate in candidates
        }
        return scores


def _numeric_feature_vector(
    question: str,
    action: ActionCandidate,
    memory_relations: Sequence[str],
    candidate_relations: Sequence[str],
    stats: RelationStats,
) -> List[float]:
    features = _numeric_features(question, action, memory_relations, candidate_relations, stats)
    return [
        features["lex_overlap"],
        features["lex_jaccard"],
        features["lex_relation_coverage"],
        features["relation_token_count_log"],
        features["candidate_count_log"],
        features["memory_hit"],
        features["memory_count_log"],
        features["relation_train_pos_rate"],
        features["relation_train_log_odds"],
        features["prefix_train_pos_rate"],
        features["prefix_train_log_odds"],
    ]


def _ranker_scores(
    rule_ranker: RuleRelationRanker,
    memory_ranker: MemoryActionSelector,
    pointwise_ranker: PointwiseLogisticRanker,
    pairwise_ranker: PairwiseLogisticRanker,
    question: str,
    candidates: Sequence[ActionCandidate],
    memory_relations: Sequence[str],
) -> Dict[str, Dict[str, float]]:
    method_scores: Dict[str, Dict[str, float]] = {}
    method_scores["rule"] = {candidate.action_id: candidate.score for candidate in rule_ranker.rank(question, candidates)}
    method_scores["memory"] = {candidate.action_id: candidate.score for candidate in memory_ranker.rank(question, candidates)}

    pointwise_scores = pointwise_ranker.scores(question, candidates, memory_relations)
    if pointwise_scores:
        method_scores["pointwise_lr"] = pointwise_scores

    pairwise_scores = pairwise_ranker.scores(question, candidates, memory_relations)
    if pairwise_scores:
        method_scores["pairwise_lr"] = pairwise_scores

    method_scores["listwise_rrf"] = _rrf_scores(candidates, method_scores)
    return method_scores


def _rrf_scores(candidates: Sequence[ActionCandidate], method_scores: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    combined = {candidate.action_id: 0.0 for candidate in candidates}
    source_methods = [method for method in ("rule", "memory", "pointwise_lr", "pairwise_lr") if method in method_scores]
    for method in source_methods:
        ranked = _rank_action_ids(candidates, method_scores[method])
        for rank, action_id in enumerate(ranked, start=1):
            combined[action_id] += 1.0 / (RRF_K + rank)
    return combined


def _rank_action_ids(candidates: Sequence[ActionCandidate], scores: Dict[str, float]) -> List[str]:
    return [
        candidate.action_id
        for candidate in sorted(
            candidates,
            key=lambda item: (-scores.get(item.action_id, float("-inf")), item.relation_id, item.action_id),
        )
    ]


def _rank_metrics(
    candidates: Sequence[ActionCandidate],
    scores: Dict[str, float],
    gold_relation: str,
) -> Tuple[Dict[str, float], Dict[str, object]]:
    ranked = sorted(
        candidates,
        key=lambda item: (-scores.get(item.action_id, float("-inf")), item.relation_id, item.action_id),
    )
    gold_ranks = [idx for idx, action in enumerate(ranked, start=1) if action.relation_id == gold_relation]
    rank = min(gold_ranks) if gold_ranks else None
    top_action = ranked[0] if ranked else None
    metrics = {
        "has_gold_candidate": 1.0 if rank is not None else 0.0,
        "top1": 1.0 if rank == 1 else 0.0,
        "mrr": 1.0 / rank if rank else 0.0,
        "gold_rank": float(rank or 0),
        "gold_margin": _gold_margin(ranked, scores, gold_relation),
    }
    for k in EVAL_KS:
        metrics[f"recall_at_{k}"] = 1.0 if rank and rank <= k else 0.0
        metrics[f"ndcg_at_{k}"] = 1.0 / math.log2(rank + 1) if rank and rank <= k else 0.0
    detail = {
        "top_relation": top_action.relation_id if top_action else "",
        "top_action_id": top_action.action_id if top_action else "",
        "gold_rank": rank,
        "gold_margin": metrics["gold_margin"],
        "top5_relations": [action.relation_id for action in ranked[:5]],
    }
    return metrics, detail


def _gold_margin(candidates_ranked: Sequence[ActionCandidate], scores: Dict[str, float], gold_relation: str) -> float:
    gold_scores = [scores.get(candidate.action_id, 0.0) for candidate in candidates_ranked if candidate.relation_id == gold_relation]
    wrong_scores = [scores.get(candidate.action_id, 0.0) for candidate in candidates_ranked if candidate.relation_id != gold_relation]
    if not gold_scores or not wrong_scores:
        return 0.0
    return max(gold_scores) - max(wrong_scores)


def _utility(
    action: ActionCandidate,
    gold_relation: str,
    gold_chain: Sequence[str],
    memory_relations: Sequence[str],
) -> float:
    if action.relation_id == gold_relation:
        return 1.0
    if action.relation_id in gold_chain[1:]:
        return 0.4
    if _relation_prefix(action.relation_id) == _relation_prefix(gold_relation):
        return 0.2
    if action.relation_id in memory_relations:
        return 0.1
    return 0.0


def _selected_reward_proxy(
    candidates: Sequence[ActionCandidate],
    scores: Dict[str, float],
    gold_relation: str,
    gold_chain: Sequence[str],
    memory_relations: Sequence[str],
) -> Dict[str, float]:
    if not candidates:
        return {"selected_utility": 0.0, "selected_pairwise_win_reward": 0.0}
    ranked = sorted(candidates, key=lambda item: (-scores.get(item.action_id, 0.0), item.relation_id, item.action_id))
    selected = ranked[0]
    utilities = [_utility(action, gold_relation, gold_chain, memory_relations) for action in ranked]
    selected_utility = _utility(selected, gold_relation, gold_chain, memory_relations)
    pairwise = [_sigmoid((selected_utility - other) / 0.25) for other in utilities[1:]]
    return {
        "selected_utility": selected_utility,
        "selected_pairwise_win_reward": _safe_mean(pairwise) if pairwise else selected_utility,
    }


def _summarize_method(metric_rows: Sequence[Dict[str, float]]) -> Dict[str, float]:
    keys = sorted({key for row in metric_rows for key in row})
    return {key: _safe_mean([row[key] for row in metric_rows if key in row]) for key in keys}


def _score_all_preferences(
    rows: Sequence[Dict[str, object]],
    rule_ranker: RuleRelationRanker,
    memory_ranker: MemoryActionSelector,
    pointwise_ranker: PointwiseLogisticRanker,
    pairwise_ranker: PairwiseLogisticRanker,
    memory: MemoryStore,
    memory_top_k: int,
) -> Dict[str, object]:
    credits_by_method: Dict[str, List[float]] = defaultdict(list)
    source_credits_by_method: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for row in rows:
        pos_rel = _row_relation(row, "positive_action")
        neg_rel = _row_relation(row, "negative_action")
        if not pos_rel or not neg_rel:
            continue
        relations = list(dict.fromkeys(list(row.get("candidate_relations", [])) + [pos_rel, neg_rel]))
        actions = [
            ActionCandidate(
                action_id=f"rel::{idx}::{relation}",
                action_type="expand",
                entity_id="",
                relation_id=relation,
            )
            for idx, relation in enumerate(relations)
        ]
        question = str(row.get("question", ""))
        memory_relations = list(row.get("verified_memory_relations", []))
        if not memory_relations:
            memory_relations = _memory_relations_for_record(memory, question, actions, top_k=memory_top_k)
        method_scores = _ranker_scores(
            rule_ranker,
            memory_ranker,
            pointwise_ranker,
            pairwise_ranker,
            question,
            actions,
            memory_relations,
        )
        source = str(row.get("negative_source", "unknown"))
        for method, scores in method_scores.items():
            pos_scores = [scores.get(action.action_id, 0.0) for action in actions if action.relation_id == pos_rel]
            neg_scores = [scores.get(action.action_id, 0.0) for action in actions if action.relation_id == neg_rel]
            pos_score = max(pos_scores) if pos_scores else 0.0
            neg_score = max(neg_scores) if neg_scores else 0.0
            if pos_score > neg_score:
                credit = 1.0
            elif pos_score == neg_score:
                credit = 0.5
            else:
                credit = 0.0
            credits_by_method[method].append(credit)
            source_credits_by_method[method][source].append(credit)

    return {
        method: {
            "num_preferences": len(credits),
            "accuracy_with_ties_half": _safe_mean(credits),
            "by_negative_source": {
                source: {
                    "count": len(values),
                    "accuracy_with_ties_half": _safe_mean(values),
                }
                for source, values in sorted(source_credits_by_method[method].items())
            },
        }
        for method, credits in sorted(credits_by_method.items())
    }


def _preference_scores(
    row: Dict[str, object],
    pos_rel: str,
    neg_rel: str,
    method: str,
    rule_ranker: RuleRelationRanker,
    memory_ranker: MemoryActionSelector,
    pointwise_ranker: PointwiseLogisticRanker,
    pairwise_ranker: PairwiseLogisticRanker,
    memory: MemoryStore,
    memory_top_k: int,
) -> Tuple[float, float]:
    relations = list(dict.fromkeys(list(row.get("candidate_relations", [])) + [pos_rel, neg_rel]))
    actions = [
        ActionCandidate(
            action_id=f"rel::{idx}::{relation}",
            action_type="expand",
            entity_id="",
            relation_id=relation,
        )
        for idx, relation in enumerate(relations)
    ]
    question = str(row.get("question", ""))
    memory_relations = list(row.get("verified_memory_relations", []))
    if not memory_relations:
        memory_relations = _memory_relations_for_record(memory, question, actions, top_k=memory_top_k)
    method_scores = _ranker_scores(rule_ranker, memory_ranker, pointwise_ranker, pairwise_ranker, question, actions, memory_relations)
    scores = method_scores.get(method, {})
    pos_scores = [scores.get(action.action_id, 0.0) for action in actions if action.relation_id == pos_rel]
    neg_scores = [scores.get(action.action_id, 0.0) for action in actions if action.relation_id == neg_rel]
    return (max(pos_scores) if pos_scores else 0.0, max(neg_scores) if neg_scores else 0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="eval_config", default="configs/webqsp_eval100.json")
    parser.add_argument("--train-config", default="configs/webqsp_train500.json")
    parser.add_argument("--run-name", default="")
    args = parser.parse_args()

    eval_cfg = load_config(args.eval_config)
    train_cfg = load_config(args.train_config)
    ensure_output_dirs(eval_cfg)
    ensure_output_dirs(train_cfg)

    train_preferences = list(iter_jsonl(resolve_output_path(train_cfg, "preferences")))
    eval_preferences = list(iter_jsonl(resolve_output_path(eval_cfg, "preferences")))
    eval_records = list(iter_jsonl(resolve_output_path(eval_cfg, "subgraphs")))
    stats = RelationStats.from_preferences(train_preferences)
    print(
        json.dumps(
            {
                "event": "loaded_data",
                "train_preferences": len(train_preferences),
                "eval_preferences": len(eval_preferences),
                "eval_records": len(eval_records),
                "sklearn_available": SKLEARN_AVAILABLE,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    train_memory = MemoryStore.load(resolve_output_path(train_cfg, "memory"))
    eval_memory = MemoryStore.load(resolve_output_path(eval_cfg, "memory"))
    memory_top_k = int(eval_cfg.get("memory", {}).get("top_k", 5))
    rule_ranker = RuleRelationRanker()
    memory_ranker = MemoryActionSelector(eval_memory, top_k=memory_top_k)

    pointwise_ranker = PointwiseLogisticRanker(stats)
    pointwise_ranker.fit(train_preferences)
    pairwise_ranker = PairwiseLogisticRanker(stats)
    pairwise_ranker.fit(train_preferences)
    print(
        json.dumps(
            {
                "event": "fit_rankers",
                "pointwise_lr_available": pointwise_ranker.available,
                "pairwise_lr_available": pairwise_ranker.available,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    method_metric_rows: Dict[str, List[Dict[str, float]]] = defaultdict(list)
    method_reward_rows: Dict[str, List[Dict[str, float]]] = defaultdict(list)
    details = []
    diagnostics = Counter()

    for record in eval_records:
        gold_chain = record.get("gold_relation_chain") or []
        if not gold_chain:
            diagnostics["skipped_no_gold_chain"] += 1
            continue
        candidates = _actions(record.get("candidate_actions") or [])
        if not candidates:
            diagnostics["skipped_no_candidates"] += 1
            continue
        gold_next = str(gold_chain[0])
        candidate_relations = _ordered_relations(candidates)
        memory_relations = _memory_relations_for_record(eval_memory, record["question"], candidates, top_k=memory_top_k)
        if gold_next in candidate_relations:
            diagnostics["gold_in_candidates"] += 1
        if gold_next in memory_relations:
            diagnostics["gold_in_memory_relations"] += 1
        if memory_relations:
            diagnostics["has_verified_memory_relation"] += 1
        diagnostics["evaluated_records"] += 1

        method_scores = _ranker_scores(
            rule_ranker,
            memory_ranker,
            pointwise_ranker,
            pairwise_ranker,
            record["question"],
            candidates,
            memory_relations,
        )

        record_detail = {
            "qid": record["qid"],
            "question": record["question"],
            "gold_next_relation": gold_next,
            "gold_relation_chain": gold_chain,
            "num_candidate_actions": len(candidates),
            "num_candidate_relations": len(candidate_relations),
            "verified_memory_relations": memory_relations,
            "methods": {},
        }
        for method, scores in method_scores.items():
            metrics, method_detail = _rank_metrics(candidates, scores, gold_next)
            rewards = _selected_reward_proxy(candidates, scores, gold_next, gold_chain, memory_relations)
            method_metric_rows[method].append(metrics)
            method_reward_rows[method].append(rewards)
            record_detail["methods"][method] = {**method_detail, **rewards}
        details.append(record_detail)

    print(
        json.dumps(
            {
                "event": "evaluated_records",
                "evaluated_records": diagnostics["evaluated_records"],
                "methods": sorted(method_metric_rows),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    preference_summaries = _score_all_preferences(
        eval_preferences,
        rule_ranker,
        memory_ranker,
        pointwise_ranker,
        pairwise_ranker,
        eval_memory,
        memory_top_k,
    )
    print(
        json.dumps(
            {
                "event": "evaluated_preferences",
                "eval_preferences": len(eval_preferences),
                "methods": sorted(preference_summaries),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    method_summaries = {
        method: {
            **_summarize_method(rows),
            "reward_proxy": _summarize_method(method_reward_rows[method]),
            "preference_eval": preference_summaries.get(method, {}),
        }
        for method, rows in sorted(method_metric_rows.items())
    }

    run_name = args.run_name or f"ranking_signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = output_root(eval_cfg) / "runs" / run_name
    summary = {
        "run_name": run_name,
        "run_dir": str(run_dir),
        "train_config": str(train_cfg["_config_path"]),
        "eval_config": str(eval_cfg["_config_path"]),
        "sklearn_available": SKLEARN_AVAILABLE,
        "pointwise_lr_available": pointwise_ranker.available,
        "pairwise_lr_available": pairwise_ranker.available,
        "num_train_preferences": len(train_preferences),
        "num_eval_preferences": len(eval_preferences),
        "num_eval_records_in": len(eval_records),
        "diagnostics": {
            **dict(diagnostics),
            "candidate_recall": diagnostics["gold_in_candidates"] / max(1, diagnostics["evaluated_records"]),
            "gold_memory_hit_rate": diagnostics["gold_in_memory_relations"] / max(1, diagnostics["evaluated_records"]),
            "verified_memory_coverage": diagnostics["has_verified_memory_relation"] / max(1, diagnostics["evaluated_records"]),
            "train_memory_items": len(train_memory.items),
            "eval_memory_items": len(eval_memory.items),
        },
        "methods": method_summaries,
    }
    write_jsonl(run_dir / "eval_ranking_details.jsonl", details, overwrite=False)
    write_json(run_dir / "summary.json", summary, overwrite=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
