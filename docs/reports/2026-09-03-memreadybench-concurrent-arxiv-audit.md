---
title: "MemReadyBench 同期 arXiv 撞题审计与选题重判"
type: literature-review
status: reviewed
created: "2026-09-03"
scope: "2025-2026 conference papers and arXiv preprints"
tags: ["agent-memory", "benchmark", "novelty-audit", "source-routing", "action-readiness"]
---

# MemReadyBench 同期 arXiv 撞题审计与选题重判

## 0. 审稿式结论

本报告在原 MetaMemBench 方案、用户提供的审稿意见以及截至 2026-09-03 可检索的同期 arXiv 工作基础上重新判断选题。结论是：

> **方向值得继续，但“判断记忆是否足以行动”已经不能作为问题层面的首创。最有希望的剩余空间，是对持久记忆 Agent 做 source-aware action readiness 的因果诊断：不仅判断当前是否能行动，还要识别每个缺失条件应从 memory、world、user 或其他来源获得，并验证路由之后是否真正闭合证据、完成可执行任务。**

原方案中以下单点已经分别被同期工作覆盖：

- evidence sufficiency、retrieve-or-stop；
- commit / probe / fallback；
- verify world / ask user 的来源区分；
- act / abstain 的成对反事实任务；
- memory operation as action；
- stale、conflict、poison、authorization drift；
- 可执行环境、逐决策点评估和失败分解中的大部分组件。

因此，不能再把这些组件中的任何一个单独写成主要创新。修订后的贡献必须来自一组尚未被同一工作共同覆盖的性质：

> **interaction-derived persistent memory × source-aware evidence location × matched source-relocation intervention × decision-point joint gold × executable closure × oracle decomposition**

### 0.1 独立评分

| 维度 | 原 MetaMemBench | 修订后 MemReadyBench | 判断依据 |
|---|---:|---:|---|
| 问题重要性 | 8.5/10 | 8.5/10 | 长程 Agent 会在不完整、过时或冲突记忆上过早执行 |
| 问题层新颖性 | 4.5-5.5/10 | 7.0-8.0/10 | SafeCommit 已直接定义 safe commitment；修订后转向跨来源路由诊断 |
| Benchmark 新颖性 | 6.0/10 | 7.5-8.0/10 | 关键取决于 source-relocation family 和真实 memory stack 诊断 |
| 当前 controller 新颖性 | 4.0-5.0/10 | 暂不作为主贡献 | 现有 monitor/ranker/verifier/gate 是合理组合，但组件均已有先例 |
| 四卡 4090 可行性 | 8.0/10 | 8.5/10 | 主要成本在 simulator、generator、validator 和推理评测 |
| 最大审稿风险 | SafeCommit + AgentAbstain + MCB 的拼接 | 因子化设计是否真正产生新诊断结论 | 必须证明来源迁移不是标签重命名 |

**Go/No-Go 判断：有条件 Go。** 在完成 20 个 base task 的 source-relocation pilot 之前，不投入大规模数据生成或 RL 训练。

## 1. 为什么必须看 arXiv，而不能只看已接收论文

Benchmark 的问题定义和投稿优先权会被公开预印本直接影响。即使 SafeCommit 标注的是 target NeurIPS、MCB 仍是 arXiv preprint，它们已经公开了与本方向高度相近的问题、术语和实验设计；正式写作不能因其尚未接收而忽略。

本次审计采用三层检索：

1. **直接问题词**：memory sufficiency、safe commitment、verify or ask、agent abstention、memory control。
2. **邻近机制词**：tool necessity、clarification under uncertainty、evidence sufficiency、provenance、memory sycophancy。
3. **反向交叉检查**：逐篇检查 problem、action space、gold、environment、counterfactual design 和 limitation，而不只看标题。

精确检索 `MemReadyBench`、`SuffMemBench`、`MemCtrlBench` 和 `MemoryDecisionBench` 暂未发现同名工作；名称可用不等于问题自动新颖，仍须持续监测。

## 2. 同期竞争工作矩阵

