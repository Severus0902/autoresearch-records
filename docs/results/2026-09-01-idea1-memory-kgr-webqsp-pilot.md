---
title: "Idea1 WebQSP Pilot: Verified Memory for KGR Action Selection"
type: result
status: pilot
created: "2026-09-01"
tags: ["idea1", "agentic-kgr", "memory", "webqsp", "pilot", "rlvr"]
---

# Idea1 WebQSP Pilot：Verified Memory 是否改善 KGR 下一跳选择

## 实验目的

本次实验不是复现完整 EoG，也不是训练 0.6B/7B 模型，而是验证一个最小问题：

> 在 query-conditioned local subgraph 中，verified memory 能否帮助 action selector 在候选关系里选出更好的下一跳 relation？

这对应 Idea1 的最小可验证信号：如果 memory 在不泄漏测试答案的前提下能显著改善下一跳选择，那么后续再接 0.6B SFT selector、pairwise/listwise ranking、GRM reranker 和 RLVR 才有意义。

## 远端环境

服务器目录：

```text
/data/wxr/AutoResearch/idea1-memory-kgr
```

数据与服务：

```text
WebQSP: /data/wxr/Pilotenv/data/webqsp.json
Virtuoso Freebase endpoint: http://127.0.0.1:8890/sparql
Virtuoso pid: 2144488
```

执行边界：

- 所有实验输出写在 `/data/wxr/AutoResearch/idea1-memory-kgr` 内。
- 未执行删除命令。
- stage 任务均通过 `nohup` 提交。

## 代码版本

相关 GitHub commits：

```text
5a6446b Add Idea1 memory KGR experiment framework
d302c26 Fix Idea1 remote output path and shell eol
fb84ef2 Add leakage-safe WebQSP smoke config
d03b75d Support nested WebQSP parse layout
2ab1fe4 Add subgraph recall analyzer
1f4a973 Improve WebQSP smoke relation candidate recall
7a6a85a Add WebQSP eval100 pilot config
5be8111 Add selector eval analyzer
```

## 实验设置

### Smoke 20

配置：

```text
configs/webqsp_smoke.json
memory split: first 200 examples, pseudo-train
eval split: offset 200, next 20 examples, pseudo-eval
max_hops: 1
edge_limit_per_entity: 300
max_relation_candidates: 100
```

输出：

```text
cache/webqsp_smoke_subgraphs.jsonl
outputs/memory/webqsp_smoke_train_memory.jsonl
outputs/eval/webqsp_smoke_selector_eval.jsonl
outputs/eval/webqsp_smoke_selector_summary.json
```

结果：

```text
num_examples: 20
gold_next_relation_candidate_recall: 0.90
gold_answer_visible_rate: 0.50
rule_next_relation_accuracy: 0.20
memory_next_relation_accuracy: 0.40
memory_utility_delta: +0.20
avg_candidate_actions: 49.15
avg_memory_hits: 3.05
```

### Eval 100

配置：

```text
configs/webqsp_eval100.json
memory split: first 500 examples, pseudo-train
eval split: offset 500, next 100 examples, pseudo-eval
max_hops: 1
edge_limit_per_entity: 300
max_relation_candidates: 100
```

输出：

```text
cache/webqsp_eval100_subgraphs.jsonl
outputs/memory/webqsp_eval100_train_memory.jsonl
outputs/eval/webqsp_eval100_selector_eval.jsonl
outputs/eval/webqsp_eval100_selector_summary.json
```

子图召回：

```text
num_records: 100
gold_next_relation_edge_recall: 0.94
gold_next_relation_candidate_recall: 0.86
gold_answer_visible_rate: 0.62
avg_edges: 67.77
avg_candidate_actions: 51.47
gold_relation_rank_avg_when_visible: 26.45
```

selector 结果：

```text
num_examples: 100
rule_next_relation_accuracy: 0.12
memory_next_relation_accuracy: 0.45
memory_utility_delta: +0.33
memory_only_correct: 34
rule_only_correct: 1
same_delta: 65
avg_candidate_actions: 51.47
avg_memory_hits: 2.27
```

## 关键观察

