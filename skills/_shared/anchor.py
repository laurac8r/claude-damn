"""Anchor cascade for /tesseract and /atlas.

The anchor is the reference frame: a slug plus the cascade rung that
resolved it. Spec §5.2.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from skills._shared.slugify import slugify


class AnchorSource(StrEnum):
    MODIFIED_FILE = "modified-file"
    BRANCH = "branch"
    MEMORY = "memory"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class Anchor:
    slug: str
    source: AnchorSource


def resolve_anchor(
    cwd: Path,
    override: str | None = None,
    memory_dir: Path | None = None,
) -> tuple[Anchor, list[str]]:
    """Resolve the anchor for ``cwd`` per the four-rung cascade.

    1. ``override`` (if provided) — slugified and tagged MODIFIED_FILE.
    2. Most recently modified file under ``cwd`` per ``git diff --name-only``.
    3. Current branch from ``git branch --show-current``.
    4. Most recently mtime'd file under ``memory_dir`` (default
       ``~/.claude/projects/<project-slug>/memory``).
    5. UNRESOLVED — synthesizes ``Anchor("void", UNRESOLVED)`` with a warning.
    """
    if override is not None:
        return Anchor(slug=slugify(override), source=AnchorSource.MODIFIED_FILE), []

    modified = _first_modified_file(cwd)
    if modified is not None:
        return (
            Anchor(
                slug=slugify(Path(modified).name),
                source=AnchorSource.MODIFIED_FILE,
            ),
            [],
        )

    branch = _current_branch(cwd)
    if branch:
        return Anchor(slug=slugify(branch), source=AnchorSource.BRANCH), []

    memory_dir = memory_dir or (Path.home() / ".claude" / "projects")
    recent_memory = _most_recent_memory(memory_dir)
    if recent_memory is not None:
        return Anchor(slug=slugify(recent_memory), source=AnchorSource.MEMORY), []

    return (
        Anchor(slug="void", source=AnchorSource.UNRESOLVED),
        ["no anchor source available"],
    )


def _first_modified_file(cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError, FileNotFoundError:
        return None
    files = [line for line in result.stdout.splitlines() if line.strip()]
    return files[0] if files else None


def _current_branch(cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError, FileNotFoundError:
        return None
    branch = result.stdout.strip()
    return branch or None


def _most_recent_memory(memory_dir: Path) -> str | None:
    if not memory_dir.is_dir():
        return None
    candidates = list(memory_dir.glob("*/memory/*.md"))
    if not candidates:
        return None
    statted: list[tuple[float, Path]] = []
    for p in candidates:
        try:
            statted.append((p.stat().st_mtime, p))
        except OSError:
            continue
    if not statted:
        return None
    statted.sort(key=lambda pair: pair[0], reverse=True)
    return statted[0][1].stem
