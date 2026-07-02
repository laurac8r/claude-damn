<!--
Title: use conventional-commit style, e.g.
  skill(atlas): …  ·  feat: …  ·  fix(hook): …  ·  docs(readme): …  ·  chore(release): bump to X.Y.Z
-->

## Summary

<!-- One or two sentences: what changes and why. -->

## Type of change

- [ ] Skill (new / edited `SKILL.md`)
- [ ] Hook (`hooks/` pre-tool guard)
- [ ] Docs (README / ROADMAP / CHANGELOG / SKILL prose)
- [ ] Test (pytest / bats)
- [ ] Chore / release (version bump, dep update)
- [ ] Infra (settings, CI, scripts, tooling)

## Changes

<!-- Bullet the concrete edits. -->

-
-

## Testing

<!-- Tick what you ran; paste counts/output if useful. -->

- [ ] `uv run ruff check` — clean
- [ ] `uv run ruff format` — clean
- [ ] `uv run pytest` — default suite green
- [ ] `bats tests/test_checkpoint_archive.bats tests/test_sync_theme.bats` — if shell scripts touched
- [ ] `uv run pytest -m ""` — full suite incl. smoke/performance (when relevant)

## Versioning

<!-- SemVer in lockstep: PATCH = docs/renames · MINOR = roadmap item · MAJOR = roadmap phase. -->

- [ ] Bumped `.claude-plugin/plugin.json` + `pyproject.toml` + `uv.lock` in lockstep
- [ ] Added a `CHANGELOG.md` entry for the new version
- [ ] N/A — non-shipping infra / docs-only with no version impact

## Checklist

- [ ] ruff clean and test suite green (evidence above)
- [ ] `CHANGELOG.md` updated (or N/A noted)
- [ ] No canonical/proprietary content leaked (`~/.claude/rules/`, proprietary `~/.claude/hooks/`, memory, `~/.tesseract/`) — safe to ship public
- [ ] Commits are atomic and conventional (per-file / script+test pairs)
