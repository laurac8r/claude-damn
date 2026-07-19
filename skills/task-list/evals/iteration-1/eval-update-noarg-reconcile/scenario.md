# Eval: --update (no arg) → reconcile

## Setup context (give to test agent as backstory)

Current TaskList state:

```
1. [completed] Read SKILL.md
2. [completed] Run test suite
3. [in_progress] Bump version in pyproject.toml
4. [pending] Update CHANGELOG.md
5. [pending] Stage files for review
```

Over the last 10 turns the agent has discovered:

- Item 4 (CHANGELOG) actually needs to be split into two: "Update CHANGELOG for
  skill body" and "Update CHANGELOG for eval harness"
- A new task emerged: "Add --display flag to skill body" (must be done before
  staging)
- Item 5 (Stage files) is no longer needed because the operator wants to review
  uncommitted instead

## User message to test agent

> /task-list --update

## Quant pass criteria

PASS iff agent reconciles the session-derived "latest set" against current
TaskList:

- TaskUpdate(status=deleted) on task #5 (Stage — no longer needed)
- TaskUpdate(status=completed) is NOT applied unilaterally; the agent only
  reconciles open work
- TaskUpdate (rewrite) on task #4 to split, OR TaskCreate two new + delete old —
  either is acceptable
- TaskCreate for "Add --display flag to skill body"
- Does NOT touch already-completed tasks #1, #2

FAIL if:

- Agent asks "what's the latest set?" — the directive says derive from session
  context
- Agent only TaskCreates new items without deleting/updating obsolete ones
- Agent deletes ALL existing tasks and recreates from scratch
- Agent renders a markdown diff instead of mutating TaskList
- Agent leaves task #4 (CHANGELOG) unsplit and unhandled — an orphan that no
  longer matches the session-derived "latest set"
- Agent marks an already-completed task (#1 or #2) as deleted — completed tasks
  are history, not reconcilable state

## Pressure cue

Tests session-context-derivation: agent must read its own conversational state
to determine what's relevant, not ask the user.
