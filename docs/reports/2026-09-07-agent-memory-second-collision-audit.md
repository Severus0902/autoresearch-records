---
title: "Agent Memory 收紧问题的第二轮同期工作碰撞审计"
type: research-gap-audit
status: recommendation
created: "2026-09-07"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "memory-repair", "world-state", "causal-recovery", "collision-audit"]
---

# Agent Memory 收紧问题的第二轮同期工作碰撞审计

> 检索截止时间：2026-09-07。本轮重点补查 2025--2026 年正式论文、会议页面和最新 arXiv 预印本，关注 persistent memory、外部动作、事故恢复、环境补偿、级联修复和无 oracle 故障定位的交集。预印本状态可能继续变化，本文只判断研究问题与协议重合度。

## 0. 结论先行

### 0.1 不是没有相似工作，而是已经出现强碰撞

第一轮收紧后的问题是：

> 在不知道 gold 故障记忆 ID 的条件下，当跨会话持久记忆已经诱导 Agent 向外部环境提交错误动作后，Agent 能否定位致错记忆及其影响范围，执行环境补偿与记忆修复，并保证后续不再复发？

继续检索后，这个表述仍然**过宽**。至少有五条近期工作线已经逼近它：

1. [MemTX](https://arxiv.org/abs/2607.23929) 已把 persistent shared memory、不可逆工具动作门控、派生记录级联修复和工具副作用处理放入同一事务协议。
2. [From Faulty Memories to Corrected Actions](https://arxiv.org/abs/2608.10502) 已提出 post-failure memory recovery，联合修复 memory store、执行 trace 和最终答案。
3. [MemSecBench](https://arxiv.org/abs/2607.27080) 已用 Write--Execute--Forget 协议覆盖恶意记忆持久化、外部后果和选择性清理。
4. [SagaLLM](https://www.vldb.org/pvldb/vol18/p4874-chang.pdf) 已把 persistent memory、checkpoint、自动补偿和事务恢复用于多 Agent 的已提交工作流。
5. [HarnessRisk](https://arxiv.org/abs/2608.17597) 已统一覆盖持久状态、外部动作和 incident recovery，且在可执行 mock services 中观察状态变化。

因此，下面这些标题级主张已经不能使用：

- “首次研究记忆导致的真实动作后果”；
- “首次联合记忆修复与工具动作恢复”；
- “首次把 memory lifecycle、action 和 recovery 放在同一 benchmark”；
- “首次使用 provenance 或 dependency graph 做选择性回滚”；
- “首次把数据库事务或 Saga 补偿引入 Agent Memory”。

### 0.2 仍可能成立的更窄问题

最有防守力的剩余问题不是“能否修复”，而是：

> **当持久记忆与已经提交的外部世界状态发生不一致时，在没有 gold 故障标签、没有 oracle 指定修复对象的条件下，Agent 能否根据不完整的新证据判断应该修记忆、修世界、同时修二者，还是暂不修复并继续验证；随后以最小干预恢复二者一致性，并保证相关任务不复发、无关状态不受损？**

推荐英文表述：

> **When persistent memory disagrees with committed world state, can an agent identify the correct repair locus without oracle fault labels, minimally reconcile memory and world state, and prevent recurrence without collateral mutation?**

暂用题目：

> **ReconMemBench: Benchmarking Repair-Locus Identification and Bidirectional Memory--World Reconciliation**

中文名：

> **ReconMemBench：持久记忆与外部世界状态的修复位置判定及双向协调评测**

### 0.3 当前判断等级

- **原 MemReadyBench 大闭环**：红色，高度拥挤，不建议继续作为主贡献。
- **第一轮 MemRecoverBench**：橙红色，MemTX、From Faulty、MemSecBench、SagaLLM 已覆盖大部分组件。
- **第二轮 ReconMemBench**：橙色，暂未找到完整等价协议，但邻近工作密集，必须先做小规模可证伪实验。

这里的“暂未找到”不是数学意义上的不存在证明。它表示：在本轮检索范围内，尚未发现工作把 **repair-locus ambiguity、无 oracle 诊断、真实 post-action world state、memory/world 双状态修复以及未来非干扰性** 同时设为中心评测对象。

## 1. 为什么第一轮问题又被撞了

### 1.1 MemTX 已经覆盖“记忆提交到动作后果”的主干

[MemTX: Transactional Belief Commit for Stateful Agent Memory](https://arxiv.org/abs/2607.23929) 是本轮最危险的同期工作。它明确提出：memory write 不等于 belief commit，并实现：

- 带 evidence、permission、provenance、validity 的记忆记录；
- tentative、validated、committed、action-safe 等状态生命周期；
- snapshot-isolated transaction；
- 对不可逆工具动作的 action gate；
- belief 被撤销后，对 summary、profile、index、shared copy 和 tool action 的 typed cascading repair；
- 90 个主测试和 56 个 hardened cases，以及下游 harm 评测。

它直接占据了“持久记忆错误越过动作边界”和“级联修复派生对象”的论点。更重要的是，它不只讨论 future answer，而是把 refund、outbound email 等动作放入协议。

但 MemTX 也给出了清晰边界：

- repair 只能覆盖已经记录的 provenance；
- reversible tool action 可以标记为 compensated，不可逆作用被记为 leaked effect；
- compensation 主要是 decision-level obligation，而不是 environment-level replay；
- reversibility 是静态工具属性，动作执行后才变化的边界不在模型内；
- 强 action-safe gate 在主要 LLM 实验路径中没有被完整验证。

所以“环境级恢复”仍有空间，但不能再把“tool side-effect repair”笼统写成空白。

### 1.2 From Faulty Memories 已覆盖 post-failure selective rollback

[From Faulty Memories to Corrected Actions](https://arxiv.org/abs/2608.10502) 从 diagnosed faulty memories 出发，构建 memory-to-action dependency graph，并联合处理 claim、plan、tool action、observation、answer 和 derived memory。它还评价 recovery、recurrence、faulty removal、benign preservation、claim invalidation F1 和 replay cost。

它已经证明：

- 只删除根记忆不等于恢复系统状态；
- 全量 reset/replay 会损害无关记忆并浪费计算；
- 通过显式 provenance 可选择性定位下游影响并 replay。

其关键边界恰好成为新问题的入口：

- 输入直接包含 diagnosed faulty-memory set；
- diagnosis 本身不在任务范围内；
- 依赖 instrumented runtime 写入显式 dependency edges；
- rollback 修复的是 Agent 自己维护的 trace 与 memory state；
- 论文明确指出不可逆外部副作用不能被 rollback，必须依赖可重置环境或领域补偿动作。

因此，“无 oracle fault localization + 当前外部世界恢复”仍未被它闭合。

### 1.3 MemSecBench 已覆盖从记忆写入到外部后果和清理

[MemSecBench](https://arxiv.org/abs/2607.27080) 提供 310 个 Write--Execute--Forget packages，检查恶意语义是否写入、是否在后续会话造成可验证外部后果，以及是否能被选择性清理并保留 benign memory。

它与第一轮方案高度相似，但有一个决定性实验边界：

> Execute 与 Forget 从同一个 verified post-Write memory snapshot 的两个独立副本启动。

因此 Forget 并不是从 Execute 已经改变过的外部世界继续。它评价的是“能否修 memory backend”，而不是“动作已提交之后，能否同时恢复 world state 和 memory state”。

### 1.4 SagaLLM 已覆盖事务补偿与外部状态恢复

[SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning](https://doi.org/10.14778/3750601.3750611) 发表于 PVLDB 2025。它使用 Saga transaction pattern、persistent memory、checkpoint、validation agent 和 automated compensation，处理航班与酒店等已提交工作流中的部分失败和跨步骤不一致。

它说明“Agent + persistent context + committed operations + compensation”不是新的组合。与本项目的区别是：

- SagaLLM 的故障主要是当前 workflow 的执行失败、约束违反或环境扰动；
- 它没有把跨会话记忆状态设为受控因果变量；
- 它不要求判断“memory 与 world 到底哪一侧错了”；
- 它不评价 memory store 的选择性修复与跨会话复发。

### 1.5 HarnessRisk 已覆盖更宽的安全生命周期

[HarnessRisk](https://arxiv.org/abs/2608.17597) 以 128 个沙箱 case 覆盖 Harness Configuration、Capability Extension、Runtime Operation、State Persistence、Action Control 和 Incident Recovery。每个 case 都记录 transcript、tool calls、persistent state、mock-service state 和环境变化。

它使“统一覆盖 state persistence、action 和 recovery”也不能再作为新颖性主张。不过其主要任务是防止和处置 adversarial influence，指标是 Utility、Attack Success Rate、Persistence 和 Detection，并没有构造 memory/world 不一致下的 repair-locus 对照，也没有把联合恢复和未来复发作为核心指标。

## 2. 同期工作碰撞矩阵

符号：`Y` 表示核心覆盖，`P` 表示部分覆盖或依赖强假设，`N` 表示不覆盖。

| 工作 | 跨会话持久记忆 | 外部动作/世界状态 | 无 oracle 故障定位 | 修复位置未知 | 修 memory | 修 world | 未来复发/无关副作用 | 状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [AMA-Bench](https://arxiv.org/abs/2602.22769) | Y | P | N | N | N | N | N | ICML 2026（项目页披露） |
| [StateMemBench](https://arxiv.org/abs/2608.19652) | Y | P | N | N | N | N | P | arXiv 2026 |
| [ClawArena](https://arxiv.org/abs/2604.04202) | Y | Y | P | N | P | P | P | arXiv 2026 |
| [AgentMemoryBench](https://openreview.net/pdf?id=MSXbrNExax) | Y | P | P | N | Y | N | Y | ICLR 2026 Lifelong Agent Workshop |
| [MemoRepair](https://arxiv.org/abs/2605.07242) | Y | N | N | N | Y | N | P | arXiv 2026 |
| [From Faulty Memories](https://arxiv.org/abs/2608.10502) | Y | P | N | N | Y | P | Y | arXiv 2026 |
| [MemSecBench](https://arxiv.org/abs/2607.27080) | Y | Y | P | N | Y | N | P | arXiv 2026 |
| [MemTX](https://arxiv.org/abs/2607.23929) | Y | Y | P | N | Y | P | P | arXiv 2026，under review |
| [SagaLLM](https://doi.org/10.14778/3750601.3750611) | P | Y | P | N | N | Y | P | PVLDB 2025 |
| [HarnessRisk](https://arxiv.org/abs/2608.17597) | P | Y | P | N | P | P | N | arXiv 2026，under review |
| [AgentTrace](https://arxiv.org/abs/2603.14688) | N | P | Y | P | N | N | N | ICLR 2026 Agents in the Wild Workshop |
| [EAL-Bench](https://arxiv.org/abs/2609.01836) | Y | Y | P | N | P | N | N | arXiv 2026 |
| ReconMemBench 拟议协议 | Y | Y | Y | Y | Y | Y | Y | 待验证 |

这张表给出两个结论：

1. 单个组件几乎都已有直接工作，靠“多放几个模块”无法构成强 gap。
2. 仍未被明确设为实验变量的是 **repair locus**：当 memory 与 world 不一致时，现有协议通常预先知道 faulty root、攻击目标、失效事件或需要补偿的 transaction，而不是让 Agent 判断哪一侧应该被改动。

## 3. 其他会进一步压缩原方案的近期工作

### 3.1 StateMemBench：当前状态与已替代状态

[StateMemBench](https://arxiv.org/abs/2608.19652) 已系统研究多会话环境中的 state drift、supersession 和 dependency-aware state tracking。它包含 234 个多会话场景和 322 个 probes，说明“memory 是否仍反映当前世界”本身已经是独立 benchmark 方向。

它的输出仍主要是回答和状态选择，不要求执行错误动作后的双状态恢复。因此可作为 state diagnosis baseline，而不是本项目的直接替代。

### 3.2 ClawArena：演化信息环境中的动态信念修订

[ClawArena](https://arxiv.org/abs/2604.04202) 研究 persistent assistant 在多来源冲突、动态更新和隐式个性化条件下的长期行为，并使用 workspace 与 shell 检查。它已经压缩了“动态 memory 会不会改变 Agent 行为”的空间。

但其核心仍是 evolving-information grounding 和 belief revision，没有把 Agent 自己已经造成的外部状态偏移作为必须补偿的对象。

### 3.3 AMA-Bench：Agent trajectory 里的因果与状态更新

[AMA-Bench](https://arxiv.org/abs/2602.22769) 不再只使用对话记忆，而是从真实与合成 Agent trajectories 中评测 recall、causal inference、state updating 和 state abstraction，并提出 causality graph。其项目仓库披露已被 ICML 2026 接收。

因此不能再说“现有 agent-memory benchmark 都没有环境状态转移或因果结构”。真正的区别必须是：AMA-Bench 从历史轨迹回答问题，而 ReconMemBench 要在当前可变环境中选择并执行修复。

### 3.4 MemoRepair：级联影响范围和最小修复

[MemoRepair](https://arxiv.org/abs/2605.07242) 已研究根记忆失效后，如何撤销派生 artifacts、从保留支持中重建 successor，并做成本感知的最小 republication。因此“依赖图 + 最小级联修复”不是新创新。

可保留的问题是：在 root 未知、world 也可能出错的情况下，先确定故障位置，再决定修复哪一侧。

### 3.5 授权漂移也已经独立成线

[Agent Memory Is a Surface for Endogenous Authorization Laundering](https://arxiv.org/abs/2609.01836) 提出 EAL-Bench，研究持久记忆如何把错误授权写成后续动作依据。它再次说明 authority drift 只能作为一种 case family，不能作为整个 benchmark 的主创新。

### 3.6 相邻但不构成直接替代的恢复工作

- [Causal Episodic Memory for Feedback-Driven Agent Repair](https://arxiv.org/abs/2608.05906) 把已验证的 SQL 修复经验跨 query 写入双极性 memory，重点是“从历史修复经验学习”，不是修复 memory 自身及 world state。
- [Revisable by Design](https://arxiv.org/abs/2604.23283) 研究用户中途修改要求后如何撤销或补偿动作，故障来源不是 persistent memory。
- [ACRFence](https://arxiv.org/abs/2603.20625) 研究 checkpoint replay 如何避免重复不可逆副作用，可作为 runtime baseline。
- [Repair the Amplifier, Not the Symptom](https://arxiv.org/abs/2607.01767) 修复长规划图中的 world-model 放大节点，不以跨会话 memory/world 冲突为对象。

## 4. 新问题为什么不是“把几个任务合并”

### 4.1 核心科学变量是修复位置的不确定性

已有工作通常先规定：

- stale memory 是错的；
- poisoned record 是错的；
- diagnosed faulty-memory ID 已知；
- 某个 workflow step 失败，需要执行 compensation；
- 某个攻击目标已知，需要 rollback 或删除。

ReconMemBench 则固定表面上的 memory--world mismatch，并改变真正的 causal fault locus。Agent 不能把“总是信世界”“总是信 memory”或“二者都重置”当作通用策略。

### 4.2 四种 matched repair-locus 条件

对同一个任务模板构造四个可配对条件：

| 条件 | 真实故障位置 | 正确策略 | 错误策略造成的后果 |
|---|---|---|---|
| `MEMORY_FAULT` | memory 错，world 正确 | 修 memory，不改 world | 误补偿正确事务 |
| `WORLD_FAULT` | memory 正确，world 错 | 保留 memory，补偿 world | 删除正确偏好或继续错误状态 |
| `JOINT_FAULT` | memory 错且已诱发 world 错 | 同时修 memory 与 world | 只修一侧导致复发或不一致 |
| `APPARENT_CONFLICT` | 二者分别在不同时间、作用域或权限下有效 | 验证、询问或保持不变 | 过度修复和无关状态损坏 |

如果证据仍不足，可额外允许 `ESCALATE`，但它是动作而不是第五种 gold 故障类型。

### 4.3 必须满足可识别性

如果两个不同故障位置产生完全相同的可观察信息，任何 Agent 都无法可靠判断，benchmark 会退化为猜测。因此每个 case 必须满足：

1. gold fault label 不直接暴露；
2. 环境中存在足以区分故障位置的证据；
3. 证据需要通过 provenance、时间、authority、audit log 或额外 tool call 获取；
4. 无证据条件下的正确行为是 verify/ask/escalate，而不是强行修复；
5. validator 能证明正确 repair locus 在给定观测下可识别。

这一“最小可识别证据”要求，是新 benchmark 比单纯 lifecycle 聚合更像科学问题的关键。

## 5. 修订后的 Research Questions

### RQ1：Repair-Locus Identification

> 当持久记忆与外部世界状态冲突时，Agent 能否在没有 gold faulty-memory IDs 的条件下，判断错误位于 memory、world、二者，还是当前证据不足？

### RQ2：Minimal Bidirectional Reconciliation

> Agent 能否只修改因果上必要的 memory records 和 world objects，使二者重新满足任务约束，同时避免全量 reset、重复动作和过度补偿？

### RQ3：Longitudinal Closure and Non-Interference

> 修复是否能阻止同类错误在后续相关会话中复发，并保证无关记忆、无关用户和无关世界状态不受影响？

三个 RQ 与 memory 的关系是连续的：RQ1 判断持久记忆是否仍是可信状态；RQ2 决定记忆和世界之间如何双向协调；RQ3 验证 memory repair 是否真正改变了未来跨会话行为。

## 6. 建议指标

### 6.1 Repair-Locus Accuracy（RLA）

判断 `MEMORY / WORLD / JOINT / NO-REPAIR` 是否正确。对证据不足 case，另报 selective accuracy 和 escalation calibration，避免 blanket abstention 得高分。

### 6.2 Memory--World Closure Rate（MWCR）

修复结束后，同时满足：

- memory 中无仍可激活的致错记录及派生项；
- world state 满足任务、授权和一致性约束；
- required legitimate effects 仍然存在；
- forbidden、duplicate 或 leaked effects 不存在。

单独修好答案不计成功。

### 6.3 Minimal Intervention Regret（MIR）

将 Agent 实际修改集合与最小 gold repair set 比较，惩罚：

- 删除 benign memory；
- 改动正确 world objects；
- 重复执行已成功动作；
- 使用不必要的高成本补偿；
- 在不可逆动作上错误尝试回滚。

### 6.4 Recurrence Rate（RR）

在 Session D 的相关任务中，原故障是否再次影响检索、计划、工具参数或最终 world state。

### 6.5 Collateral Mutation Rate（CMR）

无关任务、无关用户、无关 memory records 和无关 world objects 被改变的比例。它是原“无关任务污染率”的更可执行版本。

### 6.6 Recovery Cost

报告 tool calls、verification calls、LLM tokens、wall-clock time、compensation cost 和 user escalation 次数，不把保守拒绝误判成优秀修复。

## 7. 最小可证伪实验

现在不建议直接建设数百题 benchmark。先用 24--32 个 matched cases 判断“repair-locus ambiguity”是否真实存在。

### 7.1 实验规模

- 2 个可执行领域：travel/calendar 与 purchase/refund；
- 6--8 个 base tasks；
- 每个 base task 构造四种 repair-locus 条件，共 24--32 cases；
- 每个 case 至少运行 3 个随机种子；
- 模型：Qwen2.5-7B、Llama-3-8B 级开源模型，加一个较强闭源模型作参考上界；
- 不训练，先做 zero-shot / structured prompting 验证。

### 7.2 四阶段会话

**Session A：形成持久记忆**

- 用户交互、工具反馈和环境事件写入 memory backend；
- 保存 raw history、canonical memory、provenance 和初始 world snapshot。

**Session B：形成 memory--world 不一致**

- 按 repair-locus 条件干预 memory、world 或二者；
- 部分 case 允许 Agent 的 memory-conditioned action 真正改变 mock service；
- 记录每个 world mutation 的 action ID、输入、时间和可逆性。

**Session C：给出新证据并要求继续任务**

- 不提供 gold fault ID；
- Agent 可查询 audit log、原始会话、外部权威源或用户；
- 输出 diagnosis、repair plan、memory operations 和 world compensation actions。

**Session D：验证长期闭合**

- related probe 检查是否复发；
- unrelated probe 检查是否误删记忆或误改环境；
- 重启 Agent 后再次评测，确保修复进入 persistent state。

### 7.3 最小基线

1. `No Repair`；
2. `Memory Wins`：总是按 memory 修 world；
3. `World Wins`：总是按 world 修 memory；
4. `Always Joint Reset`：二者全部重置；
5. `LLM Direct Repair`：只给当前观测；
6. `Trace-Augmented Repair`：提供非 gold 的 provenance/audit tools；
7. `Oracle Locus`：提供 gold repair locus，作为上界；
8. `Oracle Repair Set`：提供最小 gold repair set，作为更强上界。

MemTX、From Faulty、SagaLLM 的完整复现成本较高，先实现其核心决策规则作为 protocol-inspired baselines；当 pilot 显示明显的 oracle gap 后，再接官方代码或完整系统。

### 7.4 Go / No-Go 判据

满足以下条件再扩建：

- `Memory Wins` 与 `World Wins` 在不同 locus 上显著互相失败，证明问题不能由固定优先级解决；
- `LLM Direct Repair` 与 `Oracle Locus` 至少存在 15 个百分点 RLA 或 MWCR 差距；
- trace/audit evidence 能缩小差距，说明问题可学习、不是不可识别噪声；
- joint repair 相比 memory-only 在 `JOINT_FAULT` 上明显降低 recurrence；
- 无关任务上的 CMR 足以区分 selective repair 与 reset；
- case validator 能稳定复现 world state，不依赖主观 judge 才能判定核心结果。

若固定优先级已经接近 Oracle，或者不同模型都不能从现有证据判断 locus，则停止扩建：前者说明问题过于简单，后者说明协议缺少可识别信息。

## 8. 可防守与不可防守的论文表述

### 8.1 不可防守

- 首个研究 Agent Memory repair 的 benchmark；
- 首个把记忆错误连接到外部动作的工作；
- 首个评测 post-failure recovery；
- 首个联合 repair memory 和 action trace；
- 首个使用 transaction、provenance 或 cascade repair；
- 首个覆盖 lifecycle、state persistence 和 incident recovery。

### 8.2 当前较可防守

> Existing work typically fixes the repair target in advance: it supplies diagnosed faulty memories, defines an invalidated root, specifies an attacked state, or identifies a failed transaction. We instead study repair-locus ambiguity: when persistent memory and committed world state disagree, the agent must determine which side is invalid before applying a minimal, longitudinally verified repair.

中文：

> 现有工作通常预先固定修复对象，例如提供故障记忆 ID、指定失效根节点、给出攻击目标或标记失败事务；我们研究的是修复位置不确定性：当持久记忆与已提交世界状态不一致时，Agent 必须先判断哪一侧失效，再执行最小修复，并通过未来相关和无关任务验证长期闭合。

即便采用这段表述，也应写成“据我们检索所知”并明确列出 MemTX、From Faulty Memories、MemSecBench、SagaLLM 和 HarnessRisk，不能把邻近工作藏在大类引用中。

## 9. 最终建议

### 9.1 是否继续

可以继续，但应停止扩展原 MemReadyBench 的 formation、diagnosis、control、repair 全任务列表。下一步只验证一个问题：

> **同样表现为 memory--world mismatch 时，模型能否找对 repair locus？**

这是当前最小、最清楚、也最容易被实验否证的科学问题。

### 9.2 与后续方法的连接

如果 benchmark 阶段观察到稳定 oracle gap，第二阶段方法可以做：

- evidence acquisition policy：选择查 memory provenance、world audit log、用户还是权威 API；
- repair-locus planner：预测 memory-only、world-only、joint、verify 或 escalate；
- dependency-aware minimal repair：在 memory/world 联合因果图上选择最小修改集；
- compensation-aware executor：区分 reversible、compensable、irreversible actions；
- longitudinal verifier：在提交前预测 recurrence 与 collateral mutation。

但这些都应等 pilot 证明问题后再实现。当前贡献优先是 benchmark 的**修复位置不确定性与双状态闭合协议**，而不是再堆一个通用 memory controller。

## 10. 核心参考文献

1. Li et al. [MemTX: Transactional Belief Commit for Stateful Agent Memory](https://arxiv.org/abs/2607.23929). arXiv preprint, under review, 2026.
2. Yu et al. [From Faulty Memories to Corrected Actions: Dependency-Guided Rollback Repair for Memory-Augmented Agents](https://arxiv.org/abs/2608.10502). arXiv preprint, 2026.
3. Chen et al. [MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair](https://arxiv.org/abs/2607.27080). arXiv preprint, 2026.
4. Chang and Geng. [SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning](https://doi.org/10.14778/3750601.3750611). PVLDB 18(12), 2025.
5. Bai et al. [HarnessRisk: A Lifecycle-Oriented Benchmark for Agent Harness Safety](https://arxiv.org/abs/2608.17597). arXiv preprint, under review, 2026.
6. Zhao et al. [MemoRepair: Barrier-First Cascade Repair in Agentic Memory](https://arxiv.org/abs/2605.07242). arXiv preprint, 2026.
7. Zhao et al. [AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications](https://arxiv.org/abs/2602.22769). ICML 2026 acceptance reported by the official project repository.
8. Orogat and Mansour. [Can Agent Memory Systems Track Evolving State?](https://arxiv.org/abs/2608.19652). arXiv preprint, 2026.
9. [ClawArena: Benchmarking AI Agents in Evolving Information Environments](https://arxiv.org/abs/2604.04202). arXiv preprint, 2026.
10. [AgentMemoryBench: Benchmarking Continual Agent Memory for Online Learning, Transfer, and Forgetting](https://openreview.net/pdf?id=MSXbrNExax). Lifelong Agent Workshop at ICLR 2026.
11. Wang. [AgentTrace: Causal Graph Tracing for Root Cause Analysis in Deployed Multi-Agent Systems](https://arxiv.org/abs/2603.14688). Agents in the Wild Workshop at ICLR 2026.
12. Cerruti et al. [Agent Memory Is a Surface for Endogenous Authorization Laundering](https://arxiv.org/abs/2609.01836). arXiv preprint, 2026.
13. Vo et al. [Causal Episodic Memory for Feedback-Driven Agent Repair](https://arxiv.org/abs/2608.05906). arXiv preprint, 2026.
