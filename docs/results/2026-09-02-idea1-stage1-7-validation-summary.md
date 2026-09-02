---
title: "Idea1 Stage1-7 Validation Summary"
type: result
status: pilot
created: "2026-09-02"
tags: ["idea1", "agentic-kgr", "memory", "qwen3-0.6b", "stage7", "grm-lite"]
---

# Idea1 阶段实验总结与验证文档

## 一句话结论

Idea1 的最小链路已经跑通：`query-conditioned subgraph -> verified memory -> action preference -> Qwen3-0.6B action selector -> memory ablation -> memory gate`。当前最强信号不是“直接拼 memory 显著提升”，而是“memory 有帮助也有误导，因此需要一个 query-conditioned memory gate / GRM 去决定何时启用 memory”。

## Stage7 是什么阶段

Stage7 是 **Memory Gate / GRM-lite 诊断阶段**。

它不重新训练 Qwen selector，也不访问 Freebase；它读取 Stage6 三组 selector 的逐样本输出：

- `no_memory`
- `random_memory`
- `verified_memory`

然后训练/评估一个轻量 gate，学习在 `no_memory` 与 `verified_memory` 之间选择。它的目标不是形成正式论文指标，而是回答：

> 如果有一个更好的 GRM 或 memory gate，能否避免 memory 负迁移，并超过单纯 always-use-memory 的策略？

因此 Stage7 是从 “memory 作为 prompt 字段” 走向 “memory 作为可控 agent action / reward-conditioned decision” 的过渡阶段。

## 实验环境与边界

远端目录：

```text
/data/wxr/AutoResearch/idea1-memory-kgr
```

核心数据与模型：

```text
WebQSP: /data/wxr/Pilotenv/data/webqsp.json
Freebase Virtuoso: http://127.0.0.1:8890/sparql
Qwen3-0.6B: /data/wxr/Finance/Qwen3-0.6B
```

执行边界：

- 所有代码、日志、cache、outputs、runs 均在 `/data/wxr/AutoResearch/idea1-memory-kgr` 下。
- 没有执行删除命令。
- 长任务均通过 `scripts/submit_nohup.sh` 提交。

## 阶段定义

| Stage | 名称 | 要解决的问题 | 主要产物 |
|---|---|---|---|
| Stage1 | Subgraph Build | 给定 query 和 topic entity，能否构建可用的局部候选子图 | `cache/*_subgraphs.jsonl` |
| Stage2 | Memory Build | 能否从 pseudo-train 构造可检索的 verified relation memory | `outputs/memory/*.jsonl` |
| Stage3 | Rule vs Memory Selector | memory prior 是否能改善下一跳 relation top-1 | `outputs/eval/*selector_summary.json` |
| Stage4 | Pairwise Preference | 能否把 gold relation 与 hard negative 转成可训练偏好 | `outputs/preferences/*.jsonl` |
| Stage5 | Compact Action Data | 能否把偏好压缩成 0.6B 可消费的 SFT/DPO 数据 | `outputs/train_data/*.jsonl` |
| Stage6 | Qwen3-0.6B Selector | 小模型能否学会 constrained relation action selection | `runs/qwen3_0p6b_*` |
| Stage7 | Memory Gate / GRM-lite | 能否判断什么时候应该启用 memory | `runs/qwen3_0p6b_memory_gate_eval_*` |

## Stage1：局部子图与候选关系

最初失败点主要不是 policy，而是 candidate recall。原始按 edge `LIMIT 50` 检索时，候选被高频元信息关系和同一 relation 的多个 object 淹没，gold relation candidate recall 只有 `0.15`。

改进后策略：

- relation-level sampled query，而不是 object-level edge query。
- 过滤 `common.topic.*`、`type.object.*`、`kg.object_profile.*`、`freebase.*` 等低价值关系。
- 保留 query-conditioned local subgraph，而不是把整张 KG 塞进模型。

WebQSP eval100 结果：

```text
num_records: 100
gold_next_relation_edge_recall: 0.94
gold_next_relation_candidate_recall: 0.86
gold_answer_visible_rate: 0.62
avg_edges: 67.77
avg_candidate_actions: 51.47
```

WebQSP train500 结果：

```text
num_records: 500
gold_next_relation_edge_recall: 0.99
gold_next_relation_candidate_recall: 0.938
gold_answer_visible_rate: 0.642
avg_candidate_actions: 48.86
```

验证效果：Stage1 证明“先根据 query 找 topic entity，再构造候选 relation/action”是可行的；但 1-hop 子图的 answer visible 只有约 `0.62-0.64`，后续需要扩展到多跳 rollout。

## Stage2：Verified Memory 构造

Stage2 从 WebQSP pseudo-train 中构造 relation-chain memory。当前 memory 不是最终方法，而是一个 controlled proxy：

