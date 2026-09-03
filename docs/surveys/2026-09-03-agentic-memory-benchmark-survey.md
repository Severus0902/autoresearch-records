---
title: "Agentic Memory Benchmark Survey"
type: survey
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agentic-memory", "agentic-rag", "memory", "benchmark", "survey"]
---

# Agentic Memory / Agent Memory Benchmark 调研综述

## 方向切换判断

当前建议从 KG-constrained KGR 切到 agentic memory benchmark。原因很直接：KG 场景的约束太强，实验竞争往往落在图谱检索、路径推理、Freebase/CWQ/WebQSP 复现细节和大模型推理策略上；在最多 4 卡 4090 的条件下，很难靠训练规模或 KG 资源优势打出明显差异。相比之下，agent memory 更适合做 benchmark、framework 和 evaluation protocol，核心贡献可以不依赖大规模训练。

新的主线可以定义为：

> 评估 LLM agent 是否能在跨 session、多轮任务、事实更新、冲突记忆、用户偏好和工具调用场景中正确写入、检索、更新、遗忘和使用 memory。

这条线可以自然连接 Agentic RAG：普通 RAG 多数是 single-query retrieval-then-answer，而 agentic RAG 需要在多步任务中反复检索、写入状态、使用历史经验并处理环境反馈。memory 不是“更长上下文”的替代品，而是 agent 在长期交互中维护状态和经验的外部机制。

## 关键综述

### A Survey on the Memory Mechanism of LLM-based Agents

出处：arXiv 2024。

这篇是早期系统综述，重点回答 memory 在 LLM agent 中是什么、为什么需要、如何设计和如何评估。它指出已有 memory mechanism 分散在不同论文里，缺少统一整理和抽象设计模式。对我们有用的是：可以作为 taxonomy 起点，但它偏 survey，不够 benchmark-driven。

链接：https://arxiv.org/abs/2404.13501

### Rethinking Memory in LLM based Agents

出处：arXiv 2025。

这篇比早期综述更操作化，把 memory 分成 parametric 和 contextual 两类，并明确提出 memory 的六个核心操作：consolidation、updating、indexing、forgetting、retrieval、condensation。这对我们定义 benchmark task 很有价值，因为 benchmark 不应该只测 retrieval recall，而应该分解为可评估操作。

链接：https://arxiv.org/abs/2505.00675

### Memory in the Age of AI Agents

出处：arXiv 2025/2026。

这篇更新，强调 agent memory 领域已经碎片化，并区分 agent memory、LLM memory、RAG 和 context engineering。它从 forms、functions、dynamics 三个角度组织 memory，并把 factual、experiential、working memory 作为功能维度。对我们最有用的是：它明确把 benchmark 和 open-source frameworks 当成重要组成部分，说明 benchmark 方向是合理切入点。

链接：https://arxiv.org/abs/2512.13564

### Towards Agentic RAG with Deep Reasoning

出处：arXiv 2025，submitted to ARR May。

这篇不是 memory 专属综述，但它把 RAG 和 reasoning 结合起来，强调普通 RAG 对 multi-step inference 不足，agentic RAG 会把 search 和 reasoning 交替执行。我们可以用它连接“memory benchmark”和“agentic RAG benchmark”：memory 是长期、多步、跨任务检索和状态维护的基础设施。

链接：https://arxiv.org/abs/2507.09477

## Benchmark 相关工作

### LoCoMo

全称：Evaluating Very Long-Term Conversational Memory of LLM Agents。

出处：ACL 2024 Long Papers。

LoCoMo 是长期对话 memory 的重要基准，构造了多 session、长对话、多模态元素和事件图支撑的对话数据。它评估 QA、event summarization 和 multi-modal dialogue generation。它的意义是把 memory 从短上下文扩展到 very long-term conversation；不足是偏对话回忆和理解，不完全覆盖 agent 在环境中行动后的 memory update/use。

链接：https://aclanthology.org/2024.acl-long.747/
代码：https://github.com/snap-research/locomo

### LongMemEval

出处：ICLR 2025。

