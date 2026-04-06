---
name: checkpoint-save
description: Use when pausing work that will be resumed later, when switching contexts, or when the user asks to save a checkpoint. Creates a CHECKPOINT.md that captures full resumption context.
user-invocable: true
---

# Checkpoint Save

Pause here and create a checkpoint CHECKPOINT.md file to allow us to quickly resume work on this later. Use / reference
memories as needed.

## What to Capture

Create `CHECKPOINT.md` in the project root (or working directory) with:

```markdown
# Checkpoint: [Brief Title]

**Date:** [today's date]
**Branch:** [current git branch]
**Session context:** [1-2 sentence summary of what we were doing]

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

Run `git branch --show-current` to get the current branch name. If the output is empty (detached HEAD), fall back to
the basename of CWD (`basename "$PWD"`). Apply slug rules to produce `<slug>`:

1. Lowercase.
2. Replace `/` with `-`.
3. Strip characters outside `[a-z0-9-]`.
4. Collapse consecutive `-`.

### Step 2 — Resolve archive directory

Run:

```
COMMON_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
ARCHIVE=$(dirname "$COMMON_DIR")/.checkpoints
mkdir -p "$ARCHIVE"
```

This resolves to the **main checkout root's** `.checkpoints/` directory, ensuring all git worktrees share a single
archive.

### Step 3 — Verify `.gitignore` coverage

Check whether `.checkpoints/` is listed in the main checkout's `.gitignore` (the `.gitignore` at `$(dirname
"$COMMON_DIR")/.gitignore`). If the line is absent, append `.checkpoints/` to that `.gitignore` and report to the
user:

> "Added `.checkpoints/` to `.gitignore` in the main checkout. Please review and commit that change when ready."

Do NOT auto-commit — the user handles all git commits.

### Step 4 — Handle existing CHECKPOINT.md

If `CHECKPOINT.md` exists at CWD, parse its `**Branch:**` line and apply one of the three cases below:

**Case A — Same branch as current:**
Copy the existing file to `.checkpoints/<slug>.prev.md` (overwrite any prior `.prev.md`). This is a rolling
single-slot backup before the same-branch overwrite.

**Case B — Different branch:**
The existing checkpoint belongs to a different effort. Derive `<old-slug>` from the `**Branch:**` value in the
existing file (apply the same slug rules). Move (not copy) the existing `CHECKPOINT.md` to `.checkpoints/<old-slug>.md`.
On collision (file already exists), append `-2`, `-3`, etc. until the name is free. Report to the user:

> "Archived previous checkpoint (branch: `<old-branch>`) to `.checkpoints/<old-slug>.md`."

**Case C — Branch line missing or unparseable:**
The `**Branch:**` line cannot be found or its value is empty/malformed. Use the file's modification time to form a
timestamp: `mtime` formatted as `YYYYMMDD-HHMMSS`. Move the existing file to
`.checkpoints/unparsed-<YYYYMMDD-HHMMSS>.md`. Report to the user:

> "Could not parse branch from existing CHECKPOINT.md. Archived to `.checkpoints/unparsed-<YYYYMMDD-HHMMSS>.md`."

### Step 5 — Write new CHECKPOINT.md

Write a fresh `CHECKPOINT.md` at CWD using the template above, filling in all sections. Run `git status` and
`git diff --stat` to capture current state. Review active tasks/todos in the session. Check memory files for relevant
context to reference.

### Step 6 — Stage the file

```
git add CHECKPOINT.md
```

### Step 7 — Report

Summarize to the user:

- Any archive action taken (Case A, B, or C from Step 4, or "no prior checkpoint existed").
- Confirmation that the new `CHECKPOINT.md` is written and staged.
- Invariants upheld (see below).

## Invariants

After every successful save, all three of the following must hold:

1. **CWD has exactly one `CHECKPOINT.md`** — it was just written.
2. **Its `**Branch:**` line matches the current git branch** — the template was filled in with the current branch.
3. **No prior checkpoint content has been lost** — any pre-existing `CHECKPOINT.md` was archived to `.checkpoints/`
   before overwrite (Case A → `.prev.md`; Case B → `<old-slug>.md`; Case C → `unparsed-<timestamp>.md`).

## Key Principles

- **Be specific:** "Fix the auth bug" is useless. "In `src/auth/middleware.py:47`, the token validation skips expiry
  check — add `exp` claim validation before the `return True` on line 52" is resumable.
- **Capture WHY:** Decisions without rationale get re-debated. Always include reasoning.
- **Include the resume prompt:** Make it copy-pasteable so resuming is one action.
- **Reference memories:** Link to any memory files that future-you will need. Don't duplicate their content — just point
  to them.