"""Performance/stress tests: /proceed skill across a matrix of parameters.

Matrix: complexity (2) × prompt kind (2) × model (3) = 12 combinations.
Non-deterministic. 90% pass rate is the quality gate.
"""

import pytest

pytestmark = pytest.mark.performance

EXPECTED_PHRASES = [
    "aligned",
    "approved",
    "gate",
    "proceed",
    "current",
    "single",
    "only",
]

SIMPLE_PROMPTS = {
    "summarize": "/proceed : summarize in one sentence what this skill does",
    "single_gate": "/proceed : confirm this only applies to the current gate",
}

COMPLEX_PROMPTS = {
    "summarize": (
        "/proceed : explain in detail what this skill does, "
        "describe the scope of authorization it grants, "
        "and clarify whether it applies to future gates"
    ),
    "single_gate": (
        "/proceed : contrast single-gate approval against standing authorization, "
        "describe when a user should NOT use this skill, "
        "and explain what 'current gate only' means in practice"
    ),
}

COMPLEXITY_LEVELS = {
    "simple": SIMPLE_PROMPTS,
    "complex": COMPLEX_PROMPTS,
}

MODELS = ["haiku", "sonnet", "opus"]


def _build_matrix() -> list[tuple[str, str, str]]:
    """Build the 2×2×3 test matrix."""
    matrix: list[tuple[str, str, str]] = []
    for complexity, prompts in COMPLEXITY_LEVELS.items():
        for prompt_key, prompt in prompts.items():
            for model in MODELS:
                test_id = f"{complexity}-{prompt_key}-{model}"
                matrix.append((test_id, model, prompt))
    return matrix


MATRIX = _build_matrix()


@pytest.mark.parametrize(
    "test_id, model, prompt",
    MATRIX,
    ids=[m[0] for m in MATRIX],
)
class TestProceedMatrix:
    """Exercise /proceed across the 2×3 parameter matrix.

    One invocation per cell; all assertions share the same result.
    """

    def test_cell(
        self,
        test_id: str,
        model: str,
        prompt: str,
        invoke_skill,
    ) -> None:
        result = invoke_skill(prompt, model=model, timeout=180)

        assert result.returncode == 0, (
            f"[{test_id}] Non-zero exit: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )

        assert len(result.stdout.strip()) > 0, f"[{test_id}] Empty output"

        output = result.stdout.lower()
        matched = [p for p in EXPECTED_PHRASES if p in output]
        assert len(matched) >= 1, (
            f"[{test_id}] No evidence of skill invocation. "
            f"Expected >= 1 of {EXPECTED_PHRASES}, "
            f"got:\n{result.stdout[:500]}"
        )
