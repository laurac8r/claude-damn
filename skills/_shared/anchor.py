"""Anchor cascade for /tesseract and /atlas.

The anchor is the reference frame: a slug plus the cascade rung that
resolved it. Spec §5.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AnchorSource(StrEnum):
    MODIFIED_FILE = "modified-file"
    BRANCH = "branch"
    MEMORY = "memory"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class Anchor:
    slug: str
    source: AnchorSource
