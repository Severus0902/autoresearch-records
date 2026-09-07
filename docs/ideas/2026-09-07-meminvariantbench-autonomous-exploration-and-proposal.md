---
title: "MemInvariantBench：持久 Agent Memory 的语义不变性与决定性敏感性评测"
type: autonomous-research-exploration-and-proposal
status: recommended-pilot
created: "2026-09-07"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "semantic-invariance", "metamorphic-testing", "behavioral-consistency", "memory-representation"]
---

# MemInvariantBench：持久 Agent Memory 的语义不变性与决定性敏感性评测

> 检索截止时间：2026-09-07。本文综合已有本地调研文档，并进一步检索 2025--2026 年正式论文、arXiv 预印本、项目页和代码仓库。由于 2026 年预印本仍可能更新，本文采用有边界的创新表述：**在本轮检索覆盖的工作中尚未发现完整等价协议**，不声称数学意义上的“绝对首创”。

## 0. 结论先行

### 0.1 最值得继续验证的问题

经过多轮碰撞检索，当前最适合继续推进的问题不是再做一个覆盖 formation、retrieval、use、repair 全生命周期的大而全 benchmark，也不是继续把失效传播、记忆修复、主动检索或常驻路由单独包装成新问题，而是：

> **当持久记忆所表达的事实、约束和可支持行动的语义保持不变，但其措辞、分块、会话边界、独立事件顺序、冗余度或压缩形式发生变化时，Agent 的记忆形成、检索和行动是否保持一致；而当只改变一个决定性语义条件时，Agent 又能否按预期改变行为？**

工作名：

> **MemInvariantBench: Metamorphic Evaluation of Semantic Invariance and Decisive Sensitivity in Persistent Agent Memory**

中文名：

> **MemInvariantBench：持久 Agent Memory 的语义不变性与决定性敏感性评测**

这里有一对必须同时满足的行为契约：

1. **语义不变性（semantic invariance）**：只改变记忆的表面实现，不改变任务相关语义时，正确行为不应改变。
2. **决定性敏感性（decisive sensitivity）**：只改变一个会改变正确决策的语义条件时，行为必须随之改变。

第二条非常重要。若只测一致性，一个始终忽略记忆、永远输出同一动作的 Agent 也可能获得高分；加入决定性对照后，“稳定但错误”不能冒充鲁棒。

### 0.2 为什么现在可以继续做

本问题不是凭空提出，而是由三条已有证据链共同推出：

