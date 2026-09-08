---
title: "Agent Memory 入门综述：定义、系统、方法、评测与发展趋势"
type: beginner-survey
status: canonical
created: "2026-09-08"
audience: "beginner"
scope: "Agent Memory foundations, 2023-2026 methods and evaluation"
tags: ["agent-memory", "survey", "tutorial", "benchmark", "beginner"]
---

# Agent Memory 入门综述：定义、系统、方法、评测与发展趋势

> 本文面向尚未系统了解 Agent Memory 的读者。目标不是提出某个具体研究方案，而是用一条完整主线解释：Agent 为什么需要记忆、记忆是什么、系统怎样运作、主流方法如何演化、Benchmark 在测什么，以及该领域正在走向哪里。文献状态核验截止 2026-09-08。

## 摘要

大语言模型可以在一次调用中阅读上下文，却不会天然保留上一次会话形成的状态。Agent Memory 试图弥补这一点：它把用户、工具和环境的历史交互转化为可持续、可访问、可更新的状态，并在未来回答、规划和行动中选择性使用。

早期系统主要解决“上下文放不下”和“怎样找回过去信息”；随后研究开始组织事件、反思和工作流，让 Agent 从经验中复用策略；到 2025--2026 年，重点进一步转向由 Agent 主动决定何时写、读、更新、遗忘和验证，以及记忆是否真的改善行动。评测也从事实问答扩展到动态更新、战略使用、工具调用、在线交互、成本、安全与长期副作用。

理解这个领域最重要的一句话是：

> **Agent Memory 不是一个更大的聊天记录，而是由历史形成、跨时间持续、受策略管理，并能改变未来行为的状态。**

---

## 1. 五分钟理解 Agent Memory

### 1.1 一个简单例子

假设用户在第一次会话中告诉助手：

> “我对花生过敏，以后订餐时不要选择含花生的菜。”

一周后，用户只说：

> “帮我订一份晚餐。”

一个有长期记忆的 Agent 需要完成的不只是检索“花生过敏”四个字，而是：

1. 第一次会话中判断这条信息是否值得长期写入；
2. 保存用户身份、来源、时间和适用范围；
3. 新任务到来时找到这条约束；
4. 判断它目前是否仍有效；
5. 将它用于菜单筛选和工具参数；
6. 如果用户后来澄清“检测结果表明我不过敏”，更新旧状态；
7. 避免把这一用户的约束错误应用到别人身上。

这七步覆盖了 Agent Memory 的主要研究对象：形成、组织、检索、使用、更新、遗忘和治理。

### 1.2 三个判定条件

一套机制通常需要同时满足以下条件，才属于本文所说的 Agent Memory：

- **持久性（persistence）**：信息跨 turn、任务或 session 保留，而不只存在于当前 prompt；
- **能动性（agency）**：Agent 或 memory policy 会决定写什么、读什么、怎样更新；
- **行为后果（behavioral consequence）**：记忆会影响回答、计划、工具调用或环境动作。

### 1.3 这个领域在研究什么

可以用八个问题概括：

1. 什么信息值得记住？
2. 应保存原始事件、摘要、事实，还是技能？
3. 记忆之间如何建立时间、实体和因果关系？
4. 当前任务应检索哪些内容，何时停止检索？
5. 找到的记忆是否可信、适用和足以支持行动？
6. 新旧信息冲突时如何更新、合并或保留分歧？
7. 如何在容量、时延、成本、隐私和正确性之间权衡？
8. 怎样知道系统的提升来自真正的记忆能力，而不是更长上下文或更大检索预算？

---

## 2. 正式定义

### 2.1 工作定义

> **Agent Memory 是由 Agent 与用户、工具或环境的历史交互形成，能够跨当前上下文、时间或会话持续存在，并在后续感知、推理、规划、行动或自我改进中被选择性读写和更新的状态。**

设第 `t` 步之前的交互历史为：

\[
H_{1:t-1}=\{u_i,a_i,o_i,f_i\}_{i=1}^{t-1},
\]

其中 `u` 表示用户输入，`a` 表示 Agent 动作，`o` 表示环境观察，`f` 表示反馈。记忆系统把历史与旧状态转化为新状态：

