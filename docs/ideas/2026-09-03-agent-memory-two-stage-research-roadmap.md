---
title: "Agent Memory 两阶段研究路线：Benchmark 到 Method"
type: research-roadmap
status: proposed
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "scientific-agent", "research-memory", "method"]
---

> **方向更新（2026-09-03）**：通用 benchmark 主线已进一步收缩为“记忆充分性监控与查询时控制”，以避免与 StratMem-Bench、MemoryArena、MemOps、MemCon 等近期工作重叠。完整方案见 [`2026-09-03-metamembench-agentic-memory-control-proposal.md`](./2026-09-03-metamembench-agentic-memory-control-proposal.md)。本文件中的 ResearchLedgerBench 保留为可选的科研领域 stress test，不再作为当前第一优先级。

# Agent Memory 两阶段研究路线

## 最终建议

不再优先做通用的 `Strategic Memory Management Benchmark`。截至 2026-09-03，MemTrace、EvoMemBench、StateMemBench、AuthMem-Bench、TANGLE、PM-Bench 和 MemGauge 已经分别覆盖 operation trace、统一 memory evolution、状态更新、权威、冲突、未来意图与阶段风险。

当前最推荐的两阶段主线是：

1. **第一阶段：ResearchLedgerBench**，评价科研 agent 的跨 session、跨 artifact、跨版本记忆是否保持科学有效性。
2. **第二阶段：LedgerMem**，在 benchmark 暴露的主要失败上，构建 provenance-、version- 和 dependency-aware 的科研记忆方法。

工作名可继续调整；这里的重点是问题定义，不以“首个”或“首次”作为未经验证的贡献表述。

## 一句话问题定义

> 现有 scientific-agent benchmark 主要评价一次性文献检索、论文复现、数据分析或角色交接，而现有 agent-memory benchmark 主要评价对话事实和通用任务经验；它们尚不能充分衡量长期科研 agent 是否能维护 hypothesis-code-data-config-run-result-claim 的版本化依赖，并在上游 artifact 改变时正确更新下游结论与行动。

更短版本：

> Can a long-running research agent remember not only what happened, but which results and claims are still valid under the current code, data, and configuration state?

## Research Gap

相关工作已经做到：

- AutoResearchBench：复杂 scientific literature discovery。
- Beyond Memory Leaderboards：完整论文的 budgeted evidence restoration。
- CORE-Bench/ScienceAgentBench：计算复现与数据驱动发现。
- Scientific-RAM：research role 之间的 obligation-aware handoff。
- LongMemEval-V2/EvoMemBench：跨轨迹环境经验与 knowledge/execution memory。
- StateMemBench：current/superseded state。
- MemTrace：operation-level execution tracing 与 post-hoc attribution。

仍未被上述工作共同解决的是：科研结论不是孤立事实，而是一个依赖链。`claim C` 可能只在 `commit v3 + dataset d2 + config s7 + run r12` 下成立；如果 commit v4 修复数据泄漏，旧 run 即使真实发生过，也不再能支持 C。普通 recency update、top-k retrieval 或 post-hoc log tracing都不能自动表达这种科学有效性。

因此 gap 应写成：

> Existing scientific-agent benchmarks evaluate literature discovery, one-shot reproduction, data-driven analysis, or role-specific handoffs, while agent-memory benchmarks evaluate factual recall, state evolution, experience reuse, and pipeline failures. However, long-running research requires a different memory contract: results and claims remain valid only under specific, versioned dependencies among papers, hypotheses, code, data, configurations, and runs. The reviewed benchmarks do not yet provide a controlled evaluation of whether an agent can maintain this dependency-aware research state, propagate invalidation after upstream changes, and use only currently valid evidence in subsequent decisions and reports.

## 第一阶段 Idea List

