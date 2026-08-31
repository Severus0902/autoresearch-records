# Agentic KGR + Reinforcement Learning 调研报告

日期：2026-08-31  
范围：Knowledge Graph Reasoning (KGR), Knowledge Graph Question Answering (KGQA), LLM-on-KG reasoning, agentic GraphRAG, reinforcement learning (RL) for graph/search agents  
本地 Zotero 入口：`data/zotero/library.md`

## 一句话判断

Agentic KGR + RL 是一个值得推进的方向，但核心不应只是“给 ToG/RoG 加 RL”，而应把知识图谱推理定义成可学习的多轮决策环境，让模型学习三件事：走哪条图路径、何时调用哪类检索工具、何时停止并给出可验证答案。

## 术语表

| 术语 | 本报告中的含义 |
|---|---|
| KGR | Knowledge Graph Reasoning，广义上包括图上多跳路径推理、关系预测、KGQA、KG-grounded reasoning。 |
| KGQA | Knowledge Graph Question Answering，给定自然语言问题，在 KG 上定位答案实体或生成答案。 |
| Agentic KGR | LLM 或策略模型以 agent 形式与 KG 环境交互，包含观察、动作、记忆、反思、停止等机制。 |
| RL-KGR | 将图上推理建模为序贯决策，用 RL 学习路径搜索、关系选择、工具调度或检索策略。 |
| ToG | Think-on-Graph，训练自由的 LLM-KG agent，通过迭代 beam search 探索 KG 路径。 |
| RoG | Reasoning on Graphs，先生成 KG-grounded relation paths 作为计划，再检索路径并推理。 |
| GCR/GcR | 这里按 Graph-constrained Reasoning 理解，即用 KG-Trie 约束 LLM 解码，生成 KG-grounded 推理路径。若你指的是 Graph Chain-of-Thought，本报告也把 Graph-CoT 作为相邻基线列入。 |
| Graph-RFT | Plan Then Retrieve 提出的两阶段 RL fine-tuning KGQA 框架，学习 plan-KG search-Web search 的调度。 |
| EoG | Explore-on-Graph，利用 RL 和 path-refined reward 促进 LLM 在 KG 上自主探索。 |
| GRM | 本报告建议定义为 Graph-grounded Reward Model，即面向 KG 轨迹、子图证据和答案质量的可学习奖励模型。GRM 不替代硬图验证器，而是提供更密集的过程奖励。 |

## 执行摘要

这个方向的主要机会来自一个清晰的断层：ToG、RoG、PoG、KG-Agent、GCR 等方法已经证明 KG 可以显著提升 LLM 的可追溯性、忠实性和复杂问答能力，但多数方法仍依赖手工搜索规则、固定工具调用流程、SFT 模仿路径或解码约束。它们在面对不完整 KG、噪声图、长链问题、跨源证据和 OOD 问题时，缺少一个能根据状态动态调整策略的训练目标。

经典 RL-KGR 从 DeepPath、MINERVA、Reward Shaping 到 M-Walk 已经把 KG 推理形式化为 graph-walking MDP，证明了“路径选择策略”可以学习。但早期方法的动作空间主要是实体/关系，语言理解、复杂问题分解、外部文本检索和自然语言解释能力较弱。LLM 时代的关键变化是：agent 可以同时操作 KG、文本、Web、代码和记忆，因此 RL 不只是学路径，而是学“搜索策略 + 工具调度 + 证据整合 + 停止判断”。

2025-2026 年的工作已经开始把这个方向推到前台。Graph-R1 把 GraphRAG 检索建模为多轮 agent-environment 交互并用端到端 RL 优化；Plan Then Retrieve/Graph-RFT 将 KGQA 放进 plan-KGsearch-Websearch-during-think 范式，通过多奖励训练覆盖感知的检索调度；Explore-on-Graph 使用 path-refined reward 解决固定示范路径导致的泛化瓶颈；DeepDive 用 KG 自动合成长搜索问题，再用多轮 RL 训练深度搜索 agent。这些工作共同说明：RL 对 agentic KGR 的价值，不在于替代 KG 约束，而在于让模型学会在约束空间内主动探索。

## 文献地图

### 1. 经典 RL-KGR：把图推理变成路径搜索

DeepPath 将 KG 推理建模为 policy-based agent 的多跳关系路径采样，奖励同时考虑准确性、多样性和效率。它的价值在于建立了“路径质量不只等于最终答案正确”的思想，为后续 path-refined reward 提供了早期范式。

MINERVA 进一步把问题设置成给定查询关系和起始实体，让 agent 学会在 KB 中导航到答案实体。它避免随机路径在大规模图上的不可行性，将 query-conditioned navigation 作为核心任务。这个设定和今天的 KGQA agent 很接近，只是当时没有 LLM 的自然语言计划能力。

Multi-Hop KG Reasoning with Reward Shaping 处理两个长期难点：KG 不完整带来的 false negative reward，以及 on-policy RL 容易被 spurious path 误导。它用预训练 one-hop embedding 模型估计未观测事实奖励，并通过随机 edge mask 促进路径多样性。这个思路对今天仍重要，因为 LLM-on-KG 也会遇到“答案对但路径不可靠”的问题。

M-Walk 用 MCTS 处理稀疏奖励问题，把树搜索轨迹用于 off-policy Q-learning。它提示我们：agentic KGR 不一定只能用 PPO/GRPO，也可以考虑搜索增强的策略改进，尤其适合长链、多分支、延迟奖励的图推理。

### 2. LLM-on-KG 基线：训练自由、规划式、约束式与反思式

ToG 是这个方向最自然的 baseline。它把 LLM 作为 agent，与 KG 交互式探索实体和关系，并通过 beam search 找到可能的推理路径。它的优势是训练自由、可插拔、可追溯；短板是多轮交互带来成本，搜索宽度和剪枝策略多依赖手工设计。

RoG 把 KG 结构显式放进 plan-retrieve-reason pipeline：先生成 KG-grounded relation paths 作为 faithful plans，再用这些计划从 KG 检索有效推理路径，最后让 LLM 推理。RoG 相比 ToG 更强调结构化计划，但计划生成和路径检索之间仍有固定流程的痕迹。

