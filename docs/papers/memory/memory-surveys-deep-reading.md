---
title: "Agent Memory 核心综述精读"
type: literature-notes
status: reviewed
created: "2026-09-03"
tags: ["agent-memory", "survey", "taxonomy", "deep-reading"]
---

# Agent Memory 核心综述精读

综述的作用不是再列一遍系统名称，而是确定研究对象、分类轴和可被 benchmark 操作化的术语。当前最有用的三条轴是：`representation/form`、`function/type`、`operation/dynamics`。

## 1. A Survey on the Memory Mechanism of Large Language Model based Agents

**出处**：arXiv 2024；[论文](https://arxiv.org/abs/2404.13501)；[资源](https://github.com/nuster1128/LLM_Agent_Memory_Survey)。

**要解决的问题**：早期 LLM agent memory 工作分散在对话、仿真、规划和工具使用中，缺少关于“memory 是什么、为什么需要、怎样实现、怎样评价”的全景整理。

**组织方式**：论文先界定 agent memory 对长期 agent-environment interaction 和 self-evolution 的作用，再归纳设计、评测与应用。它把 memory 看作独立于 LLM 参数、但为 agent 跨时间保持信息与经验的关键模块，强调 memory source、form、operation 和使用位置。

**贡献**：提供了领域早期共同语言，并把评价纳入 memory 设计讨论，而不是只做架构目录。其 GitHub 清单也适合追溯经典工作，如 Generative Agents、Reflexion、MemGPT 和 Voyager。

**局限**：时间较早，尚未覆盖 2025-2026 大量 RL memory manager、on-policy benchmark、端侧 personal memory 和多 agent privacy；taxonomy 偏静态，难表达 memory 如何持续演化；对过程级错误诊断不足。

**对我们的用途**：用作历史背景和概念起点，不用它单独支撑最新 gap。引言可引用它说明 memory 已被视为 agent 长期交互的基础组件。

## 2. Rethinking Memory in AI: Taxonomy, Operations, Topics, and Future Directions

**出处**：arXiv 2025；[论文](https://arxiv.org/abs/2505.00675)；[资源](https://github.com/Elvin-Yiming-Du/Survey_Memory_in_AI)。

**要解决的问题**：旧 taxonomy 常按长期/短期或应用场景分类，却忽视让 memory 发生变化的原子操作，导致不同系统难以逐模块比较。

**组织方式**：先按 representation 将 memory 分为 parametric、contextual structured 和 contextual unstructured；再提出六个基础操作：Consolidation、Updating、Indexing、Forgetting、Retrieval、Compression；随后把这些操作映射到 long-term、long-context、parametric modification 和 multi-source memory 等主题。

**贡献**：这是当前 benchmark schema 最直接的理论来源，因为 operation 可以变成事件级标签、API 或 metric。它让“图还是向量库”不再是唯一比较轴，而是追问系统在哪些操作上有能力、以什么表示执行、产生什么代价。

**局限**：六操作仍偏系统实现视角，缺少 `IGNORE/PROTECT/USE/ABSTAIN` 等与任务和安全直接关联的决策；综述覆盖范围扩到一般 AI memory，agentic action 与多 session 用户状态并非唯一主线；操作之间的因果依赖没有形成统一评测协议。

**对我们的用途**：将其六操作与 benchmark 任务对齐，但不机械照搬。我们的 v1 标签可定义 `ADD/UPDATE/IGNORE/PROTECT` 为写入侧决策，`RETRIEVE` 为候选排序，`USE/ABSTAIN` 为消费侧决策；consolidation/indexing/compression 作为 backend 内部操作与成本指标。

## 3. Memory in the Age of AI Agents

**出处**：arXiv 2025；[论文](https://arxiv.org/abs/2512.13564)。

**要解决的问题**：agent memory 概念快速膨胀，和 LLM memory、RAG、context engineering 互相混用，传统 long/short-term 分类无法覆盖现代系统。

**组织方式**：从 forms、functions、dynamics 三个视角统一领域。forms 包括 token-level、parametric、latent；functions 区分 factual、experiential、working memory；dynamics 讨论形成、演化和检索。论文还汇总 benchmark 与开源框架，并把 memory automation、RL integration、multimodal、multi-agent 和 trustworthiness 列为前沿。

**贡献**：它明确说明“memory”不应由存储介质定义。同一向量库可能承载事实或经验，同一 token state 可能是 working memory；因此 benchmark 应按功能和任务目标分 track，再把不同 form 当参赛实现。

**局限**：覆盖极广，许多类别在实证上难直接横向比较；形式、功能与动态的组合空间很大，但没有给每个组合统一实例协议；最新 benchmark 的 process supervision 仍在快速变化。

**对我们的用途**：确立三 track：personal factual/episodic、procedural/experiential、working/context。第一版主做前者，保留程序性扩展，不把 MEM1、Mem^p 与 LoCoMo 类系统强行排在同一总榜。

## 4. Rethinking Memory Mechanisms of Foundation Agents in the Second Half

**出处**：arXiv 2026；[论文](https://arxiv.org/abs/2602.06052)。

**要解决的问题**：当 agent 研究从模型能力展示转向真实 utility，memory 如何在长时、动态、用户依赖的环境中成为可学习的系统能力？

**组织方式**：用三维框架描述 foundation agent memory：substrate 分 internal/external；cognitive mechanism 分 episodic、semantic、sensory、working、procedural；subject 分 agent-centric 与 user-centric。论文进一步讨论不同 agent topology 下的 memory、操作学习策略、benchmark 与指标。

**贡献**：比纯系统 taxonomy 更靠近“谁的记忆、用于什么任务、如何学习”。尤其 agent-centric/user-centric 的区分能解释为什么 WebArena 经验复用与个性化对话不能共享全部指标；topology 维度也把 multi-agent memory 安全纳入主框架。

**局限**：作为宏观综述，操作学习与 benchmark 仍是分类级整合，无法替代具体数据协议；“second half”是研究愿景，真实用户效用、隐私同意和长期部署仍缺少大规模可复现证据。

**对我们的用途**：用于限定 benchmark subject。第一版选择 user-centric factual/episodic memory + 单 agent，避免 scope 爆炸；第二阶段再扩 agent-centric procedural memory 或 multi-agent sharing。

## 5. From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2605.06716)；[资源](https://github.com/FeishuLuo/Evolving-LLM-Agent-Memory-Survey)。

**要解决的问题**：以往综述像“静态地图”，不能解释 memory 为什么从保存轨迹演化到反思，再演化为可泛化经验。

**组织方式**：以信息抽象层级定义 Storage、Reflection、Experience 三阶段。Storage 保留 raw trajectory；Reflection 在单条轨迹内部做精炼；Experience 跨轨迹归纳通用知识。论文用长期一致性、动态环境和持续学习三种 selection pressure 解释阶段跃迁，并重点讨论 active exploration 与 cross-trajectory abstraction。

**贡献**：它把 memory 的价值从“保真存储”推进到“形成可复用经验”，并用 Minimum Description Length 的视角解释为什么高质量 memory 应比原始轨迹短、但保留能指导行为的规律。该演化叙事对第二阶段 method 很有用。

**局限**：真实系统常混合三阶段，严格分期可能过度理想化；缺少跨阶段定量比较；Experience 文献较新，存在 recency bias；没有系统整理每次演化新引入的 failure mode，例如过度抽象和错误规则迁移。

**对我们的用途**：benchmark 不只要测“是否压缩”，还要测 fidelity-generalization trade-off。程序性 track 应构造近似任务与关键约束变化，检查经验抽象究竟迁移还是负迁移。

## 6. Towards Agentic RAG with Deep Reasoning: A Survey of RAG-Reasoning Systems in LLMs

**出处**：arXiv 2025；[论文](https://arxiv.org/abs/2507.09477)；[资源](https://github.com/DavidZWZ/Awesome-RAG-Reasoning)。

**要解决的问题**：普通 retrieve-then-generate 难完成多步推理，纯 reasoning 又容易缺事实或幻觉；怎样统一检索增强推理与推理增强检索？

**组织方式**：分为 Reasoning-Enhanced RAG、RAG-Enhanced Reasoning 与 Synergized RAG-Reasoning。最后一类让 agent 在多轮中交替规划、搜索、阅读、修正和停止，是 agentic RAG 的核心形态。

**贡献**：为 agent memory 和 RAG 划出关系：RAG 多处理当前 query 的外部知识，memory 还承担跨任务状态、用户经验和历史行为；二者在主动多步检索与 evidence use 上共享技术模块。

**局限**：主体仍是 knowledge-intensive reasoning，不系统讨论长期写入、偏好更新、遗忘和权限；很多 benchmark 是无持久状态的 QA，不能直接代表 memory management。

**对我们的用途**：第二阶段可把 learned retriever/reader 设计连接到 agentic RAG，但第一阶段问题定义必须坚持“跨 session 状态如何形成和演化”，否则会退化成另一套 RAG 检索 benchmark。

## 补充锚点：MobileMem

**出处**：2026 Technical Report；[论文](https://arxiv.org/abs/2608.13606)；[代码](https://github.com/zjunlp/MobileMem)。

MobileMem 不是综述，但代表近期 benchmark 的规模与现实性上界。它用 knowledge-grounded synthesis 构造一年尺度、时间一致的 mobile experience，覆盖 Calendar、Notes、Documents、To-Do、照片、录音、浏览与截图等来源，并提供文本和多模态设置。任务包含 multi-hop、temporal reasoning、knowledge update、implicit preference 与 abstention，目标是让 agent remember the past、understand the present、adapt to the future。

它证明真实 personal memory 应长期、多源、动态和个人化，也提醒我们不要在规模或移动生态上正面竞争。其主要输出仍是 end-to-end QA/response；我们可将相同类型的 event stream 缩小到纯文本、可人工核验的 operation trace，以诊断性而非规模形成区分。

## Taxonomy 对齐

| 维度 | 可选值 | 在 benchmark 中的角色 |
|---|---|---|
| Form | token / parametric / latent / structured external / unstructured external | 系统实现变量，不作为 gold 假设 |
| Function | factual / episodic / experiential / procedural / working | 分 track，避免错误总排名 |
| Subject | user-centric / agent-centric / shared | 定义信息所有者和权限 |
| Lifecycle | form / evolve / retrieve / consume / forget | 组织 episode 时间线 |
| Atomic operation | ADD / UPDATE / IGNORE / PROTECT / RETRIEVE / USE / ABSTAIN | 可逐步标注和评分 |
| Evidence role | required / supportive / irrelevant / stale / forbidden | 构造 hard negative 与消费侧评价 |

## 综述后的核心判断

1. “memory 是哪种数据库”不是一个稳的问题定义；同一功能可以用不同 form 实现。
2. “factual、experiential、working memory”不应混在一张榜单；它们的成功标准不同。
3. 六类经典 operation 需要补入 task-facing 的 `IGNORE/PROTECT/USE/ABSTAIN`，才能覆盖战略使用和安全。
4. benchmark 的价值不只是给总分，而是产生可复用的 failure profile，指导下一篇方法究竟优化什么。
5. 第一版应缩小到 user-centric factual/episodic memory，但在 schema 中保留 source、authority、visibility、version 和 provenance，为后续扩展留接口。
