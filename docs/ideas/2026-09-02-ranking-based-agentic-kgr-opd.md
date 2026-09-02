---
title: "Ranking-based Agentic KGR: Pairwise/Listwise Reward, RLVR, and OPD"
type: idea
status: open
created: "2026-09-02"
zotero: ["@luoReasoningGraphsFaithful2024", "@yanExploreongraphIncentivizingAutonomous2026a"]
tags: ["agentic-kgr", "rog", "eog", "bog", "grpo", "rlvr", "pairwise", "listwise", "opd", "memory"]
---

# Ranking-based Agentic KGR: Pairwise/Listwise Reward, RLVR, and OPD

## 一句话问题定义

现有 RoG/EoG/BoG-style KGR 方法主要把候选路径或单条轨迹作为 pointwise 对象进行规划、检索或打分，但 agentic KGR 的核心决策其实是在同一个 query-conditioned graph state 下比较多个候选 action/path，因此需要显式建模 pairwise/listwise preference，并进一步判断 memory 或 teacher signal 何时应该参与搜索决策。

## 核心判断

当前最顺的 motivation 不是简单写“加入 memory 提升 KGR”，而是：

> Pointwise reward 判断一条路径“好不好”，但 agentic KGR 真正需要学习的是在同一个 query 和 graph state 下，一组候选路径或下一跳动作里“哪一个更好”。

因此本文可以把 KGR 从单条轨迹验证问题改写成 **query-conditioned action/path ranking problem**。这个改写能自然接上 pairwise/listwise learning-to-rank、GRPO/RLVR、memory gate 和 OPD。

## 相关方法定位

| 方法 | 发表/状态 | 核心范式 | 图检索/候选构造 | 训练/奖励特点 | 与本文 gap |
|---|---|---|---|---|---|
| RoG | ICLR 2024 | planning -> retrieval -> reasoning | LLM 生成 relation path，再在已有子图上按 relation rule BFS 得到 reasoning paths | SFT/joint fine-tuning，不是 RL | 解决 relation-path planning 和路径式检索，但没有学习在线探索策略 |
| EoG | ICLR 2026 | RoG-style graph-grounded reasoning -> RL exploration | 使用 query/KG/subgraph/reasoning path 作为环境与证据，重点不在重做 retriever | `GRPO + custom_reward_function`，`reward_model.enable=False`；代码中主要是 path match pointwise reward | 让 LLM 自主探索，但 reward 仍是单条轨迹的 pointwise verification |
| BoG | ICML 2026 main poster | forward/backjump/yield/halt 的回溯式探索 | 公开信息显示重点在 dead-end 后 backjump，不是新的初始图检索 | SFT + RL，hybrid reward；当前官方仓库尚未公开训练代码 | 改进探索控制，但没有看到显式 pairwise/listwise action ranking |

代码观察：

- RoG 官方代码：`RManLuo/reasoning-on-graphs`。本地参考目录为 `.refs/reasoning-on-graphs`。
- EoG 代码：`ysq111333/Explore-on-Graph`。本地参考目录为 `.refs/Explore-on-Graph`。
- BoG 官方仓库：`zhangSchnee/BoG`。截至 2026-09-02，本地 clone 后只看到 `Token.png`、`decoding.png`、`statistics.png`，没有训练/reward 代码。

## Pointwise Reward 的本质问题

EoG/BoG 这类方法即使用 GRPO，也大多还是：

```text
single trajectory -> verifier score
same-query trajectories -> GRPO group normalization
```

这带来几个问题：

1. **缺少相对选择信号**：模型每一步真正需要从多个 relation/entity/action 里选择，但 pointwise reward 只判断单条轨迹分数，不直接表达 `action_a > action_b`。
2. **难以利用 hard negatives**：KGR 中最有价值的负例通常是同 domain、同 relation neighborhood、语义相似但会走向 dead-end 的边；pointwise score 很难充分利用这些负例。
3. **局部合理不等于全局有效**：一条路径可能命中相关实体或部分 gold triple，但仍然偏离最终答案；pointwise reward 容易奖励局部看起来合理的行为。
4. **不同 query 的分数尺度不稳定**：不同问题的子图大小、候选分支、hop 数不同，绝对分数不易比较；GRPO 可做组内归一化，但 reward 本身仍未显式表达排序关系。
5. **memory 的作用难以建模**：memory 既可能帮助也可能误导。pointwise reward 只能说“用了 memory 的轨迹得几分”，但 pairwise 可以直接学习 `useful-memory action > no-memory action` 或 `no-memory action > misleading-memory action`。

