"""SKILL.md structural tests for /atlas."""

from __future__ import annotations


def test_frontmatter_has_required_fields(frontmatter: dict) -> None:
    assert frontmatter.get("name") == "atlas"
    assert "description" in frontmatter and frontmatter["description"]


def test_prose_mentions_read_only_invariant(skill_md: str) -> None:
    assert "read-only" in skill_md.lower()


def test_prose_references_render_function(skill_md: str) -> None:
    assert "render(" in skill_md


def test_prose_references_shared_helpers(skill_md: str) -> None:
    for fn in ("resolve_anchor", "parse_shelf", "parse_git", "parse_checkpoint"):
        assert fn in skill_md


def test_prose_documents_task_tool_fallback(skill_md: str) -> None:
    assert "absent from the tool surface" in skill_md
    assert "fallback" in skill_md.lower()


def test_fallback_specifies_markdown_table(skill_md: str) -> None:
    assert "Markdown table" in skill_md
    assert "| ID | Subject | Status | Blocked by |" in skill_md


def test_invariants_covers_task_tool_fallback(skill_md: str) -> None:
    start = skill_md.index("## Invariants")
    end = skill_md.index("## Anti-shortcuts")
    invariants = skill_md[start:end]
    assert "task" in invariants.lower()
    assert "markdown table" in invariants.lower()
    assert "abort" in invariants.lower()
