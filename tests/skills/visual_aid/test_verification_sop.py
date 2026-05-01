"""Regression contract: pin the chrome-devtools verification SOP shape in
skills/visual-aid/SKILL.md so a future edit cannot silently regress to a
human-screenshot handoff or drop a required step from the SOP."""

from __future__ import annotations

import re

import pytest


def _extract_verification_section(skill_md: str) -> str:
    """Slice between '## Verification (chrome-devtools)' and the next '## '
    header, or empty string if the section is missing."""
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
        assert re.search(
            r"^##.*chrome-devtools.*$", skill_md, re.MULTILINE | re.IGNORECASE
        ), (
            "SKILL.md must have a '## … chrome-devtools …' section header "
            "for the automated verification SOP."
        )

    def test_no_verify_flag_documented(self, skill_md: str) -> None:
        assert "--no-verify" in skill_md, (
            "SKILL.md must document the '--no-verify' opt-out flag for "
            "chrome-devtools verification."
        )

    def test_tmp_artifact_path_present(self, skill_md: str) -> None:
        assert "/tmp/visual-aid/" in skill_md, (
            "SKILL.md must specify '/tmp/visual-aid/' as the ephemeral "
            "artifact directory for verification outputs."
        )

    def test_default_on_language_present(self, skill_md: str) -> None:
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
        assert tool_name in skill_md, (
            f"SKILL.md must mention the MCP tool '{tool_name}' in the "
            "chrome-devtools verification SOP."
        )

    def test_mobile_viewport_near_take_screenshot(self, skill_md: str) -> None:
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
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        assert "375" in sop_section, (
            "Mobile viewport width '375' must be pinned in the Verification SOP."
        )
        assert "812" in sop_section, (
            "Mobile viewport height '812' must be pinned in the Verification SOP."
        )

    def test_lighthouse_threshold_90_present(self, skill_md: str) -> None:
        """The threshold '90' must sit within ~120 chars of 'lighthouse_audit'
        — proximity guards against the threshold drifting out of the audit
        step it governs."""
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
        assert not re.search(r"needs human verification", skill_md, re.IGNORECASE), (
            "'Needs human verification' is the pre-refactor handoff phrase — "
            "it must be removed in favour of automated chrome-devtools checks."
        )

    def test_no_human_directed_screenshot_instruction(self, skill_md: str) -> None:
        assert not re.search(
            r"(take a screenshot|screenshot the page).*(yourself|manually)",
            skill_md,
            re.IGNORECASE,
        ), (
            "Instructions asking the human to 'take a screenshot … yourself' or "
            "'screenshot the page … manually' must be removed after the refactor."
        )

    def test_console_error_failure_condition_present(self, skill_md: str) -> None:
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
        lh_idx = skill_md.lower().find("lighthouse")
        assert lh_idx != -1, "The word 'lighthouse' must appear in SKILL.md."
        window = skill_md[max(0, lh_idx - 300) : lh_idx + 300]
        assert re.search(r"threshold|score|fail", window, re.IGNORECASE), (
            "A lighthouse failure condition must be present: 'lighthouse' and "
            "one of 'threshold'/'score'/'fail' must appear within 300 characters."
        )


class TestHttpServerSop:
    """The verification SOP must use a local HTTP server, not file:// URLs."""

    def test_sop_uses_http_server_not_file_url_for_lighthouse(
        self, skill_md: str
    ) -> None:
        """lighthouse_audit rejects file:// URLs with INVALID_URL — the SOP
        must document serving over HTTP so the audit can run."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        assert re.search(r"http\.server|localhost", sop_section, re.IGNORECASE), (
            "The Verification SOP must mention 'http.server' or 'localhost' to "
            "document serving the HTML via HTTP rather than a file:// URL."
        )

    def test_sop_documents_lighthouse_file_url_limitation(self, skill_md: str) -> None:
        """Pin the rationale next to the step so the agent doesn't regress
        back to a file:// URL in a future edit."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        has_invalid_url = "INVALID_URL" in sop_section
        has_file_rejection = bool(
            re.search(
                r"file://.*(?:lighthouse|reject|require|http|limitation)"
                r"|(?:lighthouse|reject|require|http|limitation).*file://",
                sop_section,
                re.IGNORECASE | re.DOTALL,
            )
        )
        assert has_invalid_url or has_file_rejection, (
            "The Verification SOP must explain that lighthouse_audit rejects "
            "file:// URLs (mention 'INVALID_URL', or pair 'file://' with "
            "'lighthouse'/'reject'/'require'/'http'/'limitation')."
        )

    def test_sop_documents_server_lifecycle(self, skill_md: str) -> None:
        """Pair start with stop — a server that starts but never stops risks
        port collisions on the next invocation."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        has_start = bool(
            re.search(r"start.*server|server.*start", sop_section, re.IGNORECASE)
        )
        has_stop = bool(
            re.search(r"stop|kill|tear\s*down|teardown", sop_section, re.IGNORECASE)
        )
        assert has_start, (
            "The Verification SOP must document a server-start step "
            "('start … server' or 'server … start')."
        )
        assert has_stop, (
            "The Verification SOP must document a server-stop/teardown step "
            "('stop', 'kill', 'teardown', or 'tear down')."
        )

    def test_navigate_page_uses_http_url_form_in_sop(self, skill_md: str) -> None:
        """Drift guard: ensure navigate_page was updated alongside the server
        step, with no stale file:// URL left behind."""
        sop_section = _extract_verification_section(skill_md)
        assert sop_section, "## Verification (chrome-devtools) section must exist."
        nav_match = re.search(r"navigate_page", sop_section)
        assert nav_match, "'navigate_page' must appear in the Verification SOP."
        start = max(0, nav_match.start() - 50)
        end = min(len(sop_section), nav_match.end() + 250)
        window = sop_section[start:end]
        assert "http://" in window, (
            "The navigate_page step in the Verification SOP must use 'http://' "
            "(not 'file://') as its example URL."
        )


class TestSlotCrossCheck:
    """Every {{...}} placeholder in baseline.html must appear in SKILL.md slot docs."""

    def test_all_baseline_placeholders_in_skill_md_slot_section(
        self, baseline_html: str, skill_md: str
    ) -> None:
        """Drift guard between baseline.html slots and the '### Slot conventions'
        section of SKILL.md."""
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
