"""SKILL.md documents a fallback path for when the Task* tools are absent."""

from __future__ import annotations


def test_documents_fallback_when_task_tools_absent(skill_md: str) -> None:
    assert "## Fallback: Task tools absent from the tool surface" in skill_md
    for tool in ("TaskCreate", "TaskUpdate", "TaskList", "TaskGet"):
        assert tool in skill_md