### 2.1 P0：直接改变选题表述

| 工作 | 首次提交/出处 | 已经覆盖 | 尚未充分覆盖 | 对本工作的约束 |
|---|---|---|---|---|
| [SafeCommit](https://arxiv.org/abs/2608.04289) | arXiv 2026-08-04；目标 venue 未等于已接收 | safe commitment under memory uncertainty；stale/conflict/incomplete/corrupted；commit/probe/fallback；风险证书；确定性 simulator | 仅 3-6 个显式 latent worlds、固定动作、二值 probe，作者明确称 proof-of-concept；未系统测试真实 LLM memory stack | 不再声称首次提出“行动前判断证据是否充分” |
| [Remember, Verify, or Ask? (MCB)](https://arxiv.org/abs/2608.19564) | arXiv 2026-08-20 | persist/current-only/verify-world/ask-user；world 与 user 两类 source of truth；label 与 tool-call 双评测 | 决策发生在写入/承诺边界；动作被记录但不执行；没有后续 source change 和 task outcome | `VERIFY_WORLD` 必须进入动作空间；差异要落在 query-time sequential acquisition 与 executable closure |
| [AgentAbstain](https://arxiv.org/abs/2607.10059) | arXiv 2026-07-11 | 263 paired tasks、42 executable sandboxes；单因素 act/abstain 翻转；pre-execution/runtime abstention | 干预对象主要是 instruction/tool/environment，不是跨 session 持久记忆及其检索 packet | 成对任务和可执行拒绝不能作为独立创新；要干预 evidence location/state |
| [Router-Mem](https://arxiv.org/abs/2608.01285) | arXiv 2026-08-02 | 轻量 sufficiency router；evidence sufficient 时提前停止，否则深度分析 | QA/效率导向；没有 memory/world/user 的来源路由和外部副作用 | sufficiency router、retrieve-or-stop 已不是空白 |
| [InfMem](https://arxiv.org/abs/2602.02704) | arXiv 2026-02-02；COLM 2026 | PreThink-Retrieve-Write；主动监控 evidence sufficiency；SFT-to-RL；检索、写入和停止 | 超长文档 QA；不研究持久交互记忆和 source-of-truth routing | “System-2 memory control + SFT/RL”不能作为主创新 |
| [MemSyco-Bench](https://arxiv.org/abs/2607.01071) | arXiv 2026-07-01 | 判断 memory 何时应影响决策；拒绝把记忆当事实；作用域、冲突、更新、个性化 | 重点是 sycophancy 与 memory-vs-objective-evidence，不系统评测缺失证据应向何处获取 | 不能泛称首次研究 memory 不应被使用；要突出多来源 acquisition policy |

### 2.2 P1：覆盖关键机制或评测单元

| 工作 | 时间/状态 | 覆盖点 | 保留空间 |
|---|---|---|---|
| [SURE-RAG](https://arxiv.org/abs/2605.03534) | arXiv 2026-05-05；投稿状态不等于接收 | relevance 不等于 sufficiency；support/refute/insufficient；set-level evidence；counterfactual swaps；risk-coverage | RAG QA，不是 persistent memory、外部行动或跨来源路由 |
| [Memory as a Controlled Process (MemCon)](https://arxiv.org/abs/2607.13591) | arXiv 2026-07-15 | memory MDP；retrieve/re-retrieve/plan injection/consolidate/forget；终局反馈学习 | 是待评方法，不是跨系统带 gold decision points 的诊断 benchmark |
| [Oblivion](https://arxiv.org/abs/2604.00131) | arXiv 2026-03-31；EMNLP 2026 Main | 根据不确定性与 memory utility 决定何时读取；read/write 双路径 | 未统一诊断证据位于 memory、world 还是 user |
| [RSCB-MC](https://arxiv.org/abs/2604.27283) | arXiv 2026-04-30 | coding Agent memory controller；多种检索、abstain、ask；风险敏感 bandit | 主要是 smoke-scale artifact；不是通用、因果配对、可执行 benchmark |
| [KnowU-Bench](https://arxiv.org/abs/2604.08455) | arXiv 2026-04-09 | Android 环境、隐藏用户画像、行为日志、user simulator；询问、确认、沉默和个性化执行 | 没有 source-relocation joint gold 和 memory-stack failure decomposition |
| [Calibrate-Then-Act](https://arxiv.org/abs/2602.16699) | arXiv 2026-02-18 | 不确定条件下探索与承诺的 cost-aware 顺序决策 | QA/coding 泛化，不以持久记忆状态为可控变量 |
| [When2Tool](https://arxiv.org/abs/2605.09252) | arXiv 2026-05-10 | 18 个环境中评估工具是否必要；构造 needed/not-needed 边界 | 工具必要性不是 evidence source routing；可作为 world-probe baseline |
| [Structured Uncertainty-guided Clarification](https://arxiv.org/abs/2511.08798) | arXiv 2025-11；2026 修订 | 对 tool parameters 建模不确定性；EVPI 决定 ask/stop；clarification benchmark 与 GRPO | 缺少 persistent memory 和 memory/world/user 联合控制 |

### 2.3 P2：限制命名、来源和方法表述

| 工作 | 时间 | 影响 |
|---|---|---|
| [MetaMem](https://arxiv.org/abs/2602.11182) | arXiv 2026-01-27 | `MetaMem` 已被用于 self-evolving meta-memory，继续使用 MetaMemBench 容易命名冲突 |
| [Decision-Aware Memory Cards / CICL](https://arxiv.org/abs/2606.08151) | arXiv 2026-06-06 | 已按“对下一动作的预期效用”而非相似度组织 memory，decision-aware ranking 不是独立新意 |
| [Agentic Uncertainty Quantification](https://arxiv.org/abs/2601.15703) | arXiv 2026-01-22 | 不确定性作为主动控制信号已有系统表述 |
| [ProvenanceGuard](https://arxiv.org/abs/2606.18037) | arXiv 2026-06 | 在 MCP Agent trace 中做 claim-to-source attribution、allow/block/repair | provenance-aware gate 已有邻近工作；本工作需评估“缺失来源在哪里”，而非仅做来源归因 |

## 3. 对用户提供审稿意见的复核

### 3.1 判断正确的部分

1. **SafeCommit 是最直接竞争者。** 它不仅共享术语，还直接把“available evidence 是否足以 safely act”定义为核心问题。
2. **原四动作缺少 VERIFY_WORLD。** MCB 已证明 world fact 与 user intent 的 source-of-truth 不同，统一塞进 ASK 或 SEARCH 会造成标签语义错误。
3. **原 controller 不是强方法创新。** ranker、setwise verifier、monitor、policy 和 gate 均有邻近机制；应先做 benchmark。
4. **真正资产是 symbolic-world-first 数据生成。** 结构化 world、requirements、memory store 与可执行 validator 能提供稳定 gold，避免依赖 LLM judge。
5. **不能只看最终 success。** lucky execution、unsupported success 和正确路由后的执行失败必须分开。

### 3.2 本报告进一步收紧的部分

用户提供的意见建议增加 `VERIFY_WORLD`，这是必要但还不够。若只把四动作改成五动作，仍可能被评价为 MCB + SafeCommit 的组合。因此 v2 进一步采用两轴因子设计：

- **Source-location axis**：`CURRENT_PACKET / PERSISTENT_MEMORY / WORLD / USER / UNAVAILABLE / NONE_NEEDED`。
- **Integrity axis**：`FRESH / STALE / CONFLICTING / POISONED / AUTHORIZATION_DRIFT`。

这两个轴不能混成单一状态标签。`WORLD + STALE` 与 `MEMORY + STALE` 的正确动作不同；`USER + CONFLICTING` 与 `WORLD + CONFLICTING` 也可能需要不同 probe。

更强的因果约束是：

> 对同一 base task，只移动 decisive requirement 的可获得来源或完整性，任务目标和表面文本尽量不变；正确的第一控制动作必须随干预发生可预测翻转，而所有可解决版本在成功获取证据后应收敛到相同的最终行动与环境终态。

这比“六种 memory-state variant”更能形成独立贡献，因为它同时测试路由正确性和证据闭合后的行为一致性。

## 4. 修订后的问题定义

### 4.1 一句话问题

> **给定来自历史交互的持久记忆、当前工作 packet 和可访问的 world/user 接口，Agent 能否判断当前是否具备行动条件，定位每个缺失要求的可信来源，并在产生外部副作用前选择正确的证据获取或承诺动作？**

### 4.2 两层状态与五动作

行动准备度：

\[
r_t \in \{\text{READY},\text{NOT\_READY},\text{CONFLICTED}\}.
\]

每个未闭合 requirement 的来源位置：

\[
s_{t,j} \in \{\text{CURRENT\_PACKET},\text{PERSISTENT\_MEMORY},\text{WORLD},\text{USER},\text{UNAVAILABLE}\}.
\]

控制动作：

\[
a_t \in \{\text{SEARCH\_MEMORY},\text{VERIFY\_WORLD},\text{ASK\_USER},\text{EXECUTE},\text{ABSTAIN}\}.
\]

第一版将 `DEFER / ESCALATE` 归入 `ABSTAIN` 并在 reason code 中区分，避免动作空间在 MVP 阶段膨胀。

### 4.3 四类 gold 必须分开

1. **Latent world gold**：构造器知道事实真实位于哪里、是否有效。
2. **Observable belief state**：Agent 当前实际可见什么，避免要求其预测不可观测事实。
3. **Admissible action set**：在当前观测下允许的合理动作，不强行设单一 gold。
4. **Oracle best action**：结合成本和后续信息增益，在完整生成图上计算的最优动作。

这种分层能避免一个常见错误：latent truth 在 memory store 并不意味着 Agent 第一步必须知道应搜索；如果它尚无任何可观察线索，SEARCH 和 ASK 可能都属于 admissible set，二者差异由后续 regret 决定。

## 5. 修订后的可防守 Research Gap

建议 Introduction 使用下述受限表述：

> Recent work has studied safe commitment under memory uncertainty, memory sufficiency routing, clarification and abstention, as well as memory operation policies. However, we find no existing benchmark that jointly evaluates whether an agent grounded in interaction-derived persistent memory can (i) identify which action requirement remains unresolved, (ii) locate the authoritative source capable of resolving it across current context, persistent memory, the external world, and the user, (iii) switch its first control action under matched source-relocation interventions, and (iv) converge to the same verified executable outcome after successful evidence acquisition. Existing evaluations usually isolate one boundary, use explicit small world sets, record rather than execute decisions, or conflate retrieval, control, and execution in final task success.

中文版本：

> 近期工作已经分别研究了记忆不确定性下的安全承诺、充分性路由、澄清与拒绝以及 memory operation policy；但截至本次调研，尚未发现一个 benchmark 同时评估：基于交互历史形成持久记忆的 Agent，能否识别尚未闭合的行动条件，判断该条件应由当前上下文、持久记忆、外部世界还是用户提供，在受控的证据来源迁移下正确切换第一控制动作，并在成功获取证据后收敛到同一可验证的执行结果。

注意：正式投稿继续使用 “we find no” 或 “to our knowledge”，不要使用绝对 `first`。

## 6. 与最邻近工作的清晰边界

| 维度 | SafeCommit | MCB | AgentAbstain | MemSyco-Bench | MemReadyBench |
|---|---|---|---|---|---|
| 主要对象 | 安全承诺 controller | 写入/记忆承诺边界 | 何时不行动 | 记忆诱导迎合与冲突 | 行动条件闭合与来源路由 |
| Memory | 显式不确定 memory/world | interaction candidate | 不是主要干预对象 | retrieved memory | cross-session persistent store + packet |
| 动作 | commit/probe/fallback | persist/local/verify/ask | act/abstain/clarify | accept/reject/resolve/use | search/verify/ask/execute/abstain |
| 反事实 | latent worlds 与风险条件 | contrast set | instruction/tool/env 单因素 pair | memory validity/conflict slices | decisive requirement 的 source × integrity relocation |
| 执行 | 小型确定性 simulator | 不执行下游动作 | 42 个 sandbox | 主要评 reasoning/decision | acquisition 与最终 action 都执行 |
| 诊断 | safety certificate | label/tool agreement | paired act-abstain | memory-use behavior | source routing、closure、controller、retriever、executor oracle |

最简洁的区分句：

> **SafeCommit asks whether a proposed action is certifiably safe; MemReadyBench tests whether real memory-grounded agents can discover what evidence is still missing, route to its authoritative source, and reach a verified action-ready state.**

## 7. 必须新增的指标

### 7.1 Readiness 与 Requirement

- Readiness Macro-F1：`READY / NOT_READY / CONFLICTED`。
- Missing Requirement F1：识别未闭合 slot/constraint。
- Evidence Closure F1：当前 packet 是否覆盖一个最小充分 requirement set。
- Calibration：Brier、ECE、risk-coverage。

### 7.2 Source Routing

- **Source-Routing Accuracy**：第一证据获取动作是否指向可解决缺口的来源。
- **Wrong-Source Acquisition Rate**：例如该问用户时反复搜 memory。
- **Evidence-Location Regret**：所选动作相对 oracle 的成本/风险差。
- **Cross-Source Action-Flip Consistency**：source relocation 后动作是否按预期翻转。

### 7.3 Closure 与 Execution

- **Closure-Convergence**：所有可解决变体在获得证据后是否收敛到同一最终 action/state。
- Premature Commit Rate：证据未闭合即执行。
- Unsupported Success：结果偶然正确但证据或授权不合法。
- Exact Tool State / Task Success：由环境 validator 判定。
- Unnecessary Acquisition：已经 READY 仍 SEARCH/VERIFY/ASK。

## 8. 最小闭环及证伪标准

### 8.1 Pilot

- 20 个 base tasks，2 个域：calendar/scheduling、travel/booking。
- 每个 task 至少 6 个 source-location 变体，并选 2-3 个 integrity slices。
- 至少 120 个主 episode，另设 surface paraphrase 和 distractor versions。
- 一个 persistent memory API、一个 world verification API、一个 user simulator、一个带 side effect 的执行 API。
- 先跑规则 oracle、FullHistory、Always 系列、强模型 direct/prompted controller，不训练。

### 8.2 必须通过的 Gate

1. OracleAll 接近 100%，证明 generator/validator 自洽。
2. `FullHistory` 不能轻易饱和；否则任务只是在文本里找答案。
3. 至少两个强 baseline 的 Source-Routing Accuracy 和 Closure-Convergence 显著低于 oracle。
4. source relocation 能稳定造成正确动作翻转，且 surface paraphrase 不应改变动作。
5. 人工对 readiness、missing requirement 和 admissible set 的一致率足够高。
6. 规则指标可覆盖至少 80% 主评测，不依赖单一 LLM judge。

### 8.3 No-Go 条件

- 简单 prompt + FullHistory 在所有来源变体上接近 oracle。
- 任务只能靠人为隐藏显式关键词制造难度。
- `VERIFY_WORLD` 与 `ASK_USER` 在真实例子中无法稳定区分。
- source relocation 后的最终行动本来就不应相同，导致 Closure-Convergence 无法定义。
- benchmark 只能说明“强模型更强”，不能产生 memory-stack 级诊断。

## 9. 方法阶段如何调整

第二阶段仍可以做方法，但不再以通用五模块拼装作为贡献。更有针对性的训练目标是：

1. **Source-transition contrastive objective**：同一 base task 的 memory/world/user 版本形成 hard group，要求第一动作按来源翻转。
2. **Pairwise routing preference**：比较正确来源动作与最具迷惑性的错误来源动作。
3. **Listwise admissible action ranking**：在多个可接受动作下最小化 cost-sensitive regret。
4. **Closure reward**：只有获得完整、当前、授权正确的 requirement set 才给过程奖励。
5. **Executable outcome reward**：最终仍由 exact environment state 验证，不由 ranking score 代替。

先用 prompting/SFT 验证，只有当 sequential exploration 与预算权衡确实构成瓶颈时再上 RL。独立 GRM 不是 MVP 必需品，因为 symbolic gold 和 environment validator 已提供可验证信号。

## 10. 最终建议

### 10.1 名称

推荐：

> **MemReadyBench: Evaluating Source-Aware Action Readiness in Persistent-Memory Agents**

不再推荐 MetaMemBench，因为 `MetaMem` 已有 2026 同名方法，且原名容易让审稿人把工作理解为一般 metacognitive monitoring。

### 10.2 论文主线

1. 现有评测分别覆盖 recall、memory use、safe commitment、abstention、clarification 和 memory control。
2. 真实 Agent 的缺口不是“是否再检索”这一项，而是多个权威来源之间的 evidence acquisition routing。
3. 提出 source-aware action readiness 及其 joint gold。
4. 用 source × integrity 的 matched counterfactual families 形成因果诊断。
5. 在真实 memory stack 与可执行环境中用 oracle interventions 分离 monitor、routing、retrieval 和 execution failure。

### 10.3 一句话决策

> **继续做 benchmark，但从“memory sufficiency/control”改成“source-aware action readiness and evidence acquisition routing”；先用 20-task pilot 证明来源迁移能产生稳定、非平凡、可诊断的行为差异，再决定是否扩展数据和训练 controller。**

## 11. 参考文献与状态说明

本报告中的会议归属仅在论文页面明确标注时写为已接收；“submitted to/target”不视为接收。重点参考：

1. [SafeCommit: Certifying When Memory-Grounded Agents May Safely Act](https://arxiv.org/abs/2608.04289), arXiv, 2026-08-04.
2. [Remember, Verify, or Ask? Cross-Family Evaluation of Memory Commitment in LLM Agents](https://arxiv.org/abs/2608.19564), arXiv, 2026-08-20.
3. [AgentAbstain: Do LLM Agents Know When Not to Act?](https://arxiv.org/abs/2607.10059), arXiv, 2026-07-11.
4. [Stop When Memory Suffices: Evidence-Conditioned Progressive Execution for LLM Agents](https://arxiv.org/abs/2608.01285), arXiv, 2026-08-02.
5. [InfMem: Learning System-2 Memory Control for Long-Context Agent](https://arxiv.org/abs/2602.02704), COLM 2026.
6. [MemSyco-Bench: Benchmarking Sycophancy in Agent Memory](https://arxiv.org/abs/2607.01071), arXiv, 2026-07-01.
7. [SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective RAG](https://arxiv.org/abs/2605.03534), arXiv, 2026-05-05.
8. [Memory as a Controlled Process](https://arxiv.org/abs/2607.13591), arXiv, 2026-07-15.
9. [Oblivion](https://arxiv.org/abs/2604.00131), EMNLP 2026 Main.
10. [KnowU-Bench](https://arxiv.org/abs/2604.08455), arXiv, 2026-04-09.
11. [When2Tool](https://arxiv.org/abs/2605.09252), arXiv, 2026-05-10.
12. [Calibrate-Then-Act](https://arxiv.org/abs/2602.16699), arXiv, 2026-02-18.
13. [MetaMem](https://arxiv.org/abs/2602.11182), arXiv, 2026-01-27.
14. [Decision-Aware Memory Cards / CICL](https://arxiv.org/abs/2606.08151), arXiv, 2026-06-06.
15. [Structured Uncertainty-guided Clarification](https://arxiv.org/abs/2511.08798), arXiv, 2025-11.
16. [Agentic Uncertainty Quantification](https://arxiv.org/abs/2601.15703), arXiv, 2026-01-22.
17. [ProvenanceGuard](https://arxiv.org/abs/2606.18037), arXiv, 2026.
