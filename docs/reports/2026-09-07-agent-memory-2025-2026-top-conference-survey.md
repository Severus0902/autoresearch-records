---
title: "2025-2026 Agent Memory 顶会文献综述：定义、方法、评测与未来趋势"
type: literature-review
status: reviewed
created: "2026-09-07"
updated: "2026-09-07"
scope: "ACL/EMNLP/NAACL/COLM/NeurIPS/ICLR/ICML，补充重要 arXiv 前沿"
tags: ["agent-memory", "survey", "benchmark", "reinforcement-learning", "2025", "2026"]
---

# 2025-2026 Agent Memory 顶会文献综述：定义、方法、评测与未来趋势

> 文献状态核验截止：2026-09-07。本文把主会长文、Findings、Industry/Workshop 与 arXiv 预印本分开标注。所谓“近两年所有有关论文”，在本文中操作化为：对 2025-2026 年 ACL、EMNLP、NAACL、COLM、NeurIPS、ICLR、ICML 的论文题名与摘要进行检索，纳入以 Agent Memory 的形成、组织、检索、使用、更新、遗忘、修复、治理或评测为主要贡献的工作；仅把 memory 用作 KV cache、GPU 显存、模型参数记忆或附属模块的工作不进入核心清单。

## 摘要

2025-2026 年，Agent Memory 的研究对象已经发生了明显变化。早期问题是“怎样让模型在很长的历史中找回信息”，近期问题则是“怎样让 Agent 在持续交互中形成、组织、选择、验证、使用、更新和修复可持续状态，并让这种状态可靠地影响后续行动”。这一变化带来四条同步演进路线：

1. **存储结构**从平坦文本或向量库，走向分层记忆、事件图、超图、时间树、程序性技能和混合显式/隐式状态；
2. **控制方式**从固定的写入与 Top-k 检索，走向由 Agent 主动调用记忆操作，并进一步使用 DPO、PPO、GRPO、DAPO 等方法学习 memory policy；
3. **评测对象**从最终问答准确率，扩展到动态更新、选择性遗忘、战略使用、工具调用、on-policy 交互、操作级失败归因和安全承诺；
4. **系统目标**从单一效果最大化，扩展到准确性、成本、时延、可追溯性、权限、隐私和长期副作用之间的 Pareto 权衡。

综合正式论文与最新预印本，本文得到五个稳定判断。第一，**相关记忆被召回不等于记忆可以被使用，更不等于证据已足以支持行动**。第二，**更多记忆并不单调地带来更好表现**，陈旧、冲突、过度压缩、来源不明或越权的记忆会产生负迁移。第三，**压缩与可验证性存在结构性冲突**：越紧凑的状态越便宜，但越可能丢失时间、来源、限定条件和版本关系。第四，**RL 正从“优化最终回答”转向“学习何时及如何管理记忆”**，但奖励有效性、长程信用分配与错误写入后的累积风险仍未解决。第五，**评测的发展仍慢于方法**：现有 benchmark 已覆盖许多单点能力，却仍缺少统一、受控的 memory-state intervention，将诊断、行动、修复和未来效用置于同一个纵向实验单元。

---

## 1. 综述范围与证据标准

### 1.1 检索范围

核心会议范围包括：

- NLP：ACL、EMNLP、NAACL、COLM；
- 机器学习：NeurIPS、ICLR、ICML；
- ACL Findings、NAACL Industry 和 NeurIPS Workshop 被保留，但在表中显式标注，不与主会长文混称；
- 2026 年尚未经过同行评审、但会直接影响选题判断的工作，放入“前沿预印本”小节，不计入正式顶会结论。

检索关键词包括 `agent memory`、`agentic memory`、`long-term memory`、`episodic memory`、`procedural memory`、`experience replay`、`memory benchmark`、`memory management`、`memory-to-action`、`forgetting`、`memory safety` 等。纳入时再人工判断“memory 是否是论文主要研究对象”。

### 1.2 证据等级

| 等级 | 来源 | 本文用途 |
|---|---|---|
| A | 正式会议论文页与论文正文 | 支撑问题、方法、结果与接收出处 |
| B | Findings、Industry、Workshop、OpenReview 正式页面 | 支撑方法比较，并明确发表层级 |
| C | arXiv 预印本、技术报告 | 判断前沿趋势和撞题风险，不等价于正式接收 |
| D | 项目页、GitHub、作者博客 | 补充代码、数据和复现信息，不单独支撑核心学术结论 |

### 1.3 完整性的边界

本报告给出的是一个**可复核的领域语料集**，而不是声称题名中出现 `memory` 的论文都属于 Agent Memory。以下工作被排除或列为相邻方向：

- KV cache、attention memory、推理显存优化；
- 语言模型参数记忆、知识编辑、机器遗忘；
- 传统 POMDP/RNN memory，且不以 LLM Agent 为对象；
- 普通 RAG，只读取静态文档，不形成跨会话持久状态；
- 应用系统中存在一个 memory 模块，但论文贡献主要是推荐、医疗或机器人任务本身。

---

## 2. 术语表

| 术语 | 本文定义 | 容易混淆之处 |
|---|---|---|
| Agent Memory | 由历史交互形成、可跨时间或跨会话保留，并被 Agent 选择性读写以影响后续行为的状态 | 不等同于把历史全文塞进 prompt |
| Memory item | 一条可寻址的记忆单元，如事实、事件、经验、规则、技能或意图 | 粒度可以是 turn、event、summary、graph node |
| Memory state | 某时刻全部有效记忆及其版本、时间、来源、权限和关系 | 不是孤立的一条文本 |
| Memory system | 完成写入、组织、检索、更新、遗忘和治理的整体后端 | 可以是向量库、图、层次结构或学习模型 |
| Memory policy | 决定何时写、读、验证、使用、忽略、更新或删除的策略 | 可以是规则、LLM prompt 或训练得到的 policy |
| Working memory | 当前任务内维持和重写的临时状态 | 常与 context management 重叠，不一定跨 session |
| Episodic memory | 带时间、参与者、环境和结果的具体经历 | 与抽象事实或技能不同 |
| Semantic/factual memory | 从历史中保留的事实、偏好、概念和稳定关系 | 需要处理时间有效性和来源 |
| Experiential memory | 从一个或多个轨迹中归纳出的经验、反思和策略 | 可能产生错误归因或过度泛化 |
| Procedural memory | 可被复用的步骤、计划、工作流或技能 | 重点是“如何做”，不是“发生了什么” |
| On-policy memory evaluation | Agent 的行为会改变后续交互和未来记忆 | 与固定历史的 off-policy 评测不同 |
| Repair | 新证据到来后进行更新、失效、合并、恢复来源或保留冲突 | 不只是用新文本覆盖旧文本 |

---

## 3. Agent Memory 的定义

### 3.1 工作定义

本文采用以下定义：

> **Agent Memory 是由 Agent 与用户、工具或环境的历史交互形成，能够跨当前上下文、时间或会话持续存在，并在后续感知、推理、规划、行动或自我改进中被选择性读写和更新的状态。**

该定义至少要求三点：

1. **持久性（persistence）**：信息不只存在于当前 prompt，而能跨 turn、episode 或 session 保留；
2. **能动性（agency）**：Agent 或 memory policy 对写入、组织、检索、使用、更新、遗忘具有决策作用；
3. **行为后果（behavioral consequence）**：记忆会改变回答、计划、工具调用或环境动作。

形式化地，历史交互记为

\[
H_{1:t-1}=\{u_i,a_i,o_i,f_i\}_{i=1}^{t-1},
\]

其中 `u`、`a`、`o`、`f` 分别表示用户输入、Agent 动作、环境观察和反馈。持久记忆状态为

\[
M_t=\mathcal{U}(M_{t-1},H_t;\pi_M),
\]

其中 `U` 是状态更新过程，`π_M` 是 memory policy。Agent 的任务策略为

\[
\pi_A(a_t\mid o_t,g_t,C_t,M_t),
\]

只有当 `M_t` 来自历史、跨时刻保存并实际改变 `π_A` 时，问题才真正落在 Agent Memory 上。

