---
name: checkpoint-save
description:
  Use when pausing work that will be resumed later, when switching contexts, or
  when the user asks to save a checkpoint. Creates a CHECKPOINT.md that
  captures full resumption context.
user-invocable: true
allowed-tools: Bash(git branch --show-current), Bash(git rev-parse --show-toplevel), Bash(git rev-parse --path-format=absolute --git-common-dir), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add CHECKPOINT.md), Bash(basename:*), Bash(dirname:*), Bash(mkdir:*), Bash(cp CHECKPOINT.md *.md*), Bash(mv CHECKPOINT.md *.md*), Bash(stat:*), Bash(date:*), Read, Write, Edit
---

# Checkpoint Save

Pause here and create a checkpoint CHECKPOINT.md file to allow us to quickly
resume work on this later. Use / reference memories as needed.

## What to Capture

Create `CHECKPOINT.md` in the project root (or working directory) with:

```markdown
# Checkpoint: [Brief Title]

**Date:** [today's date] **Branch:** `[current git branch]` **Session context:**
[1-2 sentence summary of what we were doing]

## Current State

- What's been completed
- What's in progress (with file paths and line numbers)
- What's not yet started

## Next Steps

1. [Exact next action to take]
2. [Following actions in order]

## Key Decisions Made

-

[Decision]: [Why] (so we don't re-debate)

## Open Questions / Blockers

- [Anything unresolved]

## Files Modified

- [List of files changed in this session, with brief note on what changed]

## Relevant Memories

- [Reference any memory files that provide context for this work]

## Resume Command

[Exact prompt or slash command to resume, e.g. "Continue from CHECKPOINT.md"]
```

## Process

### Step 1 — Compute current-branch slug

Run `git branch --show-current` to get the current branch name. If the output is
empty (detached HEAD), fall back to the basename of CWD (`basename "$PWD"`).
Apply slug rules to produce `<slug>`:

1. Lowercase.
2. Replace `/` with `-`.
3. Strip characters outside `[a-z0-9-]`.
4. Collapse consecutive `-`.

### Step 2 — Resolve archive directory

Run:

```
COMMON_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
```

If this command exits non-zero, abort: **"Not a git repository. checkpoint-save
requires a git repo at CWD."**

Then:

```
ARCHIVE=$(dirname "$COMMON_DIR")/.checkpoints
mkdir -p "$ARCHIVE"
```

This resolves to the **main checkout root's** `.checkpoints/` directory,
ensuring all git worktrees share a single archive.

### Step 3 — Verify `.gitignore` coverage

Check whether `.checkpoints/` is listed in the main checkout's `.gitignore` (the
`.gitignore` at `$(dirname "$COMMON_DIR")/.gitignore`). If the line is absent,
append `.checkpoints/` to that `.gitignore` and report to the user:

> "Added `.checkpoints/` to `.gitignore` in the main checkout. Please review and
> commit that change when ready."

Do NOT auto-commit — the user handles all git commits.

### Step 4 — Handle existing CHECKPOINT.md

If `CHECKPOINT.md` exists at CWD, parse its `**Branch:**` line and apply one of
the four cases below. **Before auto-selecting Case A (same branch), also check
for the Case D escape hatch** — a same-branch CHECKPOINT.md may belong to an
unrelated live effort, not a stale version of current work.

**Case A — Same branch as current, same effort (stale version of current
work):** Copy the existing file to `.checkpoints/<slug>.prev.md` (overwrite any
prior `.prev.md`). This is a rolling single-slot backup before the same-branch
overwrite. Use this when the existing checkpoint's **Current State** section
describes the same work you're about to re-checkpoint — it's a natural
supersession.

**Case B — Different branch:** The existing checkpoint belongs to a different
effort. Derive `<old-slug>` from the `**Branch:**` value in the existing file
(apply the same slug rules). Move (not copy) the existing `CHECKPOINT.md` to
`.checkpoints/<old-slug>.md`. On collision (file already exists), append `-2`,
`-3`, etc. until the name is free.

**Before proceeding to Step 5, verify the `mv` succeeded.** If it fails
(permissions, disk full, cross-device), abort: **"Failed to archive existing
CHECKPOINT.md. The old checkpoint is still at CWD. Resolve the mv failure before
retrying."** Do not overwrite `CHECKPOINT.md` until the archive is confirmed.

Report to the user:

> "Archived previous checkpoint (branch: `<old-branch>`) to
> `.checkpoints/<old-slug>.md`."

**Case C — Branch line missing or unparseable:** The `**Branch:**` line cannot
be found or its value is empty/malformed. Get the file's modification time as a
timestamp (`YYYYMMDD-HHMMSS`):

