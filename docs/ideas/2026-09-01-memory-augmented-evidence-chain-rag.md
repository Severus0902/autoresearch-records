---
title: "Memory-Augmented Evidence-Chain RAG：第二场景方案"
type: idea
status: open
created: "2026-09-01"
zotero: ["@yangHotpotQADatasetDiverse2018", "@hoConstructingMultihopQADataset2020", "@trivediMuSiQueMultihopQuestions2022", "@trivediInterleavingRetrievalChain2023", "@gaoEnablingLargeLanguage2023", "@asaiSelfragLearningRetrieve2024", "@yanCorrectiveRetrievalAugmented2024", "@dongRAGcriticLeveragingAutomated2025", "@gutierrezHippoRAGNeurobiologicallyInspired2025", "@guoLightRAGSimpleFast2025", "@yuGraphRAGR1GraphRetrievalaugmented2026", "@jiangAgenticRagR1Agentic2026", "@shinnReflexionLanguageAgents2023", "@packerMemGPTTowardsLLMs2023", "@xuAMEMAgenticMemory2025", "@chhikaraMem0BuildingProductionReady2025", "@maMemChainLearningInterpretable2026"]
tags: ["rag", "memory", "rlvr", "evidence-chain", "multi-hop-qa", "verifiable-reasoning"]
---

# Memory-Augmented Evidence-Chain RAG：第二场景方案

## 一句话判断

可以把第二场景定为 **RAG + memory**，但不要写成“给 RAG 加长期记忆”。更好的定义是 **Memory-Augmented Evidence-Chain RAG**：让 agent 在多跳文本问答或带引用生成中学习何时读取、验证、使用和写回 memory，并用答案正确性、证据支撑和 citation faithfulness 构成可验证反馈。

这个场景和 KGR 主线的关系是：KGR 里的 `entity/relation/path` 对应 RAG 里的 `document/span/evidence chain`；KGR 的 path verifier 对应 RAG 的 supporting fact、citation support 和 answer verifier。它适合作为第二场景，用来证明方法不是 KG-specific trick。

## 要解决的问题

问题可以定义为 **verifiable memory use for budgeted evidence-chain retrieval**：

```text
Input:
  q: user question
  D: external document corpus
  M: verified memory store built only from training trajectories
  B: retrieval/tool/token budget
  V_text: answer, evidence and citation verifier

Goal:
  produce answer y and evidence chain e_1 ... e_n
  maximize answer correctness and evidence support
  minimize retrieval cost and memory-induced shortcuts
```

每一步 agent 可以执行的动作是：

```text
retrieve(query)
rewrite_query(query, feedback)
read_memory(q, state)
select_evidence(doc_id, span_id)
verify_evidence(answer_claim, evidence)
answer(evidence_chain)
write_memory(trajectory, verifier_feedback)
prune_memory(memory_id, utility)
stop()
```

核心不是“memory 里有没有相关文本”，而是 **memory 是否改变了检索推理策略，并且这种改变能被 verifier 归因**。

## Memory 存什么

RAG 场景里的 memory 不应该存测试问题答案，也不应该存整段可直接回答的问题。更合适的记忆单元是策略级、证据链级、失败级信息：

| Memory 类型 | 示例 | 为什么可用 |
|---|---|---|
| Query decomposition memory | `bridge-question -> find bridge entity first, then retrieve target attribute` | 复用问题分解策略，不直接泄漏答案。 |
| Retrieval strategy memory | `film award comparison -> retrieve award page before person page` | 改变检索顺序和 query rewrite。 |
| Evidence-chain pattern memory | `two-hop comparison -> need evidence for both entities plus comparison criterion` | 提高 supporting fact 覆盖。 |
| Failure memory | `semantic-neighbor page caused unsupported answer` | 用作 negative memory，减少重复错误。 |
| Stop/continue memory | `answer string found but missing citation for bridge entity -> continue retrieve` | 改善过早停止。 |

因此，memory 不是上下文缓存，而是一个会被训练、验证和剪枝的外部策略状态。

## 与普通 RAG 的差别

如果只是把历史笔记或历史检索结果拼进 prompt，reviewer 很容易认为这是普通 long-context RAG。这个方案必须让 memory 进入四个可消融位置：

| 位置 | 设计 | 消融问题 |
|---|---|---|
| Candidate generation | memory 生成候选 query rewrite、候选 evidence chain template、负向检索约束。 | memory 是否改变 search space。 |
| Action ranking | 同一 state 下比较 memory-supported action 与 no-memory action。 | memory 是否帮助下一步选择。 |
| Reward attribution | 只奖励带来可验证收益的 memory，例如 supporting fact F1 提升或 retrieval cost 下降。 | memory 是否真的有因果贡献。 |
| Write-back/pruning | 只有经过 verifier 标注且有 utility 的轨迹写入 memory；低效或误导 memory 降权。 | memory 是否越用越干净。 |