\[
M_t=\mathcal{U}(M_{t-1},H_t;\pi_M),
\]

`U` 是更新过程，`π_M` 是记忆策略。Agent 再根据当前观察、目标、上下文和记忆选择动作：

\[
\pi_A(a_t\mid o_t,g_t,C_t,M_t).
\]

关键不是系统里有没有一个名为 `memory` 的数据库，而是 `M_t` 是否来自历史、能否持续演化，以及它是否改变未来策略 `π_A`。

### 2.2 Memory item、state、system 与 policy

| 术语 | 含义 | 例子 |
|---|---|---|
| Memory item | 一条可寻址的记忆单元 | 用户偏好、一次失败、一个工作流 |
| Memory state | 某一时刻全部有效记忆及其关系和元数据 | 当前用户画像、版本和未解决冲突 |
| Memory system | 管理整个生命周期的后端 | 向量库、图、层次存储、混合架构 |
| Memory policy | 决定写、读、更新、遗忘和验证的策略 | 规则、LLM controller、训练得到的 policy |

---

## 3. 它与相邻概念有什么区别

### 3.1 Agent Memory 与长上下文

长上下文是在一次推理中让模型读取更多 token。它解决“当前能看到多少”，但不自动解决：

- 哪些历史值得保留；
- 旧信息何时失效；
- 多个来源如何冲突；
- 不同用户如何隔离；
- 哪些内容可以用于工具行动。

因此长上下文可以是 Memory 系统的 reader，却不等于完整 Memory 系统。

### 3.2 Agent Memory 与 RAG

传统 RAG 通常从相对静态的外部文档库回答当前 query。Agent Memory 的内容主要由历史交互形成，会随着后续行为和反馈持续更新。

一个实用判断是：

> 删除当前 query 后，这些信息是否仍因为过去的交互而存在，并将在未来任务中继续被访问、修改或失效？

若否，它更像普通 RAG；若是，它更接近 Agent Memory。

### 3.3 Agent Memory 与 Agentic RAG

Agentic RAG 强调当前任务内主动搜索、规划、阅读、反思和停止。它可以多步，却不一定跨 session 维护持久状态。二者的交集是“主动控制检索”；区别在于 Memory 还要管理历史形成与未来演化。

### 3.4 Agent Memory 与 Context Engineering

Context Engineering 组织当前推理所需的指令、工具说明、检索结果、临时摘要和中间状态。Agent Memory 是其中一种可被调入的长期来源，但还负责 prompt 之外的持久状态生命周期。

### 3.5 Agent Memory 与 LLM Memory

LLM Memory 还可指参数记忆、KV cache、隐藏状态、长上下文结构和推理缓存。它关注模型内部容量或效率；Agent Memory 更强调跨任务状态、操作策略和行为后果。

| 概念 | 主要对象 | 常见时间尺度 | 是否必须来自交互历史 | 是否持续更新 |
|---|---|---|---:|---:|
| 长上下文 | 当前 token 序列 | 单次调用 | 否 | 否 |
| RAG | 外部文档 | 单次任务 | 否 | 通常否 |
| Agentic RAG | 主动检索过程 | 多步任务 | 否 | 可选 |
| Context Engineering | 当前上下文配置 | 当前任务 | 否 | 临时 |
| Agent Memory | 历史形成的状态与经验 | 跨 turn/session/task | 是 | 是 |
| LLM Memory | 参数、激活与缓存 | 推理到模型生命周期 | 否 | 视机制而定 |

---

## 4. Agent 记住的是什么

### 4.1 事实与语义记忆

保存用户事实、偏好、环境知识和稳定关系，例如“用户住在上海”“项目使用 Python 3.11”。难点是时间有效性、来源和作用域。

### 4.2 情景记忆

保存带时间、人物、环境和结果的具体经历，例如“一次部署因数据库迁移顺序错误而失败”。它回答“发生过什么”。

### 4.3 经验与反思记忆

把一条或多条轨迹抽象为注意事项或策略，例如“出现该错误时先检查 schema version”。[Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)把语言反馈写入 episodic memory，展示了不更新模型参数也能从失败中改进行为。

