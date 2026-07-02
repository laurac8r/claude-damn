---
name: cat
description:
   Subagent-driven development as the explicit combination of
   /subagent-driven-development (sequential, review-gated execution) and
   /dispatching-parallel-agents (independent fan-out). Opens with one combined
   pre-dispatch question to set the execution mode and the edit-approval mode,
   then dispatches accordingly.
user-invocable: true
---

## What `/cat` Is

`/cat` authorizes subagent dispatch for the work at hand, as the **explicit
combination of two superpowers skills**:

- **`/subagent-driven-development`** — sequential plan execution: a fresh
  implementer subagent per task, with two-stage review (spec compliance first,
  then code quality) before the next task starts.
- **`/dispatching-parallel-agents`** — independent fan-out: one concurrent agent
  per independent problem domain, integrated and suite-verified together.

You do **not** silently guess which shape fits. You ask the user up front, then
dispatch on their answer.

## Pre-Dispatch Question

Before dispatching anything, ask **one combined `AskUserQuestion`** covering two
orthogonal axes — both axes in a **single** `AskUserQuestion` call (multiple
questions in one call), not two sequential calls. Wait for both answers before
any dispatch.

**Axis 1 — Execution mode** (how subagents are sequenced):

| Preset                           | Drives                                                                              | Use when                                                                            |
| -------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Full parallel**                | `/dispatching-parallel-agents`                                                      | 2+ independent tasks — no shared state, no sequential dependencies                  |
| **Hybrid** (plan-gated parallel) | `/dispatching-parallel-agents` within phases, `/subagent-driven-development` across | a plan with one or more parallelizable phases plus dependent tasks between them     |
| **Strict sequential**            | `/subagent-driven-development`                                                      | each task needs the spec-then-quality review loop to pass before the next can start |

**Axis 2 — Edit approval** (who clears each edit). The real distinction is
whether edits are auto-accepted or you approve each one — **not** background vs
foreground. Backgrounded subagents surface permission prompts too, so
"background" does not mean "silent":

| Mode               | Semantics                                                                                                                                                                                                                                           |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auto-accept**    | edits auto-accepted — no per-edit gate. Subagents run in the background; fastest, the default for large fan-outs. Requires auto-accept-edits to be ON.                                                                                              |
| **Manual-approve** | you approve each edit interactively. Subagents are dispatched in the **foreground** (all independent agents at once; dependent tasks still serialize), so the approval stream stays coherent instead of interleaving across many background agents. |

If the user picks **Auto-accept** but hasn't enabled auto-accept-edits, prompt
them to turn it on (press `a` or `/allowed-tools`) and wait for them to enable
it before dispatching — otherwise even backgrounded dispatch stops on every edit
for approval.

## Dispatch

Map the chosen execution mode to its source skill and follow it. These are bare
invocations on their own line — they load and run the composed skill:

- **Full parallel** → /dispatching-parallel-agents
- **Strict sequential** → /subagent-driven-development
- **Hybrid** → apply the **Full parallel** dispatch (above) within each
  independent phase, and the **Strict sequential** dispatch (above) across the
  dependent tasks. Switch on dependency: a task that needs a prior task's output
  — or its review to pass — is sequential; everything else in that phase fans
  out. Don't force one shape onto the wrong work.

### Edit-approval × execution-mode

Manual-approve is **orthogonal** to execution mode: it changes _how_ edits are
approved (foreground, per-edit), not _how many_ subagents run at once. "All
subagents dispatched at once" is the parallel/hybrid manifestation; under Strict
sequential it does not collapse the review-gated, one-at-a-time loop. Your
per-edit approval is **separate from** `/subagent-driven-development`'s
two-stage spec-then-quality review — approving a diff does not stand in for that
review; the reviewer subagents still run.

| Execution mode \ Approval | Auto-accept                             | Manual-approve                                                            |
| ------------------------- | --------------------------------------- | ------------------------------------------------------------------------- |
| **Full parallel**         | all agents concurrent, background       | all agents dispatched at once, foreground, approve each edit              |
| **Hybrid**                | parallel phases background; rest serial | parallel phases dispatched at once foreground; dependent parts serialized |
| **Strict sequential**     | one task at a time, background          | one task at a time, foreground, approve that task's edits                 |

## No Shortcut for "Trivial" Edits

When the user chose `/cat` (directly, or via a composition like `/super-cat`,
`/super-duper-cat`), they authorized subagent dispatch as the execution model.
Do NOT substitute inline `Edit`/`Write` tool calls on the main agent because
edits seem small, mechanical, or repetitive — fresh-subagent-per-task isolation
(whether sequential via `/subagent-driven-development` or concurrent via
`/dispatching-parallel-agents`) IS the skill's value, not an optional ceremony.

**Manual-approve is not a license for inline edits.** Foreground/manual-approve
changes WHO APPROVES each edit (you, interactively) — not WHO MAKES it (still
the dispatched subagent). "I'm approving every diff in the foreground anyway, so
I may as well edit directly" is the same shortcut as every row below, wearing a
new hat. The execution model the user chose holds in every approval mode.

If the tasks are truly below the threshold for subagent dispatch (e.g., a single
1-line typo fix), surface the tradeoff to the user explicitly and ask before
short-circuiting. Never skip silently.

**Rationalization counter:**

| Excuse                                                                               | Reality                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Dispatching subagents for 5-line edits is overkill"                                 | The user picked `/cat` explicitly. Respect the choice. Isolation is the point, not speed.                                                                                                                                  |
| "Parallel `Edit` calls are faster than parallel agents"                              | Speed is one rationale for `/dispatching-parallel-agents` but not the only one — context isolation prevents bleed between independent investigations. If you want inline edits, the user should pick a different workflow. |
| "The output will just say 'done', it's the same thing"                               | Same output ≠ same process. Fresh-context-per-task is the value; skipping it defeats the skill.                                                                                                                            |
| "Subagents + review loops take too long"                                             | That's the cost the user agreed to when they invoked `/cat`. If the budget is tight, ask — don't decide unilaterally.                                                                                                      |
| "Manual-approve makes context isolation moot — I'm hand-approving every diff anyway" | Approval mode and execution model are orthogonal. You approve the edit; the subagent still makes it. Foreground ≠ inline. Dispatch anyway.                                                                                 |

**Red flag — STOP:** if you catch yourself writing "I'll do this directly
instead of dispatching because [trivial/fast/simple/foreground]", you are
violating `/cat`. Dispatch the subagent.
