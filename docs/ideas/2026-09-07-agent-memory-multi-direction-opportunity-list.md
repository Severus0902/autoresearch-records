---
title: "Agent Memory 多方向研究机会清单：从 Benchmark 到方法的候选组合"
type: research-opportunity-portfolio
status: candidate-portfolio
created: "2026-09-07"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "research-gap", "method", "evaluation", "idea-list"]
---

# Agent Memory 多方向研究机会清单：从 Benchmark 到方法的候选组合

> 检索截止时间：2026-09-07。本文在已有 Agent Memory 综述、两轮同期工作碰撞审计和 MemInvariantBench 方案上继续扩展，补查 2025--2026 正式论文与 arXiv 预印本。对“尚未有人做过”的判断均限定为“在本轮检索覆盖的公开工作中尚未发现完整等价协议”，不声称绝对首创。

## 0. 结论先行

### 0.1 不是只有一个方向，但不能把所有方向当成同等优先级

Agent Memory 至少可以从以下六个科学问题切入：

1. **同一语义的记忆，换一种形成或存储方式后，Agent 是否仍作出相同决策？**
2. **在搜索型 Agent 中，何时应该利用记忆，何时应该暂时抑制记忆以保留探索多样性？**
3. **多条记忆共同支持或共同误导一次决策时，哪些记忆组合才是必要且充分的？**
4. **在反复压缩和有限预算下，稀有但高后果的约束为何比普通事实更容易丢失？**
5. **写入时不知道未来问题，Agent 如何决定哪些内容值得长期保留？**
6. **从成功轨迹提炼出的技能记忆，在什么边界内可迁移，何时会造成负迁移？**

但截至本轮检索，后四条已经出现较强同期工作。综合**剩余创新空间、科学价值、可证伪性、4 张 RTX 4090 的资源适配和后续方法延展性**，推荐形成如下研究组合：

| 优先级 | 方向 | 类型 | 当前判断 |
|---|---|---|---|
| **P0-A** | MemInvariantBench：语义不变性与决定性敏感性 | Benchmark first | 最稳妥主线；问题清晰、低算力、可形成新评价单位 |
| **P0-B** | ExploreMem：搜索状态条件下的记忆介入策略 | Benchmark + method | 最有方法潜力；已有现象证据，但节点级控制尚未被完整闭合 |
| **P1-A** | CoalitionMem：记忆集合的必要性、充分性与交互贡献 | Benchmark first | 有价值，但与 Shapley 式价值评估相邻，必须强调集合交互而非单条打分 |
| **P1-B** | TailGuardMem：稀有高后果约束的预算化保存 | Benchmark + deterministic method | 痛点强，但已与 Compaction Cliff 正面相邻，只适合进一步收窄 |
| **P1-C** | BlindWriteBench：未知未来查询下的写入决策 | Benchmark first | 现实性强，但“what to remember”赛道拥挤，需要加入分布漂移和尾部损失 |
| **P2** | 技能边界、来源治理、共享记忆、修复、前瞻记忆、多模态 | Extension/watchlist | 均有直接同期工作，不建议作为当前独立主标题 |

### 0.2 推荐的实际决策

不建议现在只押一条线，也不建议同时搭六套完整 benchmark。最合理的是并行做两个一周级 smoke test：

- **主线验证：MemInvariantBench**，先判断当前系统是否真的存在稳定、可复现的语义实现敏感性。
- **方法线验证：ExploreMem**，先判断“记忆带来稳定性但损害搜索多样性”能否在两个领域、两类模型和可控任务中复现，并估计节点级 oracle gate 的上界。

若二者都成立，论文组合可以是：

> **第一篇做受控 benchmark，刻画记忆状态与行为之间的语义契约；第二篇做搜索状态条件的 memory controller，使 Agent 在利用经验与保持探索之间动态切换。**

这两条线共享底层日志协议、记忆干预器、行为追踪器和统计工具，但核心问题不同，不会互相重复。

## 1. 筛选标准

### 1.1 P0 / P1 / P2 的含义

- **P0**：可以立即做最小闭环，问题边界可防守，近期工作尚未覆盖完整协议。
- **P1**：科学问题成立，但存在强相邻或部分直接工作；必须用更窄定义和 pilot 数据证明增量。
- **P2**：已有直接同期工作，或当前资源成本过高；保留为评价维度、后续扩展或跟踪方向。

