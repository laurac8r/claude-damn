"""TDD tests for /tesseract --visual renderer.

Covers: shelf parser, heat-bucket classifier, HTML renderer, CLI --visual
short-circuit (no shelf/bulk write), offline-safety (no external URLs).
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCRIPT = SKILL_DIR / "render_visual.py"

sys.path.insert(0, str(SKILL_DIR))
import render_visual as rv  # noqa: E402, I001


# ---------- parser ----------


def test_parse_shelf_counts_visits_and_picks_anchor() -> None:
    a = rv.parse_shelf(FIXTURES / "shelf" / "alpha.md")
    assert a["slug"] == "alpha"
    assert a["anchor"] == "alpha"
    assert a["visits"] == 3
    assert a["first"] == "2026-04-20"
    assert a["last"] == "2026-04-23"


def test_parse_shelf_collects_signals_newest_first_dedup() -> None:
    a = rv.parse_shelf(FIXTURES / "shelf" / "alpha.md")
    assert a["signals"] == ["third visit — ship it", "second look"]
    # em-dash default signal is filtered
    assert "—" not in a["signals"]


def test_parse_shelf_preserves_path_anchor() -> None:
    a = rv.parse_shelf(FIXTURES / "shelf" / "src-widgets-button-tsx.md")
    assert a["anchor"] == "src/widgets/Button.tsx"
    assert a["slug"] == "src-widgets-button-tsx"
    assert a["visits"] == 2


def test_parse_shelf_single_visit_silent_signal() -> None:
    b = rv.parse_shelf(FIXTURES / "shelf" / "beta.md")
    assert b["visits"] == 1
    assert b["signals"] == []


# ---------- heat classifier ----------


@pytest.mark.parametrize(
    "visits,last,today,expected",
    [
        (5, "2026-04-23", "2026-04-23", "hot"),  # frequent
        (2, "2026-04-23", "2026-04-23", "hot"),  # revisited today
        (2, "2026-04-19", "2026-04-23", "warm"),  # revisited but stale
        (1, "2026-04-23", "2026-04-23", "warm"),  # single but fresh
        (1, "2026-04-21", "2026-04-23", "cool"),  # 2d ago
        (1, "2026-04-10", "2026-04-23", "cold"),  # older single
        (1, None, "2026-04-23", "cold"),  # no date → cold
    ],
)
def test_classify_heat(
    visits: int, last: str | None, today: str, expected: str
) -> None:
    ref = date.fromisoformat(today)
    assert rv.classify_heat(visits, last, today=ref) == expected


# ---------- renderer ----------


def _render(tmp_path: Path) -> str:
    out = tmp_path / "t.html"
    rv.render_from_shelf(
        shelf_dir=FIXTURES / "shelf",
        bulk_path=FIXTURES / "bulk-beings.md",
        out_path=out,
        today=date.fromisoformat("2026-04-23"),
    )
    return out.read_text(encoding="utf-8")


def test_renderer_emits_one_article_per_anchor(tmp_path: Path) -> None:
    html = _render(tmp_path)
    assert html.count('<article class="card') == 3


def test_renderer_has_exactly_one_h1_and_lang(tmp_path: Path) -> None:
    html = _render(tmp_path)
    assert html.count("<h1") == 1
    assert 'lang="en"' in html


def test_renderer_has_no_external_urls(tmp_path: Path) -> None:
    html = _render(tmp_path)
    for token in ("http://", "https://"):
        assert token not in html, f"external URL token {token!r} leaked into output"


def test_renderer_escapes_anchor_text(tmp_path: Path) -> None:
    html = _render(tmp_path)
    # Path anchor with slashes must be escaped as text, not interpreted as markup.
    assert "src/widgets/Button.tsx" in html
    assert "<tsx" not in html  # ensure < wasn't stripped/mis-parsed


def test_renderer_includes_mode_toggle_and_sort_controls(tmp_path: Path) -> None:
    html = _render(tmp_path)
    assert 'class="mode-toggle"' in html
    assert 'data-mode="non-interactive"' in html
    assert 'data-mode="interactive"' in html
    assert 'class="sort-controls"' in html


# ---------- path defaults ----------


def test_default_paths_point_to_home_tesseract_not_claude_subdir() -> None:
    """Data dir lives at ~/.tesseract/ (top-level, fewer permission prompts),
    not ~/.claude/tesseract/."""
    home = Path.home()
    assert rv.DEFAULT_SHELF == home / ".tesseract" / "shelf"
    assert rv.DEFAULT_BULK == home / ".tesseract" / "bulk-beings.md"
    # Regression guard: the old path must not reappear.
    assert ".claude" not in rv.DEFAULT_SHELF.parts
    assert ".claude" not in rv.DEFAULT_BULK.parts


def test_skill_md_references_only_new_tesseract_path() -> None:
    """SKILL.md instructions must point agents at ~/.tesseract/, not the old
    ~/.claude/tesseract/. Consistency guard: one mention of the old path in
    the instructions would silently keep new shelves landing in the old place.
    """
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert ".claude/tesseract" not in skill_md, (
        "stale path ~/.claude/tesseract/ still in SKILL.md"
    )
    assert skill_md.count(".tesseract/") >= 3, (
        "expected ≥3 references to the new ~/.tesseract/ path"
    )


# ---------- CLI short-circuit ----------


def test_cli_visual_writes_html_and_does_not_touch_shelf_or_bulk(
    tmp_path: Path,
) -> None:
    """--visual must be read-only: zero writes to shelf/*.md or bulk-beings.md."""
    shelf = FIXTURES / "shelf"
    bulk = FIXTURES / "bulk-beings.md"
    before = {p: p.stat().st_mtime_ns for p in shelf.glob("*.md")}
    before[bulk] = bulk.stat().st_mtime_ns

    out = tmp_path / "out.html"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--shelf",
            str(shelf),
            "--bulk",
            str(bulk),
            "--out",
            str(out),
            "--today",
            "2026-04-23",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert out.exists()
    assert str(out) in result.stdout
    # No file inside the shelf or bulk was touched.
    for p, mtime in before.items():
        assert p.stat().st_mtime_ns == mtime, f"{p} was mutated by --visual run"
