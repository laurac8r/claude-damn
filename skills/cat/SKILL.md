---
name: cat
description:
  Subagent-driven development (alias for /subagent-driven-development)
user-invocable: true
---

## Prerequisites

Before proceeding, ask the user to enable **auto-accept edits** if it is not
already on. Subagent-driven development involves many file writes and edits
across parallel agents — manual approval of each edit significantly slows the
workflow. Use `AskUserQuestion` to request this:

> This workflow writes and edits many files via subagents. Please enable
> **auto-accept edits** (press `a` or use `/allowed-tools`) so I can work
> efficiently. Ready to proceed?

Wait for confirmation before continuing.

## Workflow

/subagent-driven-development