LongMemEval 针对 chat assistant 的 long-term interactive memory，评估 information extraction、multi-session reasoning、temporal reasoning、knowledge updates 和 abstention。它很适合作为我们的 baseline benchmark，因为它已经把 memory 设计拆成 indexing、retrieval、reading 三阶段。

链接：https://arxiv.org/abs/2410.10813
代码：https://github.com/xiaowu0162/LongMemEval

### MemoryAgentBench

出处：GitHub 标注为 ICLR 2026 Paper；arXiv 2025/2026。

MemoryAgentBench 明确提出 memory agent，并把核心能力定义成 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting。它指出现有 benchmark 要么依赖有限上下文，要么偏静态长文本 QA，不能反映 memory agent 逐轮积累信息的交互过程。这篇非常贴近我们要做的方向，是必须精读的 benchmark。

链接：https://arxiv.org/abs/2507.05257
代码：https://github.com/HUST-AI-HYZ/MemoryAgentBench

### MemoryBench

出处：arXiv 2025/2026。

MemoryBench 关注 LLM system 从用户反馈中进行 memory 和 continual learning 的能力，覆盖多领域、多语言、多任务。它的切入点不是“长期聊天记录里找答案”，而是服务过程中累积反馈并持续优化。这对我们很关键：benchmark 可以从 memory retrieval 扩展到 feedback-conditioned adaptation。

链接：https://arxiv.org/abs/2510.17281
代码：https://github.com/THUIR/MemoryBench

### StratMem-Bench

全称：StratMem-Bench: Evaluating Strategic Memory Use in Virtual Character Conversation Beyond Factual Recall。

出处：ACL 2026 Long Papers。

StratMem-Bench 的 memory 定义很值得借鉴：它不是把 memory 只看作“事实回忆库”，而是把 memory 视为虚拟角色对话生成时可选择、可整合、也可能应忽略的候选信息池。数据中每个样本包含 user query、virtual character persona、candidate memories，其中 memory 被分成三类：`must`、`nice` 和 `irr`。`must` 是回答必须使用的关键信息，`nice` 是可提升回答质量的支持性信息，`irr` 是不相关信息。推理时这些标签不暴露给模型，模型需要自己判断哪些 memory 应该被用、哪些应该忽略。

它对我们当前 benchmark 方向的启发是：memory evaluation 不应只看 factual recall，而应看 strategic use，即模型能否区分必要记忆、辅助记忆和噪声记忆，并把记忆自然整合进后续响应。它仍然是 single-turn dialogue generation benchmark，尚未覆盖完整的 memory write/update/delete lifecycle，因此可以作为我们 proposal 中“memory use / memory selection”维度的重要前置工作。

链接：https://aclanthology.org/2026.acl-long.1491/
代码：https://github.com/seucoin/StratMem-Bench

### MobileMem

全称：MobileMem: Learning from a Year of Mobile Experiences。

出处：arXiv 2026 technical report。

MobileMem 是近期非常值得参考的 on-device personal memory benchmark。它把 memory 场景从对话历史扩展到手机端长期用户经验，覆盖 Calendar、Photos、Notes、Documents、To-Do List、Voice Recorder、Breeno Memory、Video Memo、浏览和截图等多源数据。它提出 KEME 数据合成流程，用 user prior knowledge、temporal event graph 和 user-app trajectory synthesis 构造一年尺度、时间一致的用户轨迹。

MobileMem 提供文本和多模态两个设置：`MobileMem` 关注应用通过模板向系统级 memory layer 发送 structured memory event；`MobileMem-Omni` 关注应用不直接接入 memory layer 时，用户通过截图分享重要交互。任务覆盖 single-hop、multi-hop、temporal reasoning、knowledge update、implicit preference、abstention、visual reasoning 等。它对我们的启发是：agent memory benchmark 要走向长期、个人化、多源和部署受限；但它主要还是 end-to-end QA 评测，缺少对每条 memory 是否该写、该改、该取、该用、该忽略、该保护的过程级监督。

链接：https://arxiv.org/abs/2608.13606
代码：https://github.com/zjunlp/MobileMem

### MemoryArena

出处：arXiv 2026。