### 1.2 五项评分

每项 1--5 分：

- **N：剩余新颖性**，不是问题本身新不新，而是公开工作后还剩多少可防守空间。
- **S：科学重要性**，是否揭示一般性机制，而非只增加一个数据集。
- **F：可证伪性**，能否用受控变量和确定指标得出否定结论。
- **R：资源适配**，4 张 RTX 4090 是否足以完成主要实验。
- **M：方法延展性**，benchmark 后能否自然导出方法，而非勉强附加模型。

| 方向 | N | S | F | R | M | 总体 |
|---|---:|---:|---:|---:|---:|---|
| MemInvariantBench | 4.5 | 4.5 | 5.0 | 5.0 | 4.0 | **P0-A** |
| ExploreMem | 4.0 | 4.5 | 4.0 | 4.0 | 5.0 | **P0-B** |
| CoalitionMem | 3.0 | 4.0 | 4.5 | 3.5 | 4.0 | **P1-A** |
| TailGuardMem | 2.5 | 4.5 | 5.0 | 5.0 | 3.5 | **P1-B** |
| BlindWriteBench | 2.5 | 4.0 | 4.0 | 4.5 | 4.0 | **P1-C** |
| ScopeMem | 1.5 | 4.0 | 4.0 | 4.0 | 4.0 | P2 |
| Provenance / shared governance | 1.5 | 4.5 | 3.5 | 3.5 | 4.0 | P2 |
| Multimodal embodied memory | 2.0 | 4.0 | 3.5 | 2.0 | 4.0 | P2 |

分数是研究决策工具，不是对论文质量的评价。

## 2. P0-A：MemInvariantBench

### 2.1 一句话问题定义

> **当持久记忆表达的事实、约束和可支持行动的语义不变，但措辞、分块、顺序、冗余、会话边界或压缩实现发生变化时，Agent 是否保持正确行为；当仅改变一个决定性语义条件时，它又能否按预期改变行为？**

### 2.2 问题来源

现有 benchmark 已经分别覆盖长程召回、动态更新、战略使用、工具行动和记忆修复，但系统排名很容易受到模型、embedding、检索预算、写入粒度和 judge 的影响。MemDelta 表明仅替换 embedding 模型即可改变方法结论；Beyond Memory Leaderboards 进一步指出摄取粒度、原文保存、检索预算和评分器都会影响排名。

这些工作揭示了**评测配置混杂**，却没有完整回答另一个更基础的问题：

> 一个 memory system 是否对“任务语义等价、记忆实现不同”的输入保持一致，并对“表面接近、决定性语义不同”的输入保持敏感？

### 2.3 与最近工作的边界

| 工作 | 已解决 | 尚未覆盖的边界 |
|---|---|---|
| LongMemEval / LoCoMo | 长历史中的召回、更新和推理 | 不构造同一潜在记忆状态的 matched realization family |
| StratMem-Bench | required / supportive / irrelevant 的战略使用 | 候选记忆已给定，不检验同义状态在形成、存储和检索后的行为等价性 |
| MemDelta | 控制 backbone、embedding 与 retrieval pipeline | 控制的是系统组件，不是记忆语义状态的等价变换 |
| Beyond Memory Leaderboards | 揭示预算、粒度和 judge 对排名的影响 | 不要求同一实例同时满足正确不变性与决定性敏感性 |
| Compaction Cliff | 测试安全规则在多轮压缩中的保存 | 聚焦类型化安全规则和压缩，不覆盖多类 realization transformation 与全生命周期阶段归因 |

因此可防守的贡献不是“第一个做 memory robustness”，而是：

> **提出以 matched semantic families 为评价单位的持久记忆协议，同时测量正确不变性、决定性敏感性和失败阶段。**

### 2.4 Benchmark 路线

每个潜在语义状态 `z` 生成两类 family：

- **等价族** `E(z)`：改写、分块、重排、跨 session、增加受控冗余、压缩，但任务相关命题不变。
- **决定性对照族** `D(z)`：只改变一个会使正确行动变化的事实、授权、时间或约束。

固定 query、world state、tools、user goal 和模型，只改变 memory realization。记录：

