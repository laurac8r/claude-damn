# Changelog

All notable changes to `claude-damn` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project is pre-1.0
so entries are grouped by development phase rather than SemVer.

## [Unreleased] — `feat/transition-to-plugin`

The plugin packaging phase: introducing `uv`, `pyproject.toml`, a real test
tree, and the first spec-plan-test skill (`sme-test`).

### Added

- **Plugin scaffolding**
   - `pyproject.toml` + `uv.lock` — uv-managed `.venv`, Python ≥ 3.14. All
     test/dev packages (`pytest`, `pyyaml`, `pytest-xdist`, `ruff`) in
     `[dependency-groups] dev`, no runtime dependencies.
   - `tests/` tree with `conftest.py` and shared helpers.

- **Harness test coverage**
   - `tests/test_extract_cost.py` — session JSONL parsing and Anthropic-pricing
     cost math, including fast-mode pricing branches.
   - `tests/test_checkpoint_archive.bats` — checkpoint archive rotation across
     branches.
   - `tests/test_hook_inline_scripts.py` — pre-tool hook that blocks multiline
     non-Bash scripts from the Bash tool.
   - `tests/test_permissions.py` — `settings.json` allow/ask/deny permission
     lists.
   - `tests/test_settings_structure.py` — `settings.json` schema invariants.
   - `tests/test_sync_theme.bats` — launchd theme-sync behaviour.

- **sme-test v1** skill at `skills/sme-test/` — Subject Matter Expert TDD coach
  with three modes (`coach` default, `expert` via `-x`, `expert-auto` via
  `-xa`).
   - `SKILL.md` entry point with frontmatter, mode docs, and shared-memory
     contract.
   - 5 prompt files: `coach-dispatch`, `three-whys`, `gwt-formulation`,
     `test-writer`, `red-gate`.
   - 2 runner adapters: `adapters/python/` and `adapters/bats/` implementing the
     4-capability contract.
   - `errors/error-handlers.md` covering 5 error classes with recovery paths.
   - 132 structural tests across `tests/skills/sme_test/` (SKILL.md, prompts,
     errors, adapters, cross-file integration). Layer 4 (dogfood) deferred to
     first real usage.
   - Approved design spec at
     `docs/superpowers/specs/2026-04-05-sme-test-design.md` and 12-task
     implementation plan at `docs/superpowers/plans/2026-04-05-sme-test.md`.

- **`/proceed` skill** at `skills/proceed/SKILL.md` — single-use
  user-invocable signal that authorizes Claude to pass the current approval
  gate only (design review, plan approval, risky-action confirmation). Body
  carries the literal phrase "Aligned and approved" and an explicit
  single-gate scope clarification so it does not grant standing authorization.
   - 5-level regression coverage under `tests/{structural,behavioral,integration,smoke,performance}/test_proceed.py`
     (23 default tests + 15 marker-gated smoke/performance cells). Mirrors the
     `/listen` test pattern. Behavioral layer uses TDD mutation checks.

- **Docs**
   - `README.md` — project overview, skill catalog, setup, project structure.
   - `ROADMAP.md` — 4-phase plugin transition plan.
   - `CHANGELOG.md` — this file.

- **PR review fixes** (PR #7 feedback)
   - `tests/test_pyproject.py` — regression test asserting test-only packages
     stay in dev dependency group.
   - `tests/skills/expert_review/` — structural tests for expert-review SKILL.md
     (duplicate bullet, Phase 0 numbering).
   - `scripts/test-isolated.sh` — error guards on worktree setup commands.

### Changed

- `expert-review` guidelines — added Java plus comprehensive language, security,
  and cloud specialization references.
- `expert-review` SKILL.md — removed duplicate "You combine the roles of..."
  bullet; fixed Phase 0 step numbering (1-5 sequential).
- `CLAUDE.md` — clarified agent directives: model routing, batch operations, no
  inline non-Bash scripts via heredocs, git-commit opt-out.
- `hooks/block-inline-scripts.py` — deny feedback moved from top-level
  `systemMessage` (persistent `<system-reminder>`) to
  `hookSpecificOutput.permissionDecisionReason` so the block message is scoped
  to the denied Bash call and no longer leaks into subsequent unrelated tool
  uses. Exception path now writes to stderr with exit 1 instead of emitting a
  persistent `systemMessage`. Tests updated.
- `CLAUDE.md` — documented the PreToolUse hook output contract (use
  `permissionDecisionReason`, not `systemMessage`); noted the repo hook's Bash
  limits (300 chars / 3 statement separators); documented the `.worktrees/`
  convention and gitignored `CHECKPOINT.md`.

## [Baseline] — Pre-plugin (`~/.claude` dotfiles)

The state the plugin transition inherits from: a flat `~/.claude` directory with
commands, skills, and tooling.

### Added

- **Slash commands:** `/review`, `/expert-review`, `/address-pr-feedback`,
  `/cost`, `/cost-opt`.
- **Skill catalog (38 skills)** composed from four modifiers (`tdd`, `super`,
  `duper`, `cat`):
   - **TDD family:** `/tdd`, `/tdd-cat`, `/duper-tdd`, `/duper-tdd-cat`.
   - **Brainstorm + TDD:** `/super`, `/super-cat`, `/super-duper`,
     `/super-duper-cat`.
   - **Debug + Brainstorm + TDD:** `/super-debug-and-fix` and the `duper` /
     `cat` variants.
   - **Expert Review:** `/expert-review` through
     `/expert-super-duper-cat-review` (10 variants).
   - **Lifecycle:** `/checkpoint-save`, `/checkpoint-resume`, `/check-yourself`,
     `/continue`.
   - **PR feedback:** `/fast-pr-feedback-to-me`, `/fast-pr-feedback-to-others`,
     `/fast-pr-final-self-review`.
   - **Utility:** `/cost_`, `/cost-opt`, `/draft-cmt-msg-4-below`, `/enforce`.
   - Full combinatoric table in `skills/README.md`.
- `extract_cost.py` — parses Claude Code session JSONL files, computes real
  token usage and cost via Anthropic pricing, logs to `~/.claude/cost-log/` as
  JSONL.
- `statusline-command.sh` — shell statusline showing per-session cost.
- `settings.json` — permission allow/ask/deny rules, pre-tool hooks, script
  execution policy.
- `policy-limits.json` — remote control restrictions.
- `com.claude.sync-theme.plist` — macOS launchd plist for theme-sync service.
- `CLAUDE.md` — opinionated project rules for model routing, testing standards,
  Python style, and FastAPI architecture.
- MIT `LICENSE`.

### Changed

- Renamed project `awesome-bruno` → `awesome-claude` → `claude-damn`.
- Flattened nested directories out of the symlinked tree; removed stray
  symlinks.
- `.gitignore` added to exclude IDE config.
