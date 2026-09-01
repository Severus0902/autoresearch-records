---
title: "Idea1 实验代码框架：Memory-Guided Subgraph Action Selector"
type: experiment
status: draft
created: "2026-09-01"
zotero: ["@yanExploreongraphIncentivizingAutonomous2026a", "@sunThinkongraphDeepResponsible2024", "@luoReasoningGraphsFaithful2024", "@jiangKGagentEfficientAutonomous2025", "@luReasoningEpisodicMemory2026", "@linMemoryR1EnhancingLarge2026", "@xiaoMEM1LearningSynergize2026", "@yuGraphRAGR1GraphRetrievalaugmented2026"]
tags: ["idea1", "agentic-kgr", "memory", "rlvr", "experiment-framework", "server"]
---

# Idea1 实验代码框架：Memory-Guided Subgraph Action Selector

## 当前边界

本文件只定义实验代码框架和运行方案，不启动训练、不创建远端工程、不修改远端数据集。远端服务器可通过 SSH 访问：

```text
target: wxr-server
user: weixirun
allowed_remote_root: /data/wxr
default_workdir: /data/wxr
```

硬约束：

1. 所有远端操作只能发生在 `/data/wxr` 下。
2. 删除指令默认禁用，包括 `rm`、`rmdir`、`unlink`、`find -delete`、覆盖式清理脚本等。
3. 如果确实需要删除临时文件，必须先说明删除路径、删除原因和影响范围，得到明确允许后再执行。
4. 实验运行前必须先给出命令、日志路径、输出路径和预计资源消耗，由用户确认后再运行。
5. 长任务统一使用 `nohup`、日志文件和 pid 文件，防止 SSH/Cursor 断连导致实验中断。

## 服务器只读盘点

已经通过只读 SSH 检查确认 `/data/wxr` 下有以下相关资源：

| 路径 | 观察 | 用途 |
|---|---|---|
| `/data/wxr/Pilotenv` | 现有 pilot 环境，包含 `data/webqsp.json`、`kg/`、`baselines/`、`tests/`、`run_pilot.py`。 | 第一版代码可参考 loader、answer_eval 和 simple ToG baseline。 |
| `/data/wxr/Pilotenv/data/webqsp.json` | 约 6.5 MB，标准 WebQSP list 格式；样本含 `RawQuestion`、`TopicEntityMid`、`InferentialChain`、`Answers`。 | Idea1 的 WebQSP pilot 数据源。 |
| `/data/wxr/Pilotenv/kg/kg_loader.py` | 已有 `VirtuosoKGLoader`，支持 SPARQL endpoint 查询 Freebase 出边和 `type.object.name`。 | 可复用为 KG access adapter。 |
| `/data/wxr/Pilotenv/kg/answer_eval.py` | 已有 answer matching 和 mid-name resolution 逻辑。 | 可复用为初版 answer evaluator。 |
| `/data/wxr/Pilotenv/baselines/simple_tog.py` | 简化 ToG baseline，当前偏一次性 triples prompt。 | 可作为弱 baseline，不作为最终强基线。 |
| `/data/wxr/PoG-main/data/cwq.json` | 约 3.8 MB，CWQ 样本含 `question`、`sparql`、`topic_entity`、`answer`。 | CWQ pilot/正式数据源。 |
| `/data/wxr/PoG-main/data/WebQSP.json` | 与 Pilotenv WebQSP 大小一致。 | WebQSP 备用数据源。 |
| `/data/wxr/PoG-main/FilterFreebase` | Freebase 相关资源目录。 | 可能用于 Virtuoso/Freebase 数据服务。 |
| `/data/wxr/virtuoso-opensource/database/FilterFreebase` | Freebase 数据库目录。 | 可能是 Virtuoso 数据库副本。 |
| `/data/wxr/Enrich-on-Graph` | EMNLP 2025 Enrich-on-Graph 代码，含 RoG-webqsp 数据和 workflow。 | 后续 EoG/GraphRAG 近邻代码参考，不作为第一版依赖。 |

额外环境观察：

```text
/data 分区剩余约 656 GB，可用于实验工程、cache、日志和输出。
/ 根分区只剩约 18 GB，不应把模型缓存或实验输出写到 /home。
127.0.0.1:8890/sparql 当前只读探测为 connection refused，说明 Virtuoso endpoint 可能未启动或端口不同。
```

因此第一版框架应把所有新代码、日志、缓存和结果放在 `/data/wxr/autoresearch/idea1-memory-kgr`，并在运行前先验证 Virtuoso endpoint。

## Idea1 要解决的问题

一句话定义：

> 解决 agentic KGR 在高 branching、noisy entity/relation linking 和有限 step/tool budget 下，每个 query 从零搜索、重复犯相似局部错误的问题。

