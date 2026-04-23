# claude-damn

A composable skill library and opinionated harness for
[Claude Code](https://docs.anthropic.com/en/docs/claude-code). Ships slash
commands, skills, hooks, permission guards, and cost-tracking tooling that layer
on top of the
[superpowers](https://github.com/anthropics/claude-plugins-official/tree/main/superpowers)
plugin.

<img src="img/home-meme.png" alt="home meme" width="800">

Install via the official Claude Code marketplace:

```
/plugin install claude-damn@claude-plugins-official
```

See [`ROADMAP.md`](ROADMAP.md) for what's next and
[`CHANGELOG.md`](CHANGELOG.md) for what's landed. Design specs live in
`docs/superpowers/{specs,plans}/`.

## What's in the box

### Skills (slash commands)

Skills compose from four modifiers — stack them to build the workflow you need:

| Modifier | What it adds                            |
| -------- | --------------------------------------- |
| `super`  | Brainstorm requirements first, then TDD |
| `duper`  | Isolated git worktree                   |
| `cat`    | Parallel subagent execution             |
| `tdd`    | Test-driven development                 |

These combine into four skill families:

- **TDD** — `/tdd`, `/tdd-cat`, `/duper-tdd`, `/duper-tdd-cat`
- **Brainstorm + TDD** — `/super`, `/super-cat`, `/super-duper`,
  `/super-duper-cat`
- **Debug + Brainstorm + TDD** — `/super-debug-and-fix`,
  `/super-debug-and-fix-cat`, `/super-duper-debug-and-fix`,
  `/super-duper-debug-and-fix-cat`
- **Expert Review** — `/expert-review` through `/expert-super-duper-cat-review`
  (10 variants)

Plus utility skills: `/checkpoint-save`, `/checkpoint-resume`,
`/check-yourself`, `/cost_`, `/cost-opt`, `/fast-pr-feedback-to-me`,
`/fast-pr-feedback-to-others`, `/fast-pr-final-self-review`, `/listen`,
`/proceed`, `/sync`, and more.

See [`skills/README.md`](skills/README.md) for the full combinatoric table.

### Harness features

- **Permission guards** — granular allow/ask/deny rules in `settings.json`
  (blocks destructive GitHub CLI operations, gates commits, protects settings
  files)
- **Inline-script hook** — pre-tool hook that blocks multiline non-Bash scripts
  from running inside the Bash tool
- **Cost tracking** — `/cost_` extracts per-session token usage from JSONL logs;
  `/cost-opt` compacts and reviews optimization suggestions
- **Checkpoint system** — save/resume work across sessions with automatic
  archive rotation per branch
- **CLAUDE.md** — opinionated project rules for model routing, testing
  standards, Python style, and FastAPI architecture

## Setup

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
  and authenticated
- Git

### Install from the marketplace (recommended)

```
/plugin install claude-damn@claude-plugins-official
```

This registers every skill, command, and the inline-script PreToolUse hook.
Restart or reload the session once to pick up the hook.

### Companion plugins

`claude-damn` layers on top of `superpowers`. Install it if you don't have it
already:

```
/plugin install superpowers@claude-plugins-official
```

Other marketplace plugins the skill set composes with (all optional):

| Plugin                | What it adds                 |
| --------------------- | ---------------------------- |
| `code-review`         | PR review workflows          |
| `frontend-design`     | UI/UX skill                  |
| `code-simplifier`     | Code cleanup                 |
| `feature-dev`         | Guided feature development   |
| `skill-creator`       | Create/edit skills           |
| `security-guidance`   | Security audit               |
| `pr-review-toolkit`   | Multi-agent PR review        |
| `agent-sdk-dev`       | Agent SDK scaffolding        |
| `hookify`             | Hook rule creation           |
| `chrome-devtools-mcp` | Browser DevTools via MCP     |
| `playground`          | Interactive HTML playgrounds |
| `remember`            | Session handoff notes        |

### Verify

Open a new Claude Code session and invoke any skill — e.g.:

```
/expert-review
```

The skill content should expand in your session.

### Personalize (optional)

Operator-specific preferences (commit style, model routing, subagent delegation
targets) go in `~/.claude/rules/PERSONALIZATION.md`. Copy the template and edit
to taste:

```bash
cp rules/PERSONALIZATION.example.md ~/.claude/rules/PERSONALIZATION.md
```

`CLAUDE.md` holds general engineering rules that apply to every clone and should
stay in sync with upstream.

### Manual install (contributors / local dev)

If you're hacking on `claude-damn` itself rather than consuming it, clone the
repo and run the test suite directly:

```bash
git clone https://github.com/laurac8r/claude-damn
cd claude-damn
uv sync
uv run pytest
```

Point Claude Code at the local checkout via `claude --plugin-dir .` to test
changes without going through the marketplace.

## Quickstart

A few skill invocations to get a feel for the workflow:

```
/tdd                 # Start a test-driven development loop
/super                # Brainstorm first, then TDD
/super-duper-cat      # Brainstorm + worktree isolation + parallel subagents
/expert-review        # Multi-phase expert code review
/checkpoint-save      # Save resumable work state
/checkpoint-resume    # Pick up where you left off
/cost_                # Log this session's token spend
```

See [`skills/README.md`](skills/README.md) for the full combinatoric table of
how `super` / `duper` / `cat` / `tdd` compose into 20+ skill variants.

## Project structure

```
.
├── .claude-plugin/
│   └── plugin.json            # Plugin manifest (name, version, author, keywords)
├── CLAUDE.md                  # Project instructions (model routing, style, testing)
├── README.md                  # This file
├── LICENSE                    # MIT
├── settings.json              # Default harness config (permissions, hooks, plugins)
├── pyproject.toml             # Python tooling (uv, pytest, ruff, ty)
├── skills/                    # Auto-discovered skills (38+ SKILL.md entries)
│   ├── README.md              # Full combinatoric skill table
│   ├── tdd/                   # Base TDD workflow
│   ├── super/                 # Brainstorm + TDD
│   ├── duper/                 # Git worktree isolation
│   ├── cat/                   # Subagent-driven development
│   ├── expert-review/         # Multi-phase expert review
│   ├── expert-*-review/       # 9 combinatoric expert-review variants
│   ├── checkpoint-save/       # Save resumable checkpoint
│   ├── checkpoint-resume/     # Resume from checkpoint
│   ├── tesseract/             # Cross-session memory via file I/O
│   └── ...
├── hooks/
│   ├── hooks.json             # PreToolUse registration
│   └── block-inline-scripts.py # Guardrail for multiline non-Bash scripts
├── src/
│   └── extract_cost.py        # Token-usage parser for session JSONL logs
├── scripts/
│   └── statusline-command.sh  # Per-session cost in the statusline
├── tests/                     # pytest + bats suite
└── docs/
    └── superpowers/           # Design specs (sme-test, sme-review, etc.)
```

## Running tests

Tests are organized by fidelity level. Default `uv run pytest` runs everything
except `smoke` and `performance` (see `pyproject.toml` markers).

| Kind        | Location             | What it checks                                          | Command                                                              |
| ----------- | -------------------- | ------------------------------------------------------- | -------------------------------------------------------------------- |
| Structural  | `tests/structural/`  | Files, dirs, frontmatter — cheap existence checks       | `uv run pytest tests/structural/`                                    |
| Behavioral  | `tests/behavioral/`  | Skill body content and protocol rules                   | `uv run pytest tests/behavioral/`                                    |
| Integration | `tests/integration/` | Repo-wide references and cross-file consistency         | `uv run pytest tests/integration/`                                   |
| Harness     | `tests/test_*.py`    | `settings.json`, permissions, hooks, cost extraction    | `uv run pytest tests/test_*.py`                                      |
| Bats        | `tests/*.bats`       | Shell scripts (`checkpoint-archive`, `sync-theme`)      | `bats tests/test_checkpoint_archive.bats tests/test_sync_theme.bats` |
| Smoke       | `tests/smoke/`       | Live skill invocation (costs tokens, non-deterministic) | `uv run pytest -m smoke`                                             |
| Performance | `tests/performance/` | Stress matrix (18 combos, expensive, non-deterministic) | `uv run pytest -m performance`                                       |

Run everything cheap and deterministic:

```bash
uv run pytest
```

Run the full suite including live/expensive tests:

```bash
uv run pytest -m ""
```

### Parallel execution

For the slower suites (`performance/`, `smoke/`, or `-m ""`), run tests in
parallel with [`pytest-xdist`](https://pytest-xdist.readthedocs.io/):

```bash
uv add --dev pytest-xdist # one-time install
uv run pytest -n auto # auto = one worker per CPU core
uv run pytest -n 4 -m performance # pin worker count for the 18-combo stress matrix
```

Skip `-n` for the default suite — it runs in ~0.5s, and xdist worker startup
adds more overhead than it saves.

## License

[MIT](LICENSE)
