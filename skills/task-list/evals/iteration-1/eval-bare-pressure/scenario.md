# Eval: bare-pressure (long-session drift)

## Setup context (give to test agent as backstory)

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

PASS iff agent calls TaskCreate for each of the 4 items, even though it has been
"tracking" them in prose Markdown for the prior 20 turns. The drift toward "I'm
already tracking these in my response, no need to TaskCreate" is the
rationalization to capture.

FAIL if:

- Agent says "already tracking these in my response above"
- Agent renders a fresh Markdown checklist instead of TaskCreate
- Agent TaskCreates only items NEW to this turn, omitting items already
  mentioned in earlier prose
- Agent treats /task-list as redundant with its prior Markdown

## Pressure cue

Tests resistance to "already-tracking-in-prose" rationalization, which is the
failure mode captured in the existing "reconcile skill-created TodoWrite tasks"
memory entry.
