---
title: "面向 0.6B Agentic KGR 的 Memory-guided Subgraph Action Selector"
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
  "@luoGraphR1TowardsAgentic2025",
  "@liuAccurateInterpretableKnowledge2026",
  "@chenSearchonGraphR1TrainingLLMs2026",
  "@huangBackjumponGraphEffectiveEfficient2026",
  "@luReasoningEpisodicMemory2026",
  "@linMemoryR1EnhancingLarge2026",
  "@liuMemoryT1ReinforcementLearning2026",
  "@xiaoMEM1LearningSynergize2026",
  "@yuanKnowledgetoverificationExploringRLVR2026",
  "@yuGraphRAGR1GraphRetrievalaugmented2026",
  "@sunPeakThenCollapseFourInterface2026",
  "@kansalKnowledgeGraphsAre2026",
  "@parkSPARKSelfPlayAsymmetric2026",
  "@wuKnowledgegraphPathsIntermediate2026",
  "@liCoEvoKGCoevolvingKnowledge2026",
  "@tangUniRelRelationCentricKnowledge2025",
  "@guoG1TeachingLLMs2025",
  "@tsangAutoGraphR1EndtoEndReinforcement2026",
  "@manCoevolvingGraphText2026"
]
tags: ["agentic-kgr", "memory", "grm", "small-model", "0.6b", "rl"]
---

# 面向 0.6B Agentic KGR 的 Memory-guided Subgraph Action Selector

## 一句话论点

在 KGQA 场景中，我们验证 agent 能否借助 query-centered subgraph、可验证的 episodic memory 和 memory-aware generative reward，在 RLVR 框架下学习比独立 query 搜索更稳定、更低成本的图上动作选择策略。0.6B 模型只作为快速 pilot；正式实验应扩展到 Qwen2.5-7B 和 Llama3-8B。

## 核心想法

第一阶段不要把模型训练成完全开放式的 KGQA agent。更稳的做法是把它训练成一个受约束的动作选择器：KG、文档证据和 episodic memory 都放在模型外部，模型每一步只根据局部状态，从一组合法动作中选择下一步。

这让模型不需要记住整张 KG，也不需要自由生成长推理链。它只需要学会一个更窄的问题：在当前问题、局部子图、候选关系和 memory hints 给定时，下一步应该扩展哪条边、检索哪类证据、反思当前路径，还是停止回答。0.6B 版本用于快速检验 action space、memory 召回和 reward 设计是否有信号；7B/8B 版本用于正式比较和消融。

## 为什么适合作为第一阶段

这个 idea 小而可测。模型输入是紧凑的局部状态，输出是可解析的动作；每个动作都能被 hard graph verifier 检查，大部分 reward 也能自动计算。

它还形成一条清晰的研究路线：先做 behavior cloning，再加入 memory hints，然后用 GRM reranking 改善候选动作，最后在 action selector 稳定后再进入 online RL。这样第一周就可以验证方向是否有信号，而不是一上来就陷入完整 RL agent 的训练成本。

## 任务定义

输入：

```text
question
seed_entities
compact subgraph observation
relation candidates
top-k memory hints
current trajectory
```

输出：

```text
expand(entity_id, relation_id)
retrieve_text(entity_id or relation_id)
reflect()
stop(answer_entity_id, supporting_path_ids)
```

输出必须受约束并且机器可解析。非法 action 直接给零分或负 reward。

## 数据预处理

不能把整张 KG 直接塞给模型。建议用两层数据管线：

1. 离线索引：
   构建实体别名、关系描述、邻接表、实体 embedding、关系 embedding、文本证据索引，以及 entity-document 映射。

2. 在线子图构造：
   对每个问题先做 entity linking，召回候选关系，扩展有预算限制的 k-hop 邻域，重排候选路径，然后只序列化 top 局部证据。

3. Rollout cache：
   保存每一步 state、action、observation、verifier result、reward component 和 final answer。这个 cache 后续同时服务于 SFT、GRM 和 RL。

