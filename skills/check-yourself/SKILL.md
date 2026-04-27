---
name: check-yourself
description:
   Use when a discrete task boundary is crossed in multi-step work — step
   completion, subagent dispatch return, Skill-tool invocation return, /proceed
   gate passed, test-run completion, or file-write to a durable artifact (spec,
   plan, SKILL.md). Do not substitute an in-place TaskList update for this
   skill.
user-invocable: true
---

# Check Yourself

Run this at every task-boundary event in a multi-step workflow.

## Explicit Trigger Enumeration

Invoke after each of these events — not "proactively when it feels right":

- A step in a multi-step plan is marked complete.
- A dispatched subagent returns (DONE / DONE_WITH_CONCERNS / BLOCKED).
- A Skill-tool invocation returns.
- A `/proceed` gate is passed. **Every literal `/proceed`** — not "every
  conceptual section." If 4 `/proceed`s arrive across parts of one section,
  that's 4 boundaries, not 1. Back-to-back `/proceed`s without an intervening
  `/check-yourself` = overdue; invoke before responding to the second one.
- A test-run (pytest / ruff / uv run) completes.
- A file-write lands on a durable artifact (spec, plan, SKILL.md, CHANGELOG).

If any of the above happened since the last `/check-yourself`, invoke now.
System-reminders about stale task tracking are a sign you are overdue — don't
batch the catch-up, run the skill each boundary.

## Steps

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

   **Why conditional:** the trigger enumeration above fires many times per task
   (every test-run, every durable file-write). Running
   verification-before-completion at every such boundary is noise and defeats
   the "before completion" semantics. The gate is whether the work has
   physically reached a ship-able state — staged, committed, pushed — not
   whether it subjectively feels done.

6. **Print resume footer (conditional — pause boundary only).** Step 3 always
   runs `/checkpoint-save`, so `/checkpoint-save`'s own Step 8 footer prints
   once on every `/check-yourself` invocation. **Re-printing the footer at the
   very end of `/check-yourself` is gated narrowly to pause boundaries** —
   otherwise the footer floods every test-run / subagent-return / file-write
   boundary, which is exactly the noise the "skip at non-pause boundaries" rule
   below forbids.

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

| Excuse                                                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "I updated TaskList, that's enough"                                          | TaskList is step 1 of 4. `/remember` and `/checkpoint-save` persist across session boundaries; TaskList does not.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| "Work is still in-flight, I'll run it at the end"                            | That's exactly when checkpoints matter — before a crash or context clear, not after.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| "System-reminder already nudged me; I'll catch up later"                     | Nudges accumulate when skipped. Invoke the skill each boundary to prevent drift.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| "Skipping one step won't matter"                                             | `/check-yourself` IS the drift-preventer. Skipping once defeats its purpose.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| "It's just a small edit, not a real boundary"                                | See the trigger enumeration above. If the event is listed, it is a boundary.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| "§N parts 1 and 2 are sub-boundaries within §N"                              | The user pressed `/proceed` twice, which is two boundaries — not one. Your internal sectioning isn't the gate; the user's gesture is. (Observed: session `288700b5`, 2026-04-20: skipped after `/proceed` at L434 and L628 mid-brainstorm; followed correctly at L507 and L660.)                                                                                                                                                                                                                                                                                                                                     |
| "Every /proceed doesn't need to spawn 4 sub-skills"                          | Yes, it does. The cost of running them each time is bounded (~30s + two file writes). The cost of skipping one is an unrecoverable context window if the session crashes between gates. That's the trade the skill was designed to make; don't re-litigate it mid-flow.                                                                                                                                                                                                                                                                                                                                              |
| "I'm in flow, running remember+checkpoint-save is over-process"              | Flow is when these matter most. You are most likely to crash, compact, or lose state exactly when reasoning has momentum. The skill is the brake that fires _because_ you feel you don't need it.                                                                                                                                                                                                                                                                                                                                                                                                                    |
| "I'm in subagent-driven mode (/cat); inter-task /check-yourself is overkill" | The trigger enumeration says "a step in a multi-step plan is marked complete." The dispatch model does not change what counts as a step. If TaskUpdate flips status to `completed`, that IS the boundary — fire now, don't batch the catch-up to the next /pause. (Observed: session `b12115a3`, 2026-04-21: Task 1 → Task 2 transitions under /cat had no intervening /check-yourself; first invocation arrived only after user-initiated /pause.)                                                                                                                                                                  |
| "I'm mid-TDD; red→green is one phase, not a boundary stack"                  | Wrong frame. Red failing run is one boundary (test-run completion). Green passing run is another. The SKILL.md file-write is a third. TDD momentum is the exact state the skill exists to interrupt — you feel efficient, so you skip the persistence that lets the session survive a crash. (Observed: 2026-04-23 `/tesseract --visual` TDD session: 4 boundaries crossed in one reply — failing-pytest return, passing-pytest return, SKILL.md edit, end-to-end regen — zero intervening `/check-yourself` invocations.)                                                                                           |
| "I verified inline with grep / git status"                                   | Inline verification during a tool call is not `/check-yourself`. The skill is post-boundary reflection — surfacing drift you'd otherwise miss by forcing a pause, a task-list update, `/remember`, and `/checkpoint-save`. Pre-action verification does not trigger any of those writes. (Observed: session `afff23ef`, 2026-04-24: `/proceed` gate passed, Skill-tool returns from `/checkpoint-resume` and `/learn`, plus a CHECKPOINT.md file-write — all triggers fired, skill invoked zero times; inline `git status` / `grep` checks ran around each boundary instead, and drift went unnoticed for 3+ turns.) |
| "I'm in forward-motion between user asks — this is one continuous flow"      | Forward motion is precisely when boundaries get skipped. User asks are separate gestures; the transcript is cut into discrete turns, and a discrete boundary between turns is discrete even when reasoning feels continuous. Invocation is the forcing function — without it, the "flow" state erases the boundaries you'd otherwise honor. If you notice yourself thinking "I'll batch the check-yourself after this next thing," you are already overdue by one.                                                                                                                                                   |
