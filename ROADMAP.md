# Roadmap — `claude-damn`

Transition the flat `~/.claude` dotfile collection (commands, 38 skills, hooks,
cost tooling) into a first-class Claude Code plugin that installs alongside
`superpowers` from the official marketplace.

## Phase 0 — Baseline (done)

- [x] Slash commands: `/review`, `/expert-review`, `/address-pr-feedback`,
      `/cost`, `/cost-opt`
- [x] Full combinatoric skill catalog (38 skills): `tdd` / `super` / `duper` /
      `cat` families
- [x] `expert-review` family with multi-language + cloud + security
      specialization (10 variants)
- [x] `checkpoint-save` / `checkpoint-resume` / `check-yourself` lifecycle
      skills
- [x] `extract_cost.py` — session JSONL → token usage + cost via Anthropic
      pricing
- [x] `statusline-command.sh` — per-session cost in statusline
- [x] `settings.json` — permission allow/ask/deny rules, pre-tool hooks
- [x] `policy-limits.json` — remote control restrictions
- [x] `com.claude.sync-theme.plist` — macOS launchd theme sync

## Phase 1 — Plugin packaging (in progress, `feat/transition-to-plugin`)

- [x] Introduce `pyproject.toml` + `uv.lock` (uv-managed `.venv`, Python ≥ 3.14)
- [x] Stand up `tests/` tree with `pytest` + `ruff`
  - [x] `test_extract_cost.py` — cost parser coverage including fast-mode
        pricing
  - [x] `test_checkpoint_archive.bats` — checkpoint archive rotation
  - [x] `test_hook_inline_scripts.py` — inline-script hook guardrail
  - [x] `test_permissions.py` — settings.json permission lists
  - [x] `test_settings_structure.py` — settings schema
  - [x] `test_sync_theme.bats` — launchd theme-sync
  - [x] `tests/skills/sme_test/` — 132 structural tests for sme-test v1
- [x] **sme-test v1** — first skill built with spec-plan-test discipline (see
      `docs/superpowers/specs/2026-04-05-sme-test-design.md`)
- [ ] Dogfood sme-test on itself (Layer 4 — manual coaching run on its own
      files)
- [ ] Structural test coverage for the rest of the skill catalog (currently only
      sme-test is structurally verified; other skills are ad-hoc markdown)
- [ ] Write the Claude Code plugin manifest (`.claude-plugin/plugin.json` or
      equivalent)
- [ ] Decide final namespace: `claude-damn` as a standalone plugin vs. a
      marketplace overlay on `claude-plugins-official/superpowers`

## Phase 2 — Skill hardening

- [ ] Normalize `SKILL.md` frontmatter across all 38 skills (name, description,
      user-invocable, argument-hint)
- [ ] Port hand-wired shared-memory conventions into a reusable skill helper
- [ ] Add integration coverage for the `super` / `duper` / `cat` modifier
      composition rules documented in `skills/README.md`
- [ ] Canonicalize the error-handling contract from `sme-test/errors/` as a
      shared skill pattern

## Phase 3 — Harness integration

- [ ] Formalize pre/post tool-use hooks in `settings.json` with a typed schema
- [ ] Surface cost + policy-limit warnings through the statusline (not just
      cost)
- [ ] Theme-sync launchd plist → plugin-managed lifecycle (install/uninstall
      hooks)
- [ ] Generalize the inline-script guardrail into a shared hook the plugin can
      install

## Phase 4 — Distribution

- [ ] Install via Claude Code's plugin mechanism rather than
      `cp -r skills/* ~/.claude/skills/`
- [ ] Versioned releases with CHANGELOG entries per skill
- [ ] Per-skill quickstart docs and usage examples
- [ ] Publish to a marketplace (official or personal) for one-command install
