# Idea1: Memory-Guided KGR Experiment Framework

这个目录是 Idea1 的第一版实验代码框架。它参考 EoG 的两个核心工程信号：

- 把 KGQA 转成可验证的 graph-grounded reasoning 任务。
- 用函数式 reward 检查 reasoning path，而不是只看最终答案文本。

我们的差异是：先不直接复现 EoG 的完整 `verl/GRPO` 训练，而是把 KGR 过程拆成可控的 `state -> action -> verifier -> memory -> reward` 闭环，优先验证 verified memory 是否能在 WebQSP/CWQ 的局部子图搜索中改善下一跳选择。

## Safety Boundary

远端默认工作目录：

```text
/data/wxr/autoresearch/idea1-memory-kgr
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
  submit_nohup.sh
tests/
  test_core.py
```

## Suggested First Run

先只做环境盘点，确认数据、输出目录和 SPARQL endpoint：

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage0 configs/webqsp_pilot.json
```

再做 WebQSP 小样本：

```bash
cd /data/wxr/autoresearch/idea1-memory-kgr
bash scripts/submit_nohup.sh stage1 configs/webqsp_pilot.json
bash scripts/submit_nohup.sh stage2 configs/webqsp_pilot.json
bash scripts/submit_nohup.sh stage3 configs/webqsp_pilot.json
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
