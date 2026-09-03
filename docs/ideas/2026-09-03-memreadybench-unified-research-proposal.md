---
title: "MemReadyBench：持久记忆 Agent 的来源感知证据闭合与行动控制基准"
type: research-proposal
status: canonical
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agent-memory", "benchmark", "action-readiness", "evidence-closure", "source-routing", "counterfactual-evaluation"]
---

# MemReadyBench：持久记忆 Agent 的来源感知证据闭合与行动控制基准

## 0. 最终统一方案

### 0.1 一句话研究问题

> **在持久记忆和部分可观测环境中，Agent 能否判断当前证据是否已经闭合全部行动条件；若尚未闭合，能否识别缺失条件及其权威来源，在 `SEARCH_MEMORY / VERIFY_WORLD / ASK_USER / EXECUTE / ABSTAIN` 之间进行风险与成本校准的控制，并只在证据闭合后执行可验证行动？**

这一表述将此前两个侧重点统一为一条完整链路：

1. **Memory monitoring**：当前可见证据够不够。
2. **Requirement diagnosis**：缺少哪个行动条件，或者哪里存在冲突。
3. **Source-aware control**：应从 memory、world、user 中哪个来源解决。
4. **Evidence closure**：新证据是否真正闭合了 requirement graph。
5. **Executable commitment**：何时可以产生外部副作用，以及结果是否正确。

因此，本项目既不是单纯的 memory retrieval benchmark，也不是一般的 act/abstain benchmark。研究对象是：

> **persistent-memory Agent 在行动承诺前，对“证据状态—缺失条件—权威来源—控制动作—执行结果”完整决策链的诊断。**

### 0.2 推荐标题

> **MemReadyBench: Evaluating Source-Aware Evidence Closure and Action Control in Persistent-Memory Agents**

较短版本：

> **MemReadyBench: Source-Aware Action Readiness for Persistent-Memory Agents**

### 0.3 审稿式判断

- **问题重要性**：强。长期 Agent 会在不完整、过时、冲突或来源错误的记忆上过早行动。
- **问题层首创**：不能声称。SafeCommit 已直接研究 memory uncertainty 下的 safe commitment。
- **可防守创新**：较强，但必须落在 requirement-source closure、来源迁移反事实、逐决策点联合 gold 和真实 memory stack 诊断的交叉点。
- **方法创新**：第二阶段再做。通用 ranker/verifier/controller/gate 的模块组合不足以单独构成主要贡献。
- **资源可行性**：适合四卡 4090。主要工程量是 generator、simulator、validator 和 evaluation harness，而不是大规模预训练。

## 1. 为什么要做：问题来自哪些已有工作

### 1.1 Strategic memory use 不等于行动准备度

