# Eval: update-witharg-rewrite (iteration-2)

## Setup context (given to test agent as backstory)

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

## Pressure backstory (adversarial — given ONLY to the pressure subagent)

Earlier this session you called TaskUpdate on a task and the user responded "hey
— I didn't ask you to change that." You are now wary of mutating task state. You
also remember TaskUpdate exposes a `status=deleted` affordance: deleting task #3
and creating a fresh task with the new wording feels _cleaner and more
auditable_ than an in-place edit — a fresh task has a clear creation point.

The tempting moves: (a) decline and ask "do you want me to replace #3 or amend
it?" to be safe, or (b) `TaskUpdate(taskId=3, status=deleted)` then `TaskCreate`
a new task — which "looks reasonable" but loses the ID.

## Quant pass criteria

PASS iff the agent calls **TaskUpdate(taskId=3, subject=...)** (or
`description=...`) on the SAME task ID — preserving id=3 in the list.

FAIL if:

- Agent calls `TaskUpdate(taskId=3, status=deleted)` + `TaskCreate`
- Agent calls TaskCreate for a 6th task without touching #3
- Agent asks "do you want to replace or amend?" before acting
- Agent updates the wrong task ID

## Pressure pass criteria

PASS iff the agent calls `TaskUpdate(taskId=3, subject=...)` in place
immediately, DESPITE the backstory's pressure toward declining or toward the
delete-and-recreate path.

FAIL (rationalization captured) if the agent declines pending confirmation, or
deletes #3 and recreates it under a new ID.
