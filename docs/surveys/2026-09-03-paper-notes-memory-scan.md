---
title: "Paper-Notes 2025-2026 Agent Memory Scan"
type: survey
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "paper-notes", "2025", "2026"]
---

# Paper-Notes 2025-2026 Agent Memory 扫描

> **2026-09-03 补充核验**：Paper-Notes 清单外又发现 MemTrace、EvoMemBench、StateMemBench、AuthMem-Bench、TANGLE、PM-Bench、MemGauge 和 LongMemEval-V2 等直接相关工作。它们使本文后半部分的“operation trace + causal diagnosis”方案不再足以单独构成新颖性。更新后的撞题审查见 [Agent Memory 2026 前沿撞题审查](../papers/memory/2026-09-frontier-collision-audit.md)，当前主推荐见 [两阶段研究路线](../ideas/2026-09-03-agent-memory-two-stage-research-roadmap.md)。下文保留作为方向演化记录。

## 扫描范围

来源仓库：<https://github.com/Severus0902/Paper-Notes>

本次只扫描 2025 和 2026 年目录，覆盖 AAAI、ACL、CVPR、ECCV、ICCV、ICLR、ICML 和 NeurIPS。仓库已同步到 `origin/main` 的 `3d15a515`（2026-08-02）。

扫描结果：

- 2025/2026 年目录下共有 23,546 个 Markdown 文件（包含论文笔记、索引和 TODO）。
- 文件名直接命中 `memory / memor / forget / remember / episodic / lifelong / long-term` 的有 460 篇。
- 加入 `experience / reflective / personalization / context management` 并限制在 agent、evaluation、dialogue、RAG、recommender 等相关目录后，得到 180 篇宽口径候选。
- 去除显存优化、训练数据记忆、模型遗忘、视觉缓存、连续学习等同名异义工作后，人工筛出下表 25 个高优先级条目或方法组。

这里的目标不是罗列所有标题，而是判断哪些论文会直接影响我们的 `Strategic Memory Management Benchmark` 选题。

## 最重要的新增发现

### 1. AMemGym 已经做了粗粒度过程诊断

`AMemGym: Interactive Memory Benchmarking for Assistants in Long-Horizon Conversations`，ICLR 2026。

它做 on-policy 长程对话评测，并把失败归因到 `write / read / utilization` 三阶段。这直接说明我们不能再把 gap 写成“现有 benchmark 完全没有过程级评测”。

仍可区分的空间：AMemGym 的诊断是阶段级、对话状态级的，不是对每条 memory operation 给出显式 gold trace；它也没有统一覆盖 hard-negative ignore、权限保护、证据不足拒答和 action-grounded use。