初始子图预算：

| 参数 | 初始值 |
|---|---:|
| `max_hop` | 2 或 3 |
| `max_nodes` | 200 |
| `max_edges` | 500 |
| `max_paths` | 20 |
| `max_relation_candidates` | 20 |
| `max_memory_hints` | 5 |

## Memory 设计

这里的 memory 不是把更多文本塞进上下文，而是一个可检索、可验证、可更新的 episodic store。它记录历史探索经验，但不能直接被当作事实使用。

Memory record：

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

推理时只按 question pattern、seed entity type 和 relation overlap 检索 top-k memory hints。每条 memory hint 都必须在当前子图里重新验证，只有验证通过后才允许影响动作选择或 reward。

## GRM 角色

GRM 建议定义为 Generative Reward Model for graph-grounded trajectories。它的职责是生成结构化过程诊断，并把这些诊断转成 soft process reward；它不能替代 hard graph verifier。

因此，本方法更准确的训练定位是 KG-grounded RLVR + memory-aware GRM。RLVR 部分由确定性 verifier 提供可靠奖励，例如 action legality、path validity、answer correctness 和 output format validity；GRM 部分只负责 RLVR 难以覆盖的软过程信号，例如 memory 是否真的减少无效搜索、当前步骤是否带来新证据、是否应该继续扩展或停止。

推荐总 reward：

```text
R = alpha * R_answer
  + beta * R_hard_graph
  + gamma * R_GRM
  + eta * R_memory_utility
  - delta * Cost
```

其中 `R_answer` 评估最终答案是否正确，`R_hard_graph` 检查路径、实体和关系方向是否合法，`R_GRM` 评价 answer support、path faithfulness、evidence coverage、step utility 和 stop quality，`R_memory_utility` 只奖励 memory 带来的可验证收益，例如减少无效 hop、提高 gold-path edge recall 或改善 stop decision。

GRM 输出可以先做成结构化 JSON：

```json
{
  "path_validity": 0.0,
  "evidence_coverage": 0.0,
  "step_utility": 0.0,
  "memory_utility": 0.0,
  "stop_quality": 0.0,
  "diagnosis": "...",
  "reward": 0.0
}
```

如果 hard verifier 判定路径非法，`R_GRM` 应该被封顶或置零。这个 gating 很重要，因为否则模型可能学会用流畅但不忠实的解释欺骗 GRM。

## 最小实验

数据集：

- 先用 MetaQA 做受控 hop 分析，或用 WebQSP 做 Freebase-style KGQA。
- 第一批只使用 500-2,000 个训练问题。
- 固定 held-out split，严禁把测试问题的答案或 gold path 泄漏进 memory。

模型：

- 从 Qwen3-0.6B 或其他 0.5B-0.6B instruct/base 模型开始做 pilot。
- 正式模型使用 Qwen2.5-7B 和 Llama3-8B，并报告相同 prompt/action/parser/reward 设定下的可迁移性。
- 第一阶段先训练 non-thinking action-output mode。
- 等 parser 和 action verifier 稳定后，再测试 thinking mode。

Baselines：

| Baseline | 作用 |
|---|---|
| Rule relation ranker | 检查 learned selector 是否超过简单关系匹配。 |
| No-memory selector | 隔离 memory 的贡献。 |
| Memory selector without GRM | 测试 memory 本身是帮助还是干扰。 |
| Memory selector with GRM reranking | 测试最小方法贡献。 |
| ToG-style beam search | 和更强的规则/workflow baseline 对比。 |

Metrics：

| Metric | 含义 |
|---|---|
| `next_relation_accuracy` | 下一步关系选择是否匹配 gold 或可接受关系。 |
| `gold_path_edge_recall` | 子图和轨迹是否覆盖必要路径边。 |
| `answer_hit_within_budget` | 是否在 step/tool 预算内到达答案。 |
| `invalid_action_rate` | 模型是否输出非法实体、关系或动作 ID。 |
| `steps_to_answer` | learned policy 的搜索效率。 |
| `memory_utility_delta` | 加入 memory hints 相比 no-memory 设置带来的收益。 |

