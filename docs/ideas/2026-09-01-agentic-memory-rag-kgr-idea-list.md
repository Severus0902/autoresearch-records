---
title: "利用 Memory 做 Agentic RAG / Agentic KGR 的 Idea List"
type: idea
status: open
created: "2026-09-01"
zotero: ["@yanExploreongraphIncentivizingAutonomous2026a", "@sunThinkongraphDeepResponsible2024", "@luoReasoningGraphsFaithful2024", "@jiangKGagentEfficientAutonomous2025", "@yuGraphRAGR1GraphRetrievalaugmented2026", "@jiangAgenticRagR1Agentic2026", "@trivediInterleavingRetrievalChain2023", "@asaiSelfragLearningRetrieve2024", "@yanCorrectiveRetrievalAugmented2024", "@dongRAGcriticLeveragingAutomated2025", "@gutierrezHippoRAGNeurobiologicallyInspired2025", "@guoLightRAGSimpleFast2025", "@luReasoningEpisodicMemory2026", "@linMemoryR1EnhancingLarge2026", "@xiaoMEM1LearningSynergize2026", "@liuMemoryT1ReinforcementLearning2026", "@maMemChainLearningInterpretable2026"]
tags: ["agentic-rag", "agentic-kgr", "memory", "rlvr", "grm", "idea-list", "research-definition"]
---

# 利用 Memory 做 Agentic RAG / Agentic KGR 的 Idea List

## 总判断

这组 idea 的共同主线不是“做一个带 memory 的 agent”，而是：

> 研究 agent 在可验证的知识密集推理环境中，如何把历史检索/搜索轨迹转化为可复用、可验证、可训练、可归因的 memory，并用 memory 改善后续 query 的搜索决策。

因此，Agentic KGR 和 Agentic RAG 是两个实验场景；真正的方法贡献应放在 **verified memory**、**memory-conditioned online policy**、**memory utility reward** 和 **memory-contrastive training** 上。

## Idea List 总表

| ID | Idea | 一句话问题定义 | 场景 | 优先级 |
|---|---|---|---|---|
| I1 | Memory-Guided Subgraph Action Selector | 解决 agentic KGR 在高 branching、noisy linking 和有限预算下每个 query 从零搜索、重复犯相似局部错误的问题。 | Agentic KGR | 最高 |
| I2 | Memory-Augmented Evidence-Chain RAG | 解决 agentic RAG 在多跳文本问答中反复犯检索分解、证据链组织和过早停止错误的问题。 | Agentic RAG | 最高，作为第二场景 |
| I3 | Hybrid Agentic KGR-RAG with Shared Verified Memory | 解决 KG 不完整和纯文本检索不结构化时，agent 如何在 KG 扩展与文本检索之间做可学习调度的问题。 | KGR + RAG | 高 |
| I4 | Memory-Contrastive Next-Step Policy Learning | 解决模型不知道何时信任 memory、何时忽略 memory，以及如何把 memory 转化为下一步动作偏好的问题。 | 通用训练范式 | 最高，作为核心训练模块 |
| I5 | Memory-Aware GRM under Hard Verification | 解决 hard verifier 奖励稀疏、无法解释 memory 是否真的有用，而纯生成式 reward 又容易被幻觉欺骗的问题。 | Reward / RLVR | 最高，作为核心奖励模块 |
| I6 | Verified Memory Store with Write-Prune-Leakage Control | 解决 memory 容易退化成答案缓存、噪声上下文或 benchmark leakage 的问题。 | Memory infra | 高 |
| I7 | Low-Budget Small-Model Agentic Search Pilot | 解决 0.6B 小模型难以直接开放式推理、但仍需要快速验证 memory 是否有信号的问题。 | 实验切入 | 高 |
| I8 | Unified Verifiable Memory Interface for Agentic Reasoning | 解决 KGR 和 RAG 的 memory 定义不统一、难以迁移和公平消融的问题。 | 框架抽象 | 中高 |

## I1. Memory-Guided Subgraph Action Selector

**一句话问题定义**：解决 agentic KGR 在高 branching、noisy linking 和有限预算下每个 query 从零搜索、重复犯相似局部错误的问题。

**背景**：ToG、RoG、GCR 和 EoG 已经说明 LLM 可以在 KG 上做交互式搜索、relation-path planning、约束解码和 RL-guided path exploration。EoG 尤其接近，因为它用 path-refined reward 鼓励模型探索新的有效 KG reasoning paths。但这些方法大多仍把每个 query 当作独立 episode，没有显式复用训练过程中积累的成功路径、失败扩展和停止经验。

