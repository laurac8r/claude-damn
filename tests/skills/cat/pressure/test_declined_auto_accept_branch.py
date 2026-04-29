from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[4] / "skills" / "cat" / "SKILL.md"


def test_skill_md_documents_declined_auto_accept_branch() -> None:
    text = SKILL_MD.read_text()
    assert "If the operator declines auto-accept" in text
    assert "Permission to use Write has been denied" in text
    assert "Flip auto-accept on now" in text  # option (a)
    assert "Abort and route the work elsewhere" in text  # option (c)


def test_skill_md_warns_about_misdiagnosis() -> None:
    text = SKILL_MD.read_text()
    assert "misdiagnosis" in text.lower() or "misattribute" in text.lower()


def test_rationalization_counter_includes_manual_approval_row() -> None:
    text = SKILL_MD.read_text()
    assert "denials are explicit" in text
