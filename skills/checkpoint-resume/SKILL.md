---
name: checkpoint-resume
description:
  Use when resuming paused work, starting a session where a CHECKPOINT.md
  exists, or when the user says "continue from checkpoint", "resume", or "pick
  up where we left off"
user-invocable: true
---

# Checkpoint Resume

Resume work from a CHECKPOINT.md file. Rebuild full context and continue exactly
where we left off.

## Process

### Step 1 — Resolve the Archive Directory

Run:

```bash
COMMON_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
```

If this command exits non-zero, abort: **"Not a git repository.
checkpoint-resume requires a git repo at CWD."**

Then:

```bash
ARCHIVE=$(dirname "$COMMON_DIR")/.checkpoints
```

This resolves to the shared `.checkpoints/` directory at the main checkout root,
consistent across all worktrees.

### Step 2 — Slug Derivation

Derive `<current-slug>` from the current branch name:

1. Get branch: `git branch --show-current`
2. Lowercase the result.
3. Replace `/` with `-`.
4. Strip characters outside `[a-z0-9-]`.
5. Collapse consecutive `-`.
6. Detached HEAD fallback: use the basename of CWD, slugified the same way.

### Step 3 — Enumerate Available Checkpoints

Collect candidates:

- **Active checkpoint:** Check whether `CHECKPOINT.md` exists at CWD. If it
  does, parse its `**Branch:**` line.
- **Archive:** List `$ARCHIVE/*.md`, excluding any file matching `*.prev.md`
  (those are rolling same-branch backups, not paused efforts — do not offer them
  for resume).

### Step 4 — Decide Which Checkpoint to Resume

Apply the first matching case:

**Case A — CHECKPOINT.md present, branch matches current**

`CHECKPOINT.md` exists at CWD and its `**Branch:**` line matches the current git
branch. → Resume it. This is the normal case. Proceed to Step 5.

**Case B — CHECKPOINT.md present, branch differs from current**

`CHECKPOINT.md` exists at CWD but its `**Branch:**` line is for a different
branch than the one you are currently on. → Flag the drift and prompt the user:

> `CHECKPOINT.md` is for branch `<X>`, but you are currently on `<Y>`. How would
> you like to proceed?
>
> - **(a)** Resume it as-is (stay on current branch, use the checkpoint from
    > `<X>`)
> - **(b)** Archive it to `.checkpoints/<X-slug>.md` first, then pick a
    > checkpoint from the archive
> - **(c)** Resume a specific archived checkpoint — list the archive contents so
    > I can pick

Wait for the user's response before continuing.

**Case C — No CHECKPOINT.md at CWD, archive has `<current-slug>.md`**

`CHECKPOINT.md` does not exist at CWD, but `$ARCHIVE/<current-slug>.md` does
exist. → Offer to restore it:

> Found an archived checkpoint for the current branch (`<current-slug>`).
> Restore it to continue work?

On user confirmation: **move** (not copy) `$ARCHIVE/<current-slug>.md` to
`CHECKPOINT.md` at CWD, then proceed to Step 5. On user decline: stop and report
no active checkpoint to resume.

**Case D — No CHECKPOINT.md at CWD, no slug match, archive non-empty**

`CHECKPOINT.md` does not exist at CWD, `$ARCHIVE/<current-slug>.md` does not
exist, but the archive contains other `.md` files (excluding `*.prev.md`). →
List the archive contents and ask the user to pick:

> No checkpoint found for the current branch. The following archived checkpoints
> are available:
>
> 1. `.checkpoints/<slug-1>.md`
> 2. `.checkpoints/<slug-2>.md` ...
>
> Enter the number of the checkpoint to restore, or press Enter to cancel.

On pick: **move** (not copy) the chosen file to `CHECKPOINT.md` at CWD, then
proceed to Step 5. On cancel: stop and report no checkpoint restored.

**Case E — No CHECKPOINT.md and empty archive**

`CHECKPOINT.md` does not exist at CWD and the archive has no `.md` files
(excluding `*.prev.md`). → Report:

> No checkpoint found — neither a local `CHECKPOINT.md` nor any archived
> checkpoints exist. Nothing to resume.

Stop.

### Step 5 — Resume the Checkpoint

Once a `CHECKPOINT.md` is confirmed at CWD (either pre-existing or moved there
in Step 4):

1. Run `git status` to see current working tree state.
2. Run `git diff --stat` to see what changed since the checkpoint was written.
3. Read any memory files referenced in the checkpoint's **Relevant Memories**
   section.
4. Review the **Branch**, **Current State**, **Key Decisions Made**, and **Open
   Questions / Blockers** sections — flag any drift between the checkpoint's
   "Files Modified" list and actual file state.
5. Summarize the restored context to the user: what was done, what decisions
   were made, what is next.
6. Execute the first item from the checkpoint's **Next Steps** list.

## Invariant after Resume

After a successful resume:

- `CHECKPOINT.md` is present at CWD and reflects the resumed effort.
- The archive no longer contains the restored file — it was **moved**, not
  copied.
- The archive may still contain other paused efforts for other branches.

## Key Principles

- **Trust the checkpoint:** It was written with full session context. Don't
  second-guess decisions unless the user asks to revisit them.
- **Flag drift:** If files changed since the checkpoint was written (someone
  else committed, user edited manually), call it out before proceeding.
- **Ask about blockers:** If the checkpoint listed open questions, check if the
  user has answers before continuing.
- **Clean up after:** Once work is complete, delete or archive the CHECKPOINT.md
  so it doesn't confuse future sessions.