第一，最初失败主要不是 policy 问题，而是 candidate recall 问题。原始 `SELECT ?r ?o LIMIT 50` 会被高频元信息关系和同一 relation 的多个 object 淹没，导致 gold relation candidate recall 只有 `0.15`。改为 relation-level sampled query，并过滤 `common.topic.*`、`type.object.*`、`kg.object_profile.*`、`freebase.*` 后，smoke candidate recall 提升到 `0.90`，eval100 candidate recall 达到 `0.86`。

第二，在 candidate relation 基本可见后，verified memory 有明显正向信号。Eval100 中 rule accuracy 为 `0.12`，memory accuracy 为 `0.45`，memory-only correct 为 34 条，rule-only correct 只有 1 条。这个结果支持 Idea1 的最小假设：跨 query 的 verified relation pattern memory 可以作为下一跳 action prior。

第三，当前 memory 不是最终方法，只是 gold/silver relation-chain memory。它验证的是“如果有 verified memory，是否值得把它纳入 agentic KGR policy”，还没有证明 learned memory updater、GRM 或 RLVR 训练范式本身有效。

## 正例样本

```json
{"question": "who was stephen r covey?", "gold_next_relation": "people.person.profession", "rule_top_relation": "people.person.quotationsbook_id", "memory_top_relation": "people.person.profession"}
{"question": "who plays captain kirk in star trek?", "gold_next_relation": "tv.tv_character.appeared_in_tv_program", "rule_top_relation": "book.book_character.appears_in_book", "memory_top_relation": "tv.tv_character.appeared_in_tv_program"}
{"question": "what college did john stockton go to?", "gold_next_relation": "people.person.education", "rule_top_relation": "sports.sports_award_winner.awards", "memory_top_relation": "people.person.education"}
{"question": "where is mitt romney's family from?", "gold_next_relation": "people.person.place_of_birth", "rule_top_relation": "people.person.sibling_s", "memory_top_relation": "people.person.place_of_birth"}
```

## 负例样本

```json
{"question": "what shows are shot in new york?", "gold_next_relation": "tv.tv_location.tv_shows_filmed_here", "rule_top_relation": "tv.tv_location.tv_shows_filmed_here", "memory_top_relation": "travel.travel_destination.tourist_attractions"}
```

这个负例说明 memory 需要 query-conditioned verification 或 GRM/reranker 抑制：只靠相似问题检索和 relation overlap，仍可能把 location 类问题拉向泛化但错误的旅游/地点关系。

## 当前结论

Idea1 值得继续推进，但下一步不应该直接上 RLVR。更稳的路线是：

1. 先把 relation-level candidate recall 固定住，并在 official train/dev split 上复测。
2. 加入 conditioned memory retrieval：去掉实体名干扰，使用 question type、topic entity type、candidate relation overlap、历史 verifier utility。
3. 做 pairwise action preference：gold next relation vs hard negatives，而不是只做 rule/memory top-1。
4. 用 0.6B 训练 action selector，只输出 action id，不直接生成答案。
5. 再加入 GRM reranker，评估它是否能减少 memory 负迁移。
6. 最后接 RLVR/GRPO，把 hard verifier reward、step utility 和 memory utility 合并进 rollout reward。

## 下一步已启动：Pairwise Action Preference

用户确认继续后，已启动下一步 `stage4`，目标是把 eval100 子图转成 pairwise action preference，为 0.6B action selector、pairwise ranker 和后续 RLVR warm start 准备数据。

