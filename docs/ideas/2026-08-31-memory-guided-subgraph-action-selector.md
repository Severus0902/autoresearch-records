---
title: "Memory-aware KG-RLVR：面向 Agentic KGR 的可验证记忆与生成式过程奖励"
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
  "@manCoevolvingGraphText2026",
  "@shinnReflexionLanguageAgents2023",
  "@wangVoyagerOpenEndedEmbodied2023",
  "@parkGenerativeAgentsInteractive2023",
  "@packerMemGPTTowardsLLMs2023",
  "@xuAMEMAgenticMemory2025",
  "@chhikaraMem0BuildingProductionReady2025"
]
tags: ["agentic-kgr", "memory", "grm", "rlvr", "baseline", "small-model", "0.6b", "rl"]
---

# Memory-aware KG-RLVR：面向 Agentic KGR 的可验证记忆与生成式过程奖励

## 一句话论点

在 KGQA 场景中，我们验证 agent 能否借助 query-centered subgraph、可验证的 episodic memory 和 memory-aware generative reward，在 RLVR 框架下学习比独立 query 搜索更稳定、更低成本的图上动作选择策略。0.6B 模型只作为快速 pilot；正式实验应扩展到 Qwen2.5-7B 和 Llama3-8B。

## 明确 Motivation

ToG、RoG 和 EoG 形成了一条很清楚的技术递进线：ToG 证明 LLM 可以作为 KG 交互式 agent 逐步选择实体和关系；RoG 证明 relation-path planning 可以把 KG 结构显式注入推理过程；EoG 进一步证明 RL 和 path-refined reward 可以激励模型探索固定示范路径之外的有效 KG reasoning paths。这些工作共同说明，agentic KGR 的关键已经不只是“能否访问 KG”，而是模型能否在图上做可学习、可验证、可泛化的搜索决策。

但这些方法大多仍把每个 query 视为一次相对独立的探索 episode。即使训练集中已经出现过相似的 question pattern、relation composition、失败扩展或过早停止错误，模型也没有一个显式机制把这些历史探索经验整理成可复用、可验证、可更新的 memory。对于 WebQSP 和 CWQ 这类最多约 2-4 hop 的 KGQA 数据集，memory 的动机不应写成“路径太长”。真正的问题是：路径虽然不长，但候选实体和候选关系的 branching factor 很大，entity/relation linking 有噪声，spurious path 很多，并且 agent 在有限 step/tool budget 下容易重复犯相似的局部搜索错误。

已有 RLVR + KGR/GraphRAG 工作说明，KG 中的 action legality、path validity、answer correctness 和 retrieval outcome 可以被程序化验证，因此适合构成 hard reward。然而，纯 RLVR reward 往往稀疏、延迟，并且不一定能解释一次搜索为什么失败，尤其难以判断 memory 是否真的帮助了当前推理，还是引入了不可验证的 shortcut。因此，本 idea 的核心 motivation 是：在 KG verifier 提供可靠硬奖励的基础上，引入 verified episodic memory 复用跨 query 搜索经验，并用 memory-aware GRM 提供更细粒度的过程诊断和 dense reward。

## Research Gap

| Gap | 已有方法覆盖到哪里 | 本 idea 要补什么 |
|---|---|---|
| Cross-query memory gap | ToG/RoG/EoG 主要关注单个 query 内的搜索、规划或探索奖励。 | 把历史成功路径、失败扩展、relation pattern 和 stop mistake 存成 verified episodic memory，并在新 query 中重新验证后使用。 |
| Memory-aware reward gap | EoG、SCPRM、GraphRAG-R1 等已有路径级或过程级 reward，但主要评价当前 trajectory。 | 让 GRM 显式评价 `memory_utility`，区分 useful memory-guided exploration 和 spurious memory shortcut。 |
| RLVR stability gap | K2V、Search-on-Graph-R1、Peak-Then-Collapse 等说明 knowledge-intensive/KG setting 可做 RLVR，但 naive RLVR 可能稀疏或失稳。 | 用 hard verifier 保底，用 GRM 提供 dense process signal，用 memory 复用历史探索经验，测试是否提升低预算搜索稳定性。 |
| Non-gap | query -> top-k entity -> subgraph -> action selection 是标准可行 pipeline；0.6B 只是快速验证模型。 | 论文中不把基础 pipeline 或 0.6B 当主要 novelty，而把正式验证放到 Qwen2.5-7B 和 Llama3-8B。 |