MemoryArena 直接指出已有评测常把 memorization 和 action 分开测，而真实 agentic 场景里 memory 和 action 是耦合的：agent 在环境交互中获得 memory，再用 memory 指导后续动作。它覆盖 web navigation、preference-constrained planning、progressive information search 和 sequential formal reasoning。它是目前最贴近“agentic memory benchmark”的工作之一。

链接：https://arxiv.org/abs/2602.16313

### MemArena

出处：arXiv 2026。

MemArena 是 ego-centric/on-device personal memory assistant benchmark，强调私有交互、设备端开源模型、多 session coherent world、权限意识和 trustworthiness。它的价值是把 memory benchmark 带到隐私、权限和端侧限制，这和 4 卡 4090 的资源条件也更契合。

链接：https://arxiv.org/abs/2608.02613

### BEAM

全称：Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs。

出处：arXiv 2025/2026。

BEAM 自动生成最长到千万 token 的 coherent conversations，并用 probing questions 覆盖更广 memory abilities。它说明即使 1M context LLM 加 RAG，在对话变长时仍会困难。对我们来说，它可以支撑一个观点：benchmark 不能只靠“长上下文能力”定义 memory，要评估 memory system 的结构化选择与更新。

链接：https://arxiv.org/abs/2510.27246

### PersonaMem

出处：COLM 2025。

PersonaMem 聚焦 dynamic user profiling 和 personalized responses，包含多 session 用户历史、动态偏好演化和个性化响应选择。它更偏 personalization benchmark，但非常适合纳入我们 benchmark 的用户偏好、偏好更新、响应一致性和冲突偏好子任务。

链接：https://arxiv.org/abs/2504.14225
代码：https://github.com/bowen-upenn/PersonaMem

## Framework / Method 相关工作

### Generative Agents

出处：UIST 2023 / arXiv 2023。

Generative Agents 提出了 observation、planning、reflection 组成的 agent architecture，用自然语言记录 agent experiences，并随时间综合为 reflection，再动态检索用于行为规划。这是 agent memory 的经典起点之一，但更偏仿真系统和行为可信度。

链接：https://arxiv.org/abs/2304.03442

### MemGPT / Letta

出处：arXiv 2023/2024。

MemGPT 把 memory 设计成类似操作系统的 virtual context management，在有限上下文窗口内管理不同 memory tiers。Letta 是它后续开源平台方向，定位为 stateful agents with advanced memory。它适合作为 framework baseline。

论文：https://arxiv.org/abs/2310.08560
代码：https://github.com/letta-ai/letta

### A-MEM

出处：NeurIPS 2025。

A-MEM 强调 agentic memory organization，借鉴 Zettelkasten，把 memory 写成带 context、keywords、tags 的结构化 note，并自动建立 memory links 和更新历史 memory 表征。它适合作为 memory organization baseline。

链接：https://arxiv.org/abs/2502.12110

### MemoryOS

出处：arXiv 2025。

MemoryOS 用操作系统类比设计短期、中期、长期 personal memory，并分成 storage、updating、retrieval、generation 四个模块。它在 LoCoMo 上报告提升，适合作为 hierarchical memory baseline。

链接：https://arxiv.org/abs/2506.06326

### MIRIX

出处：arXiv 2025。

MIRIX 是 multi-agent memory system，把 memory 分成 Core、Episodic、Semantic、Procedural、Resource、Knowledge Vault 六类，并用多 agent 协调更新和检索。它还覆盖 multimodal/screen activity 场景。它适合作为 framework 类对照，尤其是结构化 memory 类型和 memory manager routing。

链接：https://arxiv.org/abs/2507.07957
代码：https://github.com/Mirix-AI/MIRIX

### Memory-R1

出处：arXiv 2025/2026。

Memory-R1 是少数直接把 RL 用到 memory management 的工作，训练 Memory Manager 学 ADD、UPDATE、DELETE、NOOP，Answer Agent 选择相关 memory 并推理，使用 PPO/GRPO。虽然你当前不打算优先训练，但这篇能作为“训练型 memory agent”的边界参照。

链接：https://arxiv.org/abs/2508.19828

## 当前 Gap

