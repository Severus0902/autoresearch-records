---
title: "面向 Agentic 知识图谱推理的记忆条件排序奖励学习"
type: idea
status: active
created: "2026-09-02"
tags: ["agentic-kgr", "memory", "ranking", "pairwise", "listwise", "grpo", "rlvr", "opd", "reward-modeling"]
related_docs:
  - "docs/ideas/2026-09-02-ranking-based-agentic-kgr-opd.md"
  - "docs/results/2026-09-02-idea1-stage1-7-validation-summary.md"
---

# 面向 Agentic 知识图谱推理的记忆条件排序奖励学习

## 一句话定义

在 query-conditioned 局部 KG 状态中，agent 每一步面对多个候选 action/path；本方向要解决的是：如何利用可验证 memory 和 pairwise/listwise ranking reward 显式学习这些候选之间的相对优劣，而不是只对单条推理轨迹做 pointwise 打分。

## 核心问题定义

给定自然语言问题 `q`、topic entities、局部知识图谱 `G_q`、当前搜索状态 `s_t`、候选动作集合 `A_t` 和可检索记忆 `M_t`，学习一个策略：

```text
pi_theta(a_t | q, G_q, s_t, A_t, M_t)
```

使模型能在有限步数内选择更可能到达答案实体的 relation/entity/path，同时避免无效跳转、dead-end、过早停止和误用 memory。

这个问题的关键不只是“某条轨迹是否正确”，而是：

```text
在同一个 query + graph state 下，
candidate_action_1, candidate_action_2, ..., candidate_action_k
谁相对更好？
memory 是否应该改变这些 action 的排序？
```

## 与 RoG / EoG / BoG 的 Gap

RoG 主要通过 query-to-relation-path planning 约束 KG 上的路径检索，把自然语言问题转化为可在 KG 中匹配的 relation-path plans。

EoG 和 BoG 进一步把 RoG-style graph-grounded reasoning 推向 agentic graph exploration：EoG 强调让模型自主探索有效 reasoning path，BoG 强调在 dead-end 后通过 backjump 恢复历史状态并重新探索。二者的主要创新都集中在“如何沿着 KG 推理出正确路径”，而不是提出一个全新的初始 KG retriever。

本方向的 research gap 是：

> RoG 主要通过 query-to-relation-path planning 约束 KG 检索；EoG/BoG 在 RoG-style candidate graph/path 基础上进一步学习探索策略。但这些方法没有显式把每一步候选 action/path 的竞争关系建模为 ranking problem，因此 pointwise reward 难以充分利用 hard negatives、memory support 和多候选路径之间的相对优劣。

需要注意边界：EoG/BoG 使用 GRPO 时会对同一 query 的多条 rollout 做 group-relative normalization，这不是完全没有组内比较；但它们没有把候选 action/path 之间的 pairwise/listwise preference 作为 reward modeling 或 policy learning 的核心对象。

BoG 中的 notebook/memory 更像 query 内部的短期搜索状态记录；本方向如果主张 memory，需要把贡献放在 cross-query verified memory、memory utility、memory gate 和 memory-conditioned ranking 上，而不是简单说“加入记忆模块”。

## 为什么 Pointwise Reward 不够

EoG/BoG-style reward 大多可以抽象为：

```text
single trajectory -> verifier score
same-query rollouts -> GRPO group normalization
```

这会留下几个问题：

1. 缺少相对选择信号：agent 每一步真正要做的是从多个候选 action 中选一个，但 pointwise reward 只告诉模型单条轨迹好不好。
2. 难以利用 hard negatives：同一实体邻域中语义相似、relation 相近但会走向 dead-end 的动作，正是最有训练价值的负例。
3. 局部合理不等于全局有效：某个 relation 看似相关，但可能不能到达答案；只看单条路径得分容易奖励“看起来合理”的错误路径。
4. Memory 的作用难以归因：memory 既可能帮忙，也可能误导。pointwise reward 很难回答“使用 memory 的 action 是否真的优于不用 memory 的 action”。
5. 多候选路径之间的全局顺序被浪费：如果已经有多条 candidate path，listwise 信号能直接约束最优路径应排在更高位置。

因此更顺的 motivation 不是“我们给 KGR 加 memory”，而是：