## 问题定义

这个 idea 要解决的问题可以定义为 **Memory-aware KG-RLVR for budgeted agentic KGQA**：给定一个自然语言问题、一个外部知识图谱、一个由历史训练轨迹构成的可验证 memory store，以及固定的 step/tool/token 预算，训练一个 agent 在局部子图中选择可验证动作，最终输出答案和支持路径。

形式化地，给定：

```text
q: natural-language question
G = (V, E, R): external knowledge graph
D: optional text/document evidence
M: verified episodic memory built from training trajectories
B = (T, C_tool, C_token): search and inference budget
V_hard: deterministic verifier
```

目标是学习一个策略 `pi_theta(a_t | o_t)`。在第 `t` 步，agent 只能观察到局部状态：

```text
o_t = {
  q,
  seed_entity_candidates,
  current_frontier_entities,
  query_centered_subgraph,
  candidate_relations,
  retrieved_memory_hints,
  trajectory_history,
  verifier_feedback,
  remaining_budget
}
```

agent 从合法动作集合中选择：

```text
a_t in {
  expand(entity_id, relation_id),
  retrieve_text(entity_id or relation_id),
  reflect(),
  stop(answer_entity_id, supporting_path_ids)
}
```

执行动作后，环境返回新的局部子图观察、verifier feedback 和预算消耗。episode 结束时，模型需要输出答案 `y`、支持路径 `P` 和完整轨迹 `tau`。其中 `P` 必须能被 KG 或外部证据验证，不能只依赖模型内部知识。

优化目标可以写成：

```text
max_theta E_{tau ~ pi_theta} [
  R_answer(y)
  + R_hard_graph(tau, P, G)
  + R_GRM(q, tau, M, S_q)
  + R_memory_utility(M, tau)
  - Cost(tau, B)
]
```

其中 `R_hard_graph` 属于 RLVR 的 hard reward，由程序化 verifier 计算；`R_GRM` 和 `R_memory_utility` 属于 dense process reward，用来评价证据覆盖、步骤有效性、停止质量和 memory 是否真的帮助了当前图搜索。

这个问题的核心研究问题是：

| Research question | 具体含义 |
|---|---|
| RQ1: verified memory 是否有用？ | 在相同子图和预算下，历史成功/失败轨迹是否能减少无效扩展并提高 answer hit。 |
| RQ2: memory-aware GRM 是否必要？ | 相比只用 hard RLVR reward，生成式过程奖励是否能更好地区分 useful memory 和 spurious memory。 |
| RQ3: memory 是否会带来泄漏或 shortcut？ | unverified memory 是否提高表面准确率但降低 path faithfulness 或 OOD 泛化。 |
| RQ4: 方法是否能扩展到正式模型？ | pilot 在 0.6B 上验证信号后，Qwen2.5-7B 和 Llama3-8B 是否保留同方向收益。 |

这个问题不包括四件事：第一，不把 entity linking 本身作为主要贡献，只报告 `seed_entity_recall@k`；第二，不要求模型记忆整张 KG，KG 始终作为外部环境存在；第三，不把 WebQSP/CWQ 的 2-4 hop 说成“长程记忆”问题；第四，不把 query-centered subgraph construction 本身当 novelty，而把它作为可验证 action space 的基础设施。

## 核心想法

第一阶段不要把模型训练成完全开放式的 KGQA agent。更稳的做法是把它训练成一个受约束的动作选择器：KG、文档证据和 episodic memory 都放在模型外部，模型每一步只根据局部状态，从一组合法动作中选择下一步。

