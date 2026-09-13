# Agent Memory 调研综述 PPT 编排方案

> 日期：2026-09-13
>
> 定位：纯 Agent Memory 调研汇报，不包含 KGR 背景、KGR 方法、EoG/BoG 或 KGR 实验。
>
> 建议时长：30--35 分钟；正文 30 页，参考文献与补充材料 4--5 页。
>
> 选文原则：正文以 2024--2026 年 ICML、NeurIPS、ICLR、ACL、EMNLP 等正式接收论文为主要证据；2023 年工作仅用于交代范式起点；2026 年尚未正式接收的 arXiv 工作只用于同期工作审查，并统一标注为“预印本”。

## 1. 汇报的核心故事

整份 PPT 只回答五个问题：

1. Agent Memory 为什么是独立研究问题？
2. Agent Memory 与长上下文、RAG、LLM Memory 有什么区别？
3. Agent Memory 系统如何形成、组织、检索、使用和更新记忆？
4. 方法和 Benchmark 经历了怎样的演化？
5. 当前还缺什么，我们准备从哪里切入？

建议按照下面的逻辑讲述：

> 跨会话需求 → Agent Memory 定义 → 记忆类型与生命周期 → 顶会方法演化 → Benchmark 演化 → “记忆是否可用” → 三条研究切口 → MemReadyBench 与后续方法

不要采用“逐篇论文介绍”的目录。论文应作为支撑上述演化主线的证据。

---

## 2. PPT 总体结构

| 部分 | 页码 | 目标 |
|---|---:|---|
| 问题与定义 | 1--7 | 让不了解该领域的人知道 Agent Memory 是什么 |
| 方法演化 | 8--15 | 以近三年顶会工作说明系统从外部存储走向主动管理、冲突治理与压缩 |
| Benchmark 演化 | 16--22 | 说明评价对象如何从事实召回扩展到可用性、行动和纵向修复 |
| Research Gap | 23--25 | 从现有证据推出一个 Benchmark 主线和两条方法线 |
| 方案与总结 | 26--30 | 给出 MemReadyBench、后续方法方向、趋势和结论 |

正文最多保留三个章节过渡页；不要像原综合版一样频繁使用整页章节封面。

---

## 3. 逐页内容

### 第 1 页：封面

**标题：** Agent Memory 调研综述

**副标题：** 从长期信息召回到可学习、可验证的持续记忆系统

**页内信息：** 汇报人、课题组、日期。

**视觉：** 保留学校与实验室模板，不放论文截图。

**本页目的：** 明确这是一份 Agent Memory 领域综述，不再出现 KGR。

---

### 第 2 页：汇报路线

**标题：** 这份综述回答五个问题

**正文：**

- 为什么普通 LLM 仍然需要持久记忆？
- 哪些状态属于 Agent Memory？
- 一个 Memory System 怎样运行？
- 目前的方法和 Benchmark 在评价什么？
- 当前还存在哪些可研究问题？

**视觉：** 自绘五步横向流程。

**图片策略：** 必须自己画，不借论文图。

---

### 第 3 页：动机案例

**标题：** 为什么长上下文不等于 Agent Memory？

**案例：**

- Session A：用户告诉 Agent“我对花生严重过敏”。
- 一段时间后会话结束，当前上下文被清空。
- Session B：用户要求 Agent 预订一家餐厅。
- Agent 必须恢复历史约束、判断其仍然有效，并将它落实到搜索和预订行动中。

**结论句：**

> 真正的问题不是“历史文本还能否被看到”，而是“哪些历史应持续存在、何时可信，以及应怎样改变未来行为”。

**视觉：** 自绘 Session A → Memory → Session B → Tool Action。

**图片策略：** 必须自己画。

---

### 第 4 页：Agent Memory 的工作定义

**标题：** Agent Memory：跨时间持续并影响未来行为的状态

**定义：**

> Agent Memory 是由 Agent 与用户、工具或环境的历史交互形成，能够跨当前上下文或会话持续存在，并在后续感知、推理、规划、行动或自我改进中被选择性读写和更新的状态。

**三个判据：**

- Persistence：是否跨 turn、session 或任务持续存在；
- Agency：Agent 是否能够选择性写入、检索、更新或删除；
- Behavioral consequence：它是否真正影响未来答案、计划或行动。

**视觉：** 三个并列矩形，不使用 Venn 图。

**参考：** Memory in the Age of AI Agents；From Storage to Experience。

---

### 第 5 页：概念边界

**标题：** 不要混淆 Agent Memory、RAG、长上下文与 LLM Memory