Graph-CoT 针对 text-attributed graphs 设计 GRBench，并让 LLM 在每轮进行 reasoning、graph interaction、graph execution。它不完全等同传统 KGQA，但对“文档图/论文图/领域图上的迭代推理”很有参考价值，尤其适合未来把 Zotero 文献网络也纳入研究系统。

GCR 把 KG 结构直接引入 LLM 解码，通过 KG-Trie 限制模型只能生成 KG 中合法路径，再由通用 LLM 对多条路径做归纳推理。它是重要 baseline，因为它把 faithfulness 做得很硬，但相对不强调自主探索和多源检索调度。RL 方向可以把它作为“强约束解码上界”或“路径合法性约束模块”。

GoG 面向不完整 KG，提出 Thinking-Searching-Generating 框架，让 LLM 既作为 agent 搜索 KG，又作为 KG 生成缺失事实。它指出真实 KGQA 不能假设 KG 完整，这一点和 RL 的探索奖励设计高度相关。

PoG 通过 Guidance、Memory、Reflection 进行自校正、自适应图上规划，解决固定探索宽度和错误路径无法纠正的问题。它可以作为 agentic planning baseline，也可以作为 RL 环境中反思动作的启发。

KG-Agent 将 LLM、多功能工具箱、KG executor 和 knowledge memory 组合成自治 agent，并用代码化指令数据微调小模型。它证明小模型在有清晰工具接口和轨迹数据时可以超过更大模型或更多数据的方法，是 RL 前 SFT/行为克隆冷启动的重要参考。

RefKG 引入 query decoupling、LLM-driven KG exploration 和 knowledge reconstruction，通过检索与反思减少噪声。它可以作为“反思式 KG agent”基线，用来区分 RL 带来的收益是不是仅仅来自多轮反思。

### 3. Agentic GraphRAG：从一次性检索转向多轮检索策略

GraphRAG、LightRAG、HippoRAG、KG-Retriever、PathRAG、GFM-RAG 这一线工作把文本库组织成图或利用图增强检索。它们主要解决的是知识组织和检索质量问题，而不是显式学习 agent 策略。它们适合作为非 RL 或弱 agentic 的 GraphRAG baseline。

ToG-2 将结构化 KG 和非结构化文档检索紧耦合，交替进行 graph retrieval 和 context retrieval。ToG-3 进一步使用多 agent 的 MACER 机制，通过 query evolution 和 subgraph evolution 动态构造和细化异构图索引。它们提示一个重要趋势：真实 KGR 越来越不是“纯 KG”，而是 KG + 文档 + 多 agent 检索系统。

GraphSearch 也沿着这个趋势推进。它用 dual-channel retrieval 同时发起文本语义检索和结构图关系检索，并通过多模块 agentic workflow 做 query decomposition、context refinement、query grounding 和 reflection routing。它不是 RL 方法，但很适合作为“强 agentic workflow baseline”。

### 4. RL 驱动的 agentic KGR/GraphRAG：当前最贴近目标的论文

Graph-R1 将 GraphRAG 检索建模为多轮 agent-environment 交互，使用端到端 RL 优化检索过程。它的贡献是把 GraphRAG 从静态构图和一次性检索，推进到可学习的多轮检索代理。

Plan Then Retrieve/Graph-RFT 是目前最贴合“KGQA + RL + 多源检索”的基线。它提出两阶段训练：先用 CoT/plan-retrieval 数据解决 GRPO 冷启动，再用包含 outcome 和 retrieval-specific signals 的多奖励 RL 学习 KG 与 Web 的调度。它的范式尤其适合不完整 KG，因为模型需要判断何时 KG 不够、何时需要 Web。

Explore-on-Graph 针对固定规则或固定示范路径限制泛化的问题，先用长 CoT SFT 给模型图探索基础能力，再用 GRPO 和 path-refined reward 训练模型探索更广的 KG 推理空间。它给 agentic KGR 一个很明确的研究问题：如何奖励“新但有效”的路径，而不是只奖励最终答案。

DeepDive 的任务更偏 deep search agent，但它用 KG 随机游走合成困难 QA，再用多轮 RL 训练浏览 agent。它对 KGR 方向的启发是：KG 不仅可以作为推理环境，也可以作为生成训练任务和难例的机制。

## 方向可行性判断

这个方向可行，而且从已有文献看已经进入“可做强 baseline 复现和改进”的阶段。最直接的可行证据是：经典 RL-KGR 证明路径策略可学习；ToG/RoG/GCR 证明 KG-grounded LLM 推理有效；Graph-R1、Graph-RFT、EoG、DeepDive 证明 RL 可以训练 LLM agent 的多轮检索或图探索策略。

但如果目标是做出论文级贡献，不能只说“我们把 RL 用到 KGQA 上”。这个表述已经被 Graph-RFT 和 EoG 覆盖。更好的切入点是找到一个更具体的策略学习问题，例如：

1. 学习搜索宽度和路径预算，而不是固定 beam size 或固定 hop 数。
2. 学习 KG、文本、Web 三类证据源的调度策略，而不是写死 pipeline。
3. 学习“合法路径约束 + 自主探索”的结合，让 GCR 类约束保证 faithfulness，让 RL 负责 coverage 和效率。
4. 学习何时反思、回退、重规划和停止，避免 agent 无限检索或过早回答。
5. 学习面向不完整 KG 的 abstention 和补充检索策略，把“KG 中没有”与“没检索到”区分开。

## 可立项的问题定义

可以把 Agentic KGR 建模为一个 partially observable MDP：

- 状态：问题 `q`、当前实体集合、已走路径、候选关系、检索到的文本证据、agent memory、剩余预算。
- 动作：选择关系、扩展实体、检索文本、调用 Web、生成子问题、反思当前路径、回退、停止回答、拒答。
- 观察：KG 邻居、路径合法性、文本片段、外部搜索结果、执行错误、验证器反馈。
- 奖励：最终答案正确性、路径合法性、证据覆盖、路径简洁性、跨源一致性、工具成本、反思有效性、拒答正确性。