这让模型不需要记住整张 KG，也不需要自由生成长推理链。它只需要学会一个更窄的问题：在当前问题、局部子图、候选关系和 memory hints 给定时，下一步应该扩展哪条边、检索哪类证据、反思当前路径，还是停止回答。0.6B 版本用于快速检验 action space、memory 召回和 reward 设计是否有信号；7B/8B 版本用于正式比较和消融。

## 方法概览

整体 pipeline 按 query-conditioned navigation 组织：

1. **Entity linking**：从 query 中识别 mention，并为每个 mention 保留 top-k seed entity candidates，而不是只保留 top-1。
2. **Candidate construction**：基于 seed entities 召回候选关系、候选邻居和候选文本证据，形成受预算限制的 legal action space。
3. **Query-centered subgraph**：构造 2-4 hop 局部子图，并记录 oracle recall，确认 gold answer 或 gold path 是否仍在可见子图内。
4. **Verified memory retrieval**：根据 question pattern、seed entity type、relation overlap 和历史 verifier result 检索 top-k memory hints，并在当前子图里重新验证。
5. **Action selection**：模型在 `expand`、`retrieve_text`、`reflect`、`stop` 中选择下一步动作。
6. **RLVR reward**：hard verifier 计算 action legality、path validity、answer correctness、format validity 和 cost。
7. **Memory-aware GRM**：GRM 生成结构化诊断，评价 evidence coverage、step utility、memory utility 和 stop quality；若 hard verifier 判定非法，GRM reward 被封顶或置零。
8. **Memory update**：episode 结束后，只把经过 verifier 标注的成功路径、失败分支、无效 relation 和 stop mistake 写入 memory。

## 为什么适合作为第一阶段

这个 idea 小而可测。模型输入是紧凑的局部状态，输出是可解析的动作；每个动作都能被 hard graph verifier 检查，大部分 reward 也能自动计算。

它还形成一条清晰的研究路线：先做 behavior cloning，再加入 memory hints，然后用 GRM reranking 改善候选动作，最后在 action selector 稳定后再进入 online RL。这样第一周就可以验证方向是否有信号，而不是一上来就陷入完整 RL agent 的训练成本。

## 动作级任务定义

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

## Memory 的切入位置

这里的 memory 主切入点是 **跨 query 的图搜索经验复用**，而不是单个 query 内的 working memory，也不是把 KG 事实长期塞进模型参数。更具体地说，memory 应该进入四个位置：

| 位置 | 输入/输出 | 作用 |
|---|---|---|
| Query 开始时 | `read_memory(q_pattern, seed_entity_types, relation_candidates)` | 给当前子图搜索一个 relation/path prior，减少一开始的盲目扩展。 |
| 每一步扩展前 | `memory_hints + current_frontier -> candidate action rerank` | 帮助模型判断哪些 relation 值得扩展、哪些历史上常是错误分支。 |
| 停止/回退时 | `trajectory + verifier_feedback + memory_hints -> stop/backtrack decision` | 复用“何时继续、何时停止、何时回退”的程序性经验。 |
| Episode 结束后 | `write_memory(q, tau, verifier_result, failure_reason)` | 只把经过 verifier 标注的成功路径、失败分支、无效扩展和 stop mistake 写回 memory。 |

因此，最适合的 memory 不是原始问答样本，也不是完整实体答案，而是 **schema-level / trajectory-level memory**：例如 `question pattern -> relation path template`、`seed entity type -> useful relation prior`、`failed relation expansion -> failure reason`、`stop condition -> verifier evidence`。这类 memory 可以跨 query 复用，同时比直接保存具体答案更不容易造成 test leakage。

