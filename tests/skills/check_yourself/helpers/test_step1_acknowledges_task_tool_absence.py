"""Step 1 (update the task list) must work when the Task* tools are absent
from the tool surface, not just when TaskList/TaskUpdate are callable.

Background: an interactive session may have TaskCreate/TaskUpdate/TaskList/
TaskGet gated off the tool surface entirely (GrowthBook flag; legacy
TodoWrite can be absent too). check-yourself's Step 1 says to "display the
current task list" without ever calling a Task* tool directly, but it also
never acknowledges that the underlying state might be a Markdown list/table
the agent is maintaining by hand rather than tool-backed state. Without that
acknowledgment, an agent hitting the tools-absent case has no signal that
Step 1 still applies and no instruction on how to behave.
"""

from __future__ import annotations


def test_step1_acknowledges_task_tools_may_be_absent(skill_md: str) -> None:
    step_1_start = skill_md.index("**Update the task list.**")
    # Bound the window to Step 1's own text — up to the next numbered step —
    # rather than a fixed character count, so the check doesn't silently
    # truncate the tail if Step 1's bullet grows or shrinks.
    step_1_end = skill_md.index("2. **Run /remember.**", step_1_start)
    window = skill_md[step_1_start:step_1_end]

    assert "TaskCreate" in window
    assert "TaskUpdate" in window
    assert "TaskList" in window
    assert "TaskGet" in window
    assert "absent" in window.lower()


def test_step1_fallback_states_once(skill_md: str) -> None:
    """Constraint: any fallback must tell the agent to state once that it is
    using the fallback and why — not silently improvise, and not repeat the
    caveat every boundary."""
    step_1_start = skill_md.index("**Update the task list.**")
    step_1_end = skill_md.index("2. **Run /remember.**", step_1_start)
    window = skill_md[step_1_start:step_1_end]

    assert "state once" in window.lower() or "once" in window.lower()
