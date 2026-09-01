from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List

from .memory_store import MemoryStore, relation_tokens, tokenize
from .schemas import ActionCandidate


class RuleRelationRanker:
    def rank(self, question: str, candidates: Iterable[ActionCandidate]) -> List[ActionCandidate]:
        question_tokens = tokenize(question)
        ranked: List[ActionCandidate] = []
        for candidate in candidates:
            overlap = len(question_tokens & relation_tokens(candidate.relation_id))
            score = overlap / max(1, len(relation_tokens(candidate.relation_id)))
            ranked.append(replace(candidate, score=score, meta={**candidate.meta, "rule_score": score}))
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked


class MemoryActionSelector:
    def __init__(self, memory: MemoryStore, top_k: int = 5):
        self.memory = memory
        self.top_k = top_k
        self.rule_ranker = RuleRelationRanker()

    def rank(self, question: str, candidates: Iterable[ActionCandidate]) -> List[ActionCandidate]:
        base = self.rule_ranker.rank(question, list(candidates))
        retrieved = self.memory.retrieve(question, base, top_k=self.top_k)
        memory_relations = {
            relation
            for row in retrieved
            for relation in row["item"].relation_template  # type: ignore[index,union-attr]
        }
        boosted: List[ActionCandidate] = []
        for candidate in base:
            memory_hit = candidate.relation_id in memory_relations
            score = candidate.score + (0.35 if memory_hit else 0.0)
            boosted.append(
                replace(
                    candidate,
                    score=score,
                    meta={
                        **candidate.meta,
                        "memory_hit": memory_hit,
                        "retrieved_memory": [
                            row["item"].memory_id  # type: ignore[index,union-attr]
                            for row in retrieved
                            if candidate.relation_id in row["item"].relation_template  # type: ignore[index,union-attr]
                        ],
                    },
                )
            )
        boosted.sort(key=lambda item: item.score, reverse=True)
        return boosted