通用 LLM agent memory 已经有很多可借鉴机制。Reflexion 把失败后的语言反思写入 episodic memory，Voyager 把可复用行为沉淀成 skill library，Generative Agents 使用 memory stream 和 reflection 组织长期行为经验，MemGPT/Mem0 关注长期记忆的分层管理、抽取和检索，A-MEM 进一步把 memory 组织成可演化的结构化网络。这些工作说明“跨任务/跨 episode 经验复用”不是空白方向。

但它们不能直接搬到 KGQA/KGR 的原因也很明确：

1. **记忆单元不同**：通用 memory 多存自然语言事件、对话偏好或技能描述；KG 推理需要存实体类型、relation sequence、path validity、失败边和 verifier 证据。
2. **检索目标不同**：通用 memory 往往按语义相似度召回；KGR memory 必须 query-conditioned，并且和当前 seed entity、candidate relation、局部子图可达性对齐。
3. **可信度要求不同**：通用 memory 被召回后常直接进入 prompt；这里的 memory 只能作为 hint，必须在当前子图和 KG verifier 中重新验证。
4. **奖励归因不同**：已有 memory 系统通常不回答“这条 memory 是否真的减少了无效 hop 或提高了 path recall”；本方法要显式定义 `memory_utility`，否则 memory 可能只是增加上下文噪声。
5. **泄漏风险不同**：WebQSP/CWQ 这类 KGQA benchmark 容易被近似问题、gold path 或答案实体污染。未经约束的 memory 会把方法变成近邻检索，而不是图上推理策略学习。
6. **动作空间不同**：通用 memory 增强的是生成上下文；本方法要训练的是受约束 action selector，输出必须是合法的 `expand/retrieve/reflect/stop` 动作。

所以可以直接借鉴的是 memory infrastructure：`read/write/update` 接口、reflection/consolidation、向量检索、图式索引、skill/procedural memory、memory operation as action。不能直接照搬的是 memory 的语义和评价方式。本文需要把它改造成 **verified cross-query graph-search memory**，并通过消融证明它不是 prompt 增广、不是答案缓存、也不是普通 RAG。

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

## Pointwise / Pairwise / Listwise 训练信号

Pointwise、pairwise 和 listwise 的 learning-to-rank 思路可以直接借鉴到这个问题里，但它们适合的位置不同。KGQA 的逐跳搜索本质上是一个受约束的序列决策问题：每一步从当前 frontier、candidate relations 和 memory hints 中选择下一跳；完整 episode 又会产生多条候选路径。因此，更合理的设计不是只选一种 ranking loss，而是分层使用。

| 形式 | 在本方法中的对象 | 优点 | 风险 | 推荐用途 |
|---|---|---|---|---|
| Pointwise | 单个 action 或单条 path 的绝对分数：`score(q, s_t, a_t)` 或 `score(q, P)` | 简单、便宜、容易用 verifier 自动标注，可快速冷启动。 | 分数校准困难；多个可行 action 共存时，硬标签会把合理但非 gold 的动作误伤。 | 第一版 action validity / path validity 过滤器，或 GRM 的辅助维度。 |
| Pairwise | 同一 state 下两个 candidate actions 的相对偏好：`a_i > a_j` | 很适合下一跳选择；不要求绝对分数可比；能处理多条可行路径和 spurious path。 | 需要构造足够多的正负 action 对；如果负样本太简单，模型只学会排除非法动作。 | 逐跳 search 的主监督信号，尤其是 memory-guided next-hop reranker。 |
| Listwise | 同一 query 或同一 state 下的一组 candidate paths/actions 的整体排序 | 直接对齐 beam search / global path ranking，能优化 top-k 路径质量。 | 候选集合大时训练贵；候选列表质量会强烈影响学习；早期环境不稳时噪声大。 | 全局路径 rerank、beam rerank、最终 answer path selection。 |

因此，若目标是“找下一跳、逐跳搜索”，第一阶段建议以 **pairwise next-hop preference** 为主。构造方式可以是：在同一个 state `s_t` 中，把能到达 gold path、提高 verifier score、减少无效 hop 或被成功历史 memory 支持且当前可验证的 action 作为 preferred action；把非法 relation、不可达 entity、重复扩展、spurious path 或导致过早 stop 的 action 作为 dispreferred action。

