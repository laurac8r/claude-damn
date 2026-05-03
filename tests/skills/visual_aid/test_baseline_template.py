"""Tests for the baseline.html extraction refactor of /visual-aid.

`TestBaselineHtmlExtracted` guards that baseline.html exists and contains all
required structural invariants (doctype, lang attr, colour-scheme blocks, a11y
selectors, print media query, key traceability and title slot placeholders).

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
        """The :focus-visible rule must cover all eight selector tokens."""
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

    def test_h1_title_slot(self, baseline_html: str) -> None:
        """The <h1>{{Title}}</h1> slot must appear in the baseline.html body."""
        assert "<h1>{{Title}}</h1>" in baseline_html, (
            "<h1>{{Title}}</h1> must be present in baseline.html so the "
            "visible heading slot is populated alongside the <title> slot."
        )

    def test_footer_source_slot(self, baseline_html: str) -> None:
        """The {{link or \"—\"}} footer source slot must be preserved."""
        assert '{{link or "—"}}' in baseline_html, (
            '{{link or "—"}} must be present in baseline.html as the footer '
            "source-link slot."
        )


class TestInlineCodeWrapping:
    """Long inline <code> identifiers (FQ Java/Kotlin paths, dotted method
    chains) must wrap inside cards instead of overflowing past the right
    edge."""

    def test_inline_code_has_overflow_wrap(self, baseline_html: str) -> None:
        """code/kbd/samp must declare overflow-wrap: anywhere (or break-word)
        so unbreakable identifiers can wrap inside the card."""
        # Find the rule body for `code, kbd, samp`.
        match = re.search(
            r"code\s*,\s*kbd\s*,\s*samp\s*\{([^}]*)\}",
            baseline_html,
            re.IGNORECASE,
        )
        assert match, "code, kbd, samp rule not found in baseline.html"
        body = match.group(1)
        assert re.search(
            r"overflow-wrap\s*:\s*(anywhere|break-word)",
            body,
            re.IGNORECASE,
        ), (
            "code/kbd/samp rule must set overflow-wrap to anywhere or "
            "break-word so long identifiers wrap inside cards"
        )

    def test_card_has_min_width_zero(self, baseline_html: str) -> None:
        """.card must set min-width: 0 so it can shrink below intrinsic
        min-content when inline code becomes long; without this, even
        overflow-wrap can't help because the grid track refuses to narrow."""
        match = re.search(
            r"\.card\s*\{([^}]*)\}",
            baseline_html,
            re.IGNORECASE,
        )
        assert match, ".card rule not found in baseline.html"
        body = match.group(1)
        assert re.search(
            r"min-width\s*:\s*0",
            body,
            re.IGNORECASE,
        ), (
            ".card must set min-width: 0 so grid items shrink below "
            "intrinsic min-content for long inline code"
        )


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
        # Slots are documented in prose near "baseline.html", not inside an
        # inlined raw HTML block. Verify baseline.html is mentioned
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