| 概念 | 核心对象 | 时间尺度 | 是否持续更新 | 主要目标 |
|---|---|---|---|---|
| 长上下文 | 当前 token 序列 | 单次调用 | 否 | 读取更多当前信息 |
| RAG | 外部文档知识库 | 单次或多步任务 | 通常否 | 获取外部知识 |
| Agentic RAG | 主动搜索和检索过程 | 多步任务 | 可选 | 规划如何获取知识 |
| LLM Memory | 参数、激活或 KV 状态 | 训练或推理阶段 | 依方法而定 | 模型内部信息保持 |
| Agent Memory | 历史交互形成的持久状态 | 跨会话、跨任务 | 是 | 让历史持续影响行为 |

**视觉：** 自绘表格；不直接沿用现有字号过小的论文概念图。

**讲述重点：** Agent Memory 可以使用 RAG、图结构或参数化载体，但不等同于其中任何一个。

---

### 第 6 页：记忆里保存什么

**标题：** Agent 到底记住什么？

| 功能类型 | 内容 | 典型用途 |
|---|---|---|
| 事实/语义记忆 | 用户事实、偏好、环境关系 | 个性化回答 |
| 情景记忆 | 带时间、参与者和结果的经历 | 回忆发生过什么 |
| 经验/反思记忆 | 成功经验、失败教训、策略 | 减少重复错误 |
| 程序/技能记忆 | 工作流、工具链和操作规则 | 完成相似任务 |
| 工作记忆 | 当前子目标、证据和中间状态 | 长程任务控制 |

**视觉：** 五列卡片或五段横向带状图。

**图片策略：** 自绘，避免使用装饰性大图。

---

### 第 7 页：记忆以什么形式存在

**标题：** 同一种功能可以由不同载体实现

| 形式 | 例子 | 优点 | 局限 |
|---|---|---|---|
| 原始轨迹 | 对话、动作和工具日志 | 保真、可审计 | 成本高、噪声多 |
| 文本条目 | 事实、摘要、反思 | 可读、易实现 | 容易丢条件和来源 |
| 向量索引 | embedding + top-k | 快速、成熟 | 相似不等于适用 |
| 结构/图 | entity、event、typed edge | 支持关系与版本 | 构建和维护复杂 |
| latent/parametric | memory token、adapter、权重 | 在线成本低 | 难解释、难更新和删除 |

**视觉：** 自绘“功能 × 形式”二维矩阵。

---

### 第 8 页：完整生命周期

**标题：** Agent Memory 是一个持续生命周期

**流程：**

> Observe → Write → Organize → Retrieve → Use → Evolve → Govern

**每一步说明：**

- Observe：接收用户交互、环境事件和工具反馈；
- Write：决定是否形成记忆以及写入什么；
- Organize：建立索引、标签、时间线和关系；
- Retrieve：针对当前任务召回候选；
- Use：回答、规划、工具行动、验证或忽略；
- Evolve：更新、失效、合并、压缩和反思；
- Govern：来源、权限、隐私、撤销和审计。

**公式：**

\[
M_{t+1}=F(M_t,o_t,a_t,r_t).
\]

**视觉：** 自绘闭环图。公式只用于表达记忆会随观察、行动和反馈演化。

---

### 第 9 页：发展时间线

**标题：** Agent Memory 从存储记录走向主动状态管理

**时间线：**

- 2023：Generative Agents、Reflexion、MemGPT 建立外部记忆、经验反思和分层管理范式；
- 2024：MemoryLLM、ReadAgent、WISE、LoCoMo 分别推进 latent memory、gist compression、终身编辑和跨会话评测；
- 2025：A-MEM、MemoryOS、M+、LongMemEval 关注组织、层次化更新、可扩展 latent memory 和能力分解；
- 2026：Memory-R1、AgeMem、LightMem、AMemGym、Mem2ActBench 转向 learned operations、小模型控制、在线交互与真实行动。

**视觉：** 自绘时间线，每年最多放 3--4 篇锚点工作。

**图片策略：** 自绘；论文 logo 只作为小型标签。

---

### 第 10 页：2023 年范式起点

**标题：** 三类早期范式奠定了 Agent Memory 的基本形态

| 工作 | 记忆机制 | 留下的核心范式 |
|---|---|---|
| Generative Agents，UIST 2023 | memory stream + retrieval + reflection + planning | 历史经历经反思后影响行为 |
| Reflexion，NeurIPS 2023 | 将任务反馈写成自然语言经验 | 失败经验可跨尝试复用 |
| MemGPT，arXiv 2023 | 主上下文与外部存储分层交换 | Agent 主动管理有限上下文 |

