# MemoAgentBench-Lite Evaluation Protocol

## Baselines

- `NoMemory`: answer only from current user query.
- `FullHistory`: include every previous message.
- `BM25Memory`: retrieve memory records with lexical search.
- `VectorMemory`: retrieve memory records with embedding search.
- `SummaryMemory`: summarize sessions and retrieve summaries.
- `StructuredMemory`: store facts/preferences/procedures as JSON records.
- `HybridMemory`: combine structured filters with text retrieval.
- `FrameworkMemory`: adapters for Mem0, Letta, MIRIX, or A-MEM-style memory.

## Metrics

### Memory Operation

- `memory_write_precision`
- `memory_write_recall`
- `memory_write_f1`
- `memory_update_accuracy`
- `selective_forgetting_accuracy`

### Retrieval

- `required_memory_recall_at_k`
- `retrieval_precision_at_k`
- `forbidden_memory_leak_rate`
- `stale_memory_rate`

### Task Outcome

- `answer_success`
- `answer_grounding`
- `action_success`
- `constraint_following`

### Cost

- `input_tokens`
- `output_tokens`
- `retrieval_latency_ms`
- `storage_bytes`

## Evaluation Design

Use both rule-based and LLM-as-judge evaluation:

- Rule-based checks handle exact memory operation labels, permission leaks, and required memory IDs.
- LLM-as-judge handles natural-language answer quality and constraint following.

The first pilot should report metrics separately instead of collapsing them into a single score. A single aggregated score can be added later after metric behavior is stable.

## First Pilot

Recommended pilot size:

- 5 domains.
- 10-20 tasks per domain.
- 3-5 sessions per task.
- 2-5 expected memory operations per task.
- 1 eval query per task in the first version.

Recommended domains:

- personal assistant.
- research assistant.
- coding assistant.
- travel planning.
- shopping/recommendation.

## Success Criteria

The pilot is worth scaling if:

- `FullHistory` is strong but expensive.
- `NoMemory` is clearly weak.
- simple BM25/vector memory fails on update, conflict, or permission tasks.
- structured or hybrid memory improves lifecycle metrics.
- at least one failure mode is not well covered by LongMemEval, LoCoMo, MemoryAgentBench, or MemoryBench.