**方案**：把 KGQA 建模为 query-centered subgraph 上的 online action policy。每一步输入 question、seed entity candidates、frontier、candidate relations、trajectory、verifier feedback 和 top-k verified memory hints；输出受控动作：`expand`、`retrieve_text`、`reflect/backtrack`、`stop`。Memory 存 schema-level / trajectory-level 经验，例如 relation path template、failed expansion、stop mistake，而不是具体答案。

**创新点**：

- 把 memory 定义为跨 query 的 verified graph-search experience，而不是 prompt 里的额外上下文。
- 每条 memory hint 必须在当前子图中重新验证，避免把历史路径直接当事实。
- 用 `memory_utility_delta` 衡量 memory 是否减少 invalid hop、提高 gold-path edge recall 或降低 steps-to-answer。
- 适合先用 0.6B 做 action selector pilot，再扩展到 Qwen2.5-7B 和 Llama3-8B。

**推荐 baseline**：ToG、RoG、GCR、EoG、Search-on-Graph-R1、RLVR without memory、verified memory without GRM、GRM without memory。

## I2. Memory-Augmented Evidence-Chain RAG

**一句话问题定义**：解决 agentic RAG 在多跳文本问答中反复犯检索分解、证据链组织和过早停止错误的问题。

**背景**：IRCoT、Self-RAG、CRAG、RAG-Critic 等方法已经把 RAG 从一次性检索推进到多步检索、反思和 critic-guided workflow。GraphRAG-R1、AgenticRag-R1 又进一步接近 RL + retrieval + agent memory。但大多数方法仍没有清楚回答：历史检索轨迹中的哪些经验可以跨 query 复用，怎样验证这些 memory 不是答案缓存，以及如何奖励 memory 的因果贡献。

**方案**：把 RAG 场景定义为 evidence-chain retrieval。Agent 的动作包括 `retrieve`、`rewrite_query`、`read_memory`、`select_evidence`、`verify_evidence`、`answer`、`write_memory`、`prune_memory` 和 `stop`。Memory 存 query decomposition、retrieval strategy、evidence-chain pattern、failure memory 和 stop/continue memory。Verifier 使用 answer EM/F1、supporting fact F1、citation support、retrieval recall@k 和 cost。

**创新点**：

- 把 memory 从“历史文本缓存”改造成 query-conditioned retrieval strategy prior。
- 用 supporting facts 和 citation faithfulness 约束 memory 使用，减少 unsupported answer。
- 构造 empty / shuffled / unverified / verified memory 对比，直接测试 memory 是否有可验证收益。
- 作为 KGR 之外的第二场景，证明方法不是 KG-specific trick。

**推荐 baseline**：BM25/vector RAG、multi-query RAG、IRCoT、Self-RAG、CRAG、RAG-Critic、HippoRAG、LightRAG、GraphRAG-R1、AgenticRag-R1。

## I3. Hybrid Agentic KGR-RAG with Shared Verified Memory

**一句话问题定义**：解决 KG 不完整和纯文本检索不结构化时，agent 如何在 KG 扩展与文本检索之间做可学习调度的问题。

**背景**：真实知识密集推理很少是纯 KG 或纯 RAG。ToG-2、ToG-3、GraphSearch、GraphRAG 一类工作已经显示出趋势：agent 需要同时利用结构化 KG、非结构化文本和多轮 query evolution。这个方向比 I1 更贴近现实系统，但工程复杂度也更高。

**方案**：把环境定义为 `E = {G, D}`，其中 `G` 是 KG，`D` 是文本语料。Agent 可以选择 `expand_kg`、`retrieve_doc`、`rewrite_query`、`link_entity`、`select_path`、`select_span`、`verify` 和 `stop`。Shared memory 同时存 relation path template、entity-linking failure、evidence-chain pattern、source-selection preference 和 stop condition。

**创新点**：

- 让 memory 学会跨源调度：什么时候走 KG，什么时候查文本，什么时候两者互证。
- Reward 同时包含 path validity 和 citation/evidence support，形成 hybrid verifier。
- 可以自然覆盖 incomplete KG、noisy KG 和 document-grounded KGQA。
- 比纯 KGR 更像 agentic RAG / agentic KGR 的交叉方向，但第一版工程风险高。

**推荐 baseline**：ToG-2、ToG-3、GraphSearch、GraphRAG/LightRAG/HippoRAG、RoG、EoG、IRCoT。

## I4. Memory-Contrastive Next-Step Policy Learning

**一句话问题定义**：解决模型不知道何时信任 memory、何时忽略 memory，以及如何把 memory 转化为下一步动作偏好的问题。