形式化地，pairwise 样本可以写成：

```text
D_pair = {
  (q, s_t, m_t, a_pos, a_neg)
}

where score_theta(q, s_t, m_t, a_pos)
    > score_theta(q, s_t, m_t, a_neg)
```

这里 `m_t` 是当前检索到并重新验证过的 memory hints。这个设计天然适合训练两类模块：第一，训练 action selector 在候选动作中选下一跳；第二，训练 GRM/reranker 判断哪一个候选动作更可能带来可验证收益。

这个设计需要避免一种牵强写法：**不要把 memory 只当成拼到 prompt 里的额外特征**。如果训练样本只是 `score(q, s_t, m_t, a_t)`，而 memory 既不改变候选动作，也不改变偏好标签，也不参与写回更新，那么 reviewer 很容易认为这是普通 retrieval-augmented reranking，不是 memory-guided reasoning。

更强的结合方式是让 memory 参与四件事：

| 结合点 | 具体做法 | 为什么不牵强 |
|---|---|---|
| Memory-conditioned candidate generation | 用 verified memory 中的 relation template、failed expansion 和 stop mistake 生成或剪枝候选 action。 | memory 改变了 search space，而不是只给模型多一段文本。 |
| Memory-contrastive pair construction | 构造 `memory-supported action > no-memory action`、`verified memory > unverified memory`、`successful-memory hint > failed/spurious hint` 等偏好对。 | pairwise 学到的是“何时信任 memory”，而不只是“哪个 relation 像答案”。 |
| Memory utility labeling | 用 rollout 差值标注 memory 是否有用，例如是否减少 invalid hop、提高 gold-path edge recall、减少 steps-to-answer。 | reward 直接衡量 memory 的因果贡献，而不是奖励“读了 memory”。 |
| Memory write-back / pruning | episode 结束后，根据 verifier 和 utility score 决定写入、合并、降权或删除 memory record。 | memory 是一个会被训练过程更新的外部状态，不是静态检索库。 |

因此，pairwise 在这里最好写成 **memory-contrastive next-hop preference**。例如在同一状态 `s_t` 下构造：

```text
(q, s_t, m_good, a_mem) > (q, s_t, m_empty, a_base)
```

只有当 `m_good` 在当前子图中可验证，并且 `a_mem` 的 rollout 比 `a_base` 带来更高的 verifier reward 或更低 cost 时，这个 pair 才成立。反过来，如果某条 memory 虽然语义相似但无法在当前子图验证，或者诱导模型走向 spurious path，就构造负例：

```text
(q, s_t, m_verified, a_good) > (q, s_t, m_unverified, a_bad)
```

这样训练目标就从“排序下一跳”变成“在图搜索中学习何时、如何、以及是否使用 memory”。这才是 memory 和 pairwise/listwise 结合的关键。

全局路径则更适合 listwise。每个 query 可以先用 ToG-style beam search、RoG-style relation planning、shortest-path oracle 或当前 policy rollout 生成候选路径集合：

```text
C_q = {P_1, P_2, ..., P_k}
```

然后根据 answer correctness、path validity、evidence coverage、cost、memory utility 和 stop quality 构造排序标签：

```text
P_i > P_j if
  R_answer(P_i) + R_hard_graph(P_i) + R_GRM(P_i) - Cost(P_i)
  >
  R_answer(P_j) + R_hard_graph(P_j) + R_GRM(P_j) - Cost(P_j)
```

推荐的训练路线是：

1. **Pointwise warm-up**：先训练 action/path validity scorer，保证模型知道什么是合法动作、合法路径和可解析输出。
2. **Pairwise next-hop reranking**：把同一 state 下的候选下一跳组成偏好对，训练 memory-guided action selector。
3. **Listwise path reranking**：对 beam 产生的完整候选路径排序，训练 final path/answer selector。
4. **RLVR fine-tuning**：把 pointwise/pairwise/listwise 学到的 scorer 或 GRM 放回环境，用 hard verifier + GRM + memory utility + cost 做闭环优化。

