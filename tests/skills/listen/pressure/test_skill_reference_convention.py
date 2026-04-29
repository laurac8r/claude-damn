from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[4] / "skills" / "listen" / "SKILL.md"


def test_skill_md_has_skill_reference_convention_section() -> None:
    text = SKILL_MD.read_text()
    assert "## Skill Reference Convention" in text


def test_convention_distinguishes_bare_vs_backticks() -> None:
    text = SKILL_MD.read_text()
    assert "Bare `/foo`" in text
    assert "invocation directive" in text
    assert "content reference" in text


def test_convention_handles_bracket_anchored_tesseract() -> None:
    text = SKILL_MD.read_text()
    assert "Bracket-anchored skills inside `/tesseract` calls" in text
    assert "remain invocation directives" in text


def test_rationalization_counter_present() -> None:
    text = SKILL_MD.read_text()
    assert "Bracket-anchored = still invocation directive" in text
