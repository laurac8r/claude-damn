---
name: expert-tdd-cat-review
description:
   Expert-level review with subagents, then fix using TDD with subagents
argument-hint: "[scope] [target|directive]"
user-invocable: true
---

/expert-review all with /cat, then fix using /tdd with /cat

## TDD execution mode (third axis)

The fix phase inherits the A/B TDD execution-mode axis defined in
`skills/tdd-cat/SKILL.md`: **Mode A** (split-phase: one RED/GREEN/REFACTOR
phase per subagent) vs **Mode B** (micro-cycle: full `/tdd` loop inside each
subagent). Ask it as the **third question** in `/cat`'s combined pre-dispatch
`AskUserQuestion` — **never default it silently**.