Paper-Notes 的 2025-2026 扫描显示，不能再笼统声称“现有 benchmark 缺少过程级 memory evaluation”：AMemGym 已经诊断 `write / read / utilization`，Memora 已经覆盖高频 memory mutation 和 forgetting-aware evaluation，MemoryAgentBench 已覆盖 incremental retrieval、test-time learning、long-range understanding 和 selective forgetting，MEMTRACK 也进入了跨平台动态状态追踪。

因此，新的 research gap 应强调 **评测维度碎片化，以及缺少统一的逐操作 ground truth 和因果诊断协议**：

> 近期 benchmark 已分别覆盖策略性记忆使用、write/read/utilization 失败诊断、面向 mutation 的遗忘、增量记忆能力和跨平台状态追踪，但这些维度分散在不兼容的场景与协议中，并且多数仍通过最终响应或粗粒度归因进行评估。当前仍缺少一个统一的 multi-session benchmark：为每一步提供显式的 memory operation ground truth，并把 agent 应该写入、更新、忽略、检索、保护和使用的记忆，与后续回答或行动结果建立可核验的因果链。

在实现上，可以用 `ADD / UPDATE / IGNORE / PROTECT` 标注写入侧操作，用 `required / supportive / irrelevant / stale / forbidden` 标注读取与使用侧角色，再通过 oracle-write、oracle-retrieval、oracle-use 等受控设置区分 backend、retriever 和 reader/actor 的责任。这个 gap 不要求通过大规模训练打败 SOTA，适合先做 benchmark 和 evaluation suite，后续再加 memory framework 或轻量 policy。

## 建议切入点

优先做 benchmark，而不是 method-first：

1. 先复现/跑通 LongMemEval、MobileMem、MemoryAgentBench 中至少一个轻量子集。
2. 梳理这些 benchmark 没覆盖好的维度：memory write correctness、memory update under contradiction、permission-aware retrieval、experience-to-action transfer、noise injection、cross-session preference drift、abstention under insufficient evidence。
3. 构造一个轻量 benchmark：不追求超大规模，追求任务定义清楚、可自动评测、能对比多种 memory backend。
4. Baseline 先用 API 模型或本地 7B/8B reader + 多种 memory backend，不做训练。
5. 论文故事先定位为 evaluation + benchmark + framework analysis。

## 最小可行 benchmark 设想

临时名称：`MemoAgentBench-Lite`。

任务单元：

- `session_stream`：跨 session 的对话、工具结果或事件流。
- `memory_ops`：期望系统写入、更新、删除、忽略的 memory 操作。
- `query`：后续任务或问题。
- `required_memory`：正确作答所需的 memory evidence。
- `forbidden_memory`：不应使用的过期、无关或无权限 memory。
- `answer` 或 `action`：最终响应或动作。

评估维度：

- Memory write F1：是否写入该写的内容。
- Update accuracy：旧事实是否被新事实覆盖。
- Selective forgetting：应遗忘或过期内容是否被忽略。
- Retrieval precision/recall：取出的 memory 是否完整且不污染。
- Answer/action success：最终任务是否成功。
- Grounding faithfulness：回答是否引用了正确 memory。
- Privacy/permission compliance：是否泄露无权限 memory。
- Efficiency：token、latency、storage。

Baseline：

- no memory。
- full history。
- BM25/vector RAG memory。
- summary memory。
- structured JSON memory。
- Letta/MemGPT-style memory。
- Mem0。
- A-MEM-style linked note memory。
- MIRIX-style typed memory。

## 当前优先级

第一优先级：写 benchmark proposal 和 schema，先不要训练。

第二优先级：选择一个已有 benchmark 跑通最小评测，推荐顺序为：

1. LongMemEval：协议清楚，ICLR 2025，适合 memory retrieval/reading pipeline。
2. MobileMem：最贴 on-device/personal memory benchmark，可以优先参考数据合成、任务类型和 baseline。
3. MemoryAgentBench：最贴 agent memory，但需要先看数据构造成本。
4. LoCoMo：经典且引用价值高，但偏长对话。
5. PersonaMem：适合补 personalization/dynamic preference 子任务。
6. MemoryArena：非常贴 agentic，但 2026 新工作，需看代码/数据可用性。

第三优先级：再决定是否做 `MemoAgentBench-Lite` 的自定义数据集。