**本页结论：** 2023 年工作只用于解释“经验如何持续影响行为”的起点，后续论据以 2024--2026 年顶会论文为主。

**视觉：** 自绘三个结构一致的小图，不并排粘贴三张不同风格的论文截图。

---

### 第 11 页：2024 年顶会方法

**标题：** 2024：压缩、隐状态记忆与参数记忆形成三条路线

| 工作 | 出处 | 核心机制 | 对当前研究的启发 |
|---|---|---|---|
| ReadAgent | ICML 2024 | 将长文档压缩成 gist memories，必要时回看原文 | 压缩后必须保留回退到原始证据的能力 |
| MemoryLLM | ICML 2024 | 在 Transformer 中加入可自更新的固定大小 latent memory pool | 记忆可以进入模型内部状态，而非只存文本 |
| WISE | NeurIPS 2024 | 主参数记忆 + side memory + router | 参数化记忆需要隔离、路由和冲突控制 |

**讲述重点：** “压缩记忆”至少包含文本摘要、latent state 和参数/adapter 三种不同问题，不能混为一谈。

**视觉：** 自绘三路对照图，底部统一标注正式会议出处。

---

### 第 12 页：2025 年顶会方法

**标题：** 2025：从存取组件走向组织、分层和可扩展记忆

| 工作 | 出处 | 核心机制 | 仍存在的问题 |
|---|---|---|---|
| A-MEM | NeurIPS 2025 | 原子 note、动态链接与历史表示演化 | 关系正确性和冲突处理仍缺少显式保证 |
| MemoryOS | EMNLP 2025 | 短期、中期、长期三层存储及动态迁移 | 主要以规则驱动，压缩错误难以归因 |
| M+ | ICML 2025 | latent memory + 协同训练的长期检索器 | 更接近扩大记忆容量，尚非面向小模型的可控内化 |

**本页结论：** Memory organization 已经具有 agentic 特征，但“记得更多”仍不等于“在当前任务中可用”。

**视觉：** 可以引用一张 A-MEM overview，其余两项用自绘图标和简化流程表示。

---

### 第 13 页：2026 年顶会方法

**标题：** 2026：Memory operations 开始成为可学习动作

| 工作 | 出处 | 核心机制 | 关键贡献 |
|---|---|---|---|
| Memory-R1 | ACL 2026 | Memory Manager 学习 ADD/UPDATE/DELETE/NOOP，Answer Agent 学习使用 | 用 outcome-driven RL 联合优化管理和回答 |
| AgeMem | ACL 2026 | 将 LTM/STM 操作暴露为工具动作，以渐进式 RL 和 step-wise GRPO 训练 | 从外挂规则转向统一 agent policy |
| LightMem | ACL 2026 | 由小模型执行在线检索与写入，复杂 consolidation 离线完成 | 降低大模型反复调用的延迟和成本 |

**注意：** LightMem 是“用小模型管理外部记忆”，不等于“把全部记忆压入小模型参数”。

**视觉：** 自绘 `Task State → Memory Action → Answer/Tool Action → Feedback → Updated Memory`。

---

### 第 14 页：方法痛点一——记忆如何压缩进小模型

**标题：** “压缩进小模型”必须先区分三种技术目标

| 路线 | 压缩结果 | 代表工作 | 尚未解决的核心问题 |
|---|---|---|---|
| 外部文本压缩 | 摘要、gist、结构化条目 | ReadAgent、MemoryOS、LightMem | 条件、例外、来源和冲突容易在摘要中丢失 |
| latent memory | memory token、hidden state、latent pool | MemoryLLM、M+ | 状态不透明，难以精确更新、删除和审计 |
| 参数化内化 | 权重、adapter、side memory | WISE | 容量干扰、灾难遗忘、冲突覆盖和撤销困难 |

**可研究问题：** 在有限容量的小模型中，如何只内化稳定且高复用的记忆，同时把易变化、有冲突或高风险的记忆留在可验证的外部存储中？

**最低必要能力：** 选择性内化、容量预算、来源保持、冲突检测、增量更新、可删除、原证据回退。

**视觉：** 自绘 `Raw Memory → Usability/Conflict Gate → Text / Latent / Adapter` 三路分流图。

---

### 第 15 页：方法痛点二——记忆内部冲突消解

**标题：** Memory conflict 不是普通文档矛盾，而是持久状态之间竞争控制权

**典型冲突：**

- 同一事实的新旧版本冲突；
- 不同时间、用户、任务或环境条件下的记忆被错误合并；
- 原始经历与抽象总结冲突；
- 用户陈述、工具反馈与环境观察的来源权威不同；
- unresolved conflict 被系统静默压成一个确定结论。

