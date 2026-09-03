# Zotero Seed: Agentic Memory Benchmark

Intended Zotero collection tree:

```text
Agentic Memory Benchmark
  00_Surveys
  01_Agent_Memory
  02_Agentic_RAG
  03_Benchmarks
  04_Frameworks
  05_Personalization
  06_Evaluation_Methodology
```

Local Zotero read API works at `http://127.0.0.1:23119/api/users/0/items/top`, but this Zotero build reports `X-Zotero-Version: 9.0.6` and rejects `POST /api/users/0/collections` with `Endpoint does not support method`. The `Memory` collection was created manually in Zotero and then used as the target collection.

Use `agent_memory_benchmark_seed.bib` as the import seed after Zotero write access is available.

## 2026-09-03 Import Status

- Target collection: `Memory`
- Zotero collection key: `XQRQDC4S`
- Zotero connector target: `C11`
- Items currently in `Memory`: 14
- Newly imported through Zotero Connector: 14
- Failed imports: 0
- Existing seed items not duplicated: 4

The following seed items were already in the Zotero library under `Agentic KGR` and were not duplicated:

- `Generative Agents: Interactive Simulacra of Human Behavior`
- `MemGPT: Towards LLMs as Operating Systems`
- `A-MEM: Agentic Memory for LLM Agents`
- `Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning`

Current Zotero Local API supports reading but returns `501 Method not implemented` for `PUT /api/users/0/items/{key}`, so these existing records were not programmatically re-attached to `Memory`. They can be manually dragged into `Memory` in Zotero, or duplicated intentionally later if needed.

## Seed Papers

| Key | Title | Venue / Status | Folder |
| --- | --- | --- | --- |
| `zhang2024memorySurvey` | A Survey on the Memory Mechanism of Large Language Model based Agents | arXiv 2024 | `00_Surveys` |
| `du2025rethinkingMemory` | Rethinking Memory in LLM based Agents | arXiv 2025 | `00_Surveys` |
| `hu2025memoryAgeAgents` | Memory in the Age of AI Agents | arXiv 2025/2026 | `00_Surveys` |
| `li2025agenticRagSurvey` | Towards Agentic RAG with Deep Reasoning | arXiv 2025 / ARR submission | `02_Agentic_RAG` |
| `maharana2024locomo` | Evaluating Very Long-Term Conversational Memory of LLM Agents | ACL 2024 Long Papers | `03_Benchmarks` |
| `wu2025longmemeval` | LongMemEval | ICLR 2025 | `03_Benchmarks` |
| `hu2025memoryagentbench` | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions | arXiv 2025/2026; GitHub marks ICLR 2026 | `03_Benchmarks` |
| `ai2025memorybench` | MemoryBench | arXiv 2025/2026 | `03_Benchmarks` |
| `wu2026stratmemBench` | StratMem-Bench | ACL 2026 Long Papers | `03_Benchmarks` |
| `he2026memoryarena` | MemoryArena | arXiv 2026 | `03_Benchmarks` |
| `zhang2026memarena` | MemArena | arXiv 2026 | `03_Benchmarks` |
| `tavakoli2025beam` | Beyond a Million Tokens | arXiv 2025/2026 | `03_Benchmarks` |
| `jiang2025personamem` | Know Me, Respond to Me | COLM 2025 | `05_Personalization` |
| `park2023generativeAgents` | Generative Agents | UIST 2023 / arXiv | `01_Agent_Memory` |
| `packer2023memgpt` | MemGPT | arXiv 2023/2024 | `04_Frameworks` |
| `xu2025amem` | A-MEM | NeurIPS 2025 | `04_Frameworks` |
| `kang2025memoryos` | Memory OS of AI Agent | arXiv 2025 | `04_Frameworks` |
| `wang2025mirix` | MIRIX | arXiv 2025 | `04_Frameworks` |
| `yan2025memoryr1` | Memory-R1 | arXiv 2025/2026 | `04_Frameworks` |
