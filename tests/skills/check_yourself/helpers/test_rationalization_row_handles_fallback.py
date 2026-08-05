"""The 'inter-task /check-yourself is overkill' rationalization row assumes
TaskUpdate exists ("If TaskUpdate flips status to `completed`, that IS the
boundary"). That framing silently breaks down when the Task* tools are absent
from the tool surface: there is no TaskUpdate call to flip, only a row edit in
the Markdown fallback table/list. The reconciliation logic in that row must
name the fallback-table case explicitly so an agent in the tools-absent state
still recognizes the boundary, rather than reading the row as inapplicable.
"""

from __future__ import annotations


def test_taskupdate_rationalization_also_names_markdown_fallback(
    skill_md: str,
) -> None:
    anchor = "If TaskUpdate flips status to"
    idx = skill_md.index(anchor)
    # The row is a single (long) table line; a few hundred chars past the
    # anchor comfortably covers the rest of that cell without spilling into
    # unrelated rows.
    window = skill_md[idx : idx + 500]

    assert "TaskUpdate" in window
    # The row must also name the no-tools case explicitly — a Markdown
    # table/list row changing status counts as the same boundary.
    assert "Markdown" in window
    assert "table" in window.lower() or "list" in window.lower()
