---
name: cat
description:
   Subagent-driven development — dispatches via /subagent-driven-development for
   sequential plan execution or /dispatching-parallel-agents for independent
   fan-out, picking the shape based on the structure of the work
user-invocable: true
---

## Prerequisites

Before proceeding, ask the user to enable **auto-accept edits** if it is not
already on. Subagent-driven development involves many file writes and edits
across parallel agents — manual approval of each edit significantly slows the
workflow. Use `AskUserQuestion` to request this:

> This workflow writes and edits many files via subagents. Please enable
> **auto-accept edits** (press `a` or use `/allowed-tools`) so I can work
> efficiently. Ready to proceed?

Wait for confirmation before continuing.

## Workflow

`/cat` authorizes subagent dispatch for the work at hand. Pick the dispatch
shape based on the structure of the work:

- **Independent fan-out** — 2+ tasks with no shared state and no sequential
  dependencies (e.g., "fix these 3 unrelated test files," "investigate 4
  separate bugs"). Use `/dispatching-parallel-agents`: dispatch concurrent
  agents, integrate results, run the full suite to verify no conflicts.
- **Plan execution** — sequential implementation tasks, each requiring the
  spec-compliance-then-code-quality review loop before the next can start. Use
  `/subagent-driven-development`: fresh implementer subagent per task, two-stage
  review, mark complete in TodoWrite, then dispatch the next.

**Mixed work** (e.g., a plan with one parallelizable phase): use
`/dispatching-parallel-agents` within that phase, `/subagent-driven-development`
for the rest. Don't force one shape onto the wrong work.

**Choosing fast:** if you can describe the work as "do these N things
independently," that's parallel dispatch. If you can describe it as "first do A,
then B depends on A's review passing," that's sequential.

## No Shortcut for "Trivial" Edits

When the user chose `/cat` (directly, or via a composition like `/super-cat`,
`/super-duper-cat`), they authorized subagent dispatch as the execution model.
Do NOT substitute inline `Edit`/`Write` tool calls on the main agent because
edits seem small, mechanical, or repetitive — fresh-subagent-per-task isolation
(whether sequential via `/subagent-driven-development` or concurrent via
`/dispatching-parallel-agents`) IS the skill's value, not an optional ceremony.

If the tasks are truly below the threshold for subagent dispatch (e.g., a single
1-line typo fix), surface the tradeoff to the user explicitly and ask before
short-circuiting. Never skip silently.

**Rationalization counter:**

| Excuse                                                  | Reality                                                                                                                                                                                                                    |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Dispatching subagents for 5-line edits is overkill"    | The user picked `/cat` explicitly. Respect the choice. Isolation is the point, not speed.                                                                                                                                  |
| "Parallel `Edit` calls are faster than parallel agents" | Speed is one rationale for `/dispatching-parallel-agents` but not the only one — context isolation prevents bleed between independent investigations. If you want inline edits, the user should pick a different workflow. |
| "The output will just say 'done', it's the same thing"  | Same output ≠ same process. Fresh-context-per-task is the value; skipping it defeats the skill.                                                                                                                            |
| "Subagents + review loops take too long"                | That's the cost the user agreed to when they invoked `/cat`. If the budget is tight, ask — don't decide unilaterally.                                                                                                      |

**Red flag — STOP:** if you catch yourself writing "I'll do this directly
instead of dispatching because [trivial/fast/simple]", you are violating `/cat`.
Dispatch the subagent.