### 3.2 与相邻概念的边界

| 概念 | 核心对象 | 典型时间尺度 | 与 Agent Memory 的关系 |
|---|---|---|---|
| LLM Memory | 参数、激活、KV cache、长上下文能力 | 单次推理到模型生命周期 | 更偏模型架构，不必包含 Agent 决策或跨会话状态 |
| RAG | 外部文档库与当前 query | 通常为单次查询 | 文档库通常不是由 Agent 历史交互形成，也不持续演化 |
| Agentic RAG | 主动规划、搜索、阅读和停止 | 单任务、多步 | 与 memory 共用检索和控制，但不必维护未来会话状态 |
| Context Engineering | 当前上下文的选择、压缩和编排 | 当前任务 | 管理瞬时计算资源，持久记忆只是可被编排的一类来源 |
| Agent Memory | 历史形成的事实、事件、经验、状态和技能 | 跨 turn、session、task | 强调生命周期、状态演化和后续行为影响 |

最实用的区分问题是：**将当前 query 删除后，这些信息是否仍因过去的交互而存在，并且会在未来任务中继续被访问、修改或失效？** 若答案是否定的，它更可能是 RAG 或 context engineering。

---

## 4. 统一分类：形式、功能与动态

`Memory in the Age of AI Agents` 用 forms、functions、dynamics 三个视角组织该领域，这比单纯的 long-term/short-term 分类更适合当前系统。

### 4.1 按形式（Form）

| 形式 | 代表机制 | 优点 | 主要风险 |
|---|---|---|---|
| Token/text memory | 原始轨迹、note、summary、文件 | 可读、易接入任意 LLM | 冗余、上下文成本、语义漂移 |
| Structured memory | 表、JSON、event graph、timeline、hypergraph | 可寻址、可组合、可追溯 | 构建误差、schema 锁定、维护成本 |
| Parametric memory | 微调、LoRA、持续学习 | 推理时紧凑、无需显式检索 | 难删除、难审计、灾难性遗忘 |
| Latent memory | memory token、隐藏状态、压缩向量 | 高压缩率、低 token 成本 | 不透明、不可逆、难验证 |
| Hybrid memory | 原始事件 + 图/索引 + 摘要/策略 | 兼顾证据与效率 | 系统复杂、跨层一致性难保证 |

### 4.2 按功能（Function）

- **事实/语义记忆**：用户事实、偏好、环境知识和稳定关系；
- **情景记忆**：带时间与上下文的具体经历；
- **经验记忆**：由轨迹和反馈形成的反思、注意事项和策略；
- **程序性记忆**：可复用的计划、工具链、技能和工作流；
- **工作记忆**：当前长程任务中的中间状态和未完成目标；
- **前瞻记忆**：在未来条件满足时执行的延迟意图。

### 4.3 按动态（Dynamics）

| 阶段 | 核心动作 | 典型失败 |
|---|---|---|
| Formation | 抽取、写入、摘要、反思、经验蒸馏 | 漏写、幻觉写入、错误归因 |
| Organization | 索引、聚类、链接、分层、版本化 | 错链、错簇、来源丢失 |
| Retrieval | 候选生成、排序、多步访问、停止 | 相似但不适用、旧版本抢占 |
| Consumption | 选择、整合、验证、action grounding | 召回后误用、证据不足即执行 |
| Evolution | 更新、合并、失效、遗忘、抽象 | 旧值残留、错误覆盖、污染扩散 |
| Governance | 权限、来源、隐私、冲突、审计 | 越权、泄露、authority collapse |

### 4.4 从三阶段演化到六阶段生命周期

`From Storage to Experience` 将技术演化概括为 `Storage -> Reflection -> Experience`。对评测而言，还需要更细的生命周期：

\[
\text{Form}\rightarrow\text{Diagnose}\rightarrow\text{Control}\rightarrow\text{Commit}\rightarrow\text{Repair}\rightarrow\text{Re-evaluate}.
\]

- `Form`：过去交互形成哪些 memory items；
- `Diagnose`：判断覆盖度、时效性、来源、权限和一致性；
- `Control`：选择 use、search、verify、ask、ignore 或 abstain；
- `Commit`：输出回答、工具调用或环境行动；
- `Repair`：依据新证据 update、invalidate、merge 或 restore provenance；
- `Re-evaluate`：在未来相关与无关任务上测长期净收益。

这一生命周期把“记住什么”升级为“什么时候足以支持下一步行为”。

---

## 5. 发展脉络：从外部存储到可学习的状态控制

### 5.1 2023-2024：奠定范式

早期基础工作定义了四种后来不断被复用的范式：

- **Generative Agents**：observation-memory-reflection-planning 闭环；
- **Reflexion**：把失败反馈转成跨尝试的语言反思；
- **Voyager**：将成功程序存成可组合的技能库，即程序性记忆；
- **MemGPT**：借鉴操作系统虚拟内存，让 Agent 管理上下文与外部存储的换入换出；
- **LoCoMo**：把长期对话扩展到多 session、事件关系和多跳问答；
- **HippoRAG**：用知识图和关联检索支持跨片段整合。

这一阶段证明了“外部记忆能够帮助 Agent”，但写入质量、状态版本、合法使用和错误修复尚未成为主要评价对象。

### 5.2 2025：组织、层次、经验复用和系统评测

2025 年正式会议论文出现四条清晰路线。

**第一，记忆组织从平坦池走向结构化关联。** A-MEM 用 Zettelkasten 式 note、标签和动态链接构造可演化网络；THEANINE 使用时间线和因果/时间关联组织长期对话；CDMem 使用 context-dependent graph index；图结构开始承担多跳整合，而不再只是检索加速。

**第二，经验记忆从复述轨迹走向可复用策略。** Agent Workflow Memory 把成功轨迹抽象为 workflow；R2D2 重构 web map 并结合反思；Contextual Experience Replay 从环境交互中维护动态经验 buffer；RMM 同时使用 prospective 与 retrospective reflection；CFGM 把经验组织成 coarse-to-fine actionable tips。

**第三，工作记忆和层次管理成为独立对象。** HiAgent 把长程任务拆成 subgoals，并压缩已经完成的局部轨迹；MemoryOS 将 STM、MTM、LTM 组织成多层系统，分别承担即时上下文、可复用摘要和长期个人知识。

**第四，Benchmark 从单一召回走向多维诊断。** LongMemEval 覆盖抽取、多 session 推理、时间、更新和拒答，并分析 indexing/retrieval/reading；MemBench 区分 factual/reflective 与 participation/observation，同时报告容量和效率；PersonaMem 关注动态用户画像；MEXTRA 则揭示长期记忆的隐私提取风险。

### 5.3 2026：策略化、RL 化、行动化和可信化

2026 年的变化不是“更多 memory 架构”，而是四个研究重心的迁移。

1. **被动后端 -> Agent 主动操作。** Memory-R1、AgeMem、MemSearcher、MemAct、Sculptor 和 StateLM 都把 memory/context operation 暴露为 Agent 动作；
2. **固定启发式 -> 学习 memory policy。** DPO、PPO、GRPO、DAPO、GSPO 和混合 on/off-policy RL 被用于写入、删除、摘要、检索、重构和上下文编辑；
3. **事实回答 -> memory-to-action。** Mem2ActBench、PersonaAgent、MemoPilot 等研究记忆如何改变工具选择、参数填充和序列决策；
4. **单次收益 -> 长期风险。** Memora 处罚 stale memory，AMemGym 研究 on-policy 误差累积，Topology Matters 与 MEXTRA 研究泄露，前沿工作进一步关注 authority、conflict、safe commitment 和 repair。

---

## 6. 方法演进趋势

### 6.1 趋势一：平坦存储变成多尺度结构

2025 年前常见管线是 `history -> chunks -> embedding -> Top-k`。它简单、强且透明，但忽略事件边界、时间关系和版本冲突。后续系统形成四类结构：

- **层次结构**：MemoryOS、HiAgent、LightMem、HiGMem、TiMem；
- **图结构**：A-MEM、THEANINE、MAGMA、HeLa-Mem、MRAgent；
- **事件与版本结构**：StructMem、AnchorMem、APEX-MEM、REMem；
- **固定大小状态**：MEM1、MemAgent、MemSearcher，用重写或覆写把上下文控制在近似常数。