- 写入后的 canonical memory state；
- 检索到的证据集合；
- 最终答案和工具行动；
- 证据引用与记忆更新；
- 每个变体的 token、位置和检索预算。

核心指标：

- **Family Worst-Case Accuracy (FWA)**：同一家族最差变体的正确率。
- **Correct Invariance Rate (CIR)**：等价族内是否全部保持正确行动。
- **Decisive Sensitivity Rate (DSR)**：决定性条件改变后行为是否正确翻转。
- **Balanced Memory Contract Score (BMCS)**：联合 CIR 与 DSR，防止“永远忽略记忆”获得高分。
- **Stage Attribution**：formation、storage、retrieval、use 中最早出现差异的位置。

### 2.5 方法路线

第二阶段可以做 `EquiMem`：

- 命题级 canonicalizer 将不同文本映射到带来源、时间、权限和作用域的 proposition；
- 对等价变体加入 representation-consistency loss；
- 对决定性对照加入 contrastive sensitivity loss；
- 多候选记忆使用 pairwise/listwise 排序，优先决定性证据而非表面相似文本。

先做 rule-based canonicalizer 和 reranker，再考虑 LoRA；不需要一开始训练大模型或做 RL。

### 2.6 一周最小实验与停止条件

- 40--60 个 base cases，每例 4 个等价变体和 2 个决定性变体。
- 两个 7B/8B 级开源模型，两个 memory backend，加 full-context control。
- 若大于 15% 的 base family 出现“单例正确但 family 失败”，且错误不能由长度和位置完全解释，则继续。
- 若所有系统 CIR 都高于 95%，或差异主要来自普通 prompt sensitivity，则停止独立 benchmark，转为其他方向的 robustness test。

详细方案见：[MemInvariantBench 完整提案](2026-09-07-meminvariantbench-autonomous-exploration-and-proposal.md)。

## 3. P0-B：ExploreMem

### 3.1 一句话问题定义

> **搜索型 Agent 能否根据当前节点的不确定性、分支新颖性和记忆适用性，逐节点决定使用、降权或暂时屏蔽长期记忆，从而同时保留经验带来的可靠性与搜索所需的多样性？**

工作名可暂定：

> **ExploreMem: Search-State-Conditioned Memory Gating for Reliable and Diverse Agents**

### 3.2 问题来源

两项正式论文共同给出了很强的现象证据：

- ACL 2026 的 SteeM 指出，长期交互中的记忆存在 **anchoring 与 under-use** 的矛盾，并将记忆依赖程度建模为可控制维度。
- ACL 2026 Findings 的 MLE Agent 研究发现，记忆对 chain-based agent 有利，却会限制 tree-based agent 的搜索多样性，导致过早收窄。

它们说明“越多用 memory 越好”并不成立，但尚未完整闭合以下决策问题：

> **不是由用户全局指定依赖程度，也不是对整条轨迹固定开关，而是在搜索树的每个节点根据状态动态决定 memory exposure。**

### 3.3 与最近工作的边界

| 工作 | 已解决 | ExploreMem 的剩余边界 |
|---|---|---|
| SteeM | 用户可控制整体 memory dependence | 控制信号主要来自用户或全局模式，不是搜索节点状态上的自主策略 |
| Demystify the Role of Memory in MLE Agents | 观察 chain/tree 架构下稳定性与多样性的差异 | 主要是机制研究，没有学习何时在单个搜索节点介入记忆 |
| Branch-and-Browse / Arbor | 将树搜索、上下文或行动记忆结合 | 记忆用于共享和加速，不以 memory-induced exploration collapse 为控制目标 |
| AT2PO 等树搜索 RL | 优化分支扩展和 turn-level credit | 没有把长期 memory exposure 当作可学习动作 |
| BASM | 判断技能记忆是否适用于当前任务 | 解决技能边界，不直接优化搜索树中的探索-利用日程 |

本方向不能声称“首次研究 memory anchoring”或“首次平衡探索与利用”。较可防守的表述是：

> **将 memory exposure 提升为搜索过程中的节点级动作，并用 matched search tasks 测量其对成功率、分支覆盖、重复探索和负迁移的因果影响。**

### 3.4 Benchmark 路线

构造具有以下结构的任务：

