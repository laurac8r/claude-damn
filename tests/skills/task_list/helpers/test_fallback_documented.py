"""SKILL.md documents a fallback path for when the Task* tools are absent."""

from __future__ import annotations


def test_documents_fallback_when_task_tools_absent(skill_md: str) -> None:
    heading = "## Fallback: Task tools absent from the tool surface"
    assert heading in skill_md
    # Scope to the Fallback section itself — the tool names already appear
    # in the pre-existing Modes sections, so an unscoped check would pass
    # regardless of what the Fallback section actually says.
    fallback = skill_md[skill_md.index(heading) :]
    for tool in ("TaskCreate", "TaskUpdate", "TaskList", "TaskGet"):
        assert tool in fallback
