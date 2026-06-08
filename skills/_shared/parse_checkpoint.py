"""CHECKPOINT.md cascade + section parser shared by /atlas.

Cascade: ``cwd/CHECKPOINT.md`` -> ``<repo-root>/CHECKPOINT.md`` ->
``<repo-root>/.worktrees/<branch-slug>/CHECKPOINT.md``. First hit wins.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from skills._shared.slugify import slugify

_BRANCH_LINE = re.compile(r"^\*\*Branch:\*\*\s*`([^`]+)`", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)$", re.MULTILINE)


@dataclass(frozen=True)
class CheckpointDoc:
    branch: str
    current_state: str
    next_steps: list[str] = field(default_factory=list)
    key_decisions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    raw: str = ""


def parse_checkpoint(cwd: Path) -> tuple[CheckpointDoc | None, list[str]]:
    """Return ``(CheckpointDoc, warnings)`` or ``(None, [])`` when no file found.

    The function never raises — all failure modes return a value + warnings.
    """
    path = _resolve_path(cwd)
    if path is None:
        return None, []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        warning = f"checkpoint file could not be read {path}: {exc}"
        return CheckpointDoc(branch="", current_state="", raw=""), [warning]

    branch_match = _BRANCH_LINE.search(text)
    if branch_match is None:
        warning = f"CHECKPOINT.md found at {path} but section parse failed"
        return CheckpointDoc(branch="", current_state="", raw=text), [warning]

    branch = branch_match.group(1)
    sections = _split_sections(text)

    return (
        CheckpointDoc(
            branch=branch,
            current_state=sections.get("Current State", "").strip(),
            next_steps=_lines(sections.get("Next Steps", "")),
            key_decisions=_lines(sections.get("Key Decisions Made", "")),
            blockers=_lines(sections.get("Open Questions / Blockers", "")),
            raw=text,
        ),
        [],
    )


def _resolve_path(cwd: Path) -> Path | None:
    """Return the first CHECKPOINT.md found via the cascade, or None."""
    candidate = cwd / "CHECKPOINT.md"
    if candidate.is_file():
        return candidate

    root = _repo_root(cwd)
    if root is None:
        return None

    candidate = root / "CHECKPOINT.md"
    if candidate.is_file():
        return candidate

    branch = _current_branch(cwd)
    if not branch:
        return None

    candidate = root / ".worktrees" / slugify(branch) / "CHECKPOINT.md"
    if candidate.is_file():
        return candidate

    return None


def _repo_root(cwd: Path) -> Path | None:
    """Return the absolute repo root via ``git rev-parse``, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError, FileNotFoundError:
        return None
    return Path(result.stdout.strip())


def _current_branch(cwd: Path) -> str:
    """Return the current git branch name, or ``""`` on failure."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError, FileNotFoundError:
        return ""
    return result.stdout.strip()


def _split_sections(text: str) -> dict[str, str]:
    """Return a mapping of H2 heading -> section body text."""
    headings = list(_H2.finditer(text))
    sections: dict[str, str] = {}
    for i, match in enumerate(headings):
        heading = match.group(1).strip()
        body_start = match.end()
        body_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        sections[heading] = text[body_start:body_end]
    return sections


def _lines(body: str) -> list[str]:
    """Return non-blank lines from ``body``."""
    return [line for line in body.splitlines() if line.strip()]