## Pairwise/Listwise 是否必须做 RLVR

不必须。

Pairwise/listwise 是训练信号的组织方式；RLVR 是用可验证 reward 做 RL 的训练范式。二者可以组合，但不是绑定关系。

| 路线 | 是否 RLVR | 是否训练 RM/GRM | 适用阶段 | 验证指标 |
|---|---|---|---|---|
| Offline pairwise ranker | 否 | 可不训练大 RM，只训练 action selector/ranker | 最小验证 | pairwise accuracy, MRR, Recall@k, next-relation accuracy |
| DPO/IPO/SimPO on preference pairs | 否 | 不需要在线 reward worker | SFT 之后的偏好优化 | chosen/rejected win rate, final action accuracy |
| Pairwise-GRPO verifier reward | 是 | 不需要单独 RM | Stage A 推荐路线 | GRPO reward, answer F1, path validity, memory utility delta |
| Learned RM/GRM + GRPO | 是 | 需要训练 RM/GRM | 后续增强 | reward-model agreement, final QA, ablation |

第一版建议走 **Stage A：直接改 verl reward worker，不专门训练 RM/GRM**。

## Stage A: Pairwise-GRPO Verifier Reward

在同一个 query 下采样多条 rollout：

```text
t_1, t_2, ..., t_n
```

先给每条轨迹计算可验证 utility：

```text
u_i = answer_f1
    + path_coverage
    + graph_validity
    + memory_support
    - dead_end_penalty
    - redundancy_penalty
    - cost_penalty
```

再把 utility 转成 pairwise reward：

```text
r_i = mean_j sigmoid((u_i - u_j) / tau)
```

或者使用更离散的胜率：

```text
r_i = mean_j I[u_i > u_j]
```

最后把 `r_i` 写回 verl 的 `reward_tensor[i, last_token]`。后续 GRPO advantage 仍然按同一个 `uid` 聚合：

```text
A_i = (r_i - mean(r_group)) / std(r_group)
```

这样可以保持 RLVR 的性质：reward 来自 KG、gold answer、path verifier、format verifier、memory verifier，而不是外部 judge model。

## 为什么不先训练 RM/GRM

第一版不建议先训练 RM/GRM，原因是：

1. KGR 的很多 reward 本来就是 hard-verifiable：action 是否存在、路径是否连通、答案是否命中、是否 dead-end。
2. 训练 RM/GRM 会引入额外变量，容易分不清提升来自 ranking reward、memory，还是 reward model 自身的语义判断。
3. 0.6B pilot 的目标是快速验证信号，不是一次性搭完整 RLHF/RLAIF 管线。
4. 如果直接用 verl 的 group-aware reward manager，就能最小成本验证 pairwise reward 是否比 pointwise reward 更适合 KGR。

因此推荐顺序是：

```text
SFT action selector
-> offline pairwise/DPO sanity check
-> pairwise-GRPO verifier reward
-> lightweight RM/GRM
-> generative GRM with hard verifier gating
```

## OPD 如何结合

这里的 OPD 暂按 **On-Policy Distillation** 理解。如果 OPD 指的是其他具体论文或算法名，需要再单独对齐定义。

OPD 解决的是另一个问题：SFT 只让 student 学 oracle/teacher 轨迹，但测试时 student 会走到自己产生的非 oracle graph state。一旦走偏，普通 SFT 没有告诉它如何补救。

OPD 的核心是：

```text
student rollout -> student-visited states
teacher labels/logits/actions on these states
student distills teacher behavior on on-policy states
```

放到 agentic KGR 中，OPD 可以这样用：

```text
q, state_t, candidate_actions, memory_t
student proposes action distribution
teacher ranks or selects next action
student learns teacher preference on this visited state
```

OPD 与本文主线的关系：

| 模块 | 解决的问题 | 是否主创新 |
|---|---|---|
| Pairwise/listwise reward | 多个候选 action/path 如何相对比较 | 是 |
| Memory gate | 何时信任、忽略或降权 memory | 是 |
| OPD | student 走到非 oracle 状态后如何继续学习 | 辅助稳定 |
| GRM/RM | hard verifier 不够时如何判断语义过程质量 | 后续增强 |

推荐叙事：

> SFT provides oracle-path imitation, OPD reduces exposure bias on student-visited graph states, and pairwise-GRPO optimizes relative action/path preferences under verifiable KG feedback.

中文表述：

> SFT 负责冷启动，OPD 负责让模型在自己访问到的图状态上学习补救和继续探索，而 pairwise/listwise GRPO 负责把候选 action/path 之间的相对优劣变成可优化的 RLVR reward。

