"""Performance tests for skills/add-to-roadmap/SKILL.md.

For a pure-prose v1 skill the meaningful perf metric is doc-length budget.
Calibrated on observed sibling rates: tesseract ~270 lines, checkpoint-save
~80 lines. Budget: 60–400 lines inclusive.

Also asserts that reading the file completes within 100 ms.
"""

from __future__ import annotations

import time
from pathlib import Path

SKILL_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "skills"
    / "add-to-roadmap"
    / "SKILL.md"
)

LINE_MIN = 60
LINE_MAX = 400
READ_BUDGET_MS = 100


class TestAddToRoadmapPerformance:
    """Doc-length budget and file-read latency for skills/add-to-roadmap/SKILL.md."""

    def test_skill_md_line_count_within_budget(self, skill_md: str) -> None:
        """SKILL.md must be between 60 and 400 lines (inclusive).

        Too short → under-specified recipe (Claude will guess).
        Too long  → unfocused (cognitive overload).

        Calibrated on sibling skills: tesseract ~270, checkpoint-save ~80.
        """
        lines = skill_md.splitlines()
        count = len(lines)
        assert count >= LINE_MIN, (
            f"SKILL.md has {count} lines — below minimum {LINE_MIN}. "
            "The recipe is likely under-specified."
        )
        assert count <= LINE_MAX, (
            f"SKILL.md has {count} lines — above maximum {LINE_MAX}. "
            "The document is likely unfocused."
        )

    def test_skill_md_read_within_100ms(self) -> None:
        """Reading SKILL.md must complete within 100 ms.

        This is a trivial local file-read assertion, but it documents the
        budget explicitly and would catch an accidentally enormous file.
        """
        assert SKILL_PATH.exists(), f"SKILL.md not found at {SKILL_PATH}"
        start = time.monotonic()
        SKILL_PATH.read_text()
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < READ_BUDGET_MS, (
            f"Reading SKILL.md took {elapsed_ms:.1f} ms — exceeds "
            f"{READ_BUDGET_MS} ms budget."
        )
