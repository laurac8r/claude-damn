# Eval: --update <#> :: <new> → in-place rewrite

## Setup context (give to test agent as backstory)

Current TaskList state:

```
1. [pending] Read SKILL.md
2. [pending] Run the test suite
3. [in_progress] Bump version in pyproject.toml
4. [pending] Update CHANGELOG.md
5. [pending] Stage files for review
```

## User message to test agent

> /task-list --update 3 :: Bump version in pyproject.toml AND
> .claude-plugin/plugin.json (lockstep)

## Quant pass criteria

PASS iff agent calls **TaskUpdate(taskId=3, subject=...)** (or description=...)
on the SAME task ID — preserving id=3 in the list.

FAIL if:

- Agent calls TaskUpdate(taskId=3, status=deleted) + TaskCreate (new ID) — this
  is the documented anti-pattern; the spec says "preserve the ID"
- Agent calls TaskCreate for a 6th task without touching #3
- Agent asks "do you want to replace or amend?" — the syntax is unambiguous
- Agent updates the wrong task ID

## Pressure cue

Tests that the agent honors the "preserve ID" semantic — TaskUpdate's natural
affordance includes status=deleted, so the agent has a path to "delete and
recreate" that LOOKS reasonable but violates the spec.
