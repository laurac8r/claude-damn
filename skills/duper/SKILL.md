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

## Workflow

/using-git-worktrees