## 训练范式

第一阶段不需要直接做完整在线 RL，可以从 ranking 和 RLVR 的组合开始：

1. **Pointwise evidence scoring**：判断单个 retrieved span 是否支持某个 answer claim，训练 citation/support verifier 或 reranker。
2. **Memory-contrastive pairwise action ranking**：在同一个 state 下构造 `verified-memory action > no-memory action`、`verified-memory action > spurious-memory action`、`continue-retrieve > premature-stop` 等 pair。
3. **Listwise evidence-chain reranking**：对完整 evidence chain 排序，优先选择答案正确、证据完整、引用可追溯、成本低的 chain。
4. **RLVR/GRPO fine-tuning**：把 hard verifier、GRM 和 memory utility 放回环境中优化 action policy。

奖励可以写成：

```text
R = R_answer
  + lambda_1 * R_evidence_support
  + lambda_2 * R_citation_faithfulness
  + lambda_3 * R_chain_completeness
  + lambda_4 * R_memory_utility
  - lambda_5 * Cost
```

其中 `R_memory_utility` 不奖励“读了 memory”，只奖励 memory 带来的可验证增益：

```text
R_memory_utility =
  score(policy with selected memory)
  - score(policy under empty or shuffled memory)
```

可操作的近似包括：supporting fact F1 delta、retrieval recall@k delta、steps-to-answer delta、unsupported citation rate delta、重复检索次数 delta。GRM 可以生成过程诊断，但最终 reward 要被 `V_text` 封顶，避免语言奖励模型鼓励看似合理但证据不支持的回答。

## 数据集与评测

| 阶段 | 数据集 | 用法 |
|---|---|---|
| Pilot | HotpotQA `@yangHotpotQADatasetDiverse2018` | 有多跳问题和 supporting facts，适合先验证 evidence-chain memory。 |
| Pilot/正式 | 2WikiMultiHopQA `@hoConstructingMultihopQADataset2020` | reasoning steps 更明确，适合做分解和证据链评估。 |
| Stress test | MuSiQue `@trivediMuSiQueMultihopQuestions2022` | 通过 single-hop composition 构造多跳问题，更能压制 shortcut。 |
| Method baseline | IRCoT `@trivediInterleavingRetrievalChain2023` | 强检索推理 baseline，适合比较 interleaved retrieval 与 memory-guided retrieval。 |
| Citation scenario | ALCE `@gaoEnablingLargeLanguage2023` | 如果要强调 citation faithfulness，可作为引用生成评测补充。 |

核心指标：

| 指标 | 含义 |
|---|---|
| Answer EM/F1 | 最终答案是否正确。 |
| Supporting fact F1 | 证据链是否覆盖 gold supporting facts。 |
| Citation precision/recall | 生成答案是否被引用文档支撑。 |
| Retrieval recall@k | top-k 检索是否覆盖支持证据。 |
| Evidence-chain completeness | 多跳证据是否完整，而不是只命中答案字符串。 |
| Steps-to-answer / tool cost | 在预算内完成推理的效率。 |
| Memory utility delta | memory 相比 empty/shuffled/unverified memory 的可验证收益。 |
| Leakage check | dev/test 的问题、答案、gold evidence 不得进入 memory。 |

## Baseline

RAG + memory 第二场景的 baseline 需要分层，不要只和最弱的 vanilla RAG 比：

| 层级 | Baseline | 目的 |
|---|---|---|
| Retrieval-only | BM25 RAG、dense/vector RAG、hybrid RAG | 确认基础检索难度。 |
| Multi-step RAG | multi-query RAG、Self-Ask/RAG、IRCoT | 对比多步检索推理。 |
| Self-correction RAG | Self-RAG、CRAG、RAG-Critic | 对比检索、生成、critic 的闭环。 |
| Graph/document memory | HippoRAG、LightRAG、GraphRAG-R1 | 对比图式或 memory-like 检索增强。 |
| Agentic memory | Reflexion、MemGPT/Mem0、A-MEM、MemChain | 对比通用 agent memory 是否足够。 |
| Internal ablation | no-memory、unverified-memory、verified-memory without GRM、GRM without memory、full method | 证明 memory 和 reward 各自贡献。 |

如果论文仍以 KGR 为第一场景，ToG/RoG/GCR/EoG 是 KGQA 主 baseline；RAG + memory 是第二场景，不需要和所有 KGR baseline 直接混跑。

## 0.6B 快速验证

0.6B 模型不建议直接承担最终答案生成。更稳的 pilot 是把它训练成 **evidence-chain action selector**：

```text
state_t =
  question
  current retrieved docs/spans
  current evidence chain
  verifier feedback
  top-k verified memory hints

output_t =
  {"action": "retrieve", "query": "..."}
  {"action": "select_evidence", "doc_id": "...", "span_id": "..."}
  {"action": "rewrite_query", "query": "..."}
  {"action": "stop"}
```