这几类结构并非简单替代关系。图与事件结构提高可解释、多跳和来源追踪能力；固定状态降低 token 开销，却面临不可逆压缩。更可能的终局是混合架构：保留 immutable raw evidence，同时维护可重建的索引、摘要和策略层。

### 6.2 趋势二：从事实记忆走向经验和程序性记忆

事实记忆回答“用户住在哪里”；经验记忆回答“这种失败通常由什么导致”；程序性记忆回答“下一次应该按什么步骤做”。Agent Workflow Memory、R2D2、RMM、ReasoningBank、AdaMEM、Mem^p、MCMA 等将轨迹压缩成 workflow、reflection、strategy 或 skill。

关键难点不是能否生成一段反思，而是：

- 反思是否由真实证据支持；
- 策略是否只适用于原任务，还是可以迁移；
- 失败经验是否会错误抑制必要探索；
- 多条经验冲突时怎样选择；
- 经验更新后是否污染其他任务。

因此 experiential memory 的核心评测应从“有无提升”转向**归因正确性、适用范围和迁移边界**。

### 6.3 趋势三：检索从语义相似度走向意图和重构

语义相似只回答“文本像不像”，不回答“事件是否处于同一情境、当前目标是否允许使用、信息是否仍有效”。STITCH/CAME-Bench 用 contextual intent 构造 hard negatives；Memory-T1 先定位时间候选再筛证据；MRAgent 不直接取回静态摘要，而是依据 cue 主动重构相关经历；REMem 通过时间和图工具组合访问 episodic memory。

未来检索器需要同时考虑：

\[
s(m,q)=\alpha s_{semantic}+\beta s_{intent}+\gamma s_{temporal}+\delta s_{authority}+\eta s_{scope}-\lambda s_{conflict}.
\]

真正困难的是各项分数不是静态权重：任务风险、行动代价和可用工具会改变最优权衡。

### 6.4 趋势四：Memory operation 变成可学习动作

代表方法的动作空间如下：

| 方法 | 主要动作 | 学习方式 | 关键价值 | 主要风险 |
|---|---|---|---|---|
| Memory-R1 | ADD/UPDATE/DELETE/NOOP + 记忆预选 | PPO/GRPO | 显式学习管理与使用 | 最终答案奖励可能掩盖错误操作 |
| AgeMem | store/retrieve/update/summarize/discard | 三阶段 RL、stepwise GRPO | 统一 STM/LTM 管理 | 动作多、长程信用分配困难 |
| MemSearcher | 搜索、推理、覆写紧凑 memory | multi-context GRPO | 固定 token 预算下联合优化 | 破坏性重写、证据不可恢复 |
| MCMA | 选择经验抽象粒度和复用方式 | DPO | 学习可迁移的抽象策略 | 偏好数据质量决定上限 |
| MemAgent | 分段读取、更新内部状态 | DAPO | 超长输入的端到端状态压缩 | 潜在状态缺少可审计性 |
| Sculptor/MemAct | summarize/hide/restore 或 delete/insert | GSPO/动态上下文策略优化 | 将 context curation 纳入 policy | 与持久记忆边界易混淆 |
| MemoPilot | memory copilot 跨 turn 辅助冻结 player | multi-turn GRPO | 直接优化序列行动收益 | 环境奖励稀疏、泛化依赖任务 |
| BudgetMem | 为各 memory 模块分配预算档位 | cost-aware PPO | 学习性能-成本权衡 | reward 权重可能主导结论 |

结论是：**GRPO 不是 Agent Memory 的研究贡献本身**。真正可发表的问题在于 memory state、动作空间、可验证 reward、长期 credit assignment，以及训练后能否在未见过的状态变化上泛化。

### 6.5 趋势五：在线与离线记忆处理分离

LightMem 将高频检索、选择和写入交给小模型，把较重的 consolidation 放到离线阶段；Agentic Plan Caching 把可复用计划放入缓存；AdaMEM 在长期成功轨迹之上为当前决策动态合成短期策略。这反映出一个工程共识：

- 在线路径需要低延迟、固定预算和稳定行为；
- 离线路径适合做聚类、反思、链接、版本整理和经验抽象；
- 两者之间必须保留 provenance 和可回滚映射，否则离线压缩错误会永久进入系统。

### 6.6 趋势六：从效果最大化走向成本与风险约束

复杂图记忆和多次 LLM 调用可以提高准确率，却可能以数量级更高的 token、延迟和存储换取小幅收益。MemBench、LightMem、RecMem、BudgetMem 等推动报告：

- construction token；
- retrieval token；
- LLM calls；
- latency；
- storage growth；
- quality-cost Pareto frontier。

与此同时，MEXTRA、Topology Matters 等说明 memory 是新的攻击面：跨用户混写、检索暴露、间接提示注入、错误合并和多 Agent 传播都会把一次局部错误变成长期风险。

---

## 7. 评测发展趋势

### 7.1 第一代：长历史中的事实召回

代表：LoCoMo、LongMemEval。

输入是一段很长或跨 session 的历史，输出是答案、总结或拒答。它们建立了长期记忆的共同底座，但最终准确率无法区分 formation、retrieval、reader 和 use 的失败。

### 7.2 第二代：动态状态与选择性遗忘

代表：PersonaMem、Memora、MemoryAgentBench。

评测开始引入偏好变化、知识更新、TTL/LRU 和 supersession。核心观念从“记住越多越好”变成“保持当前有效状态，并抑制已经失效的信息”。

### 7.3 第三代：战略使用与行动

代表：StratMem-Bench、Mem2ActBench。

- StratMem-Bench 将候选记忆标为 `must / nice / irrelevant`，评价模型是否适度使用；
- Mem2ActBench 将长期历史转成工具选择与参数填充任务，要求记忆支持可执行动作。

这一阶段证明，检索成功仍不等于 action grounding 成功。但候选往往已给定，或工具调用主要是离线评分，尚未形成完整的检索、验证、执行、修复闭环。

### 7.4 第四代：交互与过程诊断

代表：AMemGym、MemoryAgentBench，以及同期前沿的 MemTrace、EvoMemBench、MemFail、MemGauge。

AMemGym 将固定历史改成 on-policy 交互，Agent 的回复会改变未来用户行为和记忆；MemoryAgentBench 用增量 chunk 比较 long context、RAG 和 agentic memory；MemTrace 等预印本进一步尝试 operation-level failure attribution。

因此，“首次做过程级评测”已不再成立。新的 benchmark 必须给出此前没有受控的变量、可执行结果或纵向后果。

### 7.5 第五代：可信状态、权限和长期修复

2026 年前沿评测开始关注：

- stale、conflicting、incomplete、over-compressed memory；
- source authority、scope、permission 和 provenance；
- memory uncertainty 下的 verify/ask/abstain/safe commit；
- 修复后的 future utility 与 unrelated-task contamination。

这类工作尚未完全收敛到统一协议，但它指向最明确的下一步：**把 persistent memory state 作为受控因果变量，而不是只比较不同 memory backend 的最终分数。**

### 7.6 Benchmark 横向比较