> Agentic KGR 的搜索决策天然是 query-conditioned ranking problem。我们将候选 action/path 的相对优劣、可验证 memory 的使用收益，以及最终答案正确性统一到 ranking-aware RLVR 框架中。

## Idea List

### Idea A: Memory-Conditioned Pairwise Next-Hop Reward

一句话问题定义：在同一 query 和同一局部 KG 状态下，如何让模型学会 `good next-hop > hard negative next-hop`，并判断 verified memory 是否应该改变下一跳选择。

背景：RoG/EoG/BoG 都依赖局部图或候选路径，但训练信号更偏单轨迹验证；逐跳搜索本质上更接近 pairwise action selection。

方案：

- 对每个 `(q, s_t)` 枚举候选 relation/entity/action。
- 正例是 gold next relation、可到达答案的 supporting relation，或 verifier 判定能推进到答案的 action。
- 负例优先构造 hard negatives，包括同 domain relation、rule-top-wrong、memory-top-wrong、语义相近但 dead-end 的 action。
- 训练或奖励时显式建模：

```text
(q, s_t, M_t, a_good) > (q, s_t, M_t, a_bad)
```

创新点：把 KGR 下一跳搜索从 pointwise verification 改写为 pairwise preference learning；memory 不再只是 prompt 字段，而是影响 action preference 的条件变量。

优先级：最高，建议作为主线第一版。

### Idea B: Listwise Candidate Path / Action Ranking

一句话问题定义：当同一 query 有多条候选 relation path 或多条 rollout 时，如何让模型学习完整候选集合中的全局排序，而不是只比较两条路径。

背景：Pairwise 更适合逐跳搜索，listwise 更适合完整路径、partial trajectory 或最终 evidence chain 的全局排序。

方案：

- 为同一 query 生成 `k` 条 candidate path 或 rollout。
- 对每条 path 计算 answer F1、path coverage、validity、cost、memory utility 等 utility。
- 用 listwise objective 或 listwise reward 约束排序，例如 nDCG、MRR、ListMLE/Plackett-Luce 风格分数。
- 先离线验证 listwise reranking，再接入 GRPO/GSPO 的 reward worker。

创新点：把 path-level reasoning 从“采样多条后分别打分”变成“在候选集合内学习全局偏好”。

优先级：中高，建议在 pairwise next-hop 信号成立后加入。

### Idea C: Memory Gate / GRM-lite for KGR

一句话问题定义：Memory 既可能帮助也可能误导，如何让模型或奖励函数判断什么时候使用、忽略或降权 memory。

背景：当前 pilot 已经显示 verified memory 比 no/random memory 略有提升，但也存在 memory hurt case；oracle gate 有更大提升空间，说明“何时信任 memory”比“是否加入 memory”更关键。

方案：

- 构造四组对照：no memory、random/shuffled memory、verified memory、verified memory + gate。
- 记忆只允许来自训练集轨迹或 verifier-confirmed pattern，测试集只读不写，避免 answer cache leakage。
- 对每个 memory item 做当前子图验证：只有能落到当前候选 action 的 memory 才能参与排序。
- Gate 输出 `use_memory / ignore_memory / downweight_memory`，或直接输出 memory-conditioned action reward。

创新点：把 memory 变成可控决策变量，并用 verifier 约束 memory utility，而不是把 memory 当作额外上下文。

优先级：最高，应与 Idea A 绑定。

### Idea D: OPD Warm Start + Ranking Preference

一句话问题定义：SFT 只学习 oracle 轨迹，测试时模型走到自己产生的非 oracle state 后容易崩；如何在 student-visited states 上继续学习正确 action preference。

背景：EoG/BoG 都有 SFT 冷启动再 RL 的范式。OPD 可以用来缓解 exposure bias，但它不是核心 novelty，更适合作为稳定训练的辅助模块。

方案：

- 先用 oracle/silver trajectories 做 SFT。
- 让 student 在局部 KG 上 rollout，收集 student-visited states。
- 用 teacher 或 verifier 在这些 states 上标注/rank candidate actions。
- 用这些 on-policy preference pairs 继续做 DPO、pairwise SFT 或作为 GRPO 前的 warm start。