- memory item 来源于 gold/silver relation chain。
- 每条 memory 带有 question pattern、seed entity、relation template、successful action 和 verifier utility。
- 检索时只把能落到当前 candidate action 的 relation 作为 verified memory relation。

产物：

```text
outputs/memory/webqsp_eval100_train_memory.jsonl
outputs/memory/webqsp_train500_memory.jsonl
```

验证效果：Stage2 让后续实验能区分“直接用历史经验”和“历史经验是否能被当前子图验证”。这对应 Idea1 的核心边界：memory 不是自由文本经验，而是 graph-grounded、verifier-aware 的可用 prior。

## Stage3：Rule Selector vs Memory Selector

Stage3 先不训练模型，只比较两个简单 selector：

- `rule`: question 与 relation lexical overlap。
- `memory`: 在 rule 基础上给 verified memory relation 加 prior。

Smoke20：

```text
rule_next_relation_accuracy: 0.20
memory_next_relation_accuracy: 0.40
memory_utility_delta: +0.20
```

Eval100：

```text
rule_next_relation_accuracy: 0.12
memory_next_relation_accuracy: 0.45
memory_utility_delta: +0.33
memory_only_correct: 34
rule_only_correct: 1
```

验证效果：在非模型 selector 上，verified memory 的信号很强，说明跨 query 的 relation pattern memory 可以作为 KGR 下一跳搜索的 prior。

但这一步还不能说明 learned model 一定会利用 memory；它只是证明 memory signal 有信息量。

## Stage4：Pairwise Action Preference

Stage4 把每个可见 gold next relation 的样本转成 pairwise preference：

```text
positive_action = gold next relation
negative_action = same-domain hard negative / rule_top_wrong / memory_top_wrong / ranked_negative
```

Eval100 preference：

```text
num_preferences: 341
skipped.gold_not_in_candidates: 14
same_domain_hard_negative: 185
rule_top_wrong: 74
memory_top_wrong: 36
ranked_negative: 46
```

Train500 preference：

```text
num_preferences: 1857
skipped.gold_not_in_candidates: 31
skipped.no_negative: 1
same_domain_hard_negative: 1048
rule_top_wrong: 365
ranked_negative: 320
memory_top_wrong: 124
```

验证效果：Stage4 把“memory 能提升 top-1”转成了可训练监督信号，后续可以支持 SFT、DPO/pairwise ranker 或 RLVR warm start。

## Stage5：Compact Action Data

Stage5 把 preference 转为小模型可消费的格式：

- SFT：每个 qid 一个 `messages` 样本，assistant 只输出 `{"relation_id": "..."}`。
- DPO：每个 preference 一个 `prompt/chosen/rejected` 样本。

Train500 产物：

```text
outputs/train_data/webqsp_train500_action_sft.jsonl
outputs/train_data/webqsp_train500_action_dpo.jsonl
```

统计：

```text
num_preferences_in: 1857
num_dpo_rows: 1857
num_sft_rows: 468
max_candidates_per_prompt: 80
```

验证效果：Stage5 证明可以把 KGR 下一跳搜索压缩成小模型 action selection 任务，而不是让模型直接生成答案或整条路径。

## Stage6：Qwen3-0.6B Action Selector

Stage6 使用服务器已有模型：

```text
model: /data/wxr/Finance/Qwen3-0.6B
LoRA trainable params: 5,046,272 / 601,096,192 = 0.8395%
train samples: 256
max steps: 30
eval samples: 60
```

最小 verified-memory SFT：

```text
eval_before_accuracy: 0.0000
eval_before_invalid_rate: 1.0000
eval_after_accuracy: 0.7000
eval_after_invalid_rate: 0.0000
```

同版脚本重跑三组 memory ablation：

| setting | train_memory_mode | eval_memory_mode | eval_after_accuracy | eval_after_invalid_rate |
|---|---|---|---:|---:|
| no_memory | none | none | 0.7167 | 0.0167 |
| random_memory | random | random | 0.7167 | 0.0167 |
| verified_memory | verified | verified | 0.7333 | 0.0000 |

正确集合重叠：

```text
all_correct: 36
verified_only_vs_no: 6
no_only_vs_verified: 5
verified_only_vs_random: 8
random_only_vs_verified: 7
all_wrong: 8
```

验证效果：

1. 小模型路线成立：Qwen3-0.6B 用 256 条样本和 30 step 就能学会合法 relation action 输出。
2. 直接拼 verified memory 的模型级收益很小：相对 no/random 只多对 `1/60`。
3. memory 会帮忙，也会误导。关键问题不是“有没有 memory”，而是“什么时候应该相信 memory”。

## Stage7：Memory Gate / GRM-lite

Stage7 已在 2026-09-02 启动并完成：

