---
name: check-yourself
description:
  Use when a discrete task boundary is crossed in multi-step work — step
  completion, subagent dispatch return, Skill-tool invocation return, /proceed
  gate passed, test-run completion, or file-write to a durable artifact (spec,
  plan, SKILL.md). Route the boundary to its tier — full persistence run at
  pause/ship/batch gates, lightweight task-list tick at micro-boundaries. Do
  not substitute an in-place TaskList update for a due full run.
user-invocable: true
---

# Check Yourself

Run this at every task-boundary event in a multi-step workflow — at the
boundary's **tier** (full run vs lightweight tick; see Two-Tier Cadence below).

## Explicit Trigger Enumeration

A boundary exists after each of these events — not "proactively when it feels
right":

- A step in a multi-step plan is marked complete.
- A dispatched subagent returns (DONE / DONE_WITH_CONCERNS / BLOCKED).
- A Skill-tool invocation returns.
- A `/proceed` gate is passed. **Every literal `/proceed`** — not "every
  conceptual section." If 4 `/proceed`s arrive across parts of one section,
  that's 4 boundaries, not 1.
- A test-run (pytest / ruff / uv run) completes.
- A file-write lands on a durable artifact (spec, plan, SKILL.md, CHANGELOG).

If any of the above happened since the last acknowledgment, act now — at the
boundary's tier. System-reminders about stale task tracking are a sign you are
overdue. Don't batch ticks, and don't promote every tick to a full run.

## Two-Tier Cadence (Goldilocks Rule)

Boundary **detection** is universal; the **response** is tiered. This encodes
operator-confirmed pacing feedback (2026-04-24): the full persistence sequence
must not fire between every micro-step — and it must never be skipped at a
true closeout. Both directions are misfires.

**Tier 1 — Full run** (all Steps below, 1 → 6):

- A `/pause` invocation (any variant) — exactly ONE full run per pause,
  verified complete at the pause's conclusion gate.
- A ship boundary: PR about to open, work declared complete/done.
- A task-BATCH completion: every task in the active plan segment is done.
- A session-ending or context-clear signal.
- Substantial unsaved state after a long stretch with no persistence
  (judgment call — err toward one full run, not several).

**Tier 2 — Lightweight tick** (Step 1 only: update + display the task list):

- A single task/step marked complete.
- A dispatched subagent or background workflow returns.
- A Skill-tool invocation returns mid-flow.
- A mid-flight test-run completes.
- A durable-artifact file-write mid-flow.
- A literal `/proceed` gate inside an active flow — tick at minimum; promote
  to a full run only when it coincides with a Tier-1 event.

**Closeout-scoping rule.** Events that occur INSIDE an active closeout flow —
the workflow return you were waiting on, the CHECKPOINT.md append, the
`.remember`/`.checkpoints` file writes themselves — are **components of that
closeout**, not independent boundaries. One full run per closeout, anchored
and verified at its conclusion gate. Running the sequence twice in 90 seconds
with no intervening state change is over-firing, not diligence.

**Tick ≠ skip.** A tick lands visibly in the task list at the boundary itself
— a task completion gets its tick when it completes, not folded silently into
a later full run. If a listed boundary produced neither a tick nor a full run,
you are overdue.

## Steps (the Full Run)

A Tier-2 tick executes Step 1 only. A Tier-1 full run executes all steps.

**Pre-step — re-verify stale external state.** If the boundary's reflection
depends on external state read earlier in the session (git status, test counts,
file sizes, staging state), re-run the underlying tool call first — don't trust
the earlier snapshot. Numbers decay, especially when a human collaborator is
active in parallel.

1. **Update the task list.** Display the current ` ◼` / ` ✔` task list (at the
   bottom) to the user in the terminal, marking off whatever was just completed.
   If no task list exists yet, create one from the current plan.
2. **Run /remember.** Invoke the `remember` skill to save session state for
   clean continuation.
3. **Run /checkpoint-save.** Invoke the `checkpoint-save` skill to persist
   resumption context.
4. **Update core repo docs.** Update `README.md`, `CHANGELOG.md`, `ROADMAP.md`,
   etc. as appropriate and, especially, if the files already exist and/or the
   changes are extensive and/or the project/effort is lengthy/sizeable.

- Use existing docs' style(s), or otherwise best practices in the appropriate
  SWE discipline(s).

