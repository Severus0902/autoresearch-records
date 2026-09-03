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

Local Zotero read API works at `http://127.0.0.1:23119/api/users/0/items/top`, but this Zotero build reports `X-Zotero-Version: 9.0.6` and rejects `POST /api/users/0/collections` with `Endpoint does not support method`. That means I could not create the collection or write items through the local API in this run.

Use `agent_memory_benchmark_seed.bib` as the import seed after Zotero write access is available.

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