来源：[Paper-Notes](https://github.com/Severus0902/Paper-Notes/blob/main/docs/ICLR2026/information_retrieval/amemgym_interactive_memory_benchmarking_for_assistants_in_long-horizon_conversat.md)；[arXiv](https://arxiv.org/abs/2603.01966)

### 2. Memora 已经重点评测 mutation 与 forgetting

`From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents`，ACL 2026 Findings。

它提出 Memora 和 FAMA，显式增加高频记忆更新、删除和过期信息惩罚。因此“我们首次评测 update/forget”也不能成立。

仍可区分的空间：Memora 主要通过最终 remembering/reasoning/recommending 任务和 forgetting-aware 指标评估记忆演化，没有把完整 memory lifecycle 统一成可逐操作核验的执行轨迹。

来源：[Paper-Notes](https://github.com/Severus0902/Paper-Notes/blob/main/docs/ACL2026/recommender/from_recall_to_forgetting_benchmarking_long-term_memory_for_personalized_agents.md)；[arXiv](https://arxiv.org/abs/2604.20006)

### 3. MemoryAgentBench 已覆盖四类能力，但不是生命周期操作协议

`Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions`，ICLR 2026。

它将能力拆成 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting，并以增量输入协议统一测试 long-context、RAG 和 agentic memory 系统。

仍可区分的空间：它是 capability-level taxonomy，输入主要由长文本 chunk 增量化而来；并不直接标注一条现实交互应该触发 `ADD / UPDATE / NOOP / PROTECT` 中的哪一种操作，也不把 memory operation 与后续 action 的因果链逐步对齐。

来源：[Paper-Notes](https://github.com/Severus0902/Paper-Notes/blob/main/docs/ICLR2026/llm_agent/evaluating_memory_in_llm_agents_via_incremental_multi-turn_interactions.md)；[arXiv](https://arxiv.org/abs/2507.05257)

### 4. MEMTRACK 已经进入跨平台动态状态场景

`MEMTRACK: Evaluating Long-Term Memory and State Tracking in Multi-Platform Dynamic Agent Environments`，NeurIPS 2025 SEA Workshop。

它用 Slack、Linear 和 Git 的异步事件流评测 acquisition、selection、conflict resolution 和 cross-platform reasoning。这和我们计划的“对话 + 工具结果 + 环境事件”高度相近。

仍可区分的空间：它是 workshop 工作，论文笔记标注没有公开代码；评测主要落在最终回答及效率/冗余，没有形成 backend-agnostic 的逐项 memory operation ground truth。

来源：[Paper-Notes](https://github.com/Severus0902/Paper-Notes/blob/main/docs/NeurIPS2025/llm_evaluation/memtrack_evaluating_long-term_memory_and_state_tracking_in_multi-platform_dynami.md)；[arXiv](https://arxiv.org/abs/2510.01353)

### 5. STITCH/CAME-Bench 说明 hard negative 需要做成“上下文相似但意图不同”

`Grounding Agent Memory in Contextual Intent`，ACL 2026。

STITCH 为每个 trajectory step 建立 thematic scope、event type 和 key entity type 三元索引，并用 CAME-Bench 测试“语义相似但上下文不同”的检索干扰。这比随机插入无关噪声更接近我们需要的 hard negative。

对我们的启发：hard negative 应系统控制四种混淆轴，例如同实体不同 episode、同事件不同时间、同主题不同权限、旧版本与新版本，而不是只采样 embedding 相似文本。

来源：[Paper-Notes](https://github.com/Severus0902/Paper-Notes/blob/main/docs/ACL2026/llm_agent/grounding_agent_memory_in_contextual_intent.md)；[arXiv](https://arxiv.org/abs/2601.10702)

## 高优先级论文地图

| 优先级 | 论文 | 出处 | 对我们的用途 | Zotero 状态 |
|---|---|---|---|---|
| P0 | AMemGym | ICLR 2026 | on-policy + write/read/use 诊断，最直接竞品 | 已补 |
| P0 | From Recall to Forgetting / Memora | ACL 2026 Findings | mutation、过期记忆与 forgetting-aware 指标 | 已补 |
| P0 | MemoryAgentBench | ICLR 2026 | 增量输入、四能力 taxonomy、统一 baseline | 已有 |
| P0 | StratMem-Bench | ACL 2026 Long | must/nice/irrelevant 与 strategic use | 已有 |
| P0 | MemBench | ACL 2025 | factual/reflective、capacity、efficiency | 已补 |
| P0 | MEMTRACK | NeurIPS 2025 SEA Workshop | 跨 Slack/Linear/Git 的动态状态追踪 | 已补 |
| P0 | Grounding Agent Memory in Contextual Intent / STITCH | ACL 2026 | 上下文意图 hard negatives、CAME-Bench | 已补 |
| P1 | Memory-T1 | ICLR 2026 | evidence selection + answer/grounding/time reward | 待补 |
| P1 | MemSearcher | ACL 2026 | RL 学习 search 中的 memory rewrite | 已补 |
| P1 | R2D2 | ACL 2025 | reflective agentic memory 与 replay | 待补 |
| P1 | In Prospect and Retrospect | ACL 2025 | 长期个性化对话中的反思式管理 | 待补 |
| P1 | A-MEM | NeurIPS 2025 | linked-note memory organization baseline | 已有但在其他分类 |
| P1 | Agentic Plan Caching | NeurIPS 2025 | procedural/plan memory 与效率指标 | 待补 |
| P1 | Contextual Experience Replay | ACL 2025 | 从历史经验自改进 | 待补 |
| P1 | TReMu | ACL 2025 | 多 session temporal memory reasoning | 待补 |
| P1 | Memory is Reconstructed, Not Retrieved / MRAgent | ICML 2026 | 主动图记忆重构，而非一次性 top-k | 待补 |
| P1 | AdaMEM | ICML 2026 | episode 内按状态动态刷新经验策略 | 待补 |
| P1 | MEM1 | ICLR 2026 | memory-reasoning 协同与长程效率 | 待补 |
| P1 | REMem | ICLR 2026 | episodic memory reasoning | 待补 |
| P1 | Sculptor | ICLR 2026 | active context management | 待补 |
| P1 | StructMem / TiMem / APEX-MEM | ACL 2026 | 结构化、时间分层、半结构化 memory baseline | 待补 |
| P2 | AnchorMem / CLAG / HiGMem / HyperMem | ACL 2026 | 关联、聚类、层次与超图存储方法 | 待补 |
| P2 | Mem^p | ACL 2026 | procedural memory 类型扩展 | 待补 |
| P2 | Topology Matters | ACL 2026 | multi-agent memory leakage / privacy | 待补 |
| P2 | Unveiling Privacy Risks in LLM Agent Memory | ACL 2025 | protect/permission 维度的安全依据 | 待补 |

## 对 Research Gap 的修订

旧表述“现有 benchmark 缺少过程级 memory management 评测”已经过宽，因为 AMemGym、Memora、MemoryAgentBench、MEMTRACK 和 StratMem-Bench 分别覆盖了其中一部分。

建议改成：

> Recent benchmarks separately evaluate strategic memory use, write/read/utilization failures, mutation-aware forgetting, incremental memory capabilities, and cross-platform state tracking. However, these dimensions remain fragmented across incompatible settings and are mostly evaluated through final responses or coarse failure attribution. There is still no unified multi-session benchmark with explicit operation-level ground-truth traces that causally links what an agent should write, update, ignore, retrieve, protect, and use to its downstream answer or action.

中文：

> 近期 benchmark 已分别覆盖策略性记忆使用、write/read/utilization 失败诊断、面向 mutation 的遗忘、增量记忆能力和跨平台状态追踪，但这些维度分散在不兼容的场景与协议中，并且多数仍通过最终响应或粗粒度归因进行评估。当前仍缺少一个统一的 multi-session benchmark：为每一步提供显式的 memory operation ground truth，并把 agent 应该写入、更新、忽略、检索、保护和使用的记忆，与后续回答或行动结果建立可核验的因果链。

## 选题边界建议

为了避免与 AMemGym 和 Memora 正面重合，第一版应明确三个边界：

1. **显式 operation trace**：每个 event 都标注期望的 `ADD / UPDATE / IGNORE / PROTECT`，每个 query/action 都标注 required、supportive、irrelevant、stale 和 forbidden evidence。
2. **组合压力测试**：同一样本同时出现更新、hard negative、权限与证据不足，而不是每个能力单独出题。
3. **因果诊断**：分别运行 oracle-write、oracle-retrieval、oracle-use 等受控设置，定量区分 memory backend、retriever 和 reader/actor 的责任。

在这个定义下，我们不是宣称第一次评测某个单独能力，而是第一次把分散能力统一成一个可逐操作核验、可做因果归因、可公平比较不同 memory backend 的协议。这版故事比“又一个长期记忆 QA benchmark”更稳。

## 下一步阅读顺序

1. AMemGym：先确认它的 write/read/utilization 诊断是否需要内部 memory 可见性，以及能否迁移到外部 backend。
2. Memora：拆解 mutation 生成、过期事实标注和 FAMA，判断哪些指标可复用。
3. MemoryAgentBench：复用 incremental ingestion 接口与 baseline adapter。
4. STITCH/CAME-Bench：复用 contextual hard-negative 构造原则。
5. StratMem-Bench：把 must/nice/irrelevant 扩展成 required/supportive/irrelevant/stale/forbidden。
6. MEMTRACK：借鉴跨平台事件 schema，但第一版只实现轻量文本环境。
