---
name: duper-tdd-cat
description:
   TDD workflow using an isolated git worktree with subagent-driven-development
argument-hint: "[<task-description>]"
user-invocable: true
---

/tdd but using /duper with /cat

## TDD execution mode (third axis)

This composition inherits the A/B TDD execution-mode axis defined in
`skills/tdd-cat/SKILL.md`: **Mode A** (split-phase: one RED/GREEN/REFACTOR
phase per subagent) vs **Mode B** (micro-cycle: full `/tdd` loop inside each
subagent). Ask it as the **third question** in `/cat`'s combined pre-dispatch
`AskUserQuestion` — **never default it silently**.