## 推荐训练路线

### Route 1: 最小可验证路线

```text
Stage 1: RoG-style candidate generation
Stage 2: 构造 gold action 与 hard negative action
Stage 3: 训练 0.6B action selector
Stage 4: offline pairwise ranker / DPO 验证
Stage 5: pairwise-GRPO verifier reward
```

优点：工程风险最低，最容易判断 pairwise reward 是否有用。

### Route 2: 加 OPD 的稳定路线

```text
Stage 1: SFT on oracle/silver trajectories
Stage 2: student on-policy rollout
Stage 3: teacher labels/ranks student-visited states
Stage 4: OPD auxiliary training
Stage 5: pairwise-GRPO verifier reward
```

优点：更能解释为什么模型走偏后仍能恢复；缺点是需要 teacher 参与，成本更高。

### Route 3: 加 GRM 的完整路线

```text
Stage 1: hard verifier reward
Stage 2: pairwise/listwise preference data
Stage 3: train lightweight RM/ranker
Stage 4: train or prompt GRM for structured process judgment
Stage 5: verifier-gated GRM + GRPO
```

优点：论文故事完整；缺点是变量多，不适合第一版验证。

## 实验设计

第一阶段只需要证明三个问题：

1. **Ranking signal 是否存在**：gold action 相比 hard negative 是否能被规则/小模型/ranker 区分。
2. **Pairwise reward 是否优于 pointwise reward**：在同样 rollout 数和预算下，pairwise-GRPO 是否提升 next-hop accuracy、path validity、answer F1。
3. **Memory 是否真的改变 preference**：verified memory 是否让模型更倾向正确 action，同时 memory gate 是否能避免 harmful memory。

核心对照：

| 对照 | 目的 |
|---|---|
| pointwise verifier reward | 对齐 EoG/BoG-style reward |
| pairwise verifier reward | 验证 ranking reward 是否更适合候选选择 |
| listwise verifier reward | 验证全候选排序是否进一步提升 |
| no memory | 测试 memory 绝对贡献 |
| random memory | 排除 prompt noise/额外上下文收益 |
| verified memory | 测试可验证 memory prior |
| verified memory + gate | 测试何时使用 memory |
| OPD auxiliary | 测试 on-policy teacher signal 是否缓解走偏 |

指标：

```text
next_relation_accuracy
pairwise_preference_accuracy
MRR / nDCG over candidate actions
gold_path_edge_recall
path_validity
answer Hits@1 / F1
dead_end_rate
invalid_action_rate
memory_utility_delta
token/tool/step cost
```

## 论文主张边界

可以主张：

> Existing agentic KGR methods mainly optimize pointwise verifier rewards over individual trajectories. We instead formulate graph exploration as a query-conditioned ranking problem over competing actions and paths, and instantiate this view with pairwise/listwise verifier rewards, memory-conditioned preferences, and optional on-policy distillation.

中文：

> 现有 agentic KGR 方法主要对单条推理轨迹进行 pointwise verification；本文将图上探索重新建模为 query-conditioned ranking problem，在候选 action/path 之间显式学习相对偏好，并结合 verified memory 和可选的 on-policy distillation 来提升搜索策略。

暂时不要主张：

- “我们提出第一个 KGR + RLVR 方法”：EoG/BoG 已经很接近。
- “我们提出第一个 memory KGR 方法”：memory/RAG/KGR 相关工作已有很多。
- “GRM 是核心贡献”：第一版还没有训练真正 GRM。
- “memory 一定提升”：已有 pilot 显示 memory 会帮助也会误导。

## 下一步实现建议

优先实现：

1. 在现有 `experiments/idea1_memory_kgr` 中新增 `stage8_pairwise_reward_simulation.py`，先离线模拟 pointwise vs pairwise reward。
2. 统计 pairwise reward 与最终正确性的相关性，输出 reward calibration report。
3. 如果离线信号成立，再写 verl `PairwiseKGRRewardManager`，按 `uid` 分组计算组内 pairwise/listwise reward。
4. 暂不训练 RM/GRM，只使用 hard verifier 和 memory verifier。
5. OPD 放到后续 stage：先用 teacher-ranked action 生成 on-policy preference data，不急着接 teacher logits。

当前最推荐的一句话方向：

> Ranking-based Memory-Conditioned GRPO for Agentic Knowledge Graph Reasoning.

## Research Gap

