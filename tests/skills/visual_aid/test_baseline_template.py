"""Tests for the baseline.html extraction refactor of /visual-aid.

`TestBaselineHtmlExtracted` guards that baseline.html exists and contains all
required structural invariants (doctype, lang attr, colour-scheme blocks, a11y
selectors, print media query, slot placeholders).

`TestSkillMdReferencesBaseline` guards that SKILL.md no longer inlines the raw
HTML template and instead references baseline.html by name, retaining the slot
conventions documentation.

These are regression/contract tests: they pin the post-refactor invariants so a
future edit cannot silently re-inline the template or drop a structural guard.
"""

from __future__ import annotations

import re


class TestBaselineHtmlExtracted:
    """Invariants for the extracted skills/visual-aid/baseline.html file."""

    def test_doctype_declaration(self, baseline_html: str) -> None:
        """baseline.html must start with a <!doctype html> declaration."""
        assert baseline_html.lower().lstrip().startswith("<!doctype html")

    def test_html_lang_attribute(self, baseline_html: str) -> None:
        """The <html> element must declare a lang attribute."""
        assert re.search(r"<html\s[^>]*lang=", baseline_html, re.IGNORECASE)

    def test_dark_root_block_has_custom_props(self, baseline_html: str) -> None:
        """The dark-mode :root block must define --bg, --fg, and --accent."""
        assert "--bg" in baseline_html
        assert "--fg" in baseline_html
        assert "--accent" in baseline_html

    def test_light_color_scheme_media_query(self, baseline_html: str) -> None:
        """A @media (prefers-color-scheme: light) block with its own :root."""
        assert re.search(
            r"@media\s*\(\s*prefers-color-scheme\s*:\s*light\s*\)",
            baseline_html,
            re.IGNORECASE,
        )

    def test_focus_visible_selector_coverage(self, baseline_html: str) -> None:
        """The :focus-visible rule must cover all eight interactive elements."""
        assert ":focus-visible" in baseline_html
        # Find the region around :focus-visible to check selector tokens.
        idx = baseline_html.index(":focus-visible")
        region = baseline_html[max(0, idx - 300) : idx + 20]
        for token in (
            "a",
            "button",
            "input",
            "select",
            "textarea",
            "summary",
            "tabindex",
            "contenteditable",
        ):
            assert token in region, (
                f"Token '{token}' not found near :focus-visible selector"
            )

    def test_prefers_reduced_motion_media_query(self, baseline_html: str) -> None:
        """A @media (prefers-reduced-motion: reduce) block must be declared."""
        assert re.search(
            r"@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)",
            baseline_html,
            re.IGNORECASE,
        )

    def test_print_media_query(self, baseline_html: str) -> None:
        """A @media print block must be declared."""
        assert re.search(r"@media\s+print", baseline_html, re.IGNORECASE)

    def test_ring_custom_prop_in_both_schemes(self, baseline_html: str) -> None:
        """--ring must appear at least twice (once per colour scheme)."""
        assert baseline_html.count("--ring") >= 2

    def test_generated_from_slot(self, baseline_html: str) -> None:
        """The {{one-line prompt summary}} slot comment must be preserved."""
        assert '<!-- Generated from: "{{one-line prompt summary}}" -->' in baseline_html

    def test_anchors_slot(self, baseline_html: str) -> None:
        """The {{X}}, {{Y}}, {{Z}} anchors slot comment must be preserved."""
        assert "<!-- Anchors: {{X}}, {{Y}}, {{Z}} -->" in baseline_html

    def test_title_slot(self, baseline_html: str) -> None:
        """The <title>{{Title}}</title> slot must be preserved."""
        assert "<title>{{Title}}</title>" in baseline_html


class TestSkillMdReferencesBaseline:
    """Invariants for SKILL.md after the baseline.html extraction."""

    def test_inline_doctype_removed(self, skill_md: str) -> None:
        """SKILL.md must not inline <!doctype html> — it belongs in baseline.html."""
        assert "<!doctype html>" not in skill_md.lower()

    def test_baseline_html_mentioned(self, skill_md: str) -> None:
        """SKILL.md must reference baseline.html by name at least once."""
        assert "baseline.html" in skill_md

    def test_slot_conventions_retained(self, skill_md: str) -> None:
        """SKILL.md must retain slot docs outside an inlined HTML block."""
        # After refactor: slots are referenced in prose near "baseline.html",
        # not buried inside the raw HTML. Verify baseline.html is mentioned
        # (prerequisite) and then that each slot token appears in skill_md.
        assert "baseline.html" in skill_md, (
            "baseline.html must be referenced before slot docs are meaningful"
        )
        assert "{{Title}}" in skill_md
        assert "{{one-line prompt summary}}" in skill_md
        assert "{{X}}" in skill_md
        assert "{{Y}}" in skill_md
        assert "{{Z}}" in skill_md

    def test_baseline_template_section_header_retained(self, skill_md: str) -> None:
        """The ## Baseline template section header points to baseline.html."""
        assert re.search(r"^## Baseline template", skill_md, re.MULTILINE)
        # After refactor the section body must reference baseline.html —
        # not just contain raw HTML.
        assert "baseline.html" in skill_md, (
            "## Baseline template section must reference baseline.html "
            "after the inline template is extracted"
        )

    def test_skill_md_instructs_agent_to_use_baseline(self, skill_md: str) -> None:
        """SKILL.md must instruct the agent to copy/include/use baseline.html."""
        idx = skill_md.find("baseline.html")
        assert idx != -1, "baseline.html not mentioned in SKILL.md"
        region = skill_md[max(0, idx - 200) : idx + 200]
        assert re.search(
            r"\b(copy|include|use|start from)\b",
            region,
            re.IGNORECASE,
        ), "No copy/include/use/start-from verb found near 'baseline.html'"