创新点：不是单纯蒸馏 teacher 的完整 CoT，而是在模型真实访问到的图状态上蒸馏 next-hop ranking。

优先级：中高，建议作为稳定性增强，而不是第一批必须完成的主实验。

### Idea E: Verifier-Gated Generative Reward Model

一句话问题定义：当 hard verifier 只能判断答案或路径是否合法，却无法解释 memory 是否真正有用时，能否训练/调用 GRM 给出结构化过程判断。

背景：KGR 中很多 reward 可以 hard verify，例如 action 是否存在、path 是否连通、答案是否命中；因此第一版不应急着训练复杂 GRM。但后续如果要解释 memory utility 或复杂 reasoning quality，GRM 有价值。

方案：

- 第一版只用 hard verifier 和 pairwise/listwise reward，不单独训练 RM/GRM。
- 第二版训练 lightweight ranker/RM，输入 `(q, s_t, A_t, M_t, trajectory)`，输出 action/path utility。
- 第三版训练或调用 GRM 输出结构化 JSON，例如 `path_validity`、`step_utility`、`memory_utility`、`stop_quality`、`diagnosis`。
- GRM reward 必须经过 hard-verifier gating：如果 action 不合法或 path 不连通，GRM 分数不能覆盖硬错误。

创新点：把 GRM 的任务收窄为“解释和补充 hard verifier 无法覆盖的 memory/process utility”，而不是泛化地给推理文本打分。

优先级：中，建议在 pairwise/listwise hard-verifiable reward 有效后再做。

### Idea F: Agentic RAG Extension with Evidence-Chain Memory

一句话问题定义：如果跳出纯 KG 环境，如何把同一套 memory-conditioned ranking reward 用到多步 RAG 的检索、证据选择和停止决策中。

背景：Agentic RAG 与 Agentic KGR 的共同点是都需要多步搜索、候选证据排序、过程验证和预算控制。区别在于 KGR 的 action 是 relation/entity/path，RAG 的 action 是 retrieve/rewrite/select/stop。

方案：

- 把 KGR 中的 `candidate relation/action` 替换成 RAG 中的 `candidate query/evidence/action`。
- Memory 存 evidence-chain pattern、query rewrite pattern、failed retrieval、stop mistake，而不是存答案。
- Reward 使用 supporting fact F1、citation support、retrieval recall、answer F1 和 cost。
- 作为第二实验场景，证明方法不是 KG-specific trick。

创新点：提出统一的 verifiable memory-conditioned ranking 框架，在 KGR 和 RAG 两个环境中实例化。

优先级：中，适合论文扩展或第二阶段工作。

## 推荐主线

当前最稳的主线是：

```text
Idea A: pairwise next-hop reward
+ Idea C: memory gate / memory utility
+ Idea D: OPD warm start as optional stabilizer
-> later add Idea B listwise path ranking
-> finally consider Idea E GRM
```

一句话论文方向可以写成：

> Ranking-based Memory-Conditioned GRPO for Agentic Knowledge Graph Reasoning.

中文表达：

> 面向 Agentic 知识图谱推理的记忆条件排序奖励学习。

## 如何验证这个 Idea 是否有用

### 验证目标

第一轮实验不要直接追求超过 EoG/BoG 的完整指标，而是先证明三个最小命题：

1. Ranking signal 存在：在同一 query-state 下，gold/useful action 能否稳定排在 hard negatives 前面。
2. Memory utility 存在：verified memory 是否能改变 action 排序，并且这种改变不是 random prompt noise。
3. Ranking-aware reward 有端到端收益：在相同候选子图和相同预算下，pairwise/listwise reward 是否比 pointwise reward 带来更好的 path validity、next-hop accuracy 或 answer F1。

只有这三个命题成立，后续再上 7B/8B、CWQ/WebQSP 全量、GRPO/GSPO/DAPO 对比才有意义。

### 验证闭环 1：候选动作与偏好数据

数据先用 WebQSP 小规模子集，随后扩展到 CWQ。输入仍然遵循 RoG/EoG/BoG 的 query-centered 局部图设定：

```text
question
-> topic entity
-> local subgraph / candidate relations / candidate entities
-> action candidates
```

