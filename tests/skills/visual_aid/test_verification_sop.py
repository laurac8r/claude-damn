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
        ],
    )
    def test_required_mcp_tool_mentioned(self, skill_md: str, tool_name: str) -> None:
        """Each required MCP tool name must appear at least once in SKILL.md."""
        assert tool_name in skill_md, (
            f"SKILL.md must mention the MCP tool '{tool_name}' in the "
            "chrome-devtools verification SOP."
        )

    def test_mobile_viewport_near_take_screenshot(self, skill_md: str) -> None:
        """'mobile' or 'viewport' must appear within 500 chars of 'take_screenshot'."""
        idx = skill_md.find("take_screenshot")
        assert idx != -1, "take_screenshot must be present in SKILL.md."
        window = skill_md[max(0, idx - 500) : idx + 500]
        assert re.search(r"mobile|viewport", window, re.IGNORECASE), (
            "'mobile' or 'viewport' must appear within 500 characters of "
            "'take_screenshot' to confirm the mobile viewport step is documented."
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
        """A failure condition referencing console errors must exist in SKILL.md."""
        console_idx = skill_md.lower().find("console")
        assert console_idx != -1, "The word 'console' must appear in SKILL.md."
        window = skill_md[max(0, console_idx - 200) : console_idx + 200]
        assert re.search(r"errors?", window, re.IGNORECASE), (
            "A console-error failure condition must be present: 'console' and "
            "'error'/'errors' must appear within 200 characters of each other."
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
