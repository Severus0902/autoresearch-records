# Agent Memory 内部冲突消解与冲突闭包保持型压缩调研

> 调研日期：2026-09-11
>
> 本次更新：将研究对象从“外部记忆与参数知识冲突”收紧为“持久记忆池内部冲突”，并补充截至 2026-09-11 的 2025--2026 年论文与 arXiv 同期工作。
>
> 接收状态说明：ACL、NAACL、EACL、ICLR 等出处按官方论文页标注；其余统一标为 arXiv 预印本，后续状态可能变化。

## 1. 更新后的审稿式结论

### 1.1 研究对象必须收紧

本报告讨论的主要冲突发生在同一个 Agent 的持久记忆池内部，而不是：

- 模型参数知识与外部事实谁更可信；
- RAG 文档之间的一般事实核验；
- 当前上下文中的一次性矛盾；
- 多 Agent 通信本身的共识协议。

目标对象是跨会话积累的 episodic、semantic、procedural、preference 和 state memory。它们可能因时间变化、条件差异、抽象压缩、来源差异或派生依赖而形成冲突，并在后续检索、回答和工具行动中持续生效。

### 1.2 宽泛问题已经拥挤

重新检索后，以下宽泛表述均不能再作为主要创新：

1. **“首次检测 Agent Memory 冲突”不成立。** ACL 2026 的 Conflict-Aware Memory、HiMem、MOSAIC 等已经直接检测并处理记忆项之间的冲突。
2. **“首次保留冲突而不是覆盖”不成立。** TANGLE 明确研究不可消解冲突；StateFuse 将冲突保存为显式对象并延迟到投影阶段处理。
3. **“首次研究记忆更新中的新旧冲突”不成立。** MemoryAgentBench、STALE、StateMemBench 和 THEANINE 已覆盖最新事实、隐式失效、状态替代和时间线管理。
4. **“首次做面向行为的记忆压缩”不成立。** DeMem 已将 Agent Memory 写成 decision-centric rate-distortion 问题。
5. **“首次要求压缩保留语义约束”不成立。** Context Codec 已提出带来源的 typed semantic atoms、conflict/evidence 关系及压缩后验证指标。
6. **“首次做冲突感知 consolidation”不成立。** HiMem 已在 episodic-note 双层记忆中执行 conflict-aware reconsolidation；MOSAIC 在写入时进行主动冲突检测。
7. **“首次定位并抑制有害记忆组合”不成立。** 2026 年 9 月 8 日提交的 MeClear 已用 cooperative Shapley attribution 识别相互作用的负效用记忆，并在当前查询中执行最小抑制。

### 1.3 仍可做的窄问题

当前更可信的切口是：

> **面向有损 Agent Memory 巩固的冲突闭包保持**
>
> Conflict-Closure Preservation under Lossy Agent Memory Consolidation

一句话定义：

> 当持久记忆池中存在新旧版本、条件分支、例外、不同抽象粒度或不同记忆类型之间的冲突时，如何在有损巩固后仍保持原记忆池对未来查询与行动所蕴含的可判定结论、不可判定边界及证据依赖，并在闭包被破坏时定位和修复具体丢失的关系？

这不是把已有任务简单合并。关键增量是把评价单位从“单条事实是否保留”升级为“由多条记忆及其关系共同决定的语义闭包是否保留”，并要求压缩错误能够被归因到具体节点或边。

### 1.4 推荐优先级

1. **第一阶段：Benchmark-first。** 先证明普通摘要、最新优先和已有 memory system 在固定压缩预算下会系统性破坏冲突闭包。
2. **第二阶段：Method-first。** 再实现带类型关系、验证探针和局部修复的 ClosureMem。
3. **第三阶段：可选参数固化。** 仅将闭包稳定的子图写入 LoRA/adapter；动态、未决和强 provenance 依赖内容继续留在外部记忆。

第一篇工作不应从“把海量记忆训练进 0.5B 模型”起步。先把外部持久记忆的压缩正确性定义清楚，更容易在 4×RTX 4090 上形成可证伪的结果。

---

## 2. 问题边界与基本定义

### 2.1 什么是“记忆自身的冲突”

设 Agent 在时间 (t) 的持久记忆为：

\[
M_t=\{m_1,m_2,\ldots,m_n\}.
\]

每条记忆表示为：

\[
m_i=(c_i,\tau_i,s_i,a_i,\kappa_i,p_i,y_i).
\]

- (c_i)：内容或命题；
- (	au_i)：事件时间、写入时间和有效区间；
- (s_i)：记忆来源；
- (a_i)：来源权威、授权范围或置信度；
- (kappa_i)：适用条件、场景或用户范围；
- (p_i)：可回到原始会话、观察或工具反馈的 provenance；
- (y_i)：记忆类型，如 episodic、semantic、procedural、preference、state。

当两条或多条记忆不能在同一时间、条件、权限或推理依赖下同时成立，或者压缩过程错误改变了它们之间的关系，就发生内部冲突。

### 2.2 必须覆盖的冲突类型