执行命令：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage4 configs/webqsp_eval100.json
```

日志与产物：

```text
log: outputs via logs/stage4_20260901_203124.log
preferences: outputs/preferences/webqsp_eval100_pairwise_preferences.jsonl
summary: outputs/preferences/webqsp_eval100_pairwise_preferences_summary.json
```

结果：

```text
num_preferences: 341
num_source_subgraphs: 100
skipped.gold_not_in_candidates: 14
max_negatives_per_positive: 4
```

hard negative 来源：

```text
same_domain_hard_negative: 185
rule_top_wrong: 74
memory_top_wrong: 36
ranked_negative: 46
```

高频 gold relation：

```text
people.person.place_of_birth: 24
people.person.education: 20
people.person.spouse_s: 20
location.country.currency_used: 20
location.location.time_zones: 16
film.actor.film: 16
```

样例：

```json
{
  "question": "what is los angeles california time zone?",
  "gold_next_relation": "location.location.time_zones",
  "positive_action": {
    "action_type": "expand",
    "entity_id": "m.030qb3t",
    "relation_id": "location.location.time_zones"
  },
  "negative_action": {
    "action_type": "expand",
    "entity_id": "m.030qb3t",
    "relation_id": "location.location.area"
  },
  "negative_source": "same_domain_hard_negative",
  "verified_memory_relations": [
    "location.citytown.postal_codes",
    "location.location.time_zones"
  ]
}
```

这一步的意义是把“memory 提升 top-1 selection”的现象转成可训练监督信号。下一步应当把 preference 数据转换成 0.6B 可消费的 compact prompt/action-id 格式，训练一个只选择 action id 的小 selector，并做 `no-memory vs memory`、`random-memory vs verified-memory` 的模型级消融。

## 下一步继续推进：Train500 Preference 与 Compact Action Data

为了避免直接把 eval100 当训练集，本轮继续启动 `webqsp_train500`，用前 500 条 WebQSP pseudo-train 样本构造训练用子图、memory、pairwise preferences 和 0.6B 可消费的数据格式。

执行命令：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage1 configs/webqsp_train500.json
bash scripts/submit_nohup.sh stage2 configs/webqsp_train500.json
bash scripts/submit_nohup.sh stage4 configs/webqsp_train500.json
bash scripts/submit_nohup.sh stage5 configs/webqsp_train500.json
```

产物：

```text
cache/webqsp_train500_subgraphs.jsonl
outputs/memory/webqsp_train500_memory.jsonl
outputs/preferences/webqsp_train500_pairwise_preferences.jsonl
outputs/preferences/webqsp_train500_pairwise_preferences_summary.json
outputs/train_data/webqsp_train500_action_sft.jsonl
outputs/train_data/webqsp_train500_action_dpo.jsonl
outputs/train_data/webqsp_train500_action_data_summary.json
```

train500 子图召回：

```text
num_records: 500
gold_next_relation_edge_recall: 0.99
gold_next_relation_candidate_recall: 0.938
gold_answer_visible_rate: 0.642
avg_edges: 64.37
avg_candidate_actions: 48.86
gold_relation_rank_avg_when_visible: 24.64
```

train500 pairwise preference：

```text
num_preferences: 1857
num_source_subgraphs: 500
skipped.gold_not_in_candidates: 31
skipped.no_negative: 1
max_negatives_per_positive: 4
```

hard negative 来源：

```text
same_domain_hard_negative: 1048
rule_top_wrong: 365
ranked_negative: 320
memory_top_wrong: 124
```

compact action data：

```text
num_preferences_in: 1857
num_dpo_rows: 1857
num_sft_rows: 468
max_candidates_per_prompt: 80
```

SFT 样本格式：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a knowledge-graph reasoning action selector. Choose exactly one relation_id from the candidate relations. Return compact JSON only."
    },
    {
      "role": "user",
      "content": "Question: ...\nSeed entities: ...\nVerified memory relations: ...\nCandidate relations:\n0. ...\n\nSelect the best next-hop relation for graph traversal. Return JSON with key relation_id."
    },
    {
      "role": "assistant",
      "content": "{\"relation_id\": \"influence.influence_node.influenced_by\"}"
    }
  ],
  "target_relation_id": "influence.influence_node.influenced_by"
}
```

DPO/pairwise 样本格式：

```json
{
  "prompt": "Question: ...\nCandidate relations:\n0. ...",
  "chosen": "{\"relation_id\": \"location.location.time_zones\"}",
  "rejected": "{\"relation_id\": \"location.location.area\"}",
  "negative_source": "same_domain_hard_negative"
}
```

当前状态：数据格式准备已经完成，但还没有启动 0.6B 模型训练。下一步可以进入小模型实验：

1. `no_memory_sft`：prompt 中去掉 verified memory relations。
2. `memory_sft`：保留 verified memory relations。
3. `random_memory_sft`：替换成随机 memory relations。
4. 在 eval100 上比较 action selection accuracy、invalid relation rate、memory utility delta。

## Qwen3-0.6B 最小 SFT 实验

用户确认可以启动最小模型实验后，本轮使用服务器上已有的 Qwen3-0.6B 权重，没有重复下载模型。

模型与环境：

```text
model: /data/wxr/Finance/Qwen3-0.6B
python: /home/weixirun/anaconda3/envs/Finance/bin/python
GPU: CUDA_VISIBLE_DEVICES=3, NVIDIA RTX 3090
```

代码版本：

```text
ef9cb4d Add Qwen 0.6B minimal action selector training
```

执行命令：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
CUDA_VISIBLE_DEVICES=3 PYTHON_BIN=/home/weixirun/anaconda3/envs/Finance/bin/python \
  bash scripts/submit_nohup.sh stage6 configs/qwen3_0p6b_memory_sft_minimal.json
```

