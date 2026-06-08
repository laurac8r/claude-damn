"""Slugify rule shared by /tesseract and /atlas.

Lowercase the input, collapse every run of characters outside ``[a-z0-9]``
into a single ``-``, then strip leading/trailing ``-``.
"""

from __future__ import annotations

import re

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(raw: str) -> str:
    """Return the canonical slug for ``raw``.

    See ``docs/superpowers/specs/2026-04-26-atlas-design.md`` §5.2 and
    ``skills/tesseract/SKILL.md`` "Slug rule" for the source-of-truth
    description.
    """
    return _NON_SLUG.sub("-", raw.lower()).strip("-")