5. **Verification-before-completion (conditional — skip unless ALL three
   hold).** Invoke `superpowers:verification-before-completion` **only** at a
   shipping-ready boundary, not at mid-flight boundaries. The trigger is
   objective, not a feeling.

   Run these checks in order. If any fails, **skip this step** and do not invoke
   `superpowers:verification-before-completion`:

   ```
   a. `git status` — nothing unstaged and no untracked files related to the
      active work (ignored files are fine).
   b. `git log origin/<current-branch>..HEAD` — empty output (all local
      commits are pushed). If the branch has no upstream, this check fails
      by default: push first, or skip.
   c. The current boundary is a "claim complete / ship" boundary: PR is
      about to be opened, or user has said work is done, or implementation
      is being declared finished. Mid-iteration test passes do NOT qualify.
   ```

   If all three hold → invoke `superpowers:verification-before-completion`.
   Otherwise skip silently; it will fire on a later `/check-yourself` once the
   work actually reaches the shipping boundary.

   **Why conditional:** boundaries fire many times per task (every test-run,
   every durable file-write). Running verification-before-completion at every
   such boundary is noise and defeats the "before completion" semantics. The
   gate is whether the work has physically reached a ship-able state — staged,
   committed, pushed — not whether it subjectively feels done.

6. **Print resume footer (conditional — pause boundary only).** Step 3 always
   runs `/checkpoint-save`, so `/checkpoint-save`'s own Step 8 footer prints
   once on every full run. **Re-printing the footer at the very end of
   `/check-yourself` is gated narrowly to pause boundaries** — otherwise the
   footer floods every boundary, which is exactly the noise the "skip at
   non-pause boundaries" rule below forbids.

   **Gate:** print the footer here only if the triggering boundary was a
   `/pause` invocation. Concretely, scan the most recent user turn for any of
   these signals:
    - The literal token `/pause` (slash command).
    - A `<command-name>/pause</command-name>` block (CLI-injected).
    - A `Skill(skill="pause")` invocation in the parent agent's recent tool
      calls.

   If none match, **skip Step 6 entirely** — `/checkpoint-save`'s mid-response
   footer is sufficient at non-pause boundaries.

   When the gate fires, print at the very bottom of `/check-yourself`'s output
   (after the pause summary table):

   ````markdown
   **Next session, from a fresh terminal:**

   ```bash
   cd <ABSOLUTE-PATH-TO-CWD>
   ```

   Then in Claude Code:

   ```
   /checkpoint-resume
   ```

   Fallback if it doesn't auto-trigger: `Resume from CHECKPOINT.md`

   Next session will auto-load `.remember/remember.md` (20-line summary) and
   `CHECKPOINT.md` (full state).
   ````

   Skip this step at non-pause boundaries (mid-flight test-runs, subagent
   returns, /proceed gates inside an active flow) — the footer is verbose and
   would create noise on every step boundary. Only fire when checkpointing or
   pausing.

   **Why /check-yourself prints its own footer instead of relying on
   /checkpoint-save's:** in a `/pause` flow, `/check-yourself` is the LAST skill
   the user sees output from. `/checkpoint-save`'s footer prints inside
   `/check-yourself`'s nested output and is followed by Step 4 (repo docs), Step
   5 (verification-before-completion conditional), and `/check-yourself`'s own
   pause summary table. By the time the user reads the response, the visual
   ordering buries `/checkpoint-save`'s footer above three other sections; she
   scans the bottom of the response, sees the pause table, and asks "where from,
   how to resume?" because the footer scrolled past her eye-fixation point.
   Print it again at the very end. Same content, both layers — the visual
   position is what matters.

## Common Rationalizations (Don't Substitute)