| Benchmark | 出处 | 主要输入 | 主要输出 | 已覆盖 | 主要边界 |
|---|---|---|---|---|---|
| LoCoMo | ACL 2024 Long | 多 session 长对话 | QA/总结/对话 | 多跳、时间、长程召回 | 偏最终生成 |
| LongMemEval | ICLR 2025 | 长期聊天历史 | 答案/拒答 | 抽取、多 session、更新、时间 | 无完整行动闭环 |
| PersonaMem | COLM 2025 | 动态用户历史 | 个性化响应 | 用户画像、偏好变化 | 偏 personalization |
| MemBench | ACL 2025 Findings | 亲历/旁观经历 | factual/reflective answer | 效果、效率、容量 | 动态冲突有限 |
| MemoryAgentBench | ICLR 2026 | 增量输入块 | 答案/记忆表现 | 检索、学习、理解、遗忘 | chunk 不等于真实事件 |
| AMemGym | ICLR 2026 | on-policy 长期对话 | 个性化任务结果 | write/read/use 诊断 | 模拟用户与领域受限 |
| StratMem-Bench | ACL 2026 Long | query/persona/candidate memories | 角色回复 | required/supportive/irrelevant | 候选已给定，单轮使用 |
| Memora | ACL 2026 Findings | 高频变化用户状态 | 回忆/推理/推荐 | update、forgetting、stale | 主要为合成轨迹 |
| Mem2ActBench | ACL 2026 Long | 长历史与工具任务 | tool call | 工具选择、参数 grounding | 主动验证和修复有限 |
| CAME-Bench | ACL 2026 Findings | 情境相似 hard negatives | 检索/回答 | contextual intent | 非完整 lifecycle |
| MIKASA | ICLR 2026 | 部分可观测 RL/机器人任务 | 环境行动 | 通用 memory-intensive RL | 不专属于 LLM Agent Memory |

### 7.7 指标从 aggregate accuracy 走向哪几类

未来的评价指标至少应覆盖六层：

1. **内容层**：事实覆盖、时间一致性、来源保留、压缩 fidelity；
2. **检索层**：Recall@k、MRR、hard-negative discrimination、evidence precision；
3. **控制层**：USE/SEARCH/VERIFY/ASK/IGNORE/ABSTAIN 的策略正确率；
4. **行动层**：tool selection、parameter exact match、environment postcondition；
5. **演化层**：update/invalidate/merge 的正确率、stale suppression；
6. **纵向层**：future-task gain、错误复发率、无关任务污染、累计成本。

最终 accuracy 仍然需要保留，但它应该是系统结果，不再是唯一解释。

---

## 8. 重点论文精读

### 8.1 LongMemEval（ICLR 2025）

**问题。** 长期聊天助手究竟在哪一类记忆能力上失败。

**方案。** 以 500 个高质量问题覆盖信息抽取、多 session 推理、时间推理、知识更新和 abstention，并把系统拆为 indexing、retrieval、reading。

**价值。** 它将“上下文够不够长”转成系统级诊断问题，是后续 memory benchmark 的基础。

**局限。** 输出仍以答案为主，缺少工具副作用、权限和修复后的未来价值。

### 8.2 A-MEM（NeurIPS 2025 Main）

**问题。** 固定结构和固定操作限制 memory 对不同任务的适应能力。

**方案。** 新事件被写成带 contextual description、keywords、tags 的 note；系统检索相近历史，建立链接，并可更新旧 note 的描述和属性。

**价值。** 从向量池迈向 agentic organization 和 memory evolution。

**局限。** 多次 LLM 调用昂贵且非确定；错链或错误重写可能累计；原始证据与更新结果之间的可追溯性不足。

### 8.3 Agent Workflow Memory（ICML 2025）

**问题。** Web Agent 如何把复杂成功轨迹转成可复用经验，而不必反复探索。

**方案。** 从训练或测试轨迹中归纳 workflow memory，在新任务中检索并实例化工作流。

**价值。** 把 memory 从事实回忆推进到 procedural reuse，并同时减少执行步骤。

**局限。** workflow 的错误适用会造成 false reuse；环境变化后旧流程可能失效。

### 8.4 R2D2（ACL 2025 Long）

**问题。** Web Agent 如何从过去尝试中形成可检索的环境地图并利用反思改进。

**方案。** replay buffer 重构 web map，反思模块总结跨尝试经验，后续任务依据环境结构和历史反馈行动。

**价值。** 连接环境模型、episodic replay 和 reflection。

**局限。** 动态网页会使地图和经验变旧；成功结果无法证明反思归因本身正确。

### 8.5 HiAgent（ACL 2025 Long）

**问题。** 单次长程任务内，完整 action-observation 历史会造成上下文冗余。

**方案。** 以 subgoal 为单位压缩已经完成的轨迹，只保留当前推理所需的 working memory。

**价值。** 明确区分 cross-trial memory 与 in-trial working memory。

**局限。** 主要解决当前 episode 的上下文管理，不等同于跨 session 的持久记忆生命周期。

### 8.6 MemoryOS（EMNLP 2025 Main）

**问题。** 长期个性化助手如何同时管理即时上下文、局部摘要和长期用户知识。

**方案。** STM、MTM、LTM 三层存储，配套 storage、updating、retrieval、generation 模块。

**价值。** 给出工程完整的分层 memory operating system。

**局限。** 层次复杂不自动保证写入正确、来源可信或更新无污染。

### 8.7 Memory-R1（ACL 2026 Long）

**问题。** Memory manager 能否通过 RL 学会 ADD、UPDATE、DELETE 和 NOOP，而不依赖固定规则。

**方案。** Memory Manager 管理外部记忆，Answer Agent 预选并推理；二者分别以 PPO/GRPO 使用 outcome reward 优化。

**价值。** 以少量训练问题展示 learned memory operation 的可行性，是训练型 memory agent 的关键基线。

**局限。** 最终答案奖励可能让错误操作被偶然正确答案掩盖；训练集小并不等价于 reward 已得到充分验证。

### 8.8 AgeMem（ACL 2026 Long）

**问题。** LTM 与 STM 被分立管理，难以端到端适应长程任务。

**方案。** 把 store、retrieve、update、summarize、discard 等操作变成工具动作，并用三阶段 progressive RL 与 stepwise GRPO 学习统一策略。

**价值。** 从“有一个 memory controller”推进到 memory operations 与 Agent policy 的统一优化。

**局限。** 动作空间扩大后 reward design 和长程 credit assignment 更难；错误记忆操作可能跨步累积。

### 8.9 LightMem（ACL 2026 Long）

**问题。** 向量检索便宜但不稳定，多次大模型操作准确但延迟高。

**方案。** 以多个 SLM 分别承担 query planning、candidate verification 和 writing，离线大上下文模型完成 consolidation；组织为 STM/MTM/LTM。

**价值。** 将在线低时延和离线高质量整理解耦，明确面向资源约束的 memory design。

**局限。** 模块越多，错误边界越复杂；离线 consolidation 的错误可能长期固化。

### 8.10 MEM1 与 MemAgent（ICLR 2026）

**问题。** 超长输入和长程 reasoning 如何避免上下文随步数线性增长。

**方案。** 两者都让模型分段处理输入并持续改写紧凑状态；MemAgent 使用 DAPO，MEM1 通过 RL 和 rollout truncation 学习共享内部记忆。

**价值。** 展示 latent/compact state 可以用近似常数 token 支撑超长任务。

**局限。** 破坏性压缩使原始证据、来源和限定条件难以恢复，不能只用最终 QA 判断状态是否忠实。

### 8.11 AMemGym（ICLR 2026）

**问题。** 固定历史的 off-policy benchmark 会不会掩盖 Agent 自己造成的长期错误。

**方案。** 预定义结构化用户状态和演化轨迹，由模拟用户根据 Agent 回复继续交互，评价 write、read 和 utilization。

**价值。** 将 memory benchmark 变成交互环境，证明系统在 off-policy 与 on-policy 下的排名可能不同。

**局限。** 用户模拟和状态空间相对规整；诊断仍是阶段级；主要集中在长期对话和个性化。

### 8.12 MemoryAgentBench（ICLR 2026）

**问题。** 如何在统一增量接口下比较 long-context、RAG 与 agentic memory。

**方案。** 输入逐 chunk 到达，测试 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting。

**价值。** 统一了不同后端的 ingestion 接口，并把形成和遗忘放入评测。

**局限。** chunk 未必对应真实事件；缺少 authority、scope、repair 等面向行动的原子标签。

### 8.13 StratMem-Bench（ACL 2026 Long）

**问题。** 候选记忆中哪些必须用、哪些可改善表达、哪些应忽略。

**方案。** 657 个虚拟角色对话实例，包含 query、persona 与 `must/nice/irrelevant` memory pool；使用 SMC、MIQ、PES、CIR 等指标评价战略使用。

**价值。** 证明“适度使用 supportive memory”比简单事实命中更难，把 memory use 从 retrieval 中分离。

