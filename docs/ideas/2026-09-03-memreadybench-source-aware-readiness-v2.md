---
title: "MemReadyBench：持久记忆 Agent 的来源感知行动准备度评测"
type: research-proposal
status: current-recommended
version: "v2"
created: "2026-09-03"
supersedes: "2026-09-03-metamembench-agentic-memory-control-proposal.md"
tags: ["agent-memory", "benchmark", "action-readiness", "source-routing", "counterfactual-evaluation"]
---

# MemReadyBench：持久记忆 Agent 的来源感知行动准备度评测

## 0. 方案重判

原 MetaMemBench 提出的“判断当前记忆是否足以行动，并在 SEARCH/ASK/EXECUTE/ABSTAIN 间控制”的方向是重要的，但截至 2026-09-03，SafeCommit、MCB、AgentAbstain、Router-Mem、InfMem、SURE-RAG、MemCon 和 MemSyco-Bench 已分别覆盖其大部分问题与机制。

本版本不再争夺一般的 memory sufficiency 或 memory control，而把问题收紧为：

> **当行动依赖的证据可能位于当前上下文、持久记忆、外部世界或用户时，Agent 能否识别尚未闭合的要求，把信息获取动作路由到正确的权威来源，并只在证据闭合后执行？**

项目名称改为：

> **MemReadyBench: Evaluating Source-Aware Action Readiness in Persistent-Memory Agents**

## 1. 问题来源

### 1.1 SafeCommit 已占据“何时安全承诺”