| Excuse                                                                                                                                                                                                                 | Reality                                                                                                                                                                                                                                                                                                                                                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "I updated TaskList, that's enough"                                                                                                                                                                                    | At a Tier-1 gate, TaskList is step 1 of 4 — `/remember` and `/checkpoint-save` persist across session boundaries; TaskList does not. (At a Tier-2 micro-boundary the tick IS the requirement — this row is about Tier-1 gates.)                                                                                                                                                |
| "Work is still in-flight, I'll run it at the end"                                                                                                                                                                      | That's exactly when checkpoints matter — before a crash or context clear, not after. In-flight boundaries still get their ticks; a long stretch with substantial unsaved state earns a Tier-1 full run.                                                                                                                                                                       |
| "System-reminder already nudged me; I'll catch up later"                                                                                                                                                               | Nudges accumulate when skipped. Acknowledge each boundary at its tier to prevent drift.                                                                                                                                                                                                                                                                                        |
| "Skipping one step won't matter"                                                                                                                                                                                       | `/check-yourself` IS the drift-preventer. Skipping once defeats its purpose — a listed boundary gets a tick or a full run, never silence.                                                                                                                                                                                                                                      |
| "It's just a small edit, not a real boundary"                                                                                                                                                                          | See the trigger enumeration above. If the event is listed, it is a boundary — it gets at least a tick.                                                                                                                                                                                                                                                                         |
| "§N parts 1 and 2 are sub-boundaries within §N"                                                                                                                                                                        | The user pressed `/proceed` twice — two boundaries, a tick each at minimum. Your internal sectioning isn't the gate; the user's gesture is. (Contrast: sub-steps inside ONE closeout are components, not gestures — see Closeout-scoping.)                                                                                                                                     |
| "Every /proceed doesn't need the full 4-step sequence"                                                                                                                                                                 | Correct — and it never needs silence either. Every `/proceed` gets its boundary acknowledged: a tick at minimum, a full run when it coincides with a Tier-1 gate. The cost of a tick is seconds; the cost of an unacknowledged boundary is an unrecoverable context window.                                                                                                    |
| "I'm in flow, running remember+checkpoint-save is over-process"                                                                                                                                                        | Flow is when these matter most at Tier-1 gates. You are most likely to crash, compact, or lose state exactly when reasoning has momentum. The skill is the brake that fires _because_ you feel you don't need it.                                                                                                                                                              |
| "I'm in subagent-driven mode (/cat); inter-task /check-yourself is overkill"                                                                                                                                           | TaskUpdate flipping status to `completed` IS a boundary — tick it now, don't batch the catch-up to the next /pause. The full run lands at the batch or pause gate.                                                                                                                                                                                                             |
| "I dispatched N parallel subagents and treated their joint return as 1 boundary"                                                                                                                                       | Each subagent return is a distinct boundary regardless of dispatch timing — each gets its tick (one consolidated task-list update addressing all N returns before composing your reply is acceptable). A full run is NOT owed per return; it is owed at the next Tier-1 gate.                                                                                                  |
| "I'm in a /listen-driven (or /cat / /super-cat / similar serial-enforcement) flow — the wrapper guarantees inner skills run, so the inner returns are sub-boundaries that collapse into the wrapper's single boundary" | /listen and /cat-family skills are serial enforcement, not boundary mergers. Each inner Skill-tool return is its own tick-boundary regardless of what wraps the dispatch. The wrapper guarantees the inner skills RUN; it does not absorb their boundary semantics. One full run at the wrapper's Tier-1 gate (if it has one) — ticks in between.                              |
| "I'm mid-TDD; red→green is one phase, not a boundary stack"                                                                                                                                                            | Red failing run is one boundary (tick), green passing run another (tick), the SKILL.md file-write a third (tick). The phase-batch completion or ship gate is where the full run lands. Momentum erases ticks first — the tick is the brake that keeps the task list honest.                                                                                                    |
| "I verified inline with grep / git status"                                                                                                                                                                             | Inline verification during a tool call is not `/check-yourself`. The skill is post-boundary reflection — at minimum a visible tick; at Tier-1 gates the persistence writes. Pre-action verification does not trigger any of those.                                                                                                                                             |
| "I'm in forward-motion between user asks — this is one continuous flow"                                                                                                                                                | Forward motion is precisely when boundaries get skipped. User asks are separate gestures; a discrete boundary between turns is discrete even when reasoning feels continuous. If you notice yourself thinking "I'll batch the tick after this next thing," you are already overdue by one.                                                                                     |
| "The enumeration lists 6 events in my closeout, so 6 full runs"                                                                                                                                                        | Backwards. Events inside one closeout are components of it — exactly ONE full run, anchored at the closeout's conclusion gate (see Closeout-scoping). Near-duplicate `/remember` + `/checkpoint-save` writes seconds apart with no intervening state change are the over-fire failure the goldilocks feedback names.                                                           |
| "A full run is due but I already ticked — close enough"                                                                                                                                                                | A tick never satisfies a Tier-1 gate. /pause, ship, and batch-completion get the full sequence — checkpoint file ON DISK, not just an updated list. Tick-instead-of-full at a closeout is the under-fire failure; both directions are misfires.                                                                                                                                |