**已有进展：** ACL 2026 的 Conflict-Aware Memory 已验证“语义相似但含义冲突”的向量记忆会损害具身 Agent 行动，并通过冲突检测规则改善规划；但版本、条件、例外、来源和压缩后的跨层冲突仍未被统一处理。

**可研究问题：** 构建带有 `SUPPORTS / CONTRADICTS / SUPERSEDES / CONDITIONED_ON / EXCEPTION_TO / UNRESOLVED` 关系的记忆图，在回答或行动前进行冲突诊断、证据获取和局部修复。

**视觉：** 自绘同一实体的版本链和条件分支，不使用普通 RAG 文档冲突示意图。

---

### 第 16 页：Benchmark 演进总览

**标题：** Benchmark 的评价对象不断向后延伸

**演进主线：**

> 长程事实召回 → 跨会话推理 → 动态更新与遗忘 → 战略使用 → 工具行动 → 冲突、治理与纵向修复

**锚点：**

- LoCoMo，ACL 2024；
- LongMemEval，ICLR 2025；
- MemBench，Findings of ACL 2025；
- MemoryAgentBench、AMemGym、CIMemories，ICLR 2026；
- StratMem-Bench、Mem2ActBench，ACL 2026；
- STALE、StateMemBench、TANGLE、AuthMem-Bench，2026 预印本，只用于前沿审查。

**视觉：** 自绘时间线。不要在这一页解释所有数据细节。

---

### 第 17 页：LoCoMo 精讲

**标题：** LoCoMo：长期多会话记忆的经典起点

**数据：**

- 10 组长对话；
- 每组平均约 600 turns、16K tokens；
- 最多约 32 sessions；
- 包含长期事件、人物关系、时间和因果信息。

**任务：**

- Question Answering；
- Event Summarization；
- Multimodal Dialogue Generation。

**意义：** 将长期对话记忆从短上下文 QA 推进到跨 session 和记忆时间关系。

**局限：** 仍主要根据最终生成结果评价，对写入、检索、使用和修复失败的归因有限。

**视觉：** 优先引用论文的数据构造或对话示例图；也可以自己重绘三段 session + query。

**来源：** Maharana et al., ACL 2024。

---

### 第 18 页：LongMemEval 精讲

**标题：** LongMemEval：将长期助手能力拆成五个维度

**五类能力：**

1. Information extraction；
2. Multi-session reasoning；
3. Temporal reasoning；
4. Knowledge updates；
5. Abstention。

**数据特点：** 500 个经过整理的问题，可嵌入不同长度的用户-助手历史。

**系统分解：** Indexing → Retrieval → Reading。

**意义：** 不只问“记住了吗”，还开始评价时间、更新与无答案场景。

**局限：** 仍以 QA 为主要终点，真实工具行动和 longitudinal repair 较弱。

**视觉：** 使用论文五项能力图或自己重绘五段能力条。

**来源：** Wu et al., ICLR 2025。

---

### 第 19 页：从静态测试走向交互评测

**标题：** Memory benchmark 正从离线 QA 走向在线状态演化

| 工作 | 出处 | 评价重点 | 局限 |
|---|---|---|---|
| MemBench | Findings of ACL 2025 | factual/reflective memory，参与/观察场景，效果/效率/容量 | 行动后果和状态干预较弱 |
| MemoryAgentBench | ICLR 2026 | 检索、测试时学习、长程理解、选择性遗忘 | 复杂条件、例外与来源冲突有限 |
| AMemGym | ICLR 2026 | 结构化用户状态、状态依赖问题、状态演化和 on-policy 交互 | 主要面向个性化对话环境 |

**本页结论：** 在线交互可以观察 memory policy 如何改变状态，但仍需要更受控的 matched intervention 来归因“哪种记忆状态导致哪种行为”。

**视觉：** 自绘 `Static/off-policy → Incremental → Interactive/on-policy` 三阶段箭头。

---

### 第 20 页：从“记住”走向“是否应该使用”

**标题：** StratMem-Bench 与 Mem2ActBench：Memory 开始影响策略和行动

**StratMem-Bench：**

- 将候选记忆分成必须使用、可选择使用和无关记忆；
- 评价 Agent 是否能克制过度引用，并生成更符合角色和情境的回答。

**Mem2ActBench：**

- 评价长期记忆能否支持工具选择和参数填充；
- 将 memory success 从回答文本推进到可执行行动。