每条样本构造成：

```json
{
  "qid": "...",
  "question": "...",
  "state": {
    "current_entities": ["..."],
    "path_so_far": ["..."],
    "hop": 0
  },
  "candidate_actions": ["relation_a", "relation_b", "..."],
  "memory": ["verified relation/path pattern ..."],
  "positive_actions": ["gold_or_answer_reaching_relation"],
  "hard_negative_actions": ["same_domain_wrong", "memory_top_wrong", "rule_top_wrong"]
}
```

第一轮只做 first-hop relation action selection 就够，因为它能最快验证 ranking 和 memory 的信号。通过后再扩展到 2-hop/4-hop rollout。

通过标准：

- gold next relation candidate recall 足够高，至少接近或超过 `85%`。
- 每个正例平均能构造出足够 hard negatives，最好 `>= 3`。
- random memory 不应稳定优于 no memory；verified memory 应该在一部分样本上改变正确排序。

### 验证闭环 2：离线 Ranking Sanity Check

先不跑 RL，直接比较四类 selector：

| 方法 | 输入 | 目标 |
|---|---|---|
| rule/lexical ranker | question + relation text | 最低成本基线 |
| pointwise classifier | `(q, s_t, a)` | 判断单个 action 是否正确 |
| pairwise ranker | `(q, s_t, a_good, a_bad)` | 学习 good action 胜过 hard negative |
| listwise ranker | `(q, s_t, A_t)` | 学习候选集合整体排序 |

指标：

```text
next_action_accuracy
pairwise_preference_accuracy
MRR
nDCG@k
Recall@1/3/5
gold_path_edge_recall
invalid_action_rate
```

通过标准：

- Pairwise 或 listwise 在 MRR / Recall@3 上比 pointwise 至少提升 `3-5` 个点。
- hard-negative subset 上提升更明显。
- 加 verified memory 的 pairwise/listwise 模型优于 no-memory 和 random-memory。

如果这一步都不成立，说明 ranking formulation 或 memory schema 还不够好，不应急着进入 GRPO。

### 验证闭环 3：Memory Gate 是否真的必要

对同一批 query 固定候选集合，做以下 memory ablation：

| Setting | 目的 |
|---|---|
| no memory | 基础策略 |
| random/shuffled memory | 排除 prompt 变长或随机上下文收益 |
| unverified memory | 测试不验证 memory 的风险 |
| verified memory | 测试可验证 memory prior |
| verified memory + gate | 测试是否能避免 harmful memory |
| oracle gate | 估计 gate 的理论上限 |

关键指标：

```text
memory_helped
memory_hurt
memory_utility_delta
gate_accuracy
final_next_action_accuracy
answer_F1_if_rollout
```

通过标准：

- oracle gate 相比 always verified memory 有可见提升，说明 gate 问题有价值。
- learned/heuristic gate 至少超过 always verified memory `1-2` 个点。
- random/shuffled memory 不应接近 verified memory，否则 memory 贡献可能只是 prompt noise。

当前 pilot 已经有一个初步信号：always verified memory 略好于 no/random memory，oracle gate 明显更高，但 learned gate 还没有解决。这说明 memory 方向可以继续，但论文贡献应写成 memory-conditioned ranking / gate，而不是简单 memory augmentation。

### 验证闭环 4：Pairwise/Listwise Reward Simulation

在上 RL 前，先离线模拟 reward 是否合理。对同一 query 的多条候选 trajectory 计算 hard-verifiable utility：

```text
u_i = answer_f1
    + path_coverage
    + graph_validity
    + memory_utility
    - dead_end_penalty
    - repeated_action_penalty
    - cost_penalty
```

Pairwise reward：

```text
r_i = mean_j sigmoid((u_i - u_j) / tau)
```

或使用离散胜率：

```text
r_i = mean_j I[u_i > u_j]
```

Listwise reward：

```text
r_i = rank_normalized_score(u_i, {u_1, ..., u_k})
```

检查：

- pairwise/listwise reward 与最终 answer F1 是否正相关。
- pairwise reward 是否能把 hard negative trajectory 压低。
- memory utility 项是否只奖励“当前子图可验证且推动答案”的 memory。
- reward 分布是否过稀疏、过密集或方差过大。