- 历史记忆提供一个高频成功策略；
- 当前任务存在 `same-regime`、`near-regime` 和 `shifted-regime` 三种条件；
- 旧策略在前两类中分别有用或部分有用，在第三类中会使搜索过早收敛；
- 任务必须允许多条候选路径、回溯和确定性执行评分。

首版可选两个低成本域：

- **代码修复 / MLE 迷你任务**：旧 debug experience 对相似错误有用，但对 API 或数据分布变化可能误导。
- **文本化工具环境**：工具集或参数约束发生局部变化，旧 workflow 只能在部分节点复用。

对照组：

- no memory；
- always-on memory；
- trajectory-level gate；
- random node gate；
- applicability-only gate；
- node-level oracle gate。

核心指标：

- `Task Success` 与执行成本；
- `Unique Branch Coverage`；
- `Premature Convergence Rate`；
- `Memory-Induced Negative Transfer`；
- `Reliability--Diversity Pareto Area`；
- 与 node-level oracle 的 `Gating Regret`。

### 3.5 方法路线

将 `g_t in {USE, DOWNWEIGHT, SUPPRESS, VERIFY}` 作为搜索节点动作，输入可包含：

- 当前节点不确定性或 value margin；
- 候选动作熵；
- 检索记忆与当前状态的适用性分数；
- 当前分支与历史轨迹的相似度；
- 已探索分支覆盖率；
- 记忆来源、时间和失败记录。

训练顺序：

1. 用 oracle rollouts 构造 node-wise preference pairs；
2. 训练轻量 gate 或 reranker，不改 backbone；
3. 再比较 contextual bandit、pairwise/listwise preference learning；
4. 只有延迟回报确实无法由局部标签近似时，再做 GRPO/GSPO 类在线优化。

这条线与此前 KGR 的排序经验可以自然衔接：同一搜索状态下比较 `USE vs SUPPRESS` 或多个 memory package，是一个真正的相对决策问题，而不是给每条记忆单独打 pointwise 分数。

### 3.6 一周最小实验与停止条件

- 先选 30--50 个可重复执行任务，每个任务制造 same/near/shifted 三个版本。
- 使用固定 backbone，比较 no-memory、always-on 和 oracle node gate。
- 若 always-on 相比 no-memory 在 shifted 条件明显下降，而 oracle gate 能回收至少一半差距，同时不损害 same-regime，则继续做学习 gate。
- 若 memory 只改变 token 成本、不改变搜索多样性，或 oracle gate 上界很低，则停止该方向。

## 4. P1-A：CoalitionMem

### 4.1 一句话问题定义

> **当一次正确行动依赖多条互补、冗余或相互冲突的记忆时，Agent 能否识别最小充分记忆集合，并避免把单条记忆的平均贡献误当成独立价值？**

### 4.2 为什么值得研究

真实决策通常不是由一条 memory 单独支持：

- 用户偏好与当前授权需要共同成立；
- 一个事实只有结合时间信息才是有效证据；
- 两条低风险记忆合在一起可能触发高风险行动；
- 两条冗余记忆各自 leave-one-out 贡献接近零，但删除两条就会失败。

因此 pointwise utility 很难表示互补、替代和冲突关系。

### 4.3 同期碰撞与可做边界

MemLens 已经把 Shapley-style memory evaluation 用于单条记录价值分析；Decision-Aware Memory Cards、MemAudit 和 ActMem 也在研究记忆对行动的因果影响。更广义的 AgentSHAP 已把 Shapley 估计用于工具归因。

因此不能把“对 memory 做 Shapley value”当创新。可收窄为：

> **不追求每条记忆的单一全局分数，而是评测系统能否恢复最小充分集、最小阻断集以及高阶交互类型。**

### 4.4 Benchmark 与指标

为每个任务显式构造 4--8 条候选记忆，并通过符号规则定义：

- `complementary`：A 与 B 同时存在才足够；
- `substitutable`：A 或 B 任一即可；
- `inhibitory`：C 会使 A 的使用无效；
- `conditional`：D 只在时间或权限条件 E 下可用。

枚举小集合的所有子集，得到真实 utility lattice。评测：

- Minimal Sufficient Set Recovery；
- Minimal Blocking Set Recovery；
- Pairwise Interaction Sign Accuracy；
- Coalition Regret under token budget；
- 单条排序、Shapley 近似与 listwise set selector 的差距。