**局限。** 候选记忆已给定，不评写入、检索、动态更新或跨 session 修复；主要是单轮角色回复。

### 8.14 Mem2ActBench（ACL 2026 Long）

**问题。** Agent 能否从长期历史恢复正确工具与参数，而不是只回答问题。

**方案。** 2,029 个长交互 session、400 个工具任务，评价 tool selection 与 parameter grounding；人工确认绝大多数任务强依赖历史记忆。

**价值。** 把长期记忆明确连接到可执行行动。

**局限。** tool call 多为离线评分；主动 search/verify/ask、环境副作用和行动后 repair 不是主任务。

### 8.15 Memora（ACL 2026 Findings）

**问题。** 用户偏好和目标频繁变化时，Agent 能否记住新状态并停止使用旧状态。

**方案。** 构造高 mutation 的个性化轨迹，覆盖 remembering、reasoning、recommending；FAMA 同时奖励有效记忆和正确遗忘。

**价值。** 明确证明更多记忆不一定更好，stale memory 必须被处罚。

**局限。** 轨迹以合成为主，主要评价状态和响应；对权限、行动风险和修复副作用覆盖不足。

### 8.16 STITCH / CAME-Bench（ACL 2026 Findings）

**问题。** 同一人物、同一主题但不同情境的经历为什么会被 embedding 检索混淆。

**方案。** 为记忆构造 thematic scope、event type、entity type 等 contextual-intent 表示，并专门构造 context-confusable hard negatives。

**价值。** 将随机噪声升级为意图相似但实际不适用的困难负例。

**局限。** 写入阶段依赖强模型和预设标签；不覆盖完整 memory lifecycle。

### 8.17 MAGMA 与 MRAgent（ACL 2026 / ICML 2026）

**问题。** 单一相似度与静态摘要难以复原跨事件、跨时间的复杂经历。

**方案。** MAGMA 同时维护 semantic、temporal、causal、entity 等正交图；MRAgent 使用 Cue-Tag-Content 图并主动进行 memory reconstruction。

**价值。** 图不再只承担索引，而成为按当前 query 重组经历的计算结构。

**局限。** 抽取和图访问成本高；错误边会扩散；性能提升需要与更强的非图 reranker 在同预算下比较。

### 8.18 AdaMEM 与 ReasoningBank（ICML 2026 / ICLR 2026）

**问题。** 一条过去轨迹不一定直接适合当前状态，经验应如何动态抽象。

**方案。** AdaMEM 从长期成功轨迹中为当前决策合成短期策略；ReasoningBank 把成功和失败经验转成可复用 reasoning memory。

**价值。** 从“retrieve one episode”转向“cross-trajectory abstraction”。

**局限。** 经验标签和反思可能偏置；只积累成功经验会忽略恢复策略，纳入失败经验又会放大错误归因风险。

### 8.19 MemoPilot 与 BudgetMem（ICML 2026）

**问题。** Memory policy 是否可以独立于主 Agent 学习，以及如何显式控制成本。

**方案。** MemoPilot 使用冻结 player 与可训练 memory copilot，通过 multi-turn GRPO 优化长期行动；BudgetMem 为不同 memory 模块选择 Low/Mid/High 预算，并用 cost-aware RL 学习路由。

**价值。** 分别展示“可插拔 memory policy”和“质量-成本联合优化”。

**局限。** reward 权重和环境分布会强烈影响 learned policy；需要报告跨任务、跨模型和不同成本权重的稳健性。

### 8.20 MEXTRA 与 Topology Matters（ACL 2025/2026）

**问题。** 长期记忆会不会成为跨用户、跨 Agent 的隐私泄露通道。

**方案。** MEXTRA 从黑盒角度测试私有 memory extraction；Topology Matters 比较多 Agent 拓扑下的 memory leakage，并提出相应防护协议。

**价值。** 证明 memory 的读取、传播和共享边界本身就是安全问题。

**局限。** 当前治理研究仍碎片化，尚未统一覆盖 source、authority、scope、consent、retention 和 deletion guarantee。

---

## 9. 2025-2026 正式会议论文地图

### 9.1 2025 核心论文

| 论文 | 出处 | 类型 | 核心贡献 |
|---|---|---|---|
| LongMemEval | ICLR 2025 | Benchmark | 五类长期交互记忆能力与 indexing/retrieval/reading 分析 |
| A-MEM | NeurIPS 2025 Main | Method | Zettelkasten 式 agentic note network 与 memory evolution |
| Agentic Plan Caching | NeurIPS 2025 Main | Method | 缓存、检索和适配可复用计划 |
| Agent Workflow Memory | ICML 2025 | Method | 从轨迹归纳并复用 workflow |
| HiAgent | ACL 2025 Long | Method | subgoal-based hierarchical working memory |
| R2D2 | ACL 2025 Long | Method | replay graph、web map 与 reflection |
| In Prospect and Retrospect / RMM | ACL 2025 Long | Method | prospective/retrospective reflective memory |
| Contextual Experience Replay | ACL 2025 Long | Method | training-free 动态经验 buffer |
| MemBench | ACL 2025 Findings | Benchmark | factual/reflective、participation/observation、效率与容量 |
| MEXTRA | ACL 2025 Long | Safety | LLM Agent memory 的黑盒隐私提取 |
| TReMu | ACL 2025 Findings | Method | timeline 与神经符号时间推理 |
| M2PA | ACL 2025 Findings | Method | semantic/episodic/sensory/working 多记忆规划 |
| Dynamic Steering with Episodic Memory | ACL 2025 Findings | Method | 以 episodic memory 动态引导模型行为 |
| Graph-Structured Long-term Memory for Personal Assistant | ACL 2025 Findings | Method | 联想图与深思式 recall |
| THEANINE | NAACL 2025 Long | Method | timeline-based lifelong dialogue memory |
| CDMem | NAACL 2025 Industry | Method | context-dependent graph index 与在线更新 |
| MemoryOS | EMNLP 2025 Main | System | STM/MTM/LTM 分层操作系统 |
| Coarse-to-Fine Grounded Memory | EMNLP 2025 Main | Method | focus points、hybrid tips、异常反思与计划修正 |
| PersonaMem | COLM 2025 | Benchmark | 动态用户画像与规模化个性化响应 |

### 9.2 2026 ACL 系列核心论文

| 论文 | 出处 | 类型 | 核心贡献 |
|---|---|---|---|
| Agentic Memory / AgeMem | ACL 2026 Long | RL Method | 统一 STM/LTM 操作，三阶段 RL 与 stepwise GRPO |
| Memory-R1 | ACL 2026 Long | RL Method | Memory Manager + Answer Agent，PPO/GRPO |
| LightMem | ACL 2026 Long | System | SLM 驱动、在线/离线解耦的分层记忆 |
| MAGMA | ACL 2026 Long | Method | semantic/temporal/causal/entity 多图记忆 |
| APEX-MEM | ACL 2026 Long | Method | append-only 半结构属性图与 query-time resolution |
| Fine-Mem | ACL 2026 Long | RL Method | 长程 memory manager 的细粒度反馈对齐 |
| HyperMem | ACL 2026 | Method | topic-episode-fact 超图记忆 |
| StratMem-Bench | ACL 2026 Long | Benchmark | must/nice/irrelevant 的战略使用 |
| Mem2ActBench | ACL 2026 Long | Benchmark | 长期记忆到工具选择与参数填充 |
| How Memory Management Impacts LLM Agents | ACL 2026 Long | Analysis | 系统分析 memory management 对 Agent 的影响 |
| MemSearcher | ACL 2026 Findings | RL Method | reason/search/manage memory 的端到端 RL |
| Grounding Agent Memory in Contextual Intent | ACL 2026 Findings | Retrieval/Benchmark | STITCH 与 CAME-Bench hard negatives |
| From Recall to Forgetting / Memora | ACL 2026 Findings | Benchmark | 动态状态、stale memory 与遗忘评价 |
| AnchorMem | ACL 2026 Findings | Method | atomic anchors 与 immutable associative context |
| CLAG | ACL 2026 Findings | Method | 小模型驱动的动态 memory clustering |
| HeLa-Mem | ACL 2026 | Method | Hebbian association 与双路径检索 |
| StructMem | ACL 2026 | Method | 事件级绑定与跨事件结构整合 |
| TiMem | ACL 2026 Findings | Method | 五层 Temporal Memory Tree |
| HiGMem | ACL 2026 Findings | Method | event-summary 到 raw-turn 的两层读取 |
| RecMem | ACL 2026 Findings | Method | recurrence-triggered consolidation |
| Mem^p | ACL 2026 Findings | Method | 可构建、检索、更新的程序性记忆 |
| EMA | ACL 2026 Findings | Method | episodic units 与 MemDecider 选择性过滤 |
| Memory as Action / MemAct | ACL 2026 Findings | RL Method | 以 delete/insert 学习 working-memory curation |
| MemoBrain | ACL 2026 Findings | Method | dependency-aware executive memory copilot |
| Learning How to Remember / MCMA | ACL 2026 Findings | Preference Learning | DPO 学习记忆抽象与迁移粒度 |
| BMAM | ACL 2026 Findings | System | 多子系统、多时间尺度的认知启发式架构 |
| Topology Matters | ACL 2026 Findings | Safety | 多 Agent 拓扑中的 memory leakage |
| From Storage to Experience | ACL 2026 Findings | Survey | Storage-Reflection-Experience 演化框架 |

