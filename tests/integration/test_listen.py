"""Integration regression tests: /listen skill repo integration."""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
SKILL_DIR = SKILLS_DIR / "listen"
SKILL_PATH = SKILL_DIR / "SKILL.md"


class TestOldNameAbsent:
    """Verify no trace of the old /enforce skill name remains."""

    def test_enforce_dir_not_in_skills(self) -> None:
        skill_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        assert "enforce" not in skill_dirs

    def test_listen_dir_in_skills(self) -> None:
        skill_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        assert "listen" in skill_dirs

    def test_no_enforce_skill_invocation_in_repo(self) -> None:
        """Scan all non-test files for '/enforce' as a skill invocation."""
        hits: list[str] = []
        for path in PROJECT_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in (".md", ".py", ".sh", ".json", ".toml", ".yaml", ".yml"):
                continue
            if "test_listen" in path.name:
                continue
            if ".venv" in path.parts or "node_modules" in path.parts:
                continue
            try:
                text = path.read_text()
            except (UnicodeDecodeError, PermissionError):
                continue
            if "/enforce" in text:
                # Filter out false positives: "enforce" as a general word vs skill invocation
                for i, line in enumerate(text.splitlines(), 1):
                    if "/enforce" in line:
                        hits.append(f"{path.relative_to(PROJECT_ROOT)}:{i}: {line.strip()}")
        assert not hits, "Found /enforce references:\n" + "\n".join(hits)


class TestSkillCompleteness:
    """Verify the skill is a complete, parseable unit."""

    def test_skill_has_frontmatter_and_body(self) -> None:
        text = SKILL_PATH.read_text()
        parts = text.split("---", 2)
        assert len(parts) >= 3, "Must have frontmatter delimiters"
        frontmatter = yaml.safe_load(parts[1])
        assert isinstance(frontmatter, dict)
        body = parts[2].strip()
        assert len(body) > 0, "Body must not be empty"

    def test_skill_dir_contains_only_skill_md(self) -> None:
        files = list(SKILL_DIR.iterdir())
        assert len(files) == 1
        assert files[0].name == "SKILL.md"
