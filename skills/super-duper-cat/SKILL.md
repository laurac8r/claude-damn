---
name: super-duper-cat
description:
   Brainstorming workflow using an isolated git worktree with
   subagent-driven-development
user-invocable: true
---

/super but using /duper with /cat

Sequence:

1. Invoke `/super` (brainstorming) to design the work.
2. Invoke `/duper` (isolated git worktree) to set up the workspace before any
   implementation.
3. Invoke `/cat` (subagent-driven development) to execute the plan inside that
   worktree.

Each leg is a Skill-tool invocation in its own right; do not assume one
composition implies another. If a leg is skipped, name it explicitly and explain
why.