- **macOS:** `stat -f "%Sm" -t "%Y%m%d-%H%M%S" CHECKPOINT.md`
- **Linux:** `date -r CHECKPOINT.md +%Y%m%d-%H%M%S`
- **Fallback** (if both fail): `date +%Y%m%d-%H%M%S` (uses current time)

Move the existing file to `.checkpoints/unparsed-<YYYYMMDD-HHMMSS>.md`. Report
to the user:

> "Could not parse branch from existing CHECKPOINT.md. Archived to
> `.checkpoints/unparsed-<YYYYMMDD-HHMMSS>.md`."

**Case D — Existing CHECKPOINT.md is an unrelated live effort (do not touch
it):** The existing checkpoint on the current branch is a separate live work
thread whose state you must preserve in place (e.g., a long-running refactor
checkpoint on `main`, where the current session is on the same branch but
working on an unrelated concern). Case A would clobber it by rolling it to
`<slug>.prev.md`; Case D routes around that.

**Do not auto-detect Case D** — same-branch defaults to Case A. Trigger Case D
only when one of the following is true:

- The operator explicitly signals it ("don't overwrite the existing
  CHECKPOINT.md", "save to a named slug", "this is a parallel thread", "keep the
  live one intact").
- The existing file's **Current State** / **Next Steps** / **Session context**
  sections describe work clearly unrelated to this session's focus, AND the file
  is recent enough (mtime < 30 days) to plausibly be live. In ambiguous cases,
  **ask before deciding** — do not silently downgrade to Case A.

Behavior under Case D:

1. Propose (or accept operator-supplied) a **descriptive slug** capturing this
   session's focus — not the branch name. Slug rules from Step 1 apply
   (lowercase, `[a-z0-9-]`). Example: `claude-damn-skills-roadmap`,
   `statusline-pricing-opus-4-7`.
2. Ask the operator to confirm before writing: _"Existing CHECKPOINT.md on
   branch `<X>` appears to be a separate live effort (`<brief>`). Save this
   session's checkpoint to `.checkpoints/<proposed-slug>.md` and leave
   CHECKPOINT.md untouched? (y / choose different slug / treat as Case A
   overwrite)"_
3. On confirmation, write the new checkpoint to
   `.checkpoints/<descriptive-slug>.md` using the same template as Step 5. Do
   **not** touch `CHECKPOINT.md` at CWD.
4. **Skip Step 6 staging entirely** — `.checkpoints/` is gitignored, and the
   live `CHECKPOINT.md` wasn't modified.
5. Report to the user:

   > "Saved this session's state to `.checkpoints/<descriptive-slug>.md`. Live
   > `CHECKPOINT.md` (branch `<branch>`, effort `<brief>`) left untouched at
   > CWD. To resume this session's work later, reference the named archive
   > directly — it will not be auto-offered by `/checkpoint-resume` for the
   > current branch slug."

**Invariant adjustments under Case D:**

- Invariant #1 ("CWD has exactly one `CHECKPOINT.md`") — still holds; the live
  one was preserved unchanged.
- Invariant #2 (`**Branch:**` line matches current) — applies to the _live_
  file, which we did not modify. The named archive is not bound by this
  invariant.
- Invariant #3 (no prior content lost) — the live file was untouched, so nothing
  was lost.

Observed example (2026-04-24): session on `main` branch needed to pause work on
"claude-damn skills roadmap expansion + HTML→PDF SOP" while
`~/.claude/CHECKPOINT.md` held live unshipped state on the 2026-04-23 statusline
dynamic-pricing / Opus 4.7 PRICING row work. Case A would have rolled the
PRICING state to `.prev.md` and replaced CWD's CHECKPOINT.md with the roadmap
session. Case D saved the roadmap session to
`.checkpoints/claude-damn-skills-roadmap.md` and left the PRICING checkpoint
untouched.

### Step 5 — Write new CHECKPOINT.md

Write a fresh `CHECKPOINT.md` at CWD using the template above, filling in all
sections. Run `git status` and `git diff --stat` to capture current state.
Review active tasks/todos in the session. Check memory files for relevant
context to reference.

### Step 5b — Mirror to the shared archive when CWD is a linked worktree

Cases A/B/C write `CHECKPOINT.md` at CWD. When CWD is a **linked git
worktree**, that file is destroyed with the worktree on `git worktree remove` —
so the checkpoint must also exist somewhere durable.

Detect a linked worktree by comparing the worktree root to the main checkout
root (`COMMON_DIR` is from Step 2):

```
TOPLEVEL=$(git rev-parse --show-toplevel)
MAIN_ROOT=$(dirname "$COMMON_DIR")
```

If `TOPLEVEL` != `MAIN_ROOT`, CWD is a linked worktree — copy the just-written
checkpoint into the shared archive:

```
cp CHECKPOINT.md "$ARCHIVE/<slug>.md"
```

`$ARCHIVE` (Step 2) lives under the **main checkout**, so this mirror survives
the worktree's teardown. **Verify the `cp` exit code** — as with Step 4's `mv`
check, a failed copy must be surfaced, never reported as a successful
checkpoint. A pre-existing `.checkpoints/<slug>.md` is intentionally
overwritten: it is this same effort's prior mirror (unlike Step 4 Case B's
`-2`/`-3` collision-suffixing, which is for *different* efforts). Report:

> "CWD is a linked worktree — mirrored the checkpoint to
> `.checkpoints/<slug>.md` so it survives `git worktree remove`."

Skip this step **only** when `TOPLEVEL` == `MAIN_ROOT` and both commands
resolved cleanly — that is the main checkout, where `CHECKPOINT.md` at CWD is
already durable. If either command fails or returns empty, the detection is
**unresolved** — do NOT skip. Mirror anyway (`cp CHECKPOINT.md
"$ARCHIVE/<slug>.md"`): a redundant file in `.checkpoints/` costs nothing,
whereas a skipped mirror loses the checkpoint permanently on teardown. Case D
never reaches this step: it already writes to `.checkpoints/<descriptive-slug>.md`
and skips Step 5.

#### Rationalizations to reject (Step 5b)

| Excuse                                                                                                              | Reality                                                                                                                                                                                                                     |
|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Step 5 says write CHECKPOINT.md at CWD — I followed the skill exactly"                                             | Step 5 was authored assuming CWD persists. In a linked worktree it does not. Step 5b is the other half of the same instruction, not an optional add-on.                                                                     |
| "Step 4's archive only fires for a PRE-EXISTING checkpoint; there isn't one, so nothing belongs in `.checkpoints/`" | Step 4 archives the *old* file; Step 5b archives the *new* one. Absence of a prior checkpoint does not make the new one safe from teardown.                                                                                 |
| "CHECKPOINT.md is a per-worktree file; its home is the worktree root"                                               | Its *meaning* is per-worktree; its *survival* needs a location that outlives the worktree. Both are required — the live file stays at CWD AND the mirror lands in `.checkpoints/`.                                          |
| "/checkpoint-resume reads CWD's CHECKPOINT.md, so CWD is the only place that matters"                               | After `git worktree remove` there is no CWD. The mirror at `.checkpoints/<slug>.md` is what a later session resumes from — see Step 8.                                                                                      |
| "The `--show-toplevel` detection failed, so I couldn't tell if CWD is a worktree — I left it CWD-only to be safe"   | Unresolved detection is a reason to mirror, not to skip. The conservative default is to mirror — a redundant `.checkpoints/` file is harmless; skipping on ambiguity is exactly the failure mode that loses the checkpoint. |

### Step 6 — Stage the file (or acknowledge it's intentionally untracked)

**Check project convention first.** Before staging, run:

```
git log --all --oneline -- CHECKPOINT.md | head -1
```

If the output is **empty**, `CHECKPOINT.md` has never been committed to this
repo — leaving it untracked is the project's convention even when not explicitly
listed in `.gitignore`. **Skip staging** and report:

> "Left `CHECKPOINT.md` untracked to match project convention (no prior commit
> touches this path; repo treats it as local-only scratch)."

This is the correct outcome, not a failure. Staging-by-default is only
appropriate when the repo has committed a `CHECKPOINT.md` before.

**If the output shows one or more commits**, the repo tracks CHECKPOINT.md as
part of its history — proceed:

```
git add CHECKPOINT.md
```