### 9.3 2026 ICLR 核心论文

| 论文 | 类型 | 核心贡献 |
|---|---|---|
| AMemGym | Benchmark | on-policy 长期对话、结构化用户状态、write/read/use 诊断 |
| MemoryAgentBench | Benchmark | 增量交互下的检索、测试时学习、长程理解和遗忘 |
| MEM1 | RL Method | 近常数上下文的共享紧凑记忆状态 |
| Memory-T1 | RL Method | coarse-to-fine 时间候选与 evidence-grounded reward |
| REMem | Method | 带时间 gist 和 fact triple 的 episodic graph |
| Sculptor | RL Method | summarize/hide/restore/search 的主动上下文管理 |
| StateLM / Pensieve | Method | pruning/indexing/note-taking 工具与 stateful Agent |
| MemAgent | RL Method | 分段处理、覆写 memory、DAPO |
| MemGen | Method | latent generative memory 与 self-evolution |
| ReasoningBank | Method | 由成败轨迹形成 reasoning memory |
| Dual-Scale World Memory / GLoW | Method | global trajectory frontier + local trial/error memory |
| Exploratory Memory-Augmented Agent / EMPO2 | RL Method | memory 与 hybrid on/off-policy exploration |
| ReMemR1 | RL Method | revisitable memory 与多层 reward |
| MemGAS | Method | 多粒度 memory unit、关联与 entropy router |
| Memento | Multimodal/Benchmark | 超长流视频主动助手与 MementoBench |

### 9.4 2026 ICML 核心论文

| 论文 | 类型 | 核心贡献 |
|---|---|---|
| AdaMEM | Method | 长期轨迹库 + test-time 动态短期策略合成 |
| Memory is Reconstructed, Not Retrieved / MRAgent | Method | Cue-Tag-Content 图与主动经历重构 |
| MemoPilot | RL Method | 冻结 player + 可训练 memory copilot，multi-turn GRPO |
| BudgetMem | RL/System | query-aware budget-tier routing 与 cost-aware PPO |
| E-mem | Multi-Agent Method | 多 Agent 协作重构 episodic context |
| RGMem | Method | 受重整化群启发的 memory evolution |

---

## 10. 方法趋势的定量化解读

以下不是对“所有带 memory 关键词论文”的统计，而是对上节核心语料的人工编码，因此用于观察趋势，不应被当作严格 bibliometrics。

### 10.1 2025 到 2026 的变化

- 2025 年核心工作仍以外部结构、经验复用和长程 QA 为主；
- 2026 年显著增加 RL-based memory policy、working-context action、程序性记忆和 benchmark；
- 图结构继续增长，但研究重点由“图能否检索”转向“图能否支持时间、因果、事件和重构”；
- benchmark 由静态结果测量转向增量、on-policy、memory-to-action 和 forgetting；
- 可信研究仍少于效率和准确性研究，是未来增长最快的部分之一。

### 10.2 为什么最近大量工作使用 GRPO

GRPO 在 Agent Memory 中流行有三点原因：

1. memory operation 可以表示为可生成的离散动作序列，天然适合 policy optimization；
2. 同一问题可采样多条管理轨迹，通过组内相对优势减少独立 value model 的开销；
3. VERL 等训练框架降低了实现成本，研究者可以快速把 answer reward 或 step reward 接入。

但 GRPO 也有明显限制：

- 若组内样本都错或都对，优势估计信息弱；
- 最终答案 reward 对早期写入、压缩和检索动作的信用分配稀疏；
- 错误 memory 写回会影响未来 episode，单轨迹 reward 无法覆盖跨 session 后果；
- reward model 若只判断语言合理性，可能鼓励不可验证的漂亮摘要。

因此 GSPO、DAPO、DPO、offline preference learning 和 model-based verifier 并非不能使用，而是应该由任务结构决定。若训练对象是**同一步的多个候选 memory/action 排序**，pairwise/listwise preference learning 可能比直接做长程 GRPO 更稳定；若需要在线探索和延迟回报，再考虑 RL。

---

## 11. 当前领域的共同难题

### 11.1 Relevant 不等于 admissible，更不等于 sufficient

应将三件事严格分开：

\[
\text{Retrieved}(m) \neq \text{AdmissibleToUse}(m) \neq \text{SufficientToAct}(M,q).
\]

一条旧地址与当前 query 高度相关，但已经过期；一条管理员策略准确且最新，但当前用户无权使用；两条互相冲突的记忆都被成功检索，但不足以支持不可逆操作。只测 retrieval recall 会把这些情况误判为成功。

### 11.2 Compression 与 fidelity 的矛盾

固定大小 memory 可以控制 token，却可能丢失：

- 事实的时间边界；
- 来源和引用；
- 条件与例外；
- 授权范围；
- 旧版本与新版本关系；
- 反思来自成功还是失败轨迹。

未来系统应让摘要可回溯到原始证据，并在高风险任务中支持 restore/raw lookup，而不是把压缩文本当成唯一真相。

### 11.3 Update 不是字符串替换

真实更新至少包括：

- `UPDATE`：旧值被新值替代；
- `INVALIDATE`：事实或权限失效，但历史仍需保留；
- `MERGE`：多条证据合成更完整状态；
- `RESTORE_PROVENANCE`：恢复摘要中丢失的来源和限定；
- `PRESERVE_CONFLICT`：目前无法裁决时，显式保留不确定性；
- `DELETE/REDACT`：满足隐私或保留期限要求。

这些操作对未来任务的影响不同，不能统一记为“更新成功”。

### 11.4 结果指标无法承担因果诊断

一个正确答案可能来自参数常识、猜测、工具直接给出答案或错误证据偶然抵消。一个错误答案也可能来自写入、组织、检索、读取、控制、执行或修复。可靠诊断需要：

1. matched counterfactual memory families；
2. oracle memory、retrieval、diagnosis、control、execution、repair；
3. deterministic tool state 和 environment postcondition；
4. future-session evaluation。

### 11.5 On-policy 误差会形成反馈环

静态数据中一次错误只影响一个样本；真实 Agent 中，错误回复会改变用户行为，错误行动会改变环境，错误写入会影响未来检索。于是

\[
M_t \rightarrow a_t \rightarrow H_{t+1} \rightarrow M_{t+1}
\]

形成闭环。AMemGym 已证明 off-policy 与 on-policy 的系统排名可能不同。未来 benchmark 必须说明交互轨迹是否由被测 Agent 共同生成。

### 11.6 可信性不是附加模块

memory 一旦持久化，就具有比单次 hallucination 更长的影响范围。需要把以下元数据当作一等公民：

- provenance；
- timestamp 与有效期；
- authority；
- user/agent scope；
- confidence 与 conflict status；
- retention/deletion policy；
- repair history。

