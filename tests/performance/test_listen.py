"""Performance/stress tests: /listen skill across a matrix of parameters.

Matrix: prompt complexity (2) × model type (3) × subagent count (3) = 18
combinations. Non-deterministic. 90% pass rate is the quality gate.
"""

import pytest

from tests._skill_helpers import invoke_skill

pytestmark = pytest.mark.performance


SIMPLE_PROMPTS = {
    "0_subagents": (
        '/listen /tdd : say "TDD_OK"',
        ["tdd"],
    ),
    "1_subagent": (
        '/listen /cat : say "CAT_OK"',
        ["cat", "subagent"],
    ),
    "2_subagents": (
        '/listen /super-duper-cat : say "LOADED"',
        ["brainstorm", "worktree", "subagent"],
    ),
}

COMPLEX_PROMPTS = {
    "0_subagents": (
        "/listen /tdd /review /expert-review : "
        "list every skill you were asked to invoke, "
        "describe each in one sentence, "
        "and confirm you invoked all of them",
        ["tdd", "review", "expert"],
    ),
    "1_subagent": (
        "/listen /cat : plan a 3-step task, "
        "dispatch a subagent for step 1, "
        "then report what happened",
        ["subagent", "task", "step"],
    ),
    "2_subagents": (
        "/listen /super-duper-cat : "
        "walk through the brainstorming process, "
        "explain how worktrees provide isolation, "
        "and describe how subagents execute tasks",
        ["brainstorm", "worktree", "subagent"],
    ),
}

COMPLEXITY_LEVELS = {
    "simple": SIMPLE_PROMPTS,
    "complex": COMPLEX_PROMPTS,
}

MODELS = ["haiku", "sonnet", "opus"]

SUBAGENT_COUNTS = ["0_subagents", "1_subagent", "2_subagents"]


def _build_matrix() -> list[tuple[str, str, str, list[str]]]:
    """Build the 2×3×3 test matrix."""
    matrix: list[tuple[str, str, str, list[str]]] = []
    for complexity, prompts in COMPLEXITY_LEVELS.items():
        for subagent_key in SUBAGENT_COUNTS:
            prompt, expected = prompts[subagent_key]
            for model in MODELS:
                test_id = f"{complexity}-{model}-{subagent_key}"
                matrix.append((test_id, model, prompt, expected))
    return matrix


MATRIX = _build_matrix()


@pytest.mark.parametrize(
    "test_id, model, prompt, expected_phrases",
    MATRIX,
    ids=[m[0] for m in MATRIX],
)
class TestListenMatrix:
    """Exercise /listen across the 2×3×3 parameter matrix.

    One invocation per cell; all assertions share the same result.
    """

    def test_cell(
        self,
        test_id: str,
        model: str,
        prompt: str,
        expected_phrases: list[str],
    ) -> None:
        result = invoke_skill(prompt, model=model, timeout=180)

        assert result.returncode == 0, (
            f"[{test_id}] Non-zero exit: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )

        assert len(result.stdout.strip()) > 0, f"[{test_id}] Empty output"

        output = result.stdout.lower()
        matched = [p for p in expected_phrases if p in output]
        assert len(matched) >= 1, (
            f"[{test_id}] No evidence of skill invocation. "
            f"Expected >= 1 of {expected_phrases}, "
            f"got:\n{result.stdout[:500]}"
        )
