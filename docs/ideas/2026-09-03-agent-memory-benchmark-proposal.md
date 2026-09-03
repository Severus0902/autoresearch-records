---
title: "MemoAgentBench-Lite Proposal"
type: idea
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agentic-memory", "agentic-rag", "benchmark", "proposal"]
---

# MemoAgentBench-Lite：面向 Agentic RAG 的记忆能力评测

## 一句话问题定义

现有 RAG/agent benchmark 难以评估智能体在跨 session 动态交互中是否能正确写入、更新、检索、遗忘并使用 memory 来完成后续任务。

## Motivation

放弃 KG 场景后的核心动机是：KG reasoning 的上限被图谱、实体链接、候选子图和多跳路径强约束住，资源不足时很难形成明显优势；而 memory 是 agentic RAG 的通用基础设施，benchmark 可以在不做大规模训练的情况下形成清晰贡献。

现有 benchmark 有两类缺口：

- 长上下文 memory benchmark 多数仍偏“在历史里找答案”，不充分评估 memory 写入、更新、遗忘、权限和任务使用。
- agent benchmark 多数评估单次任务规划和执行，不要求 agent 把前面 session 的经验沉淀为 memory 并影响后续行为。

因此我们可以把论文故事放在：

> 从静态长上下文回忆，走向动态 agentic memory lifecycle evaluation。

## Benchmark 范围

目标不是一次性做一个巨大的 benchmark，而是做一个轻量、可复现、覆盖关键 memory lifecycle 的 benchmark。

核心场景：

1. 多 session 用户偏好：用户偏好会逐步暴露、细化、冲突或改变。
2. 工具结果记忆：agent 调用搜索、日历、文件、数据库等工具后，需要把关键结果写入 memory。
3. 历史经验复用：前一个任务中成功或失败的经验，应影响后续任务策略。
4. 事实更新：旧事实被新事实覆盖，评估是否正确使用最新 memory。
5. 噪声和 hard negatives：memory store 中存在相似但无关或过期信息。
6. 权限/隐私：某些 memory 不应在当前用户、任务或权限域下被使用。

## 数据格式草案

一个样本由 `episodes` 和 `eval_query` 组成：

```json
{
  "task_id": "memo_lite_0001",
  "domain": "personal_assistant",
  "memory_skills": ["write", "update", "retrieve", "use"],
  "episodes": [
    {
      "session_id": "s1",
      "messages": [
        {"role": "user", "content": "我下周去上海出差，偏好靠近地铁的酒店。"},
        {"role": "assistant", "content": "好的，我会记住。"}
      ],
      "expected_memory_ops": [
        {
          "op": "add",
          "type": "preference",
          "content": "用户出差住宿偏好靠近地铁",
          "valid_from": "s1"
        }
      ]
    }
  ],
  "eval_query": {
    "session_id": "s3",
    "user": "帮我选一个上海酒店。",
    "required_memory": ["用户出差住宿偏好靠近地铁"],
    "forbidden_memory": [],
    "answer_constraints": ["推荐靠近地铁的酒店"]
  }
}
```

## 评测指标

- `memory_write_f1`：该写的 memory 是否写入。
- `memory_update_acc`：新事实是否覆盖旧事实。
- `selective_forgetting_acc`：过期或要求遗忘的 memory 是否不再使用。
- `retrieval_recall`：required memory 是否被检索到。
- `retrieval_precision`：检索结果中无关/过期 memory 比例是否低。
- `answer_success`：最终回答或动作是否满足任务目标。
- `memory_grounding`：回答是否能追溯到正确 memory。
- `privacy_violation_rate`：是否使用 forbidden memory。
- `cost`：token、latency、storage。

## Baseline

第一批 baseline 不训练：

- `NoMemory`：只看当前 query。
- `FullHistory`：把所有历史放进上下文，作为强但昂贵的基线。
- `BM25Memory`：文本 memory + BM25 retrieval。
- `VectorMemory`：embedding retrieval。
- `SummaryMemory`：按 session 做摘要。
- `StructuredMemory`：JSON profile / facts / preferences。
- `HybridMemory`：summary + vector + structured filter。
- `Mem0`：生产型 memory layer。
- `Letta/MemGPT`：stateful agent memory framework。
- `A-MEM-style`：linked note / Zettelkasten memory。
- `MIRIX-style`：typed memory managers。

后续可选训练：

- memory operation classifier：预测 ADD/UPDATE/DELETE/NOOP。
- memory retrieval reranker：对 required memory 和 hard negative memory 做排序。
- preference-aware memory gate：判断什么时候使用 memory，什么时候忽略 memory。

## 创新点候选

### 创新点 1：Memory Lifecycle Evaluation

不只测“能不能回忆”，而是把 memory 拆成 write、update、retrieve、forget、use 五个阶段分别评测。

### 创新点 2：Agentic Usefulness

memory 的好坏不只由 retrieval recall 决定，还由它是否能改进后续任务成功率决定。

### 创新点 3：Dynamic Conflict and Permission

加入偏好变化、事实冲突、过期信息、权限边界，避免 benchmark 退化成简单历史 QA。

### 创新点 4：Backend-Agnostic Evaluation

同一套 schema 可以比较 full-history、RAG、summary、structured memory、Mem0、Letta、MIRIX 等不同 backend。

### 创新点 5：Small-Resource Friendly

主要跑 evaluation 和 memory backend，不强依赖大模型训练。4 卡 4090 足够做本地 7B/8B reader、embedding/reranker、小规模 agent rollout。

## 最小闭环

第一轮只做 50-100 个人工/半自动样本：

1. 构造 5 个 domain：travel、calendar、shopping、coding assistant、research assistant。
2. 每个 domain 10-20 个 multi-session tasks。
3. 每个 task 包含 3-5 个 sessions。
4. 每个样本标注 expected memory ops、required memory、forbidden memory 和 answer constraints。
5. 跑 no-memory、full-history、BM25、vector、summary、structured memory 五个 baseline。
6. 评估 memory lifecycle 指标和最终 answer success。

## 和已有工作的区别

- 相比 LoCoMo/LongMemEval：我们更强调 memory 操作和后续任务使用，而不只是长期对话 QA。
- 相比 MemoryAgentBench：我们可以做更轻量、更 agentic RAG-oriented 的任务 schema，强调工具结果、权限和可插拔 memory backend。
- 相比 MemoryBench：我们不只模拟用户反馈学习，也评估 memory write/update/retrieve/use 的完整生命周期。
- 相比 MemoryArena：我们先做 Lite 版，牺牲复杂环境，换取快速复现和可控扩展。

## 当前推荐路线

先写 benchmark，不急着 method。

执行顺序：

1. 精读并复现 LongMemEval / MemoryAgentBench 的最小子集。
2. 完成 `MemoAgentBench-Lite` schema 和 20 条 pilot data。
3. 实现 baseline runner：NoMemory、FullHistory、BM25Memory、VectorMemory、SummaryMemory。
4. 设计 LLM-as-judge + rule-based hybrid evaluator。
5. 根据 pilot 结果决定是否扩展到 100-500 条数据。

这个方向可以先投成 benchmark / dataset / evaluation paper；如果后续需要方法创新，再在 memory gate、memory update policy 或 retrieval reranker 上加轻量方法。
