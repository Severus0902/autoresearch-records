---
title: "从 StratMem-Bench 切入 Agentic Memory Benchmark 的研究方案"
type: idea
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agentic-memory", "memory-benchmark", "strategic-memory-use", "agentic-rag", "stratmem"]
---

# 从 StratMem-Bench 切入 Agentic Memory Benchmark 的研究方案

## 一句话问题定义

现有 memory benchmark 还难以回答一个更 agentic 的问题：智能体在跨 session 的动态任务中，是否能决定什么应该被写入、更新、检索、忽略、保护，并把这些 memory 正确用于后续回答或行动。

## 推荐切入点

建议从组内 ACL 2026 文章 StratMem-Bench 出发，但不要继续只做“给定候选记忆后的单轮回复生成”。更顺的切入是：

> 从 strategic memory use 扩展到 agentic memory lifecycle evaluation。

也就是说，继承 StratMem-Bench 的 `must / nice / irrelevant` 记忆使用视角，再进一步评测 agent 在多轮、多 session、多工具任务里是否能完成 `write / update / retrieve / ignore / use / protect` 的完整记忆闭环。

这个方向比继续做 KG 更适合当前资源条件：它不依赖大规模训练，也不需要在 Freebase/CWQ/WebQSP 这种强约束管线里卷检索和路径推理；更容易做成 benchmark、数据集、评测协议或轻量 framework。

## 和 StratMem-Bench 的关系

StratMem-Bench 的核心贡献是把 memory 从“事实召回库”推进到“策略性使用对象”：同一个 query 下，候选 memory 里有必须使用的 `must`、可增强回答的 `nice`、应该忽略的 `irrelevant`。模型要做的不是把所有记忆塞进回答，而是判断哪些记忆对当前回复真正有用。

可以继承的部分：

- 记忆不是越多越好，而是需要选择性使用。
- 记忆类型可以带有明确监督标签，例如 required/supportive/irrelevant。
- 评测不能只看最终文本质量，还要看是否用了该用的记忆、是否误用了不该用的记忆。

可以扩展的 gap：

- StratMem-Bench 主要是给定候选 memory 的 single-turn response generation，还没有覆盖 memory 如何产生。
- 它强调 memory use，但没有完整评测 memory write、update、delete/forget、permission control。
- 它主要面向虚拟角色对话，agentic RAG 或真实助手任务中的工具结果、历史经验、用户偏好和权限边界还没有充分建模。

因此新工作的定位可以写成：

> StratMem-Bench evaluates whether models can strategically use provided memories; we study whether agents can strategically manage and use memories across multi-session tasks.

## 前期工作脉络

| 类别 | 代表工作 | 方法/对象 | 对我们的启发 | 主要不足 |
| --- | --- | --- | --- | --- |
| 综述 | Memory in the Age of AI Agents; Rethinking Memory in LLM-based Agents; Memory for Autonomous LLM Agents | 从 memory forms、functions、operations、management 等角度建立 taxonomy | 说明 memory 已经从 RAG 附件变成 agent 基础设施 | 多为 taxonomy，不直接给出可复现实验闭环 |
| 对话长期记忆 | LoCoMo; LongMemEval | 长对话、多 session QA、时间推理、知识更新 | 可作为 long-term conversational memory 的强 baseline | 仍偏“历史中找答案”，agentic action 较弱 |
| 策略性记忆使用 | StratMem-Bench | `must / nice / irrelevant` 候选记忆选择与回复生成 | 是最适合继承的直接起点 | 记忆池是给定的，缺少 memory lifecycle |
| Agent memory benchmark | MemoryAgentBench; MemoryArena; MemArena | 增量交互、多 session agent 任务、个人 memory assistant | 证明 benchmark 化方向是合理的 | 需要进一步看是否充分拆解 use/update/protect 等组件 |
| 记忆框架 | Generative Agents; MemGPT/Letta; A-MEM; MemoryOS; MIRIX | observation/reflection、虚拟上下文、结构化 note、分层记忆、多 agent memory manager | 适合作为 framework baseline | 各框架接口差异大，统一评测成本高 |
| 训练型方法 | Memory-R1; AgeMem; GAM; AutoMem | 把 memory operation 或 memory policy 训练成可学习技能 | 可作为后续 method 扩展 | 初期不适合作为主线，训练成本和变量太多 |

