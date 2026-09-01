from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Iterable, List, Protocol, Tuple

from .schemas import ActionCandidate, EntityRef, KGQASample, SubgraphRecord, Triple


NOISY_RELATION_PREFIXES = (
    "common.topic.",
    "type.object.",
    "kg.object_profile.",
    "freebase.",
)


class KGAdapterProtocol(Protocol):
    def get_out_edges(self, mid: str, limit: int = 100) -> List[Triple]:
        ...


def _mid_like(value: str) -> bool:
    return value.startswith("m.") or value.startswith("g.")


def _entity_name(sample: KGQASample, mid: str) -> str:
    for entity in sample.topic_entities:
        if entity.mid == mid:
            return entity.name
    return ""


class SubgraphBuilder:
    def __init__(
        self,
        kg: KGAdapterProtocol,
        max_hops: int = 2,
        max_nodes: int = 200,
        max_edges: int = 500,
        edge_limit_per_entity: int = 80,
        max_relation_candidates: int = 30,
    ):
        self.kg = kg
        self.max_hops = max_hops
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.edge_limit_per_entity = edge_limit_per_entity
        self.max_relation_candidates = max_relation_candidates

    def build(self, sample: KGQASample) -> SubgraphRecord:
        nodes: "OrderedDict[str, EntityRef]" = OrderedDict()
        edges: List[Triple] = []
        seen_edges: set[Tuple[str, str, str]] = set()
        frontier = [entity.mid for entity in sample.topic_entities if entity.mid]

        for entity in sample.topic_entities:
            if entity.mid:
                nodes[entity.mid] = entity

        for _hop in range(self.max_hops):
            next_frontier: List[str] = []
            for entity_id in frontier:
                if len(edges) >= self.max_edges or len(nodes) >= self.max_nodes:
                    break
                try:
                    out_edges = self.kg.get_out_edges(entity_id, limit=self.edge_limit_per_entity)
                except Exception as exc:
                    out_edges = [
                        Triple(
                            source=entity_id,
                            relation="__kg_query_error__",
                            target=str(exc),
                            direction="error",
                        )
                    ]
                for edge in out_edges:
                    key = (edge.source, edge.relation, edge.target)
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)
                    edges.append(edge)
                    if _mid_like(edge.target) and edge.target not in nodes:
                        nodes[edge.target] = EntityRef(mid=edge.target, name=edge.target)
                        next_frontier.append(edge.target)
                    if len(edges) >= self.max_edges or len(nodes) >= self.max_nodes:
                        break
            frontier = next_frontier
            if not frontier:
                break

        actions = self._candidate_actions(edges)
        oracle = self._oracle_stats(sample, edges)
        return SubgraphRecord(
            dataset=sample.dataset,
            qid=sample.qid,
            question=sample.question,
            seed_entities=sample.topic_entities,
            nodes=list(nodes.values()),
            edges=edges,
            candidate_actions=actions,
            gold_answers=sample.gold_answers,
            gold_relation_chain=sample.gold_relation_chain,
            oracle=oracle,
        )

    def _candidate_actions(self, edges: Iterable[Triple]) -> List[ActionCandidate]:
        seen: set[Tuple[str, str]] = set()
        actions: List[ActionCandidate] = []
        for edge in edges:
            if edge.direction == "error" or not edge.relation:
                continue
            if edge.relation.startswith(NOISY_RELATION_PREFIXES):
                continue
            key = (edge.source, edge.relation)
            if key in seen:
                continue
            seen.add(key)
            action_id = f"expand::{edge.source}::{edge.relation}"
            actions.append(
                ActionCandidate(
                    action_id=action_id,
                    action_type="expand",
                    entity_id=edge.source,
                    relation_id=edge.relation,
                    target_id=edge.target,
                )
            )
            if len(actions) >= self.max_relation_candidates:
                break
        return actions

    def _oracle_stats(self, sample: KGQASample, edges: List[Triple]) -> Dict[str, object]:
        edge_relations = {edge.relation for edge in edges}
        answer_mids = {answer.mid for answer in sample.gold_answers if answer.mid}
        graph_targets = {edge.target for edge in edges}
        gold_relations = set(sample.gold_relation_chain)
        visible_relations = gold_relations & edge_relations
        return {
            "gold_answer_visible": bool(answer_mids & graph_targets) if answer_mids else None,
            "gold_relation_visible": bool(visible_relations) if gold_relations else None,
            "gold_relation_recall": len(visible_relations) / len(gold_relations) if gold_relations else None,
            "num_nodes": len({edge.source for edge in edges} | {edge.target for edge in edges}),
            "num_edges": len(edges),
        }