对 0.6B pilot 来说，最小可行版本可以只做两步：先 pointwise 过滤非法 action，再 pairwise 训练下一跳偏好。listwise 可以放到第二阶段，因为它依赖候选路径生成质量；如果 beam 本身很差，listwise 学到的是候选生成器的偏差，而不是全局推理能力。

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

## Baselines

Baseline 要分三层：基础 KGQA baseline、agentic KGR baseline、RLVR/memory baseline。第一阶段不必全部跑完，但正式实验至少要覆盖每一层，否则很难证明 memory-aware GRM 的贡献。

| Baseline | 类型 | 作用 | 优先级 |
|---|---|---|---|
| Direct / CoT | LLM-only | 检查不使用 KG 时的基础能力。 | 中 |
| Retrieval-only RAG | 非图检索 | 检查文本检索能否覆盖答案，避免 KG 方法吃掉不必要复杂度。 | 中 |
| Rule relation ranker | 弱 KG baseline | 检查 learned selector 是否超过简单关系匹配。 | 高 |
| ToG-style beam search | agentic KGR | 对比手工搜索策略和固定 beam 的图探索能力。 | 高 |
| RoG-style relation path planning | planning KGR | 对比显式 relation path planning 与 learned action selection。 | 高 |
| GCR / constrained decoding | faithful KGR | 对比强约束路径生成，检验本方法是否在 faithfulness 上吃亏。 | 中 |
| EoG | RL agentic KGR | 最关键近邻，验证本方法是否超过 path-refined reward exploration。 | 高 |
| Search-on-Graph-R1 / GraphRAG-R1 | RLVR/GraphRAG 近邻 | 若代码可复现，用来对比已有 graph-search RLVR。 | 中 |
| RLVR without memory | 内部消融 baseline | 只用 hard verifier reward，检验 memory 是否必要。 | 最高 |
| RLVR + unverified memory | 内部风险 baseline | 检验不验证 memory 是否导致 spurious shortcut 或 leakage。 | 高 |
| RLVR + verified memory without GRM | 内部消融 baseline | 隔离 verified memory 的贡献。 | 最高 |
| RLVR + GRM without memory | 内部消融 baseline | 隔离 GRM 的贡献。 | 最高 |
| Full: RLVR + verified memory + memory-aware GRM | 本方法 | 检验 memory 与 GRM 是否形成互补。 | 最高 |

第一周最小 baseline 只需要四个：Rule relation ranker、RLVR without memory、RLVR + verified memory without GRM、Full method。若这四个都没有稳定差异，就暂时不要急着复现 EoG 全量训练。

## 与 EoG 的指标目标

EoG 是最重要的外部强 baseline，但实验目标不应被简化为“所有主指标必须超过 EoG”。更合理的目标分三层：

| 层级 | 目标 | 是否必须 |
|---|---|---|
| 对齐目标 | 在 WebQSP 和 CWQ 上复现 EoG 的设定或构造公平对照，使用相同 backbone、输入 KG、评价脚本和 Hit@1/F1 指标。 | 必须 |
| 内部证明目标 | Full method 必须稳定超过 `RLVR without memory`、`RLVR + verified memory without GRM`、`RLVR + GRM without memory` 等内部消融。 | 必须 |
| 强外部目标 | 在相同或更低 step/tool/token budget 下，超过 EoG 的 Hit@1/F1，或在相近 Hit@1/F1 下显著降低搜索成本并提升 path faithfulness / stability。 | 强烈建议 |