一个合理的技术主张是：

> 相比固定流程的 LLM-on-KG 方法，RL 训练的 agentic KGR 可以在 KG 不完整和问题长链化时，学习更好的图路径探索、跨源检索调度和停止策略；同时通过 KG 约束或路径验证保持推理忠实性。

## GRM 奖励建模方案

可以训练一个 Graph-grounded Reward Model (GRM) 来改进 RL reward，但它不应被表述为“保证 reward 正确”。更稳妥的设计是：硬图验证器负责不可违反的事实约束，GRM 负责软的过程质量判断，最终答案奖励负责任务目标。也就是说，GRM 是 dense process reward，而不是唯一 reward source。

推荐的总奖励形式为：

```text
R = alpha * R_answer + beta * R_hard_graph + gamma * R_GRM - delta * Cost
```

其中 `R_answer` 评估最终答案是否正确，`R_hard_graph` 检查路径是否合法、关系方向是否正确、实体是否存在于 KG、是否使用了允许的子图，`R_GRM` 判断轨迹是否覆盖了必要证据、是否存在 spurious path、是否过早停止、是否需要转向文本或 Web 检索，`Cost` 惩罚 token、LLM calls、tool calls、hop 数和无效扩展。

GRM 的输入不应该是整张 KG，而应该是问题相关的局部观察：

```text
input = {
  question,
  seed_entities,
  retrieved_subgraph,
  trajectory_actions,
  trajectory_observations,
  final_answer,
  verifier_outputs
}
output = {
  scalar_reward,
  optional_diagnostics
}
```

训练目标建议从 pairwise ranking 开始，而不是直接回归绝对分数：

```text
(q, trajectory_good, answer_good) > (q, trajectory_bad, answer_bad)
```

正样本可以来自 gold KG path、RoG relation paths、ToG/PoG/KG-Agent 中答案正确且路径合法的轨迹，以及人工或规则验证过的多跳证据链。负样本可以系统构造：替换中间实体、反转关系方向、删除关键边、加入无关但合法路径、保留正确答案但给出 spurious path、让 agent 过早停止、让 agent 在 KG 缺失时拒绝调用文本/Web 检索。

GRM 的输出最好拆成多维诊断，再聚合成 reward。例如：

| 维度 | 判断对象 | 作用 |
|---|---|---|
| Answer support | 当前轨迹是否足以支持答案 | 避免模型靠内部知识猜答案。 |
| Path faithfulness | 路径是否存在且关系方向正确 | 约束 KG-grounded reasoning。 |
| Evidence coverage | 是否覆盖问题所需关键事实 | 奖励找全证据，而不只找对答案。 |
| Step utility | 当前动作是否带来新信息 | 惩罚重复扩展和无效检索。 |
| Stop quality | 是否应该继续检索或停止回答 | 训练 traverse/retrieve/stop 策略。 |
| Source switching | KG 不完整时是否转向 text/Web | 面向 incomplete KG 的关键能力。 |

实际 RL 训练时可以采用 hard gating：如果 `R_hard_graph` 判定路径非法或实体越界，则将 `R_GRM` 封顶或置零；如果答案正确但证据链不支持，也只给较低 reward。这样可以降低 reward hacking 风险，避免 GRM 被模型用流畅但不忠实的解释欺骗。

## 数据预处理与子图构造

不能把整张 KG 直接塞进模型。无论是 ToG、RoG、GCR、Graph-RFT 还是 EoG，实际可行的做法都是把大 KG 放在后端图存储或检索服务里，每一步只向 agent 暴露 query-centered subgraph 或候选邻居。模型看到的是局部观察，不是完整图。

建议采用“离线索引 + 在线子图”的两层预处理：

1. 离线层构建全图索引。包括实体别名表、关系文本描述、实体 embedding、关系 embedding、邻接表、倒排索引、文本证据索引、entity-to-document 映射和 relation-to-document 映射。
2. 在线层根据问题构建子图。先做 entity linking 得到 seed entities，再用关系召回、k-hop 扩展、Personalized PageRank、RoG-style relation path generation 或 ToG-style relation pruning 得到候选子图。
3. 训练层缓存 rollout 观察。每个样本保存 seed entities、候选关系、候选路径、检索文本、agent action、observation、verifier result、reward components，避免每次训练都重新扫图。

一个可复现的子图构造流程可以写成：

```text
question
  -> entity linking
  -> seed entity set
  -> relation candidate retrieval
  -> bounded k-hop expansion
  -> path scoring / PPR / semantic reranking
  -> top-N nodes, top-M edges, top-K paths
  -> serialized subgraph observation
```

子图预算需要显式记录。第一版可以设置为：

| 参数 | 建议初值 | 说明 |
|---|---:|---|
| `max_hop` | 2-3 | WebQSP/CWQ 第一版足够，长链任务再放宽。 |
| `max_nodes` | 200-500 | 给 LLM 的可读观察应更小，后端候选可更大。 |
| `max_edges` | 500-1500 | 按关系相关性和实体中心性裁剪。 |
| `max_paths` | 20-50 | 用于 RoG/GCR/GRM 评分。 |
| `max_relation_candidates` | 20-40 | 控制每步 action space。 |
| `max_text_chunks` | 5-10 | 只给与实体/关系相关的证据片段。 |

对 LLM 输入，子图不应只是原始三元组堆叠，而应带有可追踪 ID：

```text
[E12] Barack Obama
[R4] place_of_birth
[E33] Honolulu
[T7] Barack Obama -- place_of_birth --> Honolulu
source: Wikidata / Freebase / document chunk id
```

训练和评测时，agent 的动作应该通过 API 访问图，而不是直接自由生成任意三元组：

```text
expand(entity_id, relation_id)
retrieve_text(query, entity_ids, relation_ids)
verify_path(path_ids)
rerank_paths(path_ids)
reflect(state_summary)
stop(answer, supporting_path_ids)
```