---

## 12. 评测趋势与未来预计

### 12.1 方法侧未来 2-3 年

**趋势 A：Memory-native Agent。** memory 不再是外围数据库，而成为 Agent action space 的一部分；规划器同时决定 task action 与 memory action。

**趋势 B：显式与隐式状态混合。** latent memory 用于低成本压缩，显式 event/provenance store 用于验证、恢复和治理。

**趋势 C：跨轨迹经验抽象。** 从检索单条成功案例，转向从成功与失败集合中形成可迁移策略，并显式建模适用范围。

**趋势 D：多时间尺度学习。** step 内 working memory、episode 间经验和跨月用户状态将由不同频率的更新器共同维护。

**趋势 E：资源感知 memory policy。** token、延迟、调用次数、能耗和隐私风险进入 reward 或约束，系统报告 Pareto frontier。

**趋势 F：多模态与具身记忆。** 记忆单元从文本扩展到视频片段、空间地图、GUI 状态和传感器事件，重点从存储转向跨模态 consolidation 和 action grounding。

### 12.2 Benchmark 侧未来 2-3 年

**趋势 A：从静态历史到可执行环境。** 任务不只输出答案，还要验证工具状态、环境后置条件和行动副作用。

**趋势 B：从单样本到 matched family。** 固定 query、world 和 goal，仅改变 memory 的 fresh/stale/conflict/missing/authority 状态，以测因果行为变化。

**趋势 C：从一次性得分到纵向净收益。** repair 后在相关 follow-up 上应改善，在无关任务上不应污染，并报告成本。

**趋势 D：从 pipeline accuracy 到 failure attribution。** 使用 oracle ladder、operation trace 与 earliest decisive error 定位瓶颈。

**趋势 E：从平均分到风险分层。** 对不可逆工具调用、高敏感用户数据和高成本行动设置更严格的 evidence closure。

### 12.3 预计会出现的统一评价单位

未来很可能不再以“一个 question”作为最小单位，而以一个 memory episode family 为单位：