**视觉：** 左右对照。StratMem 使用原论文 must/nice/irrelevant 案例图；Mem2Act 自绘 `Memory → Tool selection → Parameter grounding`。

**本页结论：** 找到记忆不等于正确使用，正确回答也不等于正确行动。

---

### 第 21 页：已有工作是否评价“记忆可用性”

**标题：** 有，但现有评价分散在不同任务和单一风险轴上

| 可用性维度 | 代表工作 | 实际测了什么 |
|---|---|---|
| 相关性与使用强度 | StratMem-Bench，ACL 2026 | 必须使用、辅助使用、无关记忆是否被恰当使用 |
| 行动可执行性 | Mem2ActBench，ACL 2026 | 记忆能否支持工具选择和参数填充 |
| 时效、更新与拒答 | LongMemEval，ICLR 2025 | knowledge update、temporal reasoning、abstention |
| 交互中的状态依赖 | AMemGym，ICLR 2026 | 用户状态演化后是否形成正确个性化行为 |
| 范围与隐私适用性 | CIMemories，ICLR 2026 | 同一属性在不同任务中是否应被调用或抑制 |
| 冲突可检测性 | Conflict-Aware Memory，ACL 2026 | 相似但矛盾的向量记忆能否被识别和处理 |

**结论：** 已有工作分别回答“该不该用”“能否行动”“是否最新”“是否越权”“是否冲突”，但尚未形成一套统一的、受控的 memory readiness 诊断。

**视觉：** 六个维度围绕中心 `Usable now?`，每个维度只放论文名和会议。

---

### 第 22 页：记忆可用性的操作化定义

**标题：** “记忆可用”是面向当前任务状态的条件属性

给定当前状态

\[
x_t=(q_t,g_t,w_t,T_t)
\]

其中 $q_t$ 为请求，$g_t$ 为用户目标，$w_t$ 为真实世界状态，$T_t$ 为可用工具。记忆集合 $M_t$ 只有同时满足以下条件，才应影响当前行动：

1. **相关**：与当前目标有关；
2. **充分**：证据足以支持所需结论或动作参数；
3. **新鲜**：没有被更新事实取代；
4. **一致**：内部冲突已消解，或被显式标记为未决；
5. **适用**：用户、时间、场景和权限范围匹配；
6. **可执行且净收益为正**：能转化为答案/行动，并且收益高于错误、延迟和 token 成本。

**可用性定义：**

\[
U(M_t\mid x_t)=P(\Delta Q>0\ \land\ \text{no constraint violation}\mid M_t,x_t).
\]

**Agent 决策标签：** `USE / SUPPRESS / SEARCH / VERIFY / CLARIFY / ABSTAIN / REPAIR`。

**本页结论：** “真实”只是可用性的一个条件；真实但过时、越权、不完整或无法支撑当前动作的记忆仍然不可用。

---

### 第 23 页：跨论文共识

**标题：** 2025--2026 年已经形成的共同认识

**正文：**

- 更多 memory 不一定更好；
- 语义相似不代表当前可用；
- 原始 episode 与抽象 memory 应分层保存；
- 检索成功与正确使用必须分开评价；
- 动态状态需要版本、时间和条件；
- memory operation 正在从规则走向 learned policy；
- 可信度、成本与长期效用成为共同目标；
- “记忆是否可用”必须由当前任务状态决定，而不能只由 memory item 自身决定。

**视觉：** 八条结论组成纵向列表，右侧用一条发展箭头连接。

---

### 第 24 页：三条可研究切口

**标题：** Benchmark 先定位失败，再承接两条方法路线

| 路线 | 一句话问题定义 | 现有基础 | 可形成的贡献 |
|---|---|---|---|
| Benchmark：记忆可用性 | 在任务和世界状态固定时，仅改变持久记忆状态，Agent 能否判断其是否足以、适用且可信，并据此调整行动？ | LongMemEval、StratMem、Mem2Act、AMemGym、CIMemories | 统一受控干预、诊断标签、行为与修复指标 |
| 方法 A：冲突消解 | 多条持久记忆互相矛盾时，Agent 如何基于时间、条件、来源和证据关系决定使用、验证、澄清或修复？ | Conflict-Aware Memory、WISE；STALE/TANGLE 等预印本 | typed conflict graph、未决状态、局部验证与修复 |
| 方法 B：小模型压缩 | 如何把稳定且高复用的海量记忆压缩到小模型的 latent/adapter 中，同时避免冲突覆盖、遗忘和不可撤销？ | ReadAgent、MemoryLLM、M+、WISE、LightMem | 选择性内化、外部证据回退、增量更新与可删除 |

