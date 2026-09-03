---
title: "MetaMemBench：面向 Agentic Memory 的记忆监控与控制策略诊断基准"
type: research-proposal
status: merged-archive
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "agentic-memory", "benchmark", "metamemory", "memory-control"]
---

# MetaMemBench：面向 Agentic Memory 的记忆监控与控制策略诊断基准

> **状态说明（2026-09-03）**：本文中的 memory monitoring、admissible action、counterfactual state、oracle decomposition 和训练设计已并入 [MemReadyBench 统一方案](./2026-09-03-memreadybench-unified-research-proposal.md)。当前研究不再将本文作为独立版本或主方案。

## 0. 结论先行

### 0.1 是否与 StratMem-Bench 太相似

**如果题目仍然叫“动态战略记忆使用 benchmark”，确实比较相似，不建议这样立题。**

原因不是“动态”没有价值，而是 [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/) 已经把核心问题定义为：面对 query-conditioned 的 `must / nice / irrelevant` 候选记忆，模型应当使用必要记忆、选择性使用支持性记忆，并抑制无关记忆。它还在 Limitations 中明确把 multi-turn strategic memory use 列为后续扩展。因此，只把单轮改成多轮、让同一条记忆的角色随 query 变化，很容易被理解为 StratMem-Bench 的自然扩展，而不是新的问题定义。

本方案把研究对象从 **memory-content selection** 上移一层，改为 **memory-state monitoring and control**：

> **在持久记忆和部分可观测任务中，Agent 能否判断当前可用记忆是否足以、可靠地支撑下一步行动，并在继续检索、向用户澄清、直接执行或拒绝行动之间作出风险与成本校准的控制决策？**

工作名暂定：

> **MetaMemBench: Evaluating Monitoring and Control of Agent Memory under Uncertainty**

这里的 `meta-memory` 不是参数记忆，也不是“再建一层 memory”；它表示 Agent 对自身外部记忆状态进行监控，并据此控制后续行为。

### 0.2 是否属于 Agentic Memory

**属于，而且落点比“给定候选池后生成回答”更接近 agentic memory。**

[Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) 将 Agent Memory 定义为嵌入 Agent–Environment 循环、能够跨任务持续存在并随交互演化的认知状态；一次完整循环包含环境观察、可选记忆检索、行动、反馈和可选记忆更新。该综述把“检索时机与意图”“自动化记忆管理”“RL 驱动的记忆控制”列为 Agent Memory 的核心动态与前沿。

MetaMemBench 在这张图中的位置是：

- **主归属**：`Agent Memory -> Dynamics -> Retrieval Timing and Intent / Post-Retrieval Processing`。
- **方法形态**：`Agentic Memory / Automated Memory Management`，因为 Agent 自己选择 memory action。
- **交叉区域**：与 Agentic RAG 共享迭代检索，与 Context Engineering 共享工具和预算管理。
- **边界条件**：若数据源只是不会随交互演化的外部文档库，工作会更像 Agentic RAG；只有当记忆来自 Agent 的历史交互、行动、反馈或跨 session 经验，并持续影响未来决策时，核心才是 Agent Memory。

因此，论文不应声称“动态检索就是 Agentic Memory”，而应强调 **persistent, interaction-derived memory + agent-controlled access + downstream action consequence** 三个条件。

## 1. 一句话论点与贡献边界

### 1.1 一句话论点

> Persistent memory becomes genuinely agentic not merely when it is retrieved, but when an agent can monitor whether its current memory state is sufficient for action and choose a calibrated control action whose downstream consequence is verifiable.

中文：

> 持久记忆真正进入 Agentic 阶段，不只是因为它能被检索，而是因为 Agent 能判断当前记忆是否足以支撑行动，并选择一个可通过下游结果验证的控制动作。

### 1.2 不应声称的内容

本工作不声称：

- 第一个动态记忆 benchmark：AMemGym、MemoryArena、StreamMemBench 已覆盖动态或流式交互。
- 第一个战略记忆 benchmark：StratMem-Bench 已经提出战略使用评测。
- 第一个 memory-to-action benchmark：Mem2ActBench 与 MemoryArena 已覆盖记忆驱动行动。
- 第一个 memory operation benchmark：MemOps 已提供 lifecycle operation trace。
- 第一个记忆控制方法：AgeMem、MemCon、MemSearcher、Memory-R1 等已经学习或调用 memory action。
- 第一个澄清或拒答 benchmark：TANGLE 已评估不可约冲突下的澄清、校准和保留冲突。

### 1.3 可以争取的贡献边界

本工作争取定义并验证的是：

1. **Memory sufficiency monitoring**：当前 working memory 是否已经构成支持行动的最小充分证据，而不是其中是否存在相关词条。
2. **Memory control decision**：在 `SEARCH / ASK / EXECUTE / ABSTAIN` 中选择下一步，而不是固定 top-k 后直接回答。
3. **Counterfactual decision-point evaluation**：在任务文本近乎不变、只插入或移除一条 decisive memory 时，正确控制动作必须发生可预期改变。
4. **Failure decomposition**：区分 monitor 错、retriever 错、controller 错、reader/executor 错，避免只用最终 task success 把问题混在一起。
5. **Risk–cost calibration**：同时测 premature action、无效检索、过度澄清和最终成功，而不是把“检索越多”默认当成更好。

