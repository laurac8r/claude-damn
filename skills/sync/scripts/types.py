"""Core dataclasses for sync plans."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Action = Literal["add", "update", "delete", "skip"]
Direction = Literal["src→tgt", "tgt→src"]
Mode = Literal["plan", "interactive", "push", "pull", "mirror"]


@dataclass(frozen=True)
class FileOp:
    """A single planned file operation."""

    path: Path
    action: Action
    direction: Direction
    reason: str


@dataclass(frozen=True)
class SyncPlan:
    """A complete set of file operations for a single sync invocation."""

    source: Path
    target: Path
    mode: Mode
    ops: tuple[FileOp, ...]
