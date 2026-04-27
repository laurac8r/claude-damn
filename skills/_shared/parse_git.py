"""Git working-tree snapshot for /atlas.

``parse_git`` returns ``(None, [])`` when ``cwd`` is not inside a git repo
(empty state). When inside a repo, returns ``(GitState, warnings)`` —
warnings is non-empty only if a sub-command fails.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GitState:
    branch: str
    ahead: int
    behind: int
    dirty: list[str] = field(default_factory=list)
    recent_commits: list[str] = field(default_factory=list)


def parse_git(cwd: Path) -> tuple[GitState | None, list[str]]:
    if not _is_git_repo(cwd):
        return None, []

    warnings: list[str] = []
    branch = _run(cwd, ["git", "branch", "--show-current"], warnings) or ""
    dirty_text = _run(cwd, ["git", "status", "--porcelain"], warnings) or ""
    dirty = [line[3:] for line in dirty_text.splitlines() if line.strip()]
    log_text = (
        _run(
            cwd,
            ["git", "log", "--max-count=10", "--pretty=format:%s"],
            warnings,
        )
        or ""
    )
    recent_commits = [line for line in log_text.splitlines() if line.strip()]
    ahead, behind = _ahead_behind(cwd, warnings)

    return (
        GitState(
            branch=branch.strip(),
            ahead=ahead,
            behind=behind,
            dirty=dirty,
            recent_commits=recent_commits,
        ),
        warnings,
    )


def _is_git_repo(cwd: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError, FileNotFoundError:
        return False
    return result.stdout.strip() == "true"


def _run(cwd: Path, argv: list[str], warnings: list[str]) -> str | None:
    try:
        result = subprocess.run(
            argv, cwd=cwd, check=True, capture_output=True, text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        warnings.append(f"git command failed: {' '.join(argv)} ({exc})")
        return None
    return result.stdout


def _ahead_behind(cwd: Path, warnings: list[str]) -> tuple[int, int]:
    # Probe upstream silently — no warning if unconfigured (common case).
    upstream = _run(
        cwd,
        ["git", "rev-parse", "--abbrev-ref", "@{u}"],
        [],
    )
    if upstream is None:
        return 0, 0
    counts = _run(
        cwd,
        ["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"],
        warnings,
    )
    if counts is None:
        return 0, 0
    parts = counts.strip().split()
    if len(parts) != 2:
        return 0, 0
    behind, ahead = int(parts[0]), int(parts[1])
    return ahead, behind