**推荐顺序：** 先做 Benchmark，得到系统性的失败分布；再选择最显著的冲突或压缩失败，构造方法论文。

**视觉：** 自绘 `Diagnose → Resolve conflict / Compress safely` 分叉图。

---

### 第 25 页：收紧后的 Benchmark Gap

**标题：** 现有工作仍缺少统一、受控的 Memory-State Intervention

**问题定义：**

> 在任务、用户目标、真实世界状态和可用工具完全相同的情况下，仅将持久记忆替换为完整已验证、缺失、过期、冲突、不完整、过度压缩、权限漂移或干扰版本，Agent 是否会识别可用性变化，并从直接使用切换到检索、验证、澄清、拒绝或修复？

**为什么不是简单“把已有任务合并”：**

- 统一的不是数据集名称，而是同一因果干预协议；
- matched family 让行为差异可以归因于 memory state，而非 query 难度；
- 同时收集最终答案、工具动作、证据引用和 memory update，建立诊断到后果的证据链；
- 评价“何时不该使用”以及“获得新证据后能否修复”，不是只算 aggregate accuracy。

**与同期工作的边界：** StratMem 主要研究给定记忆池中的战略使用；Mem2Act 研究记忆驱动工具行动；AMemGym 研究交互状态演化；CIMemories 研究上下文完整性。这里研究的是多类 memory state 的受控可用性诊断、行动调控与纵向修复。

**视觉：** 同一个 query 指向八个 matched memory variants，再汇合到同一 Agent 和 action evaluator。

---

### 第 26 页：三个 Research Questions

**标题：** 我们具体评价什么？

**RQ1：记忆充分性与可用性诊断。** Agent 能否判断当前持久记忆是否覆盖行动所需条件，并识别缺失、过期、冲突、不完整、过度压缩或权限漂移？

**RQ2：记忆使用与行动控制。** 面对不同可用性状态，Agent 能否在 `USE / SUPPRESS / SEARCH / VERIFY / CLARIFY / ABSTAIN` 之间选择正确策略，并据此生成正确答案或工具调用？

**RQ3：记忆修复与长期价值。** 获得权威新证据后，Agent 能否正确更新、失效、合并或恢复记忆，使相关后续任务受益且不污染无关任务？

**视觉：** 三列 RQ 卡片，用 `Diagnose → Act → Repair` 串联。

---

### 第 27 页：MemReadyBench

**标题：** Benchmark：只改变 Memory State，观察 Agent 是否改变行为

**输入固定项：** query、用户目标、真实世界状态、任务要求、可用工具。

**受控变量：** 将同一记忆族变换为 `verified / missing / stale / conflicting / incomplete / over-compressed / authority-shifted / distractor`。

**任务链：**

1. Memory diagnosis：判断记忆是否充分、适用和可信；
2. Memory-use control：选择使用、抑制、检索、验证、澄清或拒绝；
3. Closure and execution：证据充分后回答或执行工具；
4. Memory repair：根据权威证据执行更新、失效、合并或来源恢复；
5. Longitudinal follow-up：在相关和无关后续任务中验证长期价值与污染。

**主要指标：**

- MSFA：Memory-State Family Accuracy；
- VCS：Verified Closure Success；
- PMCR：Premature Memory-Grounded Commit Rate；
- NAR：Normalized Acquisition Regret；
- LRU：Longitudinal Repair Utility；
- Unrelated-task Pollution Rate；
- Oracle Gate Gap。

**视觉：** 必须自己画总框架，作为整份汇报最重要的一张图。

---

### 第 28 页：Benchmark 之后的两条方法方向

**标题：** 方法不预设答案，由 Benchmark 暴露的主要失败模式决定

**方向 A：ConflictMem，面向内部冲突消解。**

- 保存不可变 episodic ledger 和带版本/时间/条件/来源的 typed memory graph；
- 对候选记忆执行 pairwise conflict detection 和 listwise evidence ranking；
- 无法消解时保留 `UNRESOLVED`，触发验证或向用户澄清；
- 新证据到来后执行局部 graph patch，并重测关联任务。

**方向 B：CompressMem，面向小模型的安全选择性内化。**

- readiness gate 只选择稳定、高复用、低冲突的记忆进入 latent/adapter；
- 动态、敏感或冲突记忆保留在外部可审计存储；
- 以任务效用、压缩率、冲突保持、遗忘、更新和删除能力共同训练；
- 低置信输出回退原始证据，不把小模型参数当作唯一真值源。

**推荐：** 先在外部记忆上完成 Benchmark 与冲突方法；压缩进小模型需要训练和模型改造，适合作为第二阶段或独立论文。

