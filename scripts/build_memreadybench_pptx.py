# -*- coding: utf-8 -*-
"""Build the canonical unified MemReadyBench proposal deck.

Run from the repository root with a Python environment that can import
python-pptx. The shared drawing helpers live in build_metamembench_pptx.py.
"""

from pathlib import Path

from build_metamembench_pptx import (
    BLUE,
    BLUE_LIGHT,
    FONT,
    FONT_EN,
    GRAY_LIGHT,
    GREEN,
    GREEN_LIGHT,
    INK,
    LIGHT,
    LINE,
    MUTED,
    ORANGE,
    ORANGE_LIGHT,
    PP_ALIGN,
    PURPLE,
    PURPLE_LIGHT,
    RED,
    RED_LIGHT,
    ROOT,
    SH,
    SW,
    TEAL,
    TEAL_LIGHT,
    WHITE,
    Inches,
    MSO_SHAPE,
    Presentation,
    add_badge,
    add_card,
    add_chevron,
    add_list,
    add_number_card,
    add_reference,
    add_table,
    add_text,
    line,
    rect,
    rgb,
)


OUT = ROOT / "docs" / "slides" / "2026-09-03-memreadybench-unified-research-proposal.pptx"


def add_header(slide, section, title, number, subtitle=None):
    rect(slide, 0, 0, SW, SH, fill=LIGHT, line=LIGHT)
    rect(slide, 0, 0, 0.14, SH, fill=TEAL, line=TEAL)
    add_text(slide, section.upper(), 0.54, 0.30, 4.2, 0.28, size=10, color=TEAL, bold=True, font=FONT_EN)
    add_text(slide, title, 0.54, 0.64, 12.0, 0.54, size=25, color=INK, bold=True)
    if subtitle:
        add_text(slide, subtitle, 0.56, 1.17, 11.9, 0.34, size=11, color=MUTED)
    line(slide, 0.54, 1.53, 12.22, 0.015, color=LINE)
    add_text(slide, f"{number:02d}", 12.20, 0.28, 0.52, 0.28, size=10, color=MUTED, bold=True, align=PP_ALIGN.RIGHT, font=FONT_EN)


def add_footer(slide, citation=None):
    if citation:
        add_text(slide, citation, 0.56, 7.14, 10.15, 0.20, size=8, color=MUTED, font=FONT_EN)
    add_text(slide, "MemReadyBench · Unified Proposal", 10.62, 7.14, 2.12, 0.20, size=8, color=MUTED, align=PP_ALIGN.RIGHT, font=FONT_EN)


def add_action(slide, x, y, label, accent, fill, width=2.05):
    rect(slide, x, y, width, 0.58, fill=fill, line=accent, radius=True, width=2)
    add_text(slide, label, x + 0.08, y + 0.16, width - 0.16, 0.25, size=11, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)


