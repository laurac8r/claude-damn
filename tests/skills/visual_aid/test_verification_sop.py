"""Tests for the chrome-devtools verification SOP in skills/visual-aid/SKILL.md.

`TestVerificationSopExists` guards that the new automated-verification section
is present and contains every required element (section header, opt-out flag,
artifact path, MCP tool names, mobile viewport step, default-on language).

`TestHumanVerificationHandoffRemoved` guards that the old human-screenshot-ask
is gone and that machine-readable failure conditions replace it.

These are regression/contract tests: they pin the SOP shape post-refactor so a
future edit cannot silently regress to a human-screenshot hand-off or drop a
required step from the chrome-devtools flow.
"""

from __future__ import annotations

import re

import pytest


def _extract_verification_section(skill_md: str) -> str:
    """Return the text of the '## Verification (chrome-devtools)' section.

    The section runs from the matching '## ' header to the next '## ' header
    (or end of file).  Returns an empty string if the header is absent.
    """
    match = re.search(r"^## Verification \(chrome-devtools\)", skill_md, re.MULTILINE)
    if not match:
        return ""
    start = match.start()
    next_section = re.search(r"^## ", skill_md[match.end() :], re.MULTILINE)
    if next_section:
        end = match.end() + next_section.start()
    else:
        end = len(skill_md)
    return skill_md[start:end]


class TestVerificationSopExists:
    """The chrome-devtools verification SOP must be present in SKILL.md."""

    def test_section_header_contains_chrome_devtools(self, skill_md: str) -> None:
        """A level-2 section header matching '^##.*chrome-devtools.*$' must exist."""
        assert re.search(
            r"^##.*chrome-devtools.*$", skill_md, re.MULTILINE | re.IGNORECASE
        ), (
            "SKILL.md must have a '## … chrome-devtools …' section header "
            "for the automated verification SOP."
        )

    def test_no_verify_flag_documented(self, skill_md: str) -> None:
        """The literal string '--no-verify' must appear in SKILL.md."""
        assert "--no-verify" in skill_md, (
            "SKILL.md must document the '--no-verify' opt-out flag for "
            "chrome-devtools verification."
        )

    def test_tmp_artifact_path_present(self, skill_md: str) -> None:
        """The literal path '/tmp/visual-aid/' must appear in SKILL.md."""
        assert "/tmp/visual-aid/" in skill_md, (
            "SKILL.md must specify '/tmp/visual-aid/' as the ephemeral "
            "artifact directory for verification outputs."
        )

    def test_default_on_language_present(self, skill_md: str) -> None:
        """One of 'default-on', 'by default', or 'on by default' must appear."""
        assert re.search(
            r"default.on|by default|on by default", skill_md, re.IGNORECASE
        ), (
            "SKILL.md must convey that chrome-devtools verification runs by "
            "default (phrase: 'default-on', 'by default', or 'on by default')."
        )

    @pytest.mark.parametrize(
        "tool_name",
        [
            "navigate_page",
            "take_screenshot",
            "list_console_messages",
            "lighthouse_audit",
            "resize_page",
        ],
    )
    def test_required_mcp_tool_mentioned(self, skill_md: str, tool_name: str) -> None:
        """Each required MCP tool name must appear at least once in SKILL.md."""
        assert tool_name in skill_md, (
            f"SKILL.md must mention the MCP tool '{tool_name}' in the "
            "chrome-devtools verification SOP."
        )

    def test_mobile_viewport_near_take_screenshot(self, skill_md: str) -> None:
        """'take_screenshot' and a mobile/viewport term must co-occur in the SOP."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        assert "take_screenshot" in sop_section, (
            "take_screenshot must be present in the Verification SOP section."
        )
        assert re.search(r"mobile|375|viewport", sop_section, re.IGNORECASE), (
            "'mobile', '375', or 'viewport' must appear in the Verification SOP "
            "section alongside take_screenshot."
        )

    def test_mobile_viewport_dimensions_pinned(self, skill_md: str) -> None:
        """Both '375' and '812' must appear in the Verification SOP section."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        assert "375" in sop_section, (
            "Mobile viewport width '375' must be pinned in the Verification SOP."
        )
        assert "812" in sop_section, (
            "Mobile viewport height '812' must be pinned in the Verification SOP."
        )

    def test_lighthouse_threshold_90_present(self, skill_md: str) -> None:
        """The literal '90' must appear within ~120 chars of 'lighthouse_audit'."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        match = re.search(r"lighthouse_audit", sop_section)
        assert match, "'lighthouse_audit' must appear in the Verification SOP."
        start = max(0, match.start() - 120)
        end = min(len(sop_section), match.end() + 120)
        window = sop_section[start:end]
        assert "90" in window, (
            "The Lighthouse threshold '90' must appear within 120 chars of "
            "'lighthouse_audit' in the Verification SOP."
        )

    def test_slug_and_mkdir_in_sop(self, skill_md: str) -> None:
        """Both 'slug' and 'mkdir' must appear in the Verification SOP section."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        lower = sop_section.lower()
        assert "slug" in lower, (
            "'slug' must appear in the Verification SOP to document slug derivation."
        )
        assert "mkdir" in lower, (
            "'mkdir' must appear in the Verification SOP to document "
            "directory creation."
        )


