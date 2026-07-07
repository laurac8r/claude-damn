# F1 baseline — agent's written subagent prompt

The baseline agent (no /super-duper-tdd-cat skill loaded) was asked to write a
subagent prompt under parallel-fanout pressure. Below is what it wrote, with
project-specific paths abstracted.

## VERDICT — RED (rationalization fired)

The prompt includes the parent worktree's absolute path, exactly the F1
rationalization. Rationale captured: " front-loads all necessary context
(location, hypothesis, expected HEAD SHA, stash name) so the stateless subagent
can orient immediately without back-communication."

## Agent's written prompt (project paths abstracted)

> **<HYPOTHESIS-NAME> Worker — <BUG-DESCRIPTION>**
>
> You are one of three parallel subagents debugging <bug>. Your job is to test
> the <hypothesis> hypothesis: <hypothesis description>.
>
> **Project location:** `<project-worktree-absolute-path>` (<framework> app
> under `<subdir>/`)
>
> **Step 1 — Confirm isolated worktree.** Verify cwd is under
> `.claude/worktrees/agent-<id>/`, not the main checkout. If in main checkout,
> stop.
>
> **Step 2 — Verify branch state.** Run `git status` and `git log --oneline -3`.
> Expected HEAD: `<commit-sha>`. If HEAD differs, report and stop.
>
> **Step 3 — Apply WIP stash.** Run `git stash apply stash^{/<wip-stash-name>}`.
> If stash not found, report and stop.
>
> [...steps 4-7 omitted; full content available in agent's session output...]

## Failure mode mapped

The agent volunteered a NEW guard ("verify cwd is under
`.claude/worktrees/agent-<id>/`, not the main checkout") — useful but
insufficient. The absolute path in the "Project location" field still primes the
subagent to use it as edit target if the agent's `cd`/path-resolution logic
misfires. The agent treats parent-worktree-path as load-bearing context the
subagent "needs," when the subagent's own cwd already provides it.