RoG 主要通过 query-to-relation-path planning 约束 KG 上的路径检索，将自然语言问题转化为可在 KG 中匹配的 relation-path plans。EoG/BoG 进一步沿着 RoG-style graph-grounded reasoning 的方向，把静态路径规划推进为由 SFT/RL 优化的 agentic graph exploration。然而，这些方法的奖励或训练信号仍主要作用在单条候选路径或单条推理轨迹上，没有显式建模同一 query-conditioned graph state 下多个候选 action/path 之间的相对竞争关系。因此，现有 pointwise-style verification 难以充分利用 hard negatives、memory support，以及多候选路径之间的细粒度优劣关系。

更稳妥的边界表述是：这些方法并非完全没有多候选生成或组内比较，RoG 有 beam-style relation-path generation，EoG/BoG 使用 GRPO 时也会对同一 query 的多条 rollout 做 group-relative normalization；但它们没有把候选 action/path 之间的 pairwise/listwise preference 显式作为 reward modeling 或 policy learning 的核心对象。

## Expected Hypotheses

第一阶段实验可以围绕以下递进假设展开：

| ID | 假设 | 对照 | 预期观察 |
|---|---|---|---|
| H1 | `SFT + OPD` 优于单纯 SFT | SFT vs SFT+OPD | OPD 在 student-visited states 上提供补救监督，降低 exposure bias，提升 next-hop/path accuracy |
| H2 | 冷启动 `GRPO/GSPO` 优于无 RL 的 SFT policy | SFT vs cold-start RL | 可验证 reward 能纠正 SFT 的局部模仿偏差，但可能不稳定 |
| H3 | `SFT/OPD warm start + GRPO/GSPO` 优于冷启动 RL | cold-start RL vs warm-start RL | warm start 降低 invalid action 和 reward sparsity，提高训练稳定性 |
| H4 | stepwise pairwise reward 优于 stepwise pointwise reward | pointwise step reward vs pairwise step reward | hard negatives 被显式利用，下一跳选择更稳 |
| H5 | listwise path/action reward 在候选集合质量足够时进一步提升 | pairwise vs listwise | 完整候选排序改善 global path selection、answer F1 和 stop decision |
| H6 | memory-conditioned ranking 优于无 memory ranking | no/random/verified memory | verified memory 改变 action preference；memory gate 避免 harmful memory |

推荐的消融顺序：

```text
SFT
SFT + OPD
SFT + pointwise GRPO/GSPO
SFT + pairwise GRPO/GSPO
SFT + listwise GRPO/GSPO
SFT + OPD + pairwise/listwise GRPO/GSPO
SFT + OPD + pairwise/listwise GRPO/GSPO + verified memory gate
```

## Reward Decomposition

Pairwise/listwise 更适合放在 **过程步骤奖励** 中，结果奖励仍应保留显式的 answer-level metric，例如 F1、Hits@1、EM 或 answer entity recall。

一个清晰的分层 reward 是：

```text
R_total = R_outcome
        + lambda_step * R_step_ranking
        + lambda_path * R_path_ranking
        + lambda_graph * R_graph_validity
        + lambda_memory * R_memory_utility
        - lambda_cost * R_cost
```

其中：

| Reward | 作用层级 | 推荐形式 | 说明 |
|---|---|---|---|
| `R_outcome` | episode-level result reward | F1 / Hits@1 / EM / answer recall | 保持显式、可验证，作为最终任务目标 |
| `R_step_ranking` | stepwise process reward | pairwise next-action win rate | 比较同一 state 下哪个下一跳更接近 gold/supporting path |
| `R_path_ranking` | trajectory/path-level process reward | listwise MRR/nDCG over candidate paths | 比较一组完整路径或 partial trajectories 的全局优劣 |
| `R_graph_validity` | hard constraint | action legality, path connectivity, no invalid relation | 约束模型不能靠语言幻觉拿分 |
| `R_memory_utility` | memory-specific process reward | memory changes preference toward useful action | 衡量 memory 是否真的改善搜索，而不是只增加上下文 |
| `R_cost` | budget control | steps, tokens, tool calls, repeated expansion | 防止模型靠过度探索换分 |

因此，pairwise/listwise 不应替代 F1，而应作为 dense process reward 解决 credit assignment：

```text
Outcome reward answers: did the final answer match?
Stepwise pairwise reward answers: did this action beat plausible alternatives?
Listwise path reward answers: did the policy rank the best path above other candidates?
Memory utility reward answers: did memory improve this decision under current state?
```

第一版可以先做：

```text
R_total = R_answer_f1
        + lambda_step * R_pairwise_next_action
        + lambda_graph * R_action_validity
        + lambda_memory * R_memory_delta
        - lambda_cost * R_steps
```

等候选路径生成质量稳定后，再加入 `R_listwise_path_ranking`。
