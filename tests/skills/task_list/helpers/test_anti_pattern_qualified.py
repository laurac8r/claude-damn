"""The markdown-checklist anti-pattern is qualified to only when Task tools
are available — it must not forbid the tools-absent Markdown-table fallback.
"""

from __future__ import annotations

import re


def test_markdown_checklist_anti_pattern_scoped_to_tools_available(
    skill_md: str,
) -> None:
    anti_patterns = skill_md[skill_md.index("## Anti-patterns") :]
    bullet_start = anti_patterns.index("markdown checklist already")
    bullet_end = anti_patterns.index("\n- ❌", bullet_start)
    # Prettier may rewrap the bullet's prose across lines — collapse
    # whitespace so line breaks don't fracture a multi-word assertion.
    bullet = re.sub(r"\s+", " ", anti_patterns[bullet_start:bullet_end])

    assert "only when the Task tools are available" in bullet
    assert "does not apply" in bullet