| 类型 | 例子 | 正确处理 | 常见压缩错误 |
|---|---|---|---|
| 时间替代 | 去年住上海，今年搬到北京 | 保留有效区间并标记 `SUPERSEDES` | 旧值复活或两值被平均 |
| 条件分区 | 工作日咖啡，周末喝茶 | 保留条件分支 | 压成无条件“喜欢咖啡” |
| 规则与例外 | 默认走高速，但暴雨时走国道 | 保留 `EXCEPTION_TO` | 低频例外被摘要删除 |
| 同权威未决 | 用户先后表达两个偏好但无时间线索 | 保留两个分支并澄清 | 强行挑一个 winner |
| 来源/授权冲突 | 用户本人偏好与第三方推测不一致 | 来源作为记忆元数据参与使用 | consolidation 后权威坍缩 |
| 抽象粒度冲突 | 原始 episode 有条件，note 写成一般规则 | episodic 与 semantic 层保持可追溯一致 | 抽象层覆盖原始证据 |
| 跨类型冲突 | semantic 偏好与 procedural policy 不一致 | 显式建模跨类型依赖 | 各 memory store 各自正确、联合行动错误 |
| 组合冲突 | 单条均不矛盾，多条组合推出相反结论 | 检查派生闭包 | 仅做 pairwise detection 无法发现 |
| 压缩诱发冲突 | 原始记录相容，摘要后变成互斥结论 | 拒绝该压缩或局部修复 | 表面流畅但未来行为错误 |

### 2.3 冲突消解不等于选一个答案

合理动作空间至少包括：

`KEEP / MERGE / SUPERSEDE / CONDITION / RETAIN-BOTH / VERIFY / CLARIFY / ABSTAIN / REPAIR`。

其中：

- 可判定冲突应依据时间、条件、来源和依赖关系更新当前状态；
- 不可判定冲突应保留分歧，不得伪造单一结论；
- 压缩引入的冲突应回到原始证据进行局部重构；
- 删除原始 evidence 不应是默认操作。

### 2.4 本阶段明确不做什么

- 不以“参数知识与外部证据冲突”为主任务；
- 不把网页真伪核验当作核心贡献；
- 不直接训练全参数模型承载所有个人历史；
- 不把普通 QA accuracy 当作唯一指标；
- 不把多种已有 benchmark 拼接后称为新 benchmark；
- 不在第一轮引入复杂 RL，以免数据、协议和算法收益无法归因。

---

## 3. 2025--2026 相关工作重新梳理

### 3.1 状态更新与可消解冲突