### 4.5 最小实验与停止条件

- 20 个符号可验证任务，每例不超过 8 条 memory，允许精确枚举。
- 若 pointwise / leave-one-out / Shapley 已与最优集合选择没有显著差距，则停止。
- 若高阶交互导致 10% 以上可重复的选择 regret，再扩展到自然语言和工具环境。

### 4.6 风险判断

这是一个漂亮但审稿风险较高的方向：容易被认为是 data valuation 或 feature attribution 的移植。必须证明**集合结构导致现有 memory system 的实际行动失败**，不能只展示新的数学指标。

## 5. P1-B：TailGuardMem

### 5.1 一句话问题定义

> **在相同 token 预算与多轮压缩下，memory system 能否优先保存低频但一旦丢失就会造成高代价行动错误的约束，而不是被高频、相似但低后果的事件淹没？**

### 5.2 问题来源与正面碰撞

这个痛点非常真实，但已经出现强直接工作：The Compaction Cliff 报告安全规则在多轮压缩中快速丢失，并提出按知识类型路由的 Knowledge Triage；OSL-MR 将 retention 建模为包含 miss、重获取和 stale risk 的约束优化；Retain or Consolidate 研究预算下的 Merge / Abstract / Rewrite 选择。

所以“关键规则在压缩中会丢失”已经不能作为新发现。剩余空间只能更窄：

- 从平均 rule recall 转向**任务后果加权的尾部风险**；
- 同一条关键约束在不同语言位置、表述和跨 session 频率下的 worst-case preservation；
- 不向算法提供人工知识类型，测试系统能否从行为后果学习风险；
- 比较 rule 被保存但未被执行，与 rule 在存储阶段已经丢失。

### 5.3 Benchmark 与方法

Benchmark 将普通事实、偏好、成功日志和安全约束混合，控制每类频率、位置、压缩轮次和后果成本。指标包括：

- Critical Constraint Survival；
- Cost-Weighted Violation Rate；
- Worst-Case Tail Loss；
- Preservation--Compression Pareto；
- Stored-but-Unenforced Rate。

方法先用 deterministic typed retention 做强基线，再尝试 cost-sensitive selector。若不提供类型标签后性能无法泛化，说明该问题更像 schema engineering，不宜扩大方法主张。

### 5.4 优先级判断

适合做 **P1 复现实验或 MemInvariantBench 的一个重要 family**，不建议单独作为当前第一篇论文标题，除非 pilot 发现现有 Knowledge Triage 在未知类型、跨语言或尾部后果上仍系统性失败。

## 6. P1-C：BlindWriteBench

### 6.1 一句话问题定义

> **当 memory 写入或遗忘发生时未来查询尚不可见，Agent 能否根据当时可观察的信息保存对未来任务真正有用的内容，并在任务分布变化时控制遗漏、陈旧与存储成本？**

### 6.2 为什么是 memory 问题

许多评测在给定当前 query 后选择证据，这更接近 retrieval。长期记忆的真正难点是：写入决策发生在 `t`，价值却要到未来 `t+k` 才显现。若训练和测试时让 selector 看到未来问题，会形成 oracle leakage。

### 6.3 同期工作与剩余空间

- OSL-MR 已强调 online-observable features 与 offline supervision 的分离，并建模 delayed costs。
- Learning What to Remember 的多因素价值模型明确区分 query-visible retrieval 与 blind forgetting。
- AdaMem 研究偏好条件的自适应写入策略。
- Nemori、MEMAUDIT、Retain or Consolidate 等也覆盖 future utility、预算选择或 consolidation。

因此一般性的“未知未来下学习 what to remember”已经拥挤。若继续做，必须加入现有工作未同时覆盖的结构：

1. 训练与测试 future-query distribution 发生可控漂移；
2. 评价平均准确率之外的 rare-event miss 和 regret；
3. 区分“没写入”“写入后被压缩掉”“写入并检索但未执行”；
4. 给出 clairvoyant oracle、observable oracle 和 online policy 三层上界。

### 6.4 最小实验与停止条件

- 用程序生成 100 条 session streams，隐藏未来 query，仅暴露历史事件和当时元数据。
- 比较 keep-all、recency、similarity、multi-factor、OSL-MR 风格 policy 与 oracle。
- 若分布漂移下所有方法都等比例下降且无可学习信号，则停止；若 observable oracle 与现有 policy 存在大差距，再进入方法阶段。