```text
log: /data/wxr/AutoResearch/idea1-memory-kgr/logs/stage7_20260902_110048.log
run_dir: /data/wxr/AutoResearch/idea1-memory-kgr/runs/qwen3_0p6b_memory_gate_eval_20260902_110048
```

输入：

```text
no_memory: runs/qwen3_0p6b_no_memory_sft_minimal_20260901_211950
random_memory: runs/qwen3_0p6b_random_memory_sft_minimal_20260901_212358
verified_memory: runs/qwen3_0p6b_memory_sft_minimal_20260901_212727
```

样本标签分布：

```text
num_cases: 60
memory_helped: 6
memory_hurt: 5
both_correct: 38
both_wrong: 11
```

策略结果：

| strategy | accuracy | invalid_rate | 说明 |
|---|---:|---:|---|
| always_no_memory | 0.7167 | 0.0167 | 永远不用 memory |
| always_random_memory | 0.7167 | 0.0167 | 随机 memory 对照 |
| always_verified_memory | 0.7333 | 0.0000 | 永远用 verified memory |
| verified_if_memory_nonempty | 0.7500 | 0.0000 | memory 非空才用 verified |
| verified_if_prediction_in_memory | 0.7500 | 0.0000 | verified 预测落在 memory 中才用 |
| verified_if_single_memory | 0.7500 | 0.0167 | 只有一个 memory relation 时才用 |
| fixed_grm_lite_gate | 0.7333 | 0.0000 | 手写线性 gate |
| loocv_grm_lite_gate | 0.6833 | 0.0000 | leave-one-out 小样本训练 gate |
| oracle_no_vs_verified | 0.8167 | 0.0000 | 在 no/verified 中完美切换 |
| oracle_all_three | 0.8667 | 0.0000 | 在 no/random/verified 中完美切换 |

验证效果：

- Oracle 从 `0.7333` 提升到 `0.8167`，说明如果能判断 memory 何时会误导，理论收益有 `+8.33` 个点。
- 简单 rule gate 已经能到 `0.7500`，略好于 always verified。
- 当前 `loocv_grm_lite_gate` 只有 `0.6833`，说明用少量手写特征和 60 条 eval 样本训练 gate 不可靠。
- Stage7 支持下一步做真正的 GRM/memory gate，但也提醒不能把这部分直接写成已解决。

## Idea 是否被验证

已经被验证的部分：

1. Query-conditioned subgraph 是必要且可行的；不能把整张 KG 塞给模型。
2. Verified memory 在非模型 selector 上有明显信息量。
3. KGR 下一跳可以被压缩成小模型 action selection。
4. Qwen3-0.6B 可以快速完成最小验证，不必一开始就上 7B/8B。
5. Memory 的收益不是稳定单调的，确实需要 gate/GRM。

尚未被验证的部分：

1. 在 official train/dev/test split 上是否仍成立。
2. 多跳 CWQ/WebQSP 完整 answering 是否提升。
3. learned GRM 是否能真正超过 heuristic gate。
4. RLVR/GRPO 是否比 SFT/DPO 带来额外收益。
5. memory 是否在 7B/8B 上仍有独立贡献，而不是被大模型内化。

## 当前 Motivation 应该如何收敛

不建议写成：

> Memory improves KG reasoning.

更准确的 motivation 是：

> Existing agentic KGR methods usually treat retrieved graph evidence or historical reasoning patterns as static context. However, memory can both help and mislead next-hop graph traversal. We study verifier-grounded memory as a controllable decision variable: when should an agent use, ignore, or down-weight memory during query-conditioned KG reasoning?

中文表述：

> 现有 agentic KGR 方法通常把图证据或历史推理模式当作静态上下文，但 memory 在下一跳搜索中既可能提供有用 prior，也可能引入负迁移。因此本方向把 verified memory 从“被动拼接的 prompt 字段”转成“由 agent/GRM 动态决定是否采用的推理动作”，研究在 query-conditioned 子图中何时使用、忽略或降权 memory。

## 下一步建议

下一步不要急着上完整 RLVR。更稳的路线是：

1. 把 eval 从 `60` 扩到完整 eval100，并固定随机种子重跑 Stage6/Stage7。
2. 生成 train/dev gate 数据：用 train500 内部切分训练 gate，用 eval100 评估 gate，避免在 eval60 上做 LOOCV。
3. 把 gate 从手写特征升级为小型 GRM/reranker：输入 question、candidate relation、memory relations、selector output，输出 `use_memory` 或 relation-level reward。
4. 加入 relation-level listwise rerank：不是只在 no/verified 两个 selector 之间切，而是对候选 relation 直接打分。
5. 扩展到 2-hop/4-hop rollout，评估 answer F1/Hits，而不是只看 first-hop relation accuracy。
