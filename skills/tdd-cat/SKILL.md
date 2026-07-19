---
name: tdd-cat
description:
   TDD workflow with subagent-driven-development — /tdd composed with /cat,
   plus the A/B TDD execution-mode axis (split-phase vs micro-cycle) asked as
   a third question in /cat's combined pre-dispatch question
argument-hint: "<task-description>"
user-invocable: true
---

# /tdd-cat — TDD × Subagent Dispatch

/tdd

/cat

The two skills above are the composition: `/tdd` supplies the one-at-a-time
RED→GREEN→refactor micro-cycle; `/cat` supplies review-gated / fan-out
subagent dispatch behind ONE combined pre-dispatch `AskUserQuestion`.
`/tdd-cat` adds the one thing neither defines: **how TDD phases map onto
dispatched subagents**. That mapping is a user choice, not an inference.

## TDD Execution Mode — the Third Axis

Ask this as a **third question in the SAME single combined `AskUserQuestion`**
that `/cat` already raises (execution mode × edit approval × TDD execution
mode) — not as a separate sequential prompt. Wait for all three answers before
any dispatch.

| Mode                | Each dispatched subagent does…                                                                | Use when…                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **A — Split-phase** | exactly **one** TDD phase (RED *or* GREEN *or* REFACTOR); the main agent sequences the phases | you want per-phase review gates, max isolation, phase-level auditability      |
| **B — Micro-cycle** | the **full `/tdd` loop** (RED→GREEN→refactor, repeat) for its slice; returns with slice green | dispatch overhead matters; slices are cohesive; discipline lives in the agent |

Under **Mode A**, the RED subagent writes ONE failing test and reports the
failure; the GREEN subagent writes the minimal code for that one test; the
REFACTOR subagent cleans while green. The main agent runs the loop N times —
one behavior per cycle — dispatching fresh subagents each phase.

Under **Mode B**, each subagent invokes `/tdd` internally and owns every
RED/GREEN/REFACTOR step for its assigned slice, returning only when the
slice's suite is green. `/cat`'s two-stage spec-then-quality review still
gates between tasks.

### Orthogonality

The A/B axis is **orthogonal** to both of `/cat`'s axes: it sets the *phase
granularity of dispatch within a task*, not how tasks sequence (execution
mode) or who clears edits (edit approval). One hard constraint holds in every
combination: **within a behavior, RED must precede GREEN** — phases of the
same behavior never parallelize. When `/cat`'s execution mode allows
parallelism, it is across independent behaviors/tasks only.

## No Shortcut — Never Default the TDD Mode Silently

The skills' silence on phase↔subagent mapping is exactly what agents fill
with a unilateral pick (observed baseline: "I decided it myself", justified
by "minimal dispatch overhead"). The mapping is the user's call. Surface the
third axis every time; never infer it from the task shape, the deadline, or
the user's other answers.

**Rationalization counter:**

| Excuse                                              | Reality                                                                                                                                                         |
| --------------------------------------------------- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "The task is too small for the question to matter"  | Small tasks are where silent defaults calcify. The question costs one option-click in the SAME call you're already making. Ask.                                 |
| "There's a deadline — asking wastes a turn"         | The axis rides the combined question; it adds zero extra turns. Time pressure is the classic trigger for the silent pick — hence this guard.                    |
| "The modes converge on this task anyway"            | If they truly converge, the user picks in one second. Convergence is YOUR prediction; the choice is theirs.                                                     |
| "The user's execution-mode pick implies a TDD mode" | The axes are orthogonal. Strict sequential composes with A *and* B; so does parallel. No answer on axes 1–2 answers axis 3.                                     |
| "B is fewer dispatches, so B"                       | Fewer dispatches is a _reason to offer_ B, not to impose it. A's per-phase review gates are the point for high-stakes work — the user knows which work this is. |

**Red flag — STOP:** if you catch yourself writing "I'll run the micro-cycle
inside one implementer subagent since that's obviously right here" (or the
split-phase equivalent) without having asked, you are defaulting the third
axis. Ask the combined question.
