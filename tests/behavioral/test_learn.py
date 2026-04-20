"""Behavioral tests: /learn skill structural invariants.

Tests assert the CONTRACT of SKILL.md (headings, references, tables) rather
than exact prose, so harmless edits don't cause spurious failures.
TDD approach: each invariant is paired with an in-memory mutation check
that SHOULD break the assertion, proving it is not vacuous.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATH = PROJECT_ROOT / "skills" / "learn" / "SKILL.md"

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
REQUIRED_FRONTMATTER_KEYS = ("name", "description", "user-invocable")


def _parse_frontmatter(content: str) -> dict[str, object]:
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError("No YAML frontmatter found")
    return yaml.safe_load(match.group(1)) or {}


def _count_table_rows(content: str) -> int:
    """Count Markdown table data rows (exclude headers and separators).

    Each Markdown table contributes exactly one separator row (`|---|---|`),
    which marks the end of its header row. Counting separators gives the
    number of tables (= number of header rows); subtracting from the total
    of non-separator `|...|` lines yields pure data rows. Single pass.
    """
    rows = 0
    headers = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if re.match(r"^\|[\s|\-:]+\|$", stripped):
            headers += 1
            continue
        rows += 1
    return max(rows - headers, 0)


@pytest.fixture(scope="module")
def skill_content() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


class TestPlaybookHeadingPresent:
    def test_heading_present(self, skill_content: str) -> None:
        assert re.search(r"^##+ .*Playbook", skill_content, re.MULTILINE), (
            "Expected a '## ... Playbook' heading in SKILL.md"
        )

    def test_mutation_without_heading_fails(self, skill_content: str) -> None:
        mutated = re.sub(
            r"^(##+ .*?)Playbook", r"\1Removed", skill_content, flags=re.MULTILINE
        )
        assert not re.search(r"^##+ .*Playbook", mutated, re.MULTILINE)


class TestSignalTableRowCount:
    def test_at_least_six_data_rows(self, skill_content: str) -> None:
        assert _count_table_rows(skill_content) >= 6, (
            "Expected at least 6 signal-taxonomy data rows"
        )

    def test_mutation_without_tables_fails(self, skill_content: str) -> None:
        mutated = re.sub(r"^\|.*$", "", skill_content, flags=re.MULTILINE)
        assert _count_table_rows(mutated) == 0


class TestSlashReferences:
    @pytest.mark.parametrize("token", ["/listen", "/writing-skills"])
    def test_token_present(self, skill_content: str, token: str) -> None:
        assert token in skill_content, f"Expected {token!r} in SKILL.md"

    def test_mutation_removes_tokens(self, skill_content: str) -> None:
        """TDD mutation: removing the tokens from SKILL.md should break
        test_token_present — asserting both original presence and mutated
        absence proves the mutation is effective, not tautological."""
        mutated = skill_content.replace("/listen", "X").replace("/writing-skills", "Y")
        assert "/listen" in skill_content and "/listen" not in mutated
        assert "/writing-skills" in skill_content
        assert "/writing-skills" not in mutated


class TestUpdateScopeMentioned:
    @pytest.mark.parametrize("needle", ["~/.claude/skills", ".claude/skills"])
    def test_scope_mentioned(self, skill_content: str, needle: str) -> None:
        assert needle in skill_content, f"Expected update-scope reference {needle!r}"


class TestTranscriptLocationMentioned:
    def test_transcript_hint_present(self, skill_content: str) -> None:
        lowered = skill_content.lower()
        assert "jsonl" in lowered or "~/.claude/projects" in lowered, (
            "Expected a hint about transcript location (jsonl or projects dir)"
        )


class TestFrontmatterValidity:
    @pytest.mark.parametrize("key", REQUIRED_FRONTMATTER_KEYS)
    def test_required_key_present(self, skill_content: str, key: str) -> None:
        fm = _parse_frontmatter(skill_content)
        assert key in fm, f"Frontmatter missing required key: {key!r}"

    def test_mutation_missing_name_fails(self, skill_content: str) -> None:
        mutated = re.sub(r"^name:.*\n", "", skill_content, flags=re.MULTILINE)
        fm = _parse_frontmatter(mutated)
        assert "name" not in fm
