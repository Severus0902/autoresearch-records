---
title: "Idea1 Stage8 Ranking Signal Minimal Loop"
type: result
status: completed
created: "2026-09-02"
tags: ["idea1", "agentic-kgr", "memory", "ranking", "pairwise", "listwise", "reward", "stage8"]
---

# Idea1 Stage8：记忆条件排序奖励的最小闭环验证

## 目标

本阶段不是继续旧的 Stage1-7 流程，而是验证“面向 Agentic 知识图谱推理的记忆条件排序奖励学习”这个新 idea 的最小闭环：

> WebQSP query-conditioned candidate actions -> pairwise/listwise preference data -> lightweight ranker/reward proxy -> memory ablation -> 判断是否值得进入 0.6B SFT/DPO 或 verl GRPO/RLVR。

这一步优先回答一个很具体的问题：在相同的 RoG/EoG-style 候选子图或候选 action 空间中，显式建模候选 action 的相对排序关系，是否能比 pointwise/rule-only 信号更好地区分 gold relation 和 hard negative relation。

## 实验环境与路径

- 远端目录：`/data/wxr/AutoResearch/idea1-memory-kgr`
- 代码：`experiments/idea1_memory_kgr/scripts/stage8_eval_ranking_signal.py`
- 启动脚本：`experiments/idea1_memory_kgr/scripts/submit_nohup.sh`
- 远端日志：`/data/wxr/AutoResearch/idea1-memory-kgr/logs/stage8_20260902_182013.log`
- 远端结果：`/data/wxr/AutoResearch/idea1-memory-kgr/runs/ranking_signal_20260902_182020`
- Python 环境：`/home/weixirun/anaconda3/envs/Finance/bin/python`

当前服务器环境里 `transformers`、`peft`、`torch`、`sklearn` 可用，但 `LLaMAFactory`、`trl`、`verl` 暂未安装。因此 Stage8 先用 sklearn 级别的轻量 ranker 做离线信号验证，避免在信号不明确时直接进入重训练。

## 实现内容

Stage8 复用了前面已经构造好的 WebQSP 数据：

- `cache/webqsp_train500_subgraphs.jsonl`
- `cache/webqsp_eval100_subgraphs.jsonl`
- `outputs/memory/webqsp_train500_memory.jsonl`
- `outputs/preferences/webqsp_train500_pairwise_preferences.jsonl`
- `outputs/preferences/webqsp_eval100_pairwise_preferences.jsonl`

对比方法包括：

- `rule`：relation lexical overlap 的规则排序。
- `memory`：在 rule score 上加入 verified-memory relation boost。
- `pointwise_lr`：把 action 是否为 gold relation 当作二分类问题训练轻量 pointwise classifier。
- `pairwise_lr`：把 `positive_action > hard_negative_action` 当作排序偏好训练轻量 pairwise ranker。
- `listwise_rrf`：对 rule、memory、pointwise、pairwise 的候选排名做 reciprocal-rank fusion。

## 主要结果

| 方法 | Top-1 | MRR | Recall@3 | Recall@5 | Preference Acc. | Selected Utility |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rule` | 0.10 | 0.1930 | 0.20 | 0.30 | 0.4941 | 0.124 |
| `memory` | 0.49 | 0.6055 | 0.71 | 0.73 | 0.8211 | 0.557 |
| `pointwise_lr` | 0.47 | 0.5979 | 0.72 | 0.75 | 0.8812 | 0.541 |
| `pairwise_lr` | 0.40 | 0.5532 | 0.70 | 0.75 | 0.9106 | 0.475 |
| `listwise_rrf` | 0.33 | 0.4850 | 0.59 | 0.73 | 0.8416 | 0.393 |

数据诊断：

- evaluated records: 100
- gold-in-candidates: 86
- candidate recall: 0.86
- verified-memory coverage: 0.97
- gold-in-memory hit rate: 0.70
- train memory items: 500
- eval memory items: 500

## 结论

1. 当前 query-conditioned candidate action 空间有基本可用的上限，100 条 WebQSP eval 样本里 gold relation 出现在候选中的比例为 0.86。
2. memory signal 不是随机噪声。verified memory 覆盖率为 0.97，gold relation 被 memory 命中的比例为 0.70。
3. `memory` 相比 `rule` 有显著提升，Top-1 从 0.10 提升到 0.49，Selected Utility 从 0.124 提升到 0.557，说明记忆先验在同一候选空间内确实能改变 action selection。
4. `pairwise_lr` 的 Top-1 不是最高，但 Preference Accuracy 达到 0.9106，是所有方法里最高的。这说明 pairwise 信号更擅长区分 hard negative，而不是直接作为最终 selector。
5. `listwise_rrf` 当前没有带来收益，说明简单 rank fusion 还不能作为 listwise 创新点，需要更强的 listwise objective 或路径级 rollout 监督。

因此，当前最顺的技术路线不是“直接把 pairwise ranker 当最终检索器”，而是：

> 用 memory 提供候选 action 的先验支持，用 pairwise/listwise ranking reward 作为过程奖励或 reward shaping，再接入 0.6B action selector、DPO/GRPO 或后续 verl reward worker。

## 最小闭环状态

已经验证：

- query-conditioned 子图或候选 action 可以产生可学习的下一跳空间。
- memory 能在候选空间中提供有效先验。
- pairwise preference 数据可以从 gold relation 与 hard negatives 中构造出来。
- pairwise ranking signal 能作为过程奖励候选，尤其适合“下一跳选择”的 stepwise reward。
- nohup 远端执行与结果落盘流程已经跑通。

尚未验证：

- 0.6B 小模型是否能通过 SFT/DPO 学到这个排序信号。
- pairwise/listwise reward 接入多跳 rollout 后是否能提升 final answer F1。
- verl GRPO/RLVR reward worker 是否能稳定训练。
- CWQ 上更复杂组合问题是否仍然需要 memory。

## 下一步方案

优先进入 Stage9：pairwise-as-process-reward 的模型级最小验证。

建议顺序：

1. 用现有 `webqsp_train500_action_dpo.jsonl` 训练 Qwen3-0.6B 的 pairwise/DPO action selector。
2. 如果暂不安装 LLaMAFactory/TRL，则先写一个 minimal DPO/LoRA 脚本，复用当前可用的 `transformers + peft + torch`。
3. 在 eval100 上比较 `no_memory`、`verified_memory`、`pointwise/SFT`、`pairwise/DPO` 四组下一跳选择。
4. 如果 pairwise/DPO 只提升 Preference Accuracy 但不提升 Top-1，则把它转为 GRPO/RLVR 的 stepwise reward，而不是直接作为 policy。
5. 再把 reward worker 接到 verl，做小步数 GRPO，最终评估 WebQSP/CWQ 的 answer-level F1。

当前判断：这个方向的“memory gap + reward gap”是成立的，但创新点需要落在 ranking reward 如何服务于 agentic multi-hop search，而不是只报告一个离线排序器指标。
