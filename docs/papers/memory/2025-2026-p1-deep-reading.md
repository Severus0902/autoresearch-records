---
title: "Agent Memory P1 论文精读"
type: literature-notes
status: reviewed
created: "2026-09-03"
tags: ["agent-memory", "method", "p1", "deep-reading"]
---

# P1：关键 Memory Method 精读

P1 论文回答“现有系统具体怎样写、组织、检索和学习 memory”。它们主要用于设计 baseline、生成可诊断 failure cases，并为第二阶段方法提供模块候选。

## 1. Memory-T1: Reinforcement Learning for Temporal Reasoning in Multi-session Agents

**出处**：ICLR 2026；[论文](https://openreview.net/forum?id=vQf2YR2Kpd)；[代码](https://github.com/Elvin-Yiming-Du/Memory-T1)。

**问题**：怎样从长而噪的多 session memory bank 中选择时间一致的证据，而不把答案错误、证据错误和时间解析错误混为一谈？

**方法**：先由模型预测 query 的时间窗口，再在窗口内用 BM25 产生候选 session；策略模型结构化输出证据 session 与答案。训练采用 GRPO，奖励由答案准确性、evidence grounding 和时间一致性组成，其中时间奖励同时考虑 session 距离与 utterance 的事件时间。细粒度标注仅用于训练 verifier，推理时不暴露。

**评测与发现**：Time-Dialog 上 3B/7B 模型达到约 67% 整体表现；候选生成开销低。论文的主要价值不是“用了 RL”，而是把 memory selection 变成可验证的显式动作，并为不同错误提供较密的监督。

**局限与启示**：时间窗口预测错会在检索前丢证据；标注成本高；session 粒度仍偏粗，timeline/comparison 类组合推理较弱。我们的 benchmark 可借鉴“答案 + grounding + operation”分层评分，但必须把更新和权限也纳入 trace。

## 2. MemSearcher: Training LLMs to Reason, Search and Manage Memory via End-to-End RL

**出处**：ACL 2026；[论文](https://arxiv.org/abs/2511.02805)；[代码](https://github.com/icip-cas/MemSearcher)。

**问题**：搜索 agent 如何在多轮检索时保持近常数上下文，同时学会保留有效证据和丢弃检索噪声？

**方法**：每轮输入只有 `(question, current memory)`；同一 LLM 生成 thought/action，接收 observation 后再覆写限定长度的自然语言 memory。由于各轮 context 不同，论文提出 multi-context GRPO：整条 trajectory 得到一个 final reward/advantage，再广播到轨迹内各轮，把每轮视作独立优化上下文。奖励主要是格式与最终答案 F1。

**评测与发现**：在多个 QA benchmark 上，3B/7B/14B 均优于同规模 ReAct，context 保持在 4K 内；这说明 selective forgetting 可以同时提高效果与效率。

**局限与启示**：覆写是破坏性的，早期丢失的信息不可恢复；没有显式 memory-quality reward，广播同一个 advantage 的信用分配仍粗；静态 Wiki 和 Qwen 系列限制了外推。它是第二阶段“trace-supervised writer”最直接的训练基线，也说明 benchmark 应提供 memory-state checkpoints，而不只提供 final answer。

## 3. R2D2: Remembering, Replaying and Dynamic Decision Making with a Reflective Agentic Memory

**出处**：ACL 2025；[论文](https://arxiv.org/abs/2501.12485)。

**问题**：网页 agent 能否把过去探索变成环境地图，并针对导航错误与执行错误采取不同修复机制？

**方法**：Remember 模块把历史网页状态和转移存成 replay graph，将 unknown MDP 转为可复用的 known MDP；新任务用 A* 搜索，LLM 提供语义启发值。Reflect 模块诊断执行失败、生成纠正反思，并把修复后的经验写回 memory。导航与执行两类失败被分治处理。

**评测与发现**：WebArena 上论文报告导航错误减半、完成率约提升三倍，并超过当时强基线。核心洞察是 memory 不只是事实库，也可以是可搜索的环境动力学。

**局限与启示**：冷启动需要先探索；网页变化会令图失效；A* 节点的 LLM 评估昂贵；只在模拟 WebArena 验证。它提示 benchmark 应区分 factual memory 和 environment/procedural memory，也应显式制造 stale transition，测试旧经验是否会误导动作。

## 4. In Prospect and Retrospect: Reflective Memory Management for Long-term Personalized Dialogue Agents

**出处**：ACL 2025；[论文](https://arxiv.org/abs/2503.08026)。

**问题**：长期对话中的写入粒度和检索策略怎样同时摆脱固定规则？

**方法**：RMM 包含 prospective reflection 与 retrospective reflection。前者在信息离开当前上下文前形成多粒度摘要，避免固定窗口切断语义；后者在回答时迭代调整检索，并使用回复中是否引用记忆作为弱监督奖励学习检索策略。

**评测与发现**：LongMemEval 上报告超过 10% 的准确率提升，说明写入组织和读取适配需要共同考虑，而不是只优化 embedding。

**局限与启示**：存储和检索仍未联合优化；“是否引用”不等价于“是否有用”，可能偏爱显眼或较长条目；缺少遗忘、容量与权限。我们的 evidence role 标签可为这种弱奖励提供更可靠的 benchmark ground truth。

## 5. A-MEM: Agentic Memory for LLM Agents

**出处**：NeurIPS 2025；[论文](https://arxiv.org/abs/2502.12110)；[代码](https://github.com/WujiangXu/AgenticMemory)。

**问题**：memory 能否像 Zettelkasten 一样自主生成索引、建立链接，并随着新信息持续演化，而不是写入后静态不变？

**方法**：每条交互被转成结构化 note，包含内容、关键词、标签和 contextual description；新 note 通过 embedding 召回近邻，再由 LLM 判断是否建立链接，以及是否更新已有 note 的表述和关系。查询时结合语义召回与 linked notes 形成上下文。

**评测与发现**：LoCoMo 上优于多种静态记忆基线。其贡献是把组织和演化都交给 agent，而非依赖固定 schema；链接使跨事件关联不必完全由单次 top-k 负责。

**局限与启示**：多次 LLM 调用带来成本和非确定性；错误链接或重写可能累积；没有清晰区分合法更新与信息污染；评测仍偏 QA。它应作为 linked-note baseline，并重点测错链、错误 merge 与不可追溯重写。

## 6. Agentic Plan Caching: Test-Time Memory for Fast and Cost-Efficient LLM Agents

**出处**：NeurIPS 2025；[论文](https://arxiv.org/abs/2506.14852)。

**问题**：怎样复用 agent 历史中的规划模式，减少每个新任务都调用大模型重新规划的成本？

**方法**：从成功执行日志中抽取去除具体上下文的计划模板与关键词；新 query 命中缓存后，由小模型把模板适配到当前数据和环境，再交给执行器。缓存单元从 query-response 升级为可复用 plan，并把通用意图与动态上下文分开。

**评测与发现**：论文报告平均降低 50.31% 成本、27.28% 延迟，同时保持 96.61% 的最优准确率。说明 procedural memory 的评价核心不仅是成功率，还包括复用率、适配成本和错误命中。

**局限与启示**：关键词匹配可能漏掉语义等价任务；只缓存成功计划，依赖可靠 success detector；模板遇到分布变化可能负迁移。benchmark 可加入“表面相似但约束不同”的 plan hard negatives，并测 false reuse。

## 7. Contextual Experience Replay for Self-Improvement of Language Agents

**出处**：ACL 2025；[论文](https://arxiv.org/abs/2506.06698)。

**问题**：语言 agent 能否在不更新参数的情况下，把过去任务轨迹提炼为环境经验并改善后续决策？

**方法**：CER 将轨迹累积到动态经验缓冲区，再由 LLM 合成为更短的环境知识和决策模式；执行新任务时检索相关经验放入上下文。它把 RL 的 experience replay 从参数更新迁移到 in-context adaptation。

**评测与发现**：WebArena 上相对 GPT-4o baseline 报告 51.0% 的成功率提升。分析强调“经验合成质量”比原样保留轨迹更重要，因为可迁移规则比冗长日志更易复用。

**局限与启示**：经验受上下文容量限制；合成错误会形成持久偏差；环境知识难跨网站迁移；额外 LLM 调用增加成本。我们应把“正确抽象”和“过度泛化”作为程序性 memory 的成对测试，而不是只看经验是否被检索。

## 8. TReMu: Towards Neuro-Symbolic Temporal Reasoning for LLM-Agents with Memory in Multi-Session Dialogues

**出处**：ACL 2025；[论文](https://arxiv.org/abs/2502.01630)。

**问题**：如何让长期对话 agent 对相对日期、事件顺序和时间间隔进行可靠计算，而不只依赖自然语言直觉？

**方法**：记忆化阶段把多 session 对话整理成时间线摘要，并将相对时间锚定到绝对时间；推理阶段让 LLM 生成 Python 程序执行日期计算和比较，再把结果用于回答，形成 neuro-symbolic temporal reasoning。

**评测与发现**：在基于 LoCoMo 构造的 600 道时间推理题上，笔记记录 GPT-4o 从 29.83% 提升至 77.67%。结果表明，memory representation 与外部确定性计算可以互补。

**局限与启示**：只评测多选 QA；依赖闭源 LLM；时间线摘要本身可能误推并级联；代码生成存在重试开销。benchmark 中时间答案应尽可能提供可执行 verifier，并分别评价事件抽取、时间归一化和最终推理。

## 9. Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents

**出处**：ICML 2026；[论文](https://arxiv.org/abs/2606.06036)；[代码](https://github.com/Ji-shuo/MRAgent)。

**问题**：一次性 top-k 或固定 n-hop 检索无法根据中间证据改变方向，怎样让记忆访问成为主动、可迭代的重构过程？

**方法**：MRAgent 构建 Cue-Tag-Content 关联图，tag 充当线索与内容之间的语义桥，并组织 episodic、semantic 与 topic 等粒度。查询时维护重构状态，模型可选择 tag、展开内容、由内容反向激活新线索、剪枝或停止，使推理与图访问交替进行。

**评测与发现**：LoCoMo/LongMemEval 上相对强基线最高提升约 23%，同时降低平均 token 与耗时。重点是检索轨迹会随中间证据变化，而不是图本身更大。

**局限与启示**：深层探索的最坏延迟高；建图、标签和路由均依赖 LLM；评测集中在对话 QA。它适合做 agentic retriever baseline，也启发我们记录 retrieval trace，而不只记录最终 evidence set。

## 10. AdaMEM: Test-Time Adaptive Memory for Language Agents

**出处**：ICML 2026；[论文](https://arxiv.org/abs/2606.05684)；[代码](https://github.com/yunx-z/AdaMEM)。

**问题**：为什么只在 episode 开始检索一次经验不够，怎样让 memory 随任务中间状态动态刷新？

**方法**：长期记忆保存成功原始轨迹；短期记忆在测试时依据当前 state 从轨迹中即时合成可执行策略。high setting 每步刷新，low setting 按需刷新。Step-MFT 只保留“加入策略后改变了下一动作”的训练样本，以动作变化作为低成本过程信用代理。

**评测与发现**：ALFWorld、WebShop、HotpotQA 上相对静态记忆基线最高有约 13%-17% 相对提升。贡献在于把“存什么”和“何时/怎样抽象”解耦，并把刷新频率视作 test-time scaling 维度。

**局限与启示**：只保留成功轨迹，忽略失败经验；动作字符串变化并不必然代表策略有因果贡献；刷新策略本身仍由提示控制；仅 text-only。benchmark 可通过 counterfactual replay 更严谨地测一条 memory 是否真正改变动作。

## 11. MEM1: Learning to Synergize Memory and Reasoning for Efficient Long-Horizon Agents

**出处**：ICLR 2026；[论文](https://openreview.net/forum?id=XY8AaxDSLb)；[代码](https://github.com/MIT-MI/MEM1)。

**问题**：如何让同一个 agent 在长程任务中边推理边压缩工作状态，使上下文不随轮数无限增长？

**方法**：每轮只保留一个不断重写的内部状态 `S_i`；上一状态、动作和观察用于产生新状态，旧内容随后丢弃。为训练动态裁剪上下文，论文将子轨迹拼接，再使用二维注意力 mask 复现每轮当时可见的信息，并用 information mask 排除环境 token；端到端 RL 迫使状态保留未来需要的信息。训练用 2-objective 复合 QA，测试扩展到更多目标。

**评测与发现**：方法在长 horizon 上保持近常数 context，并展示小模型可超过更大的全历史基线。核心贡献是 memory consolidation 与 reasoning 的协同，而不是外挂摘要器。

**局限与启示**：单一状态形成不可逆瓶颈，早期误删无法找回；复合 QA 分布规整；规则奖励难迁移到开放任务。它更接近 working memory，应与 persistent memory 分轨评测，不能只用同一“memory accuracy”。

## 12. REMem: Reasoning with Episodic Memory in Language Agents

**出处**：ICLR 2026；[论文](https://arxiv.org/abs/2602.13530)；[代码](https://github.com/intuit-ai-research/REMem)。

**问题**：怎样保留事件的时空情境，并支持排序、计数、时间过滤等不能由一次向量检索完成的 episodic reasoning？

**方法**：先从经历提取带时间、地点、参与者的 gist，再抽取可追溯事实三元组；二者组成 hybrid memory graph。查询时 agent 调用实体上下文查找、时间过滤、排序、偏移和聚合等工具。REMem-S 是单步检索，REMem-I 允许迭代推理与工具调用。

**评测与发现**：论文报告情节回忆和推理分别较此前方法提升 3.4% 与 13.4%；Test of Time 上超过 90% EM。REMem-I 在推理任务显著优于单步版本，说明结构只有通过可操作接口才能转化为推理收益。

**局限与启示**：gist/fact 抽取成本和误差均依赖 LLM；图不断增长；工具轨迹可能很长；开放式行动与权限未验证。我们的 benchmark 应同时给 event-level 原文和可选结构化状态，避免只奖励某种专用图 schema。

## 13. Sculptor: Empowering LLMs with Cognitive Agency via Active Context Management

**出处**：ICLR 2026；[论文](https://openreview.net/forum?id=HPeiH7da0Z)。

**问题**：长上下文的主要困难是否不只是容量不足，而是旧信息持续造成前摄干扰；模型能否主动整理自己的 working context？

**方法**：提供切片、折叠、摘要、展开和精确搜索等确定性、可逆工具，保持消息顺序和数量可追踪。模型在推理中决定何时操作上下文。训练采用适应动态 context 的 GSPO，通过条件轨迹和增量损失避免上下文改写破坏标准前缀假设。

**评测与发现**：多个长上下文 benchmark 上，论文记录 13B 平均分从 39.4 提升到 73.8；显式去除干扰比要求注意力“自己忽略”更有效。

**局限与启示**：零样本依赖任务 prompt；弱工具调用模型收益不稳定；精确搜索不覆盖语义近似；任务偏单轮 working memory。它提示 benchmark 应包含 full-history + active-context baseline，并显式区分可逆暂存与永久遗忘。

## 14. StructMem: Structured Memory for Long-Horizon Behavior in LLMs

**出处**：ACL 2026；[论文](https://arxiv.org/abs/2604.21748)；[代码](https://github.com/zjunlp/LightMem)。

**问题**：怎样在扁平记忆的高效率与知识图谱的结构推理能力之间找到中间表示？

**方法**：以“时序锚定的关系事件”为单元，从对话双方视角提取事件，并绑定统一时间；再周期性召回相关事件，批量生成跨事件的关系假设。它用自然语言事件保持局部上下文，又避免昂贵的实体消解和逐条图更新。

**评测与发现**：LoCoMo 上报告 76.82%，token 约 1.94M，显著低于论文所列图记忆基线的 35.8M。结果说明 memory unit 的选择可以改变效率-结构权衡。

**局限与启示**：缺少显式冲突解决和版本更新；双视角提取依赖 prompt；仅在 LoCoMo 验证；时间局部性不一定适用于跨周工作流。可作为 event memory baseline，并重点测试跨时间远距离关系。

## 15. TiMem: Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2601.02845)；[代码](https://github.com/TiMEM-AI/timem)。

**问题**：长期对话怎样在保留细节与形成稳定 persona 之间分层压缩，并让不同 query 读取合适时间粒度？

**方法**：构建 segment/session/day/week/profile 五层 Temporal Memory Tree，父子节点满足时间包含；LLM 逐层 consolidation。查询时 planner 预测需要访问的层级，gating 再筛选具体节点，把“去哪一层”和“哪些条目进入上下文”分开。

**评测与发现**：LoCoMo 和 LongMemEval-S 上同时改善准确率并减少召回上下文；时间从 metadata 上升为结构约束，使高层 persona 可追溯到低层事件。

**局限与启示**：固定五层不一定适合其他领域；构建、planner 和 gating 均依赖 LLM；偏好冲突、删除与隐私运维不足。benchmark 的时间层级应由事件跨度生成，不应强制所有系统采用固定树。

## 16. APEX-MEM: Agentic Semi-Structured Memory with Temporal Reasoning for Long-Term Conversational AI

**出处**：ACL 2026；[论文](https://arxiv.org/abs/2604.14362)。

**问题**：更新时立即合并会丢掉历史版本，完全保留又带来噪声；能否推迟冲突裁决到 query 时？

**方法**：用领域无关 ontology 支撑 property graph，事实锚定到带时间戳的 event，并采用 append-only 写入。检索时 ReAct agent 调用 SchemaViewer、EntityLookup、GraphSQL 和 Search，依据 query 时间动态解析版本冲突；图存储落在 SQLite，使时间函数、聚合和 join 可直接使用。

**评测与发现**：论文报告 LoCoMo 88.88%、LongMemEval 86.2%，时序问题对合并式系统优势明显。其主要范式是“写入保真，读取裁决”。

**局限与启示**：构建依赖强模型；一次回答平均需要约 20-30 次工具调用；固定 ontology 难覆盖专业域；严重噪声下仍弱；只测 QA。它可作为 append-only 上界 baseline，也能与 destructive-update baseline 构成关键对照。

## P1 横向结论

这些方法可以按功能分成四组：

1. **事实/情节组织**：A-MEM、REMem、StructMem、TiMem、APEX-MEM、MRAgent。
2. **经验/程序性复用**：R2D2、APC、CER、AdaMEM。
3. **学习型 memory policy**：Memory-T1、MemSearcher、MEM1、Sculptor。
4. **专项时间推理**：TReMu、Memory-T1、TiMem、APEX-MEM。

第二阶段不应提前押注“图、树还是摘要”哪一个表示最好。第一阶段 benchmark 应先暴露 dominant failure：如果 writer/update 失败占主导，再训练操作策略；如果 contextual hard negative 占主导，再做 reranker；如果已经取对但不会用，再做 evidence verifier/reader；如果成本占主导，再研究预算自适应与缓存。