更具体地说，给定自然语言问题、Freebase KG、query-centered subgraph、训练轨迹形成的 verified memory，以及固定预算，训练一个 online action policy：

```text
pi_theta(a_t | q, state_t, memory_t, verifier_feedback_t)
```

它在每一步从合法动作中选择：

```text
expand(entity_id, relation_id)
backtrack()
read_memory()
retrieve_text(optional)
stop(answer_entity_id, supporting_path)
```

目标是在相同预算下提高：

```text
answer_hit_within_budget
gold_path_edge_recall
next_relation_accuracy
path_validity
```

同时降低：

```text
invalid_action_rate
steps_to_answer
spurious_path_rate
memory_leakage_risk
```

## 第一版实验原则

第一版不追完整 SOTA，不直接复现 EoG 全量训练，也不让 0.6B 模型自由生成长答案。第一版只验证一个最小信号：

> 在同样的 query-centered subgraph 和同样的 action budget 下，verified memory 是否能帮助小模型或 scorer 选出更好的下一步 relation/action。

因此实验分三层：

| 层级 | 目标 | 是否第一版必须 |
|---|---|---|
| Environment | 构造 WebQSP/CWQ 的 query-centered subgraph、合法 action set、verifier 和日志。 | 必须 |
| Offline policy | 用 oracle/silver trajectories 训练或评测 next-step action selector。 | 必须 |
| Online RLVR | 用 rollout + verifier reward 做 GRPO/PPO 类优化。 | 暂不运行，只预留接口 |

## 推荐远端工程目录

后续经用户确认后，在远端创建：

```text
/data/wxr/autoresearch/idea1-memory-kgr/
  README.md
  configs/
    webqsp_pilot.yaml
    cwq_pilot.yaml
  data_adapters/
    webqsp_adapter.py
    cwq_adapter.py
    freebase_adapter.py
  envs/
    kgqa_env.py
    action_space.py
    verifier.py
    subgraph_builder.py
  memory/
    schema.py
    store.py
    retriever.py
    verifier.py
    updater.py
  policies/
    rule_relation_ranker.py
    simple_tog_bridge.py
    memory_action_selector.py
    grm_reranker.py
  training/
    build_silver_trajectories.py
    build_pairwise_preferences.py
    train_sft_selector.py
    train_pairwise_ranker.py
    run_rlvr_stub.py
  evaluation/
    metrics.py
    eval_next_step.py
    eval_rollout.py
    leakage_check.py
  scripts/
    stage0_inventory.sh
    stage1_build_subgraphs.sh
    stage2_build_memory.sh
    stage3_train_selector.sh
    stage4_eval_ablation.sh
  logs/
  outputs/
  cache/
  runs/
```

说明：

- `logs/`、`outputs/`、`cache/`、`runs/` 全部在 `/data/wxr/autoresearch/idea1-memory-kgr` 内。
- 第一版只读取 `/data/wxr/Pilotenv`、`/data/wxr/PoG-main` 和 Freebase/Virtuoso 服务，不改原项目。
- 如果需要写入数据预处理产物，只写入新工程的 `cache/` 或 `outputs/`。

## 模块设计

### 1. Data adapters

`webqsp_adapter.py` 读取：

```text
/data/wxr/Pilotenv/data/webqsp.json
```

输出统一样本格式：

```json
{
  "dataset": "webqsp",
  "qid": "WebQTest-1198",
  "question": "who influenced samuel taylor coleridge?",
  "topic_entities": [{"mid": "m.078w2", "name": "Samuel Taylor Coleridge"}],
  "gold_answers": [{"mid": "m.015_hb", "name": "Giambattista Vico"}],
  "gold_relation_chain": ["influence.influence_node.influenced_by"],
  "sparql": "...",
  "split": "test"
}
```

`cwq_adapter.py` 读取：

```text
/data/wxr/PoG-main/data/cwq.json
```

输出统一样本格式：

```json
{
  "dataset": "cwq",
  "qid": "...",
  "question": "Lou Seal is the mascot for the team that last won the World Series when?",
  "topic_entities": [{"mid": "m.03_dwn", "name": "Lou Seal"}],
  "gold_answers": [{"text": "2014 World Series"}],
  "gold_relation_chain": null,
  "sparql": "...",
  "split": "unknown"
}
```

### 2. Freebase adapter

第一版优先复用 `Pilotenv/kg/kg_loader.py` 中的 `VirtuosoKGLoader` 思路，封装成：

```python
class FreebaseAdapter:
    def get_out_edges(self, mid: str, limit: int) -> list[Triple]: ...
    def get_in_edges(self, mid: str, limit: int) -> list[Triple]: ...
    def get_names(self, mid: str, limit: int) -> list[str]: ...
    def execute_sparql(self, sparql: str) -> dict: ...
```