## 7. P2：ScopeMem，程序性记忆的适用边界

### 7.1 一句话问题定义

> **从历史成功轨迹提炼出的技能在遇到相似表面状态、不同工具或不同前置条件时，Agent 能否判断该技能何时可用、何时应拒绝模仿？**

这是很自然的方法方向，但已经出现直接工作：When Continual Learning Moves to Memory 发现外部经验复用只是把稳定性--可塑性问题迁移到 memory；EMNLP 2026 Findings 的 BASM 更直接构造 applicability conditions、risk cues、avoidance rules 和 recovery notes，显著缓解 skill imitation trap。

因此不建议再做宽泛的“给 skill memory 增加 boundary”。可以保留的扩展包括：

- compositional skills 的组合边界；
- 边界本身过期或冲突时如何更新；
- 跨模型迁移时 boundary calibration 是否失真；
- 将 ScopeMem 作为 ExploreMem 的 applicability feature 和 baseline。

## 8. 其他 P2 方向与不优先原因

### 8.1 来源、权限与 provenance laundering

问题很重要：低可信网页内容在 consolidation 后可能被改写成类似用户指令，来源权威被“洗白”。但已有 Memory Provenance Laundering 与 PPMF、Agent Zero Memory、AuthMem、MemLineage 等直接工作。更适合作为 MemInvariant 的 authority transformation 或共享记忆评价维度。

### 8.2 多 Agent 共享记忆治理

GroupMemBench、MAP-Graph、GateMem、Governed Shared Memory、Topology Matters 和 MemTX 已覆盖共享、拓扑、访问控制、事务提交或级联修复。当前若进入，需要真实组织权限、跨 Agent 责任归因或并发一致性等更窄系统问题，工程量较大。

### 8.3 记忆修复与外部状态恢复

MemoRepair、MemTX、From Faulty Memories to Corrected Actions、MemSecBench 和 SagaLLM 已覆盖级联更新、选择性回滚、记忆到外部后果和事务补偿。原来的 repair-locus uncertainty 仍可作为诊断维度，但目前不如两个 P0 方向干净。

### 8.4 前瞻记忆

PM-Bench、TriggerBench、ENPMR-Bench、LoCoMo-Plus 和 Typed Intention Store 已快速覆盖延迟意图、隐式触发与 intention storage。赛道新但拥挤，除非转向多意图冲突、不可逆动作前确认或真实日历/邮件工具，否则不宜重复搭 benchmark。

### 8.5 多模态与具身记忆

MEMLENS、MM-Mem、Mem-Gallery、SpaMEM、eMEM 和 MAGNET 已覆盖跨模态长期记忆、视觉细节损失和具身空间记忆。科学空间仍大，但数据构造、视频处理和环境交互成本较高，不符合当前 4 张 4090 的首发优势。

### 8.6 隐私、删除与可撤销记忆

Deployment-Time Memorization、PerMemSafe、GateMem 和多项 memory unlearning 工作已覆盖删除残留、隐私泄露和访问控制。该方向评价要求攻击模型、隐私威胁模型和系统级删除审计，适合与安全团队合作，不建议当前单独起步。

## 9. 两条 P0 如何区分，又如何共享基础设施

| 维度 | MemInvariantBench | ExploreMem |
|---|---|---|
| 核心自变量 | 同一语义状态的不同 memory realization | 搜索节点上的 memory exposure policy |
| 研究对象 | formation--storage--retrieval--use 的语义契约 | memory 与搜索探索/利用的动态关系 |
| 主要失败 | 表面实现改变导致行为漂移；决定性变化未触发行为改变 | 记忆锚定导致过早收敛；禁用记忆导致重复犯错 |
| 主要贡献形态 | 受控 benchmark、family-level metric、阶段归因 | matched search benchmark、node-level controller |
| 是否需要训练 | 首版不需要 | 首版不需要，第二阶段训练轻量 gate |
| 后续方法 | canonicalization + consistency/sensitivity | pairwise/listwise gate，必要时在线 RL |

二者可以共享：