## 与 EoG 和近邻工作的差异

EoG 是最应该优先复现的对象，因为它的 motivation 最近：固定规则和固定示范路径会限制 OOD KG exploration，因此模型需要 reward-guided autonomous exploration。这个 idea 不能只说“我们把 RL 加到 KGQA 上”，因为 Graph-RFT、Graph-R1 和 EoG-like 工作已经覆盖了这个层面的 claim。

更窄也更稳的贡献是：

1. 使用 verified episodic memory 作为可复用探索先验，而不是不受约束的额外上下文。
2. 在 query-centered subgraph 上训练小模型动作选择器，而不是要求 0.6B 模型自由生成完整推理链。
3. 用生成式奖励模型输出结构化轨迹诊断，尤其显式评价 `memory_utility`，再用 hard graph verification 对 reward 封顶。
4. 评估 memory 是否改善低预算图导航：无效扩展更少、gold-path edge recall 更高、stop decision 更好、同等 step budget 下 answer hit 更高。

截至 2026-08-31 的近邻查重：

| 近邻工作 | 已覆盖部分 | 相对本 idea 的缺口 |
|---|---|---|
| EoG | KGR + RL + path-refined reward | 没有显式可复用 memory 模块。 |
| SCPRM | KGQA + cumulative process reward + MCTS | 没有长期 memory，也不聚焦小模型 action selector。 |
| Search-on-Graph-R1 | KG search + cold-start SFT + GRPO/RLVR | 不以跨 query verified memory 或生成式 reward 诊断为中心。 |
| K2V | knowledge-intensive RLVR + process verification | 已经覆盖“知识密集任务可做 RLVR”，但不是 KGQA memory-guided search。 |
| GraphRAG-R1 | GraphRAG + process-constrained RL | 更偏检索过程约束，不研究 episodic graph-search memory。 |
| Peak-Then-Collapse | CWQ + KG tool API + GRPO/RLVR 失稳分析 | 说明 naive RLVR 不稳定，反而支撑 memory-aware dense reward 的必要性。 |
| CoEvoKG | KG + verifiable tasks + persistent evidence memory | 对 memory gap 压力最大；但它不是 CWQ/WebQSP KGQA 内的 memory-aware GRM。 |
| Backjump-on-Graph | reinforced retrospective KG exploration | retrospection 更像搜索控制，不是 verified episodic memory。 |
| REMem, Memory-T1, MEM1, Memory-R1 | RL-trained agent memory | 不做 KG-grounded path verification，也没有图上 hard verifier。 |

## 第一周计划

1. 搭建一个最小 KGQA 环境，支持 `expand`、`verify_path`、`stop` 和 action logging。
2. 实现 query-centered subgraph construction，并缓存第一版 dataset split。
3. 从 shortest paths 或 RoG-style relation paths 生成 silver actions。
4. 在 500-2,000 个样本上 fine-tune 或 prompt-test 一个 0.6B action selector。
5. 从训练轨迹中构建 memory hints，对比 no-memory 和 memory 设置。
6. 训练轻量 GRM，或先用简单 pairwise scorer 对候选 action 做 reranking。

## 当前判断

这是目前仍然值得推进的 idea，但 motivation 需要避开“首次 RLVR+KGR”。更稳的说法是：已有工作说明 KG verifier、路径 reward 和 RLVR 可以用于 KG/GraphRAG；本 idea 进一步检验 verified episodic memory 和 memory-aware GRM 是否能缓解 naive RLVR 在 KGQA 搜索中的 sparse reward、重复错误和训练不稳定问题。

0.6B 模型只用于低成本早期验证。若 memory + GRM reranking 能在 0.6B 上降低 invalid action rate、提高 path recall 和 answer hit within budget，再把同一框架扩展到 Qwen2.5-7B 和 Llama3-8B，才适合作为正式论文实验主线。