| 工作 | 出处/状态 | 解决的问题 | 对本方向的约束 |
|---|---|---|---|
| [MemoryAgentBench](https://arxiv.org/abs/2507.05257) | ICLR 2026 | 在增量交互中评测检索、测试时学习、长程理解和选择性遗忘；FactConsolidation 使用带序号的新旧事实 | 显式 latest-wins 已是基线，不足以构成创新 |
| [THEANINE](https://aclanthology.org/2025.naacl-long.435/) | NAACL 2025 Long | 用时间线组织旧事实、新事实及因果上下文 | 旧记忆并非都应删除，历史状态可能服务后续推理 |
| [STALE](https://arxiv.org/abs/2605.06527) | arXiv 2026 | 后续观察隐式使旧记忆失效，评测状态解析、陈旧前提抵抗和策略适应 | 单独做 stale detection 或 premise resistance 不新 |
| [StateMemBench](https://arxiv.org/abs/2608.19652) | arXiv 2026 | 234 个多会话场景，区分 current 与 superseded state，并建模关系依赖 | 当前状态准确率和 supersession 已被直接覆盖 |
| [Reliable Post-Retrieval Assembly](https://arxiv.org/abs/2606.01435) | arXiv 2026；COLM 2026 workshop poster | 候选抽取后用确定性最大序号规则处理 FactConsolidation | 明示时间序号场景可用简单程序解决，不必堆 LLM |

### 3.2 不可消解冲突、权威与冲突可见性

| 工作 | 出处/状态 | 解决的问题 | 剩余边界 |
|---|---|---|---|
| [TANGLE](https://arxiv.org/abs/2608.13921) | arXiv 2026 | 541 个不可消解个人记忆冲突，覆盖条件分区、行为振荡和来源矛盾；评价感知、推理、校准、澄清和忠实性 | 重点是给定/抽取记忆后的行动策略，不系统研究不同压缩预算下关系闭包损失 |
| [AuthMem-Bench](https://arxiv.org/abs/2608.01679) | arXiv 2026 | 固定 claim 与任务，仅改变来源权威，测 consolidation 是否把观察升级为授权事实 | 深入覆盖 authority 单轴，但未覆盖多关系联合闭包 |
| [StateFuse](https://arxiv.org/abs/2607.05844) | arXiv 2026 | 用不可变 OpSet/CRDT、显式冲突对象和 correction handle 保留多 Agent 冲突 | 重点是 memory contract 与确定性合并，不是有损语义压缩 |
| [LatticeMind](https://arxiv.org/abs/2608.08236) | arXiv 2026 | 在共享记忆中保存状态、证据、替代关系并执行符号检查与 LLM reconciliation | 重点是多 Agent 写入与冲突治理，未系统测压缩关系损失 |
| [MemTxn](https://arxiv.org/abs/2607.27834) | arXiv 2026 | 以事务边界支持有来源更新、冲突可见版本和完整状态恢复 | 解决更新与恢复协议，不等同于语义压缩验证 |

### 3.3 冲突感知记忆方法

| 工作 | 出处/状态 | 核心方法 | 本方案不能重复的表述 |
|---|---|---|---|
| [Conflict-Aware Memory for Embodied Agents](https://aclanthology.org/2026.acl-long.1306/) | ACL 2026 Main | Conflict Detection Rules 识别向量记忆中语义相似但冲突的文本或图像并修正索引 | 不能说首次在 memory store 内做冲突检测 |
| [HiMem](https://arxiv.org/abs/2601.06377) | arXiv 2026 | immutable episode memory + 抽象 note memory；检索反馈触发 conflict-aware reconsolidation | 不能说首次连接 episodic 与 semantic memory 并做冲突重整 |
| [MOSAIC](https://arxiv.org/abs/2607.16211) | arXiv 2026 | typed graph 保存关系，在写入时检查近邻并更新、拒绝或交由人工处理 | 不能说首次做图结构 memory conflict detection |
| [Hindsight](https://aclanthology.org/2026.acl-demo.27/) | ACL 2026 Demo | world、experience、observation、opinion 四类网络，结合时间过滤与图检索 | 不能说首次区分事实、观察与主观信念 |
| [Amory](https://aclanthology.org/2026.eacl-long.183/) | EACL 2026 Long | 将对话片段巩固为 episodic narratives，并抽象 peripheral semantic memory | 不能说首次做多粒度 narrative consolidation |

HiMem 是最接近“内部冲突 + consolidation”的工作。它的可进入边界不是再加一个 conflict classifier，而是：其关系主要被归纳为 independent、extendable、contradictory，更新以查询触发为主；尚未系统回答压缩后版本、条件、例外、未决关系和跨层派生闭包是否同时保持，也没有提供边级错误归因与压缩预算曲线。

### 3.4 有损巩固与压缩的直接同期工作

| 工作 | 出处/状态 | 核心思想 | 与本方向的直接碰撞 |
|---|---|---|---|
| [Useful Memories Become Faulty When Continuously Updated by LLMs](https://arxiv.org/abs/2605.12978) | arXiv 2026 | 连续 LLM consolidation 会使原本有用的记忆变成有害记忆；保留 raw episode 的策略更稳 | 为“压缩会造错”提供强动机，但未定义冲突闭包及局部修复 |
| [DeMem](https://arxiv.org/abs/2605.10870) | arXiv 2026 | 用 decision-centric rate-distortion 保留对决策有区别的历史状态 | 已占据“面向决策的 memory compression”；本方案必须比 decision utility 更具体 |
| [Context Codec](https://arxiv.org/abs/2605.17304) | arXiv 2026 | typed、source-grounded semantic atoms，带 equivalence、conflict 和 evidence；用 atom recall 与 recoverability 验证压缩 | 已占据“保留语义承诺的可验证压缩”；本方案必须评价跨时间持久 memory 的关系闭包 |
| [Dual-Layer Agentic Memory](https://arxiv.org/abs/2608.22215) | arXiv 2026 | 小模型写入路由、外部缓冲和周期性 SFT 参数固化 | 参数写回可作第二阶段，但不是第一阶段的新意 |
| [Deployment-Time Memorization](https://arxiv.org/abs/2606.10062) | arXiv 2026 | 比较摘要强度、检索宽度和删除模式对个性化、提取风险与删除残留的影响 | 说明压缩还会复制和残留敏感信息，provenance 与派生层清理不能忽略 |
| [MeClear](https://arxiv.org/abs/2609.09115) | arXiv 2026-09-08 | Leave-One-Out 筛选结合 sampled cooperative Shapley attribution，定位相互作用的负效用记忆；查询级抑制但不永久修改 memory bank | 已覆盖组合式 harmful-memory attribution；剩余空间是压缩关系错误、持久修复和纵向闭包验证 |
| [The Memory Trust Gap](https://arxiv.org/abs/2609.01852) | arXiv 2026；NeurIPS 2026 workshop under review | 在 Qwen3 0.6B--8B 上测 stale memory 对权威工具证据的覆盖与能力尺度效应 | 属于记忆-外部证据冲突，作为小模型风险旁证，不作为本 Benchmark 的主任务 |

### 3.5 文献给出的共同结论

1. 记忆冲突不是简单文本矛盾，而是时间、条件、来源、权限、抽象层与派生关系共同作用的结果。
2. “最新优先”只适用于显式全序且确实为覆盖更新的子集。
3. 不可消解冲突必须保持未决，不能被摘要器伪装成确定事实。
4. 流畅摘要不能保证未来行为正确；continuous consolidation 本身可能是错误源。
5. 原始 episode 应作为可审计证据保留，紧凑状态只是可撤销的派生视图。
6. 现有工作多测节点事实、最终答案或单一冲突轴，关系结构在有损巩固前后的完整保持仍缺少统一受控协议。
7. 查询级 suppress harmful memories 已有 MeClear；新方法必须证明为什么需要修改持久记忆结构，以及这种修复能否跨后续查询复用。

---

## 4. 精确的 Research Gap

### 4.1 不能再使用的旧 gap

以下说法过宽，应从论文和 PPT 中删除或降级：

- 现有工作没有研究记忆冲突；
- 现有工作都会直接覆盖旧记忆；
- 现有压缩只关注 token，不关注行为；
- 现有工作没有保留 provenance；
- 尚无 conflict-aware consolidation；
- 尚无安全、可验证的语义压缩。

### 4.2 可保留的新 gap

> 现有工作分别研究新旧状态、来源权威、不可消解冲突、显式冲突对象、决策保持压缩和语义承诺压缩，但尚缺少一个面向持续 Agent Memory 的统一受控协议，用来衡量：当多个记忆节点通过版本、条件、例外、支持、矛盾和派生关系共同决定未来行为时，有损巩固是否保持了这些关系所形成的语义闭包；若闭包被破坏，系统能否把错误定位到具体关系并以局部重整恢复，而不是重新摘要全部历史。

这个 gap 有四个必要限定：

1. **持续记忆，而非一次性 context compression。** 记忆会在多个 session 中形成、更新、检索和再次巩固。
2. **关系闭包，而非只保留重要 atom。** 一个 atom 仍在，不代表它的条件、例外、当前/历史状态和派生结论仍正确。
3. **matched intervention。** 固定原始事件、任务和查询，只改变冲突关系或压缩预算，才能归因于 memory state。
4. **可定位修复。** 评价不仅给出答案错了，还指出是哪条 `SUPERSEDES`、`CONDITIONAL_ON`、`EXCEPTION_TO` 或 `DERIVED_FROM` 边丢失。

### 4.3 这不是简单“合并别人拆开的任务”

若只是把 StateMemBench、TANGLE、AuthMem-Bench 放进一个数据集，创新较弱。真正新的实验变量应是：

> **同一个原始记忆族在不同有损巩固算子和压缩预算下，节点可被保留但关系可能被删除、错误合并或错误裁决；Benchmark 直接测这种关系变化是否改变后续行为。**

因此核心自变量是 consolidation intervention，核心中介变量是 relation-closure preservation，核心因变量是未来回答、澄清和工具行动的 behavioral equivalence。

---

## 5. 核心问题的形式化定义

### 5.1 原始记忆图

把持久记忆表示为带类型属性图：

\[
G(M)=(V,E),
\]

其中 (V) 是原子记忆，边类型集合为：

\[
\mathcal R=\{\texttt{DUPLICATE},\texttt{SUPPORTS},\texttt{SUPERSEDES},
\texttt{CONTRADICTS},\texttt{CONDITIONAL\_ON},\texttt{EXCEPTION\_TO},
\texttt{DERIVED\_FROM},\texttt{UNRESOLVED}\}.
\]

给定预算 (B)，巩固器产生紧凑记忆：

\[
C_B(M)=\widetilde M,\qquad |\widetilde M|\le B.
\]

### 5.2 冲突闭包

对查询族 (mathcal Q)，原始图通过时间、条件、来源和派生规则得到：

\[
\Gamma_M(q)=\big(A_q,U_q,P_q\big),
\]

其中：

- (A_q)：当前可支持的答案或行动集合；
- (U_q)：必须保持未决、澄清或拒绝的边界；
- (P_q)：支持结论的最小证据路径与 provenance。

若压缩后对所有关键查询 (q\in\mathcal Q) 都满足：

\[
\Gamma_{\widetilde M}(q)\equiv\Gamma_M(q),
\]

则称 (C_B) 在该查询族上保持冲突闭包。这里的等价不是文本相同，而是：

- 当前与 superseded 状态相同；
- 条件和例外的适用范围相同；
- 可回答与不可判定边界相同；
- downstream action 相同；
- 结论仍可追溯到充分证据。

### 5.3 需要识别的压缩失真

| 失真 | 定义 | 后果 |
|---|---|---|
| False Collapse | 不同条件或时间状态被合并成单一事实 | 错误泛化 |
| False Resolution | 未决冲突被压成单一 winner | 过度自信行动 |
| Stale Resurrection | 已被替代的状态重新成为 active | 使用旧地址、旧计划或旧规则 |
| Exception Loss | 低频但关键例外消失 | 高风险条件下执行默认动作 |
| Provenance Severance | 结论仍在但无法回溯充分证据 | 无法核验、撤回与审计 |
| Cross-Level Inconsistency | episode 与 note/semantic memory 不一致 | 检索不同层得到相反结论 |
| Derived Inconsistency | 上游事实更新后派生结论未重算 | 计划与当前 memory state 脱节 |
| Conflict Hallucination | 原始记忆相容，压缩后产生伪冲突 | 不必要澄清或拒绝执行 |

---

## 6. Research Questions 与可证伪假设

### RQ1：冲突闭包能否被稳定测量？

> 在相同原始记忆、查询和压缩预算下，不同 memory consolidator 对版本、条件、例外、未决和派生关系的保持能力有何差异？

**H1：** 普通 LLM 摘要在 node-level factual recall 尚可时，edge-level macro-F1、Exception Preservation 和 Unresolved Preservation 会显著下降。

### RQ2：闭包保持是否比普通压缩指标更能解释 Agent 行为？

> 在控制 token 数、模型和检索 top-k 后，关系闭包指标是否比 ROUGE、atom recall 或单轮 QA accuracy 更能预测后续回答、澄清和工具行动错误？

**H2：** 关系闭包误差对 behavioral error 的解释力显著高于文本相似度和节点召回率。

### RQ3：能否对压缩错误做边级定位与局部修复？

> 当验证探针失败时，只重构相关节点与边，能否以低于全量重新巩固的成本恢复未来任务表现？

**H3：** verifier-guided local repair 在质量相当时，比 full reconsolidation 减少至少 30% 的 token/LLM 调用成本。

### 可选 RQ4：哪些闭包稳定内容适合参数固化？

> 仅将跨多个巩固周期保持稳定且通过 closure probes 的子图写入 adapter，能否减少参数遗忘和错误内部化？

RQ4 是第二篇或扩展实验，不应绑架第一阶段 Benchmark。

---

## 7. Benchmark 方案：ConflictClosureBench

### 7.1 Benchmark 单位

一个样本不是单个 question，而是一个 matched memory family：

\[
x=(H,M,G(M),\{C_B(M)\},\mathcal Q,\mathcal A^*,\mathcal P^*).
\]

- (H)：跨 session 原始交互与事件流；
- (M)：由 (H) 形成的原子持久记忆；
- (G(M))：gold typed relation graph；
- (C_B(M))：不同系统、不同预算产生的紧凑记忆；
- (mathcal Q)：诊断、使用、澄清、行动和更新 probes；
- (mathcal A^*)：gold answers/actions；
- (mathcal P^*)：gold evidence paths。

### 7.2 受控样本族

建议第一版构造 200 个 base families，每个 family 生成 8 个变体，共约 1,600 个评测单元：

1. `CONSISTENT_DUPLICATE`：同义重复，不应误报冲突；
2. `EXPLICIT_SUPERSESSION`：显式“旧值作废”；
3. `IMPLICIT_SUPERSESSION`：通过后续事件推断旧值失效；
4. `CONTEXT_PARTITION`：不同条件下分别成立；
5. `RULE_EXCEPTION`：默认规则与关键例外；
6. `EQUAL_AUTHORITY_UNRESOLVED`：证据不足，必须保持未决；
7. `EPISODE_NOTE_MISMATCH`：原始 episode 与抽象 note 不一致；
8. `COMPOSITIONAL_DERIVATION`：上游变化影响多跳派生结论；
9. `POST_COMPRESSION_UPDATE`：压缩后继续注入更新；
10. `CLEAN_DISTRACTOR`：加入相似但无关记录，检查伪冲突。

每个 family 保持实体、目标任务、可用工具和 world state 不变，只改变 memory relation 或 consolidation output。这是因果归因成立的关键。

### 7.3 压缩干预

对同一原始 memory family 施加：

- 无压缩 full store；
- 固定 token cap；
- 2×、4×、8× compression ratio；
- periodic、online、query-conditioned 三种 consolidation schedule；
- prose、JSON atom、typed graph 三种表示。

压缩器不能看到测试 probes，避免为答案定制摘要。

### 7.4 五类任务

| 任务 | 输入 | 输出 | 对应 RQ |
|---|---|---|---|
| T1 关系诊断 | 原始或紧凑 memory | 节点状态、typed edges、缺失信息 | RQ1 |
| T2 紧凑状态生成 | 原始 memory + budget | compact memory + 保留证据 ID | RQ1 |
| T3 闭包探针 | compact memory + query | 回答/澄清/拒绝 + evidence path | RQ1、RQ2 |
| T4 纵向更新 | compact memory + 新 session | 更新后的状态与受影响派生项 | RQ2 |
| T5 局部修复 | failure trace + 原始证据片段 | patch、修复边和验证结果 | RQ3 |

### 7.5 指标

| 指标 | 含义 |
|---|---|
| Node Recall | 关键原子记忆是否保留 |
| Edge Macro-F1 | 各类支持、替代、条件、例外、冲突和派生边的宏平均 F1 |
| Conflict Closure Accuracy (CCA) | 一个 family 的关键 closure probes 是否全部保持等价 |
| False Resolution Rate (FRR) | 未决冲突被错误裁决为单一结论的比例 |
| Stale Resurrection Rate (SRR) | superseded 记忆重新支配回答或行动的比例 |
| Exception Preservation Rate (EPR) | 例外条件及其行为是否仍被保留 |
| Provenance Reachability (PR) | 结论能否到达充分原始证据路径 |
| Behavioral Equivalence Score (BES) | 压缩记忆与 full store 在回答、澄清和工具行动上的一致性 |
| Longitudinal Repair Utility (LRU) | 修复后相关后续任务恢复量减去无关任务污染 |
| Repair Localization Accuracy | 是否定位到真正损坏的节点/边 |
| Compression/Cost | token、存储、延迟、LLM 调用和训练成本 |

建议主指标为 `CCA + BES + FRR`，并报告压缩率-质量 Pareto 曲线。不要把所有维度压成一个 aggregate score。

### 7.6 数据划分与泄漏控制

- 按 base family 划分 train/dev/test，不能让同一实体故事的改写跨集合；
- 单独设置 held-out relation composition；
- 单独设置 held-out memory type pair，如 episodic-procedural；
- 测试集中包含模板外自然语言改写；
- gold graph 先由规则生成，再对自然化后的样本进行人工复核；
- 对所有自动 judge 抽样做双人标注与一致性报告；
- action task 尽量用确定性 tool-state evaluator，而不是只靠 LLM judge。

---

## 8. 方法方案：ClosureMem

### 8.1 设计原则

ClosureMem 不是新的通用向量数据库，而是位于 memory formation 与 retrieval 之间的“可验证巩固层”：

1. 原始 episodic ledger 默认不可变；
2. 把可复用信息抽成 typed atoms；
3. 显式维护关系图而非只保存摘要；
4. consolidation 前后生成同一组 closure probes；
5. 验证失败时只修复相关节点和边；
6. 无法判定时保留冲突并回退原始证据。

### 8.2 处理流程

1. **Atom extraction**：从新 session 提取事实、偏好、状态、规则、例外和工具结果。
2. **Candidate linking**：检索可能重复、替代、支持或冲突的旧 atoms。
3. **Relation typing**：预测 `DUPLICATE/SUPPORTS/SUPERSEDES/CONTRADICTS/CONDITIONAL_ON/EXCEPTION_TO/DERIVED_FROM/UNRESOLVED`。
4. **Constrained consolidation**：在预算下选择保留节点、生成抽象节点和关系边；未决边不得被静默删除。
5. **Probe compilation**：由关系图自动生成 current-state、condition、exception、unresolved、provenance 和 derived probes。
6. **Post-consolidation verification**：比较原始图与 compact graph 的 closure behavior。
7. **Edge-localized repair**：根据失败 probe 的依赖路径，仅回取相关 evidence spans 并修复 compact graph。
8. **Serving**：检索 compact graph；低置信或越界查询回退 raw ledger。

### 8.3 巩固目标

\[
\min_C\;D_{closure}(M,C(M))
+\lambda_b|C(M)|
+\lambda_r C_{repair}
+\lambda_p D_{provenance},
\]

其中：

- (D_{closure})：闭包探针上的语义与行为失真；
- (|C(M)|)：在线 memory 预算；
- (C_{repair})：发现错误后的局部修复成本；
- (D_{provenance})：证据路径丢失程度。

与 DeMem 的差异必须写清：DeMem 关心“哪些历史必须为决策保持可区分”；ClosureMem 进一步显式监督这些区别由哪些版本、条件、例外、未决和派生关系产生，并要求可定位修复。

与 Context Codec 的差异必须写清：Context Codec 面向上下文中的 typed commitments；ClosureMem 面向跨 session 持久记忆的形成、反复更新、有损巩固和后续修复，并以 relation closure 与 longitudinal behavior 为主指标。

### 8.4 训练安排

第一版应先实现无训练协议，再逐步训练：

#### Stage A：确定性与强模型基线

- 规则生成 gold graph 与 probes；
- 测 full store、latest-wins、LLM summary、typed JSON、StateFuse/Context-Codec-inspired 表示；
- 证明 closure gap 确实存在。

#### Stage B：关系识别 SFT/LoRA

- 输入候选 memory pair/subgraph；
- 输出 typed relation、适用范围、置信度和 evidence IDs；
- 对 compositional conflict 使用小子图输入，而非只做 pairwise 文本分类。

#### Stage C：hard-negative 排序

为同一原始 memory 构造仅错一条边的候选压缩：

- 丢失 `EXCEPTION_TO`；
- 把 `UNRESOLVED` 错改为 `SUPERSEDES`；
- 删除 provenance；
- 旧状态错误激活；
- 条件分支错误合并。

pairwise loss 适合“正确候选 vs 单边危险候选”，listwise loss 适合同时比较多个压缩候选。它们是方法增强，不应替代闭包指标本身。

#### Stage D：verifier-guided repair

- verifier 输出失败 probe、受影响边和最小 evidence slice；
- repair model 只生成 graph patch；
- patch 后重新运行相关 probe，不全量重新摘要。

RL 不是第一轮必需项。若后续加入，只应用于多步压缩-验证-回退策略，奖励可由 closure probes、行为执行和成本程序化计算。

---

## 9. Baselines 与消融

### 9.1 必须包含的 baseline

1. `No Memory`；
2. `Full Store`；
3. `FIFO / Recent-k`；
4. `Latest Wins`；
5. `LLM Summary`；
6. `LLM Summary + Raw Fallback`；
7. `Mem0 / A-Mem-style external memory`；
8. `HiMem-inspired episodic-note reconsolidation`；
9. `MOSAIC-inspired typed graph`；
10. `StateFuse-inspired conflict-preserving store`；
11. `MeClear-inspired query-scoped harmful-memory suppression`；
12. `DeMem-inspired decision-preserving compression`；
13. `Context Codec-inspired typed commitments`；
14. `Oracle Relation Graph`。

若官方代码或接口不完整，应标为 `protocol-inspired`，不要暗示完全复现。

### 9.2 关键消融

- 去掉时间与有效区间；
- 去掉 condition/scope；
- 去掉 `UNRESOLVED`，强制选 winner；
- 去掉 `EXCEPTION_TO`；
- 去掉跨层 `DERIVED_FROM`；
- 去掉 provenance；
- 不运行 post-consolidation probes；
- 全量重新巩固 vs edge-localized repair；
- pairwise vs listwise candidate ranking；
- prose vs JSON atoms vs typed graph；
- 2×、4×、8× 压缩预算；
- 外部 compact memory vs 可选 LoRA internalization。

---

## 10. 4×RTX 4090 最小验证闭环

### 10.1 Pilot 0：只做 60--100 个 family 的人工审计

先用模板构造 8 类内部冲突，每类约 10 个 family。比较：

- full store；
- naive summary；
- latest-wins；
- structured JSON；
- typed relation graph。

目标不是刷榜，而是确认以下现象真实存在：同样保留关键名词和事实 token，摘要仍会丢失条件、例外、未决或派生关系，并导致未来行为变化。

### 10.2 Pilot 1：Benchmark 最小版

- 200 base families × 8 variants，约 1,600 单元；
- 每个原始流包含 20--80 条记录；
- 2×、4×、8× 三档压缩；
- Qwen2.5-0.5B/1.5B/7B 或服务器已有同级模型；
- 规则 evaluator 为主，LLM judge 只处理解释质量；
- 至少 3 个随机种子。

需要回答：

1. node recall 高时，edge/closure 是否仍显著下降？
2. closure 指标是否比 ROUGE/普通 QA 更能预测行为错误？
3. 哪种 conflict family 最容易被 compression 破坏？

### 10.3 Pilot 2：小模型关系识别

- 0.5B/1.5B LoRA；
- 训练 typed edge extraction 与 evidence span selection；
- 与 7B zero-shot、规则和 embedding similarity 比较；
- hard negative 专门控制“文本相似但 relation 不同”。

若小模型对隐式替代和组合冲突明显不足，可设计 small-to-large escalation，而不是强迫 0.5B 处理全部样本。

### 10.4 Pilot 3：局部修复

- 对每个错误压缩保留 gold failure edge；
- 比较 no repair、full reconsolidation、random evidence repair 和 edge-localized repair；
- 报告恢复后的 CCA/BES、调用 token、延迟与无关关系变化率。

### 10.5 Go/No-Go 判据

满足大部分条件再扩展：

- 在 4× 或 8× 压缩下，naive summary 相对 full store 至少出现 10 个百分点的 closure loss；
- 控制 token 数后，Edge Macro-F1/CCA 对 behavioral error 的预测显著优于文本相似度和 node recall；
- ClosureMem 相对最强结构化 baseline 至少降低 8 个百分点的 FRR 或 SRR；
- clean family 性能下降不超过 3 个百分点；
- local repair 相对 full reconsolidation 至少节省 30% 成本，且质量基本相当；
- held-out relation composition 上仍有收益。

以下情况应停止或转向：

- relation closure 与 downstream behavior 几乎无相关性；
- Context Codec 或 StateFuse 的简单适配已完全解决问题；
- 方法收益只来自保存更多 token；
- gold graph 标注无法稳定复现；
- 所有复杂冲突都必须调用更大模型，局部修复无成本优势。

---

## 11. 第二阶段：海量记忆如何服务小模型

若第一阶段成立，再探索“把哪些记忆训练进小模型”，而不是全量写入参数。

### 11.1 三层载体

1. **Raw episodic ledger**：保留原始事件和 provenance，不默认删除；
2. **Compact closure graph**：在线检索，保存稳定 atoms 与必要关系；
3. **Parametric skill/adapter**：只承载跨周期稳定的语义规则、程序经验和 memory-control policy。

### 11.2 可固化性门控

只有同时满足以下条件的子图才能进入 adapter：

- 多个周期内状态稳定；
- 无 unresolved edge；
- 条件与例外已显式化；
- provenance probes 通过；
- 参数改写和 locality probes 通过；
- 外部 memory 可在 probe 失败时恢复。

### 11.3 与 Dual-Layer 的关系

Dual-Layer 已提出 fast write routing + slow parametric consolidation。本方向若进入参数阶段，增量应是：

- consolidation 单位从平坦样本变成 closure-stable subgraph；
- 写回前运行关系闭包验证；
- 写回后保留 edge-level certificate；
- 更新冲突时只失效受影响 adapter/knowledge slice；
- 同时测错误内部化、catastrophic forgetting 和删除残留。

这一阶段可采用 LoRA/adapter、replay 和 locality loss；第一轮仍不需要 RL。

---

## 12. 论文故事与贡献边界

### 12.1 推荐标题

**Benchmark-first：**

> ConflictClosureBench: Evaluating Relational Integrity under Lossy Agent Memory Consolidation

**Method-first：**

> ClosureMem: Verifiable Conflict-Closure Preservation for Longitudinal Agent Memory

### 12.2 推荐的三项贡献

1. 提出跨 session 持久记忆的 conflict-closure preservation 问题，把版本、条件、例外、未决、provenance 和派生关系纳入同一形式化框架。
2. 构建 matched-family、budget-controlled benchmark，分离节点保留、关系保留与 downstream behavioral equivalence。
3. 提出 probe-verified、edge-localized consolidation/repair 方法，在相同预算下减少错误裁决、旧状态复活和全量重整成本。

### 12.3 最容易被审稿人追问的地方

1. **与 Context Codec 有何本质区别？** 必须用 longitudinal lifecycle、relation closure、post-update 和 local repair 回答。
2. **与 DeMem 有何区别？** 必须证明显式关系闭包比 decision partition 提供额外诊断或修复价值。
3. **与 StateFuse 有何区别？** StateFuse 是 conflict-preserving contract；本方案研究有损压缩、预算曲线及压缩错误修复。
4. **与 HiMem 有何区别？** HiMem 已有 conflict-aware reconsolidation；本方案必须覆盖多关系闭包、受控压缩干预和边级归因。
5. **与 MeClear 有何区别？** MeClear 定位对当前查询有害的 memory entries 并临时抑制；本方案必须定位 consolidation 损坏的 typed edges、持久修复 compact memory，并验证未来查询复用。
6. **为什么不是把已有 benchmark 拼起来？** 数据必须通过 matched consolidation intervention 构造，而不是聚合任务。
7. **为什么必须有新方法？** 先让 Pilot 0/1 证明结构化 baseline 的剩余 failure gap，再决定是否训练。

### 12.4 可以安全声称与不能声称的内容

可以声称：

- 系统研究有损巩固前后多类型内部关系闭包；
- 在同一 memory family 和压缩预算下进行受控比较；
- 将行为失败归因到具体关系并执行局部修复。

暂时不能声称：

- 首次研究 Agent Memory conflict；
- 首次保留不可消解冲突；
- 首次做 conflict-aware consolidation；
- 首次做 decision-aware 或 verifiable compression；
- 首次将外部记忆写入小模型参数。

---

## 13. 建议阅读顺序

### P0：直接决定创新是否成立

1. [HiMem](https://arxiv.org/abs/2601.06377)：冲突感知双层 memory reconsolidation；
2. [TANGLE](https://arxiv.org/abs/2608.13921)：不可消解个人记忆冲突；
3. [StateFuse](https://arxiv.org/abs/2607.05844)：显式冲突对象与延迟裁决；
4. [DeMem](https://arxiv.org/abs/2605.10870)：decision-centric rate-distortion；
5. [Context Codec](https://arxiv.org/abs/2605.17304)：typed semantic commitments 与可验证压缩；
6. [Useful Memories Become Faulty](https://arxiv.org/abs/2605.12978)：consolidation-induced failure；
7. [MeClear](https://arxiv.org/abs/2609.09115)：组合式 harmful-memory attribution 与查询级抑制。

### P1：确定 Benchmark 维度

8. [MemoryAgentBench](https://arxiv.org/abs/2507.05257)；
9. [STALE](https://arxiv.org/abs/2605.06527)；
10. [StateMemBench](https://arxiv.org/abs/2608.19652)；
11. [AuthMem-Bench](https://arxiv.org/abs/2608.01679)；
12. [THEANINE](https://aclanthology.org/2025.naacl-long.435/)；
13. [Conflict-Aware Memory for Embodied Agents](https://aclanthology.org/2026.acl-long.1306/)。

### P2：实现与扩展

14. [MOSAIC](https://arxiv.org/abs/2607.16211)；
15. [MemTxn](https://arxiv.org/abs/2607.27834)；
16. [Dual-Layer Agentic Memory](https://arxiv.org/abs/2608.22215)；
17. [The Memory Trust Gap](https://arxiv.org/abs/2609.01852)；
18. [LightMem](https://aclanthology.org/2026.acl-long.588/)；
19. [Agentic Memory/AgeMem](https://aclanthology.org/2026.acl-long.981/)；
20. [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/)。

读每篇论文统一记录：

1. memory 的基本单位是什么？
2. 是否显式保存时间、条件、来源和类型？
3. 允许哪些 conflict/update 操作？
4. consolidation 是否有损，原始证据是否保留？
5. 评价节点、关系、答案还是真实行动？
6. 能否指出压缩错在何处并局部修复？
7. 在相同 token/调用预算下是否仍有优势？

---

## 14. 最终建议

当前最值得先做的不是泛化的“memory 冲突消解”，也不是立刻训练小模型吞下海量历史，而是：

> **先建立 ConflictClosureBench，验证有损巩固是否会在保留表面事实的同时破坏版本、条件、例外、未决和派生关系；若该 failure gap 成立，再实现 ClosureMem 的闭包验证与边级局部修复。**

这条线与现有工作距离足够近，能够继承成熟数据和系统；又比“把多个冲突任务合并起来”更窄、更可证伪。它的风险也很明确：Context Codec、DeMem、StateFuse 和 HiMem 是四个最强近邻，只有当关系闭包指标能额外解释行为错误、局部修复能带来真实成本收益时，方法贡献才站得住。

参数固化应作为后续扩展：把 closure-stable memory 写入小模型，把动态、未决和强 provenance 依赖内容留在外部。这样“冲突消解”和“海量记忆服务小模型”才是一条连续研究路线，而不是两个松散方向。