**If git refuses with "paths are ignored" (e.g. `CHECKPOINT.md` appears in the
project's `.gitignore`):** that is a deliberate project convention — some repos
treat `CHECKPOINT.md` as local-only scratch space and ignore it explicitly. Do
**NOT** force-add with `-f`. Instead, skip staging and report:

> "`CHECKPOINT.md` is gitignored by this project — left untracked, not staged.
> The file is still written at CWD and resumable locally."

This is the correct outcome, not a failure. Staging is a convenience for
projects that track checkpoints; it is not one of the invariants below.

**Any other `git add` failure** (permissions, disk full, not in a repo) —
surface the error to the user and stop; do not silently skip.

### Rationalizations to reject (Step 6)

| Excuse                                 | Reality                                                                                                                                                                                                 |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Not in `.gitignore`, so stage it"     | Gitignore is not the only convention signal. `git log --all -- CHECKPOINT.md` empty means the path has **never been tracked** — that's a stronger convention than gitignore. Check both before staging. |
| "Staging doesn't commit, no harm"      | Staging a file that's historically been untracked creates a round-trip (user has to unstage) and risks accidental commit if they `git commit -am` without reviewing staged state.                       |
| "The skill said `git add`, just do it" | The skill says stage _if the project wants it tracked_. A never-committed path is a clear signal the project does not. Check before obeying.                                                            |

### Step 7 — Report

Summarize to the user:

- Any archive action taken (Case A, B, or C from Step 4, or "no prior checkpoint
  existed").
- Whether Step 5b mirrored the checkpoint to `.checkpoints/<slug>.md` (linked
  worktree) or was skipped (main checkout).
- Confirmation that the new `CHECKPOINT.md` is written, and its staging status:
  either "staged", "intentionally untracked per project `.gitignore`", or
  "intentionally untracked per project convention (no prior commit history)".
- Invariants upheld (see below).

### Step 8 — Print resume footer (mandatory, every save)

Before this skill returns, print a copy-pasteable resume footer to the user.
This is **not optional** and **not interchangeable** with the Step 7 report —
Step 7 is prose ("staged" / "intentionally untracked"); Step 8 is a literal
shell-command + slash-command block the user can copy without retyping.

The footer template:

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
````

**Per-Case substitutions:**

- **Cases A, B, C** — `<ABSOLUTE-PATH-TO-CWD>` is the directory where the new
  `CHECKPOINT.md` was just written; the fallback prose is
  `Resume from CHECKPOINT.md`.
- **Case D** — `<ABSOLUTE-PATH-TO-CWD>` is still the CWD (CHECKPOINT.md was
  preserved in place), but the fallback prose becomes
  `Resume from .checkpoints/<descriptive-slug>.md` so the user knows to
  reference the named archive instead of the live CHECKPOINT.md, which belongs
  to the unrelated effort. `/checkpoint-resume` will not auto-find a Case-D
  archive — calling out the path is the only way the user reaches it.
- **Linked-worktree mirror (Step 5b ran)** — when CWD is a linked worktree the
  worktree may be removed before the next session. Append a second line to the
  footer so the durable copy is reachable:
  `If this worktree was removed: Resume from <MAIN_ROOT>/.checkpoints/<slug>.md`

**Why this fires every save:** the user opens a fresh session days later from a
terminal that has no scrollback. The resume footer is the only durable handoff
she sees at session start. Step 7's prose report doesn't survive context loss;
the footer's literal command block does.

#### Rationalizations to reject (Step 8)

| Excuse                                                              | Reality                                                                                                                                                                                                                                                                             |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "The CHECKPOINT.md path is obvious from earlier in the session"     | The user opens a fresh session days later from a terminal that has no scrollback; the resume footer is the only durable handoff she sees at session start. Always print it.                                                                                                         |
| "I already mentioned the path in Step 7's report"                   | Step 7's report is prose ("staged" / "intentionally untracked"). Step 8 is a copy-pasteable command block. The two are not interchangeable — the user must be able to copy-paste without re-typing or hunting for the path inside a sentence.                                       |
| "I'm under Case D, the user knows where her named archive is"       | She does not. Case D archives live under `.checkpoints/<slug>.md` — names she chose under time pressure mid-pause. Days later she will not recall whether it was `claude-damn-skills-roadmap` or `claude-damn-roadmap-skills` or just `roadmap`. Print the literal path.            |
| "/check-yourself's footer will print this — I don't need to repeat" | /check-yourself only prints the footer at pause/checkpoint boundaries. /checkpoint-save fires from many entry points (operator-direct, /pause flow, /super-tdd-cat finalization, etc.); not all of those route through /check-yourself afterward. Each skill prints its own footer. |

## Invariants

After every successful save, all three of the following must hold:

1. **CWD has exactly one `CHECKPOINT.md`** — it was just written.
2. **Its `**Branch:**` line matches the current git branch** — the template was
   filled in with the current branch.
3. **No prior checkpoint content has been lost** — any pre-existing
   `CHECKPOINT.md` was archived to `.checkpoints/` before overwrite (Case A →
   `.prev.md`; Case B → `<old-slug>.md`; Case C → `unparsed-<timestamp>.md`).
4. **If CWD is a linked worktree, a durable copy exists at
   `.checkpoints/<slug>.md`** — written by Step 5b, surviving `git worktree
   remove`. Not applicable in the main checkout (CHECKPOINT.md is already
   durable) or under Case D (which writes to `.checkpoints/` directly).

## Key Principles

- **Be specific:** "Fix the auth bug" is useless. "In
  `src/auth/middleware.py:47`, the token validation skips expiry check — add
  `exp` claim validation before the `return True` on line 52" is resumable.
- **Capture WHY:** Decisions without rationale get re-debated. Always include
  reasoning.
- **Include the resume prompt:** Make it copy-pasteable so resuming is one
  action.
- **Reference memories:** Link to any memory files that future-you will need.
  Don't duplicate their content — just point to them.
