# Changelog

All notable changes to `awesome-claude` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project is pre-1.0 so versions are
date-tagged rather than SemVer.

## [Unreleased] — `feat/transition-to-plugin`

### Added

- **sme-test v1** skill at `skills/sme-test/` — Subject Matter Expert TDD coach with three modes
  (`coach`, `expert` via `-x`, `expert-auto` via `-xa`).
  - `SKILL.md` entry point with frontmatter, mode documentation, and shared-memory contract.
  - 5 prompt files: `coach-dispatch`, `three-whys`, `gwt-formulation`, `test-writer`, `red-gate`.
  - 2 runner adapters: `adapters/python/` and `adapters/bats/` implementing the 4-capability contract.
  - `errors/error-handlers.md` covering 5 error classes with recovery paths.
  - 132 structural tests across `tests/skills/sme_test/` (SKILL.md, prompts, errors, adapters,
    cross-file integration). Layer 4 dogfood deferred to first real usage.
- `pyproject.toml` + `uv.lock` — uv-managed `.venv` with `pytest`, `ruff`, `pyyaml`.
- `tests/skills/` tree with shared `conftest.py` helpers (`parse_frontmatter`, `extract_sections`,
  `read_skill_file`).
- Design spec and implementation plan under `docs/superpowers/{specs,plans}/`.

### Changed

- README expanded from stub to project overview with development instructions.
- Expert review guidelines: added Java + comprehensive language/security/cloud references.

## [2026-03] — Pre-plugin baseline

### Added

- `extract_cost.py` — parses session JSONL files, computes token usage + cost via Anthropic pricing,
  logs to `~/.claude/cost-log/`. Covers fast-mode pricing.
- `statusline-command.sh` — statusline showing per-session cost.
- Initial slash commands: `/review`, `/expert-review`, `/address-pr-feedback`, `/cost`, `/cost-opt`.
- `settings.json` with pre-tool hooks and script execution policy.
- `policy-limits.json` defining remote control restrictions.
- `com.claude.sync-theme.plist` for theme-sync launchd service.
- MIT `LICENSE`.

### Changed

- Project renamed from `awesome-bruno` to `awesome-claude`.
- Nested directories flattened out of symlinked tree.

### Removed

- Stray symlinks (Windsurf, nested).