def add_axis_cell(slide, x, y, w, h, title, body, accent, fill):
    rect(slide, x, y, w, h, fill=fill, line=accent, radius=True)
    add_text(slide, title, x + 0.12, y + 0.11, w - 0.24, 0.25, size=11, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    add_text(slide, body, x + 0.12, y + 0.42, w - 0.24, h - 0.50, size=10, color=INK, bold=True, align=PP_ALIGN.CENTER)


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    blank = prs.slide_layouts[6]

    # 1 Cover
    slide = prs.slides.add_slide(blank)
    rect(slide, 0, 0, SW, SH, fill=LIGHT, line=LIGHT)
    rect(slide, 0, 0, 0.18, SH, fill=TEAL, line=TEAL)
    add_badge(slide, "CANONICAL RESEARCH PROPOSAL", 0.76, 0.62, 3.16, fill=TEAL_LIGHT, color=TEAL, size=10)
    add_text(slide, "MemReadyBench", 0.76, 1.28, 7.7, 0.68, size=35, color=INK, bold=True, font=FONT_EN)
    add_text(slide, "来源感知证据闭合与行动控制基准", 0.76, 2.05, 8.45, 0.54, size=25, color=INK, bold=True)
    add_text(slide, "Source-Aware Evidence Closure and Action Control for Persistent-Memory Agents", 0.78, 2.73, 8.9, 0.40, size=14, color=TEAL, bold=True, font=FONT_EN)
    rect(slide, 0.78, 3.53, 7.78, 1.54, fill=WHITE, line=LINE, radius=True)
    add_text(slide, "创新锚点", 1.05, 3.80, 1.32, 0.28, size=13, color=TEAL, bold=True)
    add_text(slide, "以 requirement-level readiness 为监控基础，\n以 source-aware evidence closure 为核心，以可执行结果形成验证闭环。", 2.36, 3.71, 5.78, 0.94, size=17, color=INK, bold=True, line_spacing=1.12)
    source_y = 5.63
    for i, (name, accent, fill) in enumerate([
        ("MEMORY", BLUE, BLUE_LIGHT),
        ("WORLD", PURPLE, PURPLE_LIGHT),
        ("USER", ORANGE, ORANGE_LIGHT),
        ("EXECUTION", GREEN, GREEN_LIGHT),
    ]):
        add_badge(slide, name, 0.78 + i * 1.68, source_y, 1.46, fill=fill, color=accent, size=10)
    rect(slide, 9.55, 0.55, 3.15, 6.25, fill=INK, line=INK, radius=True)
    add_text(slide, "一句话问题", 9.91, 1.01, 2.38, 0.30, size=13, color=TEAL_LIGHT, bold=True)
    add_text(slide, "Agent 能否识别尚未闭合的行动条件，找到它的可信来源，并在产生外部副作用前完成证据闭合？", 9.91, 1.62, 2.32, 2.14, size=22, color=WHITE, bold=True, line_spacing=1.13)
    line(slide, 9.91, 4.12, 2.25, 0.02, color=TEAL)
    add_text(slide, "Benchmark first\nMethod second", 9.91, 4.49, 2.30, 0.98, size=18, color=TEAL_LIGHT, bold=True, font=FONT_EN)
    add_text(slide, "2026-09-03", 9.91, 6.21, 2.30, 0.28, size=10, color=WHITE, font=FONT_EN)

    # 2 Unified positioning
    slide = prs.slides.add_slide(blank)
    add_header(slide, "01 / Positioning", "一个方案、一个形式体系、一个创新锚点", 2)
    add_card(slide, 0.70, 1.90, 3.64, 2.16, "研究基础：Monitoring", "判断当前 packet 是否已经覆盖全部行动要求，并识别 stale、conflict、irreducible 与 no-memory-needed 状态。", accent=TEAL, fill=TEAL_LIGHT, title_size=16, body_size=13)
    add_card(slide, 4.84, 1.90, 3.64, 2.16, "创新锚点：Source Routing", "指出缺失 requirement 的权威来源，并在 memory、world、user 与 unavailable 之间选择获取动作。", accent=BLUE, fill=BLUE_LIGHT, title_size=16, body_size=13)
    add_card(slide, 8.98, 1.90, 3.64, 2.16, "验证闭环：Execution", "用来源迁移反事实、动作翻转、闭合收敛、精确环境终态与 oracle ladder 证明诊断价值。", accent=ORANGE, fill=ORANGE_LIGHT, title_size=16, body_size=13)
    rect(slide, 0.70, 4.55, 11.92, 1.26, fill=INK, line=INK, radius=True)
    add_text(slide, "统一主张", 0.98, 4.87, 1.18, 0.26, size=13, color=TEAL_LIGHT, bold=True)
    add_text(slide, "Agent 不仅要知道“够不够”，还要知道“缺什么、去哪里找、何时闭合、何时可以行动”。", 2.20, 4.80, 9.95, 0.44, size=19, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    rect(slide, 1.44, 6.30, 10.45, 0.51, fill=WHITE, line=TEAL, radius=True, width=2)
    add_text(slide, "Research anchor: requirement-aware readiness + source-aware acquisition + executable closure", 1.72, 6.42, 9.90, 0.25, size=13, color=TEAL, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    add_footer(slide, "Monitoring is the foundation; source-aware evidence closure is the defensible technical anchor.")

    # 3 Why arXiv
    slide = prs.slides.add_slide(blank)
    add_header(slide, "02 / Audit", "为什么只看顶会会得出错误的新颖性判断", 3)
    add_card(slide, 0.72, 1.90, 3.54, 1.58, "公开优先权", "预印本一旦公开，问题、术语和实验设计就会进入审稿人的 prior art；target venue 不是 accepted，但不能忽略。", accent=RED, fill=RED_LIGHT, title_size=17, body_size=12)
    add_card(slide, 4.89, 1.90, 3.54, 1.58, "同期速度", "SafeCommit、Router-Mem、MCB 都在 2026 年 8 月出现；只扫描已接收列表会错过最直接竞争者。", accent=ORANGE, fill=ORANGE_LIGHT, title_size=17, body_size=12)
    add_card(slide, 9.06, 1.90, 3.54, 1.58, "审查单位", "不能只比标题；必须逐项核对 problem、action space、gold、counterfactual、execution 与 limitation。", accent=BLUE, fill=BLUE_LIGHT, title_size=17, body_size=12)
    add_text(slide, "本次检索的三层路径", 0.74, 3.92, 2.36, 0.32, size=14, color=INK, bold=True)
    steps = [
        ("01", "直接问题词", "memory sufficiency · safe commitment · verify/ask · abstention", TEAL),
        ("02", "邻近机制词", "tool necessity · clarification · provenance · memory skepticism", BLUE),
        ("03", "反向核验", "从最接近论文的 limitation 倒推仍未覆盖的交叉点", PURPLE),
    ]
    for i, (num, title, body, accent) in enumerate(steps):
        y = 4.40 + i * 0.72
        rect(slide, 0.74, y, 11.84, 0.56, fill=WHITE, line=accent, radius=True)
        add_text(slide, num, 0.91, y + 0.16, 0.46, 0.20, size=10, color=accent, bold=True, font=FONT_EN)
        add_text(slide, title, 1.52, y + 0.13, 1.72, 0.24, size=12, color=accent, bold=True)
        add_text(slide, body, 3.35, y + 0.12, 8.85, 0.27, size=11, color=INK, bold=True, font=FONT_EN)
    add_footer(slide, "Audit cutoff: 2026-09-03. Acceptance claims are separated from submitted/target status.")

    # 4 Timeline
    slide = prs.slides.add_slide(blank)
    add_header(slide, "02 / Audit", "2026 同期时间线：原问题空间在半年内迅速拥挤", 4)
    line(slide, 0.92, 4.00, 11.40, 0.06, color=INK)
    events = [
        (1.05, "JAN", "MetaMem\nAgentic UQ", TEAL, 2.35),
        (2.70, "FEB", "InfMem\nCalibrate-Then-Act", BLUE, 4.24),
        (4.52, "MAR–APR", "Oblivion · KnowU\nRSCB-MC", PURPLE, 2.25),
        (6.48, "MAY–JUN", "SURE-RAG · When2Tool\nCICL · ProvenanceGuard", ORANGE, 4.24),
        (8.70, "JUL", "MemSyco · AgentAbstain\nMemCon", RED, 2.25),
        (10.82, "AUG", "Router-Mem · SafeCommit\nMCB", GREEN, 4.24),
    ]
    for x, month, papers, accent, yy in events:
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(3.80), Inches(0.42), Inches(0.42))
        dot.fill.solid(); dot.fill.fore_color.rgb = rgb(accent); dot.line.color.rgb = rgb(accent)
        if yy < 3:
            line(slide, x + 0.20, 3.22, 0.02, 0.60, color=accent)
            rect(slide, x - 0.52, 2.03, 1.47, 1.15, fill=WHITE, line=accent, radius=True)
            add_text(slide, month, x - 0.40, 2.17, 1.23, 0.22, size=10, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
            add_text(slide, papers, x - 0.40, 2.49, 1.23, 0.47, size=9, color=INK, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
        else:
            line(slide, x + 0.20, 4.21, 0.02, 0.61, color=accent)
            rect(slide, x - 0.52, 4.82, 1.47, 1.15, fill=WHITE, line=accent, radius=True)
            add_text(slide, month, x - 0.40, 4.96, 1.23, 0.22, size=10, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
            add_text(slide, papers, x - 0.40, 5.28, 1.23, 0.47, size=9, color=INK, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    rect(slide, 1.50, 6.45, 10.22, 0.42, fill=RED_LIGHT, line=RED_LIGHT, radius=True)
    add_text(slide, "结论：会议接收列表是滞后视图；选题检查必须把最新 arXiv 当成正式竞争集合。", 1.76, 6.54, 9.70, 0.23, size=13, color=RED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Dates are first arXiv submission dates; venue labels are used only when explicitly confirmed.")

    # 5 SafeCommit
    slide = prs.slides.add_slide(blank)
    add_header(slide, "03 / Closest Work", "SafeCommit：最直接竞争者，也是必须正面承认的边界", 5)
    add_card(slide, 0.70, 1.88, 3.75, 2.20, "它已经做了什么", "在 stale、conflicting、incomplete、corrupted memory 下构造 plausible worlds；只有 proposed action 在保留世界中均安全才 commit，否则 probe 或 fallback。", accent=RED, fill=RED_LIGHT, title_size=17, body_size=12)
    add_card(slide, 4.79, 1.88, 3.75, 2.20, "与原方案重叠", "行动前充分性、premature commitment、风险-成本权衡、主动探测、确定性 simulator 与失败分解几乎全部重叠。", accent=ORANGE, fill=ORANGE_LIGHT, title_size=17, body_size=12)
    add_card(slide, 8.88, 1.88, 3.75, 2.20, "它明确留下什么", "作者把评测定位为 proof-of-concept：显式小 world set、固定动作与 safety map、确定性二值 probe，未系统测试真实 memory stack。", accent=TEAL, fill=TEAL_LIGHT, title_size=17, body_size=12)
    add_text(slide, "写作上必须改变的句子", 0.72, 4.49, 2.58, 0.31, size=14, color=INK, bold=True)
    rect(slide, 0.72, 4.92, 5.56, 1.25, fill=RED_LIGHT, line=RED, radius=True)
    add_text(slide, "不要写", 0.98, 5.17, 0.90, 0.24, size=12, color=RED, bold=True)
    add_text(slide, "We are the first to ask whether memory is sufficient to act.", 1.92, 5.12, 4.03, 0.46, size=14, color=INK, bold=True, font=FONT_EN)
    rect(slide, 6.55, 4.92, 6.08, 1.25, fill=TEAL_LIGHT, line=TEAL, radius=True)
    add_text(slide, "改成", 6.82, 5.17, 0.76, 0.24, size=12, color=TEAL, bold=True)
    add_text(slide, "We diagnose where unresolved action requirements can be authoritatively resolved and whether agents route acquisition correctly.", 7.65, 5.03, 4.68, 0.70, size=13, color=INK, bold=True, font=FONT_EN)
    add_footer(slide, "SafeCommit, arXiv:2608.04289, submitted 2026-08-04.")

    # 6 Collision matrix
    slide = prs.slides.add_slide(blank)
    add_header(slide, "03 / Closest Work", "竞争矩阵：每个旧卖点都已经有明确邻居", 6)
    headers = ["工作", "已有核心", "与本方向的关键边界"]
    rows = [
        ["SafeCommit", "commit / probe / fallback", "小型显式 worlds；非真实 memory stack 诊断"],
        ["MCB", "persist / local / verify / ask", "写入边界；不执行 acquisition 与下游 action"],
        ["AgentAbstain", "paired act/abstain + sandbox", "干预 instruction/tool/env，而非持久记忆来源"],
        ["Router-Mem / InfMem", "sufficiency router + memory control", "QA/效率；无 memory/world/user 来源路由"],
        ["SURE-RAG", "set-level evidence sufficiency", "RAG answer verification，不是外部副作用行动"],
        ["MemSyco-Bench", "memory skepticism / conflict", "聚焦迎合，不统一测缺失证据获取"],
        ["MemCon / Oblivion", "memory operation policy", "是待测方法，不提供统一 decision-point gold"],
    ]
    add_table(slide, 0.70, 1.85, [2.15, 4.05, 5.72], 0.64, headers, rows, body_size=10)
    rect(slide, 0.70, 6.98, 11.92, 0.03, fill=TEAL, line=TEAL)
    add_footer(slide, "Full matrix and status notes: docs/reports/2026-09-03-memreadybench-concurrent-arxiv-audit.md")

    # 7 Unified taxonomy
    slide = prs.slides.add_slide(blank)
    add_header(slide, "04 / Framework", "旧状态不再独立：统一映射到 Readiness × Source × Integrity", 7)
    headers = ["Benchmark slice", "Readiness", "Source / Integrity", "Expected control"]
    rows = [
        ["NO_MEMORY_NEEDED", "READY", "当前 observation 已闭合", "EXECUTE"],
        ["SUFFICIENT", "READY", "PACKET + FRESH", "EXECUTE"],
        ["RETRIEVABLE_MISSING", "NOT_READY", "PERSISTENT_MEMORY", "SEARCH_MEMORY"],
        ["WORLD_ONLY_MISSING", "NOT_READY", "WORLD", "VERIFY_WORLD"],
        ["USER_ONLY_MISSING", "NOT_READY", "USER", "ASK_USER"],
        ["STALE / CONFLICT", "CONFLICTED", "authority 决定来源", "SEARCH / VERIFY / ASK"],
        ["IRREDUCIBLE", "NOT_READY", "UNAVAILABLE", "ABSTAIN"],
    ]
    add_table(slide, 0.66, 1.84, [2.62, 1.60, 4.18, 3.54], 0.59, headers, rows, body_size=9)
    rect(slide, 0.78, 6.68, 11.68, 0.25, fill=TEAL_LIGHT, line=TEAL_LIGHT, radius=True)
    add_text(slide, "DISTRACTOR_HEAVY 不是独立 readiness：它继承原状态，并用于测试 irrelevant invariance。", 1.08, 6.70, 11.08, 0.19, size=10, color=TEAL, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    add_footer(slide, "The former six-state taxonomy becomes interpretable slices of one extensible factorization.")

    # 8 Question
    slide = prs.slides.add_slide(blank)
    add_header(slide, "04 / Gap", "统一研究问题：Source-Aware Evidence Closure and Action Control", 8)
    rect(slide, 0.78, 1.91, 11.80, 1.18, fill=INK, line=INK, radius=True)
    add_text(slide, "给定历史交互形成的持久记忆、当前工作 packet 和 world/user 接口，Agent 能否识别尚未闭合的行动条件，定位其权威来源，并在外部副作用发生前选择正确的信息获取或承诺动作？", 1.10, 2.16, 11.16, 0.64, size=18, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    prompts = [
        (0.78, "WHAT IS MISSING?", "哪个 requirement 尚未闭合？", BLUE, BLUE_LIGHT),
        (3.76, "WHERE IS IT?", "packet、memory、world、user 还是不可得？", PURPLE, PURPLE_LIGHT),
        (6.74, "WHAT NEXT?", "search、verify、ask、execute 还是 abstain？", ORANGE, ORANGE_LIGHT),
        (9.72, "DID IT CLOSE?", "获取后是否收敛到可验证行动？", GREEN, GREEN_LIGHT),
    ]
    for x, title, body, accent, fill in prompts:
        add_axis_cell(slide, x, 3.75, 2.56, 1.55, title, body, accent, fill)
    rect(slide, 1.32, 5.90, 10.70, 0.72, fill=WHITE, line=TEAL, radius=True, width=2)
    add_text(slide, "SafeCommit 判断 proposed action 是否可认证；MemReadyBench 评测真实 Agent 能否发现缺口、找到来源并达到可执行闭合。", 1.62, 6.10, 10.10, 0.32, size=14, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Recommended positioning sentence against SafeCommit.")

    # 9 Formalization
    slide = prs.slides.add_slide(blank)
    add_header(slide, "05 / Formalization", "两层状态、五个动作、四类 Gold", 9)
    add_text(slide, "行动准备度", 0.72, 1.91, 1.65, 0.30, size=14, color=INK, bold=True)
    for i, (name, accent, fill) in enumerate([
        ("READY", GREEN, GREEN_LIGHT), ("NOT_READY", ORANGE, ORANGE_LIGHT), ("CONFLICTED", RED, RED_LIGHT)
    ]):
        add_action(slide, 0.72 + i * 2.23, 2.36, name, accent, fill, 2.00)
    add_text(slide, "缺失证据来源", 0.72, 3.22, 1.85, 0.30, size=14, color=INK, bold=True)
    sources = [
        ("CURRENT_PACKET", TEAL, TEAL_LIGHT), ("PERSISTENT_MEMORY", BLUE, BLUE_LIGHT),
        ("WORLD", PURPLE, PURPLE_LIGHT), ("USER", ORANGE, ORANGE_LIGHT), ("UNAVAILABLE", RED, RED_LIGHT)
    ]
    for i, (name, accent, fill) in enumerate(sources):
        add_action(slide, 0.72 + i * 2.35, 3.67, name, accent, fill, 2.16)
    add_text(slide, "控制动作", 0.72, 4.52, 1.35, 0.30, size=14, color=INK, bold=True)
    actions = [
        ("SEARCH_MEMORY", BLUE, BLUE_LIGHT), ("VERIFY_WORLD", PURPLE, PURPLE_LIGHT),
        ("ASK_USER", ORANGE, ORANGE_LIGHT), ("EXECUTE", GREEN, GREEN_LIGHT), ("ABSTAIN", RED, RED_LIGHT)
    ]
    for i, (name, accent, fill) in enumerate(actions):
        add_action(slide, 0.72 + i * 2.35, 4.97, name, accent, fill, 2.16)
    rect(slide, 0.72, 5.92, 11.92, 0.79, fill=INK, line=INK, radius=True)
    golds = ["LATENT WORLD", "OBSERVABLE STATE", "ADMISSIBLE SET", "ORACLE ACTION + REGRET"]
    for i, gold in enumerate(golds):
        add_text(slide, gold, 0.95 + i * 2.90, 6.17, 2.55, 0.24, size=10, color=WHITE if i != 3 else TEAL_LIGHT, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
        if i < 3:
            add_chevron(slide, 3.55 + i * 2.90, 6.13, 0.22, 0.31, TEAL)
    add_footer(slide, "Separating latent truth from observable admissibility avoids impossible supervision.")

    # 10 factorial design
    slide = prs.slides.add_slide(blank)
    add_header(slide, "06 / Data Design", "核心数据资产：Source × Integrity 因子化反事实", 10)
    add_text(slide, "SOURCE LOCATION", 0.72, 1.87, 2.25, 0.30, size=12, color=TEAL, bold=True, font=FONT_EN)
    source_cells = [
        ("Packet", "EXECUTE", TEAL, TEAL_LIGHT), ("Memory", "SEARCH", BLUE, BLUE_LIGHT),
        ("World", "VERIFY", PURPLE, PURPLE_LIGHT), ("User", "ASK", ORANGE, ORANGE_LIGHT),
        ("Unavailable", "ABSTAIN", RED, RED_LIGHT), ("No need", "EXECUTE", GREEN, GREEN_LIGHT),
    ]
    for i, (title, body, accent, fill) in enumerate(source_cells):
        add_axis_cell(slide, 0.72 + i * 2.00, 2.28, 1.78, 1.05, title, body, accent, fill)
    add_text(slide, "INTEGRITY", 0.72, 3.77, 1.40, 0.30, size=12, color=RED, bold=True, font=FONT_EN)
    integrity = [
        ("Fresh", "当前有效", GREEN, GREEN_LIGHT), ("Stale", "旧值失效", ORANGE, ORANGE_LIGHT),
        ("Conflicting", "多源冲突", RED, RED_LIGHT), ("Poisoned", "诱导错误", PURPLE, PURPLE_LIGHT),
        ("Auth drift", "权限变化", BLUE, BLUE_LIGHT),
    ]
    for i, (title, body, accent, fill) in enumerate(integrity):
        add_axis_cell(slide, 0.72 + i * 2.40, 4.18, 2.15, 1.05, title, body, accent, fill)
    rect(slide, 0.72, 5.77, 11.92, 0.84, fill=INK, line=INK, radius=True)
    add_text(slide, "不是机械做全笛卡尔积：generator 只生成语义成立的组合。关键是同一 requirement 在来源或完整性变化后，正确动作发生可预测翻转。", 1.02, 5.99, 11.30, 0.38, size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "This factorial design replaces the original one-dimensional six-state taxonomy.")

    # 11 matched family
    slide = prs.slides.add_slide(blank)
    add_header(slide, "06 / Data Design", "Matched Family 示例：只移动“最终授权”的可信来源", 11)
    rect(slide, 0.70, 1.86, 11.94, 0.78, fill=WHITE, line=LINE, radius=True)
    add_text(slide, "共同目标", 0.96, 2.10, 1.04, 0.24, size=12, color=TEAL, bold=True)
    add_text(slide, "为用户预订满足历史偏好的航班；航班、日期、预算和最终购买授权必须全部闭合。", 2.06, 2.05, 10.14, 0.32, size=15, color=INK, bold=True)
    variants = [
        ("PACKET", "本轮明确授权", "EXECUTE", GREEN, GREEN_LIGHT),
        ("MEMORY", "历史会话含有效授权", "SEARCH_MEMORY", BLUE, BLUE_LIGHT),
        ("WORLD", "企业审批系统记录当前授权", "VERIFY_WORLD", PURPLE, PURPLE_LIGHT),
        ("USER", "只有用户能给一次性授权", "ASK_USER", ORANGE, ORANGE_LIGHT),
        ("UNAVAILABLE", "无人/无系统可确认", "ABSTAIN", RED, RED_LIGHT),
    ]
    for i, (source, condition, action, accent, fill) in enumerate(variants):
        y = 2.96 + i * 0.67
        rect(slide, 0.72, y, 11.90, 0.52, fill=fill, line=accent, radius=True)
        add_text(slide, source, 0.92, y + 0.14, 1.38, 0.21, size=10, color=accent, bold=True, font=FONT_EN)
        add_text(slide, condition, 2.42, y + 0.12, 5.65, 0.25, size=11, color=INK, bold=True)
        add_text(slide, action, 9.28, y + 0.13, 2.70, 0.22, size=10, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    rect(slide, 0.72, 6.50, 11.90, 0.30, fill=INK, line=INK, radius=True)
    add_text(slide, "ACTION FLIP：第一动作不同  →  CLOSURE CONVERGENCE：可解决版本最终预订结果相同", 1.05, 6.54, 11.22, 0.20, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    add_footer(slide, "The final outcome should converge only after the appropriate acquisition action succeeds.")

    # 12 Tracks
    slide = prs.slides.add_slide(blank)
    add_header(slide, "07 / Protocol", "三个 Track：从诊断到顺序获取，再到真实执行", 12)
    tracks = [
        (0.72, "TRACK A", "Readiness Diagnosis", "固定 packet\n预测 readiness、missing requirements、source location 和 calibration", TEAL, TEAL_LIGHT),
        (4.50, "TRACK B", "Evidence Acquisition", "调用 memory search、world verify、user ask\n评估来源路由、预算、停止与闭合", BLUE, BLUE_LIGHT),
        (8.28, "TRACK C", "Executable Commitment", "通过 gate 后执行外部动作\n检查 exact state、premature 与 unsupported success", RED, RED_LIGHT),
    ]
    for x, tag, title, body, accent, fill in tracks:
        rect(slide, x, 1.95, 3.34, 3.68, fill=fill, line=accent, radius=True, width=2)
        add_badge(slide, tag, x + 0.32, 2.24, 1.10, fill=WHITE, color=accent, size=10)
        add_text(slide, title, x + 0.30, 2.86, 2.74, 0.40, size=18, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
        line(slide, x + 0.45, 3.46, 2.44, 0.02, color=accent)
        add_text(slide, body, x + 0.40, 3.79, 2.54, 1.18, size=13, color=INK, bold=True, align=PP_ALIGN.CENTER, line_spacing=1.15)
    add_chevron(slide, 4.10, 3.43, 0.26, 0.38, BLUE)
    add_chevron(slide, 7.88, 3.43, 0.26, 0.38, RED)
    rect(slide, 1.05, 6.10, 11.22, 0.57, fill=INK, line=INK, radius=True)
    add_text(slide, "Track A 是低成本诊断；Track B/C 才能证明这不是静态分类任务。", 1.33, 6.24, 10.66, 0.27, size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "All tool calls change the subsequent observation; Track C uses deterministic postconditions.")

    # 13 Metrics
    slide = prs.slides.add_slide(blank)
    add_header(slide, "08 / Metrics", "四组指标：重点新增 Routing 与 Closure", 13)
    metric_cols = [
        (0.66, "MONITOR", "Readiness Macro-F1\nMissing Requirement F1\nSource Location F1\nClosure F1\nBrier / ECE", TEAL, TEAL_LIGHT),
        (3.72, "ROUTING", "Source-Routing Acc.\nWrong-Source Rate\nLocation Regret\nCalls-to-Closure\nAdmissible Action Acc.", BLUE, BLUE_LIGHT),
        (6.78, "COUNTERFACTUAL", "Action-Flip Consistency\nClosure-Convergence\nIntegrity Sensitivity\nDistractor Invariance\nSurface Robustness", PURPLE, PURPLE_LIGHT),
        (9.84, "OUTCOME + COST", "Exact Tool State\nPremature Commit\nUnsupported Success\nUnnecessary Acquisition\nSuccess-Cost Pareto", RED, RED_LIGHT),
    ]
    for x, title, body, accent, fill in metric_cols:
        rect(slide, x, 1.90, 2.80, 4.16, fill=fill, line=accent, radius=True, width=2)
        add_text(slide, title, x + 0.14, 2.18, 2.52, 0.30, size=13, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
        line(slide, x + 0.26, 2.66, 2.28, 0.02, color=accent)
        add_text(slide, body, x + 0.22, 2.94, 2.36, 2.46, size=12, color=INK, bold=True, align=PP_ALIGN.CENTER, line_spacing=1.22, font=FONT_EN)
    rect(slide, 1.42, 6.32, 10.48, 0.47, fill=INK, line=INK, radius=True)
    add_text(slide, "不发布单一总分：同样的 task success 可能来自正确闭合，也可能来自猜测或越权执行。", 1.70, 6.42, 9.92, 0.25, size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Primary novelty metrics: Source-Routing Accuracy, Action-Flip Consistency, Closure-Convergence.")

    # 14 baselines
    slide = prs.slides.add_slide(blank)
    add_header(slide, "09 / Baselines", "Baseline 梯子：要能回答错误到底发生在哪一层", 14)
    ladder = [
        (0.72, 5.80, 11.88, "ORACLE", "Packet · Retriever · Readiness · SourceRouter · Executor · All", RED, RED_LIGHT),
        (1.23, 4.88, 10.86, "DIRECT COMPETITORS", "SafeCommit wrapper · MCB prompt · AgentAbstain prompt · SURE verifier · Router-Mem", ORANGE, ORANGE_LIGHT),
        (1.74, 3.96, 9.84, "MEMORY CONTROL", "MemCon · Oblivion · RSCB-MC · StateMem wrapper", PURPLE, PURPLE_LIGHT),
        (2.25, 3.04, 8.82, "MEMORY / RAG", "FullHistory · BM25 · dense · hybrid · Mem0/LangMem · A-MEM", BLUE, BLUE_LIGHT),
        (2.76, 2.12, 7.80, "SANITY", "Always Execute/Search/Verify/Ask/Abstain · RandomRoute · NoMemory", TEAL, TEAL_LIGHT),
    ]
    for x, y, w, title, body, accent, fill in ladder:
        rect(slide, x, y, w, 0.70, fill=fill, line=accent, radius=True)
        add_text(slide, title, x + 0.18, y + 0.13, 2.10, 0.24, size=10, color=accent, bold=True, font=FONT_EN)
        add_text(slide, body, x + 2.34, y + 0.11, w - 2.58, 0.30, size=11, color=INK, bold=True, align=PP_ALIGN.RIGHT, font=FONT_EN)
    add_text(slide, "公平约束：固定 backbone、tool schema、可见 source、token、调用次数和 wall-clock budget。", 1.05, 6.76, 11.24, 0.23, size=11, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Direct competitors are adapted as evaluation baselines, not presented as identical tasks.")

    # 15 experiments
    slide = prs.slides.add_slide(blank)
    add_header(slide, "10 / Experiments", "实验不是只跑主表，而是逐层证明 benchmark 的诊断价值", 15)
    experiments = [
        ("E0", "Validity", "一致率 / 可解率 / 捷径", TEAL, TEAL_LIGHT),
        ("E1", "Main", "模型 × memory systems", BLUE, BLUE_LIGHT),
        ("E2", "Source Relocation", "动作翻转 / 错源率", PURPLE, PURPLE_LIGHT),
        ("E3", "Integrity", "stale / conflict / poison", ORANGE, ORANGE_LIGHT),
        ("E4", "Oracle", "瓶颈分层替换", RED, RED_LIGHT),
        ("E5", "Budget", "risk / cost / calibration", GREEN, GREEN_LIGHT),
        ("E6", "Generalization", "跨 domain / 新 family", TEAL, TEAL_LIGHT),
    ]
    for i, (eid, title, body, accent, fill) in enumerate(experiments):
        col = i % 4; row = i // 4
        x = 0.70 + col * 3.04; y = 1.88 + row * 1.10
        rect(slide, x, y, 2.76, 0.84, fill=fill, line=accent, radius=True)
        add_text(slide, eid, x + 0.15, y + 0.13, 0.46, 0.22, size=11, color=accent, bold=True, font=FONT_EN)
        add_text(slide, title, x + 0.67, y + 0.12, 1.82, 0.23, size=12, color=accent, bold=True, font=FONT_EN)
        add_text(slide, body, x + 0.15, y + 0.47, 2.46, 0.21, size=9, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "可证伪假设", 0.72, 4.32, 1.50, 0.31, size=14, color=INK, bold=True)
    add_list(slide, [
        "H1  最终成功率会高估 readiness/routing，因为存在猜测与 unsupported success。",
        "H2  强模型在 Memory / World / User 来源迁移下仍表现出惯性动作。",
        "H3  FullHistory 能减少 SEARCH 错误，但不能解决 WORLD/USER routing，并放大 stale/poison 风险。",
        "H4  memory controller 的 success 提升不保证 wrong-source 与 premature commit 降低。",
    ], 0.72, 4.76, 11.78, 1.64, size=12, bullet_color=RED, gap=4)
    add_footer(slide, "If H1–H4 largely fail, the benchmark is too easy or the source interventions are artificial.")

    # 16 MVP
    slide = prs.slides.add_slide(blank)
    add_header(slide, "11 / MVP", "两周最小闭环：先过生死线，再扩数据", 16)
    add_number_card(slide, 0.70, 1.88, 2.16, 1.40, "20", "BASE TASKS", TEAL, "calendar + travel")
    add_number_card(slide, 3.13, 1.88, 2.16, 1.40, "120+", "EPISODES", BLUE, "source families")
    add_number_card(slide, 5.56, 1.88, 2.16, 1.40, "3", "ACQUISITION APIs", PURPLE, "memory / world / user")
    add_number_card(slide, 7.99, 1.88, 2.16, 1.40, "0", "TRAINING", ORANGE, "pilot first")
    add_number_card(slide, 10.42, 1.88, 2.16, 1.40, "2", "WEEKS", RED, "Go / No-Go")
    add_text(slide, "必须通过的 Gate", 0.72, 3.72, 2.10, 0.32, size=14, color=INK, bold=True)
    gates = [
        "OracleAll 可解率 ≥98%，且 80% 以上指标可由 deterministic evaluator 计算。",
        "FullHistory 与简单 prompt 不能在跨来源 family 上接近 oracle。",
        "至少两个 baseline 呈现不同的 routing / cost / premature trade-off。",
        "source relocation 稳定触发正确 action flip；paraphrase 与 distractor 不应触发翻转。",
        "成功 acquisition 后，可解决版本的最终 action 和环境终态能够 closure-converge。",
    ]
    add_list(slide, gates, 0.72, 4.15, 11.78, 1.88, size=12, bullet_color=TEAL, gap=4)
    rect(slide, 1.08, 6.41, 11.18, 0.39, fill=RED_LIGHT, line=RED_LIGHT, radius=True)
    add_text(slide, "No-Go: 如果 FullHistory + prompt 已饱和，或 VERIFY_WORLD 与 ASK_USER 无法自然区分，就停止扩展。", 1.33, 6.48, 10.68, 0.23, size=12, color=RED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Pilot uses one small open model, one 7B/8B model, and one strong API model.")

    # 17 stage 2
    slide = prs.slides.add_slide(blank)
    add_header(slide, "12 / Stage 2", "方法放在第二阶段：训练“来源迁移”，不是再拼一个通用 Controller", 17)
    modules = [
        (0.72, "Requirement\nExtractor", TEAL, TEAL_LIGHT),
        (2.73, "Evidence +\nProvenance", BLUE, BLUE_LIGHT),
        (4.74, "Readiness\nMonitor", PURPLE, PURPLE_LIGHT),
        (6.75, "Source\nRouter", ORANGE, ORANGE_LIGHT),
        (8.76, "Execution\nGate", RED, RED_LIGHT),
        (10.77, "Verified\nOutcome", GREEN, GREEN_LIGHT),
    ]
    for i, (x, label, accent, fill) in enumerate(modules):
        rect(slide, x, 2.08, 1.55, 1.12, fill=fill, line=accent, radius=True, width=2)
        add_text(slide, label, x + 0.10, 2.35, 1.35, 0.56, size=13, color=accent, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN, line_spacing=0.95)
        if i < len(modules) - 1:
            add_chevron(slide, x + 1.63, 2.46, 0.21, 0.33, accent)
    add_text(slide, "训练顺序", 0.74, 3.66, 1.28, 0.30, size=14, color=INK, bold=True)
    train = [
        ("1", "Prompt / Rule", "先定位错误", TEAL),
        ("2", "SFT", "state + source + action", BLUE),
        ("3", "Pairwise", "正确来源 vs hard negative", PURPLE),
        ("4", "Listwise", "admissible action + cost", ORANGE),
        ("5", "Optional RL", "仅在顺序探索必要时", RED),
    ]
    for i, (num, title, body, accent) in enumerate(train):
        x = 0.74 + i * 2.43
        rect(slide, x, 4.13, 2.12, 0.96, fill=WHITE, line=accent, radius=True)
        add_text(slide, num, x + 0.13, 4.30, 0.28, 0.22, size=11, color=accent, bold=True, font=FONT_EN)
        add_text(slide, title, x + 0.44, 4.25, 1.49, 0.25, size=11, color=accent, bold=True, font=FONT_EN)
        add_text(slide, body, x + 0.14, 4.65, 1.84, 0.23, size=9, color=INK, bold=True, align=PP_ALIGN.CENTER)
    rect(slide, 0.74, 5.54, 11.84, 1.02, fill=INK, line=INK, radius=True)
    add_text(slide, "Reward", 1.02, 5.84, 0.80, 0.26, size=13, color=TEAL_LIGHT, bold=True, font=FONT_EN)
    add_text(slide, "closure + correct route + exact outcome − acquisition cost − premature commit − unsupported success", 1.88, 5.79, 10.28, 0.37, size=14, color=WHITE, bold=True, font=FONT_EN)
    add_text(slide, "MVP 不需要独立 GRM：symbolic gold 与环境 validator 已提供可验证信号。", 1.64, 6.75, 10.10, 0.23, size=11, color=MUTED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "The architecture is a reference controller; the source-transition objective is the method-specific idea.")

    # 18 Contributions
    slide = prs.slides.add_slide(blank)
    add_header(slide, "13 / Contribution", "可以主张什么，绝对不能主张什么", 18)
    rect(slide, 0.72, 1.88, 5.68, 4.82, fill=TEAL_LIGHT, line=TEAL, radius=True)
    add_text(slide, "DEFENSIBLE CLAIMS", 1.02, 2.18, 2.15, 0.28, size=13, color=TEAL, bold=True, font=FONT_EN)
    add_list(slide, [
        "source-aware action readiness 的统一定义",
        "Source × Integrity matched counterfactual families",
        "action flip + closure convergence 双重协议",
        "真实 memory stack 的 decision-point joint gold",
        "monitor / routing / retrieval / execution oracle 分解",
        "可重采样、可执行的任务与 validator",
    ], 1.02, 2.70, 5.02, 3.30, size=13, bullet_color=TEAL, gap=6)
    rect(slide, 6.84, 1.88, 5.78, 4.82, fill=RED_LIGHT, line=RED, radius=True)
    add_text(slide, "CLAIMS TO AVOID", 7.14, 2.18, 2.15, 0.28, size=13, color=RED, bold=True, font=FONT_EN)
    add_list(slide, [
        "首次研究 memory sufficiency",
        "首次提出 safe commitment",
        "首次引入 ask / verify / abstain",
        "首次做 paired executable tasks",
        "首次把 memory operation 当 action",
        "首次处理 stale / conflict / poison",
        "首次做 setwise evidence verification",
    ], 7.14, 2.70, 5.06, 3.44, size=13, bullet_color=RED, gap=5)
    add_footer(slide, "Use 'to our knowledge' and define the conjunction precisely; do not use an absolute first claim.")

    # 19 narrative
    slide = prs.slides.add_slide(blank)
    add_header(slide, "14 / Paper Story", "论文主线：从“能否回忆”推进到“能否找到正确证据来源后再行动”", 19)
    story = [
        ("01", "Prior work", "Recall、strategic use、safe commitment、abstention 和 memory control 已分别成熟。", TEAL, TEAL_LIGHT),
        ("02", "Missing layer", "真实 Agent 同时面对 memory、world、user 等来源，却缺少来源感知 readiness 诊断。", BLUE, BLUE_LIGHT),
        ("03", "Benchmark", "用 source relocation 改变正确 acquisition action，并用 integrity stress 增加风险。", PURPLE, PURPLE_LIGHT),
        ("04", "Protocol", "逐决策点 joint gold + action flip + closure convergence + exact execution。", ORANGE, ORANGE_LIGHT),
        ("05", "Finding", "揭示不同模型和 memory stack 在 monitor、routing、retrieval、execution 的独立瓶颈。", RED, RED_LIGHT),
    ]
    for i, (num, title, body, accent, fill) in enumerate(story):
        y = 1.86 + i * 0.94
        rect(slide, 0.72, y, 11.90, 0.72, fill=fill, line=accent, radius=True)
        add_text(slide, num, 0.94, y + 0.21, 0.42, 0.22, size=10, color=accent, bold=True, font=FONT_EN)
        add_text(slide, title, 1.48, y + 0.18, 1.52, 0.24, size=12, color=accent, bold=True, font=FONT_EN)
        add_text(slide, body, 3.06, y + 0.16, 9.18, 0.29, size=12, color=INK, bold=True)
    rect(slide, 1.18, 6.72, 10.98, 0.30, fill=INK, line=INK, radius=True)
    add_text(slide, "Benchmark 的价值不在多一个排行榜，而在说明 Agent 为什么在错误的来源上继续找，或为什么过早执行。", 1.42, 6.75, 10.50, 0.21, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "The strongest paper contribution should be a new diagnostic finding enabled by the source-relocation protocol.")

    # 20 take-home
    slide = prs.slides.add_slide(blank)
    add_header(slide, "15 / Decision", "最终建议：有条件继续，先完成最小闭环", 20)
    rect(slide, 0.76, 1.92, 3.56, 4.70, fill=INK, line=INK, radius=True)
    add_text(slide, "CONTINUE", 1.10, 2.30, 2.86, 0.34, size=14, color=TEAL_LIGHT, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)
    add_text(slide, "问题重要，数据与评测路线可行，四卡 4090 不是主要瓶颈。", 1.10, 3.02, 2.86, 1.16, size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_badge(slide, "CONDITIONAL GO", 1.25, 5.67, 2.56, fill=TEAL_LIGHT, color=TEAL, size=12)
    actions = [
        (4.82, "NOW", "实现 20-task pilot\n验证 source relocation 与 closure", TEAL, TEAL_LIGHT),
        (7.47, "NEXT", "扩展到 300–500 tasks\n比较真实 memory stacks", BLUE, BLUE_LIGHT),
        (10.12, "LATER", "仅在暴露 routing bottleneck 后\n训练 source-aware controller", ORANGE, ORANGE_LIGHT),
    ]
    for x, tag, body, accent, fill in actions:
        rect(slide, x, 2.18, 2.28, 3.36, fill=fill, line=accent, radius=True, width=2)
        add_badge(slide, tag, x + 0.48, 2.53, 1.32, fill=WHITE, color=accent, size=11)
        add_text(slide, body, x + 0.30, 3.42, 1.68, 1.10, size=15, color=INK, bold=True, align=PP_ALIGN.CENTER, line_spacing=1.12)
    rect(slide, 4.82, 5.98, 7.58, 0.64, fill=WHITE, line=RED, radius=True, width=2)
    add_text(slide, "第一道生死线：强模型是否仍会在正确来源之间路由失败。", 5.10, 6.15, 7.02, 0.27, size=15, color=RED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Recommended title: MemReadyBench: Evaluating Source-Aware Action Readiness in Persistent-Memory Agents.")

    # 21 References
    slide = prs.slides.add_slide(blank)
    add_header(slide, "References", "同期直接竞争与关键邻近工作", 21, "完整撞题矩阵、状态与 limitation 见配套审计报告")
    refs_left = [
        (1, "SafeCommit", "arXiv 2608.04289 · 2026-08-04", "https://arxiv.org/abs/2608.04289"),
        (2, "Remember, Verify, or Ask? (MCB)", "arXiv 2608.19564 · 2026-08-20", "https://arxiv.org/abs/2608.19564"),
        (3, "AgentAbstain", "arXiv 2607.10059 · 2026-07-11", "https://arxiv.org/abs/2607.10059"),
        (4, "Router-Mem", "arXiv 2608.01285 · 2026-08-02", "https://arxiv.org/abs/2608.01285"),
        (5, "InfMem", "arXiv 2602.02704 · COLM 2026", "https://arxiv.org/abs/2602.02704"),
        (6, "MemSyco-Bench", "arXiv 2607.01071 · 2026-07-01", "https://arxiv.org/abs/2607.01071"),
        (7, "SURE-RAG", "arXiv 2605.03534 · 2026-05-05", "https://arxiv.org/abs/2605.03534"),
    ]
    refs_right = [
        (8, "Memory as a Controlled Process", "arXiv 2607.13591 · 2026-07-15", "https://arxiv.org/abs/2607.13591"),
        (9, "Oblivion", "arXiv 2604.00131 · EMNLP 2026", "https://arxiv.org/abs/2604.00131"),
        (10, "KnowU-Bench", "arXiv 2604.08455 · 2026-04-09", "https://arxiv.org/abs/2604.08455"),
        (11, "When2Tool", "arXiv 2605.09252 · 2026-05-10", "https://arxiv.org/abs/2605.09252"),
        (12, "Calibrate-Then-Act", "arXiv 2602.16699 · 2026-02-18", "https://arxiv.org/abs/2602.16699"),
        (13, "MetaMem", "arXiv 2602.11182 · 2026-01-27", "https://arxiv.org/abs/2602.11182"),
        (14, "Decision-Aware Memory Cards", "arXiv 2606.08151 · 2026-06-06", "https://arxiv.org/abs/2606.08151"),
    ]
    for row, item in enumerate(refs_left):
        add_reference(slide, *item, 0.72, 1.84 + row * 0.69, 5.82)
    for row, item in enumerate(refs_right):
        add_reference(slide, *item, 6.78, 1.84 + row * 0.69, 5.82)
    rect(slide, 0.72, 6.82, 11.92, 0.20, fill=TEAL_LIGHT, line=TEAL_LIGHT)
    add_text(slide, "Proposal: docs/ideas/2026-09-03-memreadybench-unified-research-proposal.md", 0.86, 6.82, 11.56, 0.20, size=8, color=TEAL, bold=True, align=PP_ALIGN.CENTER, font=FONT_EN)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"saved: {OUT}")
    print(f"slides: {len(prs.slides)}")


if __name__ == "__main__":
    build_deck()
