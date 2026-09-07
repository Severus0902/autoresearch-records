# -*- coding: utf-8 -*-
"""Build a Chinese Agent Memory survey deck in the user's 20260321 style.

Run from the repository root:

    $env:PYTHONPATH='.tmp/pptx_native_py38'
    D:\Python38\python.exe scripts/build_agent_memory_2025_2026_survey_pptx.py
"""

from __future__ import annotations

from pathlib import Path

import build_20260321_style_kgr_memory_pptx as ui


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "slides" / "20260321.pptx"
OUT = ROOT / "docs" / "slides" / "2026-09-07-agent-memory-2025-2026-survey.pptx"
FRAMEWORK = ROOT / "docs" / "figures" / "2026-09-03-memreadybench-stage1-benchmark-framework.png"


def clear_slides(prs):
    slide_ids = prs.slides._sldIdLst
    for slide_id in list(slide_ids):
        prs.part.drop_rel(slide_id.rId)
        slide_ids.remove(slide_id)


def body(prs, title, citation=None):
    return ui.add_body_slide(prs, title, len(prs.slides) + 1, citation)


def section(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[2])
    for placeholder in slide.placeholders:
        placeholder.text = ""
    ui.add_text(
        slide,
        title,
        6.15,
        2.82,
        6.55,
        0.82,
        size=38 if len(title) > 13 else 44,
        color=ui.WHITE,
        bold=True,
        align=ui.PP_ALIGN.CENTER,
        valign=ui.MSO_ANCHOR.MIDDLE,
    )
    if subtitle:
        ui.add_text(
            slide,
            subtitle,
            6.30,
            3.72,
            6.20,
            0.56,
            size=15,
            color=ui.WHITE,
            align=ui.PP_ALIGN.CENTER,
            valign=ui.MSO_ANCHOR.MIDDLE,
        )
    return slide


def card(slide, x, y, w, h, title, lines, accent=ui.NAVY, fill=ui.WHITE, title_size=17, body_size=12.5):
    ui.add_rect(slide, x, y, w, h, fill=fill, line=accent, width=1.2)
    ui.add_rect(slide, x, y, w, 0.42, fill=accent, line=accent, width=0)
    ui.add_text(
        slide,
        title,
        x + 0.12,
        y + 0.07,
        w - 0.24,
        0.25,
        size=title_size,
        color=ui.WHITE,
        bold=True,
        align=ui.PP_ALIGN.CENTER,
        valign=ui.MSO_ANCHOR.MIDDLE,
    )
    text = "\n".join(f"• {line}" for line in lines)
    ui.add_text(slide, text, x + 0.18, y + 0.58, w - 0.36, h - 0.72, size=body_size, color=ui.INK, line_spacing=1.05)


def banner(slide, text, y=6.20, color=ui.NAVY, fill=ui.BLUE_LIGHT, size=15):
    ui.add_rect(slide, 0.72, y, 11.86, 0.52, fill=fill, line=color, width=1.0)
    ui.add_text(
        slide,
        text,
        0.90,
        y + 0.09,
        11.50,
        0.32,
        size=size,
        color=color,
        bold=True,
        align=ui.PP_ALIGN.CENTER,
        valign=ui.MSO_ANCHOR.MIDDLE,
    )


def pill(slide, x, y, w, text, accent, fill):
    ui.add_rect(slide, x, y, w, 0.38, fill=fill, line=accent, width=0.8, radius=True)
    ui.add_text(slide, text, x + 0.04, y + 0.07, w - 0.08, 0.20, size=10.5, color=accent, bold=True, align=ui.PP_ALIGN.CENTER)


def table(slide, columns, rows, x, y, w, h, widths=None, font_size=10.5):
    return ui.add_table(slide, [columns] + rows, columns, x, y, w, h, widths=widths, font_size=font_size)


def add_flow_node(slide, x, y, w, h, title, subtitle, accent, fill):
    ui.add_rect(slide, x, y, w, h, fill=fill, line=accent, width=1.4)
    ui.add_text(slide, title, x + 0.08, y + 0.14, w - 0.16, 0.30, size=16, color=accent, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, subtitle, x + 0.09, y + 0.56, w - 0.18, h - 0.68, size=10.5, color=ui.INK, align=ui.PP_ALIGN.CENTER)


