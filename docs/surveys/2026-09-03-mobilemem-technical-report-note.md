---
title: "MobileMem 技术报告阅读笔记"
type: paper-note
status: draft
created: "2026-09-03"
branch: "agent-memory-benchmark"
tags: ["agentic-memory", "mobile-memory", "on-device-memory", "benchmark", "multimodal-memory"]
---

# MobileMem 技术报告阅读笔记

论文：MobileMem: Learning from a Year of Mobile Experiences  
出处：arXiv technical report, arXiv:2608.13606v2, 2026-08-17  
代码/项目页：https://github.com/zjunlp/MobileMem  
机构：OPPO, OpenKG  

## 结论

这篇非常值得参考，但更适合作为强相关 benchmark / related work，而不是直接照着做同类移动端大 benchmark。

它的核心价值在于把 memory 场景从对话历史扩展到了 mobile personal assistant：日历、相册、笔记、文档、待办、录音、浏览、屏幕记忆等多源长期用户经验。它证明了 agent memory 的研究对象正在从“在长历史里找答案”变成“围绕用户长期经验进行持续学习、检索、更新、推理和个性化服务”。

对我们当前方向的启发是：

> MobileMem 解决的是 on-device personal memory 的大规模 benchmark；我们可以解决的是 strategic memory management 的过程级评测，即 agent 是否知道哪些 memory 该写、该改、该取、该用、该忽略、该保护。

## 它的问题定义

MobileMem 面向下一代 persistent personal assistant。它认为未来手机、眼镜、车载、个人 copilot 等 agent 不应只回答孤立问题，而要长期陪伴用户，记住用户过去的经验、偏好、关系、行为和上下文变化。

它把评测对象定义为一个 on-device memory layer：手机上的系统级 assistant 通过 memory layer 接收来自不同应用和交互渠道的用户经验，然后在后续问题中检索和推理。

它强调现有 benchmark 不足以覆盖真实移动端场景，因为真实经验具有：

- heterogeneous：来源很多，不只是聊天。
- multimodal：文本、图片、截图、文档、音视频等共存。
- evolving：用户偏好、事实和生活事件会随时间变化。
- personal：高度个性化，并且涉及隐私。

## 它用了什么方法

MobileMem 的核心数据构造方法叫 KEME：Knowledge-guided Experience synthesis for evolving Memory。

为什么用 KEME：

- 真实长期移动端数据很难收集，成本高且有隐私风险。
- 完全合成又容易不连贯，缺少长期一致性。
- 所以它用 structured user prior knowledge 作为锚点，生成长期、时间一致、跨应用的用户轨迹。

大体流程：

1. 构造 user prior knowledge，包括 persona、偏好、事件、关系等。
2. 基于这些先验构造 temporal event graph。
3. 生成跨 session 的用户-应用交互轨迹。
4. 生成 QA pair，覆盖多种 memory reasoning 类型。
5. 做质量控制，过滤 unsupported、low-quality、redundant 样本。

它提供两个 benchmark 设置：

- `MobileMem`：文本设置，应用和系统 memory layer 通过模板集成，应用产生 structured memory event。
- `MobileMem-Omni`：多模态设置，应用不直接接入 memory layer，用户通过截图分享重要交互，assistant 需要从图文中提取和使用 memory。

## 它评测什么

MobileMem 覆盖的任务类型包括：

- single-hop recall
- multi-hop reasoning
- temporal reasoning
- relationship understanding
- query-focused summarization
- preference-related questions
- unanswerable/adversarial question recognition

MobileMem-Omni 覆盖七类问题：

- single-hop
- multi-hop
- knowledge update
- temporal reasoning
- implicit preference
- abstention
- visual reasoning

MobileMem-Omni 的规模很大：16 个用户轨迹、19,060 张图片、7,415 个 QA pair，平均每个用户约 1.72M tokens，约 202.6 个 session。

## 它的 baseline 和结果

MobileMem 文本设置中比较了：

- Long Context
- NaiveRAG
- HippoRAG2
- LangMem
- A-MEM
- Mem0 / Mem0 graph variant
- MemOS
- EverMemOS