这种设计有两个好处。第一，它能让 hard verifier 精确判断每一步是否合法。第二，它能让 GRM 只评价“agent 已经观察到的子图和轨迹”，避免模型因为看过整张 KG 而产生不可复现的信息泄漏。

## Memory 结合方案

Agentic KGR 与 memory 方向高度相关，但这里的 memory 不应被理解成“把更多文本塞进上下文”。更有价值的定义是：memory 是 agent 可检索、可验证、可更新的长期经验层，用来记录过去问题的成功路径、失败路径、子图检索决策、停止判断和 verifier 反馈。

可以把 memory 分为四类：

| Memory 类型 | 在 Agentic KGR 中的作用 |
|---|---|
| Working memory | 当前 episode 的已走路径、候选实体、候选关系、检索证据、剩余预算。 |
| Episodic memory | 过去相似问题的成功/失败轨迹，用于 warm-start 当前搜索。 |
| Semantic memory | 从 KG、文档、Zotero 文献、实验记录中沉淀出的长期事实和概念关系。 |
| Procedural memory | 过去学到的策略经验，例如何时走 KG、何时检索文本、何时反思、何时停止。 |

在方法上，memory 应该作为显式工具接入 agent，而不是隐式拼接到 prompt：

```text
read_memory(query_pattern, seed_entities, relation_candidates)
write_memory(question, trajectory, supporting_paths, failure_reason, verifier_outputs)
retrieve_subgraph(seed_entities, memory_hints)
verify_memory(memory_ids, current_subgraph)
```

这种设计可以和 GRM 形成闭环。GRM 不仅评价当前轨迹是否好，也评价 memory 是否真的帮助了推理。例如，若一条 memory 提供了历史成功路径，但该路径中的实体或关系在当前问题子图中无法验证，则 hard verifier 应降低其可信度；若 memory 帮助 agent 更快找到支持路径并减少无效扩展，则 GRM 可以给正的 process reward。

推荐的 memory-aware reward 为：

```text
R = alpha * R_answer
  + beta * R_hard_graph
  + gamma * R_GRM
  + eta * R_memory_utility
  - delta * Cost
```

其中 `R_memory_utility` 不奖励“读了多少 memory”，而奖励 memory 是否带来了可验证收益：更高的 gold path recall、更少无效 hop、更少重复检索、更好的 stop decision。这样可以避免模型为了拿 memory reward 而反复检索无关历史轨迹。

这个结合方向的关键风险是 memory leakage。训练集问题的 gold path 或答案如果直接进入 test-time memory，会虚高结果。因此实验必须区分三种设置：closed-book memory，即测试时只允许读训练阶段沉淀的通用策略经验；task-memory，即允许读同一任务族的历史失败/成功轨迹但不能包含测试答案；oracle-memory，即上界分析，允许读人工标注的相关经验但必须单独报告。

## 推荐切入点：Memory-guided Subgraph Action Selector

当前最适合作为第一阶段验证的 idea 是 **Memory-guided Subgraph Action Selector**。它不要求 0.6B 小模型直接生成完整推理链，也不要求模型记住整张 KG，而是让小模型在每一步根据问题、局部子图和 memory hints 选择下一步动作。

任务形式如下：

```text
Input:
  question
  seed_entities
  compact subgraph observation
  relation candidates
  top-k memory hints
  current trajectory

Output:
  one action from a constrained action set:
    expand(entity_id, relation_id)
    retrieve_text(entity_id or relation_id)
    reflect()
    stop(answer_entity_id, supporting_path_ids)
```

这个 idea 适合 0.6B 模型的原因有四点。第一，动作空间是受控的，模型输出可以被解析和验证，不需要开放式生成长答案。第二，知识主要在后端 KG、子图和 memory store 中，小模型只学习策略，不承担大模型式知识记忆。第三，reward 可以很快闭环：选对关系、走到答案实体、减少无效 hop、正确停止都能自动计算。第四，baseline 清晰，可以从 ToG 的规则式 beam search、RoG 的 relation path、无 memory 的 action selector 和有 memory 的 action selector 逐级比较。

第一版不建议直接做完整 RL。更稳的路线是三步：

1. Behavior cloning：用 ToG/RoG/最短路径/gold path 生成 `(state, action)` 数据，先 SFT 一个 0.6B action selector。
2. GRM reranking：训练轻量 GRM 对候选 action 或候选轨迹打分，用它做 reranker，而不是立刻进 RL。
3. Online RL：在 SFT 模型稳定后，再用 GRPO/PPO 类方法优化 answer reward、hard graph reward、GRM reward、memory utility reward 和 cost。

最小可验证实验可以只用 WebQSP 或 MetaQA。每个问题先通过 entity linking 找 seed entity，构造 2-hop 或 3-hop 子图，然后让模型在候选关系中选择下一跳。第一阶段只评估 `next-relation accuracy`、`gold-path edge recall`、`answer hit rate within budget`、`invalid action rate` 和 `steps-to-answer`。如果 0.6B 在这些指标上能超过规则式 relation ranking 或无 memory selector，再扩展到 CWQ 和不完整 KG 设置。

模型上，Qwen3-0.6B 是合适的首个验证对象：它是 0.6B 参数规模，支持长上下文和 agentic/tool-use 场景，可用于快速测试 action-format following 与小模型策略学习。实践上建议先使用 non-thinking mode 做动作选择，保证输出短、稳定、易解析；需要反思动作时再单独测试 thinking mode。

这个方案的论文贡献可以这样表述：

> We study whether a small language model can learn graph reasoning policies over query-centered subgraphs by reusing verified episodic memory and optimizing graph-grounded process rewards.

它的贡献边界也比较清楚：不是提出新的大模型 KGQA 系统，而是验证小模型是否能在 KG 工具、子图观察和 memory 经验的支持下学习可解释、低成本的推理策略。

## 推荐 baseline 体系

### 最小 baseline

