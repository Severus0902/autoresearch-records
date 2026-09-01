from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .io_utils import read_records
from .schemas import AnswerRef, EntityRef, KGQASample


def _as_list(value: Any) -> List[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_sparql_relations(sparql: str) -> List[str]:
    if not sparql:
        return []
    relations = re.findall(r"(?:ns:|fb:)([A-Za-z0-9_.]+)", sparql)
    return [rel for rel in relations if "." in rel and not rel.startswith("m.")]


def _entity_refs_from_mid_name(mid_value: Any, name_value: Any = None) -> List[EntityRef]:
    mids = _as_list(mid_value)
    names = _as_list(name_value)
    entities: List[EntityRef] = []
    for idx, mid in enumerate(mids):
        if isinstance(mid, dict):
            mid_text = _stringify(mid.get("mid") or mid.get("id") or mid.get("kb_id"))
            name_text = _stringify(mid.get("name") or mid.get("label") or mid.get("text"))
        else:
            mid_text = _stringify(mid)
            name_text = _stringify(names[idx]) if idx < len(names) else ""
        if mid_text or name_text:
            entities.append(EntityRef(mid=mid_text, name=name_text))
    return entities


def _webqsp_answers(raw_answers: Any) -> List[AnswerRef]:
    answers: List[AnswerRef] = []
    for answer in _as_list(raw_answers):
        if isinstance(answer, dict):
            mid = _stringify(
                answer.get("AnswerArgument")
                or answer.get("EntityMid")
                or answer.get("mid")
                or answer.get("id")
            )
            text = _stringify(
                answer.get("EntityName")
                or answer.get("AnswerArgument")
                or answer.get("answer")
                or answer.get("text")
            )
        else:
            mid = ""
            text = _stringify(answer)
        if text or mid:
            answers.append(AnswerRef(text=text or mid, mid=mid))
    return answers


def _cwq_entities(value: Any) -> List[EntityRef]:
    if isinstance(value, dict):
        return [EntityRef(mid=_stringify(k), name=_stringify(v)) for k, v in value.items()]
    entities: List[EntityRef] = []
    for item in _as_list(value):
        if isinstance(item, dict):
            mid = _stringify(item.get("mid") or item.get("id") or item.get("kb_id"))
            name = _stringify(item.get("name") or item.get("label") or item.get("text"))
        else:
            mid = _stringify(item)
            name = ""
        if mid or name:
            entities.append(EntityRef(mid=mid, name=name))
    return entities


def _cwq_answers(value: Any) -> List[AnswerRef]:
    answers: List[AnswerRef] = []
    for item in _as_list(value):
        if isinstance(item, dict):
            text = _stringify(item.get("answer") or item.get("name") or item.get("text") or item.get("label"))
            mid = _stringify(item.get("mid") or item.get("id") or item.get("kb_id"))
        else:
            text = _stringify(item)
            mid = ""
        if text or mid:
            answers.append(AnswerRef(text=text or mid, mid=mid))
    return answers


def parse_webqsp_record(record: Dict[str, Any], idx: int, split: str) -> KGQASample:
    qid = _stringify(record.get("QuestionId") or record.get("qid") or record.get("id") or f"webqsp_{idx}")
    question = _stringify(record.get("RawQuestion") or record.get("question") or record.get("Question"))
    topic_entities = _entity_refs_from_mid_name(
        record.get("TopicEntityMid") or record.get("topic_entity") or record.get("q_entity"),
        record.get("TopicEntityName") or record.get("TopicEntity") or record.get("q_entity_name"),
    )
    relation_chain = [_stringify(x) for x in _as_list(record.get("InferentialChain")) if _stringify(x)]
    sparql = _stringify(record.get("Sparql") or record.get("sparql"))
    if not relation_chain:
        relation_chain = _extract_sparql_relations(sparql)
    return KGQASample(
        dataset="webqsp",
        qid=qid,
        question=question,
        topic_entities=topic_entities,
        gold_answers=_webqsp_answers(record.get("Answers") or record.get("answers") or record.get("answer")),
        split=_stringify(record.get("split") or split),
        gold_relation_chain=relation_chain,
        sparql=sparql,
        raw=record,
    )


def parse_cwq_record(record: Dict[str, Any], idx: int, split: str) -> KGQASample:
    qid = _stringify(record.get("ID") or record.get("qid") or record.get("id") or f"cwq_{idx}")
    question = _stringify(record.get("question") or record.get("RawQuestion") or record.get("Question"))
    sparql = _stringify(record.get("sparql") or record.get("Sparql"))
    relation_chain = [_stringify(x) for x in _as_list(record.get("InferentialChain")) if _stringify(x)]
    if not relation_chain:
        relation_chain = _extract_sparql_relations(sparql)
    topic_entities = _cwq_entities(
        record.get("topic_entity")
        or record.get("q_entity")
        or record.get("entities")
        or record.get("TopicEntityMid")
    )
    return KGQASample(
        dataset="cwq",
        qid=qid,
        question=question,
        topic_entities=topic_entities,
        gold_answers=_cwq_answers(record.get("answer") or record.get("answers") or record.get("Answers")),
        split=_stringify(record.get("split") or split),
        gold_relation_chain=relation_chain,
        sparql=sparql,
        raw=record,
    )


def load_samples(dataset: str, path: str | Path, limit: int = 0, split: str = "unknown") -> List[KGQASample]:
    records = read_records(Path(path))
    parser = parse_webqsp_record if dataset.lower() == "webqsp" else parse_cwq_record
    samples = [parser(record, idx, split) for idx, record in enumerate(records)]
    samples = [sample for sample in samples if sample.question and sample.topic_entities]
    if limit and limit > 0:
        samples = samples[:limit]
    return samples


def samples_to_dicts(samples: Iterable[KGQASample]) -> List[Dict[str, Any]]:
    return [sample.to_dict() for sample in samples]