从 EoG 论文 Table 1 看，EoG 在标准 WebQSP/CWQ 上已经很强：Qwen2.5-7B-Instruct 在 WebQSP 上约为 Hit@1 90.7、F1 78.1，在 CWQ 上约为 Hit@1 82.7、F1 73.8；Llama-3.1-8B-Instruct 在 WebQSP 上约为 Hit@1 92.8、F1 81.3，在 CWQ 上约为 Hit@1 86.6、F1 77.9。因此，如果只在普通 i.i.d. split 上拼最终 F1，难度会很高，而且 memory 的必要性不一定明显。

更稳的论文目标是：标准 WebQSP/CWQ 上尽量接近或超过 EoG，同时在更贴合本 idea 的设置中明显超过它，例如：

1. **Budget-controlled setting**：固定更小的 step/tool/token budget，比较 answer hit within budget、steps-to-answer 和 invalid action rate。
2. **Memory-stress setting**：构造 relation composition、question template 或 entity type 的 OOD split，测试跨 query verified memory 是否能复用搜索经验。
3. **Noisy candidate setting**：增加 entity/relation linking 噪声，测试 memory 和 GRM 是否能减少错误分支。
4. **Stability setting**：比较 outcome-only RLVR、EoG-style path reward 和 memory-aware GRM 是否出现 peak-then-collapse 或 reward hacking。
5. **Faithfulness setting**：在答案正确之外，报告 supporting path validity、gold-path edge recall 和 spurious path rate。

因此，正式实验中最理想的结果是：在 WebQSP/CWQ 标准指标上超过 EoG，同时在低预算、OOD、noisy candidate 和训练稳定性指标上也优于 EoG 或 EoG-style baseline。最低可接受结果是：标准 Hit@1/F1 与 EoG 接近，但明显减少搜索成本、提高 path faithfulness，并通过消融证明 verified memory 和 memory-aware GRM 是收益来源。

## Ablation 设计

| Ablation | 目的 | 预期观察 |
|---|---|---|
| 去掉 memory | 测试跨 query 经验是否真的有用。 | 若性能不降，memory gap 在 WebQSP/CWQ 普通 split 上不强。 |
| 使用 unverified memory | 测试 verifier 是否必要。 | 若短期准确率升高但 path faithfulness 下降，说明 memory 有 leakage/shortcut 风险。 |
| 只保留 successful paths | 测试成功经验是否足够。 | 若失败分支消融后无效扩展增加，说明 failed memory 有价值。 |
| 只保留 failed paths | 测试失败经验是否能帮助避坑。 | 若 steps-to-answer 降低，说明 memory 主要提供搜索剪枝。 |
| 去掉 `memory_utility` reward | 测试 GRM 是否真的在评价 memory。 | 若 memory 检索次数增加但收益下降，说明需要显式 utility 约束。 |
| DRM scorer 替代 GRM | 区分简单打分和生成式诊断。 | 若 DRM 性能接近 GRM，GRM 的论文价值要转向可解释性或错误分析。 |
| GRM without hard gating | 测试 verifier gating 是否必要。 | 若 hallucinated rationale 获得高 reward，说明 hard verifier 是必需模块。 |
| Outcome-only RLVR | 测试稀疏最终奖励是否足够。 | 若训练不稳或探索成本高，支撑 dense process reward 的必要性。 |
| 不同模型规模 | 测试方法是否只对小模型有效。 | 0.6B 做 pilot，7B/8B 做正式结果和 scaling 分析。 |

## 实验协议

| 维度 | 设计 |
|---|---|
| 数据集 | WebQSP 和 CWQ 为主；MetaQA 只作为早期受控 hop pilot。 |
| 模型 | Qwen3-0.6B 用于快速验证；Qwen2.5-7B 和 Llama3-8B 用于正式实验。 |
| 子图预算 | 报告 `max_hop`、`max_nodes`、`max_edges`、`max_paths`、`max_relation_candidates` 和 `max_memory_hints`。 |
| Split | 除普通 i.i.d. split 外，增加 relation composition / question template / entity type 的 OOD split。 |
| Memory 防泄漏 | 测试样本答案、gold path 和同源改写问题不得进入 test-time memory。 |
| 训练阶段 | SFT/BC -> RLVR without memory -> RLVR + verified memory -> RLVR + verified memory + GRM。 |
| 成本约束 | 固定 step budget、tool-call budget 和 token budget，避免靠更多搜索堆出结果。 |