- 标准化 memory object：content、source、time、authority、scope、confidence；
- memory exposure 和 intervention API；
- agent trajectory logger；
- deterministic tool evaluator；
- family-level bootstrap 与 paired significance test；
- Qwen2.5-7B、Llama-3.x-8B 等本地基线。

## 10. 建议的并行最小验证计划

### 第 1 周：不训练，只测问题是否真实存在

**Track A：MemInvariant**

- 20 个 base tasks；
- 每个任务 3 个等价变体 + 1 个决定性变体；
- full-context、naive RAG、一个真实 memory backend；
- 输出 CIR、DSR 与 formation/retrieval/use 的初步归因。

**Track B：ExploreMem**

- 15 个 base search tasks；
- 每例 same-regime 与 shifted-regime；
- no-memory、always-on、trajectory gate、node oracle；
- 输出成功率、分支覆盖和 gating oracle gap。

### 第 2 周：只扩成立的方向

- 若 Track A 的 family failure 稳定，扩到 50--100 个 base cases 并增加 backend。
- 若 Track B 的 oracle gap 稳定，生成节点级 pairwise 数据并训练小 gate。
- 若两条都不成立，再启动 CoalitionMem 的精确小集合实验，不直接进入大规模方法开发。

### 第 3--4 周：形成可投稿的最小故事

- Benchmark 论文至少包含 3 类 memory state、2 个任务域、3 个 memory baseline、2 个 backbone、严格 matched intervention 和人工审计。
- 方法论文先证明 learned gate 接近 oracle、优于 always-on/no-memory，并在未见任务变化上泛化。
- 只有轻量方法在 held-out 上成立后，再使用 4 张 4090 做 LoRA 或小规模 RL。

## 11. 论文故事建议

### 11.1 最稳主故事

> 现有 Agent Memory benchmark 主要按独立实例汇总最终准确率，难以判断系统是否真正保持了持久记忆的任务语义。我们以 matched semantic families 为评价单位，要求系统同时满足语义不变性与决定性敏感性，并定位 formation、retrieval 和 use 阶段的失效。

### 11.2 最有方法感的故事

> 现有长期记忆要么持续注入搜索过程、造成经验锚定和探索收缩，要么被整体关闭、失去经验复用收益。我们将 memory exposure 建模为搜索节点级决策，并学习在可靠性和分支多样性之间动态切换。

### 11.3 不建议的宽泛故事

- “现有 memory benchmark 只测事实召回”：2026 年已不成立。
- “现有工作不会决定何时使用 memory”：StratMem、SteeM、SafeCommit、BASM 等已覆盖多个版本。
- “现有工作没有研究 memory repair”：MemTX、MemoRepair、MemSecBench 等直接冲突。
- “现有 memory system 不会决定 what to remember”：OSL-MR、AdaMem、Nemori、MEMAUDIT 等已形成拥挤赛道。
- “我们首次对 memory 做 ranking / Shapley”：MemReranker、SkillReranker、MemLens 等已削弱该表述。

## 12. 最终排序与选择原则

### 12.1 当前排序

1. **MemInvariantBench**：最适合先做 benchmark，最符合当前资源和前期积累。
2. **ExploreMem**：最值得并行验证，若 oracle gap 大，方法潜力甚至高于第一条。
3. **CoalitionMem**：作为集合交互方向的储备，理论结构好但审稿边界较险。
4. **TailGuardMem**：作为压力测试很强，作为独立标题已被近期工作挤压。
5. **BlindWriteBench**：现实问题明确，但需要用分布漂移和尾部损失避开同期拥挤区。
6. **ScopeMem 及其他 P2**：作为模块或评价维度，不单独立项。

### 12.2 选择不是靠“哪条听起来更新”，而是靠三个可观测量

- **现象幅度**：受控干预是否产生足够大的、跨模型可复现的行为差异。
- **oracle gap**：完美诊断或完美控制相对现有系统是否存在实质上界。
- **方法可学性**：不用未来信息时，轻量策略能否稳定缩小 oracle gap。

只要其中任意一项不成立，就应及时停止，而不是继续扩大数据规模掩盖问题。

## 13. 核心参考文献

### 13.1 P0-A：不变性与评测混杂