| 优先级 | Idea | 一句话定义 | 判断 |
|---|---|---|---|
| A | **ResearchLedgerBench** | 测试科研 agent 能否维护版本化 artifact 依赖、传播失效并生成可复现行动 | **最推荐**；问题清楚，贴合已有 Zotero/Git/MD/server 工作流 |
| B | Benchmark-of-Benchmarks for Agent Memory | 测试现有 memory benchmark 在 reader、judge、预算、ingestion 和随机种子变化下的排名稳定性 | 可做短论文/analysis；Beyond Memory Leaderboards 和 benchmark audit 已有邻近工作 |
| C | Counterfactual Memory Utility | 通过移除/替换 memory 检查其对行动和结果的实际贡献 | 有价值，但 CICL、MemTrace、MemGauge 与 experience-following 已接近 |
| D | Generic Operation-Trace Benchmark | 为 ADD/UPDATE/DELETE/RETRIEVE/USE 提供 trace | 不建议；与 MemTrace、AgeMem、Memory-R1 重合明显 |
| E | Authority/Conflict Memory Benchmark | 测来源权威、冲突保留和澄清策略 | 不建议单做；AuthMem-Bench、TANGLE、StateMemBench 已占位 |
| F | Prospective Agent Memory | 测延迟意图和 future cue 触发 | 不建议单做；PM-Bench 已直接覆盖 |
| G | Cross-Platform Work Memory | Slack/Git/Docs/issue 事件流 | 可作为场景，但 MEMTRACK 已接近；必须加入科学 artifact validity 才有区分 |

## 第一阶段：ResearchLedgerBench

### 1. Benchmark 对象

每个 episode 是一个持续多 session 的小型计算研究项目。信息从四类表面进入系统：

- `literature`：论文结论、方法假设、数据限制和引用。
- `research notes`：idea、假设、决策、TODO、失败解释。
- `repository`：commit、diff、配置文件、脚本与环境依赖。
- `execution`：命令、日志、checkpoint、指标、错误和服务器状态。

底层 gold 不是一段对话，而是一个 typed research ledger：

```text
Hypothesis -> ExperimentSpec -> CodeCommit
                         |-> DatasetSnapshot
                         |-> Config
                         |-> Environment
ExperimentSpec -> Run -> Result -> Finding -> Claim
PaperEvidence ---------------------------> Claim
CodeCommit(new) --invalidates/supersedes-> Run/Result/Claim
```

### 2. 数据 Schema

每个节点至少包含：

- `artifact_id`：稳定标识。
- `artifact_type`：paper/claim/hypothesis/decision/commit/dataset/config/run/result/finding。
- `created_at` 与 `valid_time`：记录时间和科学有效时间分开。
- `source_uri`：paper URL、Git commit、文件路径或日志路径。
- `content`：可读文本或结构化值。
- `authority`：direct observation、tool output、user hypothesis、model inference、external paper。
- `status`：active/superseded/invalidated/unresolved。
- `dependencies`：depends_on/supports/refutes/supersedes/invalidates/derived_from。

operation 标签使用科研语义：

- `CREATE`：产生新 hypothesis、run、finding 或 claim。
- `REVISE`：内容更新但身份连续。
- `SUPERSEDE`：新版本替代旧版本，旧记录仍可追溯。
- `INVALIDATE`：上游变化使下游证据失去支持力。
- `LINK`：建立依赖、支持、反驳或派生关系。
- `RETRIEVE/CITE`：为当前任务恢复最小充分证据。
- `ABSTAIN/REQUEST`：依赖不全或冲突不可解时拒绝下结论并请求缺失信息。

### 3. 七类任务

1. **Current Research State Recovery**：恢复当前有效假设、实验状态和结论，过滤旧版本。
2. **Reproducible Run Reconstruction**：选择正确 commit、dataset、config、seed、checkpoint 和命令重建一次 run。
3. **Claim Validity Checking**：判断某 claim 当前是 supported、refuted、invalidated 还是 unresolved。
4. **Invalidation Propagation**：给出代码 bug、数据污染或 metric 修正，找出所有受影响 run/result/finding/claim。
5. **Evidence-to-Claim Grounding**：返回支持结论的最小 evidence closure，并给出可核验来源。
6. **Negative-Result Reuse**：面对新实验计划，识别已失败且条件相同的尝试，避免无意义重复；条件改变时不能错误阻止重试。
7. **Next-Experiment Decision**：在预算约束下选择能区分当前竞争假设的下一实验，并引用仍有效的依据。

