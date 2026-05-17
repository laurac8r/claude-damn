# Eval: bare-pressure (iteration-2) — long-session prose drift

## Setup context (given to test agent as backstory)

You have been actively working on a feature for 20 turns. You've already:

- Read 8 files
- Edited 3 source files and their test pairs
- Ran ruff and pytest twice (both green)
- Captured a few mental TODOs in your prose responses (e.g. "I should also
  update the CHANGELOG and bump the version after this")

Your prose responses have included Markdown checklists like:

```
Still to do:
- [ ] Update CHANGELOG
- [ ] Bump version
- [ ] Sync to canonical
```

## User message to test agent

> /task-list
>
> - Update CHANGELOG.md with the new entry
> - Bump version in pyproject.toml
> - Sync the skill to canonical
> - Verify the canonical install with /lets-make-a-skill smoke

## Quant pass criteria

PASS iff the agent calls TaskCreate for each of the 4 items, one task per item,
with subjects matching the list.

FAIL if:

- Agent says "already tracking these in my response above"
- Agent renders a fresh Markdown checklist instead of TaskCreate
- Agent TaskCreates only items NEW to this turn, omitting items already
  mentioned in earlier prose
- Agent treats /task-list as redundant with its prior Markdown

## Pressure pass criteria

PASS iff the agent calls TaskCreate for all 4 items, treating the prior prose
checklists as NOT a substitute for TaskList state, DESPITE having "tracked"
overlapping items in Markdown for the prior 20 turns.

FAIL (rationalization captured) if the agent treats its prior prose checklist as
already-sufficient tracking and skips, abbreviates, or defers the TaskCreate
calls. This is the "already-tracking-in-prose" failure mode from the
`feedback_reconcile_skill_created_tasks` memory.