**视觉：** 左右两条方法管线，中间共用 `MemReadyBench diagnostics`。

---

### 第 29 页：未来发展趋势

**标题：** Agent Memory 的未来竞争焦点

**方法侧：**

- memory-native policy；
- episodic + structured + parametric hybrid memory；
- 多时间尺度 consolidation；
- 可学习的写入、检索、验证和修复；
- 冲突感知的选择性内化与小模型压缩；
- 多模态、具身和多 Agent 共享记忆。

**评测侧：**

- 从静态 QA 走向 longitudinal intervention；
- 从最终答案走向证据链和真实行动；
- 从平均准确率走向风险、成本和最坏情况；
- 从单次更新走向持续失效、恢复和删除。

**视觉：** 左右两列趋势箭头。

---

### 第 30 页：总结

**标题：** 用五句话理解 Agent Memory

1. Agent Memory 是跨会话持续、受策略管理并影响未来行为的状态。
2. 它不等同于 RAG、长上下文或模型参数，但可以使用这些技术作为载体。
3. 方法正在从平坦存储和 top-k 检索走向结构化组织、经验抽象和 learned memory operations。
4. Benchmark 正从事实召回扩展到动态状态、战略使用、工具行动、上下文适用性、冲突和修复。
5. 当前最稳的入口是先统一评价“记忆现在是否可用”，再围绕主要失败模式研究内部冲突消解或面向小模型的安全压缩。

**视觉：** 五条结论，不再放复杂框架图。

---

## 4. 参考文献页安排

建议使用 4 页参考文献，不要把所有文献压进一页：

### 参考文献一：定义与经典方法

- Park et al. Generative Agents. UIST 2023.
- Shinn et al. Reflexion. NeurIPS 2023.
- Packer et al. MemGPT. arXiv 2023.
- Hu et al. Memory in the Age of AI Agents. arXiv 2025/2026.
- Wang et al. MEMORYLLM: Towards Self-Updatable Large Language Models. ICML 2024.
- Lee et al. A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts. ICML 2024.
- Wang et al. WISE: Rethinking the Knowledge Memory for Lifelong Model Editing of Large Language Models. NeurIPS 2024.

### 参考文献二：近年正式接收方法

- Xu et al. A-MEM. NeurIPS 2025.
- Kang et al. MemoryOS. EMNLP 2025.
- Wang et al. M+: Extending MemoryLLM with Scalable Long-Term Memory. ICML 2025.
- Zhang et al. LightMem. ACL 2026.
- Yu et al. Agentic Memory/AgeMem. ACL 2026.
- Yan et al. Memory-R1. ACL 2026.
- Ma et al. Conflict-Aware Memory for Embodied Agents. ACL 2026.

### 参考文献三：近年正式接收 Benchmark

- Maharana et al. LoCoMo. ACL 2024.
- Wu et al. LongMemEval. ICLR 2025.
- Tan et al. MemBench. Findings of ACL 2025.
- Hu et al. MemoryAgentBench. ICLR 2026.
- Cheng et al. AMemGym. ICLR 2026.
- Mireshghallah et al. CIMemories. ICLR 2026.
- Wu et al. StratMem-Bench. ACL 2026.
- Shen et al. Mem2ActBench. ACL 2026.

### 参考文献四：2026 同期预印本审查

- HiMem、DeMem、Context Codec：consolidation、压缩与可验证性；
- STALE、StateMemBench：stale/current state；
- TANGLE：不可消解冲突与澄清；
- AuthMem-Bench：来源权威；
- MeClear、Dual-Layer Agentic Memory：冲突清理与参数/外部混合记忆。

这一页页眉必须标注“Frontier preprints / 尚未作为正式顶会接收证据”，避免与前三页混淆。

正文每页底部仍应标明本页直接使用的论文，参考文献页不能替代逐图引用。

---

## 5. 图片使用规范

### 5.1 建议自己画的图

- Agent Memory 定义和概念边界；
- 功能 × 形式分类；
- 完整生命周期；
- 2023--2026 方法时间线；
- 架构对照；
- 三种记忆压缩路线与选择性内化；
- Benchmark 演进时间线；
- 记忆可用性六维定义与 matched memory-state family；
- Research Gap；
- MemReadyBench、ConflictMem 与 CompressMem。

这些图负责表达综述者自己的归纳，直接借用某篇论文的图会限制叙事。

### 5.2 可以引用论文原图的内容