1. [Beyond Memory Leaderboards](https://arxiv.org/abs/2607.16848) 发现 ingestion granularity、raw-text preservation、retrieval budget、modality 和 judge choice 都会改变 scientific-memory 结果；Graphiti 的领先在控制检索预算后消失。这说明当前 memory leaderboard 可能混入协议实现因素。
2. [GroupMemBench](https://arxiv.org/abs/2605.14498) 发现最强系统平均准确率仅 46.0%，BM25 可匹敌多数 Agent Memory 系统，并将失败指向 memory ingestion 对结构与词汇特征的损失。这说明“写入后如何表示”本身会改变可用性。
3. [Useful Memories Become Faulty When Continuously Updated by LLMs](https://arxiv.org/abs/2605.12978) 发现相同轨迹在不同更新日程下会产生不同记忆，并可能由有益变有害。这说明 memory state 不只是 experience semantics 的函数，也受 consolidation realization 影响。

通用 NLP 领域已经有可借鉴的方法论：[CheckList](https://aclanthology.org/2020.acl-main.442/) 使用 invariance 与 directional expectation tests 做行为测试；[Contrast Sets](https://aclanthology.org/2020.findings-emnlp.117/) 用最小但有意义的编辑检查局部决策边界；[Same Meaning, Different Scores](https://aclanthology.org/2026.lrec-1.363/) 进一步证明真值条件等价的词汇和句法变化会造成模型性能与排名波动。但这些工作不研究持久记忆的“历史摄入--记忆形成--检索--行动”流水线。

截至本轮检索，尚未发现一项 Agent Memory 工作同时具备：

- 对同一潜在记忆状态构造多种**语义等价的历史/记忆实现**；
- 用最小决定性变化构造配对的**行为应变对照**；
- 评价最终答案之外的工具行动、参数和证据；
- 通过 full-context、oracle memory、all-memory-visible、native retrieval 等干预定位 failure stage；
- 报告 family worst case、行为一致性、决定性敏感性和系统排名翻转。

因此，当前可防守的贡献不是“首次研究 memory robustness”，而是：

> **把语义等价记忆实现造成的行为不稳定定义为一个 Agent Memory 问题，并通过双侧变形测试与阶段归因协议，将表面形式敏感性、记忆形成失败、检索失败和记忆使用失败分离。**

### 0.3 推荐路线

优先采用两阶段路线：

1. **第一阶段：MemInvariantBench。** 先证明问题真实存在、可重复、不是基础模型的普通 prompt sensitivity，也不是 token budget 变化造成的假象。
2. **第二阶段：EquiMem。** 若 benchmark 观察到稳定缺口，再做具有规范化表示、来源保留和等价一致性目标的 memory method。

这条路线适合现有四卡 4090：第一阶段几乎不需要训练；第二阶段可先训练小型 reranker/controller，0.6B 或 1.5B 用于快速验证，7B/8B 用于正式实验。

---

## 1. 自动探索过程：哪些问题被排除了

本节保留候选问题池及淘汰原因，避免后续又绕回已经拥挤的方向。

| 候选问题 | 代表性同期工作 | 判断 | 原因 |
|---|---|---|---|
| 受控记忆状态的诊断、使用、修复全闭环 | SafeCommit、MemOps、StateMemBench、AgentMemoryBench、MemTX | 降级 | 组合完整但问题过宽，多个组成部分已有直接工作 |
| 无 oracle 的 memory/world repair locus | MemTX、From Faulty Memories、SagaLLM、HarnessRisk | 可做但高碰撞 | 修复位置不确定性仍有空间，但系统工程重、近邻工作密集 |
| 依赖图上的级联失效传播 | RECON、MemoRepair、From Faulty Memories | 淘汰为主创新 | RECON 已明确评测 cascading invalidation，其他工作已有依赖引导修复 |
| 最小充分证据集与 setwise memory | RECON、SMMBench、Router-Mem | 淘汰为主创新 | minimal necessary/sufficient proof subgraph 与 evidence sufficiency 已被覆盖 |
| 长期写入价值与 credit assignment | Memory-R2、CHIME、TRUSTMEM、Nemori | 淘汰为主创新 | 写入/更新的未来效用、偏好对和局部回滚奖励已成为密集方向 |
| 多 Agent 共享记忆一致性 | GateMem、Governed Shared Memory、CoAgent、TOKI | 淘汰为主创新 | ownership、并发、共享状态治理与事务语义已有多条工作线 |
| 自生成记忆导致 evidence laundering | Honest Lying、BeliefMem、Zombie Agents、Memory Contagion | 淘汰为主创新 | 自我强化、幻觉持久化和偏差传播已有直接定义 |
| 记忆删除与遗忘残留 | Deployment-Time Memorization、Memora、PersistBench | 淘汰为主创新 | forgetting residue、tombstone/full purge 和持久化清理已有工作 |
| 未知未来查询下的常驻记忆路由 | InMind、ProactAgent、Proactive Memory Agent、Nemori | 重要但拥挤 | InMind 明确留下 routing 问题，但主动检索、选择性注入和未来效用预测已有同期方法 |
| 同一语义、不同记忆实现下的行为不变性 | Faulty Memories、Beyond Memory Leaderboards、GroupMemBench；通用方法为 CheckList/Contrast Sets | **保留** | 邻近证据充分，但尚未发现完整的 matched memory-family、双侧契约和阶段归因 benchmark |

### 1.1 为什么不优先追 InMind 的“常驻路由”开放问题

[Keep It InMind](https://arxiv.org/abs/2607.24368) 的问题非常清楚：当 later query 与关键记忆之间只能通过世界知识建立联系时，query-conditioned retrieval 可能完全看不到该记忆。它报告关键记忆直接置于上下文时的间接任务准确率为 84.0%，而六类记忆系统最高仅约 14.4%；常驻状态诊断能恢复大部分差距。

但把“学习何时检索或注入记忆”直接作为方法主线，会立即与以下工作竞争：

- [Ask Only When Needed](https://arxiv.org/abs/2604.20572) 已将何时、检索什么建模为显式 policy action，并用 paired-branch process reward 训练；
- [Remember When It Matters](https://arxiv.org/abs/2607.08716) 已使用独立 memory agent 决定注入提醒或保持沉默，并报告 Terminal-Bench 与 tau2-Bench 的提升；
- [What Deserves Memory](https://aclanthology.org/2026.acl-long.1607/) 已从未来可预测性角度决定哪些经验值得保留；
- [Stop When Memory Suffices](https://arxiv.org/abs/2608.01285) 已训练 sufficiency router 决定是否继续扩大检索。

因此该问题仍重要，但直接做一个“memory router”不容易形成清晰的新颖性。它可以作为 MemInvariantBench 的一个应用场景或 EquiMem 的后续模块，而不应作为当前第一主线。

### 1.2 为什么 repair-locus 方向暂不作为第一主线

上一轮收紧得到的 ReconMemBench 研究“memory 与 world 不一致时到底修哪一边”。问题本身比大闭环清晰，但要做出可信结果，需要可执行 world simulator、audit log、补偿动作、不可逆副作用和长期复发检查，工程成本较高。同时 [From Faulty Memories to Corrected Actions](https://arxiv.org/abs/2608.10502)、[MemTX](https://arxiv.org/abs/2607.23929) 与 [RECON](https://arxiv.org/abs/2607.16716) 已覆盖大量相邻组件。

MemInvariantBench 的优势是：

- 因果变量更单一：只改变记忆实现或一个决定性语义条件；
- 先用现成 memory systems 即可验证，不依赖复杂训练；
- 可以从 QA 扩到 tool action，但首轮不必构造完整可逆世界；
- 若没有显著现象，可以低成本停止，不会先投入数月 simulator 工程。

---

## 2. 核心问题的严格定义

### 2.1 研究对象

给定：

- 原始跨会话历史 (H)；
- 由历史隐含的潜在事实、偏好、约束和事件状态 (S(H))；
- 当前查询或任务 (q)；
- memory system (F)，将历史写成持久记忆 (M=F(H))；
- native retriever/router (R)，返回可见记忆 (E=R(M,q))；
- action agent (A)，输出答案、工具调用或行动 (y=A(q,E))。

定义一组**语义保持变换** (T_{mathrm{inv}})，满足：

\[
S(T_{\mathrm{inv}}(H)) = S(H)
\]

也就是任务相关事实、来源、时间、权限、否定、数量和适用范围均不变，只改变表面实现。

定义一组**决定性语义变换** (T_{\Delta})，只改变一个会影响正确行为的条件：

\[
S(T_{\Delta}(H)) \neq S(H), \qquad d(S(T_{\Delta}(H)),S(H))=1
\]

其中 (d=1) 表示只改变一个预先标注的决定性字段，而不是任意改写整个场景。

### 2.2 语义等价记忆族

对每个 base case (b)，构造：

\[
\mathcal{F}_b^{\mathrm{inv}}=\{H_b,T_1(H_b),...,T_K(H_b)\}
\]

它们共享相同 gold state 与可接受行为集合。这个集合称为**语义等价记忆族**（semantic-equivalent memory family）。

再构造决定性对照：

\[
\mathcal{F}_b^{\Delta}=\{T_{\Delta_1}(H_b),...,T_{\Delta_L}(H_b)\}
\]

每个对照只改变一个决定性条件，并带有明确的 expected behavior relation，例如：

- 工具从 `book_flight` 变为 `ask_user`；
- 参数 `vegan=false` 变为 `vegan=true`；
- 从“可以执行”变为“必须拒绝或验证”；
- 从旧偏好切换到有更晚时间戳的新偏好。

### 2.3 两个不可混淆的概念

**表面一致不等于正确。** 两个变体都输出同一个错误答案，只能算 raw consistency，不能算 correct invariance。

**行为变化不等于敏感性正确。** 决定性条件改变后模型随机换了一个错误答案，也不能算 directional sensitivity；变化方向与最终结果都必须正确。

---

## 3. Research Questions

### RQ1：Memory-Realization Invariance

> 当历史所表达的任务相关语义不变、但记忆的措辞、分块、会话边界、独立事件顺序、冗余和压缩形式变化时，Agent 的形成结果、检索证据和最终行为是否保持正确且等价？

### RQ2：Decisive Sensitivity

> 当仅改变一个会影响决策的记忆语义条件时，Agent 能否在保持其他行为不变的同时，对应地改变答案、工具选择、参数、验证或拒绝策略？

### RQ3：Failure-Stage Attribution

> 行为不稳定主要来自 memory formation、retrieval/routing，还是在证据已经可见后的 memory use；不同 memory architecture 的失败位置是否不同？

### RQ4：Leaderboard Reliability

> 在单一记忆实现上得到的系统排名，是否能跨语义等价记忆族保持稳定；控制 token budget、reader 和 judge 后是否仍发生显著 ranking flip？

四个 RQ 的关系是连续的：RQ1 检查不该改变时是否改变，RQ2 检查应该改变时是否改变，RQ3 解释变化发生在哪里，RQ4 判断现有单点 benchmark 排名是否可信。

---

## 4. 为什么这是 Agent Memory 问题，而不只是 prompt robustness

审稿人最可能提出的质疑是：“这不就是 paraphrase robustness 吗？”必须从实验设计上回答，而不是只靠措辞。

### 4.1 干预发生在 memory formation 之前或 memory state 内部

普通 prompt robustness 通常保持知识库不变，只改当前 query。这里固定 (q)，改变的是跨会话历史的实现或写入后的持久 memory state，因此变化会穿过：

> history ingestion -> memory extraction/consolidation -> storage representation -> retrieval/routing -> memory-conditioned action

系统可能在写入时丢失否定、合并错误实体、因分块不同而拆散证据，或在检索时因措辞变化返回不同内容。这些都不是单轮 prompt test 能观察的。

### 4.2 必须加入 full-context control

对每个变体，都让同一个 reader 直接读取完整历史。如果 full-context reader 本身在等价变体上不稳定，则该 case 可能是普通语言模型敏感性或变换质量问题，不应直接归因于 memory system。

只有当：

- full context 稳定；
- oracle canonical memory 稳定；
- native memory pipeline 不稳定；

才有充分证据把主要问题定位为 Agent Memory pipeline。

### 4.3 评价对象包含持久状态与行动

除最终答案外，benchmark 还记录：

- memory write/update/delete 结果；
- 检索到的 proposition/source IDs；
- 工具名称与参数；
- use / verify / ask / ignore / abstain 等控制行为；
- 证据引用；
- token、延迟和检索预算。

这使它能够判断“同义历史是否形成同义 memory state”，而不只是判断两句回答是否相似。

---

## 5. 与最接近工作的边界

| 工作 | 已解决的问题 | 与本方案最接近之处 | 仍未覆盖的核心 |
|---|---|---|---|
| [Useful Memories Become Faulty](https://arxiv.org/abs/2605.12978) | 连续 consolidation 会把有益轨迹改写成有害记忆 | 同一轨迹池在不同更新日程下得到不同 memory | 未构造系统化语义等价家族、决定性对照和 formation/retrieval/use 阶段归因 |
| [Beyond Memory Leaderboards](https://arxiv.org/abs/2607.16848) | scientific memory 排名受粒度、预算、模态、judge 影响 | 证明 protocol sensitivity 和 ranking reversal | 主要控制系统协议，不把同一潜在记忆状态的多种等价实现作为成对测试对象 |
| [GroupMemBench](https://arxiv.org/abs/2605.14498) | 多人对话中的 speaker grounding、更新、术语歧义 | 发现 ingestion 抹去结构和词汇线索 | 每个潜在场景主要对应一个实现，不测试等价实现下行为是否应保持不变 |
| [Are We Ready For An Agent-Native Memory System?](https://arxiv.org/abs/2606.24775) | 将 memory 拆成 representation、extraction、retrieval/routing、maintenance 并做消融 | 提供系统级分解框架 | 不使用 matched semantic-equivalence families 和双侧行为契约 |
| [Text2Mem](https://aclanthology.org/2026.findings-acl.100/) | 用 schema contract 和 semantic invariants 执行 memory operation 指令 | 明确使用“semantic invariants” | 不评价同一历史语义经不同 realization 后的形成、检索和任务行为；对象是 memory-control language |
| [CAME-Bench/STITCH](https://aclanthology.org/2026.findings-acl.584/) | 长目标轨迹中的 contextual intent retrieval | 用 symbolic storyboard 再生成自然语言，适合借鉴构造 | 未对同一 storyboard 生成并比较多个等价 trajectory/memory realizations |
| [Keep It InMind](https://arxiv.org/abs/2607.24368) | 记忆与 query 仅经世界知识关联时的 retrieval blind spot | 使用 paired controls 定位 storage/knowledge/retrieval | 改变的是 query 类型和可见性，不测试语义等价 memory state 的实现敏感性 |
| [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/) | required/supportive/irrelevant memory 的战略使用 | 强调记忆不应一律使用 | 给定候选 memory pool，不改变同一语义状态的形成与实现 |
| [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/) | 长期记忆驱动 tool selection 与 parameter grounding | 提供 action-level evaluation | 不测试 action 对 memory realization 的不变性与决定性敏感性 |
| [Same Meaning, Different Scores](https://aclanthology.org/2026.lrec-1.363/) | 真值条件等价的词汇/句法变化导致模型和排名波动 | 提供 meaning-preserving perturbation 方法 | 对象是普通 LLM benchmark input，不经过持久 memory pipeline |
| [CheckList](https://aclanthology.org/2020.acl-main.442/) / [Contrast Sets](https://aclanthology.org/2020.findings-emnlp.117/) | 行为测试、不变性测试和局部决策边界 | 提供核心方法论 | 未定义 Agent Memory 的状态形成、检索证据、行动和阶段归因 |

### 5.1 可防守的 gap 表述

推荐论文表述：

> Existing agent-memory benchmarks typically evaluate one realization of each interaction history or memory state. Recent studies show that ingestion granularity, update schedules, and representation choices can materially change memory utility and even system rankings, yet these factors are usually treated as protocol details rather than controlled semantic variables. Consequently, current evaluations cannot determine whether a memory system preserves behavior across semantically equivalent realizations, remains sensitive to minimal decision-changing updates, or fails during formation, retrieval, or use.

对应中文：

> 现有 Agent Memory benchmark 通常只评价每段交互历史或记忆状态的一种具体实现。近期工作已经表明，摄入粒度、更新日程和表示方式会显著影响记忆效用，甚至改变系统排名，但这些因素通常仍被视为协议细节，而不是受控的语义变量。因此，现有评测难以判断：memory system 能否在语义等价实现之间保持正确行为，能否对最小的决定性更新产生必要响应，以及失败究竟发生在形成、检索还是使用阶段。

### 5.2 不能声称的内容

不能写：

- 首次发现 memory representation 会影响 Agent；
- 首次研究 Agent Memory robustness；
- 首次使用 semantic invariance；
- 首次发现 benchmark protocol 会影响排名；
- 首次用配对样本评价 memory；
- 首次分解 formation、retrieval 和 use。

可以写成：

> To our knowledge, we provide the first systematic agent-memory evaluation centered on matched semantic-equivalence families, paired decisive edits, and stage-aware attribution across memory formation, retrieval, and action.

正式投稿前仍需再次做 arXiv 与 OpenReview collision audit。

---

## 6. Benchmark 数据构造

### 6.1 先从符号状态出发，而不是直接让 LLM 改写文本

每个 case 先建立可执行的 canonical schema：

```json
{
  "entities": [],
  "events": [],
  "facts": [],
  "preferences": [],
  "constraints": [],
  "timestamps": [],
  "authority": [],
  "provenance": [],
  "query": {},
  "required_evidence_ids": [],
  "acceptable_actions": [],
  "forbidden_actions": []
}
```

生成流程：

1. 人工或规则定义 canonical world/memory state；
2. 由模板和 LLM 生成多种 history realization；
3. 用确定性 validator 检查 entity、time、negation、quantity、permission 和 provenance；
4. 用独立模型做语义核验，但不把 LLM judge 当作唯一真值；
5. 人工抽检高风险变换；
6. full-context reader 未达到稳定阈值的 family 被修订或剔除。

### 6.2 语义保持变换

首版建议六类，不要一开始追求几十种扰动：

| 变换类型 | 具体操作 | 必须保持不变的内容 | 主要压力位置 |
|---|---|---|---|
| 词汇/句法改写 | 同义替换、主动/被动、从句重排 | 真值条件、否定、程度、实体 | extractor、embedding retriever |
| turn segmentation | 一轮拆多轮、多轮合一轮 | speaker、时间、语义归属 | session parser、chunker |
| session regrouping | 改变会话边界或中断位置 | 事件顺序、跨会话身份 | session-level memory writer |
| independent-event permutation | 只重排无因果依赖的独立事件 | 时间戳与因果偏序 | streaming updater、consolidator |
| redundancy realization | 重复、释义复述、多个等价证据 | authority 与最终事实 | dedup、importance、retrieval |
| lossless compression/expansion | 在保留限定条件下压缩或展开 | scope、exception、quantity、permission | summarizer、memory budget |

不建议首版直接加入会改变证据权威性的 channel conversion，例如把用户本人陈述改成第三方转述。即使文本语义相近，authority 已经变化，不能算严格等价。

### 6.3 决定性语义变换

每个 base family 至少配两个 minimal delta：

| 变化类型 | 示例 | 预期行为关系 |
|---|---|---|
| 否定/极性 | “可以购买”变为“不要购买” | execute -> reject/ask |
| 数量或阈值 | 预算 1000 变为 100 | 高价选项 -> 低价选项/无解 |
| 时间更新 | 旧偏好被更晚陈述替代 | 使用 latest valid state |
| 权限范围 | “可查看”变为“可发送”或反向 | read-only -> action-safe / blocked |
| 身份归属 | 偏好属于用户 A 而非 B | 个性化行为必须切换 |
| 必要前提缺失 | 去掉唯一支持执行的条件 | execute -> verify/ask/abstain |

delta 变体应尽量维持词汇重叠和长度，使模型不能仅凭“文本变化更大”猜测标签变化。

### 6.4 首版任务领域

建议三个领域，每个领域都包含回答与动作：

1. **个人助理**：饮食限制、预算、日程、联系人、授权和偏好更新。
2. **工具型工作流**：邮件、日历、文件、表格或订单的 tool selection 与 parameter grounding。
3. **科研/知识工作**：论文结论、实验配置、结果版本和引用来源，但首版只做可验证的信息与工具操作，不做开放式科研质量判断。

第三个领域可以与用户现有 Zotero--Markdown--GitHub--server 工作流结合，但不应把 benchmark 限死为 scientific agent；它只是检验迁移性的一个领域。

---

## 7. 评测协议与阶段归因

### 7.1 固定变量

每个 family 内固定：

- query/task；
- canonical semantic state；
- gold evidence proposition IDs；
- reader model、system prompt 与 decoding；
- 可用工具及其 schema；
- retrieval token/character budget；
- judge 与 validator；
- 除目标变换外的历史长度区间。

对 compression、redundancy 和 segmentation 等可能改变 token 数的变换，应额外提供 length-matched subset，防止把预算变化误判为语义实现敏感性。

### 7.2 五级干预梯度

| 层级 | 输入给 Agent 的内容 | 用途 |
|---|---|---|
| `L0 No Memory` | 仅当前任务 | 测任务先验与无记忆上限/下限 |
| `L1 Full History` | 完整历史变体 | 检查变换有效性与 reader 的普通语言鲁棒性 |
| `L2 Oracle Canonical Memory` | 从符号状态生成的标准记忆 | 测理想 memory representation 下的 use 能力 |
| `L3 System All-Memory-Visible` | 被测系统形成的全部记忆，不经过 native retrieval | 分离 formation 与 retrieval |
| `L4 Native End-to-End` | 系统原生写入、检索、路由和行动 | 最终 benchmark 结果 |

可选增加 `L3.5 Oracle Retrieval from System Memory`：若系统能映射 source/proposition IDs，则从其已形成的 memory 中强制提供 gold-relevant records，用于进一步区分 retrieval 与 use。

### 7.3 故障定位逻辑

- `L1` 不稳定：普通 reader sensitivity 或变换无效，暂不能归因于 memory。
- `L1` 稳定而 `L2` 不稳定：canonical memory realization 或 action reader 有问题。
- `L2` 稳定而 `L3` 不稳定：formation/extraction/consolidation 造成语义漂移。
- `L3` 稳定而 `L4` 不稳定：native retrieval/routing 对 realization 敏感。
- gold evidence 已稳定可见但行动不稳定：memory use/controller 失败。

这套归因是本方案与只报告 aggregate accuracy 的关键区别。

### 7.4 输出协议

建议统一输出：

```json
{
  "final_answer": "...",
  "decision": "USE|VERIFY|ASK|IGNORE|ABSTAIN|EXECUTE|REJECT",
  "tool_calls": [{"name": "...", "arguments": {}}],
  "evidence_ids": [],
  "retrieved_memory_ids": [],
  "memory_updates": [],
  "confidence": 0.0
}
```

核心分数尽量由 deterministic validator 判定；LLM judge 只用于开放文本的语义等价辅助评分，并报告多 judge 或人工校准结果。

---

## 8. 指标定义

设 base family 数量为 (B)，第 (b) 个 family 有 (K_b) 个语义等价变体。(c_{b,k}\in\{0,1\}) 表示变体 (k) 的最终结果是否正确。

### 8.1 Family Worst-Case Accuracy（FWA）

\[
\mathrm{FWA}=\frac{1}{B}\sum_{b=1}^{B}\min_k c_{b,k}
\]

只有 family 中所有等价实现都正确，该 family 才计 1。它比平均准确率更能暴露“换一种分块就失效”的问题。

### 8.2 Correct Invariance Rate（CIR）

对每个等价变体对 ((i,j))，检查：

1. 两个结果都正确；
2. 工具动作、参数和控制决策满足预定义行为等价关系；
3. 证据集合在 proposition 层面语义等价。

\[
\mathrm{CIR}=\frac{1}{N_{\mathrm{pair}}}\sum_{b,i<j}
\mathbb{1}[c_{b,i}=1\land c_{b,j}=1\land \mathrm{EqBehavior}(y_{b,i},y_{b,j})]
\]

另报 Raw Pairwise Consistency，但不能把它当主指标，因为“一直错”也可能一致。

### 8.3 Decisive Sensitivity Rate（DSR）

对 base 与 minimal delta 对，要求二者分别正确，且行为变化满足 gold relation：

\[
\mathrm{DSR}=\frac{1}{N_{\Delta}}\sum_{b,l}
\mathbb{1}[c_b=1\land c_{b,l}^{\Delta}=1\land
\mathrm{ExpectedChange}(y_b,y_{b,l}^{\Delta})]
\]

### 8.4 Balanced Memory Contract Score（BMCS）

\[
\mathrm{BMCS}=\frac{2\cdot \mathrm{FWA}\cdot \mathrm{DSR}}
{\mathrm{FWA}+\mathrm{DSR}}
\]

它同时惩罚“不该变却变”和“该变却不变”。若任一侧很弱，总分都会下降。

### 8.5 Stage-specific metrics

- **Formation Proposition F1**：形成的 memory 是否覆盖 canonical proposition，并避免新增无支持命题。
- **Retrieval Evidence Recall/Precision**：按 proposition/source IDs 而不是字符串计算。
- **Action Equivalence Accuracy**：工具、参数、控制策略是否在等价变体中保持等价。
- **Evidence-grounded Action Rate**：正确行动是否引用了必要证据，而非碰巧答对。

### 8.6 Leaderboard Stability

- **Ranking Flip Rate**：系统对在不同 realization 上相对排名翻转的比例。
- **Kendall's tau**：各 realization 下系统排序与 canonical 排序的一致性。
- **Representation Regret**：同一系统在 family 最佳与最差 realization 之间的性能差。

最终榜单必须同时报告平均准确率、FWA、DSR、BMCS 和 ranking stability，不能再用一个 aggregate accuracy 掩盖不稳定性。

---

## 9. Baselines 与公平性控制

### 9.1 最小 baseline 集

1. `No Memory`；
2. `Full History`；
3. `BM25`；
4. `Dense Retrieval`；
5. `Hybrid BM25 + Dense`；
6. `Mem0`；
7. `A-MEM` 或另一个图/结构化 memory system；
8. `Always-visible Markdown/Profile`；
9. `Oracle Canonical Memory`；
10. `Oracle Evidence`。

第一版不必一次接十几个复杂系统。先保证稀疏、稠密、混合、结构化、始终可见和 oracle 六类机制都有代表。

### 9.2 公平性原则

- 所有系统使用同一个 answer/action model；
- 使用相同最大 evidence budget，同时报告系统原生预算结果；
- 分离 ingestion cost 与 query-time cost；
- 固定 decoding，随机系统至少跑三次；
- 保留 raw outputs、retrieval packets、memory snapshots 和 judge logs；
- 不允许某系统通过手工针对 benchmark 的 query rewriting 获得未声明优势；
- 对有专用 adapter 的系统，报告 adapter 配置与版本。

这些原则直接吸收 Beyond Memory Leaderboards 对 protocol interpretability 的警告。

---

## 10. 最小可证伪实验

### 10.1 Pilot 规模

- 48 个 base cases；
- 3 个领域，每个 16 个；
- 每个 base 生成 4 个 invariant variants 和 2 个 decisive deltas；
- 总计 (48\times(1+4+2)=336) 个运行实例/系统/模型；
- 人工审查全部 canonical cases，并抽查至少 30% 的生成变体；
- 先接 5--6 个 baseline，不训练。

模型建议：

- Qwen2.5-7B-Instruct；
- Llama-3-8B-Instruct；
- 一个较强闭源模型作为参考上界，若 API 成本允许；
- 0.6B 只用于流水线调试，不用于决定 benchmark 是否存在真实 gap。

### 10.2 Pilot 先回答的三个问题

1. 同一语义 family 内，native memory pipeline 是否出现显著性能波动？
2. 这种波动在 full context 下是否明显减弱，从而可归因于 memory pipeline？
3. 不同系统的最差 realization 是否不同，并造成 ranking flip？

### 10.3 Go / No-Go 条件

满足以下多数条件再扩成正式 benchmark：

- 人工语义等价审查一致性较高，目标为 Cohen's kappa >= 0.80；
- `Full History` 的 FWA >= 0.90，说明变换本身大体有效；
- 至少两个 memory systems 的平均准确率与 FWA 相差 >= 8 个百分点；
- 至少一个主要变换类别在两个模型上复现显著下降；
- `Oracle Canonical Memory` 能关闭 native pipeline 缺口的至少 30%；
- decisive delta 上 strong reader 的 DSR 不饱和但明显高于 native memory systems；
- 至少出现一次在 bootstrap 置信区间下仍稳定的 system ranking reversal。

出现以下情况则停止或转向：

- full-context 与 memory systems 同样不稳定：转为通用 language robustness，不再声称 memory-specific；
- 控制长度与预算后差异消失：现象主要是 budget effect；
- 所有强系统 FWA 与 DSR 均接近饱和：问题不再有足够难度；
- 语义等价无法可靠标注：缩小变换类型，只保留可由 schema 验证的变换；
- 只有单一系统或单一模型出现现象：不足以支撑通用 benchmark。

### 10.4 最小统计分析

- family-clustered bootstrap 置信区间；
- 配对 McNemar test 比较 canonical 与 variant；
- mixed-effects logistic regression，固定效应为 transform/system/model，随机效应为 base family；
- Kendall's tau 与 bootstrap ranking flip；
- 对多变换类别使用 Holm correction。

统计单位必须是 base family，而不是把同一家族的多个变体当成独立样本。

---

## 11. 第二阶段方法：EquiMem

Benchmark 若验证现象后，方法不应只是“再加一个 prompt”。推荐做一个轻量、可消融的 **EquiMem**。

### 11.1 核心思路

> 将自然语言历史先映射到带 provenance 的规范化命题/事件表示，在等价 realization 之间约束 memory formation 与 retrieval 的一致性，同时保留对决定性语义变化的可分辨性。

### 11.2 模块

1. **Typed canonicalizer**：抽取 entity、event、time、negation、quantity、authority、scope 和 provenance。
2. **Evidence-preserving store**：规范化 proposition 与原始 source span 双层保存，不让抽象完全替代证据。
3. **Equivalence-aware deduplication**：将释义和重复证据聚为同一 proposition group，但保留来源计数与权威性。
4. **Proposition-level retriever/reranker**：以 normalized propositions、query 和 action requirement 共同排序，不只匹配 raw chunk。
5. **Contract-aware controller**：根据证据选择 use、verify、ask、ignore、abstain 或 execute。

### 11.3 训练目标

对 invariant pair ((M_i,M_j))，要求 action/evidence distribution 接近；对 decisive pair ((M,M^{\Delta}))，要求关键行动分布至少相距 margin (m)：

\[
\mathcal{L}=\mathcal{L}_{task}
+\lambda_{inv}D(p(y|M_i,q),p(y|M_j,q))
+\lambda_{\Delta}\max(0,m-D(p(y|M,q),p(y|M^{\Delta},q)))
\]

这与用户此前关注的 pairwise/listwise learning-to-rank 自然连接：

- invariant variants 可作为同 relevance level 的组内一致性约束；
- decisive delta 中的必要证据与干扰证据构成 hard pair；
- 多证据候选可用 listwise loss 保持 proposition group 的整体排序。

不建议第一步就上 RL。先验证：canonicalization + pairwise reranking 是否能提升 FWA 和 DSR，同时不牺牲平均准确率。若 SFT/ranking 已有效，再考虑用 GRPO/GSPO 优化 controller 的长期工具结果。

### 11.4 低成本实现顺序

1. `EquiMem-Rules`：规则 schema + hybrid retrieval，无训练；
2. `EquiMem-Ranker`：训练小型 cross-encoder 或 0.6B reranker；
3. `EquiMem-SFT`：0.6B/1.5B controller 做 pairwise consistency SFT；
4. `EquiMem-7B`：在 Qwen2.5-7B 或 Llama-3-8B 上做正式 LoRA；
5. 只有当 tool outcome 存在稳定可验证 reward 时，再做 RLVR。

### 11.5 方法成功标准

方法不仅要提高平均准确率，还必须：

- 提高 FWA 和 CIR；
- 不降低 DSR；
- 降低 ranking/behavior variance；
- 在未见过的 transform type 上迁移；
- 不靠更大 retrieval budget 获益；
- 在至少两个领域与两个 reader model 上复现。

---

## 12. 推荐论文故事

### 12.1 Motivation

现有 benchmark 默认把一段 history 或 memory serialization 当作潜在状态的唯一观测。可是 persistent memory 需要经过摄入、分块、总结、合并、重组和检索；这些表面实现可能改变 Agent 行为，甚至翻转系统排名。若同一事实换一种无关紧要的表达就导致不同工具行动，那么单一 realization 上的高准确率并不能证明 Agent 真正“记住并使用”了信息。

### 12.2 Gap

已有工作分别研究了 protocol sensitivity、continuous consolidation drift、多用户结构损失、query-memory implicit association 和普通 LLM 的同义表述敏感性，但缺少一个 memory-native 的 matched intervention protocol，同时测试：

- 不该改变行为时是否稳定；
- 应该改变行为时是否敏感；
- 失败在 formation、retrieval 还是 use；
- leaderboard 是否跨 realization 可靠。

### 12.3 Contribution

1. 定义 persistent Agent Memory 的 semantic-equivalence family 与双侧行为契约；
2. 构造包含 invariant transforms 与 decisive deltas 的 benchmark；
3. 设计 oracle ladder 和 stage attribution protocol；
4. 揭示平均准确率掩盖的 worst-case failure 与 ranking instability；
5. 可选提出 EquiMem，验证规范化命题表示和一致性学习能否缓解该问题。

### 12.4 一句话摘要雏形

> We show that current agent-memory systems can change what they retrieve and do when the same persistent state is merely rephrased, resegmented, or reorganized. MemInvariantBench evaluates this hidden instability through matched semantic-equivalence families, minimal decision-changing contrasts, and stage-aware interventions that separate memory formation, retrieval, and use.

---

## 13. 审稿风险与应对

### 风险 1：只是普通鲁棒性 benchmark

应对：固定 query；干预历史与 memory state；加入 full-context control；记录 formed memory、retrieved evidence 与 tool action；用 oracle ladder 证明额外损失来自 memory pipeline。

### 风险 2：语义等价由 LLM 主观判断

应对：canonical schema 为真值；只允许受约束变换；确定性验证关键字段；人工双标；LLM judge 只作辅助。

### 风险 3：差异其实来自 token 长度

应对：提供 length-matched slice；固定 retrieval budget；分别报告原生协议与预算控制协议。

### 风险 4：一致性会奖励固执错误

应对：CIR 要求成对正确；与 DSR 组成 BMCS；同时报告 no-memory baseline。

### 风险 5：只证明 benchmark 不稳定，没有方法价值

应对：先用 `EquiMem-Rules` 或简单 canonicalization intervention 做机制验证；若 oracle canonical memory 能显著关闭缺口，就给出明确的方法路径。

### 风险 6：不同系统不暴露内部 memory

应对：定义最小 adapter contract：ingest、search、dump/export（若可用）、answer/action。黑盒系统至少评 end-to-end 与 retrieved packets；无法 dump 的系统不报告 formation attribution。

### 风险 7：工作名碰撞

本轮以 `MemEquivBench`、`MemInvariantBench` 和相关关键词检索，未发现同名正式项目；但名称仅为 working title，投稿前再次检查。

---

## 14. 下一步执行清单

### 本周：只做数据与协议验证

- 完成 canonical schema v0.1；
- 人工写 12 个 base cases，每个领域 4 个；
- 每个 case 生成 2 个 invariant variants 和 1 个 decisive delta；
- 跑 Full History、BM25、Dense、Hybrid 四条线；
- 检查是否能出现 memory-specific variance。

### 第二周：扩到 pilot

- 扩到 48 个 base cases、336 个实例；
- 接入 Mem0 与一个结构化 memory system；
- 实现 FWA、CIR、DSR、BMCS 与 ranking stability；
- 做 stage attribution 和 error taxonomy；
- 根据 Go / No-Go 条件决定扩建或停止。

### Pilot 成立后

- 扩展 transform taxonomy；
- 加 tool-action domain；
- 实现 EquiMem-Rules 与 EquiMem-Ranker；
- 再决定是否需要 0.6B/1.5B SFT 与 7B/8B 正式训练。

---

## 15. 最终判断

### 15.1 是否是可以接着做的问题

**可以，推荐先做 12-case smoke test，再做 48-case pilot。**

它当前比 repair-locus、主动 memory router、最小充分证据和长期 credit assignment 更适合作为第一主线，原因是：

- 问题边界单一且可被否证；
- 有三条独立同期证据支持问题重要性；
- 尚未发现完整等价 benchmark；
- 不需要先训练大模型；
- 能自然产生方法第二阶段；
- 可复用现有 Memory benchmark adapter 和用户的四卡 4090 资源；
- 即使最终发现现象不强，也能在两周内停止，机会成本可控。

### 15.2 当前置信度

- **问题重要性：高**；
- **问题定义清晰度：高**；
- **与 Agent Memory 的直接关系：高**；
- **新颖性置信度：中等偏高**；
- **实验可行性：高**；
- **顶会潜力：取决于 pilot 是否出现跨系统、跨模型的稳定 ranking flip 与 stage-specific finding**；
- **最大风险：被评价为通用鲁棒性工作，或语义等价构造不够严谨**。

最终建议不是立刻写大规模 benchmark，而是先验证一个最关键的事实：

> **当语义不变时，强 memory systems 是否真的会因为历史/记忆实现方式不同而做出不同且可归因于 memory pipeline 的行为？**

只要这个现象在控制 full context、长度和预算后仍稳定存在，MemInvariantBench 就有继续扩建的研究价值。

---

## 16. 核心参考文献

### 直接问题来源

1. Zhang et al. [Useful Memories Become Faulty When Continuously Updated by LLMs](https://arxiv.org/abs/2605.12978). arXiv preprint, 2026.
2. Sheverev et al. [Beyond Memory Leaderboards: Evaluating Scientific Memory as Budgeted Context Restoration](https://arxiv.org/abs/2607.16848). arXiv preprint, 2026.
3. [GroupMemBench: Benchmarking LLM Agent Memory in Multi-Party Conversations](https://arxiv.org/abs/2605.14498). arXiv preprint, 2026.
4. Zhou et al. [Are We Ready For An Agent-Native Memory System?](https://arxiv.org/abs/2606.24775). arXiv preprint, 2026.
5. Wang et al. [Text2Mem: A Unified Memory Operation Language for Memory Operating System](https://aclanthology.org/2026.findings-acl.100/). Findings of ACL 2026.
6. [Grounding Agent Memory in Contextual Intent](https://aclanthology.org/2026.findings-acl.584/). Findings of ACL 2026.

### Benchmark 边界

7. Wu et al. [StratMem-Bench: Evaluating Strategic Memory Use in Virtual Character Conversation Beyond Factual Recall](https://aclanthology.org/2026.acl-long.1491/). ACL 2026 Main Conference, Long Paper.
8. Shen et al. [Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents](https://aclanthology.org/2026.acl-long.370/). ACL 2026 Main Conference, Long Paper.
9. He et al. [MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks](https://arxiv.org/abs/2602.16313). arXiv preprint, 2026.
10. Wang et al. [EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective](https://arxiv.org/abs/2605.18421). arXiv preprint, 2026.
11. Li et al. [Keep It InMind: Benchmarking the Implicit-Association Blind Spot in Agent Memory](https://arxiv.org/abs/2607.24368). arXiv preprint, 2026.
12. Arya. [RECON: Benchmarking Agent Memory for Compositional Reasoning over Long Contexts](https://arxiv.org/abs/2607.16716). arXiv preprint, 2026.
13. Tan et al. [MemBench: Towards More Comprehensive Evaluation on the Memory of LLM-based Agents](https://aclanthology.org/2025.findings-acl.989/). Findings of ACL 2025.

### 方法论来源

14. Ribeiro et al. [Beyond Accuracy: Behavioral Testing of NLP Models with CheckList](https://aclanthology.org/2020.acl-main.442/). ACL 2020, Best Overall Paper.
15. Gardner et al. [Evaluating Models' Local Decision Boundaries via Contrast Sets](https://aclanthology.org/2020.findings-emnlp.117/). Findings of EMNLP 2020.
16. Kostic et al. [Same Meaning, Different Scores: Lexical and Syntactic Sensitivity in LLM Evaluation](https://aclanthology.org/2026.lrec-1.363/). LREC 2026.
17. Cao et al. [Evaluating the Retrieval Robustness of Large Language Models](https://arxiv.org/abs/2505.21870). arXiv preprint, 2025.

### 被比较的方法方向

18. Cai et al. [Ask Only When Needed: Proactive Retrieval from Memory and Skills for Experience-Driven Lifelong Agents](https://arxiv.org/abs/2604.20572). arXiv preprint, 2026.
19. Wu et al. [Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents](https://arxiv.org/abs/2607.08716). arXiv preprint, 2026.
20. Lin et al. [Stop When Memory Suffices: Evidence-Conditioned Progressive Execution for LLM Agents](https://arxiv.org/abs/2608.01285). arXiv preprint, 2026.
21. Ma et al. [What Deserves Memory: Adaptive Memory Distillation for LLM Agents](https://aclanthology.org/2026.acl-long.1607/). ACL 2026 Main Conference, Long Paper.

---

## 17. 检索说明

本轮使用的核心检索组合包括：

- `agent memory semantic invariance benchmark`；
- `semantics-preserving agent memory`；
- `agent memory robustness chunking ingestion representation`；
- `metamorphic long-term memory LLM agent`；
- `same memory different behavior LLM agent`；
- `update schedule agent memory`；
- `query-independent routing always-visible memory`；
- `future utility memory retention routing`；
- `MemEquivBench` 与 `MemInvariantBench` 精确名称检索。

检索结果中存在大量仅在评分时使用“semantic equivalence”的 benchmark。那类做法是判断预测答案与 gold answer 是否同义，不等于本文所说的**对输入历史/持久记忆构造语义等价 family，并要求整个 memory pipeline 的行为满足不变性契约**。两者必须在写作中明确区分。