运行前必须先做 endpoint 检查：

```bash
curl -I http://127.0.0.1:8890/sparql
```

如果 8890 不通，再检查 Virtuoso 是否需要启动或端口是否不同。启动服务属于环境操作，先只写入文档，不直接执行。

### 3. Subgraph builder

输入 question 和 topic entities，构造受预算限制的局部子图：

```text
max_hop: 2 for WebQSP pilot, 3 or 4 for CWQ pilot
max_nodes: 200
max_edges: 500
max_relation_candidates: 20
max_paths: 20
```

输出：

```json
{
  "qid": "...",
  "seed_entities": ["m.078w2"],
  "nodes": [...],
  "edges": [...],
  "frontier": [...],
  "candidate_actions": [
    {"action": "expand", "entity": "m.078w2", "relation": "influence.influence_node.influenced_by"}
  ],
  "oracle": {
    "gold_answer_visible": true,
    "gold_relation_visible": true,
    "gold_path_visible": true
  }
}
```

第一版必须报告 `oracle_subgraph_recall`，否则无法判断是 policy 不行，还是子图构造已经把答案丢了。

### 4. Verified memory store

Memory 不存具体测试答案，不存完整测试问题，不存 gold path 的 dev/test 信息。第一版只从 train trajectories 写入：

```json
{
  "memory_id": "webqsp_train_000001_step2",
  "source_split": "train",
  "question_pattern": "who influenced <person>",
  "seed_entity_types": ["person"],
  "relation_template": ["influence.influence_node.influenced_by"],
  "successful_action": {
    "type": "expand",
    "relation": "influence.influence_node.influenced_by"
  },
  "failed_actions": [
    {"type": "expand", "relation": "people.person.profession", "reason": "spurious_neighbor"}
  ],
  "verifier_result": {
    "path_valid": true,
    "answer_reached": true
  },
  "utility": {
    "delta_gold_path_edge_recall": 1.0,
    "delta_invalid_action": -1,
    "delta_steps_to_answer": -1
  }
}
```

Memory 检索条件：

```text
question pattern similarity
topic entity type overlap
candidate relation overlap
historical verifier result
memory utility score
```

Memory 使用规则：

1. 召回后只作为 action prior。
2. 必须在当前 subgraph/candidate actions 中重新验证 relation/action 是否可用。
3. 未验证 memory 不能参与正 reward。
4. dev/test 阶段全局 memory 只读。

### 5. Action policy

第一版 policy 不直接生成答案文本，只输出受控 action JSON：

```json
{
  "action": "expand",
  "entity_id": "m.078w2",
  "relation_id": "influence.influence_node.influenced_by",
  "reason": "verified memory suggests this relation for influence questions"
}
```

最小模型路线：

| 阶段 | 模型/方法 | 目标 |
|---|---|---|
| Rule baseline | relation lexical ranker | 快速确认数据和 verifier。 |
| No-memory selector | 0.6B SFT 或 scorer | 学会合法下一步 action。 |
| Verified-memory selector | 0.6B + memory hints | 测 memory 是否提高 next-step decision。 |
| GRM reranker | 7B/8B 或 API model 生成诊断 | 评价 step utility、memory utility、stop quality。 |
| Online RLVR | 暂不第一版运行 | 等 offline 信号稳定后再做。 |

### 6. Verifier and reward

Hard verifier：

```text
action_legality: entity/relation/action 是否存在于当前候选集合
path_validity: 执行动作后路径是否连通且方向正确
answer_reached: frontier/path 是否到达 gold answer entity 或可解析 answer
format_validity: action JSON 是否可解析
budget_validity: 是否超 step/tool/token 预算
```

Reward：

```text
R = R_answer
  + beta * R_hard_graph
  + gamma * R_step_utility
  + eta * R_memory_utility
  - delta * Cost
```

其中第一版只实现可程序化部分：

```text
R_answer
R_hard_graph
R_step_utility
R_memory_utility_delta
Cost
```

GRM 第一版只作为日志诊断或 reranker，不直接驱动 online RL。

## 实验阶段

### Stage 0: Inventory and endpoint validation

目的：确认数据路径、Python 环境、Freebase endpoint、写入目录和日志目录。

只读/轻量命令示例：

```bash
cd /data/wxr
python3 --version
df -h /data/wxr
curl -I http://127.0.0.1:8890/sparql
```

预期输出：

```text
server reachable
dataset files readable
output root writable after user approval
Virtuoso endpoint reachable or marked as blocked
```

### Stage 1: Build unified samples and subgraphs

输入：

```text
/data/wxr/Pilotenv/data/webqsp.json
/data/wxr/PoG-main/data/cwq.json
```

输出：