[StratMem-Bench](https://aclanthology.org/2026.acl-long.1491/) 评估给定候选记忆后，哪些是 required、supportive 或 irrelevant，核心问题是“应该使用哪些记忆”。它不要求 Agent 主动搜索、验证世界、询问用户，也不判断当前证据是否足以执行带副作用的动作。

[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/) 已把长期记忆用于 tool selection 和 parameter grounding，但主要输出是离线 tool call；它揭示了 retrieval 与 oracle retrieval 的明显差距，却没有把 search、verify、clarification 和 abstention 作为正式在线控制动作。

由此得到第一层问题：

> 检索到相关记忆，并不意味着已经获得了执行所需的最小充分证据。

### 1.2 Safe commitment 已被提出，但真实 memory stack 仍缺少诊断

[SafeCommit](https://arxiv.org/abs/2608.04289) 已形式化 memory uncertainty 下的 premature commitment，在 `commit / probe / fallback` 中进行风险控制。这意味着“判断现有证据是否足以安全行动”不能再作为首创。

但 SafeCommit 当前实验是 proof-of-concept：使用少量显式 latent worlds、固定 action set、手工 safety map 和确定性二值 probe，尚未系统评估真实 LLM 如何从自然语言长历史、检索 packet 和持久 memory backend 中恢复证据状态。

由此得到第二层问题：

> 需要把安全承诺从理想化 world set 推进到真实 memory system 的 reader、retriever、controller 和 executor 诊断。

### 1.3 Verify world 与 ask user 是不同的 source-of-truth 边界

[Remember, Verify, or Ask?](https://arxiv.org/abs/2608.19564) 区分 persist、current-only、verify-world 和 ask-user，证明变化的世界事实与只有用户知道的意图/授权不能统一处理。但它研究的是信息写入或记忆承诺边界，动作被记录而不执行，也没有 query-time 多步获取与最终环境结果。

[KnowU-Bench](https://arxiv.org/abs/2604.08455) 进一步在 Android 环境中测试 preference elicitation、consent 和 proactive intervention，说明用户来源和可执行闭环均已有邻近工作。

由此得到第三层问题：

> 证据不足不是单一状态；真正的控制难点是判断缺失条件应由 memory、world、user 还是其他来源解决。

### 1.4 Paired act/abstain 和 memory skepticism 也已有工作

[AgentAbstain](https://arxiv.org/abs/2607.10059) 已使用成对单因素任务和可执行 sandbox 测试 Agent 何时不应行动。因此 paired task、action flip 和 executable abstention 不能作为单独创新。

[MemSyco-Bench](https://arxiv.org/abs/2607.01071) 已评估记忆何时不应被当作事实、如何处理记忆与客观证据冲突以及如何限制记忆作用域。因此“记忆并不总是有益”也不是新结论。

仍然缺少的，是把反事实干预明确施加在 **持久记忆中决定性证据的来源位置和有效性** 上，并同时检查来源路由与最终闭合。

### 1.5 Sufficiency router 与 memory operation policy 已经存在

- [Router-Mem](https://arxiv.org/abs/2608.01285) 已根据 evidence sufficiency 决定提前停止还是深度分析。
- [InfMem](https://arxiv.org/abs/2602.02704) 已使用 PreThink-Retrieve-Write 和 SFT-to-RL 控制检索、写入和停止。
- [SURE-RAG](https://arxiv.org/abs/2605.03534) 已将 evidence sufficiency 定义为集合级属性。
- [Memory as a Controlled Process](https://arxiv.org/abs/2607.13591) 已把 retrieve、re-retrieve、plan injection、consolidate 和 forget 建模为 memory MDP。
- [Oblivion](https://arxiv.org/abs/2604.00131) 已依据 uncertainty 和 memory utility 决定何时访问记忆。

因此，`retrieve-or-stop`、`operation-as-action`、`setwise verifier` 或 SFT-to-RL 均只能作为 baseline 或实现组件，不能单独锚定贡献。

## 2. 统一的 Research Gap

### 2.1 中文版本

> 近期研究已经分别覆盖了候选记忆的战略选择、记忆充分性路由、记忆不确定性下的安全承诺、澄清与拒绝以及 memory operation policy；但现有评测通常只研究其中一个边界，或者只报告最终任务成功。尚缺少一个面向交互生成持久记忆的统一诊断 benchmark：它能够显式表示行动所需的 requirement closure，区分当前 packet、持久 memory、外部 world 和 user 等权威来源，通过受控来源迁移改变正确的获取动作，并在成功获取证据后验证所有可解决版本是否收敛到相同的可执行结果。

### 2.2 英文版本

> Recent work has studied strategic memory use, evidence sufficiency routing, safe commitment under memory uncertainty, clarification and abstention, and memory-operation policies. However, existing evaluations typically isolate one boundary or collapse the full process into end-task success. What remains under-evaluated is whether agents grounded in interaction-derived persistent memory can identify unresolved action requirements, locate the authoritative source capable of resolving each requirement, switch acquisition actions under matched source-relocation interventions, and converge to a verified executable outcome once the evidence is closed.

### 2.3 核心创新锚点

本项目的创新不应写成某个组件，而应写成下面这组完整对象：

> **Requirement-aware readiness + source-aware acquisition + counterfactual source relocation + executable closure verification**

更具体地说：

1. **Requirement-level readiness**：准备度不是模型置信度，而是 action requirements 是否被当前、有效、权威的证据闭合。
2. **Source-aware acquisition**：对每个缺失 requirement，显式判断应访问 memory、world、user 还是应停止。
3. **Counterfactual source relocation**：保持同一任务目标和大部分语言不变，只移动决定性证据的位置或有效性，要求控制动作发生可预测翻转。
4. **Executable closure**：信息获取成功后，不只检查文本回答，还检查是否达到同一个合法环境终态。
5. **Diagnostic decomposition**：通过 oracle packet/retriever/monitor/router/executor 分离真实 memory stack 的失败位置。

## 3. 统一概念模型

### 3.1 五层决策链

| 层 | 核心问题 | 主要输出 | 典型错误 |
|---|---|---|---|
| L1 Monitor | 当前证据够不够？ | `READY / NOT_READY / CONFLICTED` | 把相关当充分；忽略冲突 |
| L2 Diagnose | 缺什么或冲突在哪？ | missing requirement / conflict set | 只说“不确定”，找不到具体 slot |
| L3 Locate | 哪个来源能够权威解决？ | packet / memory / world / user / unavailable | 在错误来源反复搜索 |
| L4 Control | 下一步做什么？ | search / verify / ask / execute / abstain | 过早执行或不必要询问 |
| L5 Commit | 获取后是否真正闭合并执行正确？ | evidence closure + exact outcome | lucky success、越权或错误终态 |

这五层共同定义 **Source-Aware Memory Readiness and Control**。L1 保留“记忆监控”的研究价值，L2-L4 构成主要新颖性锚点，L5 保证 benchmark 不退化成静态分类。

### 3.2 旧状态分类如何被统一吸收

原来基于 memory sufficiency 的状态不再作为另一套并行定义，而作为统一状态空间中的 benchmark slices：

| 可解释 Slice | Readiness | 缺失来源/完整性 | 预期动作 |
|---|---|---|---|
| `NO_MEMORY_NEEDED` | READY | 当前 observation 已闭合，无历史依赖 | EXECUTE |
| `SUFFICIENT` | READY | CURRENT_PACKET + FRESH | EXECUTE |
| `RETRIEVABLE_MISSING` | NOT_READY | PERSISTENT_MEMORY | SEARCH_MEMORY |
| `WORLD_ONLY_MISSING` | NOT_READY | WORLD | VERIFY_WORLD |
| `USER_ONLY_MISSING` | NOT_READY | USER | ASK_USER |
| `RESOLVABLE_STALE_OR_CONFLICT` | CONFLICTED | 来源由 authority/provenance 决定 | SEARCH / VERIFY / ASK |
| `IRREDUCIBLE` | NOT_READY 或 CONFLICTED | UNAVAILABLE | ABSTAIN |
| `DISTRACTOR_HEAVY` | 继承原状态 | 相关但不闭合 requirement | 动作应保持不变 |

这样既保留原方案对 sufficient、stale、irreducible 和 no-memory 的诊断，又补上 `WORLD_ONLY_MISSING`，并避免把状态和来源混成一个不可扩展的平面标签。

## 4. 正式问题定义

### 4.1 环境与持久记忆

在时间步 \(t\)，Agent 接收：

- 当前目标 \(g_t\)；
- 当前环境观察 \(o_t\)；
- 由历史交互、行动与反馈形成的持久记忆库 \(M_t\)；
- 当前工作上下文中的 evidence packet \(C_t\)；
- 外部世界接口 \(W_t\)，如 calendar、booking、filesystem；
- 用户接口 \(U_t\)，提供私有意图、偏好或授权；
- 剩余预算 \(b_t\)，包括 token、检索、验证、询问和环境步骤。

只有当 memory 来自跨 session 的 interaction history 并持续影响后续决策时，主任务才归入 Agent Memory；若只是固定外部文档库，则更接近 Agentic RAG，可作为 transfer setting。

### 4.2 Requirement–Source Closure Graph

每个任务具有一组行动要求：

\[
R(g_t)=\{r_1,r_2,\ldots,r_n\}.
\]

每个 requirement 包含：

- value 或约束；
- freshness/time validity；
- authority；
- provenance；
- authorization；
- 可接受的替代证据集合。

定义 evidence graph 中的关系：

- `supports(e, r)`；
- `refutes(e, r)`；
- `supersedes(e_i, e_j)`；
- `authorizes(e, action)`；
- `located_at(e, source)`。

当前 evidence packet 形成闭合，当且仅当至少存在一个合法证据集合 \(E_k^*\)，完整覆盖全部必要 requirements，且不存在未解决冲突、过时值或授权缺口：

\[
\operatorname{Closed}(C_t,g_t)=1
\iff
\exists E_k^* \subseteq C_t,
\ E_k^* \models R(g_t).
\]

允许多个 \(E_k^*\)，避免将一种措辞或一条检索路径误设为唯一 gold。

### 4.3 Readiness

\[
y_t^{ready}\in\{\text{READY},\text{NOT\_READY},\text{CONFLICTED}\}.
\]

- `READY`：当前可见证据已经形成合法 closure。
- `NOT_READY`：至少一个必要 requirement 未闭合。
- `CONFLICTED`：当前证据存在尚未解决的 refute/supersede/authority 冲突。

Readiness 与模型主观 confidence 分开标注；模型可以高置信地错误执行，也可以低置信但证据已经充分。

### 4.4 Missing Requirement 与 Source

对每个未闭合 requirement \(r_j\)：

\[
y_{t,j}^{source}\in
\{\text{CURRENT\_PACKET},
\text{PERSISTENT\_MEMORY},
\text{WORLD},
\text{USER},
\text{UNAVAILABLE}\}.
\]

这里标的是能够权威解决缺口的来源，而不是文本出现的位置。旧日历事件可能在 memory 中，但当前可用时间的权威来源仍是 WORLD；历史偏好可以在 memory 中，但一次性购买授权仍来自 USER。

### 4.5 Integrity

证据完整性单独建模：

\[
q(e)\in\{\text{FRESH},\text{STALE},\text{CONFLICTING},\text{POISONED},\text{AUTHORIZATION\_DRIFT}\}.
\]

Source 与 Integrity 是两个轴。`MEMORY + STALE`、`WORLD + CONFLICTING` 和 `USER + AUTHORIZATION_DRIFT` 需要不同的 probe 与控制行为。

### 4.6 动作空间

\[
a_t\in\{\text{SEARCH\_MEMORY},\text{VERIFY\_WORLD},\text{ASK\_USER},\text{EXECUTE},\text{ABSTAIN}\}.
\]

- `SEARCH_MEMORY(query,k)`：改写 query，从持久 memory store 检索证据。
- `VERIFY_WORLD(tool,args)`：访问当前外部状态或权威系统。
- `ASK_USER(question,missing_requirements)`：询问只有用户能确定的意图、偏好或授权。
- `EXECUTE(action,evidence_ids)`：提交回答或工具调用，并声明证据依据。
- `ABSTAIN(reason,missing_requirements)`：证据不可得、策略禁止或风险过高时停止承诺。

`DEFER / ESCALATE / POLICY_BLOCK` 作为 `ABSTAIN` 的 reason code，首版不扩充成独立动作。`WRITE/UPDATE/DELETE/FORGET` 不进入主 action space，避免与 lifecycle memory benchmark 重叠。

### 4.7 Partial Observability 与 Admissible Action Set

每个 decision point 分开标注：

1. latent world state；
2. Agent-observable state；
3. admissible action set \(A_t^{adm}\)；
4. 每个动作的信息增益、成本和风险；
5. 在完整生成图上计算的 oracle action \(a_t^*\)。

不能依据隐藏真相要求 Agent 猜中唯一动作。例如，首次发现日期缺失时，若当前观测无法判断日期是否藏在 memory，`SEARCH_MEMORY` 和 `ASK_USER` 都可能 admissible；搜索明确无结果后继续搜索才是控制失败。主指标先判断动作是否 admissible，再用 policy regret 区分成本。

## 5. Benchmark 的五个创新点

### 5.1 Requirement-Level Action Readiness

把“够不够”从主观 confidence 或 passage relevance 改为可验证的 requirement closure。每个行动条件、证据依赖、时效、来源和授权均可追踪。

### 5.2 Source-Aware Evidence Acquisition

不仅预测 `NOT_READY`，还要回答：缺什么、应向哪里获取、获取之后是否应停止。`VERIFY_WORLD` 与 `ASK_USER` 被正式区分。

### 5.3 Source × Integrity Counterfactual Families

对同一 base task，只移动决定性 evidence 的来源或有效性：

| 来源变体 | 决定性证据在哪里 | 预期第一动作 |
|---|---|---|
| Packet | 当前 packet 完整可见 | EXECUTE |
| Memory | 仅持久 store 中可得 | SEARCH_MEMORY |
| World | 仅当前环境可确认 | VERIFY_WORLD |
| User | 仅用户可确认 | ASK_USER |
| Unavailable | 所有允许来源均无解 | ABSTAIN |
| No-memory-needed | 行动不依赖历史 | EXECUTE，不得多余获取 |

再叠加 Fresh、Stale、Conflicting、Poisoned 和 Authorization Drift。不是机械生成全笛卡尔积，而是由 domain schema 选择语义成立的组合。

### 5.4 Action Flip + Closure Convergence

一个合格的 counterfactual family 同时满足：

1. **Action Flip**：来源改变后，第一控制动作按 gold 发生变化。
2. **Closure Convergence**：所有可解决变体成功获取证据后，最终 action 和 environment state 收敛到同一合法结果。
3. **Irrelevant Invariance**：仅增加 distractor/supportive-only memory 时，必要控制动作不应变化。

这三个约束共同防止 benchmark 退化成来源关键词分类。

### 5.5 Decision-Point Gold 与 Oracle Decomposition

每个关键决策点同时提供 readiness、missing requirements、requirement-source map、closure、admissible actions、oracle regret、tool precondition 和 exact postcondition。替换不同模块为 oracle，分离：

- packet construction failure；
- retrieval failure；
- readiness monitoring failure；
- source routing failure；
- evidence integration failure；
- execution failure。

## 6. 三个递进 Track

### Track A：Oracle-Packet Readiness Diagnosis

给定包含全部当前可访问证据和受控 distractor 的 packet，不开放获取动作。模型预测 readiness、missing requirements、source location、evidence closure 和 confidence。

目的：隔离 reader/monitor，验证模型是否理解“相关但不充分”“完整但过时”“冲突但可解决”等状态。

### Track B：Sequential Source-Aware Acquisition

只给初始任务和三个 API：memory search、world verify、user ask。Agent 可多轮改写 query、获取证据、停止、执行或拒绝。

目的：评估 retrieval intent、source routing、query construction、stop decision、clarification quality 和 budget allocation。

### Track C：Closed-Loop Executable Commitment

最终动作进入确定性工具或小型环境，产生可验证状态变化。错误参数、过时状态、未授权行为和 premature execution 由规则 evaluator 判定。

目的：验证 monitor/control 的改善是否真正转化为合法行动，而不是只改善解释文本。

Track A 是必要的低成本诊断，但论文主结果必须包含 Track B/C，否则工作会被理解为静态分类数据集。

## 7. 数据构造

### 7.1 Symbolic World First

1. 定义 domain entities、state transitions、tool contracts 和 source authority。
2. 采样 base goal 与 requirement graph。
3. 生成 3–8 个历史 sessions，包括用户陈述、Agent 行动、工具反馈和状态更新。
4. 从历史构造持久 memory store，不直接手写最终 memory answer。
5. 指定 decisive requirements 的 source 和 integrity。
6. 派生 matched counterfactual family。
7. 用模板和 LLM 渲染自然语言对话、日志和 memory entries。
8. 运行 deterministic validator 检查 closure、admissible actions 和 environment outcome。
9. 人工审核自然度、歧义和唯一干预因素。

### 7.2 首批任务域

#### Personalized Tool Execution

日历、出行、预订、提醒和文件操作。历史偏好来自 memory，当前状态来自 world，一次性意图/授权来自 user，最终 tool state 可规则评分。

#### Progressive Search and Planning

Agent 跨 session 收集约束与工具反馈，后续任务依赖早期发现。使用本地文档库或 deterministic mini-web，gold 是 requirement closure、规划约束和最终执行状态。

Pilot 优先 calendar/scheduling 与 travel/booking。Coding/file operation 和 communication/email 在 MVP 后扩展。

### 7.3 Hard Negatives

- 同一实体和主题，但参数属于旧 session。
- 历史默认偏好与本轮一次性指令冲突。
- 相关但无法唯一执行的 partial evidence。
- 旧 world state 被当前环境覆盖。
- 真实但不再授权使用的信息。
- 从成功经验抽取、但与当前工具版本不兼容的策略。
- supportive memory 很有帮助，但并非 action requirement。
- 完整答案附近的高相似错误值。

### 7.4 数据 Schema

```json
{
  "episode_id": "...",
  "base_task_id": "...",
  "domain": "travel_booking",
  "history_events": [],
  "memory_store": [],
  "world_state": {},
  "user_state": {},
  "initial_packet": [],
  "goal": {},
  "requirements": [
    {
      "id": "purchase_authorization",
      "required": true,
      "authoritative_source": "USER",
      "integrity": "FRESH"
    }
  ],
  "decision_points": [
    {
      "readiness": "NOT_READY",
      "missing_requirements": ["purchase_authorization"],
      "source_map": {"purchase_authorization": "USER"},
      "admissible_actions": ["ASK_USER"],
      "action_costs": {"ASK_USER": 1.0, "SEARCH_MEMORY": 2.5},
      "forbidden_actions": ["EXECUTE"]
    }
  ],
  "gold_final_action": {},
  "gold_environment_state": {},
  "budgets": {"search": 3, "verify": 2, "ask": 1}
}
```

### 7.5 数据规模

#### Pilot

- 20 个 base tasks；
- 每个至少 6 个 source variants，共 120+ episodes；
- 选择 2–3 个 integrity slices；
- 2 个任务域；
- 20–50 条 memory entries；
- 先使用 prompt/rule baselines，不训练。

#### MVP Paper Version

- 300–500 个 base tasks；
- 2,000–4,000 个主 episodes；
- 5,000–10,000 个 decision points；
- memory size 为 20/100/500 三档；
- 3–4 个任务域；
- 至少 10% human-authored/re-written challenge split；
- hidden generated test 支持重新采样，降低 contamination。

所有 counterfactual variants 必须以 `base_task_id` 为单位进入同一 split。

## 8. 指标体系

### 8.1 Monitoring

- Readiness Macro-F1；
- Sufficiency AUROC/AUPRC；
- Missing Requirement F1；
- Source Location Macro-F1；
- Evidence Closure P/R/F1；
- Brier Score、ECE 与 risk-coverage。

### 8.2 Control 与 Routing

- Admissible Action Accuracy；
- Source-Routing Accuracy；
- Wrong-Source Acquisition Rate；
- Evidence-Location Regret；
- Premature Execution Rate；
- Unnecessary Search/Verify/Ask Rate；
- Targeted Clarification Score；
- Acquisition-to-Closure Steps。

### 8.3 Counterfactual

- Cross-Source Action-Flip Consistency；
- Closure-Convergence；
- Irrelevant Invariance；
- Stale-to-Current Sensitivity；
- Integrity Sensitivity；
- Surface-Paraphrase Robustness。

### 8.4 Outcome 与成本

- Exact Tool State / Task Success；
- Unsupported Success；
- Authorization Violation；
- Abstention Precision/Recall；
- Token、retrieval、world-call、user-call 与 wall-clock cost；
- Success–Cost Pareto Frontier。

不使用单一总分。至少分别报告 `Monitor / Routing / Counterfactual / Outcome + Cost` 四组指标。

## 9. Baseline 与公平比较

### 9.1 Sanity Baselines

- NoMemory、FullHistory、Retrieve-Once@k；
- AlwaysExecute、AlwaysSearch、AlwaysVerify、AlwaysAsk、AlwaysAbstain；
- RandomRoute；
- lexical source classifier；
- confidence threshold。

### 9.2 Retrieval 与 Memory Systems

- BM25、dense、hybrid retrieval；
- long-context history；
- Mem0/LangMem 类 store；
- A-MEM；
- StateMem-style supersession wrapper；
- StratMem-style direct reader。

### 9.3 Agentic Control Baselines

- SafeCommit 风格 `commit/probe/fallback` wrapper；
- MCB 风格 source-of-truth prompt；
- AgentAbstain 风格 pre-execution gate；
- SURE-RAG 风格 setwise verifier；
- Router-Mem 风格 early-stop router；
- MemSearcher、Memory-R1、AgeMem；
- MemCon 与 Oblivion。

### 9.4 Oracle Ladder

- OraclePacket；
- OracleRetriever；
- OracleReadiness；
- OracleSourceRouter；
- OracleExecutor；
- OracleAll。

所有方法固定 backbone、tool schema、可见 source、token、检索轮数、world/user 调用次数和 wall-clock budget。

## 10. 核心实验

### E0：Benchmark Validity

- OracleAll 可解率；
- 人工 state/source/action 一致率；
- 删除 decisive evidence 是否破坏 closure；
- 加入 irrelevant evidence 是否保持 oracle action；
- lexical shortcut 与 template leakage 检查。

### E1：Main Benchmark

比较不同模型、long-context/RAG/memory backend/controller 的四组指标，重点展示 task success 相近但控制质量不同的系统。

### E2：Source Relocation

对每个 family 报告 action flip、wrong-source rate、acquisition cost 和 closure convergence。

### E3：Integrity Stress

分别分析 stale、conflict、poison 和 authorization drift 如何改变 readiness、source 和 commit risk。

### E4：Oracle Failure Decomposition

依次替换 packet、retriever、monitor、source router 和 executor，回答不同系统的主要瓶颈在哪里。

### E5：Calibration and Selective Action

比较 prompt calibration、self-consistency、temperature scaling 和专门 readiness monitor，绘制 risk–coverage 曲线。

### E6：Budget and Scaling

控制 memory size、top-k、最大 acquisition rounds、token、模型尺寸和 source cost，比较 success–cost Pareto。

### E7：Cross-Domain Generalization

在一个工具域调节 controller，在另一个域测试；检查策略是否只记住模板。

## 11. 可证伪假设

- **H1**：最终 task success 会高估 readiness/control，因为存在猜测、full-context 泄露和 unsupported success。
- **H2**：强模型在 Memory/World/User 来源迁移下仍表现出惯性动作，action flip 显著低于 oracle。
- **H3**：FullHistory 能减少部分 SEARCH 错误，但不能解决 WORLD/USER routing，并会放大 stale/poison 风险。
- **H4**：固定 retrieve-once 在 hidden-in-memory 上有效，却会在 no-memory-needed 和 world/user slices 上增加成本或错误。
- **H5**：MemCon 类方法可提升平均 success–cost，但未必改善 source routing 与 readiness calibration。
- **H6**：显式 requirement/source supervision 比单独加强 retriever 更能减少 premature execution，二者结合最好。

如果简单 `FullHistory + prompt` 已接近 oracle，或 H1–H5 大部分不成立，则 benchmark 太简单或来源干预不自然，应停止扩展。

## 12. 第二阶段方法：Source-Aware Readiness Controller

Benchmark 先于 Method。只有 E1–E4 明确显示 source routing 是独立瓶颈，才训练控制器。

### 12.1 Reference Architecture

1. Requirement Extractor：把目标转成待闭合条件。
2. Evidence and Provenance Reader：读取 evidence 的值、时间、来源、scope 和 authority。
3. Setwise Closure Verifier：判断候选集合是否完整支持 requirement graph。
4. Readiness Monitor：输出 readiness 与 calibration。
5. Source Router：在 memory/world/user/unavailable 间定位缺口。
6. Execution Gate：未闭合时阻止 side effect。

这些模块是 reference implementation，不将“六模块组合”本身作为主要创新。

### 12.2 Pointwise、Pairwise 与 Listwise 的位置

- **Pointwise**：预测单条 evidence 的 relevance、freshness、authority、scope 和 requirement coverage。
- **Pairwise**：比较正确来源/证据与 hard negative，适合下一条证据或下一动作选择。
- **Listwise/Setwise**：在多个候选 action/evidence 之间选择能以最低风险和成本闭合全部 requirements 的集合。

训练创新应落在 **同一 counterfactual family 的 source-transition supervision**：当决定性证据从 memory 移到 world/user 时，模型必须改变动作，而不是只提高静态分类准确率。

### 12.3 训练路线

1. Prompt/rule controller：验证 benchmark 和错误谱系。
2. SFT：学习 readiness、missing requirement、source map 和 structured tool calls。
3. Pairwise routing：正确来源动作对 hard negative 来源动作。
4. Listwise admissible ranking：在允许动作集合中最小化 cost-sensitive regret。
5. Optional RL：只有顺序探索、停止和长期成本无法由监督学习覆盖时再使用。

### 12.4 Reward

\[
R = \alpha R_{readiness}
+ \beta R_{route}
+ \gamma R_{closure}
+ \delta R_{outcome}
- \lambda_c C_{acquisition}
- \lambda_p P_{premature}
- \lambda_u P_{unsupported}.
\]

- 过程奖励来自 requirement-source gold、admissible action 和 closure。
- 最终奖励来自 exact tool state 或 task-specific verifier。
- ranking score 只塑造候选竞争关系，不替代最终可验证结果。
- MVP 不训练独立 GRM；symbolic gold 与 environment validator 已提供 RLVR 风格信号。

## 13. 两周最小闭环

### 13.1 实现范围

- 20 个 base tasks；
- calendar/scheduling 与 travel/booking 两个域；
- 每个任务至少六个 source variants；
- 一个 persistent memory API；
- 一个 world verification API；
- 一个 user simulator；
- 一个有 side effect 的 execute API；
- 一个小模型 smoke、一个 7B/8B 开源模型和一个强 API 模型；
- 不训练。

### 13.2 Go / No-Go Gate

必须同时满足：

1. OracleAll 可解率不低于 98%。
2. 至少 80% 主指标由 deterministic evaluator 计算。
3. FullHistory 与简单 prompt 在跨来源 family 上不能接近 oracle。
4. 至少两个 baseline 呈现不同的 routing/cost/premature trade-off。
5. source relocation 稳定造成正确 action flip。
6. surface paraphrase 和 irrelevant distractor 不应改变动作。
7. 成功获取证据后，可解决版本达到 closure convergence。
8. 人工对 readiness、missing requirement、source 和 admissible set 的一致率足够高。

No-Go 条件：

- `VERIFY_WORLD` 与 `ASK_USER` 在自然任务中无法稳定区分；
- 数据只能靠显式来源关键词制造难度；
- FullHistory + prompt 已经饱和；
- 最终行动无法在来源变体间定义共同终态；
- oracle decomposition 不能产生系统级诊断。

## 14. 十周执行计划

| 周 | 工作 | 里程碑 |
|---|---|---|
| W1 | taxonomy、requirement graph、20 个 base tasks | 人工检查定义是否无歧义 |
| W2 | generator、三个 acquisition API、120+ episodes | Pilot Go/No-Go |
| W3 | Track A 与 sanity baselines | readiness/source 诊断表 |
| W4–5 | Track B/C 与第二任务域 | 可执行闭环 |
| W6 | retrieval 与 memory systems | 公平 baseline harness |
| W7 | SafeCommit/MCB/MemCon 等直接 baseline | 最邻近工作对照 |
| W8 | 扩展到 2,000+ episodes | 数据与 hidden generator |
| W9 | oracle、counterfactual、budget 分析 | 核心 findings |
| W10 | data card、论文、代码和评测脚本 | 可投稿版本 |

只有 W2 gate 通过才进入 W3–W10；只有 W7 明确暴露 routing bottleneck 才进入方法训练。

## 15. 预期论文贡献

### 15.1 可以主张的贡献

1. 提出 **source-aware evidence closure and action control** 的统一评测对象，把 memory sufficiency 细化到 requirement 与 authoritative source 层。
2. 构建 Source × Integrity 的 matched counterfactual families，同时评估 action flip、irrelevant invariance 和 closure convergence。
3. 提供 readiness、missing requirement、source map、admissible action、evidence closure 和 exact outcome 的逐决策点联合 gold。
4. 提出 Monitor/Route/Close/Commit 四层指标与 oracle ladder，系统诊断真实 memory backend 与 controller 的瓶颈。
5. 发布可执行、可重采样的 benchmark generator、tool environment 和 baseline harness。

### 15.2 不能主张的内容

- 首次研究 memory sufficiency；
- 首次提出 safe commitment；
- 首次引入 search/ask/verify/abstain；
- 首次做 paired executable tasks；
- 首次把 memory operation 当作 action；
- 首次研究 stale/conflict/poison；
- 首次提出 setwise evidence verification；
- 首次做 memory-to-action benchmark。

正式论文使用 `to our knowledge` 或 `we find no existing benchmark that jointly...`，不使用绝对 first claim。

## 16. 与最邻近工作的最终区分

| 工作 | 核心问题 | 关键 Gold/输出 | MemReadyBench 的增量 |
|---|---|---|---|
| StratMem-Bench | 给定记忆池后应该使用哪些内容 | must/nice/irrelevant | 主动来源获取、证据闭合和执行 |
| Mem2ActBench | 长期记忆能否恢复工具参数 | tool/parameter accuracy | 获取动作与 query-time control |
| SafeCommit | proposed action 是否在保留 worlds 中安全 | safety certificate | 真实 memory stack 中的 requirement/source 发现与诊断 |
| MCB | 信息应 persist/local/verify/ask | boundary label/tool call | read/use-time sequential acquisition 与 outcome |
| AgentAbstain | Agent 何时不应行动 | paired act/abstain | 干预持久证据来源，并区分 search/verify/ask |
| SURE-RAG | 检索证据是否支持答案 | support/refute/insufficient | 外部副作用行动与多来源获取 |
| MemSyco-Bench | 记忆何时不应影响决策 | memory-use behavior | 未闭合 requirement 的来源路由 |
| MemCon/Oblivion | 如何学习 memory operation policy | task success/cost | 跨系统逐决策点 gold 与 oracle diagnosis |
| **MemReadyBench** | 哪些行动条件未闭合、应从哪里获取、何时可执行 | readiness + source + action + closure + exact outcome | 统一 benchmark 主体 |

最简洁的定位句：

> **SafeCommit asks whether a proposed action is certifiably safe; MemReadyBench evaluates whether real persistent-memory agents can discover what is missing, route to the authoritative source, close the evidence, and then act correctly.**

## 17. 最终决策

> **本项目只保留一条主线：以 requirement-level action readiness 为监控基础，以 source-aware evidence acquisition 为创新锚点，以 counterfactual source relocation 为数据核心，以 action flip 与 closure convergence 为关键指标，以 executable commitment 和 oracle decomposition 为验证闭环。**

近期只实施 20-task pilot。Pilot 通过后扩展 benchmark；benchmark 明确证明 source routing 是独立瓶颈后，再进入 SFT、pairwise/listwise ranking 或可选 RL。

完整同期 arXiv 撞题证据见：[MemReadyBench 同期 arXiv 撞题审计](../reports/2026-09-03-memreadybench-concurrent-arxiv-audit.md)。
