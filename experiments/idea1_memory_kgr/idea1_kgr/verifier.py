from __future__ import annotations

import re
from typing import Iterable, List, Sequence

from .schemas import ActionCandidate, AnswerRef, SubgraphRecord


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def answer_hit(predicted: Iterable[str], gold_answers: Sequence[AnswerRef]) -> float:
    pred_norm = {normalize_text(item) for item in predicted if item}
    gold_norm = {normalize_text(answer.text) for answer in gold_answers if answer.text}
    if not pred_norm or not gold_norm:
        return 0.0
    return 1.0 if pred_norm & gold_norm else 0.0


def legal_action(action: ActionCandidate, subgraph: SubgraphRecord) -> bool:
    if action.action_type != "expand":
        return False
    return any(
        edge.source == action.entity_id and edge.relation == action.relation_id
        for edge in subgraph.edges
    )


def next_relation_reward(action: ActionCandidate, gold_relation_chain: Sequence[str], step_index: int = 0) -> float:
    if not gold_relation_chain or step_index >= len(gold_relation_chain):
        return 0.0
    return 1.0 if action.relation_id == gold_relation_chain[step_index] else 0.0


def hard_graph_reward(action: ActionCandidate, subgraph: SubgraphRecord) -> float:
    return 1.0 if legal_action(action, subgraph) else -1.0


def memory_utility_delta(no_memory_correct: bool, memory_correct: bool) -> float:
    if memory_correct and not no_memory_correct:
        return 1.0
    if no_memory_correct and not memory_correct:
        return -1.0
    return 0.0
