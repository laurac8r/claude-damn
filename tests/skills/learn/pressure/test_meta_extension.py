from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[4] / "skills" / "learn" / "SKILL.md"


def test_classifier_table_present() -> None:
    text = SKILL_MD.read_text()
    assert "Classify fix target before invoking /writing-skills" in text
    assert "Target | Signal | How to fix" in text


def test_classifier_covers_all_four_tiers() -> None:
    text = SKILL_MD.read_text()
    # SKILL.md tier
    assert "**SKILL.md**" in text
    # CLAUDE.md / PERSONALIZATION.md tier
    assert "CLAUDE.md / PERSONALIZATION.md" in text
    # Hookify tier
    assert "Hookify rule" in text or "**Hookify" in text
    # settings.json tier
    assert "settings.json" in text


def test_settings_json_routes_to_update_config() -> None:
    text = SKILL_MD.read_text()
    assert "/update-config" in text
    assert "JSON delta" in text


def test_hookify_routes_to_writing_rules() -> None:
    text = SKILL_MD.read_text()
    assert "/writing-rules" in text


def test_global_policy_files_not_auto_edited() -> None:
    text = SKILL_MD.read_text()
    assert "never auto-edited" in text or "Do NOT auto-edit" in text


def test_when_in_doubt_heuristic_present() -> None:
    text = SKILL_MD.read_text()
    assert "When in doubt" in text
    assert "any skill could exhibit" in text
