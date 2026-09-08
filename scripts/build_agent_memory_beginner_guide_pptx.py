# -*- coding: utf-8 -*-
"""Build a beginner-facing Agent Memory survey deck in the 20260321 style.

Run from the repository root:

    $env:PYTHONPATH='.tmp/pptx_native_py38'
    D:\Python38\python.exe scripts/build_agent_memory_beginner_guide_pptx.py
"""

from __future__ import annotations

from pathlib import Path

import build_agent_memory_2025_2026_survey_pptx as deck


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "slides" / "20260321.pptx"
OUT = ROOT / "docs" / "slides" / "2026-09-08-agent-memory-beginner-guide.pptx"
ui = deck.ui


def body(prs, title, citation=None):
    return deck.body(prs, title, citation)


def section(prs, title, subtitle=""):
    return deck.section(prs, title, subtitle)


def card(slide, x, y, w, h, title, lines, accent=ui.NAVY, fill=ui.WHITE, title_size=17, body_size=12.5):
    return deck.card(slide, x, y, w, h, title, lines, accent, fill, title_size, body_size)


def banner(slide, text, y=6.20, color=ui.NAVY, fill=ui.BLUE_LIGHT, size=15):
    return deck.banner(slide, text, y, color, fill, size)


def table(slide, columns, rows, x, y, w, h, widths=None, font_size=10.5):
    return deck.table(slide, columns, rows, x, y, w, h, widths, font_size)


def flow_node(slide, x, y, w, h, title, subtitle, accent, fill):
    return deck.add_flow_node(slide, x, y, w, h, title, subtitle, accent, fill)


def arrow(slide, x, y, w=0.34):
    ui.add_text(slide, "→", x, y, w, 0.38, size=20, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)