**背景**：如果只把 memory 作为 prompt feature，方法会显得牵强，因为模型可能只是读到了更多上下文。已有 ranking 思路中的 pointwise、pairwise、listwise 可以转化为 agentic search 的训练信号，其中 pairwise 最适合逐步搜索，listwise 适合完整路径或证据链排序。

**方案**：构造 memory-contrastive preference data：

```text
(q, s_t, m_verified, a_good) > (q, s_t, m_empty, a_base)
(q, s_t, m_verified, a_good) > (q, s_t, m_unverified, a_bad)
(q, s_t, m_failure, a_avoid) > (q, s_t, m_empty, a_repeat_error)
```

KGR 中 `a_t` 是下一跳 relation/entity/action；RAG 中 `a_t` 是下一次 retrieve/rewrite/select/stop。训练路线是 pointwise legality warm-up -> pairwise next-step ranking -> listwise path/evidence-chain reranking -> online RLVR。

**创新点**：

- 训练目标不是“哪个 action 像 gold”，而是“memory 在什么条件下改变 action preference”。
- 可以显式区分 useful memory、spurious memory、irrelevant memory 和 harmful memory。
- Pairwise 信号便宜，适合 0.6B pilot。
- 能自然接入 online policy，因为每一步 state 都可以构造对比样本。

**推荐 baseline**：no-memory pairwise、random-memory pairwise、unverified-memory pairwise、pointwise-only、listwise-only、RLVR-only。

## I5. Memory-Aware GRM under Hard Verification

**一句话问题定义**：解决 hard verifier 奖励稀疏、无法解释 memory 是否真的有用，而纯生成式 reward 又容易被幻觉欺骗的问题。

**背景**：EoG、SCPRM、GraphRAG-R1 等已有工作已经把路径级或过程级 reward 用到 KGR/GraphRAG；Memory-R1、REMem、MEM1 等也证明 memory operation 可以通过 RL 学习。因此，不能把“RLVR + memory”本身当 novelty。更稳的点是：GRM 是否能生成结构化过程诊断，并且专门评价 memory utility。

**方案**：把 reward 分成 hard verifier 和 soft GRM 两层：

```text
R = R_answer
  + R_hard_validity
  + R_evidence_or_path_support
  + R_GRM_process
  + R_memory_utility
  - Cost
```

GRM 输出结构化 JSON，例如 `path_validity`、`evidence_coverage`、`step_utility`、`memory_utility`、`stop_quality` 和 `diagnosis`。如果 hard verifier 判定 action/path/evidence 不合法，GRM reward 被封顶或置零。

**创新点**：

- 把 GRM 的任务从“给轨迹打分”收窄为“解释 memory 是否带来可验证收益”。
- 通过 hard gating 防止语言奖励模型奖励流畅但不忠实的 rationale。
- 可以比较 DRM、GRM、hard-only RLVR 和 full reward，形成清楚消融。
- 对 KGR 和 RAG 都成立：KGR 用 path verifier，RAG 用 evidence/citation verifier。

**推荐 baseline**：hard-only RLVR、DRM scorer、GRM without hard gating、GRM without memory utility、outcome-only reward。

## I6. Verified Memory Store with Write-Prune-Leakage Control

**一句话问题定义**：解决 memory 容易退化成答案缓存、噪声上下文或 benchmark leakage 的问题。

**背景**：通用 agent memory 可以直接写自然语言反思、偏好和历史事件，但 KGQA/RAG benchmark 对泄漏非常敏感。如果 memory 存了测试答案、gold path、gold evidence 或同源改写问题，性能提升就不能说明 agent 学会了推理策略。

**方案**：定义严格的 memory schema 和生命周期：

```text
read_memory -> verify_memory -> use_memory -> write_memory -> prune_memory
```

Memory 只能由 training trajectories 写入；dev/test 全局 memory 只读。Memory record 包含 question pattern、entity/document type、successful path/evidence pattern、failed action、verifier feedback、utility score、source split 和 timestamp。低 utility、不可验证、诱导错误或疑似泄漏的 memory 被降权或删除。

**创新点**：

- 把 memory safety 变成方法的一部分，而不是实验后补充说明。
- 用 empty/shuffled/unverified/answer-cache memory 做反事实消融，证明收益不是泄漏。
- 为 KGR 和 RAG 统一提供可审计 memory log。
- 适合写成系统贡献和实验协议贡献。

**推荐 baseline**：answer-cache memory、unverified memory、train-only verified memory、test-time write-enabled memory、read-only memory。

## I7. Low-Budget Small-Model Agentic Search Pilot

**一句话问题定义**：解决 0.6B 小模型难以直接开放式推理、但仍需要快速验证 memory 是否有信号的问题。