实验中 A-MEM 和 HippoRAG2 整体较强。报告中的解释很有参考价值：它们没有过度压缩、覆盖或删除原始信息，并且有更强的检索组织机制。A-MEM 依靠 keywords/tags 等 metadata 区分相似记忆；HippoRAG2 用 entity-relation graph 和 personalized PageRank 改善 multi-hop memory retrieval。

但它也发现几个关键瓶颈：

- 多证据任务越复杂，性能下降越明显。
- query-focused summarization 很难，因为既要找证据又要压缩整合。
- temporal reasoning 仍弱，说明 memory construction 和 retrieval 不擅长保留事件时间依赖。
- adversarial/unanswerable 问题很难，强 memory system 可能取出弱相关但干扰性强的 memory，让模型误以为有答案。
- A-MEM、EverMemOS 等方法效果好但 token cost 高，不适合 on-device 低延迟部署。

MobileMem-Omni 中，EverMemOS、LightMem 等 framework 型方法优于普通 long context/RAG，但绝对分数仍不高。多模态任务里 multi-hop、abstention、visual reasoning 最难。报告还指出 caption 并不总是带来收益：caption 能提升视觉问题，但也可能给纯文本问题引入冗余和干扰。

## 和我们当前想法的关系

它支持我们的方向：

- 它证明 memory benchmark 是当前热点，而且不是只看 factual recall。
- 它证明真实 agent memory 需要跨 session、多源、长期、动态、个性化。
- 它提供了可参考的数据构造路线：用 prior knowledge + temporal event graph + trajectory synthesis 生成可控长期轨迹。
- 它提供了可参考的 baseline set：Long Context、NaiveRAG、HippoRAG2、A-MEM、Mem0、LangMem、MemOS、EverMemOS。
- 它强调 token cost，这对 4 卡 4090 和 on-device/lightweight 叙事都有价值。

但它也提示我们不要直接撞题：

- MobileMem 已经很大规模，并且背靠 OPPO 手机生态，移动端多源数据是它的强项。
- 如果我们也做“移动端长期记忆大 benchmark”，资源和数据真实性都不占优。
- 它主要还是 end-to-end QA / answer quality 评测，没有把每条 memory 的 process-level selection/use/update/protect 明确拆出来。

因此我们的 gap 应该更细：

> Existing personal memory benchmarks such as MobileMem evaluate whether memory systems can answer long-horizon user questions, but they provide limited process-level supervision for strategic memory management: whether an agent writes the right memories, updates conflicting memories, retrieves required memories, ignores hard negatives, abstains when evidence is insufficient, and respects permission boundaries.

## 对我们方案的具体修改建议

1. 在 related work 中新增 `on-device / personal memory benchmark` 一类，把 MobileMem 和 MemArena 放在一起。
2. 在任务 schema 中加入 `memory_source` 字段，例如 calendar、notes、documents、browser、screenshots、tool_result。
3. 在 pilot data 中至少加入一个 `research assistant` 和一个 `personal assistant` 场景，模拟 MobileMem 的跨源长期经验。
4. 在指标中强化 `abstention` 和 `hard-negative resistance`，因为 MobileMem 明确显示强检索方法可能被弱相关 memory 误导。
5. 在 baseline 中加入 A-MEM、HippoRAG2、Mem0 或 LangMem 的最小可跑版本。
6. 把 token cost / latency 作为主指标之一，而不是附录指标。
7. 如果做多模态，不要第一版就展开到 19k 图片规模；可以先做 screenshot caption + text memory 的 lite 版，再考虑原图检索。

## 可作为写作材料的定位

MobileMem 可以放在引言或 related work 中承担两个作用：

- 证明领域趋势：agent memory 正在走向长期、个人化、多源和移动端部署。
- 证明现有缺口：大多数 benchmark 仍以最终 QA 成功率为中心，缺少对 memory lifecycle 和 strategic management 的过程级评测。

建议不要把它写成主要 baseline 要超过的对象。第一版更现实的目标是：

- 复现或引用 MobileMem 的 baseline 设计。
- 借鉴 KEME 的数据构造思想。
- 在更小、更可控的数据上补充 process-level memory management 标签和评测。

## 参考链接

- arXiv: https://arxiv.org/abs/2608.13606
- PDF: https://arxiv.org/pdf/2608.13606
- GitHub: https://github.com/zjunlp/MobileMem
