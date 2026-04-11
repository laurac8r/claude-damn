# awesome-claude

A personal collection of Claude Code customizations — commands, skills, hooks, and scripts — being
transitioned into a proper Claude Code plugin.

## What's in here

- **`skills/`** — Reusable skills invoked via the `Skill` tool.
  - `sme-test/` — Subject Matter Expert TDD coach. Teaches Given/When/Then thinking before touching code.
    Three modes: `coach` (default), `expert` (`-x`), `expert-auto` (`-xa`).
- **`commands/`** — Slash commands (`/review`, `/expert-review`, `/address-pr-feedback`, `/cost`, `/cost-opt`).
- **`extract_cost.py`** — Parses Claude Code session JSONL files and computes real token usage and cost
  via the Anthropic pricing table. Logs to `~/.claude/cost-log/` as JSONL.
- **`statusline-command.sh`** — Shell statusline showing per-session cost.
- **`settings.json`** — Hook and permission config for the harness.
- **`com.claude.sync-theme.plist`** — macOS launchd plist for syncing theme state.

## Status

Currently on branch `feat/transition-to-plugin` — converting the flat `~/.claude` layout into a proper
plugin package with tests, a `pyproject.toml`, and `uv`-managed dependencies. See
[`ROADMAP.md`](ROADMAP.md) for the transition plan and [`CHANGELOG.md`](CHANGELOG.md) for what's landed.

## Development

```bash
uv sync # install dev deps
uv run pytest # run the full test suite
uv run ruff check . # lint
uv run ruff format . # format
```

[//]: # (Design specs and implementation plans live in `docs/superpowers/{specs,plans}/`.)

## License

MIT — see [`LICENSE`](LICENSE).