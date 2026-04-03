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

1. Run `git status` and `git diff --stat` to capture current state
2. Review any active tasks/todos in the session
3. Check memory files for relevant context to reference
4. Write CHECKPOINT.md with all sections filled in
5. Stage the checkpoint file: `git add CHECKPOINT.md`

## Key Principles

- **Be specific:** "Fix the auth bug" is useless. "In `src/auth/middleware.py:47`, the token validation skips expiry
  check — add `exp` claim validation before the `return True` on line 52" is resumable.
- **Capture WHY:** Decisions without rationale get re-debated. Always include reasoning.
- **Include the resume prompt:** Make it copy-pasteable so resuming is one action.
- **Reference memories:** Link to any memory files that future-you will need. Don't duplicate their content — just point
  to them.