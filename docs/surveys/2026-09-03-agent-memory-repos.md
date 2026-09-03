---
title: "Agent Memory Repository Watchlist"
type: survey
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agentic-memory", "repos", "benchmark", "framework"]
---

# Agent Memory 仓库与代码清单

## Benchmark 优先

| 仓库 | 类型 | 用途 | 备注 |
| --- | --- | --- | --- |
| https://github.com/HUST-AI-HYZ/MemoryAgentBench | benchmark | incremental multi-turn memory agent benchmark | GitHub 标注 ICLR 2026；最贴 agent memory |
| https://github.com/THUIR/MemoryBench | benchmark | memory and continual learning in LLM systems | 关注用户反馈和服务时学习 |
| https://github.com/seucoin/StratMem-Bench | benchmark | strategic memory use in virtual character dialogue | ACL 2026；`must/nice/irr` 三类 memory 很适合借鉴 |
| https://github.com/zjunlp/MobileMem | benchmark | on-device personal long-term memory | arXiv 2026 technical report；KEME 数据合成和多源手机记忆场景很适合参考 |
| https://github.com/xiaowu0162/LongMemEval | benchmark | long-term interactive memory | ICLR 2025；适合先复现 |
| https://github.com/snap-research/locomo | benchmark | very long-term conversational memory | ACL 2024；经典长期对话 memory |
| https://github.com/GoodAI/goodai-ltm-benchmark | benchmark/library | LTM and continual learning tests | 工程化 benchmark，可看任务设计 |
| https://github.com/bowen-upenn/PersonaMem | benchmark | dynamic user profiling/personalization | COLM 2025；适合偏好演化子任务 |

## Framework / Memory Backend

| 仓库 | 类型 | 用途 | 备注 |
| --- | --- | --- | --- |
| https://github.com/mem0ai/mem0 | framework | production memory layer | star 多，适合做强工程 baseline |
| https://github.com/letta-ai/letta | framework | stateful agent / MemGPT successor | OS-style memory baseline |
| https://github.com/Mirix-AI/MIRIX | framework | typed multi-agent memory system | 六类 memory + multi-agent managers |

## 建议复现顺序

1. `LongMemEval`：先确认数据、评测和 baseline 依赖能否在服务器跑通。
2. `MobileMem`：看 on-device/personal memory 的数据 schema、KEME 合成流程和 baseline 设置。
3. `MemoryAgentBench`：看 incremental multi-turn interaction 的 schema，决定是否复用。
4. `LoCoMo`：作为长期对话 memory 的经典支撑和对照。
5. `PersonaMem`：抽取 personalization/dynamic profile 的任务模式。
6. `Mem0` / `Letta` / `MIRIX`：作为 memory backend baseline，而不是一开始就改它们的源码。

## 不建议第一轮做的事

- 不第一轮 clone 大量仓库进主 repo。
- 不第一轮训练 memory policy。
- 不第一轮设计复杂 web/browser environment。
- 不第一轮做端侧 multimodal benchmark。

第一轮目标是把 benchmark schema 和 baseline runner 确定下来。
