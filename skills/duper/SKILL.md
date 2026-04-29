---
name: duper
description: Isolated git worktree workflow (alias for /using-git-worktrees)
user-invocable: true
---

## Prerequisites

Before proceeding, ask the user to enable **auto-accept edits** if it is not
already on. Worktree workflows involve many file writes and edits across
isolated checkouts — manual approval of each edit significantly slows the
workflow. Use `AskUserQuestion` to request this:

> This workflow writes and edits many files in an isolated worktree. Please
> enable **auto-accept edits** (press `a` or use `/allowed-tools`) so I can work
> efficiently. Ready to proceed?

Wait for confirmation before continuing.

### If the operator declines auto-accept

If the operator declines auto-accept, **STOP**. Subagent `Write`/`Edit` tool
calls will be silently denied by Claude Code's manual-approval permission
system, producing the generic error
`"Permission to use Write has been denied."`. Do NOT proceed into dispatch — the
failures will look like hook denials and trigger misdiagnosis.

Surface this tradeoff explicitly and require an explicit choice before
proceeding:

- **(a)** Flip auto-accept on now, then re-run.
- **(b)** Operator-performed inline edits in the worktree (no isolated
  dispatch).
- **(c)** Abort and route the work elsewhere (different workflow, different
  session).

Do not silently proceed. The whole point of asking for auto-accept up front is
that subagent dispatch is incompatible with manual-approval mode.

## Workflow

/using-git-worktrees
