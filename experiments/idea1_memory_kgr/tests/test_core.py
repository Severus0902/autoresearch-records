from __future__ import annotations

import json
from pathlib import Path

from idea1_kgr.data_adapters import parse_webqsp_record
from idea1_kgr.memory_store import build_memory_from_samples
from idea1_kgr.policies import MemoryActionSelector, RuleRelationRanker
from idea1_kgr.schemas import ActionCandidate, Triple
from idea1_kgr.subgraph_builder import SubgraphBuilder


class FakeKG:
    def get_out_edges(self, mid: str, limit: int = 100):
        return [
            Triple(source=mid, relation="people.person.place_of_birth", target="m.city"),
            Triple(source=mid, relation="people.person.profession", target="m.job"),
        ]


def test_webqsp_parser_extracts_question_entities_answers_and_chain():
    sample = parse_webqsp_record(
        {
            "QuestionId": "q1",
            "RawQuestion": "where was Ada born?",
            "TopicEntityMid": "m.ada",
            "TopicEntityName": "Ada",
            "InferentialChain": ["people.person.place_of_birth"],
            "Answers": [{"AnswerArgument": "m.city", "EntityName": "London"}],
        },
        idx=0,
        split="train",
    )

    assert sample.question == "where was Ada born?"
    assert sample.topic_entities[0].mid == "m.ada"
    assert sample.gold_answers[0].text == "London"
    assert sample.gold_relation_chain == ["people.person.place_of_birth"]


def test_webqsp_parser_supports_nested_parses_layout():
    sample = parse_webqsp_record(
        {
            "QuestionId": "q2",
            "RawQuestion": "where is taylor swift from?",
            "topic_entity": {"m.0dl567": "Taylor Swift"},
            "Parses": [
                {
                    "TopicEntityMid": "m.0dl567",
                    "TopicEntityName": "Taylor Swift",
                    "InferentialChain": ["people.person.place_of_birth"],
                    "Answers": [{"AnswerArgument": "m.0zlgm", "EntityName": "Reading"}],
                }
            ],
        },
        idx=0,
        split="test",
    )

    assert sample.topic_entities[0].mid == "m.0dl567"
    assert sample.topic_entities[0].name == "Taylor Swift"
    assert sample.gold_answers[0].text == "Reading"
    assert sample.gold_relation_chain == ["people.person.place_of_birth"]


def test_subgraph_builder_creates_expand_actions():
    sample = parse_webqsp_record(
        {
            "QuestionId": "q1",
            "RawQuestion": "where was Ada born?",
            "TopicEntityMid": "m.ada",
            "InferentialChain": ["people.person.place_of_birth"],
            "Answers": [{"AnswerArgument": "m.city", "EntityName": "London"}],
        },
        idx=0,
        split="train",
    )
    record = SubgraphBuilder(FakeKG(), max_hops=1).build(sample)

    assert record.oracle["gold_answer_visible"] is True
    assert {action.relation_id for action in record.candidate_actions} == {
        "people.person.place_of_birth",
        "people.person.profession",
    }


def test_memory_selector_boosts_verified_relation():
    sample = parse_webqsp_record(
        {
            "QuestionId": "q1",
            "RawQuestion": "where was Ada born?",
            "TopicEntityMid": "m.ada",
            "InferentialChain": ["people.person.place_of_birth"],
            "Answers": [{"AnswerArgument": "m.city", "EntityName": "London"}],
        },
        idx=0,
        split="train",
    )
    memory = build_memory_from_samples([sample])
    candidates = [
        ActionCandidate("a1", "expand", "m.ada", "people.person.profession"),
        ActionCandidate("a2", "expand", "m.ada", "people.person.place_of_birth"),
    ]

    rule_top = RuleRelationRanker().rank("where was Ada born?", candidates)[0]
    memory_top = MemoryActionSelector(memory).rank("where was Ada born?", candidates)[0]

    assert rule_top.relation_id in {"people.person.place_of_birth", "people.person.profession"}
    assert memory_top.relation_id == "people.person.place_of_birth"
