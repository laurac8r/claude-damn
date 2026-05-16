"""Structural tests for skills/add-to-roadmap/SKILL.md.

Verifies frontmatter correctness, required body sections, slug-name/dir
alignment, and argument-hint string against the canonical spec.
"""

from __future__ import annotations

import re
from pathlib import Path


class TestAddToRoadmapStructure:
    """Structural invariants for skills/add-to-roadmap/SKILL.md."""

    def test_frontmatter_name_field(self, frontmatter: dict) -> None:
        """name: field must equal the skill slug."""
        assert frontmatter.get("name") == "add-to-roadmap"

    def test_frontmatter_description_present_and_nonempty(
        self, frontmatter: dict
    ) -> None:
        """description: must be a non-empty string."""
        assert isinstance(frontmatter.get("description"), str)
        assert len(frontmatter["description"].strip()) > 0

    def test_frontmatter_user_invocable_true(self, frontmatter: dict) -> None:
        """user-invocable: must be the boolean True."""
        assert frontmatter.get("user-invocable") is True

    def test_frontmatter_argument_hint_present(self, frontmatter: dict) -> None:
        """argument-hint: must be present."""
        assert "argument-hint" in frontmatter

    def test_frontmatter_argument_hint_canonical_form(self, frontmatter: dict) -> None:
        """argument-hint: must equal the canonical '<phase-or-section> :: <task-text>'.

        This is the exact string the slash-command renderer displays as the
        usage hint.
        """
        assert frontmatter["argument-hint"] == "<phase-or-section> :: <task-text>"

    def test_skill_dir_name_matches_frontmatter_name(
        self, skill_root: Path, frontmatter: dict
    ) -> None:
        """Skill directory name must match frontmatter name:."""
        assert skill_root.name == frontmatter["name"], (
            f"Directory '{skill_root.name}' does not match frontmatter "
            f"name '{frontmatter['name']}'."
        )

    def test_section_locating_roadmap_md(self, skill_md: str) -> None:
        """Body must have a '## Locating ROADMAP.md' section."""
        assert re.search(r"^## Locating ROADMAP\.md", skill_md, re.MULTILINE), (
            "Missing '## Locating ROADMAP.md' section."
        )

    def test_section_address_space_resolution(self, skill_md: str) -> None:
        """Body must have an address-space resolution section."""
        assert re.search(r"^## Address-space resolution", skill_md, re.MULTILINE), (
            "Missing '## Address-space resolution' section."
        )

    def test_section_item_formatting(self, skill_md: str) -> None:
        """Body must have an item-formatting section."""
        assert re.search(r"^## Item formatting", skill_md, re.MULTILINE), (
            "Missing '## Item formatting' section."
        )

    def test_section_examples(self, skill_md: str) -> None:
        """Body must have an Examples section."""
        assert re.search(r"^## Examples", skill_md, re.MULTILINE), (
            "Missing '## Examples' section."
        )
