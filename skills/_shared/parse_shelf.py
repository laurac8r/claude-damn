"""Tesseract shelf parser shared by /tesseract and /atlas.

Each shelf file at ``~/.tesseract/shelf/<slug>.md`` contains an optional
``# Shelf — <slug>`` H1 followed by one or more ``## <ISO-timestamp>``
blocks. ``parse_shelf`` returns one ``ShelfEntry`` per parseable block plus
a list of warning strings for anything skipped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

_ISO_HEADING = re.compile(r"^## (\S+)\s*$", re.MULTILINE)
_H1 = re.compile(r"^# Shelf — (\S+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ShelfEntry:
    date: date
    slug: str
    body: str


def parse_shelf(path: Path) -> tuple[list[ShelfEntry], list[str]]:
    """Return ``(entries, warnings)`` for a shelf file.

    Missing files yield ``([], [])`` — empty state, not failure.
    """
    try:
        if not path.is_file():
            return [], []
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"shelf file unreadable {path.name!r}: {exc}"]
    except UnicodeDecodeError as exc:
        return [], [f"shelf file not valid UTF-8 {path.name!r}: {exc}"]
    slug = _resolve_slug(text, path)

    headings = list(_ISO_HEADING.finditer(text))
    entries: list[ShelfEntry] = []
    warnings: list[str] = []

    for i, match in enumerate(headings):
        ts_raw = match.group(1).strip().strip('"')
        body_start = match.end() + 1  # skip trailing newline of heading line
        body_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = text[body_start:body_end].strip()

        try:
            parsed_date = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).date()
        except ValueError:
            warnings.append(f"shelf entry skipped: malformed timestamp {ts_raw!r}")
            continue

        entries.append(ShelfEntry(date=parsed_date, slug=slug, body=body))

    return entries, warnings


def _resolve_slug(text: str, path: Path) -> str:
    h1 = _H1.search(text)
    if h1:
        return h1.group(1)
    return path.stem
