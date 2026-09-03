---
title: "Agent Memory P2 论文精读"
type: literature-notes
status: reviewed
created: "2026-09-03"
tags: ["agent-memory", "structure", "safety", "p2", "deep-reading"]
---

# P2：结构、程序性记忆与安全边界精读

P2 论文不会直接决定第一版 benchmark 的主任务，但它们决定扩展性：怎样制造结构性 hard negatives、怎样支持小模型、怎样把 privacy/protection 变成可测约束。

## 1. AnchorMem: Anchored Facts with Associative Contexts for Building Memory in Large Language Models

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2604.17377)；[代码](https://github.com/RayNeo-AI-2025/AnchorMem)。

**问题**：如何同时获得原子事实级检索精度与原始交互的完整语境，避免重写丢细节或实体图产生虚假连接？

**方法**：将每条记忆拆成可检索的原子事实锚点和不可变原始上下文；用 event 而非高频实体连接跨记忆内容，形成 associative event graph。查询先命中事实锚点，再沿映射恢复完整交互，做到“检索粒度细、生成上下文完整”。

**评测与发现**：LoCoMo 上优于 A-MEM、Mem0 等对照，证明 retrieval unit 与 generation context 不必是同一个对象。事件桥接比通用实体桥接更少产生错误关联。

**局限与启示**：事实和事件抽取依赖 LLM；节点随历史线性增长；只在 LoCoMo 验证；event 归并边界仍是启发式。benchmark 可分别提供 atomic evidence 与 source event，使系统能自由选择是否解耦，并测 source-grounding。

## 2. CLAG: Adaptive Memory Organization via Agent-Driven Clustering for Small Language Model Agents

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2603.15421)；[代码](https://github.com/dmis-lab/CLAG)。

**问题**：小模型对无关上下文更敏感，怎样避免全局 memory pool 中的跨主题干扰和错误演化？

**方法**：让 SLM agent 在线决定新 memory 属于哪个语义 cluster；更新和演化只在局部 cluster 内发生。检索采用两阶段流程，先选 cluster，再在 cluster 内做细粒度匹配，从组织层面缩小噪声空间。

**评测与发现**：多个 QA 数据集上优于全局池基线。其贡献不是新 embedding，而是把 clustering 变成 agent 可执行的 memory operation，并限制更新的影响范围。

**局限与启示**：冷启动时 cluster 尚未形成；路由能力受小模型上限限制；cluster 分裂阈值需调参；缺少大模型对照。我们的 baseline 应至少加入“小模型 + 分层/聚类检索”，并按模型规模报告 noise sensitivity。

## 3. HiGMem: A Hierarchical and LLM-Guided Memory System for Long-Term Conversational Agents

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2604.18349)；[代码](https://github.com/ZeroLoss-Lab/HiGMem)。

**问题**：如何避免向量检索为了召回而返回膨胀证据集，让下游 LLM 在大量弱相关信息中失去精度？

**方法**：用 event summary 与原始 dialogue turn 组成两层 memory，并保持双向可追溯链接。查询时先浏览事件摘要，LLM 再判断哪些细粒度对话轮“值得读取”，用语义推理替代纯 top-k 扩张。

**评测与发现**：LoCoMo10 五类问题中四类取得最优 F1，召回量降低一个数量级；笔记记录 evidence precision 提升显著且 recall 基本保持。对抗性问题收益尤其大，支持“更小、更准的 evidence set”这一判断。

**局限与启示**：记忆构建较慢；相关性判断依赖 LLM；时序题仍弱；只在 LoCoMo10 验证。benchmark 应绘制 answer quality 与 evidence budget 的 Pareto 曲线，而不是固定所有系统返回相同 k。

## 4. HyperMem: Hypergraph Memory for Long-Term Conversations

**出处**：ACL 2026；[论文](https://arxiv.org/abs/2604.08256)。

**问题**：pairwise 图难以表达多个 episode 共同属于一个主题的高阶联合依赖，怎样减少跨事件检索碎片化？

**方法**：构建 topic-episode-fact 三层超图，以 hyperedge 将多个 episode 或 facts 作为整体关联；进行无需训练的超图 embedding 传播。检索按 topic 到 episode 再到 fact 粗到细展开，用 RRF 融合 sparse/dense 排名并经 reranker 精排。

**评测与发现**：LoCoMo 上报告 LLM-as-judge 92.73%，多跳题提升突出。超图提供一种比固定二元边更直接的 group relation 表示。

**局限与启示**：构建依赖多次 LLM 抽取；在线增量更新成本不清楚；只处理单用户；依赖 LLM judge；Open Domain 较弱。我们不应把某种拓扑作为 benchmark gold，而应把“同组联合依赖”体现在 evidence set 中，让图、树、超图公平竞争。

## 5. Mem^p: Exploring Agent Procedural Memory

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2508.06433)；[代码](https://github.com/zjunlp/MemP)。

**问题**：agent 如何把任务轨迹转成可复用、可验证、可修补和淘汰的程序性知识，而不是每次重新探索？

**方法**：从轨迹中抽取细粒度分步指令和高层脚本，比较不同 build/retrieve/update 策略；新任务按 query 或状态召回 procedural memory，执行后依据 benchmark reward 进行添加、验证、反思与淘汰。论文系统拆解程序性记忆的生命周期，而不是只展示一个 prompt 技巧。

**评测与发现**：TravelPlanner 与 ALFWorld 上成功率随记忆累积提升、执行步数下降；反思式更新优于简单追加，memory 还能跨模型迁移。

**局限与启示**：任务类型有限；向量检索难识别结构等价任务；更新反馈仍较粗；容量和长期遗忘未覆盖。第一阶段可把 procedural memory 作为独立 track，避免与 personal factual memory 混成一个榜单。

## 6. Topology Matters: Measuring Memory Leakage in Multi-Agent LLMs

**出处**：ACL 2026 Findings；[论文](https://arxiv.org/abs/2512.04668)。

**问题**：多 agent 网络的连接拓扑如何影响一个 agent 私有 memory 被其他 agent 逐轮提取的风险？

**方法**：MAMA 在合成文档中植入带标签的 PII，先通过 Engram 阶段把隐私写入目标 agent，再在 Resonance 阶段让攻击 agent 最多交互 10 轮提取信息。实验系统比较 fully connected、ring、chain、binary tree、star 和 star-ring，改变 agent 数量、攻击者/目标位置和底座模型；泄露率用精确匹配到的 ground-truth PII 比例计算。

**评测与发现**：fully connected 泄露最高、chain 防护最强；攻击者与目标距离越短、目标中心性越高，泄露越严重；泄露前几轮快速增加后趋于平台；模型影响绝对值，但不改变拓扑相对排序。

**局限与启示**：PII 与任务均为合成；攻击和泄露度量集中于可精确匹配实体；真实协作中的间接推断、访问撤销和工具权限更复杂。它证明 `PROTECT` 不能只是单 agent 拒答，还应绑定 audience、source、agent identity 与传播路径。

## 7. Unveiling Privacy Risks in LLM Agent Memory

**出处**：ACL 2025；[论文](https://arxiv.org/abs/2502.13172)；[代码](https://github.com/wangbo9719/MEXTRA)。

**问题**：攻击者能否在黑盒条件下利用 agent 工作流，从记忆模块中提取其他用户的敏感查询？

**方法**：MEXTRA 设计 locator + aligner 两部分攻击 prompt：先把 agent 引导到目标 memory 范围，再让输出形式与系统正常任务对齐，绕过普通“重复上下文”攻击在 agent pipeline 中失效的问题；同时自动生成多样攻击提示。在医疗和网购 agent 上，以提取到的私人查询衡量泄露。

**评测与发现**：不同 memory retrieval 函数的泄露差异明显，说明隐私风险并非只由 LLM 决定，检索器和 prompt workflow 都是攻击面。

**局限与启示**：只测两类 agent 与单一主模型；memory 静态不更新；缺少系统防御；输入过滤可能改变结果。我们的 `forbidden evidence` 应在 retriever 输出和 final response 两处评分，分别测 exposure 与 disclosure。

## P2 横向结论

- AnchorMem、HiGMem、HyperMem 说明 memory representation 应与 retrieval budget、上下文恢复和高阶关联一起评价。
- CLAG 说明相同 noise 对 3B/7B 小模型的伤害可能显著高于大模型，榜单应分模型规模。
- Mem^p 说明 factual/personal memory 与 procedural/experience memory 的输入、评价和错误类型不同，宜分 track。
- Topology Matters 与 MEXTRA 说明 privacy 不只是最终拒答，至少包括 storage scope、retrieval exposure、cross-agent propagation 和 output disclosure 四层。

P2 最适合作为 benchmark v1.1 扩展。v1 的主线仍应优先完成单 agent、多 session、可自动验证的 factual/episodic management；权限字段从第一版 schema 就保留，但不必一开始实现复杂 multi-agent topology。
