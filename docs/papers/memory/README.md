---
title: "Agent Memory 2025-2026 精读索引"
type: literature-notes
status: reviewed
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "deep-reading", "2025", "2026"]
---

# Agent Memory 2025-2026 精读索引

本目录汇总当前选题直接相关的 2025-2026 年论文。优先级不是论文质量排序，而是对 agent memory benchmark 选题及其最终收敛方向 `ResearchLedgerBench` 的直接影响程度。

## 阅读范围

- [P0：直接竞争 benchmark](./2025-2026-p0-deep-reading.md)：7 篇。
- [P1：关键 memory method](./2025-2026-p1-deep-reading.md)：16 篇。
- [P2：结构、程序性记忆与安全边界](./2025-2026-p2-deep-reading.md)：7 篇。
- [核心综述](./memory-surveys-deep-reading.md)：6 篇综述，并补充 MobileMem 作为近期 benchmark 锚点。
- [前沿撞题审查](./2026-09-frontier-collision-audit.md)：补查 Paper-Notes 清单之外、会直接改变 gap 的 2026 年新工作。
- [两阶段研究路线](../../ideas/2026-09-03-agent-memory-two-stage-research-roadmap.md)：第一阶段 benchmark，第二阶段 method。

## 统一术语

- `memory operation`：一次原子操作，如 `ADD / UPDATE / IGNORE / PROTECT / RETRIEVE / USE`。
- `memory lifecycle`：从信息进入系统到后续被检索、使用、过期或保护的完整流程。
- `operation trace`：一个 episode 中每个事件应触发的 gold memory operation 序列。
- `evidence role`：某条记忆对当前任务的角色，分为 `required / supportive / irrelevant / stale / forbidden`。
- `causal diagnosis`：通过 oracle-write、oracle-retrieval、oracle-use 等受控替换，定位最终失败由哪个模块造成。
- `versioned scientific validity`：结果或 claim 只在特定 code、data、config 与 environment 版本组合下有效。
- `dependency closure`：支持或失效一个 claim 所需遍历的完整 artifact 依赖集合。

## 阅读结论预告

现有工作已经分别覆盖 write/read/use、更新与遗忘、增量交互、战略性使用、跨平台状态追踪和隐私泄露。进一步核验发现，MemTrace 已覆盖 execution graph 和 operation-level failure attribution，EvoMemBench 已统一 in/cross-episode 与 knowledge/execution memory，StateMemBench、AuthMem-Bench、TANGLE 等也分别覆盖状态、权威和不可解冲突。因此“通用 operation trace benchmark”同样不够新。当前更推荐转向带明确领域对象的 `ResearchLedgerBench`：评测长期科研 agent 能否维护 hypothesis-code-data-run-result-claim 的版本化依赖与有效性。

## 证据边界

本轮精读以论文正式页面、arXiv/OpenReview 记录和 `Severus0902/Paper-Notes` 的全文笔记为主。定量结果只记录可从这些来源确认的数字；尚未公开代码或只在 workshop/arXiv 出现的工作会显式标注，不把预印本结果等同于稳定结论。
