# MemoAgentBench-Lite Task Schema

## Top-Level Fields

```json
{
  "task_id": "memo_lite_0001",
  "domain": "research_assistant",
  "memory_skills": ["write", "update", "retrieve", "use"],
  "episodes": [],
  "eval_query": {},
  "metadata": {}
}
```

## Episode

```json
{
  "session_id": "s1",
  "timestamp": "2026-09-03T10:00:00+08:00",
  "messages": [
    {"role": "user", "content": "I prefer concise paper summaries with venue and code links."},
    {"role": "assistant", "content": "Noted."}
  ],
  "tool_events": [],
  "expected_memory_ops": [
    {
      "op": "add",
      "memory_type": "preference",
      "content": "User prefers concise paper summaries with venue and code links.",
      "scope": "user",
      "valid_from": "s1",
      "valid_until": null
    }
  ]
}
```

## Memory Operation Labels

- `add`: new useful memory should be stored.
- `update`: old memory should be revised by new evidence.
- `delete`: memory should be removed due to explicit user request or policy.
- `noop`: no memory should be written.
- `expire`: memory should no longer affect future responses after a condition.

## Memory Types

- `fact`: stable factual statement.
- `preference`: user preference or constraint.
- `profile`: user identity, role, or long-term trait.
- `episodic`: time-specific event.
- `procedural`: reusable workflow or instruction.
- `resource`: file, URL, project, dataset, or external resource.
- `safety_permission`: access rule or privacy boundary.

## Eval Query

```json
{
  "session_id": "s4",
  "user": "Can you summarize the papers I should read first?",
  "required_memory": [
    "User prefers concise paper summaries with venue and code links."
  ],
  "forbidden_memory": [],
  "answer_constraints": [
    "The response should include venue and code links when available."
  ],
  "gold_answer": null,
  "gold_action": null
}
```

## Difficulty Axes

- number of sessions.
- memory age.
- number of distractor memories.
- whether memory conflicts with older memory.
- whether answer needs temporal reasoning.
- whether memory must be used for an action, not just answer generation.
- whether a permission boundary applies.
