---
name: checkpoint-resume
description: Use when resuming paused work, starting a session where a CHECKPOINT.md exists, or when the user says "continue from checkpoint", "resume", or "pick up where we left off"
user-invocable: true
---

# Checkpoint Resume

Resume work from a CHECKPOINT.md file. Rebuild full context and continue exactly where we left off.

## Process

1. Read `CHECKPOINT.md` from the project root (or working directory)
2. Run `git status` and `git diff --stat` to see what changed since the checkpoint
3. Read any memory files referenced in the checkpoint
4. Review the **Next Steps** section — the first item is your immediate action
5. Summarize the restored context to the user: what was done, what's next
6. Begin executing the next step

## Context Rebuild Order

1. **Branch:** Verify you're on the correct branch listed in the checkpoint
2. **State:** Compare current file state against the checkpoint's "Files Modified" list — flag any drift
3. **Decisions:** Read "Key Decisions Made" so you don't re-debate resolved questions
4. **Blockers:** Check "Open Questions / Blockers" — ask the user if any have been resolved
5. **Resume:** Execute from the "Next Steps" list

## Key Principles

- **Trust the checkpoint:** It was written with full session context. Don't second-guess decisions unless the user asks to revisit them.
- **Flag drift:** If files changed since the checkpoint was written (someone else committed, user edited manually), call it out before proceeding.
- **Ask about blockers:** If the checkpoint listed open questions, check if the user has answers before continuing.
- **Clean up after:** Once work is complete, delete or archive the CHECKPOINT.md so it doesn't confuse future sessions.