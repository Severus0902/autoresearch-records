# Agentic Memory Zotero Import Log

Date: 2026-09-03

Target collection:

```text
Memory
```

Collection identifiers:

- Local API key: `XQRQDC4S`
- Connector target: `C11`

## Imported

The following 22 items are now in `Memory`:

- `AMemGym: Interactive Memory Benchmarking for Assistants in Long-Horizon Conversations` (`I2GS3W8M`)
- `From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents` (`M34C32UB`)
- `MemBench: Towards More Comprehensive Evaluation on the Memory of LLM-based Agents` (`PK36EBP7`)
- `MEMTRACK: Evaluating Long-Term Memory and State Tracking in Multi-Platform Dynamic Agent Environments` (`YQB59T8A`)
- `Grounding Agent Memory in Contextual Intent` (`H8QB3EFX`)
- `MemSearcher: Training LLMs to Reason, Search and Manage Memory via End-to-End Reinforcement Learning` (`ELL95ICX`)

- `MobileMem: Learning from a Year of Mobile Experiences`
- `StratMem-Bench: Evaluating Strategic Memory Use in Virtual Character Conversation Beyond Factual Recall`
- `MIRIX: Multi-agent memory system for LLM-based agents`
- `Memory OS of AI agent`
- `Know me, respond to me: Benchmarking LLMs for dynamic user profiling and personalized responses at scale`
- `Beyond a million tokens: Benchmarking and enhancing long-term memory in LLMs`
- `MemArena: An ego-centric benchmark for on-device agentic personal memory assistants at scale`
- `MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks`
- `MemoryBench: A benchmark for memory and continual learning in LLM systems`
- `Evaluating memory in LLM agents via incremental multi-turn interactions`
- `LongMemEval: Benchmarking chat assistants on long-term interactive memory`
- `Evaluating very long-term conversational memory of LLM agents`
- `Towards agentic RAG with deep reasoning: A survey of RAG-reasoning systems in LLMs`
- `Memory in the age of AI agents`
- `Rethinking memory in LLM based agents: Representations, operations, and emerging topics`
- `A survey on the memory mechanism of large language model based agents`

## Existing But Not Moved

The following 4 seed items already existed in Zotero under `Agentic KGR`. They were not duplicated:

- `Generative agents: Interactive simulacra of human behavior`
- `MemGPT: Towards LLMs as operating systems`
- `A-MEM: Agentic memory for LLM agents`
- `Memory-R1: Enhancing large language model agents to manage and utilize memories via reinforcement learning`

Reason: this Zotero Local API build supports connector imports but does not implement item `PUT`, so I cannot attach existing records to another collection without either duplicating them or using the Zotero UI.

## Deep-Reading And Frontier Update

After completing the P0/P1/P2 deep reading and the 2026 novelty audit, 38 additional records were added to `Memory`. The collection now contains 60 top-level items.

- P1: 14 new records; together with `MemSearcher`, 15 P1 records are in `Memory`. `A-MEM` remains as the existing non-duplicated record under `Agentic KGR`.
- P2: all 7 records were added.
- Surveys: `Rethinking Memory Mechanisms of Foundation Agents in the Second Half` (`UTJ4DHYF`) and `From Storage to Experience` (`KU7LS2QG`) were added.
- Frontier audit: 13 records tagged `frontier-collision` were added, including `EvoMemBench` (`4G8BA8VK`), `MemTrace` (`YDJ69YLJ`), `StateMemBench`'s paper (`Q2K86EDY`), `LongMemEval-V2` (`53HKGMGU`), and `Scientific-RAM` (`6Z95ULSP`).
- Scientific-agent anchors: `AutoResearchBench`, `CORE-Bench`, and `ScienceAgentBench` were added for benchmark-boundary comparison.

The new records include priority/topic tags and links to their detailed reports in `docs/papers/memory/`. Creator metadata was left empty where it had not yet been independently verified; titles, venues, links, and research-role tags were prioritized for reliable retrieval.

## MetaMemBench Collision Audit Update

The following 6 records were added after reframing the benchmark around memory sufficiency monitoring and query-time control. The `Memory` collection now contains 66 top-level items.

- `Memory as a Controlled Process: Learned Adaptive Memory Management for LLM Agents` (`43BMMDU9`)
- `MemOps: Benchmarking Lifecycle Memory Operations in Long-Horizon Conversations` (`TM4IP9YX`)
- `Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents` (`RNBRCTGW`)
- `StreamMemBench: Streaming Evaluation of Agent Memory for Future-Oriented Assistance` (`CVTYBU79`)
- `CIMemories: A Compositional Benchmark for Contextual Integrity in LLMs` (`TS7EFVB7`)
- `Decision-Aware Memory Cards: Counterfactual-Inspired Context Selection and Compression for Tool-Using LLM Agents` (`M42JMTGK`)

These papers define the nearest boundaries for the new proposal: memory control methods already exist (`MemCon`), lifecycle operation evaluation already exists (`MemOps`), and dynamic, actionable, streaming, privacy-aware, and decision-aware memory each have direct prior work. The remaining target is a controlled diagnostic benchmark for whether an agent can assess memory sufficiency and choose `SEARCH / ASK / EXECUTE / ABSTAIN` before committing to an action.