def main():
    if not SRC.exists():
        raise FileNotFoundError(SRC)

    prs = ui.Presentation(str(SRC))
    clear_slides(prs)

    # 1. Cover
    slide = section(prs, "Agent Memory 文献综述", "2025-2026 顶会方法、评测与未来趋势")
    ui.add_text(slide, "从长期召回到可学习、可验证的记忆生命周期", 6.30, 4.30, 6.15, 0.44, size=17, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "文献状态核验截止：2026-09-07", 6.30, 5.03, 6.15, 0.30, size=11, color=ui.WHITE, align=ui.PP_ALIGN.CENTER)

    # 2. Scope
    slide = body(prs, "综述范围与检索口径", "官方会议论文页、ACL Anthology、ICLR/ICML/NeurIPS Proceedings；核验截止 2026-09-07。")
    card(slide, 0.70, 1.18, 3.75, 2.05, "时间与会议", ["2025-01 至 2026-09", "ACL / EMNLP / NAACL / COLM", "NeurIPS / ICLR / ICML"], ui.NAVY, ui.BLUE_LIGHT)
    card(slide, 4.78, 1.18, 3.75, 2.05, "纳入标准", ["Memory 是主要研究对象", "覆盖形成、组织、使用或演化", "影响 Agent 后续回答或行动"], ui.TEAL, ui.TEAL_LIGHT)
    card(slide, 8.86, 1.18, 3.75, 2.05, "状态分层", ["主会论文单独标注", "Findings / Industry 不混称主会", "arXiv 只用于前沿撞题审计"], ui.PURPLE, ui.PURPLE_LIGHT)
    ui.add_text(slide, "人工编码的正式会议核心地图", 0.82, 3.67, 3.25, 0.34, size=16, color=ui.NAVY, bold=True)
    ui.add_metric_card(slide, 0.82, 4.08, 2.35, 1.62, "68", "核心正式论文", "19 篇（2025）+ 49 篇（2026）", accent=ui.NAVY, fill=ui.BLUE_LIGHT)
    ui.add_metric_card(slide, 3.43, 4.08, 2.35, 1.62, "7", "会议系列", "NLP + ML 核心会议", accent=ui.TEAL, fill=ui.TEAL_LIGHT)
    ui.add_metric_card(slide, 6.04, 4.08, 2.35, 1.62, "6", "生命周期阶段", "Form 到 Re-evaluate", accent=ui.PURPLE, fill=ui.PURPLE_LIGHT)
    ui.add_metric_card(slide, 8.65, 4.08, 2.35, 1.62, "9", "前沿预印本", "只作趋势与撞题审计", accent=ui.ORANGE, fill=ui.LIGHT)
    ui.add_text(slide, "“所有”指上述可复核口径内的语料集，不包含 KV cache、GPU memory、参数记忆和仅附带 memory 模块的应用论文。", 0.84, 5.92, 11.30, 0.44, size=11.5, color=ui.MUTED, align=ui.PP_ALIGN.CENTER)

    # 3. Executive summary
    slide = body(prs, "审稿式总判断")
    card(slide, 0.68, 1.18, 3.82, 2.08, "研究对象变了", ["从“长历史中找事实”", "到“形成、选择、使用、修复状态”", "Memory 成为 Agent 的一等状态"], ui.NAVY, ui.BLUE_LIGHT)
    card(slide, 4.77, 1.18, 3.82, 2.08, "方法范式变了", ["平坦检索 → 分层/图/事件/latent", "启发式 → 主动操作与 learned policy", "结果优化 → 成本、风险、长期效用"], ui.TEAL, ui.TEAL_LIGHT)
    card(slide, 8.86, 1.18, 3.82, 2.08, "评测问题变了", ["Recall → update / forgetting", "Response → action / on-policy", "Accuracy → 诊断、修复、未来副作用"], ui.PURPLE, ui.PURPLE_LIGHT)
    banner(slide, "核心共识：Retrieved ≠ Admissible to Use ≠ Sufficient to Act", 3.69, ui.RED, ui.RED_LIGHT, 18)
    ui.add_text(slide, "最明显的未决问题", 0.88, 4.58, 2.35, 0.34, size=16, color=ui.NAVY, bold=True)
    ui.add_text(slide, "在同一任务中只改变持久记忆的完整、过期、冲突、压缩或授权状态时，Agent 是否会调整行动；获得新证据后，能否修复记忆并改善未来任务？", 0.90, 5.02, 11.55, 0.83, size=17, color=ui.INK, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)

    # 4. Definition
    slide = body(prs, "Agent Memory：工作定义", "Hu et al., Memory in the Age of AI Agents, arXiv:2512.13564；Luo et al., ACL Findings 2026。")
    ui.add_rect(slide, 0.74, 1.12, 11.86, 1.10, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.3)
    ui.add_text(slide, "由 Agent 与用户、工具或环境的历史交互形成，能够跨当前上下文、时间或会话持续存在，并在后续感知、推理、规划、行动或自我改进中被选择性读写和更新的状态。", 1.02, 1.36, 11.30, 0.63, size=19, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)
    card(slide, 0.92, 2.76, 3.55, 2.14, "持久性 Persistence", ["跨 turn / episode / session 保留", "不只存在于当前 prompt", "形成可持续的 M_t"], ui.NAVY, ui.WHITE)
    card(slide, 4.90, 2.76, 3.55, 2.14, "能动性 Agency", ["决定写、读、验证、更新、遗忘", "规则、LLM 或 learned policy", "memory operation 是决策"], ui.TEAL, ui.WHITE)
    card(slide, 8.88, 2.76, 3.55, 2.14, "行为后果 Behavior", ["改变回答与计划", "改变工具调用与环境动作", "影响未来状态与交互"], ui.PURPLE, ui.WHITE)
    banner(slide, "判别句：删除当前 query 后，这些信息是否仍因过去交互而存在，并会在未来继续被访问、修改或失效？", 5.43, ui.NAVY, ui.LIGHT, 14)

    # 5. Boundaries
    slide = body(prs, "与 LLM Memory、RAG、Agentic RAG 的边界", "Hu et al., 2025/2026；本文按 persistence、agency、behavioral consequence 重整。")
    columns = ["概念", "核心对象", "时间尺度", "与 Agent Memory 的边界"]
    rows = [
        ["LLM Memory", "参数 / 激活 / KV cache", "单次推理到模型生命周期", "不必包含 Agent 决策与跨会话状态"],
        ["RAG", "静态外部文档库", "通常单次 query", "文档不一定由历史交互形成或持续演化"],
        ["Agentic RAG", "多步搜索与证据获取", "单任务、多步", "共用检索控制，但不必维护未来会话状态"],
        ["Context Engineering", "当前上下文编排", "当前任务", "管理瞬时资源；memory 只是信息源之一"],
        ["Agent Memory", "事实、事件、经验、状态、技能", "跨轮 / 会话 / 任务", "强调形成、演化、使用、修复和行为后果"],
    ]
    table(slide, columns, rows, 0.66, 1.25, 12.02, 4.70, widths=[1.50, 2.60, 2.30, 5.62], font_size=11.5)
    banner(slide, "若没有跨 session 的形成、写回与未来复用，问题容易退化为 Agentic RAG。", 6.13, ui.RED, ui.RED_LIGHT, 15)

    # 6. Taxonomy
    slide = body(prs, "统一分类：形式 × 功能 × 动态", "Memory in the Age of AI Agents: forms, functions and dynamics。")
    card(slide, 0.64, 1.15, 3.86, 4.78, "形式 Form", ["Token / text memory", "Structured external memory", "Parametric memory", "Latent memory", "Hybrid memory", "回答：存在哪里、怎样表示"], ui.NAVY, ui.BLUE_LIGHT, body_size=13.5)
    card(slide, 4.74, 1.15, 3.86, 4.78, "功能 Function", ["事实 / 语义记忆", "情景记忆", "经验记忆", "程序性记忆", "工作记忆 / 前瞻记忆", "回答：记忆用于什么"], ui.TEAL, ui.TEAL_LIGHT, body_size=13.5)
    card(slide, 8.84, 1.15, 3.86, 4.78, "动态 Dynamics", ["Formation / Organization", "Retrieval / Consumption", "Evolution / Forgetting", "Governance / Repair", "多时间尺度更新", "回答：记忆怎样变化"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=13.5)
    banner(slide, "long-term / short-term 只描述时间层级，无法覆盖现代 Agent Memory 的结构、用途和操作。", 6.12, ui.NAVY, ui.LIGHT, 14)

    # 7. Lifecycle
    slide = body(prs, "可评测的 Agent Memory 生命周期")
    nodes = [
        ("Form", "形成\n抽取 / 写入", ui.NAVY, ui.BLUE_LIGHT),
        ("Diagnose", "诊断\n完整 / 时效 / 权限", ui.TEAL, ui.TEAL_LIGHT),
        ("Control", "控制\n用 / 查 / 验 / 问", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Commit", "行动\n回答 / 工具 / 拒绝", ui.ORANGE, ui.LIGHT),
        ("Repair", "修复\n更新 / 失效 / 合并", ui.RED, ui.RED_LIGHT),
        ("Re-evaluate", "再评测\n未来收益 / 污染", ui.GREEN, ui.GREEN_LIGHT),
    ]
    x0, y, w, h, gap = 0.52, 2.05, 1.83, 2.05, 0.25
    for i, (title, subtitle, accent, fill) in enumerate(nodes):
        x = x0 + i * (w + gap)
        add_flow_node(slide, x, y, w, h, title, subtitle, accent, fill)
        if i < len(nodes) - 1:
            ui.add_text(slide, "→", x + w + 0.01, y + 0.76, gap - 0.02, 0.35, size=19, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "历史交互 H₁:ₜ", 0.70, 1.28, 2.10, 0.36, size=15, color=ui.MUTED, bold=True)
    ui.add_text(slide, "持久状态 Mₜ", 5.54, 1.28, 2.10, 0.36, size=15, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "未来状态 Mₜ₊₁", 10.52, 1.28, 2.10, 0.36, size=15, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.RIGHT)
    banner(slide, "关键变化：评价对象从 memory content 扩展到 memory policy 与 longitudinal consequence。", 4.77, ui.NAVY, ui.BLUE_LIGHT, 15)

    # 8. Timeline
    slide = body(prs, "发展时间线：从存储到经验，再到可信状态控制")
    yline = 3.36
    ui.add_line(slide, 0.96, yline, 12.28, yline, color=ui.INK, width=1.8)
    years = [
        (1.15, "2023", "外部记忆成型", "Generative Agents\nReflexion / Voyager\nMemGPT"),
        (4.08, "2024", "长期对话与关联", "LoCoMo\nHippoRAG\nMemoryBank"),
        (7.02, "2025", "组织与经验复用", "LongMemEval / A-MEM\nAWM / HiAgent\nMemoryOS"),
        (9.96, "2026", "策略、RL 与行动", "AgeMem / Memory-R1\nAMemGym / Mem2Act\nMEM1 / AdaMEM"),
    ]
    colors = [ui.NAVY, ui.TEAL, ui.PURPLE, ui.ORANGE]
    fills = [ui.BLUE_LIGHT, ui.TEAL_LIGHT, ui.PURPLE_LIGHT, ui.LIGHT]
    for idx, (x, year, title, examples) in enumerate(years):
        ui.add_rect(slide, x, yline - 0.13, 0.26, 0.26, fill=ui.WHITE, line=colors[idx], width=2.0, radius=True)
        ui.add_text(slide, year, x - 0.42, yline + 0.29, 1.10, 0.30, size=15, color=colors[idx], bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
        card(slide, x - 0.82, 1.23, 2.25, 1.72, title, examples.split("\n"), colors[idx], fills[idx], title_size=14, body_size=10.5)
    banner(slide, "领域主线：Storage → Reflection → Experience → State diagnosis / control / repair", 5.15, ui.NAVY, ui.LIGHT, 16)

    # 9. 2025 landscape
    slide = body(prs, "2025：结构化组织、经验复用与系统评测", "LongMemEval (ICLR); A-MEM/Plan Caching (NeurIPS); AWM (ICML); ACL/NAACL/EMNLP 2025。")
    card(slide, 0.66, 1.16, 2.82, 4.64, "组织", ["A-MEM：动态链接 note", "THEANINE：时间线", "CDMem：上下文图索引", "Graph Personal Memory"], ui.NAVY, ui.BLUE_LIGHT, body_size=12.5)
    card(slide, 3.62, 1.16, 2.82, 4.64, "经验", ["AWM：workflow", "R2D2：web map + reflection", "CER：experience replay", "RMM / CFGM：反思与技巧"], ui.TEAL, ui.TEAL_LIGHT, body_size=12.5)
    card(slide, 6.58, 1.16, 2.82, 4.64, "层次", ["HiAgent：working memory", "MemoryOS：STM/MTM/LTM", "M2PA：多记忆规划", "动态写入与在线更新"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=12.5)
    card(slide, 9.54, 1.16, 2.82, 4.64, "评测与安全", ["LongMemEval：五类能力", "MemBench：事实/反思", "PersonaMem：动态画像", "MEXTRA：隐私提取"], ui.ORANGE, ui.LIGHT, body_size=12.5)
    banner(slide, "2025 的共识：记忆不只是容量问题，组织方式、经验粒度和成本同样决定表现。", 6.05, ui.NAVY, ui.WHITE, 14)

    # 10. 2026 landscape
    slide = body(prs, "2026：主动操作、RL、行动与可信治理", "ACL/ICLR/ICML 2026 正式论文；前沿 arXiv 仅作趋势补充。")
    card(slide, 0.66, 1.16, 2.82, 4.64, "主动操作", ["Memory-R1 / AgeMem", "MemSearcher / MemAct", "Sculptor / StateLM", "写、删、搜、摘要、恢复"], ui.NAVY, ui.BLUE_LIGHT, body_size=12.5)
    card(slide, 3.62, 1.16, 2.82, 4.64, "学习策略", ["PPO / GRPO / DAPO", "DPO preference learning", "multi-turn / stepwise reward", "cost-aware memory policy"], ui.TEAL, ui.TEAL_LIGHT, body_size=12.5)
    card(slide, 6.58, 1.16, 2.82, 4.64, "行动耦合", ["Mem2Act：工具与参数", "PersonaAgent：个性化行动", "MemoPilot：序列决策", "on-policy 反馈回路"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=12.5)
    card(slide, 9.54, 1.16, 2.82, 4.64, "可信状态", ["Memora：stale / forgetting", "Topology：传播泄露", "authority / conflict", "safe commitment / repair"], ui.RED, ui.RED_LIGHT, body_size=12.5)
    banner(slide, "2026 的转折：Memory 从被动数据库变成 Agent policy 可操作、可训练、也会累积风险的状态。", 6.05, ui.NAVY, ui.WHITE, 14)

    section(prs, "方法发展趋势", "结构、功能、检索、学习与资源约束")

    # 12. Structures
    slide = body(prs, "趋势一：平坦检索走向多尺度混合结构")
    structures = [
        ("Flat", "chunks + embedding\nTop-k", ui.MUTED, ui.LIGHT),
        ("Hierarchical", "STM / MTM / LTM\nevent → raw turn", ui.NAVY, ui.BLUE_LIGHT),
        ("Graph", "semantic / temporal\ncausal / entity", ui.TEAL, ui.TEAL_LIGHT),
        ("Compact", "overwrite state\nmemory token", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Hybrid", "raw evidence + index\nsummary + policy", ui.ORANGE, ui.LIGHT),
    ]
    for i, (title, text, accent, fill) in enumerate(structures):
        x = 0.63 + i * 2.48
        add_flow_node(slide, x, 2.04, 2.18, 2.24, title, text, accent, fill)
        if i < 4:
            ui.add_text(slide, "→", x + 2.19, 2.89, 0.30, 0.36, size=18, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "代表工作", 0.70, 4.72, 1.20, 0.30, size=14, color=ui.NAVY, bold=True)
    ui.add_text(slide, "BM25 / dense retrieval    MemoryOS / LightMem / TiMem    A-MEM / MAGMA / MRAgent    MEM1 / MemAgent    APEX-MEM / REMem", 1.76, 4.71, 10.68, 0.42, size=11.5, color=ui.MUTED, align=ui.PP_ALIGN.CENTER)
    banner(slide, "更可能的终局不是单一路线胜出，而是：紧凑状态负责推理，原始证据层负责验证、恢复与治理。", 5.50, ui.NAVY, ui.BLUE_LIGHT, 14)

    # 13. Functions
    slide = body(prs, "趋势二：从事实记忆到经验与程序性记忆")
    card(slide, 0.68, 1.22, 3.73, 4.58, "事实 / 情景", ["保存用户事实与具体事件", "目标：准确、时效、可追溯", "基准：LoCoMo / LongMemEval", "风险：旧值残留、事件混淆"], ui.NAVY, ui.BLUE_LIGHT)
    card(slide, 4.80, 1.22, 3.73, 4.58, "经验 / 反思", ["从成功与失败轨迹归纳策略", "目标：跨任务改进与少犯旧错", "方法：R2D2 / RMM / ReasoningBank", "风险：错误归因、过度泛化"], ui.TEAL, ui.TEAL_LIGHT)
    card(slide, 8.92, 1.22, 3.73, 4.58, "程序 / 技能", ["保存 workflow、计划、工具链", "目标：直接复用可执行过程", "方法：AWM / Mem^p / AdaMEM", "风险：环境变化、false reuse"], ui.PURPLE, ui.PURPLE_LIGHT)
    banner(slide, "新的评测重点：经验是否有证据、策略适用到哪里、复用是否提高成功率而不压缩探索。", 6.03, ui.RED, ui.RED_LIGHT, 14)

    # 14. Retrieval
    slide = body(prs, "趋势三：从语义相似到意图、时间、权威与重构", "STITCH/CAME-Bench; Memory-T1; REMem; MRAgent。")
    ui.add_text(slide, "传统相关性", 0.77, 1.23, 2.00, 0.32, size=17, color=ui.MUTED, bold=True)
    ui.add_text(slide, "s = semantic similarity", 0.77, 1.72, 3.15, 0.50, size=20, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "→", 4.05, 1.72, 0.50, 0.50, size=27, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "条件化可用性", 4.67, 1.23, 2.40, 0.32, size=17, color=ui.NAVY, bold=True)
    ui.add_rect(slide, 4.64, 1.70, 7.70, 1.10, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.2)
    ui.add_text(slide, "s(m,q)= α·semantic + β·intent + γ·time + δ·authority + η·scope − λ·conflict", 4.86, 1.99, 7.26, 0.48, size=16, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
    card(slide, 0.76, 3.30, 2.75, 2.11, "Contextual intent", ["同实体不同事件", "同主题不同目标"], ui.TEAL, ui.TEAL_LIGHT, title_size=15)
    card(slide, 3.77, 3.30, 2.75, 2.11, "Temporal validity", ["旧版本 vs 新版本", "发生时间 vs 有效时间"], ui.PURPLE, ui.PURPLE_LIGHT, title_size=15)
    card(slide, 6.78, 3.30, 2.75, 2.11, "Authority / scope", ["来源可信度", "权限与用途边界"], ui.ORANGE, ui.LIGHT, title_size=15)
    card(slide, 9.79, 3.30, 2.75, 2.11, "Reconstruction", ["由 cue 主动重组经历", "按需恢复原始证据"], ui.RED, ui.RED_LIGHT, title_size=15)
    banner(slide, "检索的目标正在从“找最像的文本”变成“找当前任务中可合法使用、足以行动的证据集合”。", 5.72, ui.NAVY, ui.WHITE, 14)

    # 15. Learnable operations
    slide = body(prs, "趋势四：Memory operations 成为可学习动作")
    columns = ["方法", "Memory 动作", "训练", "主要意义"]
    rows = [
        ["Memory-R1", "ADD / UPDATE / DELETE / NOOP", "PPO / GRPO", "学习管理与使用"],
        ["AgeMem", "store / retrieve / summarize / discard", "stepwise GRPO", "统一 STM / LTM"],
        ["MemSearcher", "search / reason / overwrite", "multi-context GRPO", "固定 token 联合优化"],
        ["MCMA", "抽象粒度与复用策略", "DPO", "跨任务可迁移经验"],
        ["MemAgent", "分段读取 / 重写状态", "DAPO", "超长输入状态压缩"],
        ["Sculptor / MemAct", "hide / restore / delete / insert", "GSPO / RL", "主动管理 working context"],
        ["MemoPilot", "memory copilot across turns", "multi-turn GRPO", "优化序列行动"],
        ["BudgetMem", "模块预算档位", "cost-aware PPO", "质量-成本联合优化"],
    ]
    table(slide, columns, rows, 0.62, 1.16, 12.08, 5.20, widths=[2.05, 3.56, 2.05, 4.42], font_size=10.6)
    banner(slide, "算法名称不是贡献：贡献来自 state、action、verifier、credit assignment 与可证伪的长期假设。", 6.40, ui.RED, ui.RED_LIGHT, 13.5)

    # 16. RL decision map
    slide = body(prs, "何时用 SFT、DPO、GRPO、GSPO 或 DAPO？")
    card(slide, 0.68, 1.18, 2.82, 4.74, "SFT", ["动作标签清楚", "可生成 oracle trace", "适合冷启动", "风险：继承 teacher 偏差"], ui.NAVY, ui.BLUE_LIGHT, body_size=12.5)
    card(slide, 3.62, 1.18, 2.82, 4.74, "DPO / 排序学习", ["同一状态有优劣动作", "pairwise/listwise 信号", "适合候选记忆与控制", "风险：离线分布偏移"], ui.TEAL, ui.TEAL_LIGHT, body_size=12.5)
    card(slide, 6.56, 1.18, 2.82, 4.74, "GRPO / GSPO", ["需要采样多条策略", "有可验证结果/过程奖励", "适合长程 memory policy", "风险：组内退化、稀疏奖励"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=12.5)
    card(slide, 9.50, 1.18, 2.82, 4.74, "DAPO / On-policy", ["超长序列或持续交互", "行为改变未来状态", "适合压缩与在线控制", "风险：成本和稳定性"], ui.ORANGE, ui.LIGHT, body_size=12.5)
    banner(slide, "先证明 prompting 与偏好学习不足，再引入 RL；否则训练范式会遮住真正的 memory failure。", 6.10, ui.NAVY, ui.WHITE, 14)

    # 17. Online/offline and efficiency
    slide = body(prs, "趋势五：在线/离线解耦与质量-成本 Pareto")
    card(slide, 0.72, 1.25, 5.58, 3.82, "在线路径：低延迟、固定预算", ["query rewriting / intent detection", "coarse retrieval + candidate verification", "incremental writing / local update", "工具前的 evidence check", "代表：LightMem、BudgetMem"], ui.NAVY, ui.BLUE_LIGHT, body_size=13)
    card(slide, 7.02, 1.25, 5.58, 3.82, "离线路径：重计算、慢演化", ["clustering / graph linking", "reflection / consolidation", "version cleanup / provenance repair", "cross-trajectory abstraction", "代表：A-MEM、AdaMEM、MCMA"], ui.TEAL, ui.TEAL_LIGHT, body_size=13)
    ui.add_text(slide, "共同报告", 0.88, 5.38, 1.18, 0.30, size=14, color=ui.NAVY, bold=True)
    for i, txt in enumerate(["Answer / Success", "Token", "Latency", "LLM Calls", "Storage", "Risk"]):
        pill(slide, 2.08 + i * 1.68, 5.34, 1.46, txt, [ui.NAVY, ui.TEAL, ui.PURPLE, ui.ORANGE, ui.GREEN, ui.RED][i], [ui.BLUE_LIGHT, ui.TEAL_LIGHT, ui.PURPLE_LIGHT, ui.LIGHT, ui.GREEN_LIGHT, ui.RED_LIGHT][i])
    banner(slide, "精度提升若来自数量级更高的调用成本，就必须在同预算下重新比较。", 6.06, ui.RED, ui.RED_LIGHT, 14)

    # 18. Trust
    slide = body(prs, "趋势六：可信记忆成为系统边界", "MEXTRA, ACL 2025；Topology Matters, ACL Findings 2026；前沿 authority/conflict/safe-commit 工作。")
    card(slide, 0.66, 1.17, 2.82, 4.78, "来源 Provenance", ["谁产生了这条记忆", "能否回到原始证据", "压缩是否保留引用"], ui.NAVY, ui.BLUE_LIGHT)
    card(slide, 3.62, 1.17, 2.82, 4.78, "权限 Authority", ["谁有权写入/读取", "是否允许用于当前行动", "授权是否已经过期"], ui.TEAL, ui.TEAL_LIGHT)
    card(slide, 6.58, 1.17, 2.82, 4.78, "冲突 Conflict", ["多来源无法裁决", "保留不确定而非强行合并", "必要时澄清或拒绝"], ui.PURPLE, ui.PURPLE_LIGHT)
    card(slide, 9.54, 1.17, 2.82, 4.78, "传播与隐私", ["跨用户、跨 Agent 泄露", "污染会持久复用", "删除与审计保证"], ui.RED, ui.RED_LIGHT)
    banner(slide, "一次 hallucination 是局部错误；被写入 memory 的 hallucination 会变成可重复、可传播的长期状态错误。", 6.12, ui.RED, ui.WHITE, 14)

    section(prs, "评测发展趋势", "从召回正确率到行动、诊断与长期修复")

    # 20. benchmark timeline
    slide = body(prs, "Benchmark 演进：五代评价对象")
    stages = [
        ("1 长程召回", "LoCoMo\nLongMemEval", "事实 / 多跳 / 时间", ui.NAVY, ui.BLUE_LIGHT),
        ("2 动态状态", "PersonaMem\nMemora", "更新 / 遗忘", ui.TEAL, ui.TEAL_LIGHT),
        ("3 战略与行动", "StratMem\nMem2Act", "选择 / 工具", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4 交互诊断", "AMemGym\nMemoryAgentBench", "on-policy / stages", ui.ORANGE, ui.LIGHT),
        ("5 可信修复", "前沿 2026", "authority / repair", ui.RED, ui.RED_LIGHT),
    ]
    for i, (title, papers, ability, accent, fill) in enumerate(stages):
        x = 0.56 + i * 2.48
        ui.add_rect(slide, x, 1.34, 2.22, 3.94, fill=fill, line=accent, width=1.3)
        ui.add_text(slide, title, x + 0.10, 1.57, 2.02, 0.44, size=15.5, color=accent, bold=True, align=ui.PP_ALIGN.CENTER)
        ui.add_text(slide, papers, x + 0.15, 2.30, 1.92, 0.78, size=15, color=ui.INK, bold=True, align=ui.PP_ALIGN.CENTER)
        ui.add_line(slide, x + 0.30, 3.30, x + 1.92, 3.30, color=accent, width=1.0)
        ui.add_text(slide, ability, x + 0.15, 3.62, 1.92, 0.72, size=12.5, color=ui.MUTED, align=ui.PP_ALIGN.CENTER)
        if i < 4:
            ui.add_text(slide, "→", x + 2.20, 3.01, 0.30, 0.34, size=18, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    banner(slide, "现状：几乎每个单点能力都已有 benchmark；空白更多出现在受控因果干预与跨会话闭环。", 5.72, ui.NAVY, ui.WHITE, 14)

    # 21. Benchmark comparison 1
    slide = body(prs, "代表性 Benchmark 对照（一）")
    columns = ["Benchmark", "出处", "主要任务", "核心信号", "主要边界"]
    rows = [
        ["LoCoMo", "ACL 2024", "跨 session QA / 总结", "多跳、时间、长程回忆", "偏最终生成"],
        ["LongMemEval", "ICLR 2025", "五类长期聊天任务", "QA / abstention", "无完整行动闭环"],
        ["PersonaMem", "COLM 2025", "动态画像与个性化", "profile / response", "偏 personalization"],
        ["MemBench", "ACL Findings 2025", "事实与反思记忆", "效果 / 效率 / 容量", "动态冲突有限"],
        ["MemoryAgentBench", "ICLR 2026", "增量形成与遗忘", "retrieval / learning / LRU", "chunk 非真实事件"],
        ["AMemGym", "ICLR 2026", "on-policy 长期对话", "write / read / use", "模拟用户与领域受限"],
    ]
    table(slide, columns, rows, 0.56, 1.22, 12.20, 5.30, widths=[2.08, 1.70, 2.52, 2.73, 3.17], font_size=10.8)

    # 22. Benchmark comparison 2
    slide = body(prs, "代表性 Benchmark 对照（二）")
    columns = ["Benchmark", "出处", "主要任务", "核心信号", "主要边界"]
    rows = [
        ["StratMem-Bench", "ACL 2026 Long", "候选记忆战略使用", "must / nice / irrelevant", "候选已给定、单轮"],
        ["Memora", "ACL Findings 2026", "动态用户状态", "stale penalty / forgetting", "合成轨迹为主"],
        ["Mem2ActBench", "ACL 2026 Long", "记忆到工具行动", "tool / parameter accuracy", "主动验证有限"],
        ["CAME-Bench", "ACL Findings 2026", "情境混淆检索", "intent hard negatives", "非完整 lifecycle"],
        ["MementoBench", "ICLR 2026", "超长流视频主动助手", "text / object / action", "多模态场景特定"],
        ["前沿 2026", "arXiv", "状态、权威、冲突、修复", "causal / longitudinal", "状态与成熟度待核验"],
    ]
    table(slide, columns, rows, 0.56, 1.22, 12.20, 5.30, widths=[2.08, 1.70, 2.52, 2.73, 3.17], font_size=10.8)

    # 23. metric stack
    slide = body(prs, "评价指标：从最终答案扩展到六层证据链")
    layers = [
        ("内容", "coverage / freshness / provenance / fidelity", ui.NAVY, ui.BLUE_LIGHT),
        ("检索", "Recall@k / MRR / hard-negative precision", ui.TEAL, ui.TEAL_LIGHT),
        ("控制", "USE / SEARCH / VERIFY / ASK / ABSTAIN", ui.PURPLE, ui.PURPLE_LIGHT),
        ("行动", "tool selection / parameters / postcondition", ui.ORANGE, ui.LIGHT),
        ("演化", "update / invalidate / merge / stale suppression", ui.RED, ui.RED_LIGHT),
        ("纵向", "future gain / recurrence / contamination / cost", ui.GREEN, ui.GREEN_LIGHT),
    ]
    for i, (name, metrics, accent, fill) in enumerate(layers):
        y = 1.14 + i * 0.83
        ui.add_rect(slide, 0.83, y, 1.20, 0.58, fill=accent, line=accent, width=0)
        ui.add_text(slide, name, 0.91, y + 0.13, 1.04, 0.28, size=15, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER)
        ui.add_rect(slide, 2.12, y, 10.20, 0.58, fill=fill, line=accent, width=0.8)
        ui.add_text(slide, metrics, 2.35, y + 0.13, 9.74, 0.28, size=14, color=accent, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
    banner(slide, "最终准确率仍要保留，但它是系统结果，不是唯一的失败解释。", 6.18, ui.NAVY, ui.WHITE, 14)

    # 24. 2025 deep reads
    slide = body(prs, "2025 代表工作：回答了什么？")
    card(slide, 0.66, 1.18, 2.82, 4.78, "LongMemEval", ["长期助手在哪类能力失败", "五类任务 + 三阶段分析", "奠定系统级 benchmark", "缺行动与纵向修复"], ui.NAVY, ui.BLUE_LIGHT, body_size=12)
    card(slide, 3.62, 1.18, 2.82, 4.78, "A-MEM", ["怎样自主组织 memory", "note + tag + link + evolution", "推动 agentic organization", "错链和重写会累积"], ui.TEAL, ui.TEAL_LIGHT, body_size=12)
    card(slide, 6.58, 1.18, 2.82, 4.78, "Agent Workflow Memory", ["怎样复用成功轨迹", "轨迹 → workflow", "程序性记忆的重要起点", "环境变化导致 false reuse"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=12)
    card(slide, 9.54, 1.18, 2.82, 4.78, "MemoryOS / HiAgent", ["怎样管理多时间尺度", "STM/MTM/LTM 与 subgoal", "强调工作记忆和层次", "复杂度不等于可靠"], ui.ORANGE, ui.LIGHT, body_size=12)

    # 25. 2026 deep reads
    slide = body(prs, "2026 代表工作：回答了什么？")
    card(slide, 0.66, 1.18, 2.82, 4.78, "Memory-R1 / AgeMem", ["能否学习 memory operations", "PPO/GRPO + step rewards", "管理与 policy 开始统一", "reward validity 仍是核心"], ui.NAVY, ui.BLUE_LIGHT, body_size=12)
    card(slide, 3.62, 1.18, 2.82, 4.78, "MEM1 / MemAgent", ["怎样压缩超长状态", "固定大小覆写 memory", "显著控制 token", "原始证据难恢复"], ui.TEAL, ui.TEAL_LIGHT, body_size=12)
    card(slide, 6.58, 1.18, 2.82, 4.78, "AMemGym", ["固定历史是否可靠", "on-policy 用户模拟", "write/read/use 诊断", "状态和领域仍较规整"], ui.PURPLE, ui.PURPLE_LIGHT, body_size=12)
    card(slide, 9.54, 1.18, 2.82, 4.78, "StratMem / Mem2Act", ["如何适度使用并转化为行动", "候选角色 + 工具参数", "超越 factual recall", "尚未覆盖完整 repair 闭环"], ui.RED, ui.RED_LIGHT, body_size=12)

    # 26. consensus
    slide = body(prs, "跨论文共识与仍有争议的地方")
    card(slide, 0.74, 1.18, 5.65, 4.78, "已经形成的共识", ["更多 memory 不一定更好", "结构与粒度会改变检索和成本", "经验需要抽象，不能只保存原轨迹", "memory use 与 retrieval 必须分开", "动态环境需要更新和遗忘", "系统必须报告质量-成本权衡"], ui.GREEN, ui.GREEN_LIGHT, body_size=13)
    card(slide, 6.94, 1.18, 5.65, 4.78, "仍未解决的争议", ["图结构是否真的优于强 reranker", "latent compression 能否兼顾可验证性", "RL 提升来自 policy 还是更强监督", "反思怎样避免错误归因", "on-policy benchmark 如何保持可控", "安全元数据应由谁写、谁验证"], ui.RED, ui.RED_LIGHT, body_size=13)
    banner(slide, "最需要的不是再给 memory 换一个存储介质，而是建立能区分这些解释的实验协议。", 6.14, ui.NAVY, ui.WHITE, 14)

    # 27. Gap
    slide = body(prs, "当前仍可防守的 Research Gap")
    ui.add_rect(slide, 0.72, 1.13, 11.90, 1.20, fill=ui.RED_LIGHT, line=ui.RED, width=1.2)
    ui.add_text(slide, "不能再声称：只有事实召回、没有更新/遗忘、没有战略使用、没有 memory-to-action、没有过程诊断、没有 RL memory operations。", 0.98, 1.42, 11.38, 0.62, size=16.5, color=ui.RED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "可防守的窄 Gap", 0.78, 2.72, 2.30, 0.38, size=18, color=ui.NAVY, bold=True)
    ui.add_rect(slide, 0.72, 3.13, 11.90, 2.25, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.4)
    ui.add_text(slide, "在保持 query、world、user goal、requirements 和 tools 不变时，仅改变由历史交互形成的 persistent memory 的覆盖度、时效性、冲突、压缩和授权状态，Agent 是否会调整记忆信任与行动策略；获得权威新证据后，能否修复 memory，使未来相关任务改善且不污染无关任务？", 1.02, 3.50, 11.30, 1.42, size=19, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)
    banner(slide, "创新不是任务拼盘，而是把 persistent memory state 设为受控因果变量。", 5.72, ui.NAVY, ui.WHITE, 15)

    # 28. Future
    slide = body(prs, "未来 2-3 年：方法与评测的预计趋势")
    card(slide, 0.70, 1.16, 5.72, 4.82, "方法侧", ["Memory-native Agent：任务动作 + 记忆动作", "显式证据层 + 隐式紧凑状态", "跨轨迹经验抽象与适用范围", "step / episode / month 多时间尺度学习", "成本、时延与风险进入约束", "多模态、具身与多 Agent 共享记忆"], ui.NAVY, ui.BLUE_LIGHT, body_size=13)
    card(slide, 6.90, 1.16, 5.72, 4.82, "评测侧", ["静态 QA → 可执行环境", "单样本 → matched state family", "单次得分 → future utility", "aggregate → oracle ladder / attribution", "平均风险 → 高风险行动分层", "自然语言 judge → 确定性状态验证"], ui.TEAL, ui.TEAL_LIGHT, body_size=13)
    banner(slide, "评价单位将从 question 变成跨会话的 memory episode family。", 6.16, ui.PURPLE, ui.PURPLE_LIGHT, 15)

    # 29. Research options
    slide = body(prs, "可选研究切入点：从 Benchmark 到方法")
    columns = ["方向", "一句话问题", "潜在贡献", "主要风险"]
    rows = [
        ["Memory-State Intervention", "状态变化是否触发策略变化", "因果、backend-agnostic 评测", "易退化为 RAG 充分性"],
        ["Longitudinal Repair", "修复能否带来未来净收益", "闭合 use-repair-future loop", "数据与环境构造较重"],
        ["Memory Trust Controller", "何时用、查、验、问、拒绝", "检索后的控制层", "单独分类器可能过薄"],
        ["Authority-aware Memory", "来源与授权怎样约束行动", "可信 metadata 一等化", "前沿撞题密集"],
        ["Budget-aware Evaluation", "同预算下真实收益是多少", "质量-成本-风险 Pareto", "单做成本新颖性不足"],
    ]
    table(slide, columns, rows, 0.58, 1.18, 12.18, 4.86, widths=[2.60, 3.25, 3.18, 3.15], font_size=10.5)
    banner(slide, "优先顺序：状态干预 Benchmark → 定位 dominant failure → 再训练 controller / reranker / repairer。", 6.18, ui.NAVY, ui.BLUE_LIGHT, 14)

    # 30. Roadmap
    slide = body(prs, "建议执行路线：Benchmark First, Method Second")
    steps = [
        ("1", "Pilot", "50-100 个 base tasks\n4-7 个 memory-state variants", ui.NAVY, ui.BLUE_LIGHT),
        ("2", "Baselines", "No-memory / full-history\nBM25 / dense / structured", ui.TEAL, ui.TEAL_LIGHT),
        ("3", "Oracle Ladder", "memory / retrieval / diagnosis\ncontrol / execution / repair", ui.PURPLE, ui.PURPLE_LIGHT),
        ("4", "Failure Map", "识别 dominant bottleneck\n检查跨模型与跨域稳定性", ui.ORANGE, ui.LIGHT),
        ("5", "Method", "SFT / DPO 优先\n必要时小模型 RL → 7B", ui.RED, ui.RED_LIGHT),
    ]
    for i, (num, title, txt, accent, fill) in enumerate(steps):
        x = 0.58 + i * 2.49
        ui.add_rect(slide, x, 1.56, 2.20, 3.38, fill=fill, line=accent, width=1.3)
        ui.add_rect(slide, x + 0.72, 1.28, 0.76, 0.76, fill=accent, line=accent, width=0, radius=True)
        ui.add_text(slide, num, x + 0.82, 1.48, 0.56, 0.30, size=20, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
        ui.add_text(slide, title, x + 0.15, 2.28, 1.90, 0.38, size=17, color=accent, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
        ui.add_text(slide, txt, x + 0.16, 3.05, 1.88, 1.15, size=11.5, color=ui.INK, align=ui.PP_ALIGN.CENTER)
        if i < 4:
            ui.add_text(slide, "→", x + 2.18, 3.00, 0.31, 0.34, size=18, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    banner(slide, "四卡 4090 的优势不在于硬训大模型，而在于先用强诊断协议找到值得训练的窄模块。", 5.54, ui.NAVY, ui.WHITE, 14)

    # 31. Framework as one concrete option
    slide = body(prs, "一个可落地的一阶段方案：MemReadyBench", "该图为当前项目方案示意，用于把综述结论落到可执行 benchmark；二阶段训练不在本图内。")
    if FRAMEWORK.exists():
        slide.shapes.add_picture(str(FRAMEWORK), ui.Inches(0.72), ui.Inches(1.16), width=ui.Inches(11.90), height=ui.Inches(5.41))
    else:
        ui.add_text(slide, "Framework image not found", 1.0, 2.5, 11.0, 1.0, size=24, color=ui.RED, bold=True, align=ui.PP_ALIGN.CENTER)

    # 32. Decision criteria
    slide = body(prs, "何时值得从 Benchmark 进入方法训练？")
    criteria = [
        ("State effect", "同一模型在不同 memory state 上出现可重复 policy flip", ui.NAVY, ui.BLUE_LIGHT),
        ("Metric gap", "episode accuracy 明显高估 family-level performance", ui.TEAL, ui.TEAL_LIGHT),
        ("Attribution", "oracle ladder 定位到一两个可训练模块", ui.PURPLE, ui.PURPLE_LIGHT),
        ("Repair value", "相关任务收益为正，无关任务污染接近零", ui.ORANGE, ui.LIGHT),
        ("Non-trivial", "简单 prompt、更多 Top-k 或 full history 不能修复", ui.RED, ui.RED_LIGHT),
    ]
    for i, (title, txt, accent, fill) in enumerate(criteria):
        y = 1.12 + i * 1.03
        ui.add_rect(slide, 0.82, y, 2.30, 0.70, fill=accent, line=accent, width=0)
        ui.add_text(slide, title, 0.94, y + 0.18, 2.06, 0.30, size=15, color=ui.WHITE, bold=True, align=ui.PP_ALIGN.CENTER, font=ui.FONT_EN)
        ui.add_rect(slide, 3.22, y, 9.12, 0.70, fill=fill, line=accent, width=0.8)
        ui.add_text(slide, txt, 3.50, y + 0.17, 8.56, 0.32, size=15, color=accent, bold=True, align=ui.PP_ALIGN.CENTER)
    banner(slide, "先让数据证明该训练什么，再决定是 reranker、verifier、controller 还是 repairer。", 6.25, ui.NAVY, ui.WHITE, 14)

    # 33. Conclusion
    slide = body(prs, "结论：Agent Memory 的竞争焦点已经改变")
    ui.add_text(slide, "过去", 0.95, 1.28, 1.35, 0.44, size=23, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_rect(slide, 0.72, 1.88, 3.15, 3.60, fill=ui.LIGHT, line=ui.MUTED, width=1.1)
    ui.add_text(slide, "存更多\n\n召回更多\n\n回答更准", 1.16, 2.45, 2.28, 2.30, size=24, color=ui.MUTED, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "→", 4.10, 3.17, 0.72, 0.70, size=38, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_text(slide, "现在与未来", 5.14, 1.28, 2.35, 0.44, size=23, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER)
    ui.add_rect(slide, 4.92, 1.88, 7.68, 3.60, fill=ui.BLUE_LIGHT, line=ui.NAVY, width=1.3)
    ui.add_text(slide, "何时可信   何时需要新证据   何时可以行动\n\n如何更新与失效   如何恢复来源与冲突\n\n修复是否改善未来任务，并控制成本与风险", 5.34, 2.34, 6.84, 2.54, size=21, color=ui.NAVY, bold=True, align=ui.PP_ALIGN.CENTER, valign=ui.MSO_ANCHOR.MIDDLE)
    banner(slide, "Memory 不再只是存储组件，而是 Agent 的持续状态、控制策略和责任边界。", 5.92, ui.NAVY, ui.WHITE, 16)

    # 34-36. References
    slide = body(prs, "参考文献（一）：综述与 2025")
    left = [
        "Hu et al. Memory in the Age of AI Agents. arXiv:2512.13564, 2025/2026.",
        "Luo et al. From Storage to Experience. ACL Findings, 2026.",
        "Wu et al. LongMemEval. ICLR, 2025.",
        "Xu et al. A-MEM. NeurIPS Main, 2025.",
        "Wang et al. Agent Workflow Memory. ICML, 2025.",
        "Hu et al. HiAgent. ACL Long, 2025.",
    ]
    right = [
        "R2D2: Reflective Agentic Memory. ACL Long, 2025.",
        "In Prospect and Retrospect. ACL Long, 2025.",
        "Contextual Experience Replay. ACL Long, 2025.",
        "Tan et al. MemBench. ACL Findings, 2025.",
        "Ong et al. THEANINE. NAACL Long, 2025.",
        "Kang et al. MemoryOS. EMNLP Main, 2025.",
    ]
    ui.add_reference_columns(slide, left, right)

    slide = body(prs, "参考文献（二）：2026 方法")
    left = [
        "Yu et al. Agentic Memory (AgeMem). ACL Long, 2026.",
        "Yan et al. Memory-R1. ACL Long, 2026.",
        "Zhang et al. LightMem. ACL Long, 2026.",
        "MAGMA. ACL Long, 2026.",
        "APEX-MEM. ACL Long, 2026.",
        "MemSearcher. ACL Findings, 2026.",
    ]
    right = [
        "MEM1. ICLR, 2026.",
        "MemAgent. ICLR Oral, 2026.",
        "Sculptor. ICLR, 2026.",
        "AdaMEM. ICML, 2026.",
        "MRAgent. ICML, 2026.",
        "MemoPilot / BudgetMem. ICML, 2026.",
    ]
    ui.add_reference_columns(slide, left, right)

    slide = body(prs, "参考文献（三）：2026 Benchmark 与治理")
    left = [
        "AMemGym. ICLR, 2026.",
        "MemoryAgentBench. ICLR, 2026.",
        "Wu et al. StratMem-Bench. ACL Long, 2026.",
        "Shen et al. Mem2ActBench. ACL Long, 2026.",
        "From Recall to Forgetting (Memora). ACL Findings, 2026.",
        "Grounding Agent Memory in Contextual Intent. ACL Findings, 2026.",
    ]
    right = [
        "MEXTRA. ACL Long, 2025.",
        "Topology Matters. ACL Findings, 2026.",
        "MemoryArena. arXiv:2602.16313, 2026.",
        "MemTrace. arXiv:2605.28732, 2026.",
        "MobileMem. arXiv:2608.13606, 2026.",
        "SafeCommit / AuthMem-Bench / TANGLE. arXiv, 2026.",
    ]
    ui.add_reference_columns(slide, left, right)

    section(prs, "谢谢！", "Agent Memory：从“记住什么”到“何时可信、如何行动、怎样修复”")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Saved {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
