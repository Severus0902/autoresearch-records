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
