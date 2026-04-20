"""Performance/stress tests: /learn skill across a model × prompt matrix.

Non-deterministic. 90% pass rate is the quality gate. Each cell invokes
/learn once with a different prompt complexity and model; assertions
check the skill's playbook vocabulary, not exact prose.
"""

import pytest

pytestmark = pytest.mark.performance

SIMPLE_PROMPTS = {
    "taxonomy": (
        "/learn : name the two classifications in one line",
        ["misfire", "preference"],
    ),
    "delegate": (
        "/learn : in one line, name the skill /learn delegates fixes to",
        ["writing-skills"],
    ),
    "enforcement": (
        "/learn : in one line, name the skill /learn invokes first to "
        "enforce its workflow",
        ["listen"],
    ),
}

COMPLEX_PROMPTS = {
    "taxonomy": (
        "/learn : list the full signal taxonomy with one-line definitions, "
        "then name the two classifications and the decision rule between them",
        ["misfire", "preference", "skipped", "ignored"],
    ),
    "delegate": (
        "/learn : describe the full approval flow from signal detection "
        "through /writing-skills invocation, including per-finding gates",
        ["writing-skills", "approve", "misfire"],
    ),
    "enforcement": (
        "/learn : explain how /learn's body composes with /listen and "
        "/writing-skills, and why /listen's enforcement matters",
        ["listen", "writing-skills", "enforce"],
    ),
}

COMPLEXITY_LEVELS = {
    "simple": SIMPLE_PROMPTS,
    "complex": COMPLEX_PROMPTS,
}

MODELS = ["haiku", "sonnet", "opus"]

PROMPT_KEYS = ["taxonomy", "delegate", "enforcement"]


def _build_matrix() -> list[tuple[str, str, str, list[str]]]:
    """Build the 2×3×3 test matrix."""
    matrix: list[tuple[str, str, str, list[str]]] = []
    for complexity, prompts in COMPLEXITY_LEVELS.items():
        for key in PROMPT_KEYS:
            prompt, expected = prompts[key]
            for model in MODELS:
                test_id = f"{complexity}-{model}-{key}"
                matrix.append((test_id, model, prompt, expected))
    return matrix


MATRIX = _build_matrix()


@pytest.mark.parametrize(
    "test_id, model, prompt, expected_phrases",
    MATRIX,
    ids=[m[0] for m in MATRIX],
)
class TestLearnMatrix:
    """Exercise /learn across 2×3×3 = 18 cells. One invocation per cell."""

    def test_cell(
        self,
        test_id: str,
        model: str,
        prompt: str,
        expected_phrases: list[str],
        invoke_skill,
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
            f"[{test_id}] No evidence of /learn vocabulary. "
            f"Expected >= 1 of {expected_phrases}, "
            f"got:\n{result.stdout[:500]}"
        )