Metrics：

| Metric | 含义 |
|---|---|
| `next_relation_accuracy` | 下一步关系选择是否匹配 gold 或可接受关系。 |
| `gold_path_edge_recall` | 子图和轨迹是否覆盖必要路径边。 |
| `answer_hit_within_budget` | 是否在 step/tool 预算内到达答案。 |
| `invalid_action_rate` | 模型是否输出非法实体、关系或动作 ID。 |
| `steps_to_answer` | learned policy 的搜索效率。 |
| `memory_utility_delta` | 加入 memory hints 相比 no-memory 设置带来的收益。 |
| `oracle_subgraph_recall` | 子图构造阶段是否保留 gold answer/path，上界必须单独报告。 |
| `memory_hit_rate` | 检索到的 memory 是否在当前 query 中可验证且相关。 |
| `reward_success_corr` | GRM reward 与 hard verifier / final answer success 的相关性。 |
| `training_stability` | RL 过程中是否出现 peak-then-collapse 或 reward hacking。 |

## 预期 Claim 与证伪标准

| Claim | 需要的证据 | 证伪标准 |
|---|---|---|
| Verified memory 能改善低预算 KG 搜索。 | Full method 在相同 step/tool budget 下超过 RLVR without memory，并提高 path recall 或降低无效扩展。 | 只在 oracle memory 或疑似泄漏设置下提升；普通 verified memory 无收益。 |
| Memory-aware GRM 优于简单 path reward。 | 去掉 `memory_utility` 或用 DRM 替代 GRM 后，stop quality、reward-success correlation 或错误分析明显变差。 | DRM 与 GRM 等价，且 GRM 没有额外稳定性或可解释性收益。 |
| Hard verifier + GRM 比 naive RLVR 更稳定。 | 相比 outcome-only RLVR，训练曲线更少 collapse，invalid action rate 更低。 | Full method 同样出现明显 peak-then-collapse，或 GRM reward 与 verifiable success 脱钩。 |
| 方法可扩展到正式模型。 | Qwen2.5-7B 和 Llama3-8B 上保持同方向收益。 | 收益只存在于 0.6B pilot，正式模型上消失。 |

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

## 实验框架入口

服务器 `/data/wxr` 上已有 Freebase/WebQSP/CWQ 相关资源后的第一版代码框架和 nohup 运行方案，见 [2026-09-01-idea1-memory-guided-kgr-framework.md](../experiments/2026-09-01-idea1-memory-guided-kgr-framework.md)。该文档只定义实验工程结构和运行协议，明确要求先经用户确认后再创建远端工程或执行任何实验。

## 当前判断

这是目前仍然值得推进的 idea，但 motivation 需要避开“首次 RLVR+KGR”。更稳的说法是：已有工作说明 KG verifier、路径 reward 和 RLVR 可以用于 KG/GraphRAG；本 idea 进一步检验 verified episodic memory 和 memory-aware GRM 是否能缓解 naive RLVR 在 KGQA 搜索中的 sparse reward、重复错误和训练不稳定问题。

0.6B 模型只用于低成本早期验证。若 memory + GRM reranking 能在 0.6B 上降低 invalid action rate、提高 path recall 和 answer hit within budget，再把同一框架扩展到 Qwen2.5-7B 和 Llama3-8B，才适合作为正式论文实验主线。

更宽的论文定位见 `docs/ideas/2026-09-01-verifiable-memory-augmented-reasoning.md`。推荐把最终题目上升为 verifiable memory-augmented reasoning，把 KGR/KGQA 作为第一阶段可验证实验场；如果后续能补一个非 KG 的 verifiable reasoning 场景，论文就不必被限定为纯 KGR 工作。