```text
cache/webqsp_samples.jsonl
cache/cwq_samples.jsonl
cache/webqsp_subgraphs.jsonl
cache/cwq_subgraphs.jsonl
```

关键指标：

```text
num_samples
seed_entity_recall
oracle_subgraph_recall
avg_nodes
avg_edges
avg_candidate_actions
```

### Stage 2: Build silver trajectories and memory

Silver trajectory 来源：

1. WebQSP 的 `InferentialChain`。
2. CWQ 的 SPARQL relation sequence。
3. shortest-path 或 constrained BFS。
4. ToG/PoG-style rollout，作为后续增强。

Memory 从 train split 的成功/失败 trajectories 生成：

```text
outputs/memory/train_memory.jsonl
outputs/preferences/pairwise_next_step.jsonl
```

### Stage 3: Train or evaluate action selector

第一版可先不训模型，先做 reranking/scoring ablation：

| Variant | 含义 |
|---|---|
| rule_relation_ranker | 只用 relation/question lexical overlap。 |
| no_memory_selector | 不给 memory，只用当前 state。 |
| random_memory_selector | 给随机 memory，检测噪声影响。 |
| unverified_memory_selector | 给语义相似但未验证 memory。 |
| verified_memory_selector | 给当前子图可验证 memory。 |
| verified_memory_plus_grm | verified memory + GRM/reranker。 |

如果第一版要训练 0.6B，则只训练：

```text
input: q + compact state + candidate actions + verified memory hints
output: preferred action id
```

### Stage 4: Evaluation

核心指标：

```text
next_relation_accuracy
answer_hit_within_budget
gold_path_edge_recall
oracle_subgraph_recall
invalid_action_rate
steps_to_answer
memory_hit_rate
memory_utility_delta
spurious_path_rate
```

必须报告的消融：

```text
no memory
random memory
unverified memory
verified memory
verified memory without GRM
GRM without memory
full method
```

## nohup 运行方案

所有长任务都用 `nohup`，并把 stdout/stderr 写入日志。示例命令如下，只有用户确认后才执行。

### 环境盘点

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
mkdir -p logs
nohup bash scripts/stage0_inventory.sh > logs/stage0_inventory_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > logs/stage0_inventory.pid
```

### 构造子图

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
mkdir -p logs cache outputs
nohup bash scripts/stage1_build_subgraphs.sh configs/webqsp_pilot.yaml > logs/stage1_webqsp_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > logs/stage1_webqsp.pid
```

### 构造 memory 和 pairwise 偏好

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
nohup bash scripts/stage2_build_memory.sh configs/webqsp_pilot.yaml > logs/stage2_memory_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > logs/stage2_memory.pid
```

### 训练/评估 selector

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
nohup bash scripts/stage3_train_selector.sh configs/webqsp_pilot.yaml > logs/stage3_selector_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > logs/stage3_selector.pid
```

### 查看任务状态

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
cat logs/stage3_selector.pid
tail -n 100 logs/stage3_selector_YYYYMMDD_HHMMSS.log
```

注意：这里的 `tail`、`cat`、`ps` 是只读观察命令，可以执行；任何删除日志、清 cache、覆盖结果的命令都需要额外确认。

## 第一版最小验证建议

优先顺序：

1. WebQSP pilot，先抽 500 条 train、100 条 dev。
2. 只做 `max_hop=2` 的 query-centered subgraph。
3. 不训练大模型，先实现 rule baseline + memory reranker，确认 memory signal。
4. 如果 verified memory 相比 no-memory 提升 `next_relation_accuracy` 或 `gold_path_edge_recall`，再训练 0.6B selector。
5. 如果 WebQSP 有信号，再切 CWQ，测试 3-4 hop 和更复杂 compositionality。

第一版成功标准：

```text
verified memory > no memory
verified memory > random memory
verified memory > unverified memory in path faithfulness
memory_utility_delta > 0 under same step budget
```

第一版失败信号：

```text
oracle_subgraph_recall low
memory_hit_rate low
verified memory and random memory no difference
unverified memory improves answer but hurts path validity
```

如果失败，优先修 data/subgraph/memory schema，不急着进入 RL。

## 待用户确认后才执行的事项

以下动作都还没有执行，需要用户明确确认：

1. 在 `/data/wxr/autoresearch/idea1-memory-kgr` 创建远端工程目录。
2. 写入实验代码 skeleton。
3. 检查或启动 Virtuoso/Freebase endpoint。
4. 生成 WebQSP/CWQ cache。
5. 运行任何 `nohup` 任务。
6. 安装依赖、创建 conda/env、下载模型或写入 HuggingFace cache。

当前可以立即执行的下一步是：用户审核本文件后，确认是否进入“创建远端代码 skeleton，不运行实验”的阶段。
