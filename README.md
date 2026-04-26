# claude-damn

A composable skill library and opinionated harness for
[Claude Code](https://docs.anthropic.com/en/docs/claude-code). Ships slash
commands, skills, hooks, permission guards, and cost-tracking tooling that layer
on top of the
[superpowers](https://github.com/anthropics/claude-plugins-official/tree/main/superpowers)
plugin.

<img src="img/home-meme.png" alt="home meme" width="800">

> **⏳ Status:** v1.0.0 submitted to the official Claude Code marketplace on
> 2026-04-23; **awaiting Anthropic review**. Until approval lands, install via
> the local / git path below (the `/plugin install` command will start working
> once the submission is accepted — watch `CHANGELOG.md` for the flip).

Install ahead of marketplace approval:

```bash
# Point Claude Code at a local clone
git clone https://github.com/laurac8r/claude-damn
claude --plugin-dir ./claude-damn
```

Once approved, this becomes:

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

### Install from the marketplace (post-approval)

> **Not yet available.** v1.0.0 is awaiting Anthropic marketplace review as of
> 2026-04-23. Once accepted, the command below will work. Until then, use the
> pre-approval install path under "Manual install" below.

```
/plugin install claude-damn@claude-plugins-official
```

This will register every skill, command, and the inline-script PreToolUse hook.
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

### Manual install (pre-approval, and for contributors)

Until the marketplace submission is approved, this is the primary install path.
It's also the right path if you're hacking on `claude-damn` itself:

```bash
git clone https://github.com/laurac8r/claude-damn
cd claude-damn
uv sync        # dev/test dependencies
uv run pytest  # 422 tests green
```

Then point Claude Code at the local checkout so skills, commands, and the
PreToolUse hook load:

```bash
claude --plugin-dir /absolute/path/to/claude-damn
```

Or use `--add-dir` to allow tool access without registering as a plugin:

```bash
claude --add-dir /absolute/path/to/claude-damn
```

Once the marketplace submission is approved, you can remove the local clone and
switch to `/plugin install claude-damn@claude-plugins-official`.

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
├── skills/                    # Auto-discovered skills (one SKILL.md per skill)
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

## Privacy

`claude-damn` runs entirely on your local machine. The plugin itself does not
collect, transmit, store, or share any user data with the author or any
third-party service. Specifically:

- **Skills and hooks execute locally.** Every skill, every hook, every script
  runs inside your Claude Code session on your own filesystem. Nothing is phoned
  home to a `claude-damn` server — there is no `claude-damn` server.
- **Cost-tracking artifacts stay on-disk.** `/cost_` writes session token-usage
  logs to `~/.claude/cost-log/` and `~/.claude/COST-SUMMARY.md`. `/cost-opt`
  reads and compacts those same files. None of this is uploaded anywhere.
- **Checkpoint state stays in-repo.** `/checkpoint-save` writes `CHECKPOINT.md`
  to your working tree and archives to `.checkpoints/` — local files only.
- **Tesseract transmissions are local-only.** `/tesseract` reads and writes
  `~/.claude/tesseract/shelf/*.md` and `~/.claude/tesseract/bulk-beings.md` on
  your disk. The skill explicitly advises gitignoring these files in any repo
  that mirrors `~/.claude`.

**Upstream data flows the plugin does not govern:**

- Your prompts and Claude's responses travel to Anthropic as part of normal
  Claude Code operation. That is governed by
  [Anthropic's privacy policy](https://www.anthropic.com/legal/privacy), not
  this plugin.
- Skills that shell out to `gh`, `git`, `curl`, or other tools follow the
  privacy practices of those tools and any remote services they talk to.

If any future version of `claude-damn` adds data collection or transmission,
this section will be updated before that version ships.

## License

[MIT](LICENSE)
