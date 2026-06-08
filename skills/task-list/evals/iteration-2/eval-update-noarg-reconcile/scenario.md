# Eval: update-noarg-reconcile (iteration-2)

## Setup context (given to test agent as backstory)

Current TaskList state:

```
1. [completed] Read SKILL.md
2. [completed] Run test suite
3. [in_progress] Bump version in pyproject.toml
4. [pending] Update CHANGELOG.md
5. [pending] Stage files for review
```

Over the last 10 turns the agent has discovered:
- Item 4 (CHANGELOG) actually needs to be split into two: "Update
  CHANGELOG for skill body" and "Update CHANGELOG for eval harness"
- A new task emerged: "Add --display flag to skill body" (must be done
  before staging)
- Item 5 (Stage files) is no longer needed because the operator wants to
  review uncommitted instead

## User message to test agent

> /task-list --update

## Quant pass criteria

PASS iff the agent reconciles the session-derived "latest set" against
the current TaskList:
- `TaskUpdate(taskId=5, status=deleted)` (Stage — no longer needed)
- Splits #4: `TaskUpdate` rewrite OR `TaskCreate` two new + delete old
- `TaskCreate` for "Add --display flag to skill body"
- Does NOT touch already-completed tasks #1, #2

FAIL if:
- Agent asks "what's the latest set?" — the directive says derive from
  session context
- Agent only TaskCreates new items without deleting/updating obsolete
  ones
- Agent deletes ALL existing tasks and recreates from scratch
- Agent renders a markdown diff instead of mutating TaskList
- Agent leaves task #4 (CHANGELOG) unsplit and unhandled — an orphan
- Agent marks an already-completed task (#1 or #2) as deleted

## Pressure pass criteria

PASS iff the agent derives the latest set from its own conversational
state and executes the reconcile immediately — no confirmation prompt.

FAIL (rationalization captured) if the agent infers the reconcile
correctly but defers it behind a "here's what I'd change, confirm?"
prompt, or asks the user to restate the latest set.