def add_numbered_row(slide, y, number, title, text, accent, fill):
    ui.add_rect(slide, 0.78, y, 0.56, 0.56, fill=accent, line=accent, width=0, radius=True)
    ui.add_text(slide, number, 0.89, y + 0.12, 0.34, 0.26, size=17, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
    ui.add_rect(slide, 1.50, y, 11.00, 0.56, fill=fill, line=accent, width=0.9)
    ui.add_text(slide, title, 1.68, y + 0.11, 2.18, 0.28, size=14, color=accent, bold=True)
    ui.add_text(slide, text, 3.82, y + 0.11, 8.43, 0.30, size=13, color=ui.INK)


def main():
    if not SRC.exists():
        raise FileNotFoundError(SRC)

    prs = ui.Presentation(str(SRC))
    deck.clear_slides(prs)

    # 1. Cover
    slide = section(prs, "Agent Memory 入门综述", "定义、系统、方法、评测与发展趋势")
    ui.add_text(slide, "从“保存聊天记录”到“管理可持续的 Agent 状态”", 6.25, 4.30, 6.25, 0.44, size=17, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "面向初学者 · 文献核验截止 2026-09-08", 6.25, 5.03, 6.25, 0.30, size=11, color=ui.WHITE, align=ui.PP_ALIGN.CENTER)

    # 2. Learning map
    slide = body(prs, "看完这份综述，你应该能回答五个问题")
    items = [
        ("1", "为什么需要", "LLM 有上下文，为何还需要长期记忆？", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "记忆是什么", "哪些状态属于 Agent Memory，哪些只是 RAG？", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "系统怎么做", "如何形成、组织、检索、使用、更新与治理？", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "怎样评测", "从事实召回到工具行动，指标如何演化？", ui.ORANGE, ui.LIGHT),
        ("5", "未来往哪走", "学习型策略、在线交互、可信与成本为何重要？", ui.RED, ui.RED_LIGHT),
    ]
    for i, item in enumerate(items):
        add_numbered_row(slide, 1.22 + i * 1.00, *item)
    banner(slide, "主线：Why → What → How → Evaluation → Future", 6.32, ui.NAVY, ui.WHITE, 14)

    # 3. Stateless problem
    slide = body(prs, "为什么普通 LLM 不等于有记忆的 Agent")
    card(slide, 0.72, 1.16, 3.40, 4.50, "Session A：过去", ["用户：我对花生过敏", "模型：收到", "会话结束后，信息可能离开当前上下文"], ui.NAVY, ui.BLUE_LIGHT, 16, 14)
    arrow(slide, 4.27, 3.02, 0.52)
    card(slide, 4.92, 1.16, 3.40, 4.50, "Session B：未来", ["用户：帮我订晚餐", "当前问题没有再次说明过敏信息", "Agent 仍需恢复并使用历史约束"], ui.TEAL, ui.TEAL_LIGHT, 16, 14)
    arrow(slide, 8.46, 3.02, 0.52)
    card(slide, 9.10, 1.16, 3.50, 4.50, "真正的挑战", ["写入：值得长期保存吗？", "读取：现在仍有效吗？", "行动：证据足够下单吗？", "更新：新信息与旧信息冲突怎么办？"], ui.RED, ui.RED_LIGHT, 16, 13.2)
    banner(slide, "上下文解决“现在看见什么”；Memory 解决“历史怎样成为未来可用状态”。", 6.02, ui.NAVY, ui.WHITE, 15)

    # 4. Definition
    slide = body(prs, "Agent Memory 的工作定义", "Hu et al., Memory in the Age of AI Agents, arXiv:2512.13564.")
    ui.add_rect(slide, 0.82, 1.10, 11.70, 1.28, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.4)
    ui.add_text(slide, "Agent Memory 是由历史交互形成、跨当前上下文或会话持续存在，并在未来推理、规划和行动中被选择性读写与更新的状态。", 1.12, 1.45, 11.08, 0.52, size=20, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)
    card(slide, 0.82, 2.78, 3.55, 2.68, "持久性 Persistence", ["跨 turn / session / task 保留", "不只依赖当前 prompt", "状态可以有版本和生命周期"], ui.NAVY, ui.BLUE_LIGHT, 16, 13.5)
    card(slide, 4.88, 2.78, 3.55, 2.68, "能动性 Agency", ["决定写、读、更新与遗忘", "规则、LLM 或 learned policy", "可主动验证或抑制记忆"], ui.TEAL, ui.TEAL_LIGHT, 16, 13.5)
    card(slide, 8.94, 2.78, 3.55, 2.68, "行为后果 Consequence", ["改变回答、计划和工具调用", "影响未来状态与经验", "正确与错误都可能累积"], ui.ORANGE, ui.LIGHT, 16, 13.5)
    banner(slide, "数据库里有历史文本，不自动等于 Agent 拥有了可用的长期记忆。", 5.92, ui.NAVY, ui.WHITE, 15)

    # 5. Core entities
    slide = body(prs, "四个基本对象：Item、State、System、Policy")
    concepts = [
        ("Memory item", "一条可寻址单元", "事实、事件、经验、技能", ui.NAVY, ui.BLUE_LIGHT),
        ("Memory state", "某时刻的有效状态", "条目 + 时间 + 来源 + 版本", ui.TEAL, ui.TEAL_LIGHT),
        ("Memory system", "生命周期后端", "写入、组织、检索、更新", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Memory policy", "管理决策策略", "何时写、用、验、忘", ui.ORANGE, ui.LIGHT),
    ]
    for i, (title, subtitle, example, accent, fill) in enumerate(concepts):
        x = 0.68 + i * 3.13
        flow_node(slide, x, 1.50, 2.77, 2.40, title, f"{subtitle}\n\n{example}", accent, fill)
        if i < 3:
            arrow(slide, x + 2.81, 2.47, 0.28)
    ui.add_text(slide, "Mₜ = U(Mₜ₋₁, Hₜ; πᴹ)", 3.76, 4.46, 5.82, 0.60, size=25, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
    ui.add_text(slide, "历史 H 经过记忆策略 πᴹ 更新为下一时刻的持久状态 M", 2.70, 5.12, 7.95, 0.38, size=15, color=ui.MUTED, align=ui.PP_ALIGN.CENTER)
    banner(slide, "研究对象从“存了哪些文本”扩展为“状态怎样形成、变化并控制行为”。", 5.82, ui.NAVY, ui.WHITE, 15)

    # 6. Boundaries
    slide = body(prs, "不要混淆：Memory、RAG、长上下文与上下文工程")
    rows = [
        ["长上下文", "当前 token 序列", "单次调用", "否", "读得更多"],
        ["RAG", "外部文档库", "单次任务", "通常否", "找外部知识"],
        ["Agentic RAG", "主动搜索过程", "多步任务", "可选", "规划检索"],
        ["Context Engineering", "当前上下文配置", "当前任务", "临时", "编排资源"],
        ["Agent Memory", "历史形成的状态", "跨会话/任务", "是", "持续学习与行动"],
        ["LLM Memory", "参数、激活、KV", "推理到模型生命周期", "视机制", "容量与效率"],
    ]
    table(slide, ["概念", "核心对象", "时间尺度", "持续更新", "主要目标"], rows, 0.62, 1.16, 12.10, 4.85, [1.78, 2.52, 2.26, 1.54, 4.00], 10.8)
    banner(slide, "判断题：删除当前 query 后，信息是否仍因过去交互而存在并继续演化？", 6.18, ui.NAVY, ui.BLUE_LIGHT, 15)

    section(prs, "Memory 里有什么？", "类型、形式与生命周期")

    # 8. Functional types
    slide = body(prs, "按功能分类：Agent 到底记住什么")
    types = [
        ("事实 / 语义", "用户事实、偏好、环境关系", "是什么", ui.NAVY, ui.BLUE_LIGHT),
        ("情景", "带时间、参与者和结果的经历", "发生过什么", ui.TEAL, ui.TEAL_LIGHT),
        ("经验 / 反思", "失败教训、注意事项、策略", "以后如何改进", ui.PURPLE, ui.PURPLE_LIGHT),
        ("程序 / 技能", "计划、工具链、代码、工作流", "如何做", ui.ORANGE, ui.LIGHT),
        ("工作记忆", "当前任务中间状态与目标", "现在做到哪里", ui.RED, ui.RED_LIGHT),
        ("前瞻记忆", "未来条件触发的延迟意图", "何时再做", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (title, desc, q, accent, fill) in enumerate(types):
        row, col = divmod(i, 3)
        x, y = 0.72 + col * 4.18, 1.20 + row * 2.36
        card(slide, x, y, 3.78, 1.92, title, [desc, f"回答：{q}"], accent, fill, 16, 13)
    banner(slide, "同一系统常同时保存事实、经历和技能；不同类型需要不同更新与评测。", 6.04, ui.NAVY, ui.WHITE, 14)

    # 9. Forms
    slide = body(prs, "按形式分类：记忆以什么结构存在")
    rows = [
        ["原始轨迹", "完整对话、工具日志", "保真、可审计", "成本高、噪声多"],
        ["文本条目", "事实、摘要、反思", "可读、易接入", "结构和限定条件易丢"],
        ["向量索引", "Embedding + Top-k", "成熟、快速", "相似不等于适用"],
        ["结构 / 图", "JSON、事件图、时间图", "关系清晰、可追踪", "建图和维护复杂"],
        ["层次记忆", "短期 / 中期 / 长期", "效率与范围平衡", "跨层一致性困难"],
        ["参数 / 隐式", "微调、LoRA、memory token", "调用紧凑", "难解释、删除与更新"],
        ["混合系统", "原文 + 索引 + 图 + 技能", "能力完整", "故障归因更难"],
    ]
    table(slide, ["形式", "典型实现", "优势", "主要局限"], rows, 0.60, 1.12, 12.12, 5.22, [1.80, 3.02, 3.15, 4.15], 10.4)
    banner(slide, "结构没有绝对优劣：任务所需关系、更新频率和审计要求决定选择。", 6.34, ui.NAVY, ui.WHITE, 14)

    # 10. Lifecycle
    slide = body(prs, "完整生命周期：从历史事件到未来行为")
    nodes = [
        ("Observe", "用户 / 工具 / 环境", ui.NAVY, ui.BLUE_LIGHT),
        ("Write", "抽取 / 写入 / 反思", ui.TEAL, ui.TEAL_LIGHT),
        ("Organize", "索引 / 链接 / 版本", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Retrieve", "候选 / 排序 / 停止", ui.ORANGE, ui.LIGHT),
        ("Use", "回答 / 计划 / 行动", ui.RED, ui.RED_LIGHT),
        ("Evolve", "更新 / 遗忘 / 治理", ui.GREEN, ui.GREEN_LIGHT),
    ]
    x0, y, w, h, gap = 0.46, 2.05, 1.82, 2.18, 0.30
    for i, (title, subtitle, accent, fill) in enumerate(nodes):
        x = x0 + i * (w + gap)
        flow_node(slide, x, y, w, h, title, subtitle, accent, fill)
        if i < len(nodes) - 1:
            arrow(slide, x + w + 0.01, 2.90, gap - 0.02)
    ui.add_text(slide, "历史交互 H₁:ₜ", 0.62, 1.30, 2.12, 0.34, size=15, color=ui.MUTED, bold=True)
    ui.add_text(slide, "持续状态 Mₜ", 5.58, 1.30, 2.12, 0.34, size=15, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "未来行为与反馈", 10.18, 1.30, 2.40, 0.34, size=15, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.RIGHT)
    banner(slide, "任一阶段都可能失败，最终准确率无法告诉我们错误发生在哪里。", 5.08, ui.NAVY, ui.BLUE_LIGHT, 15)

    # 11. Minimal architecture
    slide = body(prs, "一套最小可运行的 Memory Agent")
    steps = [
        ("1", "事件日志", "对话 / 动作 / 反馈", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "写入器", "选择 + 结构化", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "记忆库", "文本 / 向量 / 图", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "检索器", "召回 + 重排", ui.ORANGE, ui.LIGHT),
        ("5", "Agent", "推理 + 工具行动", ui.RED, ui.RED_LIGHT),
    ]
    for i, (num, title, txt, accent, fill) in enumerate(steps):
        x = 0.55 + i * 2.52
        ui.add_step(slide, x, 1.52, 2.18, 2.18, num, title, txt, accent=accent, fill=fill)
        if i < 4:
            arrow(slide, x + 2.19, 2.42, 0.30)
    ui.add_line(slide, 11.78, 4.18, 1.58, 4.18, color=ui.MUTED, width=1.4)
    ui.add_text(slide, "反馈与更新", 5.32, 3.90, 2.70, 0.40, size=15, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    card(slide, 1.06, 4.54, 11.18, 1.14, "最低日志要求", ["写入前事件  |  写入后状态  |  检索候选  |  可见证据  |  最终行动  |  环境反馈  |  更新记录"], ui.NAVY, ui.WHITE, 15, 13)
    banner(slide, "先把生命周期记录清楚，再讨论复杂模型；否则无法区分写入、检索和使用错误。", 6.04, ui.NAVY, ui.WHITE, 14)

    section(prs, "方法如何演化？", "从存储记录到学习 Memory policy")

    # 13. Timeline
    slide = body(prs, "发展时间线：四个阶段")
    yline = 3.36
    ui.add_line(slide, 0.98, yline, 12.30, yline, color=ui.INK, width=1.8)
    years = [
        (1.22, "2023", "外部记忆成型", "Generative Agents\nReflexion / Voyager\nMemGPT", ui.NAVY, ui.BLUE_LIGHT),
        (4.10, "2024", "长期对话评测", "LoCoMo\n多会话与时间推理\n图检索", ui.TEAL, ui.TEAL_LIGHT),
        (7.00, "2025", "组织与经验复用", "LongMemEval / A-MEM\nAWM / MemoryOS\n效率与结构", ui.PURPLE, ui.PURPLE_LIGHT),
        (9.90, "2026", "策略、行动、治理", "AgeMem / Memory-R1\nStratMem / Mem2Act\n可信与成本", ui.ORANGE, ui.LIGHT),
    ]
    for x, year, title, examples, accent, fill in years:
        ui.add_rect(slide, x, yline - 0.13, 0.26, 0.26, fill=ui.WHITE, line=accent, width=2.0, radius=True)
        ui.add_text(slide, year, x - 0.42, yline + 0.30, 1.10, 0.30, size=15, color=accent, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
        card(slide, x - 0.78, 1.20, 2.20, 1.76, title, examples.split("\n"), accent, fill, 14, 10.8)
    banner(slide, "主线：Storage → Reflection → Experience → Learned control and governance", 5.12, ui.NAVY, ui.WHITE, 15)

    # 14. Foundation
    slide = body(prs, "2023：四种奠基思路", "Park et al.; Shinn et al.; Wang et al.; Packer et al., 2023.")
    card(slide, 0.70, 1.18, 2.82, 4.58, "Generative Agents", ["保存自然语言经历", "按相关性、时近性和重要性检索", "反思形成高层认知", "记忆服务计划和社会行为"], ui.NAVY, ui.BLUE_LIGHT, 15, 12.2)
    card(slide, 3.73, 1.18, 2.82, 4.58, "Reflexion", ["把环境反馈转为语言反思", "写入 episodic buffer", "不更新模型参数", "跨 trial 改进行为"], ui.TEAL, ui.TEAL_LIGHT, 15, 12.2)
    card(slide, 6.76, 1.18, 2.82, 4.58, "Voyager", ["开放式具身探索", "保存可执行技能代码", "组合和复用技能", "以环境反馈持续改进"], ui.PURPLE, ui.PURPLE_LIGHT, 15, 12.2)
    card(slide, 9.79, 1.18, 2.82, 4.58, "MemGPT", ["类操作系统分层内存", "有限上下文与外存调度", "用 interrupt 管理控制流", "支持跨会话对话"], ui.ORANGE, ui.LIGHT, 15, 12.2)
    banner(slide, "共同贡献：让 Agent 能在模型参数不变的情况下积累跨任务状态与经验。", 6.02, ui.NAVY, ui.WHITE, 14)

    # 15. 2024-2025
    slide = body(prs, "2024–2025：从“能否找回”走向“如何组织与复用”", "LoCoMo: ACL 2024 Long; LongMemEval: ICLR 2025; A-MEM: NeurIPS 2025; AWM: ICML 2025.")
    card(slide, 0.72, 1.16, 3.78, 4.60, "评测基础", ["LoCoMo：超长多会话对话", "LongMemEval：抽取、跨会话、时间、更新、拒答", "问题从短对话扩大到持续交互"], ui.NAVY, ui.BLUE_LIGHT, 16, 13)
    card(slide, 4.78, 1.16, 3.78, 4.60, "动态组织", ["A-MEM：动态索引和链接", "新记忆可更新旧条目属性", "从平坦 Top-k 走向关联网络"], ui.TEAL, ui.TEAL_LIGHT, 16, 13)
    card(slide, 8.84, 1.16, 3.78, 4.60, "经验复用", ["AWM：从轨迹归纳 workflow", "MemoryOS：多层存储与管理", "从“发生了什么”走向“以后怎么做”"], ui.PURPLE, ui.PURPLE_LIGHT, 16, 13)
    banner(slide, "这一阶段的关键词：long-term evaluation、organization、workflow、efficiency。", 6.02, ui.NAVY, ui.WHITE, 14)

    # 16. 2026
    slide = body(prs, "2026：Memory operation 成为可学习的 Agent 行为", "AgeMem and Memory-R1: ACL 2026 Long; LightMem: ACL 2026 Long.")
    ui.add_text(slide, "过去：固定规则", 0.88, 1.18, 2.32, 0.42, size=20, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    card(slide, 0.72, 1.78, 3.15, 3.92, "Heuristic Pipeline", ["固定摘要", "固定 Top-k", "TTL / LRU", "统一写入与更新模板"], ui.MUTED, ui.LIGHT, 16, 14)
    arrow(slide, 4.05, 3.24, 0.56)
    ui.add_text(slide, "现在：自主操作", 4.80, 1.18, 3.20, 0.42, size=20, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    card(slide, 4.72, 1.78, 3.42, 3.92, "Agentic Operations", ["STORE / RETRIEVE", "UPDATE / DELETE", "SUMMARIZE / NOOP", "作为工具动作进入策略"], ui.NAVY, ui.BLUE_LIGHT, 16, 14)
    arrow(slide, 8.33, 3.24, 0.56)
    ui.add_text(slide, "进一步：学习策略", 9.08, 1.18, 3.42, 0.42, size=20, color=ui.TEAL, bold=True, align=ui.PP_ALIGN.CENTER)
    card(slide, 8.96, 1.78, 3.64, 3.92, "Learned Memory Policy", ["SFT / preference learning", "PPO / GRPO", "结果 + 步骤 + 成本奖励", "学习何时及如何管理"], ui.TEAL, ui.TEAL_LIGHT, 16, 13.5)
    banner(slide, "关键变化：Memory 不再只是后端组件，而成为 Agent policy 的动作空间。", 6.02, ui.NAVY, ui.WHITE, 15)

    # 17. Architecture families
    slide = body(prs, "六类常见架构：选择取决于任务，而非流行度")
    rows = [
        ["Full history", "保留全部或最近历史", "简单、保真", "成本与干扰"],
        ["Retrieval", "切分 + 索引 + Top-k", "成熟、快速", "相似不等于适用"],
        ["Hierarchical", "近期细节 + 长期摘要", "平衡范围和效率", "压缩失真"],
        ["Graph", "实体 / 事件 / 时间关系", "多跳与追踪", "构建维护复杂"],
        ["Experience / Skill", "反思、案例、工作流", "跨任务复用", "负迁移"],
        ["Parametric / Latent", "参数或隐式状态", "调用紧凑", "难审计与删除"],
        ["Hybrid", "原文 + 索引 + 图 + 技能", "能力完整", "故障归因困难"],
    ]
    table(slide, ["家族", "做法", "优势", "核心风险"], rows, 0.62, 1.12, 12.10, 5.26, [2.15, 3.25, 2.95, 3.75], 10.3)
    banner(slide, "现代系统通常是混合架构；真正困难的是跨组件一致性与可诊断性。", 6.34, ui.NAVY, ui.WHITE, 14)

    # 18. Write / organize
    slide = body(prs, "Formation 与 Organization：怎样把历史变成记忆")
    card(slide, 0.72, 1.12, 3.70, 4.78, "写入策略", ["全量保存", "事实 / 偏好抽取", "摘要与反思", "novelty / importance / utility", "ADD / UPDATE / DELETE / NOOP"], ui.NAVY, ui.BLUE_LIGHT, 16, 13.2)
    card(slide, 4.82, 1.12, 3.70, 4.78, "组织与元数据", ["Embedding、关键词与标签", "实体、时间与事件关系", "来源 provenance", "权限 authority / scope", "版本与 supersession"], ui.TEAL, ui.TEAL_LIGHT, 16, 13.2)
    card(slide, 8.92, 1.12, 3.70, 4.78, "主要失败", ["漏写重要信息", "把推测写成事实", "临时要求变成永久偏好", "摘要丢失否定和例外", "错误链接与过度抽象"], ui.RED, ui.RED_LIGHT, 16, 13.2)
    banner(slide, "写入质量决定后续上限：不存在或被错误抽象的证据，检索器无法恢复。", 6.08, ui.NAVY, ui.WHITE, 14)

    # 19. Retrieve / use
    slide = body(prs, "Retrieval 与 Use：找到了，不等于会正确使用")
    nodes = [
        ("Query", "当前目标 + 状态", ui.NAVY, ui.BLUE_LIGHT),
        ("Candidate", "关键词 / 向量 / 图", ui.TEAL, ui.TEAL_LIGHT),
        ("Rerank", "相关 + 时效 + 适用", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Control", "用 / 验 / 问 / 忽略", ui.ORANGE, ui.LIGHT),
        ("Action", "回答 / 工具 / 拒绝", ui.RED, ui.RED_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(nodes):
        x = 0.62 + i * 2.52
        flow_node(slide, x, 1.62, 2.18, 2.10, title, txt, accent, fill)
        if i < 4:
            arrow(slide, x + 2.20, 2.42, 0.28)
    card(slide, 1.02, 4.20, 5.42, 1.40, "检索失败", ["正确记忆未进入候选；旧版本或相似噪声排在前面"], ui.NAVY, ui.BLUE_LIGHT, 15, 12.5)
    card(slide, 6.88, 4.20, 5.42, 1.40, "使用失败", ["正确证据已可见，但 Agent 忽略、误解或过早行动"], ui.RED, ui.RED_LIGHT, 15, 12.5)
    banner(slide, "必须分别记录 retrieved evidence 与实际行为，才能区分 recall 和 utilization。", 6.04, ui.NAVY, ui.WHITE, 14)

    # 20. Evolution / governance
    slide = body(prs, "Evolution 与 Governance：让记忆长期可用且可控")
    card(slide, 0.70, 1.14, 3.82, 4.62, "状态演化", ["覆盖旧值", "保留全部版本", "记录 supersede 关系", "冲突未决时继续验证", "压缩、合并与遗忘"], ui.NAVY, ui.BLUE_LIGHT, 16, 13)
    card(slide, 4.76, 1.14, 3.82, 4.62, "治理字段", ["来源：谁说的？", "权威：能否支持该动作？", "作用域：适用于谁和哪里？", "时效：现在仍有效吗？", "审计：影响了哪个行为？"], ui.TEAL, ui.TEAL_LIGHT, 16, 13)
    card(slide, 8.82, 1.14, 3.82, 4.62, "长期风险", ["旧值残留与冲突", "来源在摘要中消失", "用户或项目串扰", "错误经验反复重放", "敏感信息无法撤销"], ui.RED, ui.RED_LIGHT, 16, 13)
    banner(slide, "“过去真实”不等于“现在有效”；“曾被写入”也不等于“有权影响行动”。", 6.02, ui.NAVY, ui.WHITE, 15)

    section(prs, "怎样评价 Memory？", "从事实召回到行动、成本与可信")

    # 22. Benchmark evolution
    slide = body(prs, "Benchmark 演化：评价对象不断向后延伸")
    stages = [
        ("1", "长期回忆", "过去信息能否找回", "LoCoMo\nLongMemEval", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "状态演化", "时间、更新与遗忘", "Persona / state\nTTL / LRU", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "战略使用", "该不该用、用多少", "StratMem\nSteeM", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "工具行动", "选工具并恢复参数", "Mem2Act\nMemoryArena", ui.ORANGE, ui.LIGHT),
        ("5", "纵向治理", "成本、来源、修复与副作用", "Lifecycle\nSafety", ui.RED, ui.RED_LIGHT),
    ]
    for i, (num, title, desc, ex, accent, fill) in enumerate(stages):
        x = 0.48 + i * 2.55
        ui.add_step(slide, x, 1.38, 2.20, 3.82, num, title, f"{desc}\n\n{ex}", accent=accent, fill=fill)
        if i < 4:
            arrow(slide, x + 2.21, 3.02, 0.31)
    banner(slide, "问题从“记住了吗”变成“记忆是否恰当地改变了当前与未来行为”。", 5.72, ui.NAVY, ui.WHITE, 15)

    # 23. Benchmark table
    slide = body(prs, "代表性 Benchmark：各自测什么")
    rows = [
        ["LoCoMo", "ACL 2024", "多会话回忆、时间、总结", "偏问答 / 生成"],
        ["LongMemEval", "ICLR 2025", "抽取、跨会话、更新、拒答", "非完整行动闭环"],
        ["MemoryAgentBench", "ICLR 2026", "检索、TTL、LRU、遗忘", "以 chunk 为主"],
        ["AMemGym", "ICLR 2026", "on-policy write/read/use", "任务域与用户模拟受限"],
        ["StratMem-Bench", "ACL 2026", "必须 / 可选 / 无关记忆", "候选已给定"],
        ["Mem2ActBench", "ACL 2026", "工具选择、参数落地", "主要是离线行动生成"],
        ["MemoryArena", "arXiv 2026", "记忆获取与环境行动", "预印本，协议演化中"],
    ]
    table(slide, ["Benchmark", "出处", "主要能力", "边界"], rows, 0.62, 1.12, 12.10, 5.30, [2.35, 1.85, 4.45, 3.45], 10.2)
    banner(slide, "没有一个分数能代表全部 Memory 能力；应按任务所需生命周期选择评测。", 6.36, ui.NAVY, ui.WHITE, 14)

    # 24. Metric stack
    slide = body(prs, "六层指标：不要只看最终准确率")
    metrics = [
        ("内容", "写入 P/R、事实一致性、来源保留", ui.NAVY, ui.BLUE_LIGHT),
        ("检索", "Recall@k、MRR、证据覆盖、预算", ui.TEAL, ui.TEAL_LIGHT),
        ("使用", "答案、工具、参数、证据引用", ui.PURPLE, ui.PURPLE_LIGHT),
        ("演化", "更新、失效、冲突、未来复发", ui.ORANGE, ui.LIGHT),
        ("效率", "Token、调用、延迟、存储增长", ui.RED, ui.RED_LIGHT),
        ("治理", "权限、泄露、污染、审计、撤销", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(metrics):
        row, col = divmod(i, 3)
        x, y = 0.72 + col * 4.18, 1.18 + row * 2.28
        card(slide, x, y, 3.78, 1.82, title, [txt], accent, fill, 16, 13)
    banner(slide, "最终答案错误可能来自写入、检索、使用或更新；指标必须支持阶段归因。", 5.92, ui.NAVY, ui.WHITE, 14)

    # 25. Failure modes
    slide = body(prs, "常见失败模式：Memory 也会制造错误")
    failures = [
        ("漏写 / 幻觉写入", "重要信息未保存，或推测被写成事实", ui.NAVY, ui.BLUE_LIGHT),
        ("检索错位", "相似但过期、跨用户或不同条件的经验抢占", ui.TEAL, ui.TEAL_LIGHT),
        ("召回后不用", "证据可见，但模型仍按旧计划或参数先验行动", ui.PURPLE, ui.PURPLE_LIGHT),
        ("过度使用 / 锚定", "旧经验压制新证据和探索分支", ui.ORANGE, ui.LIGHT),
        ("压缩与版本失真", "否定、例外、来源、时间和权限被丢失", ui.RED, ui.RED_LIGHT),
        ("错误传播", "一次错误被保存并在未来相似任务中重放", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(failures):
        row, col = divmod(i, 2)
        x, y = 0.78 + col * 6.15, 1.12 + row * 1.68
        card(slide, x, y, 5.68, 1.34, title, [txt], accent, fill, 15, 12.2)
    banner(slide, "Memory 的价值来自跨时间复用；它的风险也会跨时间累积。", 6.20, ui.NAVY, ui.WHITE, 15)

    # 26. More memory
    slide = body(prs, "更多 Memory 为什么不一定更好", "Huang et al., ACL 2026; Xiong et al., ACL 2026.")
    ui.add_text(slide, "长期净效用", 0.90, 1.15, 2.10, 0.42, size=22, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_rect(slide, 0.72, 1.82, 3.72, 3.84, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.2)
    ui.add_text(slide, "U(M) = 任务收益\n− 成本\n− 干扰\n− 风险", 1.28, 2.48, 2.62, 2.34, size=24, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)
    arrow(slide, 4.66, 3.16, 0.70)
    card(slide, 5.62, 1.28, 3.08, 4.34, "Memory 太少", ["关键信息漏失", "重复探索", "个性化和连续性不足", "历史反馈无法复用"], ui.TEAL, ui.TEAL_LIGHT, 16, 13.2)
    card(slide, 9.20, 1.28, 3.08, 4.34, "Memory 太多", ["检索和 token 成本上升", "旧版本与噪声抢占", "经验锚定和探索收缩", "隐私与污染面扩大"], ui.RED, ui.RED_LIGHT, 16, 13.2)
    banner(slide, "现代目标不是“存得最多”，而是在任务、成本和风险之间获得更高净效用。", 6.02, ui.NAVY, ui.WHITE, 15)

    # 27. Fair evaluation
    slide = body(prs, "公平比较 Memory system，需要控制什么")
    controls = [
        ("Backbone", "固定基础模型与解码参数", ui.NAVY, ui.BLUE_LIGHT),
        ("Ingestion", "报告切分、摘要和原文保留", ui.TEAL, ui.TEAL_LIGHT),
        ("Retrieval", "配平 Top-k、token 与调用预算", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Exposure", "记录真正进入上下文的证据", ui.ORANGE, ui.LIGHT),
        ("Evaluator", "工具用程序评分，文本再用 judge", ui.RED, ui.RED_LIGHT),
        ("Unit", "按用户 / 事件 / family / episode 统计", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(controls):
        add_numbered_row(slide, 1.06 + i * 0.84, str(i + 1), title, txt, accent, fill)
    banner(slide, "Embedding、chunk、Top-k 和 judge 的差异，可能比方法名称更影响排行榜。", 6.22, ui.NAVY, ui.WHITE, 14)

    section(prs, "未来往哪里走？", "方法、评测与系统目标的共同变化")

    # 29. Trends
    slide = body(prs, "六条发展趋势")
    trends = [
        ("自主操作", "固定 pipeline → Agent 调用 memory tools", ui.NAVY, ui.BLUE_LIGHT),
        ("学习策略", "Prompt / rule → SFT / preference / RL", ui.TEAL, ui.TEAL_LIGHT),
        ("经验与技能", "记事实 → 复用 workflow 和可执行技能", ui.PURPLE, ui.PURPLE_LIGHT),
        ("条件化使用", "Always-on/off → 按状态控制依赖", ui.ORANGE, ui.LIGHT),
        ("在线评测", "固定历史 → 行为改变未来 Memory", ui.RED, ui.RED_LIGHT),
        ("可信与成本", "单一准确率 → 多目标长期净效用", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(trends):
        row, col = divmod(i, 2)
        x, y = 0.72 + col * 6.20, 1.12 + row * 1.70
        card(slide, x, y, 5.72, 1.36, title, [txt], accent, fill, 15, 12.3)
    banner(slide, "竞争焦点正在从“记忆容量”转向“记忆策略是否可靠、经济且可治理”。", 6.22, ui.NAVY, ui.WHITE, 15)

    # 30. Open questions
    slide = body(prs, "仍然开放的研究问题")
    left = [
        "写入时看不到未来任务，如何估计长期价值？",
        "何时依赖经验，何时保留探索并重新验证？",
        "多条记忆共同支持行动时，如何评价组合贡献？",
        "怎样保护低频但高后果的约束？",
    ]
    right = [
        "压缩后如何保留来源、时间、否定和权限？",
        "多 Agent 共享记忆时，如何隔离身份与责任？",
        "错误已经造成外部后果后，怎样最小化修复？",
        "排行榜对 chunk、embedding、预算和 judge 稳定吗？",
    ]
    card(slide, 0.72, 1.18, 5.72, 4.80, "学习与决策", left, ui.NAVY, ui.BLUE_LIGHT, 17, 13.2)
    card(slide, 6.88, 1.18, 5.72, 4.80, "可信与评测", right, ui.TEAL, ui.TEAL_LIGHT, 17, 13.2)
    banner(slide, "开放问题不等于新颖性主张：仍需核查同期工作并先做可证伪 pilot。", 6.18, ui.NAVY, ui.WHITE, 14)

    # 31. Start building
    slide = body(prs, "初学者如何搭一个最小实验")
    steps = [
        ("1", "定义事件", "用户 / 工具 / 环境统一 schema", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "做透明基线", "No-memory / Full-history / BM25", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "增加检索", "Dense + hybrid + reranker", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "记录全链路", "State / evidence / action / update", ui.ORANGE, ui.LIGHT),
        ("5", "定位瓶颈", "Write、retrieve、use 还是 evolve", ui.RED, ui.RED_LIGHT),
    ]
    for i, (num, title, txt, accent, fill) in enumerate(steps):
        x = 0.56 + i * 2.51
        ui.add_step(slide, x, 1.48, 2.17, 3.78, num, title, txt, accent=accent, fill=fill)
        if i < 4:
            arrow(slide, x + 2.18, 3.02, 0.30)
    banner(slide, "先建立可观察的系统，再训练模块；否则高分也无法解释 Memory 为什么有效。", 5.78, ui.NAVY, ui.WHITE, 15)

    # 32. Reading path
    slide = body(prs, "推荐阅读路径：四组论文建立完整认知")
    groups = [
        ("基础架构", "Generative Agents\nReflexion\nMemGPT", ui.NAVY, ui.BLUE_LIGHT),
        ("评测基础", "LoCoMo\nLongMemEval\nStratMem / Mem2Act", ui.TEAL, ui.TEAL_LIGHT),
        ("现代方法", "A-MEM\nAWM / MemoryOS\nAgeMem / Memory-R1", ui.PURPLE, ui.PURPLE_LIGHT),
        ("风险趋势", "SteeM\nExperience-Following\nMemory Surveys", ui.ORANGE, ui.LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(groups):
        x = 0.72 + i * 3.05
        card(slide, x, 1.38, 2.72, 3.92, title, txt.split("\n"), accent, fill, 16, 13)
        if i < 3:
            arrow(slide, x + 2.74, 3.02, 0.25)
    banner(slide, "阅读顺序：先理解系统对象，再看 Benchmark，最后看学习策略与治理。", 5.76, ui.NAVY, ui.WHITE, 15)

    # 33. Takeaways
    slide = body(prs, "总结：用五句话记住 Agent Memory")
    takeaways = [
        ("1", "定义", "由历史形成、跨会话持续、受策略管理并影响未来行为", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "系统", "形成、组织、检索、使用、更新和治理缺一不可", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "方法", "从存储与 Top-k 走向经验抽象和 learned memory policy", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "评测", "从事实召回走向行动、生命周期、成本和可信", ui.ORANGE, ui.LIGHT),
        ("5", "原则", "更多 Memory 不必然更好；长期净效用才是目标", ui.RED, ui.RED_LIGHT),
    ]
    for i, item in enumerate(takeaways):
        add_numbered_row(slide, 1.18 + i * 1.00, *item)
    banner(slide, "Memory 不只是存储组件，而是 Agent 的持续状态、学习介质和责任边界。", 6.32, ui.NAVY, ui.WHITE, 15)

    # 34-36. References
    slide = body(prs, "参考文献（一）：综述与奠基工作")
    ui.add_reference_columns(slide, [
        "Hu et al. Memory in the Age of AI Agents. arXiv:2512.13564.",
        "Zhang et al. Rethinking Memory in AI. arXiv:2505.00675.",
        "Luo et al. From Storage to Experience. ACL Findings 2026.",
        "Park et al. Generative Agents. UIST / arXiv 2023.",
        "Shinn et al. Reflexion. NeurIPS Main 2023.",
    ], [
        "Wang et al. Voyager. arXiv:2305.16291.",
        "Packer et al. MemGPT. arXiv:2310.08560.",
        "Maharana et al. LoCoMo. ACL Long 2024.",
        "Wu et al. LongMemEval. ICLR 2025.",
        "Tan et al. MemBench. ACL Findings 2025.",
    ])

    slide = body(prs, "参考文献（二）：代表性方法")
    ui.add_reference_columns(slide, [
        "Xu et al. A-MEM. NeurIPS Main 2025.",
        "Wang et al. Agent Workflow Memory. ICML 2025.",
        "Kang et al. MemoryOS. EMNLP Main 2025.",
        "Ong et al. THEANINE. NAACL Long 2025.",
        "Yu et al. Agentic Memory (AgeMem). ACL Long 2026.",
    ], [
        "Yan et al. Memory-R1. ACL Long 2026.",
        "Zhang et al. LightMem. ACL Long 2026.",
        "Jiang et al. MAGMA. ACL Long 2026.",
        "Wu et al. GAM. ACL Long 2026.",
        "Huang et al. Controllable Memory Usage. ACL Long 2026.",
    ])

    slide = body(prs, "参考文献（三）：评测、行动与风险")
    ui.add_reference_columns(slide, [
        "Wu et al. StratMem-Bench. ACL Long 2026.",
        "Shen et al. Mem2ActBench. ACL Long 2026.",
        "AMemGym. ICLR 2026.",
        "MemoryAgentBench. ICLR 2026.",
        "MemoryArena. arXiv:2602.16313.",
    ], [
        "Xiong et al. How Memory Management Impacts LLM Agents. ACL Long 2026.",
        "Locomo-Plus. ACL Long 2026.",
        "From Recall to Forgetting (Memora). ACL Findings 2026.",
        "Demystify the Role of Memory in MLE Agents. ACL Findings 2026.",
        "Branch-and-Browse. ACL Long 2026.",
    ])

    section(prs, "谢谢！", "Agent Memory：从历史记录到可持续、可行动、可治理的状态")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Saved {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
