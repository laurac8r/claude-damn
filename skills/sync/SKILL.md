---
name: sync
description:
  Sync files between two local directories, repos, or git worktrees. Five modes
  (plan/interactive/push/pull/mirror), .gitignore-aware, Claude-workflow
  allowlist via --claude, dropbox-restore-style per-directory prompts.
argument-hint:
  "[target] [--mode plan|interactive|push|pull|mirror] [--from PATH] [--dry-run]
  [--yes] [--limit N] [--include GLOB] [--exclude GLOB] [--no-gitignore]
  [--delete] [--claude]"
user-invocable: true
---

# /sync

Sync files between two local directories. Source defaults to `$PWD`. Target is
the first positional argument or `--to`.

## When the user types `/sync ...`

1. Parse the user's arguments.
2. Run from the repo root (where `pyproject.toml` lives):
   ```bash
   uv run python -m skills.sync.scripts.sync <args>
   ```
3. Show the output to the user.

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