最小实验设置：

1. 数据：HotpotQA 或 2WikiMultiHopQA 先抽 500 到 2000 条训练样本，固定 dev/test。
2. 索引：固定 Wikipedia paragraph index，BM25 + dense hybrid retrieval。
3. Memory：只从 train trajectories 生成，记录 query pattern、rewrite、evidence-chain template、失败检索和 stop mistake。
4. 训练：先 SFT 行为克隆，再做 memory-contrastive pairwise ranking，最后小规模 GRPO/RLVR。
5. 对比：empty memory、random memory、unverified memory、verified memory、verified memory + GRM。
6. 放大：pilot 有信号后，用 Qwen2.5-7B 和 Llama3-8B 做正式 agent policy 或 answer generator。

第一周的成功标准不是超过 SOTA，而是看到一个清晰信号：在相同检索预算下，verified memory 能提高 supporting fact F1 或降低 steps-to-answer，并且 unverified/random memory 不应带来同等收益。

## 论文动机写法

可以这样写：

> Existing RAG systems retrieve evidence for each query largely from scratch. Even when an agent repeatedly encounters similar multi-hop decomposition patterns, retrieval failures and evidence-chain mistakes, most systems lack a verifiable mechanism to reuse such experience without turning memory into an answer cache. We study whether language agents can learn to use verified memory as a strategy prior for evidence-chain retrieval, and optimize memory use through verifier-grounded rewards.

中文对应：

> 现有 RAG 系统通常把每个 query 当成一次独立检索，即使训练过程中已经出现过相似的问题分解模式、失败检索和证据链错误，也缺少一种可验证机制把这些经验复用到新 query 中。同时，直接加入长期 memory 容易退化成答案缓存或 prompt 增广。因此，我们研究 agent 能否把经过 verifier 标注的历史检索轨迹作为策略先验，并通过 answer support、citation faithfulness 和 memory utility reward 学习何时使用、如何使用以及何时忽略 memory。

不建议写成：

```text
We add memory to RAG.
We use memory to improve long-context QA.
We store past questions and answers for better retrieval.
```

这几种表述都会削弱创新点。

## 核心文献与出处

| 文献 | Zotero | 接收/出处 | 在本方案中的角色 |
|---|---|---|---|
| HotpotQA | `@yangHotpotQADatasetDiverse2018` | EMNLP 2018 | 多跳文本 QA pilot 数据集。 |
| 2WikiMultiHopQA | `@hoConstructingMultihopQADataset2020` | COLING 2020 | 有 reasoning steps 的多跳 QA 数据集。 |
| MuSiQue | `@trivediMuSiQueMultihopQuestions2022` | TACL 2022 | 更难的多跳组合泛化压力测试。 |
| IRCoT | `@trivediInterleavingRetrievalChain2023` | ACL 2023 | interleaved retrieval + CoT baseline。 |
| ALCE | `@gaoEnablingLargeLanguage2023` | EMNLP 2023 | 引用生成和 citation faithfulness 评估。 |
| Self-RAG | `@asaiSelfragLearningRetrieve2024` | ICLR 2024 | 检索、生成、critic 的自反思 baseline。 |
| CRAG | `@yanCorrectiveRetrievalAugmented2024` | arXiv/CoRR 2024 预印本 | corrective retrieval baseline。 |
| RAG-Critic | `@dongRAGcriticLeveragingAutomated2025` | ACL 2025 | critic-guided agentic RAG baseline。 |
| HippoRAG | `@gutierrezHippoRAGNeurobiologicallyInspired2025` | NeurIPS 2024 | long-term memory / graph-like RAG 近邻。 |
| LightRAG | `@guoLightRAGSimpleFast2025` | Findings of EMNLP 2025 | 轻量图式 RAG baseline。 |
| GraphRAG-R1 | `@yuGraphRAGR1GraphRetrievalaugmented2026` | WWW 2026 | GraphRAG + process-constrained RL 近邻。 |
| AgenticRag-R1 | `@jiangAgenticRagR1Agentic2026` | arXiv/CoRR 2026 预印本，未确认正式接收 | agentic RL + retrieval + stack memory 近邻，需要重点区分。 |

## 当前建议

第二场景就用 RAG + memory，但论文里要命名为 **Memory-Augmented Evidence-Chain RAG**。它最适合承担两个作用：

1. 证明 KGR 主线里的 memory interface 可以迁移到文本证据链推理。
2. 帮你把贡献从“又一个 KGR agent”提升为“verifiable memory-augmented reasoning”。

如果时间有限，优先做 KGR 第一场景；RAG + memory 先设计成轻量第二实验。若 RAG 场景的 memory utility 信号很强，再考虑把它提升为主场景。
