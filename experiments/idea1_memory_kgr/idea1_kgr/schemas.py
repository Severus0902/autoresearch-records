from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EntityRef:
    mid: str
    name: str = ""


@dataclass
class AnswerRef:
    text: str
    mid: str = ""


@dataclass
class KGQASample:
    dataset: str
    qid: str
    question: str
    topic_entities: List[EntityRef]
    gold_answers: List[AnswerRef]
    split: str = "unknown"
    gold_relation_chain: List[str] = field(default_factory=list)
    sparql: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Triple:
    source: str
    relation: str
    target: str
    source_name: str = ""
    target_name: str = ""
    direction: str = "out"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionCandidate:
    action_id: str
    action_type: str
    entity_id: str
    relation_id: str = ""
    target_id: str = ""
    score: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubgraphRecord:
    dataset: str
    qid: str
    question: str
    seed_entities: List[EntityRef]
    nodes: List[EntityRef]
    edges: List[Triple]
    candidate_actions: List[ActionCandidate]
    gold_answers: List[AnswerRef]
    gold_relation_chain: List[str] = field(default_factory=list)
    oracle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryItem:
    memory_id: str
    source_qid: str
    source_split: str
    question_pattern: str
    seed_entity_names: List[str]
    seed_entity_mids: List[str]
    relation_template: List[str]
    successful_action: Dict[str, Any]
    failed_actions: List[Dict[str, Any]] = field(default_factory=list)
    verifier_result: Dict[str, Any] = field(default_factory=dict)
    utility: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