| 组别 | 方法 | 用途 |
|---|---|---|
| LLM-only | Direct answer, CoT, self-consistency | 判断模型内生知识与纯推理上限。 |
| Text RAG | BM25/vector RAG, IRCoT | 判断没有 KG 时的检索推理能力。 |
| KG agent | ToG | 训练自由的交互式 KG 搜索强基线。 |
| KG planning | RoG | relation-path planning + retrieval + reasoning 基线。 |
| KG constrained | GCR/GcR | 约束解码和 faithful path 上界。 |
| Graph-CoT | Graph Chain-of-Thought | text-attributed graph 迭代推理基线。 |

### 完整 baseline

| 组别 | 方法 | 用途 |
|---|---|---|
| Classic RL-KGR | DeepPath, MINERVA, Reward Shaping, M-Walk | 证明传统图走路策略学习的历史基线。 |
| Reflection/planning KG agents | PoG, RefKG, KG-Agent, GoG | 区分 RL 和 SFT/反思/程序化工具使用的收益。 |
| GraphRAG | GraphRAG, LightRAG, HippoRAG, PathRAG, KG-Retriever, GFM-RAG | 作为图检索与文档图问答基线。 |
| Agentic GraphRAG | GraphSearch, ToG-2, ToG-3 | 强 workflow 型基线。 |
| RL agentic | Graph-R1, Graph-RFT, EoG, DeepDive | 直接竞争或强相关 RL 基线。 |

如果时间有限，第一阶段建议只复现 Direct/CoT、BM25/vector RAG、ToG、RoG、GCR、Graph-RFT 或 EoG。ToG/RoG/GCR 是你点名的核心 baseline，Graph-RFT/EoG 是最接近新方向的 RL baseline。

## 数据集与评测

KGQA 数据集建议从 WebQSP、ComplexWebQuestions (CWQ)、GrailQA、MetaQA 开始。WebQSP 和 CWQ 是 ToG/RoG/GCR/EoG 常用交集，适合先做可比实验；GrailQA 更复杂，适合测试组合泛化；MetaQA 有清晰的 1-hop/2-hop/3-hop 设定，适合分析路径长度。

GraphRAG/文档图数据集可考虑 GRBench、GraphRAG-Bench、HotpotQA、2WikiMultihopQA、MuSiQue 等。其中 GRBench 强调 text-attributed graphs；GraphRAG-Bench 需要分开引用 Xiao et al. 的 domain-specific arXiv benchmark 与 Xiang et al. 的 ICLR 2026 GraphRAG-Benchmark 论文，它们共同指向领域文本图和完整 pipeline 评测，适合后续从 KGQA 扩展到文献图和领域研究助手。

评测指标不要只看 EM/F1/Hits@1。建议至少加入：

- 答案正确性：EM、F1、Hits@1、MRR。
- 路径忠实性：生成路径是否存在于 KG、关系方向是否正确、实体是否可追溯。
- 证据覆盖：答案所需事实是否被检索到，跨源证据是否一致。
- 预算效率：LLM calls、tool calls、tokens、latency、检索步数。
- 行为质量：是否过早停止、是否重复检索、是否能正确拒答。
- 泛化：unseen KG、OOD relation pattern、KG incompleteness、噪声边。

## 可能的方法路线

### 路线 A：RL-ToG

把 ToG 的 beam search 和 relation/entity pruning 改成可学习策略。SFT 阶段用 ToG/RoG/PoG 轨迹做行为克隆，RL 阶段用答案正确性、路径合法性、路径长度、工具成本做奖励。优点是容易接现有 baseline，缺点是容易被审稿人认为只是 ToG 的训练版。

### 路线 B：GCR + RL Explorer

用 GCR 的 KG-Trie 或路径验证器保证生成路径合法，让 RL agent 只在合法动作空间中学习探索和停止。这个方向的亮点是同时追求 faithfulness 和 exploration：约束负责不胡说，RL 负责找得更全、更快。风险是实现复杂，需要把约束解码和 RL rollout 接起来。

### 路线 C：Coverage-aware Multi-source Agent

面向不完整 KG，将动作空间扩展为 KG search、text retrieval、Web search、answer、abstain。奖励不仅看最终答案，也看是否在 KG 不足时正确切换到文本/Web。这条路线最贴近 Graph-RFT，但可以进一步强调“结构覆盖”和“证据一致性”的奖励设计。

### 路线 D：Research-KG Agent

把你的 Zotero 文献、Markdown idea/experiment/result 和 GitHub commit 组织成研究知识图谱，让 agent 在“论文-想法-实验-结果-代码变更”图上做推理和实验建议。这个方向更应用系统化，适合做 AutoResearch demo；若要投学术论文，需要设计可复现 benchmark，例如让系统回答“某个想法有哪些文献支持、已有实验是否足够、下一步实验是什么”。

我建议先做路线 B 或 C。路线 B 更有技术新意，路线 C 更容易和当前 RL-agent/search 论文对话。路线 D 可以作为系统场景和长期应用，不建议作为第一篇方法论文的唯一贡献。

## 实验路线图

第 0 阶段：建立统一环境。把 KGQA 数据集、KG 图、文本证据、Web mock 或真实检索工具包装成同一套 action/observation 接口。先保证 ToG、RoG、GCR 能跑同一批样本。

第 0.5 阶段：构建数据预处理管线。离线建立实体、关系、邻接表、embedding、文本证据和 entity-document 映射；在线为每个问题生成 query-centered subgraph，并缓存 seed entities、候选关系、候选路径、文本证据和 verifier outputs。

第 1 阶段：复现强 baseline。至少跑 Direct/CoT、RAG、ToG、RoG、GCR、PoG/KG-Agent 中 1 个、Graph-RFT/EoG 中 1 个。输出统一的答案准确率、路径忠实性、LLM calls 和 latency。

第 2 阶段：收集或合成轨迹。可以从 RoG relation paths、ToG beam paths、PoG planning traces、KG-Agent tool programs 中抽取成功轨迹，做 SFT 冷启动。失败轨迹也要保留，用于训练 verifier、GRM 或 preference/reward model。

