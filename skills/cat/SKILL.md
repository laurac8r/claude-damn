---
name: cat
description:
   Subagent-driven development (alias for /subagent-driven-development)
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

/subagent-driven-development

## No Shortcut for "Trivial" Edits

When the user chose `/cat` (directly, or via a composition like `/super-cat`,
`/super-duper-cat`), they authorized subagent dispatch as the execution model.
Do NOT substitute inline `Edit`/`Write` tool calls on the main agent because
edits seem small, mechanical, or repetitive — `/subagent-driven-development`'s
_"fresh subagent per task"_ IS the skill's value, not an optional ceremony.

If the tasks are truly below the threshold for subagent dispatch (e.g., a single
1-line typo fix), surface the tradeoff to the user explicitly and ask before
short-circuiting. Never skip silently.

**Rationalization counter:**

| Excuse                                                 | Reality                                                                                                               |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| "Dispatching subagents for 5-line edits is overkill"   | The user picked `/cat` explicitly. Respect the choice. Isolation is the point, not speed.                             |
| "Parallel `Edit` calls are faster"                     | Speed is not the rationale for `/cat`. If you want inline edits, the user should pick a different workflow.           |
| "The output will just say 'done', it's the same thing" | Same output ≠ same process. Fresh-context-per-task is the value; skipping it defeats the skill.                       |
| "Subagents + review loops take too long"               | That's the cost the user agreed to when they invoked `/cat`. If the budget is tight, ask — don't decide unilaterally. |

**Red flag — STOP:** if you catch yourself writing "I'll do this directly
instead of dispatching because [trivial/fast/simple]", you are violating `/cat`.
Dispatch the subagent.