[SafeCommit](https://arxiv.org/abs/2608.04289) 已把 memory uncertainty 下的 premature commitment 形式化为 safe commitment，并在 `commit / probe / fallback` 之间选择。因此不能再声称首次研究“记忆是否足以行动”。它的局限是显式小型 latent-world set、固定 action/safety map 和 proof-of-concept simulator，尚未系统诊断自然语言持久记忆系统。

### 1.2 MCB 已占据 world/user 来源边界

[MCB](https://arxiv.org/abs/2608.19564) 要求模型在 persist、current-only、verify-world 和 ask-user 之间选择，说明变化的世界事实与只有用户知道的意图不能用同一个 ASK/SEARCH 标签处理。但 MCB 发生在写入/记忆承诺边界，且不执行下游 acquisition 和 task action。

### 1.3 AgentAbstain 已占据 paired act/abstain evaluation

[AgentAbstain](https://arxiv.org/abs/2607.10059) 用 263 对任务和 42 个 sandbox 测试 act/abstain 翻转。因此“单因素反事实 + 可执行拒绝”不是新意。其干预对象主要是 instruction、tool 或 environment，而非持久 memory 中决定性证据的位置和状态。

### 1.4 Sufficiency、memory control 和 memory skepticism 均已有工作

- [Router-Mem](https://arxiv.org/abs/2608.01285) 已训练 sufficiency router 决定提前停止还是深度分析。
- [InfMem](https://arxiv.org/abs/2602.02704) 已用 PreThink-Retrieve-Write 和 SFT-to-RL 控制证据检索、写入与停止。
- [SURE-RAG](https://arxiv.org/abs/2605.03534) 已证明 relevance 不等于 set-level sufficiency。
- [MemCon](https://arxiv.org/abs/2607.13591) 已把多种 memory operation 建模为 MDP。
- [MemSyco-Bench](https://arxiv.org/abs/2607.01071) 已测试 memory 何时不应作为事实或不应主导决策。

因此，新问题必须同时包含持久记忆、多个权威来源、来源迁移干预、顺序信息获取和可执行闭合，不能依靠单个已有机制支撑新颖性。

## 2. 一句话 Research Gap

> **现有工作分别评估安全承诺、记忆充分性、澄清、拒绝和 memory operation，但尚缺少一个面向交互生成的持久记忆 Agent 的统一诊断 benchmark：它能在同一任务的受控反事实版本中移动决定性证据的来源，评估 Agent 是否识别缺失要求、路由到 memory/world/user 中正确的权威来源，并在证据闭合后收敛到同一可验证执行结果。**

英文写作版本：

> Existing work studies safe commitment, memory sufficiency, clarification, abstention, and memory-operation policies in isolation. What remains under-evaluated is whether agents grounded in interaction-derived persistent memory can identify unresolved action requirements, route evidence acquisition to the authoritative source, switch control actions under matched source-relocation interventions, and converge to a verified executable outcome once the evidence is closed.

## 3. 正式定义

### 3.1 环境

时间步 \(t\) 的观测包含：

- 当前目标 \(g_t\)；
- 当前观测和工作 packet \(C_t\)；
- 跨 session 持久记忆库 \(M_t\)；
- 外部世界接口 \(W_t\)，如 calendar、booking、filesystem；
- 用户接口 \(U_t\)，由可控 user simulator 提供私有偏好或意图；
- 剩余预算 \(b_t\)，包括 token、检索、验证、询问和环境步数。

目标行动需要闭合 requirement graph：

\[
R(g_t)=\{r_1,r_2,\ldots,r_n\},
\]

其中每个 requirement 有值、时效、authority、provenance 和 authorization 条件。

### 3.2 行动准备度

\[
y_t^{ready}\in\{\text{READY},\text{NOT\_READY},\text{CONFLICTED}\}.
\]

- `READY`：至少一个合法 requirement closure 已被当前可见证据完整支持。
- `NOT_READY`：缺失要求仍可通过至少一个来源解决。
- `CONFLICTED`：当前证据之间存在尚未消解的冲突，不能直接承诺。

### 3.3 证据来源

对每个未闭合 requirement \(r_j\)：

\[
y_{t,j}^{source}\in\{\text{CURRENT\_PACKET},\text{PERSISTENT\_MEMORY},\text{WORLD},\text{USER},\text{UNAVAILABLE}\}.
\]

- `CURRENT_PACKET`：已经可见，只需正确读取/整合。
- `PERSISTENT_MEMORY`：历史交互中已存在，但尚未取回。
- `WORLD`：当前外部状态才是权威来源，必须验证。
- `USER`：只有用户能确定的意图、偏好或授权。
- `UNAVAILABLE`：当前允许接口均无法解决。

无须额外证据的任务通过 requirement graph 为空或已闭合表示，不把 `NONE_NEEDED` 混入缺失来源标签。

### 3.4 五动作空间

\[
a_t\in\{\text{SEARCH\_MEMORY},\text{VERIFY\_WORLD},\text{ASK\_USER},\text{EXECUTE},\text{ABSTAIN}\}.
\]

`ABSTAIN` 附带 reason code：`UNAVAILABLE / POLICY_BLOCK / DEFER / ESCALATE`。第一版不把这些拆成独立动作。

### 3.5 可观测性与合理动作集合

数据同时提供：

1. latent world state；
2. Agent-observable state；
3. admissible action set \(A_t^{adm}\)；
4. 在完整生成图和成本函数下计算的 oracle action \(a_t^*\)。

主指标首先判断预测是否落在 \(A_t^{adm}\)，再用 regret 区分多个合理动作；避免用 latent truth 对 Agent 提出不可观测要求。

## 4. Benchmark 的核心创新

### 4.1 Source × Integrity 因子化干预

对每个 base task 选择一个或多个 decisive requirements，在两个轴上派生 matched variants。

**来源轴：**

| 变体 | 决定性证据位置 | 预期第一动作 |
|---|---|---|
| Packet | 当前 packet 已完整可见 | EXECUTE |
| Memory | 仅持久 memory store 中存在 | SEARCH_MEMORY |
| World | 仅当前环境状态可确认 | VERIFY_WORLD |
| User | 仅用户知道意图/授权 | ASK_USER |
| Unavailable | 所有允许来源均无解 | ABSTAIN |
| No-need | 任务本身不需要历史证据 | EXECUTE，且不得多余获取 |

**完整性轴：**

| 状态 | 含义 | 主要诊断 |
|---|---|---|
| Fresh | 当前、完整、权威 | 正常路径 |
| Stale | 曾经真实但已失效 | 能否覆盖旧值 |
| Conflicting | 多条来源冲突 | authority/time/provenance 推理 |
| Poisoned | 记忆中含诱导性错误 | memory skepticism |
| Authorization drift | 内容仍真，但权限已变化 | 是否在执行前重新确认 |

不是所有笛卡尔积都合理；generator 根据 domain schema 只生成语义成立的组合。

### 4.2 双重反事实不变量

每个 family 同时检验两个性质：

1. **Action flip**：证据来源变化时，第一控制动作按预期切换。
2. **Closure convergence**：所有可解决变体完成 acquisition 后，最终 action 和环境终态应一致。

这使 benchmark 不只是“看模型选了哪个标签”，而是验证它是否通过正确来源恢复了同一可执行事实基础。

### 4.3 Joint Gold 与 Oracle Decomposition

每个 decision point 输出：

- readiness；
- missing requirements；
- requirement-source map；
- evidence closure；
- admissible actions；
- oracle action 与 action cost；
- tool precondition；
- exact postcondition；
- failure attribution hooks。

替换 packet、retriever、monitor、router 或 executor 为 oracle，分别估计系统瓶颈。

## 5. 数据构造流程

### 5.1 Symbolic world first

1. 定义 domain schema、entities、state transitions 和 tool contracts。
2. 采样 base goal 与 requirement graph。
3. 生成跨 session interaction history，并由其形成 persistent memory store。
4. 指定 decisive requirement 的 source 和 integrity。
5. 渲染自然语言历史、当前请求、memory items 和 tool outputs。
6. 运行 deterministic validator，检查 gold action、closure 和 postcondition。
7. 生成 paraphrase、distractor 和 counterfactual family。

### 5.2 首批任务域

**Calendar / Scheduling**

- 历史偏好在 memory；
- 当前空闲时间在 world；
- 一次性优先级或最终授权在 user；
- 日历写入提供 exact executable outcome。

**Travel / Booking**

- 常旅客偏好与历史证件信息在 memory；
- 当前价格、库存和签证状态在 world；
- 预算变更与购买授权在 user；
- 预订或保留操作提供副作用验证。

MVP 之后可扩展 coding/file operations 和 communication/email，但不在 pilot 同时铺开。

### 5.3 自然性与防捷径

- 同一 family 保持目标、实体和大部分表面文本一致。
- 不在 prompt 中直接出现 `memory/world/user` 标签词。
- 对来源线索做 paraphrase 与位置随机化。
- 设置 lexical shortcut baseline。
- 人工抽检 decisive factor 是否唯一变化。
- 发布 generator seed、完整 state graph 和 validator。

## 6. 三个评测 Track

### Track A：Readiness Diagnosis

固定 packet，评估 readiness、missing requirement、source location 和 calibration。用于判断 reader/monitor 是否理解当前证据状态。

### Track B：Sequential Evidence Acquisition

Agent 可调用 memory search、world verify 和 user ask，评估 action routing、预算、停止和 closure。工具返回真实改变后续 observation。

### Track C：Executable Commitment

在 action gate 之后执行具有副作用的任务，检查 exact environment state、premature commit、unsupported success 和 abstention。

Track A 是低成本诊断，B/C 才是论文主结果；否则会退化成分类数据集。

## 7. 指标

### 7.1 Monitor

- Readiness Macro-F1；
- Missing Requirement F1；
- Source Location Macro-F1；
- Evidence Closure F1；
- Brier / ECE / risk-coverage。

### 7.2 Routing

- Source-Routing Accuracy；
- Admissible Action Accuracy；
- Wrong-Source Acquisition Rate；
- Evidence-Location Regret；
- Search/Verify/Ask-to-Closure steps。

### 7.3 Counterfactual

- Cross-Source Action-Flip Consistency；
- Closure-Convergence；
- Irrelevant-Distractor Invariance；
- Surface-Paraphrase Robustness；
- Integrity Sensitivity。

### 7.4 Outcome 与风险

- Exact Tool State / Task Success；
- Premature Commit Rate；
- Unsupported Success；
- Unnecessary Acquisition；
- Abstention Precision/Recall；
- Success-Cost Pareto。

不使用单一 composite score 排名；至少分别报告 Monitor、Routing、Counterfactual、Outcome/Cost 四组指标。

## 8. Baseline 设计

### 8.1 Sanity Baselines

- AlwaysExecute、AlwaysSearch、AlwaysVerify、AlwaysAsk、AlwaysAbstain；
- NoMemory、FullHistory、RandomRoute；
- lexical source classifier；
- confidence threshold。

### 8.2 Retrieval 与 Memory Systems

- BM25、dense、hybrid、retrieve-once@k；
- long-context history；
- Mem0/LangMem 类 store；
- A-MEM、StateMem wrapper；
- MemCon/Oblivion 风格 controller。

### 8.3 直接竞争 baseline

- SafeCommit 风格 `commit/probe/fallback` wrapper；
- MCB 风格 source-of-truth prompt；
- AgentAbstain 风格 pre-execution abstention prompt；
- SURE-RAG 风格 setwise sufficiency verifier；
- Router-Mem 风格 early-stop router。

### 8.4 Oracle Ladder

- OraclePacket；
- OracleRetriever；
- OracleReadiness；
- OracleSourceRouter；
- OracleExecutor；
- OracleAll。

所有方法固定 backbone、tool schema、可见来源、最大 token、acquisition calls 和 wall-clock budget。

## 9. 核心实验与假设

### E0：Benchmark Validity

验证 annotation agreement、generator validity、oracle solvability、shortcut resistance 和 difficulty gradient。

### E1：Main Results

比较不同模型、long-context/RAG/memory system/controller 的四组指标。

### E2：Source Relocation

同一 family 上报告 action-flip、wrong-source 和 closure-convergence。

### E3：Integrity Stress

分析 stale、conflict、poison 和 authorization drift 是否改变来源选择和 commit risk。

### E4：Oracle Decomposition

定量回答错误来自 packet、retrieval、readiness、source routing 还是 execution。

### E5：Budget and Calibration

改变 memory size、top-k、验证成本、询问成本和 action risk，画 success-cost/risk-coverage 曲线。

### 可证伪假设

- H1：最终 task success 会系统性高估 readiness 和 routing 能力。
- H2：强模型在 Memory/World/User 来源迁移下仍会选择惯性动作，action-flip 明显低于 oracle。
- H3：FullHistory 减少 SEARCH 错误，但不能解决 WORLD/USER routing，并会增加 stale/poison 风险。
- H4：memory controller 的总体 success 提升不保证 Wrong-Source Acquisition 和 Premature Commit 降低。
- H5：source-aware prompt/SFT 的收益主要出现在跨来源 family，而不是普通 retrieval slice。

如果 H1-H4 大多不成立，说明该问题对现有强模型过于简单或数据设计没有制造真实控制边界，应停止扩展。

## 10. 最小闭环

### 10.1 两周 Pilot

| 周 | 工作 | 产物 |
|---|---|---|
| W1 | schema、20 base tasks、source variants、validator | 120+ episodes；人工审查表 |
| W2 | 三类 API、sanity baselines、2-3 个模型 | pilot 主表、family heatmap、Go/No-Go memo |

模型优先：一个小模型 smoke、一个 7B/8B 开源模型、一个强 API 模型。Pilot 不训练。

### 10.2 Go 条件

- OracleAll 可解率 >= 98%；
- 强 baseline 的 cross-source family accuracy 明显低于 oracle；
- 至少出现两类不同的系统瓶颈；
- FullHistory、AlwaysVerify 等单策略不能支配所有 slice；
- 80% 以上指标由 deterministic evaluator 计算。

### 10.3 规模化目标

- 300-500 个 base tasks；
- 2,000-4,000 个主 episodes；
- 3-4 个领域；
- public dev + hidden generated test；
- 可重新采样 fresh instances，降低 contamination。

## 11. 第二阶段方法

只有 benchmark 证明来源路由是独立瓶颈后，才进入方法阶段。

### 11.1 Reference Controller

- requirement extractor；
- evidence/provenance reader；
- readiness monitor；
- source router；
- execution gate。

它是用于解释 benchmark 的 reference method，不在第一版声称架构新颖。

### 11.2 训练顺序

1. Prompt/rule controller，建立可达上界和错误类型。
2. SFT 学习 readiness、requirement-source map 和 tool calls。
3. Pairwise 学习正确来源动作相对 hard negative 的偏好。
4. Listwise 学习 admissible action set 内的 cost-aware ranking。
5. 仅在顺序探索与延迟反馈必要时使用 RL。

### 11.3 Reward

\[
R = R_{closure}+R_{route}+R_{outcome}
-\lambda_c C_{acquisition}
-\lambda_p P_{premature}
-\lambda_u P_{unsupported}.
\]

结果奖励由 exact environment state 或 task-specific verifier 给出；过程奖励来自 source map、admissible action 和 closure。MVP 不训练独立 GRM。

## 12. 贡献边界与写作纪律

### 12.1 可以主张

1. source-aware action readiness 的统一评测定义；
2. source × integrity 的 matched counterfactual families；
3. action flip 与 closure convergence 的联合协议；
4. 对真实 memory stack 的 decision-point gold 和 oracle decomposition；
5. 可执行、可重采样的 benchmark 与错误谱系。

### 12.2 不能主张

- 首次研究 memory sufficiency；
- 首次研究 safe commitment；
- 首次让 Agent ask/verify/abstain；
- 首次做 paired executable tasks；
- 首次把 memory operation 建模为 action；
- 首次研究 stale/conflict/poison；
- 首次提出 setwise evidence verification。

### 12.3 标题与摘要用语

避免：`the first benchmark for knowing when memory is sufficient`。

推荐：

> We introduce MemReadyBench, a diagnostic benchmark for source-aware action readiness in persistent-memory agents. Rather than asking only whether retrieved memory is relevant or whether an action should be committed, MemReadyBench intervenes on where decisive evidence can be obtained and tests whether agents route acquisition correctly before converging to a verified executable outcome.

## 13. 当前决策

> **优先实现 benchmark pilot，不训练；以 source relocation 是否产生稳定而非平凡的 action flip、以及 acquisition 后是否 closure-converge 作为第一道生死线。Pilot 通过后扩展 benchmark，benchmark 结果明确暴露 routing bottleneck 后再做轻量 SFT/排序学习方法。**

完整同期工作证据与审稿式比较见：[MemReadyBench 同期 arXiv 撞题审计](../reports/2026-09-03-memreadybench-concurrent-arxiv-audit.md)。