第 2.5 阶段：训练 GRM。先构造 pairwise 轨迹偏好数据，再训练 GRM 判断 answer support、path faithfulness、evidence coverage、step utility、stop quality 和 source switching。训练完成后用 held-out trajectories 检查 GRM 是否偏好“答案正确但路径虚假”的轨迹；如果会，则必须加强 hard graph gating。

第 3 阶段：RL 训练。优先使用 GRPO 或 PPO 类方法，奖励设计从简单到复杂递进：

1. outcome reward：答案正确。
2. validity reward：路径存在于 KG，关系方向正确。
3. coverage reward：答案支撑事实被覆盖。
4. efficiency reward：少工具调用、少 token、少无效 hop。
5. abstention reward：KG 不完整时正确转向文本/Web 或拒答。
6. GRM reward：对过程轨迹、证据覆盖和停止时机给 dense reward，但受 hard graph verifier 封顶。

第 4 阶段：消融实验。至少消融 path validity reward、coverage reward、reflection action、KG/Text/Web 调度、约束解码模块、SFT 冷启动数据规模。

第 5 阶段：错误分析。按错误类型分成 entity linking error、wrong relation、spurious path、missing KG fact、retrieval noise、premature answer、over-search、format error。这个错误 taxonomy 会直接支撑论文讨论部分。

## 主要风险

第一，RL reward 容易被 hack。只奖励最终答案会鼓励模型绕过 KG 路径，甚至用内部知识猜答案。因此必须显式奖励路径合法性和证据覆盖。

第二，和 Graph-RFT/EoG 的差异需要非常明确。如果只是“GRPO + KGQA”，新意不足。需要强调约束、跨源调度、abstention、图覆盖、研究场景或动态 KG 中的一个核心差异。

第三，评测成本高。Agentic 方法常常 LLM calls 多、latency 高，因此必须把效率作为主指标，而不是附录指标。

第四，KG 不完整会让“路径忠实性”和“答案正确性”冲突。一个模型可能给出正确答案但 KG 中没有完整证据；这时应评估它是否能识别 KG 缺口并调用补充检索。

第五，baseline 复现难。ToG/RoG/GCR/EoG/Graph-RFT 依赖不同图、prompt、模型和 API。建议先构建统一日志格式，把每一步 action、observation、LLM output、path、answer、reward 全部保存。

第六，子图构造可能引入不可见上限。如果答案实体或关键桥接关系在 preprocessing 阶段被裁掉，后续 agent 再强也无法恢复。因此每个数据集都要报告 oracle subgraph recall，例如 gold answer entity recall、gold path edge recall 和 supporting fact recall。

## 推荐论文题目方向

1. Constrained Exploration for Agentic Knowledge Graph Reasoning with Reinforcement Learning
2. Learning When to Traverse, Retrieve, and Stop for LLM Reasoning over Incomplete Knowledge Graphs
3. Faithful and Coverage-Aware Agentic Knowledge Graph Reasoning via Reinforcement Learning
4. From Graph Constraints to Graph Exploration: Reinforcement Learning for Agentic KGQA
5. Memory-guided Subgraph Action Selection for Small-Model Knowledge Graph Reasoning

如果目标是快速做出 0.6B 小模型验证，我最推荐第 5 个。它把贡献压在一个小而可检验的问题上：小模型是否能借助局部子图和可验证 memory，学会比规则搜索更好的下一步动作选择和停止策略。第 2 个更适合后续扩展成完整 RL-agent 论文。

## 下一步建议

优先做一个小型 reproducibility matrix：

| 任务 | 数据 | baseline | 输出 |
|---|---|---|---|
| KGQA | WebQSP, CWQ | Direct, CoT, ToG, RoG, GCR | 准确率、路径忠实性、调用成本 |
| Incomplete KGQA | GoG/Graph-RFT 设定或人工删边 | ToG, RoG, GoG, Graph-RFT | KG 缺口识别、跨源检索收益 |
| RL policy | 同上 | SFT-only, RL outcome-only, RL multi-reward | RL 奖励消融 |
| Agent behavior | OOD relation/path length split | PoG, KG-Agent, EoG | 反思、回退、停止策略分析 |

如果要立刻开工，我建议先把本地 AutoResearch 系统接到 GitHub remote，然后新建 `experiments/agentic-kgr-rl`，第一批目标不是训练模型，而是写统一 runner 和日志格式。等 ToG/RoG/GCR 在同一环境里跑通，再上 RL。

更具体的第一阶段建议是：先做 `Memory-guided Subgraph Action Selector`。用 WebQSP 或 MetaQA 构造小规模 query-centered subgraph 数据，SFT 一个 0.6B 模型输出受控 action，再用 hard verifier 和轻量 GRM 做候选动作重排。第一周目标不是追 SOTA，而是证明小模型在局部子图和 memory hints 下能降低无效扩展并提升 answer hit rate within budget。

## 核心文献接收/发表出处表

下表记录本报告核心文献的接收或发表出处。依据链接优先使用 ACL Anthology、OpenReview/ICLR、NeurIPS Proceedings、ACM、AAAI、IEEE 或 arXiv/CoRR；尚未确认正式接收的工作保留预印本状态。

