# claude-damn

A composable skill library and opinionated harness for
[Claude Code](https://docs.anthropic.com/en/docs/claude-code). Ships slash
commands, skills, hooks, permission guards, and cost-tracking tooling that layer
on top of the
[superpowers](https://github.com/anthropics/claude-plugins-official/tree/main/superpowers)
plugin.

<img src="img/home-meme.png" alt="home meme" width="800">

Currently on branch `feat/transition-to-plugin` — converting the flat
`~/.claude` layout into a proper plugin package with tests, `pyproject.toml`,
and `uv`-managed dependencies. See [`ROADMAP.md`](ROADMAP.md) for the transition
plan and [`CHANGELOG.md`](CHANGELOG.md) for what's landed. Design specs and
implementation plans live in `docs/superpowers/{specs,plans}/`.

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
`/fast-pr-feedback-to-others`, `/fast-pr-final-self-review`, `/sync`, and more.

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

### 1. Enable the official plugin marketplace

In Claude Code, confirm you can access plugins from `claude-plugins-official`.
If prompted, approve marketplace access:

```
claude plugins list
```

### 2. Install required plugins

At minimum, install **superpowers** — the skill engine this repo builds on:

```
claude plugins install superpowers@claude-plugins-official
```

The full set used by this project (all from `claude-plugins-official`):

```
superpowers          # Core skill engine — required
code-review          # PR review workflows
frontend-design      # UI/UX skill
code-simplifier      # Code cleanup
feature-dev          # Guided feature development
skill-creator        # Create/edit skills
security-guidance    # Security audit
pr-review-toolkit    # Multi-agent PR review
agent-sdk-dev        # Agent SDK scaffolding
hookify              # Hook rule creation
chrome-devtools-mcp  # Browser DevTools via MCP
playground           # Interactive HTML playgrounds
remember             # Session handoff notes
```

### 3. Clone this repo

```bash
git clone <repo-url> claude-damn
cd claude-damn
```

### 4. Copy skills and config to your Claude Code home

```bash
# Skills
cp -r skills/* ~/.claude/skills/

# Project settings (review before overwriting — merges with your existing config)
# settings.json contains permissions, hooks, enabled plugins, and model routing
cp settings.json ~/.claude/settings.json

# Project instructions
cp CLAUDE.md ~/.claude/CLAUDE.md
```

> **Note:** If you already have a `~/.claude/settings.json` or
> `~/.claude/CLAUDE.md`, merge manually rather than overwriting. The
> `settings.json` in this repo includes hook definitions, permission
> allow/ask/deny lists, and plugin enablement that you may want to adapt to your
> own setup.

### 5. Verify

Open a new Claude Code session and run a skill to confirm everything loaded:

```
/expert-review
```

You should see the skill content expand in your session.

## Project structure

```
.
├── CLAUDE.md                  # Project instructions (model routing, style, testing)
├── CHECKPOINT.md              # Current work-in-progress checkpoint
├── settings.json              # Claude Code harness config (permissions, hooks, plugins)
├── .prettierrc                # Prettier config for Markdown
├── skills/
│   ├── README.md              # Full combinatoric skill table
│   ├── tdd/                   # Base TDD workflow
│   ├── super/                 # Brainstorm + TDD
│   ├── duper/                 # Git worktree isolation
│   ├── cat/                   # Subagent-driven development
│   ├── expert-review/         # Multi-phase expert review
│   ├── expert-*-review/       # 9 combinatoric expert-review variants
│   ├── checkpoint-save/       # Save resumable checkpoint
│   ├── checkpoint-resume/     # Resume from checkpoint
│   ├── check-yourself/        # Post-step self-check
│   └── ...                    # 37 skills total
├── tests/
│   ├── test_checkpoint_archive.bats
│   ├── test_extract_cost.py
│   ├── test_hook_inline_scripts.py
│   ├── test_permissions.py
│   └── test_settings_structure.py
└── docs/
    └── superpowers/           # Design specs
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