- [MemDelta: Controlled Baselines and Hidden Confounds in Agent Memory Evaluation](https://arxiv.org/abs/2606.29914), arXiv, 2026.
- [Beyond Memory Leaderboards: Evaluating Scientific Memory as Budgeted Context Restoration](https://arxiv.org/abs/2607.16848), arXiv, 2026.
- [The Compaction Cliff in Long-Running AI Agent Memory](https://arxiv.org/abs/2608.22752), CIKM 2026.
- [StratMem-Bench: Evaluating Strategic Memory Use in Virtual Character Conversation Beyond Factual Recall](https://aclanthology.org/2026.acl-long.1491/), ACL 2026 Long.

### 13.2 P0-B：记忆锚定与搜索多样性

- [Controllable Memory Usage: Balancing Anchoring and Innovation in Long-Term Human-Agent Interaction](https://aclanthology.org/2026.acl-long.670/), ACL 2026 Long.
- [Demystify the Role of Memory in Machine Learning Engineering Agents](https://aclanthology.org/2026.findings-acl.525/), Findings of ACL 2026.
- [Branch-and-Browse: Efficient and Controllable Web Exploration with Tree-Structured Reasoning and Action Memory](https://aclanthology.org/2026.acl-long.838/), ACL 2026 Long.
- [AT2PO: Agentic Turn-based Policy Optimization via Tree Search](https://aclanthology.org/2026.acl-long.1106/), ACL 2026 Long.

### 13.3 记忆价值、保留与集合贡献

- [MemLens: A Value-Aware Memory Management System with Interactive Analytics for LLM-based Agents](https://arxiv.org/abs/2607.25992), arXiv, 2026.
- [Learning What to Remember: Observability-Safe Memory Retention via Constrained Optimization for Long-Horizon Language Agents](https://arxiv.org/abs/2606.10616), arXiv, 2026.
- [Learning What to Remember: A Cognitively Grounded Multi-Factor Value Model for Agentic Memory](https://arxiv.org/abs/2606.12945), arXiv, 2026.
- [AdaMem: Learning What to Remember with Adaptive Memory Policies for Personalized Agents](https://arxiv.org/abs/2606.21144), arXiv, 2026.
- [Retain or Consolidate? Budget-Dependent Operator Selection for Language Agent Memory](https://arxiv.org/abs/2607.17545), arXiv, 2026.

### 13.4 程序性记忆、来源与其他前沿

- [When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents](https://arxiv.org/abs/2604.27003), arXiv, 2026.
- [When Not to Imitate: Boundary-Aware Skill Memory for Reliable Tool-Use LLM Agents](https://arxiv.org/abs/2608.22339), EMNLP 2026 Findings.
- [Memory Provenance Laundering in LLM Agents](https://arxiv.org/abs/2607.29167), arXiv, 2026.
- [PM-Bench: Evaluating Prospective Memory in LLM Agents](https://arxiv.org/abs/2607.12385), arXiv, 2026.
- [MEMLENS: Benchmarking Multimodal Long-Term Memory in Large Vision-Language Models](https://arxiv.org/abs/2605.14906), arXiv, 2026.

## 14. 与仓库已有材料的关系

- [2025--2026 Agent Memory 顶会综述](../reports/2026-09-07-agent-memory-2025-2026-top-conference-survey.md)：领域定义、方法演化和 benchmark 地图。
- [第一轮切入点审计](../reports/2026-09-07-agent-memory-gap-and-entry-point-audit.md)：诊断、行动和 repair 闭环的边界。
- [第二轮同期碰撞审计](../reports/2026-09-07-agent-memory-second-collision-audit.md)：MemTX 等工作对 repair 方案的进一步挤压。
- [MemInvariantBench 完整方案](2026-09-07-meminvariantbench-autonomous-exploration-and-proposal.md)：P0-A 的严格定义、数据构造、指标和方法细节。

## 15. 最终建议

当前不应把研究方向重新扩回“Agent Memory 全生命周期大 benchmark”。更好的策略是保留一个有层次的候选组合：

> **以 MemInvariantBench 作为低风险 benchmark 主线，以 ExploreMem 作为高方法潜力的并行主线，以 CoalitionMem 作为精确集合实验的储备；其余方向作为压力测试和评价维度吸收，而不是重新单独立项。**

这样既不把所有希望押在一个问题上，也避免在已经拥挤的写入、遗忘、冲突和修复赛道里重复造轮子。