## 可以解决的问题

这篇新工作要解决的不是“模型能不能记住一个事实”，而是下面这个更具体的问题：

> 当一个 agent 在多个 session 中不断接收用户偏好、工具结果、任务反馈和冲突信息时，现有 memory systems 是否能稳定地区分该记、该改、该取、该用和该忽略的信息？

它可以拆成六个子问题：

- `write`：哪些信息值得写入长期记忆？
- `update`：新事实和旧事实冲突时，是否能正确覆盖或保留版本？
- `retrieve`：当前任务需要哪些历史记忆？
- `ignore`：相似但无关、过期、误导性的 memory 是否被过滤？
- `use`：最终回答/行动是否真正利用了正确记忆？
- `protect`：隐私、权限、用户边界相关 memory 是否被错误泄露或跨域使用？

## 为什么用 benchmark/evaluation 方法

第一，资源匹配。4 卡 4090 很难在训练型 memory agent 上和大组硬碰硬，但完全足够跑开源 7B/8B reader、embedding/reranker、BM25/vector/summary/structured memory baselines。

第二，贡献更清晰。Memory 领域现在方法很多，但评测仍然碎片化。做 benchmark 可以先定义问题边界、任务 schema、指标和 baseline，再决定是否需要训练方法。

第三，和组内 ACL 工作承接自然。StratMem-Bench 已经证明“memory use 不等于 factual recall”，新工作可以顺势说：下一步不是只看给定候选记忆的策略性使用，而是看 agent 是否能在完整生命周期中管理并使用记忆。

第四，可扩展。初版可以做 100-500 条高质量 pilot；后续可以扩展到更多 domain、更多 memory backend，或加入轻量 memory gate / reranker / policy learning。

## 初版方案：StratMem-AgentBench

临时命名：`StratMem-AgentBench` 或 `MemoAgentBench-Lite`。

每条样本由三部分组成：

- `episodes`：跨 session 的对话、工具结果、用户反馈、环境事件。
- `memory_supervision`：期望的 add/update/delete/noop 操作，以及 required/supportive/irrelevant/forbidden memory 标签。
- `eval_task`：后续查询、回答或行动任务，要求 agent 使用正确 memory 并避免错误 memory。

推荐任务域：

- personal assistant：日程、旅行、购物、偏好管理。
- research assistant：论文阅读、idea 记录、实验状态、引用偏好。
- coding assistant：项目约定、bug 修复经验、代码风格、失败命令记录。
- enterprise assistant：权限隔离、团队知识、跨用户信息边界。

推荐 baseline：

- `NoMemory`：只看当前 query。
- `FullHistory`：全部历史塞进上下文，作为高成本强基线。
- `BM25Memory`：文本检索。
- `VectorMemory`：embedding 检索。
- `SummaryMemory`：session 摘要。
- `StructuredMemory`：JSON profile/facts/preferences。
- `HybridMemory`：structured filter + vector retrieval + summary。
- `FrameworkBaseline`：选择 Mem0、Letta/MemGPT、A-MEM 或 MIRIX 中 1-2 个可跑的系统。

推荐指标：

- `memory_write_f1`：该写的信息是否写入。
- `update_accuracy`：冲突信息是否被正确更新。
- `retrieval_recall`：required memory 是否被取出。
- `retrieval_precision`：irrelevant/expired memory 是否被排除。
- `strategic_use_score`：must 是否使用、nice 是否合理使用、irrelevant 是否未使用。
- `answer_success`：最终任务是否成功。
- `permission_violation_rate`：是否误用 forbidden/private memory。
- `cost`：token、latency、存储量。

## 写作故事线

可以参考 StratMem-Bench 的写法，但把 narrative 往 agentic lifecycle 上推一步。

摘要/引言可以按下面逻辑展开：

1. LLM agents 越来越依赖 memory 维持长期交互能力，但 memory 不只是长上下文或 RAG 检索。
2. 组内 StratMem-Bench 已经指出，高质量 memory use 需要区分必须使用、可选增强和应忽略的信息。
3. 真实 agent 场景里，memory 不是预先给定的候选池，而是在多 session 交互中持续写入、更新、检索、过滤和使用。
4. 现有 benchmark 要么偏长期对话 QA，要么偏单轮候选 memory 使用，要么偏框架演示，缺少统一评测 agentic memory lifecycle 的协议。
5. 因此我们提出一个轻量、可扩展、backend-agnostic 的 benchmark，用于评测 agent 是否能在动态任务中策略性管理和使用 memory。