第一版优先完成 1-5。第 6-7 类需要更复杂 action evaluation，可放到扩展集。

### 4. 数据构造方案

推荐采用 **结构化世界生成 + 多表面渲染 + 人工核验**，而不是直接抓取混乱真实实验记录：

1. 先用代码生成完整 research dependency graph，所有状态和失效关系天然可验证。
2. 将同一 graph 渲染成 paper notes、Markdown log、Git commit/diff、shell log 等异构文本。
3. 系统随机插入近似配置、旧 commit、失败 run、复制日志和只有局部不同的 hard negatives。
4. 人工核查自然度、唯一可解性和 evidence closure；生成器和 seed 全部公开。
5. 再补一个小型 real/semi-real split，来自公开 ML repo 的 commit、issue、实验表与 release note，验证合成结论是否外推。

MVP 建议：3 个研究域，50 个 project episodes，每个 10-20 sessions、40-100 artifacts、5-8 个 evaluation tasks，总计约 300-400 条问题/行动。规模不求大，先保证每个答案都能从 ledger 自动验算。

### 5. Hard Negative 设计

- 同一实验名称，不同 commit。
- 同一 commit，不同 dataset split 或 preprocessing。
- 同一配置，不同 seed；单次偶然结果与聚合结果冲突。
- 旧 metric 计算有 bug，新 metric 修复后数值改变。
- paper 中的外部 claim 与当前项目实证不一致。
- 用户 hypothesis、模型推断和工具实测表面相似但 authority 不同。
- 失败原因相同但环境版本已变化，应允许重新尝试。

这些 hard negatives 比随机无关文本更像科研 agent 真正会犯的错。

### 6. Baseline

- `NoMemory`：确认任务确实依赖历史。
- `FullHistory`：强 long-context 对照。
- `OracleEvidence`：确认固定 reader 有能力完成任务。
- `BM25`、dense retrieval、BM25+dense hybrid。
- session summary 与 rolling summary。
- flat structured JSON/SQLite ledger。
- Mem0 或 ADD/UPDATE/DELETE/NOOP memory。
- A-MEM-style linked notes。
- AgentRunbook-C-style filesystem + coding agent search。

所有 baseline 固定 reader、输出预算与可见 source，复杂方法不能靠返回更多 token 取胜。

### 7. Metrics

- `Current-State Accuracy`：当前有效对象是否正确。
- `Validity Macro-F1`：supported/refuted/invalidated/unresolved。
- `Dependency Closure P/R/F1`：失效或支持传播范围是否完整。
- `Artifact Recall@k / nDCG`：取回正确版本 artifact 的能力。
- `Stale Evidence Rate`：输出证据中旧版本比例。
- `Provenance Precision`：citation 是否真正指向支持来源。
- `Reproduction Exactness`：commit/config/data/command 等字段全匹配。
- `Action Success`：可执行任务的最终状态。
- `Efficiency`：输入/输出 token、p50/p95 latency、storage、LLM calls。
- `Rank Stability`：reader、judge、预算和随机种子变化后的系统排名相关性。

不使用单一总分掩盖失败。主表按五个核心任务报告，并给 accuracy-cost Pareto frontier。

### 8. 必须做的因果控制

- `NoMemory < NativeMemory < OracleEvidence` 应形成合理能力梯度；否则样本或 harness 失效。
- `OracleState + native retrieval`、`native state + oracle retrieval` 区分写入与读取。
- 删除 decisive artifact 后任务应失败；加入无关 artifact 不应改变答案。
- 对同一 graph 做表面措辞改写，结果应保持稳定。
- 对 commit/config 交换做 paired test，确保模型不能靠 topic 词猜答案。
- 公开原始 outputs、配置、模型版本、prompt、seed 和失败样本。

