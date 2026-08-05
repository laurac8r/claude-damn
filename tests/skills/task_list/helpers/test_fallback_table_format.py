"""The fallback specifies a Markdown table as the tracking format."""

from __future__ import annotations

import re


def test_fallback_specifies_markdown_table_format(skill_md: str) -> None:
    heading = "### Markdown-table fallback format"
    assert heading in skill_md

    # Scope the search to the fallback section so an earlier unrelated table
    # in the file can't fool this test into validating the wrong one.
    fallback_section = skill_md[skill_md.index(heading) :]

    # Header row's cell text, ignoring prettier's column padding.
    header_match = re.search(r"^\|(.+)\|\s*$", fallback_section, re.MULTILINE)
    assert header_match is not None, "no Markdown table header row found"
    header_cells = [cell.strip() for cell in header_match.group(1).split("|")]
    assert header_cells == ["#", "Status", "Task"]

    # A GFM table separator row (---) must immediately follow the header.
    separator_line = fallback_section.splitlines()[
        fallback_section[: header_match.end()].count("\n") + 1
    ]
    assert re.fullmatch(r"\|[\s:-]+\|[\s:-]+\|[\s:-]+\|", separator_line)