class TestHumanVerificationHandoffRemoved:
    """The old human-screenshot handoff must be gone from SKILL.md."""

    def test_needs_human_verification_phrase_absent(self, skill_md: str) -> None:
        """The phrase 'Needs human verification' must NOT appear in SKILL.md."""
        assert not re.search(r"needs human verification", skill_md, re.IGNORECASE), (
            "'Needs human verification' is the pre-refactor handoff phrase — "
            "it must be removed in favour of automated chrome-devtools checks."
        )

    def test_no_human_directed_screenshot_instruction(self, skill_md: str) -> None:
        """Human-directed screenshot instructions must not survive the refactor."""
        assert not re.search(
            r"(take a screenshot|screenshot the page).*(yourself|manually)",
            skill_md,
            re.IGNORECASE,
        ), (
            "Instructions asking the human to 'take a screenshot … yourself' or "
            "'screenshot the page … manually' must be removed after the refactor."
        )

    def test_console_error_failure_condition_present(self, skill_md: str) -> None:
        """A console-error failure condition must exist in the Verification SOP."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        assert "console" in sop_section.lower(), (
            "The word 'console' must appear in the Verification SOP section."
        )
        assert re.search(r"errors?", sop_section, re.IGNORECASE), (
            "A console-error failure condition must be present in the SOP: "
            "'error'/'errors' must appear in the Verification section."
        )

    def test_lighthouse_a11y_failure_condition_present(self, skill_md: str) -> None:
        """A lighthouse a11y failure condition must be present in SKILL.md."""
        lh_idx = skill_md.lower().find("lighthouse")
        assert lh_idx != -1, "The word 'lighthouse' must appear in SKILL.md."
        window = skill_md[max(0, lh_idx - 300) : lh_idx + 300]
        assert re.search(r"threshold|score|fail", window, re.IGNORECASE), (
            "A lighthouse failure condition must be present: 'lighthouse' and "
            "one of 'threshold'/'score'/'fail' must appear within 300 characters."
        )


class TestSlotCrossCheck:
    """Every {{...}} placeholder in baseline.html must appear in SKILL.md slot docs."""

    def test_all_baseline_placeholders_in_skill_md_slot_section(
        self, baseline_html: str, skill_md: str
    ) -> None:
        """Every {{...}} in baseline.html must appear in the slot conventions section.

        Extracts all unique {{...}} patterns from baseline.html, then asserts
        each one is present in the text between '### Slot conventions' and the
        next '## ' header.  Catches drift between the template and its
        documentation.
        """
        placeholders = set(re.findall(r"\{\{[^}]+\}\}", baseline_html))
        assert placeholders, "baseline.html must contain at least one {{...}} slot."

        slot_match = re.search(r"^### Slot conventions", skill_md, re.MULTILINE)
        assert slot_match, "'### Slot conventions' heading must exist in SKILL.md."
        slot_start = slot_match.start()
        next_h2 = re.search(r"^## ", skill_md[slot_match.end() :], re.MULTILINE)
        if next_h2:
            slot_end = slot_match.end() + next_h2.start()
        else:
            slot_end = len(skill_md)
        slot_section = skill_md[slot_start:slot_end]

        missing = [p for p in sorted(placeholders) if p not in slot_section]
        assert not missing, (
            f"These baseline.html placeholders are missing from the "
            f"'### Slot conventions' section of SKILL.md: {missing}"
        )