### 4.4 程序性与技能记忆

保存“如何做”的可复用步骤、代码或工作流。[Voyager](https://arxiv.org/abs/2305.16291)维护可执行技能库；[Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html)从网页任务轨迹中归纳可复用 workflow。

### 4.5 工作记忆

维护当前长程任务的中间状态、待办目标、证据和计划。它可能只在一个任务内存在，因此与 context management 的边界最接近。

### 4.6 前瞻记忆

保存“未来满足某条件时要做什么”，例如“下次登录服务器后检查训练日志”。它不仅要记住内容，还要在正确时间或事件触发时主动执行。

---

## 5. 记忆以什么形式存在

| 形式 | 典型实现 | 优点 | 局限 |
|---|---|---|---|
| 原始轨迹 | 完整对话、工具日志、文件 | 信息保真、便于审计 | token 与检索成本高 |
| 文本条目 | note、事实、摘要、反思 | 可读、易接入 LLM | 容易丢失结构与限定条件 |
| 向量索引 | embedding + Top-k | 工程成熟、检索快 | 相似不等于适用，版本关系弱 |
| 结构化记录 | JSON、表、slot、event | 易验证、可更新 | schema 设计和抽取成本高 |
| 图结构 | 实体图、事件图、时间图、超图 | 表达关系、依赖与多跳证据 | 建图错误和维护复杂 |
| 层次记忆 | 短期/中期/长期，多级摘要 | 兼顾效率与范围 | 跨层一致性难保证 |
| 参数/隐式记忆 | 微调、LoRA、memory token | 推理时紧凑 | 难删除、难解释、难局部更新 |
| 混合系统 | 原始证据 + 索引 + 摘要 + 技能 | 兼顾保真和效率 | 组件多，错误来源难定位 |

现代系统常采用混合结构。重要的不是“图一定优于向量库”，而是结构是否匹配任务需要，并且在成本、可更新性和可追溯性上值得。

---

## 6. 一个完整 Memory 系统怎样工作

可以把生命周期概括为：

`Observe -> Write -> Organize -> Retrieve -> Use -> Update/Forget -> Govern`

### 6.1 Observe：获取历史事件

来源包括用户消息、Agent 动作、工具反馈、环境事件、其他 Agent 消息和人工纠正。系统首先要确定身份、时间和 session 边界。

### 6.2 Write：决定写什么

常见方法：

- 全量保存；
- 规则抽取事实和偏好；
- LLM 摘要或反思；
- 根据 novelty、importance、future utility 打分；
- 让 policy 选择 `ADD / UPDATE / DELETE / NOOP`。

典型失败是漏写、幻觉写入、把临时要求写成永久偏好，以及从一次偶然成功过度归纳策略。

### 6.3 Organize：建立可访问结构

系统会为条目增加 embedding、关键词、标签、实体、时间、来源、权限和关系。[A-MEM](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html)借鉴 Zettelkasten，动态建立记忆链接并让旧条目随新信息演化；2026 年的 MAGMA、GAM 等进一步使用多图或层次图表达不同关系。

### 6.4 Retrieve：为当前任务选候选

常见流水线是：

1. 用 query、用户、时间和任务状态构造检索请求；
2. 向量、关键词或图遍历生成候选；
3. 用 reranker 判断相关性、时效和适用性；
4. 在 token/cost 预算下选择 Top-k；
5. 必要时继续多步检索或停止。

最大误区是把“文本相似”当成“当前可用”。高度相似的旧经验可能已经过期，或来自错误用户和不同任务条件。

### 6.5 Use：让记忆影响推理和行动

使用方式包括：

- 引用事实回答问题；
- 应用偏好进行个性化；
- 用过去经验修改计划；
- 调用合适工具并恢复参数；
- 判断是否需要查询、验证、追问或拒绝行动。

[StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/)强调必须、可选和无关记忆的差异；[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)把长期记忆用于工具选择与参数落地。这标志着评测从“找回信息”走向“用记忆做事”。

### 6.6 Update 与 Forget：维持当前有效状态

常见策略：

- 覆盖旧值；
- append-only 保存全部版本；
- 显式记录 supersede 关系；
- 证据不足时保留冲突；
- 按 TTL、LRU、价值或风险遗忘；
- 把多个事件压缩为更抽象的规则。

困难在于“过去真实”不等于“现在有效”。覆盖过快会丢失历史，保留过多又会让旧版本抢占检索结果。

### 6.7 Govern：控制来源、权限与风险

高质量记忆通常还需要：

- provenance：这条信息来自哪里；
- authority：来源是否有权影响当前决策；
- scope：适用于哪个用户、项目或环境；
- validity：当前是否仍有效；
- privacy：谁能读取、修改和删除；
- audit：哪条记忆影响了哪个动作。

当 Agent 可以发邮件、下单或修改文件时，治理不再是附加功能，而是行动前的证据边界。

---

## 7. 方法如何演化

### 7.1 2023：外部记忆架构成型

- [Generative Agents](https://arxiv.org/abs/2304.03442)：保存自然语言经历，通过 relevance、recency、importance 检索，并形成高层反思用于计划。
- [Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)：把环境反馈转化为语言反思，跨 trial 改善行为。
- [Voyager](https://arxiv.org/abs/2305.16291)：用不断增长的可执行技能库支持开放式具身学习。
- [MemGPT](https://arxiv.org/abs/2310.08560)：借鉴操作系统分层内存，在有限上下文与外部存储之间调度信息。

这一阶段回答：**怎样让模型拥有当前 prompt 之外的可持续信息。**

### 7.2 2024：长期对话与检索评测建立

- [LoCoMo](https://aclanthology.org/2024.acl-long.747/)提供最长可达 32 个 session、平均约 600 turn 的对话，评价 QA、事件总结和多模态对话生成。
- 图检索、时间建模和个性化记忆逐渐成为主流增强方式。

这一阶段回答：**很长的历史里还能否找到并综合过去信息。**

### 7.3 2025：组织、经验抽象与工程效率

- [LongMemEval](https://openreview.net/pdf?id=pZiyCaVuti)系统评价信息抽取、跨 session 推理、时间推理、知识更新和拒答。
- [A-MEM](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html)让记忆链接和上下文属性动态演化。
- [Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html)把成功轨迹归纳为可复用 workflow。
- [MemoryOS](https://aclanthology.org/2025.emnlp-main.1318/)与后续层次系统强调多级存储、更新和检索的工程闭环。

这一阶段回答：**怎样把大量事件组织成更可复用的知识和经验。**

### 7.4 2026：可学习策略、行动和治理

- [AgeMem](https://aclanthology.org/2026.acl-long.981/)将长期与短期记忆操作统一为 Agent 的工具动作，并用分阶段 RL 和 step-wise GRPO 学习。
- [Memory-R1](https://aclanthology.org/2026.acl-long.583/)分别训练 Memory Manager 和 Answer Agent，学习 `ADD / UPDATE / DELETE / NOOP` 及记忆选择。
- [LightMem](https://aclanthology.org/2026.acl-long.588/)以小模型和离线 consolidation 降低在线延迟。
- [SteeM](https://aclanthology.org/2026.acl-long.670/)把记忆依赖建模为可控制维度，处理 anchoring 与 under-use。
- [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/)揭示 experience-following、错误传播和错误经验重放。

这一阶段回答：**怎样学习 Memory policy，以及怎样控制它对行动的影响和风险。**

### 7.5 三条总趋势

方法演化可以同时用三条轴理解：

1. **Storage -> Reflection -> Experience**：从保存记录到抽象经验；
2. **Heuristic -> Agentic -> Learned Policy**：从固定规则到 Agent 主动操作，再到训练 memory policy；
3. **Answer -> Action -> Governance**：从回答正确到工具行动，再到可验证、可撤销和有权限边界的长期行为。

---

## 8. 主流架构家族

### 8.1 Full-history / Sliding-window

直接保留全部或最近历史。实现简单，适合作为基线；随着历史增长，成本和干扰迅速增加。

### 8.2 Retrieval memory

把历史切分、索引并按 query 取 Top-k。适合事实回忆，工程最成熟；主要风险是 chunk 粒度、embedding、预算和 reranker 共同影响结果。

### 8.3 Summary / Hierarchical memory

将近期细节、中期摘要和长期抽象分层保存。效率高，但反复压缩会丢失时间、来源、否定和低频约束。

### 8.4 Graph / Structured memory

把人物、事件、时间、因果和依赖显式连接。适合多跳推理、版本更新和追踪来源；构建与更新质量决定上限。

### 8.5 Experiential / Procedural memory

保存反思、案例、技能或工作流。它能改善长程 Agent 任务，却最容易发生负迁移：旧经验与当前任务表面相似但条件不同。

### 8.6 Parametric / Latent memory

把经验压入模型参数或隐式状态。调用成本低，但可解释、可更新、可删除和权限管理更困难。

### 8.7 Hybrid memory

同时保存原始证据、结构化事实、索引、摘要和技能。它最接近真实系统，但也使失败归因成为重要问题：错误究竟发生在写入、组织、检索还是使用？

---

## 9. Benchmark 如何演化

### 9.1 第一代：长期事实回忆

核心问题是过去信息能否在很长历史中被找回。代表工作包括 LoCoMo 和 LongMemEval。它们奠定了长期记忆的公共任务与数据格式。

### 9.2 第二代：时间、更新与遗忘

评测加入事件先后、跨 session 推理、偏好变化、旧信息失效、TTL/LRU 和拒答，关注系统能否维护“当前有效状态”。

### 9.3 第三代：战略使用与行动

StratMem-Bench 评价哪些记忆必须使用、可以使用或不应使用；Mem2ActBench 评价工具选择和参数恢复。重点从 passive recall 转为 memory-to-action。

### 9.4 第四代：交互过程与生命周期

AMemGym 等评测让 Agent 自己参与交互并形成记忆；近期工作还诊断 write、retrieve、use、update 和 repair 的具体阶段，而不只报告最终准确率。

### 9.5 第五代：成本、可信与长期副作用

最新评测开始关注：

- 检索和上下文预算；
- 来源、权限与污染；
- 过早行动与拒绝；
- 错误记忆的传播；
- 修复后的复发和无关状态损伤；
- 不同评测配置是否造成系统排名翻转。

### 9.6 代表性 Benchmark

| Benchmark | 出处 | 主要输入 | 核心能力 | 主要边界 |
|---|---|---|---|---|
| LoCoMo | ACL 2024 Long | 多 session 长对话 | 回忆、多跳、时间、总结 | 输出偏问答/生成 |
| LongMemEval | ICLR 2025 | 可扩展聊天历史 | 抽取、跨会话、更新、拒答 | 非完整行动闭环 |
| MemBench | ACL 2025 Findings | 亲历/旁观经历 | 事实、反思、容量、效率 | 动态冲突有限 |
| MemoryAgentBench | ICLR 2026 | 增量 memory chunks | 检索、TTL、LRU、遗忘 | chunk 与真实事件有距离 |
| AMemGym | ICLR 2026 | on-policy 长时交互 | write/read/use 诊断 | 任务域与用户模拟受限 |
| StratMem-Bench | ACL 2026 Long | query、角色与候选记忆 | 必须/可选/无关的战略使用 | 候选已给定，偏单轮生成 |
| Mem2ActBench | ACL 2026 Long | 长期历史与工具任务 | 工具选择、参数落地 | 主要评价离线 action generation |
| MemoryArena | arXiv 2026 | 多 session Agent task | memory acquisition 与行动耦合 | 预印本，协议仍在演化 |

---

## 10. 应该评价哪些指标

只报告最终答案准确率，会把多个阶段混在一起。一个更完整的指标体系包括：

### 10.1 内容质量

- 写入 Precision / Recall；
- 事实和摘要一致性；
- 时间、来源、权限字段保留率；
- 重复、冲突和过期条目比例。

### 10.2 检索质量

- Recall@k、Precision@k、MRR、nDCG；
- gold evidence coverage；
- 检索预算、token 成本与延迟；
- 新旧版本的正确选择率。

### 10.3 使用与行动

- 最终回答正确率或 F1；
- 工具选择准确率；
- 参数 grounding 准确率；
- 证据引用正确率；
- 在证据不足时的 verify / ask / abstain 行为。

### 10.4 状态演化

- update、merge、invalidate、delete 的准确率；
- stale memory 残留率；
- 冲突解决与来源恢复；
- 相关未来任务收益与无关任务污染率。

### 10.5 效率

- 每轮模型调用次数；
- 读写 token；
- 存储增长；
- 在线延迟；
- 单次成功任务的总成本。

### 10.6 安全与治理

- 越权记忆使用率；
- 污染写入率与传播率；
- 敏感信息泄露率；
- 高风险动作前的验证成功率；
- 删除、撤销和审计的完备性。

---

## 11. 常见失败模式

### 11.1 漏写与错误写入

重要信息没有进入 memory，或模型把推测、玩笑和临时要求写成事实。

### 11.2 检索不到与检索错

正确条目存在但没有被找到；或者相似但不适用的旧经验排在前面。

### 11.3 召回后不用

证据已经进入上下文，模型仍按参数先验或旧计划行动。检索指标正常，任务却失败。

### 11.4 过度使用与 Memory Anchoring

历史经验对当前输出产生过强约束，使 Agent 重复旧方案、忽略新证据或减少搜索分支。更多 Memory 因此不保证更好。

### 11.5 时间失效与冲突

旧地址、旧偏好或旧环境状态仍被当作当前事实；多个来源互相矛盾时，系统过早选择一方。

### 11.6 压缩失真

摘要保留了结论，却丢失否定、例外、来源、授权和时间条件。压缩越多，错误可能越难追踪。

### 11.7 错误传播

一次失败被写成“成功经验”，后续相似任务反复重放。2026 年的经验跟随研究显示，memory addition/deletion 会系统性改变长期行为。

### 11.8 身份、权限和来源漂移

系统把一个用户的偏好应用给另一个用户，或将低可信来源在多次总结后升级为事实。

### 11.9 评测混杂

embedding、chunk、Top-k、原文保留和 judge 不同，可能比方法本身更影响结果。因此公平比较需要固定预算并报告 pipeline 配置。

---

## 12. 为什么“更多 Memory”并不总是更好

记忆带来的收益和风险可以写成一个简单权衡：

\[
U(M)=\text{task gain}-\lambda_1\text{cost}-\lambda_2\text{interference}-\lambda_3\text{risk}.
\]

增加 Memory 容量可能提高覆盖，却也会：

- 增加检索候选和上下文成本；
- 让旧版本、噪声和相似经验更容易被召回；
- 强化 anchoring，抑制新的探索；
- 扩大隐私、权限和污染攻击面。

因此研究目标逐渐从“最大化存储和召回”转向“最大化长期净效用”。

---

## 13. Memory policy 如何学习

### 13.1 规则与 Prompt

最简单的方法使用阈值、TTL、固定 Top-k 和 LLM 提示词。优点是透明、便宜；缺点是难以适应任务和长期反馈。

### 13.2 监督学习与偏好学习

可训练 writer、retriever、reranker 或 controller：

- pointwise：判断单条记忆是否相关或有用；
- pairwise：比较两条记忆或两个动作谁更适合；
- listwise：对整个候选集合排序；
- DPO/contrastive loss：学习偏好或边界。

这类方法适合有明确局部标签的模块，成本通常低于在线 RL。

### 13.3 强化学习

当写入的价值延迟到未来、多步检索和更新共同决定结果时，可以把 memory operations 当作 action，用任务成功、成本和长期收益形成奖励。

AgeMem 使用分阶段 RL 和 step-wise GRPO；Memory-R1 使用 PPO/GRPO 学习管理和使用记忆。RL 的优势是优化整体结果，难点是：

- 长程信用分配；
- 奖励是否真正反映 Memory 质量；
- 错误写入会改变未来训练分布；
- policy 可能学会投机地少写或过度依赖某类任务规律。

因此合理顺序通常是：规则基线 -> 监督/偏好学习 -> 只有确有延迟回报时再做 RL。

---

## 14. 2025--2026 的方法趋势

### 14.1 从固定 pipeline 到自主 Memory operation

Agent 开始把 `store / retrieve / update / summarize / discard` 当作可调用工具，并学习何时执行。

### 14.2 从平坦条目到多关系结构

时间、实体、因果、来源和层次被拆分建模，图结构和混合记忆增加。但“是否需要图”越来越依赖任务，而不是默认答案。

### 14.3 从事实记忆到经验与程序记忆

系统不只记住“是什么”，还提炼“如何做”。这使 Agent 能跨任务学习，也带来技能适用边界和负迁移问题。

### 14.4 从全局开关到条件化使用

研究开始承认 always-on 与 always-off 都不理想，Memory 的依赖程度、验证和行动承诺应由当前状态控制。

### 14.5 从单目标准确率到多目标优化

效果、token、延迟、存储、隐私、权限、来源和副作用共同决定系统价值。预算约束和 Pareto 前沿成为重要评价方式。

### 14.6 从离线问答到在线长期交互

未来任务和 Memory 由 Agent 自己的行动产生，评价从固定历史的 off-policy 逐步转向 on-policy。此时一次错误写入会改变后续状态分布，系统更接近真实部署。

---

## 15. 评测趋势

1. **从 instance average 到结构化单元。** 不只平均每道题，而按用户、事件、会话、状态族或完整 episode 统计。
2. **从最终答案到阶段诊断。** 区分 write、retrieve、use、update 和 action failure。
3. **从静态历史到受控干预。** 固定任务与世界，只改变 Memory 状态，观察行为差异。
4. **从一次正确到未来净收益。** 检查修复后是否复发，是否损害无关任务。
5. **从无预算比较到成本配平。** 固定 Top-k、token、模型调用和原文可见性。
6. **从单一 judge 到混合评价。** 工具和状态尽量程序评分，开放文本才使用人工或 LLM judge。
7. **从效果到可信。** provenance、authority、privacy 和 auditability 逐步进入 benchmark。

---

## 16. 仍然开放的问题

下面是领域问题，不代表任何一项都尚无人研究或天然具有新颖性：

- 写入时不知道未来任务，如何估计长期价值？
- 何时应依赖经验，何时应保留探索和重新验证？
- 多条记忆共同支持一个行动时，如何评价组合贡献？
- 怎样保留低频但高后果的约束，而不保存全部历史？
- 压缩后如何保留来源、时间、否定和权限？
- 多个 Agent 共享记忆时，如何隔离身份、授权和责任？
- 错误记忆已经导致外部动作后，怎样最小化修复副作用？
- 显式文本、图和隐式记忆之间如何安全迁移？
- 如何评价多年、多应用、多模态的真实个人记忆？
- 一个 benchmark 的排名是否对 chunk、embedding、预算和 judge 稳定？

这些问题都需要进一步核查同期工作，并通过小规模可证伪实验确认现象，而不能只凭宽泛 gap 表述立项。

---

## 17. 初学者如何阅读这个领域

### 第一组：先理解基本架构

1. [Generative Agents](https://arxiv.org/abs/2304.03442)：记忆、反思与计划。
2. [Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)：把反馈变成可复用经验。
3. [MemGPT](https://arxiv.org/abs/2310.08560)：分层 Memory 与上下文调度。

### 第二组：理解 Benchmark

1. [LoCoMo](https://aclanthology.org/2024.acl-long.747/)：超长多会话对话。
2. [LongMemEval](https://openreview.net/pdf?id=pZiyCaVuti)：五类长期记忆能力。
3. [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/)：从记住到恰当使用。
4. [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)：从记忆到工具行动。

### 第三组：理解现代方法

1. [A-MEM](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html)：动态组织。
2. [Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html)：程序性经验。
3. [AgeMem](https://aclanthology.org/2026.acl-long.981/)：统一短期/长期操作与 RL。
4. [Memory-R1](https://aclanthology.org/2026.acl-long.583/)：学习管理和使用 Memory。
5. [LightMem](https://aclanthology.org/2026.acl-long.588/)：效率导向的系统设计。

### 第四组：理解风险和趋势

1. [Controllable Memory Usage](https://aclanthology.org/2026.acl-long.670/)：锚定与可控依赖。
2. [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/)：经验跟随和错误传播。
3. [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564)：形式、功能、动态和领域边界。
4. [From Storage to Experience](https://aclanthology.org/2026.findings-acl.2069/)：Storage、Reflection、Experience 的演化视角。

---

## 18. 实现一个最小 Memory Agent

初学者可以从下面的最小结构开始，不必立刻训练模型：

```text
Event Log
  -> Memory Writer
  -> Structured Memory Store
  -> Hybrid Retriever (BM25 + Embedding)
  -> Reranker / Validity Filter
  -> Agent Planner or Tool Caller
  -> Feedback and Memory Update
```

每条 memory item 至少保存：

```json
{
  "content": "用户对花生过敏",
  "type": "constraint",
  "subject": "user_001",
  "event_time": "2026-09-01",
  "source": "user_statement",
  "authority": "self_report",
  "scope": "food_ordering",
  "validity": "active",
  "supersedes": null
}
```

最低限度对照：

- no-memory；
- full-history；
- BM25；
- dense Top-k；
- hybrid retrieval；
- oracle evidence。

最低限度日志：

- 写入前事件；
- 写入后的 memory state；
- 检索候选与分数；
- 实际进入上下文的证据；
- 最终答案或工具调用；
- 环境反馈；
- 更新、失效和删除记录。

这套日志比一开始选择复杂模型更重要，因为它决定后续能否区分形成、检索和使用错误。

---

## 19. 对这个领域的整体判断

Agent Memory 已经从“给 LLM 接一个向量库”发展为独立的 Agent 系统问题。其核心对象是一个持续演化的状态以及管理该状态的策略。系统不仅要记得多，还要知道：

- 什么值得形成长期状态；
- 哪种结构能支持未来任务；
- 当前是否应当相信和使用；
- 证据何时足以支持行动；
- 新信息到来后怎样更新或保留冲突；
- 如何控制成本、权限、隐私和错误传播。

因此，未来较强的工作通常不会只报告“在 QA 上提高几个点”，而会同时说明 **Memory 改变了什么行为、在哪个阶段起作用、代价是什么、失效时会造成什么后果，以及评测结论是否在受控条件下成立。**

---

## 20. 核心参考文献

### 综述与定义

- Hu et al. [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564), arXiv, 2025/2026.
- Zhang et al. [Rethinking Memory in AI: Taxonomy, Operations, Topics, and Future Directions](https://arxiv.org/abs/2505.00675), arXiv, 2025.
- Luo et al. [From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms](https://aclanthology.org/2026.findings-acl.2069/), Findings of ACL 2026.

### 奠基工作

- Park et al. [Generative Agents](https://arxiv.org/abs/2304.03442), UIST 2023 / arXiv.
- Shinn et al. [Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html), NeurIPS 2023 Main.
- Wang et al. [Voyager](https://arxiv.org/abs/2305.16291), arXiv 2023.
- Packer et al. [MemGPT](https://arxiv.org/abs/2310.08560), arXiv 2023.

### 代表性方法

- Xu et al. [A-MEM](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html), NeurIPS 2025 Main.
- Wang et al. [Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html), ICML 2025.
- Kang et al. [MemoryOS](https://aclanthology.org/2025.emnlp-main.1318/), EMNLP 2025 Main.
- Yu et al. [AgeMem](https://aclanthology.org/2026.acl-long.981/), ACL 2026 Long.
- Yan et al. [Memory-R1](https://aclanthology.org/2026.acl-long.583/), ACL 2026 Long.
- Zhang et al. [LightMem](https://aclanthology.org/2026.acl-long.588/), ACL 2026 Long.
- Huang et al. [Controllable Memory Usage](https://aclanthology.org/2026.acl-long.670/), ACL 2026 Long.
- Xiong et al. [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/), ACL 2026 Long.

### 代表性 Benchmark

- Maharana et al. [LoCoMo](https://aclanthology.org/2024.acl-long.747/), ACL 2024 Long.
- Wu et al. [LongMemEval](https://openreview.net/pdf?id=pZiyCaVuti), ICLR 2025.
- Wu et al. [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/), ACL 2026 Long.
- Shen et al. [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/), ACL 2026 Long.
