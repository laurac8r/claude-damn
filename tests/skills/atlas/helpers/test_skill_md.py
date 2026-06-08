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