通过标准：

- Pairwise/listwise reward 对正确轨迹的排序优于 pointwise reward。
- Reward 不会大量奖励非法 action、断裂 path 或 answer-unreachable path。
- Reward 与最终任务指标有正相关，而不只是优化格式。

### 验证闭环 5：最小 GRPO / RLVR 实验

第一版不需要专门训练 RM/GRM，直接改造 verl 的 reward worker 即可。每个 query 采样多条 rollout，同一个 `uid` 组成一个 group：

```text
rollout_1, rollout_2, ..., rollout_n
```

先计算每条 rollout 的 utility，再转成 group 内 pairwise/listwise reward，写回 reward tensor。结果奖励仍保留显式 answer-level reward：

```text
R_total = R_answer_f1
        + lambda_step * R_pairwise_next_action
        + lambda_path * R_listwise_path
        + lambda_graph * R_graph_validity
        + lambda_memory * R_memory_utility
        - lambda_cost * R_steps
```

第一版可以简化为：

```text
R_total = R_answer_f1
        + lambda_step * R_pairwise_next_action
        + lambda_graph * R_action_validity
        + lambda_memory * R_memory_delta
        - lambda_cost * R_steps
```

核心对照：

| ID | 方法 | 目的 |
|---|---|---|
| B0 | rule/RoG-style candidate ranker | 检索和候选下界 |
| B1 | SFT, no memory | 小模型 action selector 基线 |
| B2 | SFT, verified memory | 检查 memory prompt 收益 |
| B3 | pointwise GRPO, no memory | 对齐 EoG/BoG-style reward |
| B4 | pointwise GRPO, verified memory | 检查 memory + pointwise 是否足够 |
| B5 | pairwise GRPO, no memory | 检查 ranking reward 独立贡献 |
| B6 | pairwise GRPO, verified memory + gate | 主方法 |
| B7 | listwise GRPO, verified memory + gate | 后续增强 |
| B8 | OPD warm start + pairwise GRPO | 稳定性增强 |

通过标准：

- B5 优于 B3：说明 pairwise reward 本身有贡献。
- B6 优于 B5 和 B4：说明 memory-conditioned ranking 有贡献。
- B7 如果进一步提升，说明 listwise path-level ranking 有价值。
- B8 如果提升训练稳定性和降低 invalid action，说明 OPD 值得作为训练模块保留。

## 具体执行计划

### 第一步：只做 WebQSP 小规模离线验证

目标：证明 ranking signal 和 memory utility 是否存在。

任务：

- 固定 topic entity 和局部子图构造，不改检索器。
- 生成 500 条训练 query、100 条评估 query 的 candidate action 数据。
- 构造 pointwise、pairwise、listwise 三种训练/评估格式。
- 输出每个 query 的 hard negative 统计、candidate recall 和 memory hit 统计。

预期产物：

```text
outputs/ranking_data/webqsp_train500_actions.jsonl
outputs/ranking_data/webqsp_eval100_actions.jsonl
outputs/ranking_data/webqsp_train500_pairwise.jsonl
outputs/ranking_data/webqsp_train500_listwise.jsonl
outputs/reports/ranking_signal_sanity_webqsp.json
```

### 第二步：训练 0.6B action selector / ranker

目标：低成本验证模型是否能学到排序信号。

模型：

```text
Qwen3-0.6B first
Qwen2.5-7B later
Llama3-8B later
```

对照：

```text
pointwise CE
pairwise preference
listwise softmax/ListMLE
no memory
random memory
verified memory
verified memory + gate
```

预期结果：

- 0.6B 不需要回答完整问题，只需要输出合法 action。
- 如果 0.6B 上 pairwise/listwise 已经优于 pointwise，说明方向值得上 7B/8B。
- 如果 0.6B 学不到，但 rule/memory ranker 有明显信号，需要检查 prompt/action format，而不是马上否定 idea。

### 第三步：多跳 rollout 评估

目标：确认 next-hop 排序提升能否传导到 answer F1。

设置：

- WebQSP 最多 2-hop 到 4-hop。
- CWQ 后续验证 compositional 多跳。
- 固定候选图和最大步数，比较不同 policy。

指标：

