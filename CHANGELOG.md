# Changelog

All notable changes to `claude-damn` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project is pre-1.0
so entries are grouped by development phase rather than SemVer.

## [Unreleased] — post-v1.0.0 skill catalog expansion (Phase 5)

First wave of post-v1.0.0 skill additions. Each new skill ships through
TDD discipline (RED tests first, then SKILL.md) and the
`tests/skills/<skill>/{helpers,smoke,pressure,performance}/` test taxonomy.

### Added

- **`/add-to-roadmap` (v1, prose)** — appends a checkbox task to the project's
  `ROADMAP.md` under a fuzzy-resolved `## Phase` or `### Subsection` header.
  Walks up from CWD to repo root, fuzzy contains-match (case-insensitive),
  bottom-of-section insertion, unified-diff confirmation gate before write.
  Pure-prose v1; deterministic Python helper roadmapped for v2.
- `tests/skills/add_to_roadmap/` — 28 tests across 4 layers (structural 9,
  smoke 9, pressure 7, performance 2). Doc-length budget calibrated on
  observed sibling-skill rates (`tesseract` ~270 lines, `checkpoint-save`
  ~80).
- `ROADMAP.md` Phase 5: `/add-to-roadmap` helper-script entry under "Flag
  additions to existing skills" — first dogfood-eat of the new skill (added
  manually since the skill couldn't add itself).

### Fixed

- `tests/performance/test_learn.py`, `tests/smoke/test_learn.py`: trailing-
  newline / whitespace fixes from `uv run ruff format` (no behavior change).

## [1.0.0] — 2026-04-23 (submitted, review pending)

v1.0.0 **submitted** to the official Claude Code marketplace on 2026-04-23 as a
standalone plugin alongside `superpowers`. Currently **awaiting Anthropic
review** — not yet listed. Until approval, install via `git clone` +
`claude --plugin-dir` (see README). This section will be updated with an
"(approved)" note and the effective install command once the submission lands.

### Added (v1.0.0)

- `.claude-plugin/plugin.json` manifest (v1.0.0, MIT, author + keywords set for
  marketplace discovery).
- `hooks/hooks.json` registering PreToolUse Bash hook for the existing
  `block-inline-scripts.py` guardrail via `${CLAUDE_PLUGIN_ROOT}`.
- Privacy policy section in `README.md` documenting that skills, hooks, and
  cost-tracking run entirely locally — no data collection or transmission by the
  plugin itself.
- README rewrite for marketplace-install flow: top-of-file
  `/plugin install claude-damn@claude-plugins-official`, Companion plugins
  table, Quickstart section, updated Project structure.

### Fixed (v1.0.0)

- `skills/cost-opt/SKILL.md` frontmatter: multi-line unquoted `description`
  (invalid YAML) rewritten as single-line quoted scalar so
  `claude plugin validate .` parses it.
- `skills/sme-test/SKILL.md`: added GFM header-separator rows to two tables that
  prettier was collapsing into prose.
- `pyproject.toml` consolidated two duplicate `dev = [...]` keys (the fuller
  list was incorrectly nested under `[tool.pytest.ini_options]` where `uv sync`
  never picked it up).
- `tests/test_hook_inline_scripts.py`: deleted buggy shadowed F811 duplicates of
  `test_null_command_is_allowed`, `test_non_string_command_is_allowed`,
  `test_non_dict_tool_input_is_allowed` — the first copy had contradictory
  assertions from a half-done PR #37 refactor; the second copy matches current
  hook behavior.
- `src/extract_cost.py`: `sorted(PRICING, key=len)` →
  `sorted(PRICING.keys(), key=lambda k: len(k))` to preserve `_T = str` through
  ty's overload resolution.
- `tests/conftest.py` fixture: return annotation `Path | None` →
  `Iterator[Path | None]` for yield-based fixture.
- `tests/test_skill_helpers.py` `_FakeRun`: `last_args: tuple | None` →
  `tuple = ()` (same for `last_kwargs`) to remove needless `None` narrowing
  burden.

### Tooling (v1.0.0)

- Linters at zero: ruff 11 → 0, ty 12 → 0, prettier 17 → 0.
- Tests green: pytest 422 passed, 58 deselected.
- `.prettierignore` covers `.pytest_cache/` (auto-generated) and
  `rules/PERSONALIZATION.example.md` (prettier 3.8.2 idempotency bug on HTML
  comment inside list with `tabWidth: 3`).

## [0.2.0] — `feat/transition-to-plugin` pre-ship

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

- **`/proceed` skill** at `skills/proceed/SKILL.md` — single-use user-invocable
  signal that authorizes Claude to pass the current approval gate only (design
  review, plan approval, risky-action confirmation). Body carries the literal
  phrase "Aligned and approved" and an explicit single-gate scope clarification
  so it does not grant standing authorization.
   - 5-level regression coverage under
     `tests/{structural,behavioral,integration,smoke,performance}/test_proceed.py`
     (23 default tests + 15 marker-gated smoke/performance cells). Mirrors the
     `/listen` test pattern. Behavioral layer uses TDD mutation checks.

- **`/tesseract` skill** at `skills/tesseract/SKILL.md` — user-invocable
  cross-session reflection tool. Resolves an anchor (file/branch/topic), reads
  four "hallways" of evidence (git, memory, shelf, bulk-beings), and writes back
  a shelf entry plus a one-line learning to `~/.claude/tesseract/`. Solo skill —
  no subagents, no shared memory, communicates with its own past and future only
  via file I/O.
   - Structural + regression coverage at
     `tests/skills/tesseract/test_skill_md.py` (11 tests: 5 regressions for the
     PR #21 review fixes — slug-rule prose accuracy, `git log --grep -F`,
     porcelain rename handling, `printf` append form — plus 6 structural
     invariants for frontmatter, hallway count, process-step numbering, and
     skill-dir/spec-name alignment).

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

- **PR review fixes** (PR #19 feedback)
   - `tests/performance/test_proceed.py` — corrected matrix docstring (actual
     matrix is complexity × prompt kind × model, not 2×3).
   - `tests/smoke/test_proceed.py` — tightened `test_not_standing_authorization`
     to require explicit negation of "standing" or a current-gate-only phrase in
     proximity, so the test no longer passes on incidental occurrences of
     "current"/"single"/"only".

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
  limits (400 chars / 4 statement separators); documented the `.worktrees/`
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
