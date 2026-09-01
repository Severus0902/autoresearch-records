from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .io_utils import iter_jsonl, write_jsonl
from .schemas import ActionCandidate, KGQASample, MemoryItem


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text or "")}


def relation_tokens(relation: str) -> set[str]:
    return tokenize(relation.replace(".", " ").replace("_", " "))


def question_pattern(question: str) -> str:
    text = re.sub(r"\b[mMgG]\.[A-Za-z0-9_]+\b", "<entity>", question)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


class MemoryStore:
    def __init__(self, items: Sequence[MemoryItem] | None = None):
        self.items = list(items or [])

    @classmethod
    def load(cls, path: str | Path) -> "MemoryStore":
        p = Path(path)
        if not p.exists():
            return cls()
        items = [MemoryItem(**row) for row in iter_jsonl(p)]
        return cls(items)

    def save(self, path: str | Path, overwrite: bool = False) -> int:
        return write_jsonl(Path(path), (item.to_dict() for item in self.items), overwrite=overwrite)

    def retrieve(self, question: str, candidates: Iterable[ActionCandidate], top_k: int = 5) -> List[Dict[str, object]]:
        q_tokens = tokenize(question)
        candidate_relations = {candidate.relation_id for candidate in candidates if candidate.relation_id}
        scored = []
        for item in self.items:
            pattern_score = _jaccard(q_tokens, tokenize(item.question_pattern))
            memory_relations = set(item.relation_template)
            relation_score = 1.0 if memory_relations & candidate_relations else 0.0
            utility_score = float(item.utility.get("delta_gold_path_edge_recall", 0.0))
            score = 0.55 * pattern_score + 0.35 * relation_score + 0.10 * utility_score
            if score > 0:
                scored.append({"score": score, "item": item})
        scored.sort(key=lambda row: row["score"], reverse=True)
        return scored[:top_k]


def build_memory_from_samples(samples: Iterable[KGQASample]) -> MemoryStore:
    items: List[MemoryItem] = []
    for idx, sample in enumerate(samples):
        if not sample.gold_relation_chain:
            continue
        first_relation = sample.gold_relation_chain[0]
        item = MemoryItem(
            memory_id=f"{sample.dataset}_{sample.split}_{idx:06d}",
            source_qid=sample.qid,
            source_split=sample.split,
            question_pattern=question_pattern(sample.question),
            seed_entity_names=[entity.name for entity in sample.topic_entities if entity.name],
            seed_entity_mids=[entity.mid for entity in sample.topic_entities if entity.mid],
            relation_template=sample.gold_relation_chain,
            successful_action={
                "type": "expand",
                "relation": first_relation,
            },
            verifier_result={
                "path_valid": True,
                "answer_reached": True,
                "source": "gold_or_silver_relation_chain",
            },
            utility={
                "delta_gold_path_edge_recall": 1.0,
                "delta_invalid_action": -1.0,
            },
        )
        items.append(item)
    return MemoryStore(items)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