\[
\mathcal{F}_i=(H_i,M_i^{1:K},q_i,W_i,A_i,E_i,M'_i,Q_i^{future}).
\]

其中 `H` 是形成历史，`M^{1:K}` 是受控记忆状态家族，`q` 是固定任务，`W` 是真实世界状态，`A` 是允许动作集合，`E` 是新证据，`M'` 是修复结果，`Q_future` 是相关与无关后续任务。这个单位能同时测 diagnosis、control、commit、repair 和 future utility。

---

## 13. 仍可防守的 Research Gap

以下表述已经不足以作为新颖性：

- “现有 benchmark 只测 factual recall”；
- “没有动态更新或 forgetting”；
- “没有 strategic memory use”；
- “没有 memory-to-action”；
- “没有 write/read/use 分解”；
- “没有通过 RL 学习 memory operations”；
- “没有 operation-level failure tracing”。

更窄、也更可防守的 gap 是：

> **近期工作已经分别研究长期召回、动态更新、战略使用、工具行动、on-policy 交互、操作级诊断和安全风险；但仍缺少统一、受控的纵向评测：在保持 query、world、user goal、requirements 和可用工具不变时，仅改变由历史交互形成的 persistent memory 的覆盖度、时效性、冲突、压缩和授权状态，观察 Agent 是否相应改变记忆信任与行动策略；再提供权威新证据，评价它能否修复 memory，使未来相关任务改善且不污染无关任务。**

这个 gap 不是把几个既有任务拼在一起，而是把 `persistent memory state` 设为受控因果变量，把 `use-control-repair-future utility` 设为一个完整实验单元。

---

## 14. 可选研究切入点

### 14.1 方向 A：Memory-State Intervention Benchmark

**问题。** 同一任务仅改变 persistent memory 的状态时，Agent 是否做出正确的策略变化。

**最小设计。** 每个 base task 构造 `fresh-complete / missing / stale / conflicting / over-compressed / authority-drift / distractor` 变体；固定世界、目标和工具。

**贡献。** 从 backend 排名转向 memory state 的因果行为评价。

**风险。** 必须证明变体自然、任务确实依赖跨 session memory，且不是普通 RAG 的证据充分性题。

### 14.2 方向 B：Longitudinal Memory Repair

**问题。** Agent 在新证据到来后能否正确修复持久状态，并在未来任务中获得净收益。

**最小设计。** Session A 形成记忆，Session B 暴露错误并提供权威证据，Session C 同时包含相关与无关 follow-up。

**贡献。** 将 repair correctness、future benefit 和 collateral contamination 放在同一协议中。

**风险。** 数据构造和环境状态验证成本较高。

### 14.3 方向 C：Memory Trust Controller

**问题。** 在 memory 已被检索的前提下，何时 use、verify、ask、ignore、abstain 或 execute。

**最小设计。** 先用规则和 oracle 生成 action preference；做 prompting 与 SFT/DPO baseline；只有在序列决策确实需要探索时再做 GRPO/GSPO。

**贡献。** 把检索器之后的“可用性判断”作为独立控制问题。

**风险。** 单独做 action classifier 可能过薄，需要与真实工具结果和纵向 repair 结合。

### 14.4 方向 D：Source- and Authority-Aware Memory

**问题。** consolidation 和 retrieval 能否保留来源权威、授权范围和冲突状态。

**最小设计。** 对相同事实设置 user statement、tool observation、system policy、third-party report 等来源；改变 authority ordering 和 expiry。

**贡献。** 把 provenance 从可选 metadata 提升为 action admissibility 的决定因素。

**风险。** 前沿 AuthMem-Bench、TANGLE、SafeCommit 等预印本正在快速覆盖该空间，需要持续撞题审计。

### 14.5 方向 E：Budget-Aware Memory Evaluation

**问题。** 在固定 token、时延和工具预算下，不同 memory system 的真实收益是多少。

**最小设计。** 统一 reader、retrieval budget、上下文长度和调用次数，报告 accuracy-cost-risk Pareto frontier。

**贡献。** 避免复杂系统用数量级更高成本换取小幅准确率提升。

**风险。** 单纯做成本 benchmark 新颖性有限，最好与状态干预或 repair 结合。

---

## 15. 对当前研究决策的建议

在暂不锁定具体方法的前提下，最稳的路线是 `benchmark first, method second`：

1. 先用 50-100 个 base tasks 做 matched memory-state pilot；
2. 同时跑 no-memory、full-history、BM25、dense、hybrid、summary、structured event、A-MEM 类 baseline；
3. 加入 oracle memory、oracle retrieval、oracle diagnosis、oracle control、oracle repair；
4. 判断 dominant failure 是 formation、retrieval、adequacy、control、execution 还是 repair；
5. 再决定训练 reranker、setwise verifier、trust controller、writer/repairer 或 budget policy。

进入方法阶段的判据应是：

- 不同 memory state 能稳定触发不同的模型失败；
- episode accuracy 明显高估 family-level accuracy；
- oracle ladder 能把主要错误归因到一个或两个可训练模块；
- repair 在相关任务上产生收益且无关任务污染接近零；
- 轻量 baseline 不能通过简单 prompt 修复该失败。

在 4 张 RTX 4090 的资源条件下，首轮没有必要训练大规模 memory RL。更合理的顺序是：

`prompting -> supervised classifier/reranker -> DPO/OPD -> 小模型 RL pilot -> 必要时扩到 7B`。

---

## 16. 结论

Agent Memory 已经从“给 LLM 加一个外部知识库”发展为 Agent 的一等状态与决策问题。2025 年的主要进展是结构化组织、层次管理、经验复用和长期评测；2026 年则快速转向主动 memory operations、RL 学习、memory-to-action、on-policy 交互和可信治理。方法侧的共同方向是更主动、更结构化、更紧凑、更可学习；评测侧的共同方向是更动态、更交互、更接近真实行动，但对因果状态干预和纵向修复的覆盖仍不充分。

最重要的领域判断是：**未来竞争不再是谁能存更多或召回更多，而是谁能在有限预算和不完美记忆下，判断何时可信、何时需要获取新证据、何时可以行动，以及出错后能否修复持续状态。**

---

## 参考文献与官方入口

### 核心综述

1. Hu et al. [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564). arXiv, 2025/2026.
2. Du et al. [Rethinking Memory in LLM based Agents: Representations, Operations, and Emerging Topics](https://arxiv.org/abs/2505.00675). arXiv, 2025.
3. Luo et al. [From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms](https://aclanthology.org/2026.findings-acl.2069/). ACL 2026 Findings.
4. Zhang et al. [A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501). arXiv, 2024.

### 2025 正式论文

5. Wu et al. [LongMemEval](https://proceedings.iclr.cc/paper_files/paper/2025/file/d813d324dbf0598bbdc9c8e79740ed01-Paper-Conference.pdf). ICLR 2025.
6. Xu et al. [A-MEM](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html). NeurIPS 2025 Main.
7. [Agentic Plan Caching](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9549f7d06700f0966d5f938f1d11022a-Abstract-Conference.html). NeurIPS 2025 Main.
8. Wang et al. [Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html). ICML 2025.
9. Hu et al. [HiAgent](https://aclanthology.org/2025.acl-long.1575/). ACL 2025 Long.
10. [R2D2: Reflective Agentic Memory](https://aclanthology.org/2025.acl-long.1464/). ACL 2025 Long.
11. [In Prospect and Retrospect](https://aclanthology.org/2025.acl-long.413/). ACL 2025 Long.
12. [Contextual Experience Replay](https://aclanthology.org/2025.acl-long.694/). ACL 2025 Long.
13. Tan et al. [MemBench](https://aclanthology.org/2025.findings-acl.989/). ACL 2025 Findings.
14. [Unveiling Privacy Risks in LLM Agent Memory](https://aclanthology.org/2025.acl-long.1227/). ACL 2025 Long.
15. [TReMu](https://aclanthology.org/2025.findings-acl.972/). ACL 2025 Findings.
16. Zhou et al. [M2PA](https://aclanthology.org/2025.findings-acl.1191/). ACL 2025 Findings.
17. Ong et al. [THEANINE](https://aclanthology.org/2025.naacl-long.435/). NAACL 2025 Long.
18. Gao et al. [CDMem](https://aclanthology.org/2025.naacl-industry.80/). NAACL 2025 Industry.
19. Kang et al. [MemoryOS](https://aclanthology.org/2025.emnlp-main.1318/). EMNLP 2025 Main.
20. Yang et al. [Coarse-to-Fine Grounded Memory](https://aclanthology.org/2025.emnlp-main.659/). EMNLP 2025 Main.
21. [PersonaMem](https://www.microsoft.com/en-us/research/publication/know-me-respond-to-me-benchmarking-llms-for-dynamic-user-profiling-and-personalized-responses-at-scale/). COLM 2025.
22. [Dynamic Steering with Episodic Memory](https://aclanthology.org/2025.findings-acl.706/). ACL 2025 Findings.
23. [Graph-Structured Long-term Memory for Personal Assistant](https://aclanthology.org/2025.findings-acl.901/). ACL 2025 Findings.

### 2026 正式论文

24. Yu et al. [Agentic Memory / AgeMem](https://aclanthology.org/2026.acl-long.981/). ACL 2026 Long.
25. Yan et al. [Memory-R1](https://aclanthology.org/2026.acl-long.583/). ACL 2026 Long.
26. Zhang et al. [LightMem](https://aclanthology.org/2026.acl-long.588/). ACL 2026 Long.
27. [MAGMA](https://aclanthology.org/2026.acl-long.1709/). ACL 2026 Long.
28. [APEX-MEM](https://aclanthology.org/2026.acl-long.749/). ACL 2026 Long.
29. Wu et al. [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/). ACL 2026 Long.
30. Shen et al. [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/). ACL 2026 Long.
31. [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/). ACL 2026 Long.
32. [MemSearcher](https://aclanthology.org/2026.findings-acl.736/). ACL 2026 Findings.
33. [Grounding Agent Memory in Contextual Intent](https://aclanthology.org/2026.findings-acl.584/). ACL 2026 Findings.
34. [From Recall to Forgetting / Memora](https://aclanthology.org/2026.findings-acl.1337/). ACL 2026 Findings.
35. [CLAG](https://aclanthology.org/2026.findings-acl.824/). ACL 2026 Findings.
36. [EMA](https://aclanthology.org/2026.findings-acl.250/). ACL 2026 Findings.
37. [Memory as Action](https://aclanthology.org/2026.findings-acl.956/). ACL 2026 Findings.
38. [MemoBrain](https://aclanthology.org/2026.findings-acl.127/). ACL 2026 Findings.
39. [Learning How to Remember / MCMA](https://aclanthology.org/2026.findings-acl.1535/). ACL 2026 Findings.
40. [BMAM](https://aclanthology.org/2026.findings-acl.1973/). ACL 2026 Findings.
41. [Topology Matters](https://aclanthology.org/2026.findings-acl.1980/). ACL 2026 Findings.
42. [AMemGym](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0856bc553d3e3b9827e5140d0ad3bf8d-Abstract-Conference.html). ICLR 2026.
43. [MemoryAgentBench](https://iclr.cc/virtual/2026/poster/10010781). ICLR 2026.
44. [MEM1](https://iclr.cc/virtual/2026/poster/10008961). ICLR 2026.
45. [Memory-T1](https://iclr.cc/virtual/2026/poster/10006811). ICLR 2026.
46. [MemAgent](https://iclr.cc/virtual/2026/poster/10007825). ICLR 2026 Oral.
47. [Sculptor](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f9155a06ba1b20e40c38bf8541db456f-Abstract-Conference.html). ICLR 2026.
48. [StateLM / Pensieve](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8c54e9bfed4119c873f575d1d1e2f0a0-Abstract-Conference.html). ICLR 2026.
49. [ReasoningBank](https://iclr.cc/virtual/2026/poster/10007887). ICLR 2026.
50. [Memento](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b5f4587a0bdb81ecc6ce9d82320a5c2-Abstract-Conference.html). ICLR 2026.
51. [AdaMEM](https://icml.cc/virtual/2026/poster/63989). ICML 2026.
52. [MRAgent](https://icml.cc/virtual/2026/poster/60697). ICML 2026.
53. [MemoPilot](https://icml.cc/virtual/2026/poster/62463). ICML 2026.
54. [BudgetMem](https://icml.cc/virtual/2026/poster/66266). ICML 2026.

### 前沿预印本：不计作正式顶会接收

55. [MemoryArena](https://arxiv.org/abs/2602.16313). arXiv, 2026.
56. [EvoMemBench](https://arxiv.org/abs/2605.18421). arXiv, 2026.
57. [MemTrace](https://arxiv.org/abs/2605.28732). arXiv, 2026.
58. [MobileMem](https://arxiv.org/abs/2608.13606). Technical Report, 2026.
59. [StateMemBench](https://arxiv.org/abs/2608.19652). arXiv, 2026.
60. [AuthMem-Bench](https://arxiv.org/abs/2608.01679). arXiv, 2026.
61. [TANGLE](https://arxiv.org/abs/2608.13921). arXiv, 2026.
62. [SafeCommit](https://arxiv.org/abs/2608.04289). arXiv, 2026.
63. [PM-Bench](https://arxiv.org/abs/2607.12385). arXiv, 2026.

## 仓库内配套材料

- [Agent Memory 文献阅读总报告（2026-09-04）](./2026-09-04-agent-memory-literature-reading-summary.md)
- [Agent Memory 核心综述精读](../papers/memory/memory-surveys-deep-reading.md)
- [P0：直接竞争 Benchmark 精读](../papers/memory/2025-2026-p0-deep-reading.md)
- [P1：关键 Memory Method 精读](../papers/memory/2025-2026-p1-deep-reading.md)
- [P2：结构、程序性记忆与安全边界精读](../papers/memory/2025-2026-p2-deep-reading.md)
- [2026 前沿撞题审查](../papers/memory/2026-09-frontier-collision-audit.md)
- [MemReadyBench 统一研究方案](../ideas/2026-09-03-memreadybench-unified-research-proposal.md)
