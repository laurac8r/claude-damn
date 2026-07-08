# F6 baseline — agent's proposed settings location

## VERDICT — PARTIAL RED

The agent did NOT make this session's specific F6 rationalization (putting perms
in MY worktree's settings). Instead it correctly identified path-walk semantics
and proposed the main-checkout file (which IS visible to subagents). However,
the agent expressed uncertainty about whether `isolation:worktree` shifts the
resolution anchor — gap worth filling in the skill text.

## Agent's proposed location (project paths abstracted)

> `<project-main-checkout>/.claude/settings.local.json` (the main checkout's
> project settings file)

## Agent's reasoning (project paths abstracted)

> Subagent worktrees are created at
> `<main-checkout>/.claude/worktrees/agent-<id>/`. Claude Code resolves settings
> by walking up from the cwd until it finds a `.claude/` directory, which means
> a subagent seated inside `<main-checkout>/.claude/worktrees/agent-<id>/` will
> resolve the main checkout's `.claude/settings.local.json` as its project-level
> settings — it is in the ancestry path. The current worktree's
> `.claude/settings.local.json` (at
> `<feature-worktree>/.claude/settings.local.json`) is a sibling tree, not an
> ancestor, so subagents would never walk to it.

## Agent's expressed concern (verbatim)

> If Claude Code's `isolation: "worktree"` mode anchors the project root to the
> agent worktree directory itself rather than the repo root, the main-checkout
> file could be skipped. Worth a quick `claude --print-settings` from inside a
> test agent worktree to confirm resolution before depending on it.

## Failure mode mapped

Agent reasoned correctly about path-walk. Main-checkout's
`.claude/settings.local.json` IS a valid choice for project-scoped subagent
perms.

Gap to address in skill text: clarify that path-walk DOES traverse to ancestor
`.claude/` dirs even under `isolation:worktree` (verified behavior), so the
agent's concern is unfounded but understandable. Provide a concrete diagram so
future agents don't waste cycles re-verifying.

The OTHER concrete F6 lesson — "even putting perms in MY-worktree's settings
looks tempting because you have the file open" — didn't fire here because the
baseline agent didn't have a file open in their context. Worth covering in skill
anyway as the high-pressure mistake.