## 2. 问题来源：从已有工作中的未解决难点推导

下表不是泛泛列 related work，而是给每一个问题定义提供来源。

| 证据来源 | 已解决的问题或主要发现 | 仍然留下的可验证问题 | 本方案承接方式 |
|---|---|---|---|
| [StratMem-Bench, ACL 2026](https://aclanthology.org/2026.acl-long.1491/) | 给定约 9 条短候选记忆，评估 `must/nice/irr` 的选择与整合；`must+nice` 的 SMC 均低于 50%，主要瓶颈是选择；作者明确限制为单次 response | 系统并不需要判断“当前记忆是否足以行动”，也不能主动搜索、澄清或拒绝；multi-turn 已被作者列为直接扩展 | 不以多轮为新意；把标签从“内容角色”扩展到“记忆状态 + 下一控制动作” |
| [Mem2ActBench, ACL 2026](https://aclanthology.org/2026.acl-long.370/) | 评估从长期记忆恢复工具参数；最佳被动检索与 oracle retrieval 相差超过 23 F1 | 评测是 offline tool-call generation，不含执行反馈；交互澄清仅作诊断上界，却把 Parameter F1 从 29.24 提升到 48.68 | 将“是否应该继续检索或澄清”变成正式任务，并通过工具执行验证 |
| [MemoryArena, 2026](https://arxiv.org/abs/2602.16313) | 把记忆获取、环境行动和跨 session 复用放进 Memory-Agent-Environment loop | 主要报告整体 task success/progress；难以判断失败源于记忆状态估计、控制动作、检索还是执行 | 在每个关键 decision point 提供 gold state、admissible action 与 counterfactual pair |
| [AMemGym, ICLR 2026](https://arxiv.org/abs/2603.01966) | 用结构化用户状态支持 on-policy 长程对话评测与优化 | 动态环境本身已经不是空白；但 memory-control action 的正确性仍未成为独立可校准目标 | 借鉴结构化 simulator，但输出 gold memory-control decision，而非只问最终个性化质量 |
| [MemCon, 2026](https://arxiv.org/abs/2607.13591) | 将 `Retrieve/PlanInject/Re-Retrieve/Consolidate/Forget/NoOp` 建模为 Memory MDP，并用终局二值反馈学习轻量控制器 | 证明“控制有用”，但训练和比较仍主要依赖终局成功与 token；没有跨系统统一的 gold decision points 来诊断控制策略为何对或错 | 把 MemCon 当强 baseline；专门评估其 monitor、动作选择、成本和反事实稳定性 |
| [AgeMem, ACL 2026](https://aclanthology.org/2026.acl-long.981/) | 将 LTM/STM 操作暴露为工具动作，并通过 progressive RL 与 step-wise GRPO 学习统一管理 | operation-as-action 已经成立，不能再作为单独创新；现有任务也很难比较某一步 memory action 是否必要 | benchmark 先提供独立于特定 RL 算法的动作监督和可验证 reward |
| [MemOps, 2026](https://arxiv.org/abs/2607.12893) | 为 remember/forget/update/reflect 构造 trigger、target、scope、state transition 和 evidence trace | 重点是长对话中的 lifecycle operation 执行，不是查询时对“证据是否充分、应该检索还是澄清”的控制 | v1 不做全生命周期，集中在 read/use-time control，避免重复 |
| [MemTrace, 2026](https://arxiv.org/abs/2605.28732) | 把真实 memory pipeline 转成 execution graph，对失败做 post-hoc root-cause attribution | 说明 final answer 会掩盖 operation failure；但它从已经失败的系统轨迹回溯，不提供受控干预下的 prospective decision gold | 通过配对干预预先定义“动作应否改变”，形成可执行的因果诊断 |
| [TANGLE, 2026](https://arxiv.org/abs/2608.13921) | 在不可约个人记忆冲突中评估冲突识别、置信度、澄清和 memory faithfulness | 冲突只是 memory insufficiency 的一种；不覆盖“缺失但可检索”“缺失且只能问用户”“充分但检索有害”等状态 | 把 TANGLE 作为 conflict slice；主问题是统一的 sufficiency-aware control |
| [StateMemBench, 2026](https://arxiv.org/abs/2608.19652) | 区分 current 与 superseded state，证明旧状态会被错误复用 | stale state 已经是独立方向，不能把“动态更新”整体据为新意 | stale/resolvable 只作为一个状态类别，并要求系统选择搜索更新或拒绝执行 |
| [CIMemories, ICLR 2026](https://arxiv.org/abs/2511.14937) | 评估不同任务语境中哪些个人属性可以或不可以披露，揭示 utility–privacy 冲突 | 说明“相关”不等于“应该使用”；但核心是信息流隐私，而非一般 memory sufficiency | 在 future trustworthy split 中加入 `forbidden` 证据，主 benchmark 不抢 privacy 故事 |

由这些证据可以把 research gap 写成：

> Existing benchmarks evaluate factual recall, strategic use of a provided memory pool, evolving state, lifecycle operations, irreducible conflict, or end-to-end task success in memory–agent–environment loops. Meanwhile, recent methods such as AgeMem and MemCon already learn when and how to invoke memory operations. However, current evaluation still lacks a controlled and diagnostic protocol for testing whether an agent can assess the sufficiency of its current memory state and choose the appropriate next control action before committing to an answer or executable action. Final task success cannot distinguish a correct memory policy from lucky execution, while fixed candidate-pool evaluation cannot measure search, clarification, or calibrated abstention.

这个 gap 的关键词不是 `dynamic`，而是：

> **diagnostic + counterfactual + sufficiency-aware + control-before-commitment**

## 3. 与最邻近工作的清晰区分

| 工作 | 记忆输入 | Agent 可选动作 | 主要 gold | 主要输出 | 与本工作的关键差异 |
|---|---|---|---|---|---|
| StratMem-Bench | 已给定的小候选池 | 生成一条 response | must/nice/irr | SMC/MIQ/PES/CIR | 评“用哪些”，不评“够不够、下一步做什么” |
| Mem2ActBench | 长历史经固定 memory framework 检索 | 生成 tool call | 参数及工具 | Tool/Parameter Accuracy | 不把搜索/澄清/拒绝作为正式在线动作 |
| MemoryArena | 跨 session 轨迹与 memory backend | 环境 action | 最终/过程任务状态 | Success/Progress | 有闭环，但没有 memory-policy decision gold |
| AMemGym | 模拟用户与演化状态 | 对话 response | 结构化用户状态 | 个性化与记忆表现 | 有 on-policy 环境，但控制动作不是核心评测单元 |
| MemOps | 长对话证据 | remember/update/forget/reflect 识别 | operation trace | operation probes | 评 lifecycle state transition，不评 query-time evidence sufficiency |
| TANGLE | 冲突记忆 | 回答/澄清/拒绝 | conflict type/action | 五维冲突指标 | 专注不可约冲突，不覆盖完整的 availability/sufficiency 状态空间 |
| MemCon | 任意 memory backend | 多种 memory operation | 无逐步 benchmark gold | task success/token | 是待评方法，不是独立 diagnostic benchmark |
| **MetaMemBench** | 持久 store + 当前 working packet | SEARCH/ASK/EXECUTE/ABSTAIN | state、evidence closure、admissible action、environment result | monitor/control/task/cost | 评“Agent 是否知道记忆够不够，并在承诺行动前正确控制” |

最重要的写作句式：

> StratMem-Bench asks **which memories should appear in a response**; MetaMemBench asks **whether the currently available memory can justify acting at all, and what the agent should do next if it cannot**.

## 4. 正式问题定义

### 4.1 环境与记忆

在时间步 $t$，Agent 面对：

- 当前任务目标 $g_t$；
- 环境观察 $o_t$；
- 跨 session 持久记忆库 $M_t$；
- 当前已经放入工作上下文的 memory packet $C_t \subseteq M_t$；
- 剩余预算 $b_t$，包括检索次数、澄清次数、token 和环境步骤。

任务的正确执行依赖一组或多组最小充分证据闭包：

\[
\mathcal{E}^{*}(g_t)=\{E_1^*,E_2^*,\ldots\},
\]

其中每个 $E_i^*$ 都足以支持合法的最终回答或行动。允许多组闭包，是为了避免把只有一种措辞或检索路径错误地当成唯一 gold。

### 4.2 记忆充分性不是相关性

定义 $C_t$ 对目标 $g_t$ 的状态 $z_t$：

1. `NO_MEMORY_NEEDED`：当前任务无需历史记忆即可安全执行。
2. `SUFFICIENT`：$C_t$ 已包含至少一个完整、当前有效且无未决冲突的证据闭包。
3. `RETRIEVABLE_MISSING`：当前 packet 不充分，但缺失证据存在于持久 store 中，可通过更好的 memory search 获取。
4. `USER_ONLY_MISSING`：缺失约束不在 memory store，只能向用户澄清。
5. `RESOLVABLE_STALE_OR_CONFLICT`：当前 packet 含旧值或冲突，但 store 中存在时间、来源或后续反馈可解决。
6. `IRREDUCIBLE`：现有 store 无法唯一支持行动，合理选择是澄清或拒绝承诺。

相关记忆可能仍然不充分；相似度高的旧偏好可能还是有害的。这个定义直接回应 Mem2ActBench 的 sparse critical evidence、StateMemBench 的 supersession、TANGLE 的 underdetermination，以及 StratMem-Bench 的 irrelevant suppression。

### 4.3 控制动作

在每个 decision point，Agent 只能执行下列一种外部可见动作：

- `SEARCH_MEMORY(query, k)`：重新构造 query，从持久 memory store 获取新证据。
- `ASK_USER(question)`：请求只有用户能补足的约束；模拟用户按隐藏 world state 回答。
- `EXECUTE(action_or_answer, evidence_ids)`：提交回答或调用工具，并声明所依赖的证据。
- `ABSTAIN(reason, missing_requirements)`：在证据不可补足或风险过高时拒绝承诺。

第一版不把 `WRITE/UPDATE/DELETE/FORGET` 放进主 action space。它们由 MemOps、AgeMem、Memory-R1 等工作覆盖较多，过早加入会让 benchmark 失控。v1 只评 **read/use-time control**；后续可以新增 lifecycle track。

### 4.4 最优策略与允许动作集

每个 decision point 不标单一动作字符串，而标：

- 当前 `memory_state`；
- 缺失字段或未解决条件；
- 一个 `admissible_action_set`；
- 每个动作的预期信息增益、成本和风险；
- 最终可执行状态与 gold environment outcome。

动作 gold 只能依据 Agent 当时可见的信息判定，不能要求 Agent 猜测隐藏的 store 内容。如果可见状态尚不足以区分“缺失但可检索”和“只能询问用户”，`SEARCH_MEMORY` 与 `ASK_USER` 都可以进入允许集合，再以调用成本和后续观察计算 regret；在搜索已明确返回无结果后继续重复搜索，才构成确定的控制失败。

例如，缺失航班日期且 store 中不存在日期时，`ASK_USER` 是低 regret 动作；首次搜索可以被允许但产生额外 cost；直接订票属于 `premature execution`。这种设计承认多条合理路径，同时仍能以规则计算 policy regret。

## 5. Benchmark 总体结构

### 5.1 三个递进 Track

#### Track A：Oracle Packet Monitoring

给定包含全部可访问任务相关证据和受控 distractor 的 oracle memory packet，不开放 search，要求模型：

1. 判断当前 packet 是 `NO_MEMORY_NEEDED / SUFFICIENT / INSUFFICIENT / CONFLICTED`；
2. 指出当前证据闭包和缺失条件；
3. 选择 `EXECUTE / ASK_USER / ABSTAIN`。

目的：隔离 monitor 和 reader 能力，不让检索器掩盖问题。`RETRIEVABLE_MISSING` 与 `USER_ONLY_MISSING` 只在开放 memory API 的 Track B 中根据交互轨迹进一步区分，因为单看 packet 无法公平判断缺失证据的外部可用性。

#### Track B：Active Memory Control

只给初始任务和 memory API，不直接给完整候选池。Agent 可多轮 `SEARCH_MEMORY`、改写 query、停止搜索、澄清或执行。

目的：评估 retrieval timing、intent、query construction、stop decision 和 budget allocation。MemCon、Self-RAG-style router、Memory-R1 或 MemSearcher 可在此比较。

Track B/C 中的 hidden `memory_state` 用于离线诊断，不强制 Agent 在每一步显式输出标签；主评测只要求标准化工具动作。需要分析校准时，再开启 state/confidence 输出协议。

#### Track C：Closed-Loop Memory-to-Action

最终动作进入确定性工具或小型环境，产生可验证状态变化与反馈。错误参数不能只靠语言 judge 判分。

目的：确认 monitor/control 提升是否真正转化为行动成功，而不是只改善自我解释。

### 5.2 两个核心任务域

第一版不追求十几个 domain，优先建立两个互补、可规则评分的域：

1. **Personalized Tool Execution**：日历、出行、购物、提醒、文件操作等；当前请求故意省略一部分历史偏好或状态，gold 是结构化 tool call 和环境终态。可借鉴 Mem2ActBench 的 reverse-generation 思路与 BFCL/ToolACE 的 schema，但必须重新构造 memory-control variants。
2. **Progressive Search and Planning**：Agent 跨 session 收集约束和结果，后续任务依赖早期搜索/反馈；使用本地文档库或确定性 mini-web，gold 是 evidence closure、规划约束和最终状态。可借鉴 MemoryArena 的 progressive search，但把 memory decision point 单独标注。

对话型 `nice memory` 只保留为 transfer/challenge split，不作为主故事。这样既能对 StratMem 做承接实验，又不会把论文重新拉回虚拟角色的社交丰富度。

## 6. 数据构造方案

### 6.1 先建可执行世界，再生成自然语言

使用 **symbolic world first, language rendering second**：

1. 构造结构化 world state：用户偏好、工具参数、事件、时间、来源、权限、任务约束。
2. 生成跨 3–8 个 session 的历史事件，并形成持久 memory store。
3. 为当前任务生成 requirement graph，明确哪些字段决定工具可执行性。
4. 从同一个 base task 派生不同 memory-state variants。
5. 再用模板与 LLM 将事件渲染成自然对话、工具日志和 memory entry。
6. 运行 deterministic validator，检查 gold action、证据闭包和环境结果。
7. 人工审核自然度、歧义性和 action-set 合理性，而不是让人工从零写 gold。

### 6.2 核心反事实配对

同一个 base task 至少生成六种 variant：

| Variant | 只改变什么 | 预期控制行为 |
|---|---|---|
| Complete | decisive evidence 已在 packet 中 | 直接执行，不再搜索 |
| Hidden-in-store | 从 packet 移除 decisive item，但保留在 store | SEARCH 后执行 |
| User-only missing | 从整个 store 移除，只存在于 user simulator | ASK_USER 后执行 |
| Stale | packet 中保留旧值，store 中含 superseding event | SEARCH/resolve 后执行 |
| Irreducible | 两条同权威冲突证据，无消歧信息 | ASK_USER 或 ABSTAIN |
| Distractor/no-memory | 加入高相似 hard negatives，或当前任务根本不依赖历史 | 忽略记忆并执行 |

这种配对比随机加入无关文本更关键：任务 wording、工具和大部分 history 保持不变，只有 decisive memory availability 变化，正确 action 也必须变化。它能直接检测“模型是否真的在监控 memory state”。

### 6.3 Hard Negatives

- 主题与实体都相同，但参数属于旧 session。
- 同一偏好在不同任务 scope 下适用性不同。
- 历史默认值与当前一次性指令冲突。
- 相关但不足以唯一执行的 partial evidence。
- 从成功经验抽取的策略与当前环境版本不兼容。
- 多条 supportive memory 会增强回答，但不是执行必要条件。
- 检索结果包含完整答案附近的高相似错误值。

### 6.4 数据规模

#### Pilot

- 60 个 base tasks。
- 每个 6 个 counterfactual variants，共约 360 个 episodes。
- 每个 episode 2–5 个 decision points，约 900–1,500 个控制决策。
- 20–50 条 memory entries，2 个任务域。

#### MVP Paper Version

- 300–500 个 base tasks。
- 1,800–3,000 个 episodes。
- 5,000–10,000 个 decision points。
- memory size 分为 20/100/500 三档；大规模档通过可控 distractor expansion 生成。
- 至少 10% human-authored 或 human-rewritten challenge split。

数据切分必须以 `base_task_id` 为单位，所有 variants 进入同一 split，避免模型看到同一任务的另一版本。

### 6.5 建议 Schema

```json
{
  "episode_id": "...",
  "base_task_id": "...",
  "domain": "tool_execution",
  "history_events": [],
  "memory_store": [],
  "initial_packet": [],
  "goal": {},
  "decision_points": [
    {
      "state_label": "USER_ONLY_MISSING",
      "required_evidence_sets": [["m12", "u3"]],
      "missing_requirements": ["departure_date"],
      "admissible_actions": ["ASK_USER"],
      "suboptimal_actions": {"SEARCH_MEMORY": 0.2},
      "forbidden_actions": ["EXECUTE"]
    }
  ],
  "gold_final_action": {},
  "gold_environment_state": {},
  "budgets": {"search_calls": 3, "clarifications": 1}
}
```

## 7. 指标体系

### 7.1 Monitoring

- `Memory-State Macro-F1`：六类状态分类。
- `Sufficiency AUROC/AUPRC`：将 `SUFFICIENT/NO_MEMORY_NEEDED` 与其余状态区分。
- `Brier Score / ECE`：模型对“现在可以安全执行”的概率是否校准。
- `Missing-Requirement F1`：缺了什么，而不只是说“不够”。
- `Evidence Closure P/R/F1`：提交的 evidence IDs 是否构成最小充分闭包。

### 7.2 Control

- `Admissible Action Accuracy`：动作是否在允许集合内。
- `Policy Regret`：相对 oracle policy 的任务风险与成本差。
- `Premature Execution Rate`：证据不足时直接执行。
- `Unnecessary Search Rate`：已经充分或无需记忆时继续搜索。
- `Unnecessary Clarification Rate`：memory store 已可解决时仍打扰用户。
- `Targeted Clarification Score`：问题是否准确询问缺失 slot，而非泛化追问。
- `Search-to-Closure Steps`：多少次 memory action 后取得充分证据。

### 7.3 Outcome 与成本

- `Task Success / Exact Tool State`。
- `Unsupported Success Rate`：结果碰巧正确，但证据或控制轨迹不合法。
- `Token / Retrieval / LLM-call Cost`。
- `Success–Cost Pareto Frontier`。
- `Risk–Coverage Curve`：允许 abstain 后，在不同 coverage 下的错误风险。

### 7.4 反事实指标

- `Action Flip Consistency`：插入/移除 decisive memory 后，动作是否按 gold 改变。
- `Irrelevant Invariance`：加入无关或 supportive-only memory 后，不应错误改变必要控制动作。
- `Stale-to-Current Sensitivity`：加入 superseding evidence 后是否停止使用旧值。
- `Surface Robustness`：同一 world graph 的多种自然语言渲染是否得到一致策略。

主表不建议只给一个总分。至少分开报告 `Monitor / Control / Outcome / Cost` 四组指标；综合 utility 只能作为次要排序。

## 8. Baseline 与公平比较

### 8.1 非学习 Baseline

- `NoMemory`：不访问历史。
- `FullHistory`：将允许范围内的完整 history 放入上下文。
- `Retrieve-Once@k`：固定 query、固定 top-k，一次检索后直接执行。
- `Always-Search`、`Always-Ask`、`Always-Execute`：暴露 action-class imbalance。
- `Confidence Threshold`：模型低置信时 search/ask 的简单 router。
- BM25、dense、hybrid retrieval。

### 8.2 Memory System Baseline

- Mem0 或 LangMem：生产型 ADD/UPDATE/RETRIEVE memory。
- A-MEM：linked note memory。
- StratMem-style direct reader：把 top-k packet 直接交给模型，要求隐式选择。
- StateMem-style wrapper：处理 supersession 的强对照。

### 8.3 Agentic Control Baseline

- Self-RAG / Adaptive Retrieval 风格的 `retrieve-or-answer`。
- MemSearcher 或 Memory-R1：具备搜索/管理动作的学习型策略。
- AgeMem：完整 memory operation policy；若 checkpoint 或复现实在不可得，应明确标为 paper-reported 或部分复现。
- **MemCon**：最关键的近期 baseline，因为它明确学习 memory control action。

### 8.4 Oracle Decomposition

- `OraclePacket + NativeController`：测控制器是否会用已经足够的证据。
- `NativeRetriever + OracleMonitor`：测检索瓶颈。
- `OracleRetriever + NativeMonitor`：测充分性判断与停止。
- `OracleController + NativeExecutor`：测最终 reader/executor。
- `OracleAll`：检查数据和 harness 的可解性上界。

所有 baseline 固定 backbone、tool schema、最大 token、最大搜索轮数和可见 memory source。否则更复杂系统可能只靠更多 context 或更多 LLM calls 获胜。

## 9. 核心实验

### E0：Benchmark Validity

- `NoMemory < NativeMemory < OracleAll` 是否形成合理能力梯度。
- 删除 decisive evidence 是否显著降低可执行性。
- 加入 irrelevant evidence 是否不改变 oracle action。
- 人工对 state label、missing requirement 和 admissible action 的一致率。

### E1：Main Benchmark

比较 open/closed LLM、long-context、RAG、memory frameworks 和 agentic controllers，在四组指标上的差异。目标不是只做 leaderboard，而是展示“最终分相同的系统可能有完全不同的控制失败”。

### E2：Failure Decomposition

通过四种 oracle intervention 分解：

- monitor failure；
- retrieval failure；
- controller failure；
- integration/execution failure。

这一步承接 StratMem 的 selection bottleneck、Mem2Act 的 retrieval gap 和 MemTrace 的 attribution 动机。

### E3：Counterfactual Policy Test

对每个 base task 比较六种 variants。关键观察不是平均 accuracy，而是相同 Agent 的 action 是否随 memory sufficiency 发生正确变化。

### E4：Calibration and Selective Action

让模型输出执行置信度，绘制 risk–coverage curve；比较 prompt calibration、self-consistency、temperature scaling 和专门 monitor 的效果。

### E5：Budget and Scaling

控制 memory size、top-k、最大 search rounds、token budget 与模型尺寸。需要回答：

- 大模型是否只是更会在错误 evidence 上猜对？
- 增加检索轮数何时从收益变成干扰？
- control policy 的收益能否超过额外调用成本？

### E6：Cross-Domain Generalization

在 tool domain 训练/调阈值，在 progressive search domain 测试，反之亦然。若控制策略只能记住任务模板，就不能支持“通用 agentic memory”论点。

## 10. 预期研究问题与可证伪假设

这些是实验前假设，不是结果：

- **H1**：现有系统的最终正确率会高估 memory control 能力，因为一部分结果来自猜测、full-context 泄露或不合法证据。
- **H2**：强模型在 `SUFFICIENT` 上能执行，但在 `USER_ONLY_MISSING` 与 `IRREDUCIBLE` 上仍会过早承诺。
- **H3**：固定 retrieve-once 在 `Hidden-in-store` 有帮助，却在 `NO_MEMORY_NEEDED` 与 distractor-heavy 设置增加成本或错误。
- **H4**：MemCon 类控制方法会改善平均 success–cost，但其 terminal binary feedback 未必带来良好的 sufficiency calibration。
- **H5**：显式训练 monitor 比只扩展 retriever 更能降低 premature execution；二者结合效果最佳。

若 H1–H4 均不成立，且简单 confidence threshold 已接近 oracle，则该问题不值得扩成完整 benchmark，应及时停止或转向更困难的真实任务。

## 11. 预期论文贡献

1. 提出 `memory monitoring and control before commitment` 的问题定义，将 strategic selection 与 end-to-end action 之间缺失的决策层显式化。
2. 构建具有 gold memory state、evidence closure、admissible action 和可执行结果的 counterfactual benchmark。
3. 提出 monitor/control/outcome/cost 四层评测协议与 oracle decomposition，诊断不同 memory system 的真实瓶颈。
4. 系统评估现有 long-context、RAG、memory backend 与 agentic controller，并给出可复现实验 harness。

“同一条 memory 随 query 角色变化”可以保留为数据属性，但不能再作为主创新；StratMem 已经明确采用 instance-specific role。

## 12. 第二阶段方法：MetaMem Controller

Benchmark 先做，方法只针对第一阶段暴露的主要失败。

### 12.1 模块

1. `State Monitor`：输出 $p(z_t|g_t,o_t,C_t)$、缺失 slot 和冲突来源。
2. `Evidence Ranker`：对候选 memory 的边际决策效用排序，而非只按语义相似度。
3. `Setwise Sufficiency Verifier`：判断选中集合是否已形成完整 evidence closure。
4. `Control Policy`：根据状态、风险和预算选择 SEARCH/ASK/EXECUTE/ABSTAIN。
5. `Execution Gate`：只有 verifier 通过或 policy 合法接受风险时才允许最终 action。

### 12.2 与 pairwise/listwise 的结合

- `Pointwise`：预测单条 memory 的相关性、时效性、authority 和 slot coverage。
- `Pairwise`：在 hard negative 与 decisive evidence 之间学习相对效用，特别适合下一条 memory/action 选择。
- `Listwise/Setwise`：排序并选择能够闭合全部需求的最小证据集合；它解决“每条都相关，但组合仍不充分”的问题。
- 最终 task reward 仍使用 exact tool success、evidence validity 和环境状态，不用 ranking score 替代结果奖励。

### 12.3 训练路线

1. Prompt/rule baseline，先证明 benchmark 有效。
2. 用 gold state/action/evidence 做 SFT；0.6B 只做 pipeline smoke test。
3. 用 counterfactual pairs 做 pairwise ranker，用完整 evidence closure 做 listwise/setwise selector。
4. 在 Qwen2.5-7B 与 Llama-3-8B 量级验证泛化。
5. 只有当 SFT 后仍存在明显的长程停止和预算分配问题，再尝试 GRPO/GSPO。

可验证 RL reward 可写为：

\[
R=R_{task}+\alpha R_{admissible}+\beta R_{closure}
-\lambda C_{search}-\mu C_{clarify}
-\eta P_{premature}-\xi P_{unsupported}.
\]

第一版不需要单独训练 GRM。结构化 gold 与环境执行已经能提供 RLVR 风格信号；只有开放式澄清质量或自然语言交互质量占比很高时，再训练辅助 judge/GRM。

## 13. 资源与可行性

### 13.1 为什么适合 4×4090

- benchmark 的核心资产是生成器、simulator、evaluator 和 baseline harness，不依赖从头训练大模型。
- deterministic environment 可在 CPU 执行，GPU 主要用于本地 0.6B/7B/8B inference 与轻量 SFT/LoRA。
- 反事实 variants 由同一 symbolic world 自动生成，标注成本低于从真实长对话逐条人工判断。
- closed model 只用于少量 frontier baseline，不需要成为数据生成和评分的唯一依赖。

### 13.2 最小闭环

1. 先做 20 个 base tasks × 6 variants。
2. 只实现 Track A 与一个确定性 calendar/travel tool。
3. 跑 `AlwaysExecute / RetrieveOnce / FullHistory / Oracle` 四个 baseline。
4. 检查 action flip、premature execution 与 unnecessary search 是否能区分系统。
5. 再加入 Track B 的 memory API 和 Track C 的完整工具集。

这个闭环不需要训练，1–2 周即可判断问题是否成立。

## 14. 主要风险与应对

| 风险 | 审稿人可能的质疑 | 应对 |
|---|---|---|
| 与 StratMem 相似 | “只是 multi-turn StratMem” | 主标签和 action space 改为 sufficiency/control；以工具执行和反事实动作翻转为核心，不以 nice memory enrichment 为主 |
| 与 MemoryArena 相似 | “已有 memory-agent-environment loop” | 强调 decision-point gold、oracle decomposition 和 control calibration；MemoryArena 是下游 gym/来源，不是要取代的对象 |
| 与 MemOps 相似 | “已有 operation trace” | v1 只评 read/use-time policy；MemOps 评 lifecycle state transition |
| 与 MemCon/AgeMem 相似 | “控制策略已有” | 把它们当被评方法；贡献是统一 diagnostic protocol，而非发明 memory action |
| 合成数据过强 | 模型学习模板捷径 | paired split、surface paraphrase、human challenge split、held-out tool schema/domain |
| 动作 gold 有主观性 | SEARCH 与 ASK 都可能合理 | admissible action set + cost/regret，不强制唯一动作 |
| LLM judge 不稳定 | 结果不可复现 | 主指标使用结构化 state、evidence ID、tool execution；LLM judge 仅评自然语言澄清质量 |
| 规模太大 | 多域环境工程难以完成 | 第一版只做两个可执行域、四个主动作和 read-time control |

## 15. Go / No-Go Gate

在扩大数据前，pilot 必须满足：

- `OracleAll` 在结构化主任务上接近可解上界。
- `NoMemory` 与 `OraclePacket` 有显著差距，证明任务确实依赖 memory。
- 至少两个 baseline 在 `premature execution` 与 `unnecessary search` 上呈现不同 trade-off。
- 配对 variant 中，强模型的 action flip 不是近乎满分，否则 monitor 问题太简单。
- FullHistory 不能轻易饱和全部任务；否则扩大 memory、冲突和预算约束。
- 人工对 state 和 admissible action 的一致率足够高。
- 至少 80% 主指标可规则化计算。

## 16. 10 周执行计划

| 周 | 目标 | 交付物 |
|---|---|---|
| 1 | 固化 taxonomy、动作空间和 20 个手工样例 | spec v0.1 + annotation guide |
| 2 | symbolic world、variant generator、validator | 120-episode pilot |
| 3 | Track A evaluator 与四个 sanity baselines | pilot report + go/no-go |
| 4–5 | memory API、Track B、两个工具域 | executable harness |
| 6 | BM25/dense/hybrid、Mem0/A-MEM、adaptive router | baseline table v1 |
| 7 | MemCon/学习型 controller 接入与 oracle decomposition | diagnostic table |
| 8 | 扩到 1,800+ episodes，human challenge review | dataset v1 |
| 9 | calibration、counterfactual、budget、cross-domain 实验 | full result matrix |
| 10 | 论文与开源清理 | paper draft + code/data card |

## 17. 论文写作骨架

### Introduction

1. 长期 memory 让 Agent 跨 session 复用事实和经验。
2. 现有 benchmark 从 recall 进展到 strategic use、state tracking 和 memory-to-action。
3. 但在真实行动前，Agent 还要解决一个未被单独测量的问题：当前 memory 到底够不够；不够时应搜、问，还是拒绝。
4. 现有 end-to-end success 会混淆 monitor/control/retrieval/execution，给定候选池又无法测试主动控制。
5. 提出 MetaMemBench 与四层诊断协议。

### Related Work

- Long-term memory recall and evolution：LoCoMo、LongMemEval、MemoryAgentBench、StateMemBench。
- Strategic and actionable memory：StratMem-Bench、Mem2ActBench、MemoryArena、TANGLE。
- Memory operation and control：MemOps、MemTrace、Memory-R1、AgeMem、MemCon。
- Adaptive/agentic retrieval：Self-RAG、MemSearcher，以及 survey 中 retrieval timing/intent 的路线。

### Method / Benchmark

- formal problem；
- state/action taxonomy；
- counterfactual generator；
- three tracks；
- exact evaluator 与 metrics。

### Experiments

- validity；
- main comparison；
- oracle decomposition；
- counterfactual consistency；
- calibration/cost；
- robustness/generalization。

### Discussion

- Agent Memory 与 Agentic RAG 的边界；
- 为什么 memory sufficiency 不等于 retrieval relevance；
- 何时应当澄清而非继续检索；
- synthetic-to-real gap、privacy 和用户打扰成本。

## 18. 当前推荐决策

### 推荐主线

> **MetaMemBench：评测 Agent 对持久记忆的充分性监控与查询时控制。**

### 暂时放弃的表述

> Dynamic Strategic Memory Use Benchmark

它可以作为 related-work bridge 或一个 subtask 名称，但不宜做论文标题和核心 novelty。

### 与之前 ResearchLedgerBench 的关系

ResearchLedgerBench 可以降级为未来的 **domain-specific stress test**：科研 artifact 的版本和依赖天然适合产生 `stale / missing / irreducible` 决策点。但第一篇 benchmark 先用通用、可执行的 personal tool 与 progressive search 任务建立问题定义，避免因为科研场景太窄而削弱通用性。

## 参考文献入口

- Hu et al. [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564), 2025/2026 survey.
- Wu et al. [StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/), ACL 2026 Long Paper.
- Shen et al. [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/), ACL 2026 Long Paper.
- He et al. [MemoryArena](https://arxiv.org/abs/2602.16313), arXiv 2026.
- Cheng et al. [AMemGym](https://arxiv.org/abs/2603.01966), ICLR 2026.
- Hao et al. [MemOps](https://arxiv.org/abs/2607.12893), arXiv 2026.
- Deng et al. [MemTrace](https://arxiv.org/abs/2605.28732), arXiv 2026.
- Yang et al. [TANGLE](https://arxiv.org/abs/2608.13921), arXiv 2026.
- Fan et al. [StateMemBench](https://arxiv.org/abs/2608.19652), arXiv 2026.
- Yu et al. [AgeMem](https://aclanthology.org/2026.acl-long.981/), ACL 2026 Long Paper.
- Jiang et al. [Memory as a Controlled Process (MemCon)](https://arxiv.org/abs/2607.13591), arXiv 2026.
- Hu et al. [MemoryAgentBench](https://arxiv.org/abs/2507.05257), 2025.
- Liu et al. [StreamMemBench](https://arxiv.org/abs/2606.14571), 2026.
- Mireshghallah et al. [CIMemories](https://arxiv.org/abs/2511.14937), ICLR 2026.
- Wang et al. [Decision-Aware Memory Cards / CICL](https://arxiv.org/abs/2606.08151), 2026.
- Shen et al. [Understanding Stage-Wise Utility–Risk Trade-offs in LLM Agent Memory (MemGauge)](https://arxiv.org/abs/2608.30177), 2026.
