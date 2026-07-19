"""SessionStart hook — ensure the remember plugin's log dir exists.

The official `remember` plugin's `hooks/hooks.json` redirects stderr to
`${CLAUDE_PROJECT_DIR:-.}/.remember/logs/hook-errors.log`. Bash opens the
redirect target *before* running the script body, so on a fresh worktree
where `.remember/logs/` does not yet exist, the very first hook firing
dies with "No such file or directory" before the script's own defensive
`mkdir -p` ever runs.

This hook fires earlier (SessionStart) and creates the `.remember/`
subdirs the plugin expects, making the remember plugin robust on
first-touch worktrees.

Companion patch (transient): the same `mkdir -p && …` chain was inlined
into `~/.claude/plugins/cache/.../hooks.json` for belt-and-suspenders.
That cache file is overwritten on plugin update; this user-side hook is
the durable layer.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Mirrors the dirs that the remember plugin's session-start-hook.sh
# creates internally (v0.5.0 lines 57-58):
#   "$PROJECT/.remember/tmp", "$PROJECT/.remember/logs",
#   "$PROJECT/.remember/logs/autonomous"
_REMEMBER_SUBDIRS: tuple[str, ...] = (
    ".remember/tmp",
    ".remember/logs",
    ".remember/logs/autonomous",
)


def resolve_project_dir(payload: Any) -> Path | None:
    """Return project dir from payload['cwd'] or $CLAUDE_PROJECT_DIR, else None."""
    if isinstance(payload, dict):
        cwd = payload.get("cwd")
        if isinstance(cwd, str) and cwd:
            return Path(cwd)
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return None


def ensure_dirs(project_dir: Path) -> list[str]:
    """Create `.remember/` subdirs under `project_dir`. Idempotent.

    Returns paths actually newly created (testability).
    """
    created: list[str] = []
    for sub in _REMEMBER_SUBDIRS:
        target = project_dir / sub
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(target))
    return created


def main_from_stdin() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError, ValueError:
        # Fail open — don't wedge sessions on malformed payloads.
        print("{}")
        return
    project_dir = resolve_project_dir(payload)
    if project_dir is not None:
        try:
            ensure_dirs(project_dir)
        except OSError, ValueError:
            # Fail open — never wedge a session. OSError covers permission
            # errors / read-only FS; ValueError covers an embedded-NUL path
            # (Path.mkdir raises ValueError, not OSError, for that).
            pass
    print("{}")


if __name__ == "__main__":
    main_from_stdin()
    sys.exit(0)