| Zotero key | 方法/论文 | 接收/发表出处 | 依据链接 | 状态 |
|---|---|---|---|---|
| `@xiongDeepPathReinforcementLearning2017` | DeepPath | EMNLP 2017 | [ACL Anthology](https://aclanthology.org/D17-1060/) | 正式会议论文 |
| `@dasGoWalkArrive2017` | MINERVA / Go for a Walk and Arrive at the Answer | ICLR 2018 | [OpenReview](https://openreview.net/forum?id=Syg-YfWCW) | 正式会议论文 |
| `@linMultiHopKnowledgeGraph2018` | Multi-Hop KG Reasoning with Reward Shaping | EMNLP 2018 | [ACL Anthology](https://aclanthology.org/D18-1362/) | 正式会议论文 |
| `@shenMWalkLearningWalk2018` | M-Walk | NeurIPS 2018 | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2018/hash/c6f798b844366ccd65d99bc7f31e0e02-Abstract.html) | 正式会议论文 |
| `@panUnifyingLargeLanguage2024` | Unifying LLMs and KGs: A Roadmap | IEEE Transactions on Knowledge and Data Engineering, 2024 | [IEEE DOI](https://doi.org/10.1109/TKDE.2024.3352100) | 期刊论文 |
| `@sunThinkongraphDeepResponsible2024` | Think-on-Graph / ToG | ICLR 2024 | [OpenReview](https://openreview.net/forum?id=nnVO1PvbTv) | 正式会议论文 |
| `@luoReasoningGraphsFaithful2024` | Reasoning on Graphs / RoG | ICLR 2024 | [OpenReview](https://openreview.net/forum?id=ZGNWW7xZ6Q) | 正式会议论文 |
| `@jinGraphChainofthoughtAugmenting2024` | Graph Chain-of-Thought | Findings of ACL 2024 | [ACL Anthology](https://aclanthology.org/2024.findings-acl.11/) | 正式会议论文 |
| `@xuGenerateonGraphTreatLLM2024` | Generate-on-Graph / GoG | EMNLP 2024 Main | [ACL Anthology](https://aclanthology.org/2024.emnlp-main.1023/) | 正式会议论文 |
| `@chenPlanongraphSelfcorrectingAdaptive2024` | Plan-on-Graph / PoG | NeurIPS 2024 Main Conference Track | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4254e856d01a5e7b7ea050477c3ef9b9-Abstract-Conference.html) | 正式会议论文 |
| `@luoGraphconstrainedReasoningFaithful2025` | Graph-constrained Reasoning / GCR | ICML 2025 poster | [OpenReview](https://openreview.net/forum?id=Fr7kH2SFq7) | 正式会议论文 |
| `@jiangKGagentEfficientAutonomous2025` | KG-Agent | ACL 2025 Long Papers | [ACL Anthology](https://aclanthology.org/2025.acl-long.468/) | 正式会议论文 |
| `@zhouReflectionKnowledgeGraph2025` | Reflection on KG / RefKG | Findings of ACL 2025 | [ACL Anthology](https://aclanthology.org/2025.findings-acl.1221/) | 正式会议论文 |
| `@maThinkongraph20Deep2025` | Think-on-Graph 2.0 / ToG-2 | ICLR 2025 | [OpenReview](https://openreview.net/forum?id=oFBu7qaZpS) | 正式会议论文 |
| `@wuThinkongraph30Efficient2025` | Think-on-Graph 3.0 / ToG-3 | arXiv/CoRR 预印本 | [arXiv](https://arxiv.org/abs/2509.21710) | 未确认正式接收 |
| `@edgeLocalGlobalGraph2025a` | GraphRAG / From Local to Global | arXiv/CoRR 预印本 | [arXiv](https://arxiv.org/abs/2404.16130) | 未确认正式接收 |
| `@guoLightRAGSimpleFast2025` | LightRAG | Findings of EMNLP 2025 | [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.568/) | 正式会议论文 |
| `@gutierrezHippoRAGNeurobiologicallyInspired2025` | HippoRAG | NeurIPS 2024 | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html) | 正式会议论文 |
| `@chenKGretrieverEfficientKnowledge2025` | KG-Retriever | IEEE International Conference on Knowledge Graph (ICKG) 2025 | [IEEE Xplore](https://ieeexplore.ieee.org/document/11184752) | 正式会议论文 |
| `@chenPathRAGPruningGraphbased2026` | PathRAG | AAAI 2026 | [AAAI Proceedings](https://ojs.aaai.org/index.php/AAAI/article/view/40268) | 正式会议论文 |
| `@xiaoGraphRAGbenchChallengingDomainspecific2025` | GraphRAG-Bench | arXiv/CoRR 预印本 | [arXiv](https://arxiv.org/abs/2506.02404) | 未确认正式接收；不要与下一行 ICLR 2026 benchmark paper 合并 |
| `@xiangWhenUseGraphs2026` | When to use Graphs in RAG / GraphRAG-Benchmark | ICLR 2026 | [ICLR Proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/6c9e01d6cefbbf4cdd265032550e767f-Abstract-Conference.html) | 正式会议论文 |
| `@luoGraphR1TowardsAgentic2025` | Graph-R1 | ICML 2026 | [project page](https://github.com/LHRLAB/Graph-R1) | 正式会议论文；最终 proceedings 页仍需复核 |
| `@yangGraphSearchAgenticDeep2025` | GraphSearch | arXiv/CoRR 预印本 | [arXiv](https://arxiv.org/abs/2509.22009) | 未确认正式接收 |
| `@luDeepDiveAdvancingDeep2025` | DeepDive | arXiv/CoRR 预印本 | [arXiv](https://arxiv.org/abs/2509.10446) | 未确认正式接收 |
| `@songPlanThenRetrieve2026` | Plan Then Retrieve / Graph-RFT | WWW 2026 / Proceedings of the ACM Web Conference 2026 | [ACM DOI](https://doi.org/10.1145/3774904.3792191) | 正式会议论文 |
| `@yanExploreongraphIncentivizingAutonomous2026a` | Explore-on-Graph / EoG | ICLR 2026 | [arXiv](https://arxiv.org/abs/2602.21728) | 正式会议论文 |

## 核心参考文献

- Xiong et al. 2017. DeepPath: A Reinforcement Learning Method for Knowledge Graph Reasoning. EMNLP 2017. Zotero: `@xiongDeepPathReinforcementLearning2017`. https://arxiv.org/abs/1707.06690
- Das et al. 2017. Go for a Walk and Arrive at the Answer: Reasoning Over Paths in Knowledge Bases using Reinforcement Learning. ICLR 2018. Zotero: `@dasGoWalkArrive2017`. https://arxiv.org/abs/1711.05851
- Lin et al. 2018. Multi-Hop Knowledge Graph Reasoning with Reward Shaping. EMNLP 2018. Zotero: `@linMultiHopKnowledgeGraph2018`. https://aclanthology.org/D18-1362/
- Shen et al. 2018. M-Walk: Learning to Walk over Graphs using Monte Carlo Tree Search. NeurIPS 2018. Zotero: `@shenMWalkLearningWalk2018`. https://proceedings.neurips.cc/paper_files/paper/2018/hash/c6f798b844366ccd65d99bc7f31e0e02-Abstract.html
- Pan et al. 2024. Unifying Large Language Models and Knowledge Graphs: A Roadmap. IEEE TKDE. Zotero: `@panUnifyingLargeLanguage2024`. https://doi.org/10.1109/TKDE.2024.3352100
- Sun et al. 2024. Think-on-Graph: Deep and Responsible Reasoning of Large Language Model on Knowledge Graph. ICLR 2024. Zotero: `@sunThinkongraphDeepResponsible2024`. https://arxiv.org/abs/2307.07697
- Luo et al. 2024. Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning. ICLR 2024. Zotero: `@luoReasoningGraphsFaithful2024`. https://arxiv.org/abs/2310.01061
- Jin et al. 2024. Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs. Findings of ACL 2024. Zotero: `@jinGraphChainofthoughtAugmenting2024`. https://aclanthology.org/2024.findings-acl.11/
- Xu et al. 2024. Generate-on-Graph: Treat LLM as both Agent and KG for Incomplete Knowledge Graph Question Answering. EMNLP 2024. Zotero: `@xuGenerateonGraphTreatLLM2024`. https://aclanthology.org/2024.emnlp-main.1023/
- Chen et al. 2024. Plan-on-Graph: Self-Correcting Adaptive Planning of Large Language Model on Knowledge Graphs. NeurIPS 2024. Zotero: `@chenPlanongraphSelfcorrectingAdaptive2024`. https://arxiv.org/abs/2410.23875
- Luo et al. 2025. Graph-constrained Reasoning: Faithful Reasoning on Knowledge Graphs with Large Language Models. ICML 2025/OpenReview. Zotero: `@luoGraphconstrainedReasoningFaithful2025`. https://openreview.net/forum?id=Fr7kH2SFq7
- Jiang et al. 2025. KG-Agent: An Efficient Autonomous Agent Framework for Complex Reasoning over Knowledge Graph. ACL 2025. Zotero: `@jiangKGagentEfficientAutonomous2025`. https://aclanthology.org/2025.acl-long.468/
- Zhou et al. 2025. Reflection on Knowledge Graph for Large Language Models Reasoning. Findings of ACL 2025. Zotero: `@zhouReflectionKnowledgeGraph2025`. https://aclanthology.org/2025.findings-acl.1221/
- Ma et al. 2025. Think-on-Graph 2.0: Deep and Faithful Large Language Model Reasoning with Knowledge-guided Retrieval Augmented Generation. ICLR 2025. Zotero: `@maThinkongraph20Deep2025`. https://arxiv.org/abs/2407.10805
- Wu et al. 2025. Think-on-Graph 3.0: Efficient and Adaptive LLM Reasoning on Heterogeneous Graphs via Multi-Agent Dual-Evolving Context Retrieval. arXiv:2509.21710. Zotero: `@wuThinkongraph30Efficient2025`. https://arxiv.org/abs/2509.21710
- Edge et al. 2024. From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130. Zotero: `@edgeLocalGlobalGraph2025a`. https://arxiv.org/abs/2404.16130
- Guo et al. 2025. LightRAG: Simple and Fast Retrieval-Augmented Generation. Findings of EMNLP 2025. Zotero: `@guoLightRAGSimpleFast2025`. https://arxiv.org/abs/2410.05779
- Gutierrez et al. 2024. HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models. NeurIPS 2024. Zotero: `@gutierrezHippoRAGNeurobiologicallyInspired2025`. https://arxiv.org/abs/2405.14831
- Chen et al. 2025. KG-Retriever: Efficient Knowledge Indexing for Retrieval-Augmented Large Language Models. IEEE ICKG 2025. Zotero: `@chenKGretrieverEfficientKnowledge2025`. https://arxiv.org/abs/2412.05547
- Chen et al. 2026. PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational Paths. AAAI 2026. Zotero: `@chenPathRAGPruningGraphbased2026`. https://ojs.aaai.org/index.php/AAAI/article/view/40268
- Xiao et al. 2025. GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating Graph Retrieval-Augmented Generation. arXiv:2506.02404. Zotero: `@xiaoGraphRAGbenchChallengingDomainspecific2025`. https://arxiv.org/abs/2506.02404
- Xiang et al. 2026. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation. ICLR 2026. Zotero: `@xiangWhenUseGraphs2026`. https://proceedings.iclr.cc/paper_files/paper/2026/hash/6c9e01d6cefbbf4cdd265032550e767f-Abstract-Conference.html
- Luo et al. 2025. Graph-R1: Towards Agentic GraphRAG Framework via End-to-end Reinforcement Learning. ICML 2026 / arXiv:2507.21892. Zotero: `@luoGraphR1TowardsAgentic2025`. https://arxiv.org/abs/2507.21892
- Yang et al. 2025. GraphSearch: An Agentic Deep Searching Workflow for Graph Retrieval-Augmented Generation. arXiv:2509.22009. Zotero: `@yangGraphSearchAgenticDeep2025`. https://arxiv.org/abs/2509.22009
- Lu et al. 2025. DeepDive: Advancing Deep Search Agents with Knowledge Graphs and Multi-Turn RL. arXiv:2509.10446. Zotero: `@luDeepDiveAdvancingDeep2025`. https://arxiv.org/abs/2509.10446
- Song et al. 2026. Plan Then Retrieve: Reinforcement Learning-Guided Complex Reasoning over Knowledge Graphs. WWW 2026. Zotero: `@songPlanThenRetrieve2026`. https://doi.org/10.1145/3774904.3792191
- Yan et al. 2026. Explore-on-Graph: Incentivizing Autonomous Exploration of Large Language Models on Knowledge Graphs with Path-refined Reward Modeling. ICLR 2026. Zotero: `@yanExploreongraphIncentivizingAutonomous2026a`. https://arxiv.org/abs/2602.21728