**背景**：0.6B 不适合一开始就做完整 answer generation 或复杂 free-form CoT，但适合做受控 action selection。你的真实目标可以是 Qwen2.5-7B 和 Llama3-8B；0.6B 的角色是低成本验证 action space、memory retrieval、preference data 和 reward 是否有信号。

**方案**：把小模型限制为输出机器可解析动作。KGR pilot 使用 WebQSP/MetaQA 的 500 到 2000 条样本，动作是 `expand/retrieve/stop`；RAG pilot 使用 HotpotQA/2Wiki 的小子集，动作是 `retrieve/rewrite/select_evidence/stop`。先 SFT，再 pairwise rerank，最后小规模 RLVR。

**创新点**：

- 把小模型变成 search policy，而不是知识生成器。
- 知识留在外部 KG、文档索引和 memory store 中，模型只学习策略。
- 每个动作都可验证，训练闭环快。
- 如果 0.6B 上没有 memory utility 信号，可以尽早止损或调整 memory schema。

**推荐 baseline**：rule ranker、BM25/vector ranker、no-memory action selector、verified-memory action selector、full GRM reranker。

## I8. Unified Verifiable Memory Interface for Agentic Reasoning

**一句话问题定义**：解决 KGR 和 RAG 的 memory 定义不统一、难以迁移和公平消融的问题。

**背景**：如果论文只写 KGR，容易被认为空间太窄；如果直接写通用 memory reasoning，又容易太泛。更稳的路线是提出一个通用 memory interface，并在 KGR 和 RAG 两个可验证场景中实例化。

**方案**：抽象成统一框架：

```text
Input:
  q: question/task
  E: external environment or evidence source
  M: long-term memory store
  V: verifier
  B: budget

Policy:
  pi_theta(a_t | q, state_t, memory_t, verifier_feedback_t)

Memory operations:
  read_memory
  verify_memory
  use_memory
  write_memory
  prune_memory
```

KGR 中 `E=KG`，memory 是 graph-search trajectory；RAG 中 `E=document corpus`，memory 是 evidence-chain trajectory。统一指标是 answer success、support validity、cost 和 memory utility delta。

**创新点**：

- 把 Agentic KGR 和 Agentic RAG 从两个孤立系统变成同一框架下的两个实例。
- 方法贡献不依赖某一个 benchmark 或某一种 KG schema。
- 可以支撑论文题目从 KGR 提升为 verifiable memory-augmented reasoning。
- 风险是框架过大，因此应把 I1 作为主实验，I2 作为第二场景，I8 作为论文叙事骨架。

**推荐 baseline**：KGR-specific baselines + RAG-specific baselines + shared internal ablations。

## 这些 Idea 之间的关系

最适合成论文主线的组合是：

```text
I8 作为总框架
+ I1 作为第一实验场景
+ I2 作为第二实验场景
+ I4 作为训练方法
+ I5 作为 reward 方法
+ I6 作为 memory 安全协议
```

I7 是执行策略，不是单独论文贡献。I3 是更野心的系统扩展，可以放在后续工作或第二篇论文。

## 最推荐的切入组合

当前最稳的第一版不是八个 idea 全做，而是：

| 位置 | 选择 |
|---|---|
| 论文题目方向 | Verifiable Memory-Augmented Agentic Reasoning |
| 主实验场 | I1: Agentic KGR with verified memory |
| 第二实验场 | I2: Agentic evidence-chain RAG with verified memory |
| 核心训练法 | I4: Memory-contrastive next-step policy learning |
| 核心 reward | I5: Verifier-gated memory-aware GRM |
| 防质疑协议 | I6: Write/prune/leakage-controlled memory store |
| 快速验证 | I7: 0.6B action selector pilot |

一句话版本：

> 我们研究 agentic KGR/RAG 中的 verified memory use：让模型在多步搜索中学习何时读取、验证、使用和写回历史轨迹记忆，并用 verifier-gated reward 与 memory-contrastive training 证明 memory 不是答案缓存，而是真正改善了低预算搜索策略。

## 当前排序

按“新意清晰度 + 0.6B 可验证性 + 论文风险”综合排序：

1. **I1 + I4 + I5**：最适合作为第一阶段核心实验，先在 KGR 上验证。
2. **I2 + I4 + I5**：作为第二场景，验证能迁移到 agentic RAG。
3. **I6**：必须做，不然 memory 方向很容易被质疑 leakage。
4. **I8**：适合作为论文总叙事，但不要让实验摊太大。
5. **I3**：有潜力，但工程复杂度高，适合后续扩展。
6. **I7**：不是贡献，但决定能不能快速跑出第一批信号。