日志与产物：

```text
log: /data/wxr/AutoResearch/idea1-memory-kgr/logs/stage6_20260901_210324.log
run_dir: /data/wxr/AutoResearch/idea1-memory-kgr/runs/qwen3_0p6b_memory_sft_minimal_20260901_210324
summary: runs/qwen3_0p6b_memory_sft_minimal_20260901_210324/summary.json
adapter: runs/qwen3_0p6b_memory_sft_minimal_20260901_210324/adapter
```

训练设置：

```text
train_data: outputs/train_data/webqsp_train500_action_sft.jsonl
max_train_samples: 256
num_encoded_train_rows: 256
max_steps: 30
micro_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 2e-4
LoRA r/alpha/dropout: 8 / 16 / 0.05
trainable_params: 5,046,272 / 601,096,192 = 0.8395%
eval_data: eval100 subgraphs + eval100 verified memory
max_eval_samples: 60
```

结果：

```text
eval_before_accuracy: 0.0000
eval_before_invalid_rate: 1.0000
eval_after_accuracy: 0.7000
eval_after_invalid_rate: 0.0000
accuracy_delta: +0.7000
mean_loss: 0.077124
final_loss: 0.000402
```

初步解释：

- 未训练的 Qwen3-0.6B 虽然能读 prompt，但在这个 constrained JSON action selection 格式下没有稳定输出候选 relation，初始 invalid rate 为 1.0。
- 只用 256 条 SFT 样本、30 个 optimizer steps 的 LoRA warm start 后，模型已经能稳定输出合法 `relation_id`，eval60 下一跳 accuracy 达到 0.70。
- 这个结果证明“把 KGR 下一跳搜索动作压缩成 action selector，再用小模型快速验证”是可行的。
- 但这还不能单独证明 memory 的贡献，因为当前 prompt 保留了 verified memory relations，且 eval 只覆盖 60 条样本。下一步需要做 `no_memory_sft`、`random_memory_sft`、`verified_memory_sft` 三组模型级消融。

## Qwen3-0.6B Memory Ablation

为了判断提升是否真的来自 memory，本轮补充三组可比的 stage6 对照实验。三组实验都使用同一份 train500 SFT 数据、同一个 Qwen3-0.6B base model、同样的 LoRA 配置、同样的 256 条训练样本、30 个 optimizer steps 和 eval60 设置。

代码版本：

```text
c5e7441 Add Qwen memory ablation configs
```

对照定义：

```text
verified_memory: 训练和评估都保留 verified memory relations
no_memory: 训练和评估都把 memory relations 置为空列表
random_memory: 训练和评估都用候选 relation 中随机 relation 替换 verified memory
```

执行记录：

```text
no_memory:
  log: logs/stage6_20260901_211950.log
  run_dir: runs/qwen3_0p6b_no_memory_sft_minimal_20260901_211950
random_memory:
  log: logs/stage6_20260901_212358.log
  run_dir: runs/qwen3_0p6b_random_memory_sft_minimal_20260901_212358
verified_memory:
  log: logs/stage6_20260901_212727.log
  run_dir: runs/qwen3_0p6b_memory_sft_minimal_20260901_212727
```