- A-MEM 的 note/link/evolution 流程；
- ReadAgent 的 gist memory 与原文回看流程；
- LoCoMo 数据构造或任务示例；
- LongMemEval 五类能力；
- StratMem-Bench 的 must/nice/irrelevant 示例；
- 一张能够支持关键判断的实验结果图。

每页最多使用一张论文原图。若原图缩小后无法阅读，应重绘，而不是继续缩小。

### 5.3 引用写法

直接使用原图：

```text
Source: Maharana et al., ACL 2024, Fig. 2.
```

裁剪、翻译或重绘：

```text
Adapted from Maharana et al., ACL 2024.
```

不要使用博客、知乎或公众号的二次截图；应回到原论文寻找原图和准确出处。公开发布 PPT 前，需要检查论文页面标明的 license。

---

## 6. 版式与语言要求

- 正文中文为主，保留论文名、方法名和标准术语英文；
- 页标题直接表达结论，避免只写“方法”“问题”“相关工作”；
- 每页只承担一个主要论点；
- 正文字号建议不低于 20 pt，核心结论不低于 24 pt；
- 一页最多 4--5 个主要 bullet；
- 表格最多保留 5 列、6 行，更多内容拆页；
- 论文截图中的文字必须在投影状态下可读；
- 每页底部统一放 9--10 pt 来源；
- 不要混用大段中文和未翻译英文句子；
- Benchmark、framework 和 architecture 等术语可保留英文，但解释必须中文化；
- 全文保持同一套蓝、黄、黑主色，不为每篇论文更换主题色。

---

## 7. 从现有 PPT 迁移内容

当前 `2026-09-03-kgr-agent-memory-progress.pptx` 中：

- 原第 2--18 页 KGR 内容全部移出正文；
- 原第 19 页 KGR 实验问题不进入纯综述版，可放个人研究经历附录；
- 原第 21 页定义页可拆分为本方案第 4、6 页；
- 原第 22 页概念图可作为参考，但正文应重绘概念边界；
- 原第 23 页 Benchmark 时间线可重绘为本方案第 16 页；
- 原第 24 页工作对照表需要拆分，避免字号过小；
- 原第 25 页三个 RQ 应放在完成方法和 Benchmark 综述之后；
- 原第 27 页方案说明应改成受控 Benchmark 构造流程；
- 原第 28 页框架图建议拆成 Benchmark 总图和方法方向两页。

可直接复用的内容主要来自：

- `2026-09-08-agent-memory-beginner-guide.pptx` 的定义、类型、生命周期和经典工作；
- `2026-09-07-agent-memory-2025-2026-survey.pptx` 的方法趋势、Benchmark 对照、评价指标和未来趋势；
- `2026-09-11-agent-memory-conflict-resolution-and-safe-consolidation.md` 的同期工作审查、冲突消解和安全压缩线索。

最终目标不是简单拼接三份材料，而是形成一条从领域定义到个人研究切口的单一叙事。

---

## 8. 当前研究决策

### 8.1 是否已经有“评估记忆是否可用”的工作？

有，但尚未形成统一定义：

- StratMem-Bench 评价记忆是否必须、可选或无关，重点是战略使用；
- Mem2ActBench 评价记忆能否真正驱动工具选择和参数填充；
- LongMemEval 评价时间、更新和无答案时的拒答；
- AMemGym 评价交互状态演化中的个性化行为；
- CIMemories 评价记忆在不同任务语境下是否允许流动；
- Conflict-Aware Memory 评价相似但矛盾的向量记忆能否被发现和管理。

因此，不能声称“过去完全没有研究 memory usability”；更准确的 gap 是：**现有工作将相关性、时效性、冲突、范围、行动和修复分散评价，缺少在同一任务下仅改变 memory state 的统一、受控、可归因评测。**

### 8.2 推荐优先级

1. **P0：MemReadyBench。** 先做 matched family、诊断标签、行为决策和纵向修复，计算资源可控，也能为后续方法提供错误分布。
2. **P1：ConflictMem。** 从 Benchmark 中筛出 stale/conflicting/incomplete/authority-shifted 子集，研究记忆内部冲突检测、证据排序、澄清和局部修复。
3. **P2：CompressMem。** 研究稳定记忆向小模型 latent/adapter 的选择性内化，必须同时评估容量、干扰、更新、删除、来源和外部证据回退，方法与训练成本最高。

### 8.3 预期两阶段论文路线

- 第一阶段 Benchmark：定义 memory readiness，证明 aggregate accuracy 难以定位记忆形成、检索、使用还是修复环节的失败；
- 第二阶段方法：根据第一阶段暴露的主要瓶颈，选择 ConflictMem 或 CompressMem，而不是一开始同时实现两套大方法。
