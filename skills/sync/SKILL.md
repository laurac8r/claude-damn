---
name: sync
description:
   Sync files between two local directories, repos, or git worktrees. Five modes
   (plan/interactive/push/pull/mirror), .gitignore-aware, Claude-workflow
   allowlist via --claude, dropbox-restore-style per-directory prompts.
argument-hint:
   "[--from PATH] <target | --to PATH> [--mode
   plan|interactive|push|pull|mirror] [--dry-run] [--yes] [--limit N] [--include
   GLOB] [--exclude GLOB] [--no-gitignore] [--delete] [--claude]"
user-invocable: true
---

# /sync

Sync files between two local directories. Source defaults to `$PWD` (or set
explicitly with `--from`). Target is the first positional argument or `--to`
(exactly one — passing both raises "target: use positional or --to, not both").

## When the user types `/sync ...`

1. **Parse the user's arguments** and translate shorthand:
   - If the user's first token is a mode name (`plan`, `interactive`, `push`,
     `pull`, `mirror`), rewrite it to `--mode <name>`. The script treats any
     bare positional as the `target` directory, so `plan` as a bare arg
     collides with `--to` and errors.
   - Strip any leading `@` from path tokens (e.g. `@.claude/docs/…` →
     `.claude/docs/…`). `@` is a convention from the Claude Code slash-command
     surface, not a valid shell path.
   - If the user passes a literal placeholder like `<every …>`, don't pass it
     through — expand it to concrete paths first, or tell the user you need a
     real path.
2. **Run from the `claude-damn` repo root** (the directory containing
   `pyproject.toml`; locate it with `git rev-parse --show-toplevel` if needed):
   ```bash
   PYTHONPATH="$HOME/.claude" python3 -m skills.sync.scripts.sync <args>
   ```
   If you are in a claude-damn worktree (`.worktrees/<slug>`), that also works
   — the module is available from any checkout. Don't `cd` into the source or
   target being synced; `cd` into the repo that hosts the sync module.
3. **Show the output to the user.**

### Concrete invocation examples

```bash
# Plan a sync: /foo → /bar with the Claude allowlist (gitignored files kept)
uv run python -m skills.sync.scripts.sync --mode plan --claude \
  --from /Users/you/src --to /Users/you/dst

# Execute a push after plan-mode approval
uv run python -m skills.sync.scripts.sync --mode push --yes --claude \
  --from /Users/you/src --to /Users/you/dst

# Positional target (equivalent to --to), source defaults to $PWD
uv run python -m skills.sync.scripts.sync --mode plan /Users/you/dst
```

**Common translation mistakes — do not do these:**

```bash
# ❌ BAD: `plan` becomes the positional target, collides with --to
uv run python -m skills.sync.scripts.sync plan --claude --to /Users/you/dst
#   error: target: use positional or --to, not both

# ❌ BAD: bare @ prefix on the target path
uv run python -m skills.sync.scripts.sync --mode plan --claude \
  --from /src @/Users/you/dst
```

## Modes

| Mode          | Behavior                                                                                                                |
| ------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `plan` (def.) | Print the plan and exit. **Chat with the user to refine** (add excludes, change scope), then re-run in a non-plan mode. |
| `interactive` | Source → target, prompting y/n/a per directory.                                                                         |
| `push`        | Source → target, non-interactive. Requires `--delete` to remove target-only files.                                      |
| `pull`        | Target → source, non-interactive.                                                                                       |
| `mirror`      | Bidirectional; newer mtime wins; `--delete` needed for removals.                                                        |

## Plan-mode chat loop (the default)

When `--mode plan` is used (or no `--mode` is given), you MUST:

1. Run the command and show the rendered plan.
2. Ask the user if the plan looks right. Suggest common refinements:
   - "Want me to exclude `node_modules/` / `dist/` / anything else?"
   - "Should I also include Claude files (`--claude`)?"
   - "Which mode do you want when we execute — push, pull, or mirror?"
3. Re-run `--mode plan` with updated flags until the user says "go".
4. Then run the same command again with the chosen mode (e.g.
   `--mode push --yes`) to execute.

## `--claude` flag

Opt-in. Carries over a curated allowlist of Claude-workflow files (`CLAUDE.md`,
`.claude/skills/`, `.remember/`, `docs/superpowers/`, etc.) even when they're
gitignored. Ephemeral state like `.claude/projects/`, `.claude/plugins/`,
`.claude/cache/` is **always** excluded — users cannot opt back in. The built-in
allowlist can be overridden with `~/.claude/sync-allowlist.txt` (one glob per
line).

## Safety guarantees

- `.git/` is never copied.
- All subprocess calls use explicit argv; never `shell=True`.
- Failures surface as non-zero exit codes with error messages on stderr.
- `plan` mode writes nothing. `--dry-run` on any other mode writes nothing.