注：第一次并行启动 `random_memory` 时落到繁忙 GPU 后 OOM 退出，随后单独绑定 GPU3 重跑成功；未执行清理或删除操作。

指标：

| setting | train_memory_mode | eval_memory_mode | eval_after_accuracy | eval_after_invalid_rate | mean_loss | final_loss |
|---|---|---|---:|---:|---:|---:|
| no_memory | none | none | 0.7167 | 0.0167 | 0.167086 | 0.073575 |
| random_memory | random | random | 0.7167 | 0.0167 | 0.160913 | 0.002509 |
| verified_memory | verified | verified | 0.7333 | 0.0000 | 0.077972 | 0.000523 |

正确集合重叠：

```text
all_correct: 36
verified_only_vs_no: 6
no_only_vs_verified: 5
verified_only_vs_random: 8
random_only_vs_verified: 7
all_wrong: 8
```

verified memory 帮助的样例：

```json
{"qid": "WebQTest-1031", "question": "what has angelina jolie accomplished?", "gold": "people.person.profession", "verified_pred": "people.person.profession", "no_pred": "award.award_winner.awards_won", "random_pred": "award.award_winner.awards_won", "verified_memory": ["film.actor.film", "people.person.parents", "people.person.profession"]}
{"qid": "WebQTest-1164", "question": "what type of art does claude monet do?", "gold": "visual_art.visual_artist.associated_periods_or_movements", "verified_pred": "visual_art.visual_artist.associated_periods_or_movements", "no_pred": "visual_art.visual_artist.art_forms", "random_pred": "people.person.profession", "verified_memory": ["people.person.profession", "visual_art.visual_artist.art_forms", "visual_art.visual_artist.associated_periods_or_movements"]}
{"qid": "WebQTest-1464", "question": "what to do with my kids in toronto?", "gold": "travel.travel_destination.tourist_attractions", "verified_pred": "travel.travel_destination.tourist_attractions", "no_pred": "travel.travel_destination.how_to_get_here", "random_pred": "travel.travel_destination.how_to_get_here", "verified_memory": ["travel.travel_destination.tourist_attractions"]}
```

verified memory 误导的样例：

```json
{"qid": "WebQTest-1329", "question": "who played bilbo in the fellowship of the ring?", "gold": "film.film.starring", "verified_pred": "film.film_character.portrayed_in_films", "no_pred": "film.film.starring", "random_pred": "film.film.starring", "verified_memory": ["film.film.starring", "film.film_character.portrayed_in_films"]}
{"qid": "WebQTest-1333", "question": "where does the tennessee river go?", "gold": "geography.river.mouth", "verified_pred": "geography.river.origin", "no_pred": "geography.river.mouth", "random_pred": "geography.river.mouth", "verified_memory": ["geography.river.mouth", "geography.river.origin", "location.location.partially_contained_by"]}
{"qid": "WebQTest-312", "question": "who plays captain kirk in star trek?", "gold": "tv.tv_character.appeared_in_tv_program", "verified_pred": "film.film_character.portrayed_in_films", "no_pred": "tv.tv_character.appeared_in_tv_program", "random_pred": "film.film_character.portrayed_in_films", "verified_memory": ["film.film_character.portrayed_in_films", "tv.tv_character.appeared_in_tv_program"]}
```

当前结论：

1. Qwen3-0.6B 经过极少量 SFT 后已经能学会 action selection 输出格式，invalid rate 从 1.0 降到约 0。
2. 在 WebQSP eval60 的浅跳场景中，verified memory 的模型级收益很小：相对 no/random 只多对 1/60。
3. memory 不是天然有效，主要问题是“多个候选 memory relation 同时合理”时会放大混淆；这直接指向 GRM/reranker 或 memory gating，而不是继续把 memory 简单拼进 prompt。
4. 对 Idea1 来说，下一步更应该把问题定义成：如何让 agent 在 query-conditioned subgraph 中判断哪些 memory 可用、哪些 memory 应该被抑制，而不是只证明“有 memory 字段会更好”。