一句话 motivation 可以写成：

> From strategic memory use to strategic memory management: evaluating whether LLM agents can not only select useful memories, but also maintain, update, protect, and apply them across sessions.

## 难点和风险

- 数据构造难：样本既要有真实感，又要能自动评测，不能退化成模板填空。
- 指标可信度难：最终回答质量需要 LLM judge，但 memory 使用/泄露最好尽量规则化，避免 judge bias。
- 和已有 benchmark 的边界难：必须明确相对 LoCoMo、LongMemEval、MemoryAgentBench、MemoryArena、StratMem-Bench 的差异。
- 长上下文混淆难：FullHistory 可能在小数据上表现很强，需要通过成本、噪声、权限、过期信息来体现 memory system 的价值。
- 隐私/权限设计难：forbidden memory 任务要可控，不能做成纯安全红队，也不能太弱。
- Framework baseline 工程难：MemGPT/Letta、A-MEM、MIRIX 等系统接口不统一，第一版要控制 baseline 数量。
- 合成数据偏差难：如果完全用 LLM 生成任务，模型可能适应模板。需要人工审核、domain 多样化和 hard negatives。

## 最小执行路线

第一阶段：复现和对齐。

- 精读 StratMem-Bench，抽取它的 memory 类型、数据格式和指标设计。
- 跑通 LongMemEval 或 LoCoMo 的最小评测流程，理解长期记忆 benchmark 的工程形式。
- 看 MemoryAgentBench/MemoryArena 的数据 schema，确认 agentic multi-session task 的已有边界。

第二阶段：构造 pilot。

- 先做 50 条样本，覆盖 4 个 domain，每条 3-5 个 session。
- 每条样本标注 expected memory ops、required/supportive/irrelevant/forbidden memory。
- 保证每条样本都有 hard negatives，例如相似偏好、过期事实、错误工具结果、权限不匹配信息。

第三阶段：跑 baseline。

- 先跑 `NoMemory / FullHistory / BM25 / Vector / Summary / Structured`。
- Reader 模型先用 Qwen2.5-7B 或 Llama-3-8B，本地可控。
- 评测先用 rule-based + LLM judge hybrid。

第四阶段：判断是否需要方法创新。

- 如果主要错误来自 retrieval，可以加 memory reranker。
- 如果主要错误来自 write/update，可以加 memory operation classifier。
- 如果主要错误来自“该不该用”，可以继承 StratMem 的 strategic use，做 memory gate。
- 如果主要错误来自权限和噪声，可以转向 memory governance benchmark。

## 当前最建议的论文题目方向

- `StratMem-AgentBench: Evaluating Strategic Memory Management in Multi-Session LLM Agents`
- `Beyond Strategic Memory Use: Benchmarking the Memory Lifecycle of LLM Agents`
- `From Recall to Strategic Memory Management: A Benchmark for Agentic Memory Systems`

更推荐第二个题目。它最清楚地表达了和组内 ACL paper 的继承关系，同时不会被限制在 virtual character conversation 里。

## 参考链接

- StratMem-Bench, ACL 2026 Long Papers: https://aclanthology.org/2026.acl-long.1491/
- StratMem-Bench GitHub: https://github.com/seucoin/StratMem-Bench
- 2026 上半年 Agent Memory 研究全景: https://blog.coolgpu.cn/pages/2026-07-05-llm-agent-memory-research-2026.html
- Agent Memory 2026 下半年趋势预测: https://www.daoyuly.cn/2026/2026-07-02-agent-memory-h2-2026-outlook/
- LoCoMo, ACL 2024 Long Papers: https://aclanthology.org/2024.acl-long.747/
- LongMemEval, ICLR 2025: https://arxiv.org/abs/2410.10813
- MemoryAgentBench: https://arxiv.org/abs/2507.05257
- MemoryBench: https://arxiv.org/abs/2510.17281
- MemoryArena: https://arxiv.org/abs/2602.16313
- MemGPT: https://arxiv.org/abs/2310.08560
- A-MEM: https://arxiv.org/abs/2502.12110
- Memory-R1: https://arxiv.org/abs/2508.19828