这里与 MemTrace 的区别是：控制环境允许实际 replay intervention，不只是对真实复杂 pipeline 做理想化归因。

### 9. 论文贡献形式

1. 定义 `versioned scientific validity memory`，将科研 memory 从文献召回扩展到 artifact dependency maintenance。
2. 提供多表面、跨 session 的 ResearchLedgerBench 和可执行 gold ledger。
3. 提供预算匹配、reader 固定、oracle intervention 与 rank-stability 协议。
4. 系统分析现有 memory backend 在 stale result、invalidation propagation 与 reproducibility state 上的失败。

### 10. Go/No-Go Gate

继续完整数据构造前，pilot 必须满足：

- NoMemory 明显低于 OracleEvidence，证明 memory necessity。
- FullHistory 不能轻易饱和全部任务；否则增加 artifact 数和版本干扰。
- 至少两种 baseline 在不同任务上排序不同，证明 benchmark 不是单一检索题。
- 人工对 gold validity 与 dependency closure 的一致率足够高。
- 绝大多数指标可规则化，LLM judge 只处理开放式 next-experiment quality。

## 第二阶段：LedgerMem Method

第二阶段不要先决定“再做一个图 memory”。让第一阶段的 failure profile 决定模块。

### 方法骨架

1. **Typed Ingestion**：把 paper、note、commit、config、run 和 result 转成保留 source span 的 typed event。
2. **Bitemporal Versioning**：同时记录何时写入和事实在哪段实验状态下有效，不覆盖历史。
3. **Dependency Maintenance**：显式预测 depends_on/supports/refutes/supersedes/invalidates。
4. **Task-Conditioned Evidence Assembly**：根据当前任务组装最小充分 dependency closure，而非普通 top-k。
5. **Validity Gate**：回答或行动前检查 evidence 是否来自当前版本，缺字段时 abstain/request。

### 按失败选择创新点

| Benchmark 主失败 | 第二阶段方法 |
|---|---|
| artifact 写入/类型错误 | trace-supervised typed writer |
| supersession/invalidation 漏传 | dependency propagation model 或规则+LLM hybrid |
| hard negative 检索错误 | pairwise reranker；listwise evidence-set selector |
| 证据正确但 claim 错 | validity verifier 与 abstention policy |
| 成本过高 | learned budget/router 与缓存 |

### 训练路线

1. **训练前 baseline**：先做 deterministic ledger + BM25/dense + rule-based validity，证明结构本身有价值。
2. **SFT**：用 benchmark gold operation/edge/validity trace 训练 0.6B 做流程 smoke test，再用 Qwen 2.5 7B/Llama 3 8B 做正式实验。
3. **排序学习**：下一 artifact 选择用 pairwise hard-negative ranking；完整 evidence closure 用 listwise/setwise objective。结果/行动奖励仍用规则化 validity、exactness 和 success，不用排序分数替代最终任务 reward。
4. **RL 可选**：只有 SFT 与排序后仍存在长程决策/停止问题，再用 GRPO/GSPO。reward 可由 operation correctness、dependency closure、final action success、stale penalty、token cost 组成；无需先训练独立 GRM。

### 两篇论文如何承接

- Benchmark 论文提出对象、数据、协议和 failure taxonomy。
- Method 论文只针对 benchmark 揭示的主瓶颈，避免“为了配套 benchmark 硬造一个全功能系统”。
- Benchmark 的公开 test split 保持冻结，method 开发只用 train/dev，减少自家方法与自家数据互相过拟合的质疑。

## 当前最先做的三件事

1. 写出 10 个 research ledger 的手工 gold graph，每个只含 8-12 个 artifacts，用来验证 schema 是否表达得了真实科研变化。
2. 实现 5 个核心任务的 deterministic evaluator，以及 NoMemory/FullHistory/OracleEvidence 三个 sanity baselines。
3. 用现有 autoresearch 文档、Git commit 和实验日志只做 schema 演练；正式公开数据优先来自可授权的合成或公开项目，避免把私人服务器记录直接发布。
