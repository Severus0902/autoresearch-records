---
title: "Memory-guided Subgraph Action Selector for 0.6B Agentic KGR"
type: idea
status: open
created: "2026-08-31"
zotero: [
  "@sunThinkongraphDeepResponsible2024",
  "@luoReasoningGraphsFaithful2024",
  "@jiangKGagentEfficientAutonomous2025",
  "@gutierrezHippoRAGNeurobiologicallyInspired2025",
  "@songPlanThenRetrieve2026",
  "@yanExploreongraphIncentivizingAutonomous2026a",
  "@luoGraphR1TowardsAgentic2025"
]
tags: ["agentic-kgr", "memory", "grm", "small-model", "0.6b", "rl"]
---

# Memory-guided Subgraph Action Selector for 0.6B Agentic KGR

## Core Idea

The first tractable idea is not to train a 0.6B model as a full open-ended KGQA agent. Instead, train it as a constrained action selector over query-centered subgraphs. The KG, document evidence, and episodic memory stay outside the model; the model only decides the next action from a small legal action set.

## Why This Is a Good First Cut

This idea is small enough to validate quickly because the model does not need to memorize the KG or generate long explanations. It receives a compact local state and chooses one parseable action. Every action can be checked by a hard graph verifier, and most rewards can be computed automatically.

It also creates a clean research line: start with behavior cloning, add memory hints, add GRM reranking, then move to online RL only after the action selector is stable.

## Task Formulation

Input:

```text
question
seed_entities
compact subgraph observation
relation candidates
top-k memory hints
current trajectory
```

Output:

```text
expand(entity_id, relation_id)
retrieve_text(entity_id or relation_id)
reflect()
stop(answer_entity_id, supporting_path_ids)
```

The output should be constrained and machine-parseable. Invalid actions receive zero or negative reward.

## Data Preprocessing

Do not feed the full KG to the model. Use a two-layer data pipeline:

1. Offline index:
   Build entity aliases, relation descriptions, adjacency lists, entity embeddings, relation embeddings, text evidence indexes, and entity-document mappings.

2. Online subgraph construction:
   For each question, run entity linking, retrieve relation candidates, expand a bounded k-hop neighborhood, rerank paths, and serialize only the top local evidence.

3. Rollout cache:
   Save each state, action, observation, verifier result, reward component, and final answer. This cache becomes the training source for SFT, GRM, and RL.

Initial subgraph budget:

| Parameter | Initial Value |
|---|---:|
| `max_hop` | 2 or 3 |
| `max_nodes` | 200 |
| `max_edges` | 500 |
| `max_paths` | 20 |
| `max_relation_candidates` | 20 |
| `max_memory_hints` | 5 |

## Memory Design

Use memory as a verified episodic store, not as raw context stuffing.

Memory record:

```json
{
  "question_pattern": "...",
  "seed_entity_types": ["..."],
  "successful_relation_path": ["..."],
  "failed_paths": [["..."]],
  "supporting_fact_ids": ["..."],
  "verifier_result": "valid",
  "failure_reason": ""
}
```

At inference time, retrieve only top-k memory hints by question pattern, seed entity type, and relation overlap. Every memory hint must be rechecked against the current subgraph before it can affect reward.

## GRM Role

The Graph-grounded Reward Model (GRM) should provide soft process reward. It should not replace hard graph verification.

Recommended reward:

```text
R = alpha * R_answer
  + beta * R_hard_graph
  + gamma * R_GRM
  + eta * R_memory_utility
  - delta * Cost
```

GRM judges whether the current action or trajectory improves answer support, path faithfulness, evidence coverage, step utility, stop quality, and source switching. If the hard verifier says the path is illegal, GRM reward should be capped or set to zero.

## Minimal Experiment

Dataset:

- Start with MetaQA for controlled hop analysis, or WebQSP for Freebase-style KGQA.
- Use 500-2,000 training questions first.
- Keep a fixed held-out split and prevent answer/gold-path leakage into memory.

Model:

- Start with Qwen3-0.6B or another 0.5B-0.6B instruct/base model.
- First train in non-thinking action-output mode.
- Only test thinking mode after the parser and action verifier are stable.

Baselines:

| Baseline | Purpose |
|---|---|
| Rule relation ranker | Checks whether the learned selector beats simple relation matching. |
| No-memory selector | Isolates memory value. |
| Memory selector without GRM | Tests whether memory alone helps or hurts. |
| Memory selector with GRM reranking | Tests the proposed minimal contribution. |
| ToG-style beam search | Compares against a stronger rule/workflow baseline. |

Metrics:

| Metric | Meaning |
|---|---|
| `next_relation_accuracy` | Whether the next selected relation matches a gold or acceptable relation. |
| `gold_path_edge_recall` | Whether the subgraph and trajectory cover required path edges. |
| `answer_hit_within_budget` | Whether the answer is reached before the step/tool budget is exhausted. |
| `invalid_action_rate` | Whether the model emits invalid entity/relation/action IDs. |
| `steps_to_answer` | Efficiency of the learned policy. |
| `memory_utility_delta` | Improvement from retrieved memory hints versus no-memory setting. |

## First Week Plan

1. Build a tiny KGQA environment with `expand`, `verify_path`, `stop`, and action logging.
2. Implement query-centered subgraph construction and cache the first dataset split.
3. Generate silver actions from shortest paths or RoG-style relation paths.
4. Fine-tune or prompt-test a 0.6B action selector on 500-2,000 examples.
5. Add memory hints from training trajectories and compare no-memory versus memory settings.
6. Train a lightweight GRM or use a simple pairwise scorer to rerank candidate actions.

## Decision

This is the recommended first idea because it is small, measurable, and expandable. It can produce an early result even before full RL: if memory + GRM reranking improves action validity, path recall, and answer hit within budget for a 0.6B model, the direction is worth scaling to GRPO/PPO and harder datasets.

