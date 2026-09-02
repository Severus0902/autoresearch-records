# Idea1: Memory-Guided KGR Experiment Framework

这个目录是 Idea1 的第一版实验代码框架。它参考 EoG 的两个核心工程信号：

- 把 KGQA 转成可验证的 graph-grounded reasoning 任务。
- 用函数式 reward 检查 reasoning path，而不是只看最终答案文本。

我们的差异是：先不直接复现 EoG 的完整 `verl/GRPO` 训练，而是把 KGR 过程拆成可控的 `state -> action -> verifier -> memory -> reward` 闭环，优先验证 verified memory 是否能在 WebQSP/CWQ 的局部子图搜索中改善下一跳选择。

## Safety Boundary

远端默认工作目录：

```text
/data/wxr/AutoResearch/idea1-memory-kgr
```

约束：

- 只在 `/data/wxr` 下创建和写入实验框架、日志、cache、outputs、runs。
- 不在脚本里执行删除命令。
- 输出文件默认不覆盖；如果文件已存在，脚本会报错，除非显式加 `--overwrite`。
- 长任务只通过 `scripts/submit_nohup.sh` 提交，并写入 `logs/*.log` 和 `logs/*.pid`。

## Layout

```text
configs/
  webqsp_pilot.json
  cwq_pilot.json
  qwen3_0p6b_memory_sft_minimal.json
  qwen3_0p6b_no_memory_sft_minimal.json
  qwen3_0p6b_random_memory_sft_minimal.json
idea1_kgr/
  data_adapters.py
  freebase_adapter.py
  subgraph_builder.py
  memory_store.py
  policies.py
  verifier.py
  metrics.py
scripts/
  stage0_inventory.py
  stage1_build_subgraphs.py
  stage2_build_memory.py
  stage3_eval_selector.py
  stage4_build_pairwise_preferences.py
  stage5_prepare_action_data.py
  stage6_train_qwen_action_selector.py
  stage7_eval_memory_gate.py
  submit_nohup.sh
tests/
  test_core.py
```

## Suggested First Run

先只做环境盘点，确认数据、输出目录和 SPARQL endpoint：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage0 configs/webqsp_pilot.json
```

再做 WebQSP 小样本：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage1 configs/webqsp_smoke.json
bash scripts/submit_nohup.sh stage2 configs/webqsp_smoke.json
bash scripts/submit_nohup.sh stage3 configs/webqsp_smoke.json
bash scripts/submit_nohup.sh stage4 configs/webqsp_smoke.json
bash scripts/submit_nohup.sh stage5 configs/webqsp_smoke.json
```

这些命令只是推荐执行方式。本轮只上传代码，不启动任何实验。

## Experiment Variants

第一版只验证下一跳 action selection：

- `rule`: 只用 question/relation lexical overlap。
- `memory`: 在当前 candidate action 可验证的前提下加入 train split 形成的 memory prior。

后续扩展：

- `random_memory`: 排查 memory 噪声是否伪提升。
- `unverified_memory`: 验证“只检索相似经验但不落到当前子图验证”是否会污染路径。
- `grm_reranker`: 加生成式奖励模型/图证据 judge，对候选 action 或完整路径重排。
- `rlvr`: 只在 offline signal 稳定后接 GRPO/PPO 类训练。

## Pairwise Preference Format

`stage4` 会把每个可见 gold next relation 的样本转成若干 pairwise action preference：

```json
{
  "qid": "WebQTest-1215",
  "question": "who was stephen r covey?",
  "positive_action": {"action_type": "expand", "relation_id": "people.person.profession"},
  "negative_action": {"action_type": "expand", "relation_id": "people.person.quotationsbook_id"},
  "negative_source": "rule_top_wrong"
}
```

这一步不训练模型，只为后续 0.6B action selector、pairwise reward/ranker 和 RLVR warm start 准备数据。

`stage5` 会进一步导出两种 compact 数据：

- SFT JSONL：每个 qid 一个 `messages` 训练样本，assistant 只输出 `{"relation_id": "..."}`。
- DPO/pairwise JSONL：每条 preference 一个 `prompt/chosen/rejected` 样本。

`stage5` 仍然只是数据准备，不启动模型训练。

## Minimal 0.6B Training

`stage6` 用 Qwen3-0.6B 做最小 action selector SFT。推荐先使用已有模型目录：

```text
/data/wxr/Finance/Qwen3-0.6B
```

启动示例：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
PYTHON_BIN=/home/weixirun/anaconda3/envs/Finance/bin/python \
  bash scripts/submit_nohup.sh stage6 configs/qwen3_0p6b_memory_sft_minimal.json
```

默认只做小步 LoRA SFT，并在 eval100 上做 greedy action selection 评估。输出目录位于 `runs/` 下。

### Memory Ablations

`stage6` 支持三种 prompt memory 条件：

- `verified`: 训练和评估都保留 verified memory relations。
- `none`: 训练和评估都把 memory relations 置为空列表。
- `random`: 训练和评估都用候选 relation 中的随机 relation 替换 verified memory，保持字段格式不变。

对照组示例：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
CUDA_VISIBLE_DEVICES=3 PYTHON_BIN=/home/weixirun/anaconda3/envs/Finance/bin/python \
  bash scripts/submit_nohup.sh stage6 configs/qwen3_0p6b_no_memory_sft_minimal.json
CUDA_VISIBLE_DEVICES=0 PYTHON_BIN=/home/weixirun/anaconda3/envs/Finance/bin/python \
  bash scripts/submit_nohup.sh stage6 configs/qwen3_0p6b_random_memory_sft_minimal.json
```

## Stage7: Memory Gate / GRM-Lite

`stage7` 是 gate 诊断阶段。它不重新加载 Qwen 权重，也不访问 Freebase，而是读取 stage6 的三组逐样本预测：

- `no_memory`
- `random_memory`
- `verified_memory`

它会评估：

- always-no / always-random / always-verified 三个基线。
- 若干 rule gate，例如 memory 非空才使用、verified 预测在 memory 中才使用。
- `loocv_grm_lite_gate`：用 leave-one-out 方式训练一个轻量线性 gate，估计可学习 gating 的初步空间。
- `oracle_no_vs_verified`：如果完美知道 memory 是否会帮忙，在 no-memory 和 verified-memory 之间切换的上限。

启动示例：

```bash
cd /data/wxr/AutoResearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage7 configs/qwen3_0p6b_memory_gate_eval.json
```

这一步的目的不是形成正式论文指标，而是判断下一步是否值得训练真正的 GRM/memory gate。