```text
answer F1 / Hits@1 / EM
path validity
answer visible after rollout
dead_end_rate
invalid_action_rate
steps_to_answer
memory_helped / memory_hurt
```

通过标准：

- Pairwise/listwise 至少降低 dead-end 和 invalid action。
- 在 candidate recall 足够的 query 上，answer F1 有可见提升。
- 如果 next-hop accuracy 提升但 answer F1 不动，要检查 stop decision、multi-hop compounding error 和 answer extraction。

### 第四步：接入 GRPO Reward Worker

目标：验证 ranking reward 在 online policy 优化中是否优于 pointwise reward。

第一版实现：

- 不训练独立 RM/GRM。
- 用 hard verifier 计算 action legality、path connectivity、answer F1、memory utility。
- 在同一 query 的 rollout group 内计算 pairwise win-rate reward。
- 结果 reward 仍使用 F1/EM，pairwise/listwise 作为 process reward。

这一步才算真正验证 “RLVR + ranking reward + memory-conditioned policy”。

### 第五步：决定是否加入 GRM

只有在以下条件满足时才加入 GRM：

- hard verifier reward 有信号，但无法解释 memory utility。
- pairwise/listwise reward 有提升，但 case study 显示 reward 仍误判语义相关但推理无效的路径。
- 需要更细粒度的 step diagnosis 或 stop-quality 判断。

GRM 第一版不应替代 hard verifier，而应作为 gated soft reward：

```text
if hard_validity == false:
    R_GRM = 0
else:
    R_GRM = structured_process_score
```

## 成功与失败判据

### 可以继续投入的信号

- Candidate recall 足够高，说明检索/子图不是主要瓶颈。
- Pairwise/listwise 在 offline ranking 上显著优于 pointwise。
- Verified memory 优于 random/shuffled memory，且 oracle gate 有明显上限。
- Pairwise GRPO 优于 pointwise GRPO。
- Pairwise GRPO + memory gate 优于 pairwise GRPO without memory。
- 提升不仅出现在 next-hop accuracy，也能传导到 path validity、dead-end rate 或 answer F1。

### 需要调整方向的信号

- Candidate recall 很低，说明需要先改子图构造，否则任何 policy 都被上界卡住。
- Verified memory 和 random memory 差不多，说明 memory schema 不够可验证或只是 prompt noise。
- Pairwise/listwise 只提升 ranking metric，不提升 rollout 或 answer metric，说明局部排序没有传导到全局推理。
- Gate 学不到，且 oracle gap 也不大，说明 memory 在 WebQSP/CWQ 这种短跳任务上的贡献可能不足。
- 7B/8B 上 memory 贡献消失，说明小模型上看到的收益可能只是能力不足时的补丁。

## 当前最应该做的实验

现在最应该做的不是直接追 EoG 指标，而是跑一个最小但干净的验证链：

```text
WebQSP candidate action data
-> pointwise vs pairwise vs listwise offline ranking
-> no/random/verified memory ablation
-> 0.6B action selector
-> pairwise reward simulation
-> minimal GRPO reward worker
```

如果这条链路跑通并满足通过标准，再扩展到：

```text
CWQ
multi-hop rollout
Qwen2.5-7B / Llama3-8B
OPD warm start
listwise path ranking
GRM
```

## 写论文时的主张边界

可以主张：

- Agentic KGR 的图上探索可以被重新建模为 query-conditioned ranking problem。
- Pairwise/listwise reward 比 pointwise reward 更适合学习候选 action/path 的相对优劣。
- Verified memory 的价值不是提供更多上下文，而是作为可验证的 ranking prior 改变下一跳选择。
- Memory gate / memory utility 是必要问题，因为 memory 同时存在 help 和 hurt。

暂时不要主张：

- “第一个 KGR + RLVR 方法”：EoG/BoG 已经非常接近。
- “第一个 KGR + memory 方法”：相关 memory/RAG/KGR 工作很多，BoG 也有 query 内 notebook。
- “GRM 是当前核心贡献”：第一版还没有训练真正 GRM。
- “超过 EoG 是第一目标”：第一目标应是证明 ranking reward 和 memory utility 的独立贡献；完整 SOTA 对比放在后续。
