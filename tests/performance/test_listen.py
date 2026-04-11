"""Performance/stress tests: /listen skill across a matrix of parameters.

Matrix: prompt complexity (5) × model type (5) × subagent count (5) = 125 combinations.
Non-deterministic. 90% pass rate is the quality gate. Cost is not a concern.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

pytestmark = pytest.mark.performance

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class SkillResult:
    """Captured output from a Claude Code skill invocation."""

    stdout: str
    stderr: str
    returncode: int


# ---------------------------------------------------------------------------
# Matrix dimension: Prompt complexity (5 levels)
# Each level maps subagent_count -> (prompt, expected_phrases)
# ---------------------------------------------------------------------------

TRIVIAL_PROMPTS = {
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
    "3_subagents": (
        '/listen /tdd /review /cat : say "ALL_OK"',
        ["tdd", "review"],
    ),
    "5+_subagents": (
        '/listen /tdd /review /cat /super /duper : say "FIVE_OK"',
        ["tdd", "review"],
    ),
}

SIMPLE_PROMPTS = {
    "0_subagents": (
        "/listen /tdd : list the 3 core steps of TDD in a numbered list",
        ["red", "green", "refactor", "tdd", "test"],
    ),
    "1_subagent": (
        "/listen /cat : create a single task and report its status",
        ["subagent", "task"],
    ),
    "2_subagents": (
        "/listen /super-duper-cat : list the skills you loaded",
        ["brainstorm", "worktree", "subagent", "tdd"],
    ),
    "3_subagents": (
        "/listen /tdd /review /cat : name each skill you invoked",
        ["tdd", "review", "cat"],
    ),
    "5+_subagents": (
        "/listen /tdd /review /cat /super /duper : name each skill you invoked",
        ["tdd", "review"],
    ),
}

MEDIUM_PROMPTS = {
    "0_subagents": (
        "/listen /tdd /review : list which skills you were asked to invoke and briefly describe each",
        ["tdd", "review"],
    ),
    "1_subagent": (
        "/listen /cat : create a task list with 2 items, then say DONE",
        ["subagent", "task", "done"],
    ),
    "2_subagents": (
        "/listen /super-duper-cat : describe your brainstorming approach and how TDD fits in",
        ["brainstorm", "tdd", "test"],
    ),
    "3_subagents": (
        "/listen /tdd /review /cat : for each skill, explain its purpose in one sentence",
        ["tdd", "review", "cat"],
    ),
    "5+_subagents": (
        "/listen /tdd /review /cat /super /duper : "
        "list every skill you were asked to invoke, confirm you invoked each",
        ["tdd", "review"],
    ),
}

COMPLEX_PROMPTS = {
    "0_subagents": (
        "/listen /tdd /review /expert-review : list every skill you were asked to invoke, "
        "describe the purpose of each in one sentence, and confirm you invoked all of them",
        ["tdd", "review", "expert"],
    ),
    "1_subagent": (
        "/listen /cat : plan a 3-step task, dispatch a subagent for step 1, "
        "then report what happened",
        ["subagent", "task", "step"],
    ),
    "2_subagents": (
        "/listen /super-duper-cat : walk through the brainstorming process, "
        "explain how worktrees provide isolation, and describe how subagents execute tasks",
        ["brainstorm", "worktree", "subagent", "isolation"],
    ),
    "3_subagents": (
        "/listen /tdd /review /cat : for each skill, explain its core principle, "
        "describe how it changes your workflow, and confirm it was invoked",
        ["tdd", "review", "cat", "invoke"],
    ),
    "5+_subagents": (
        "/listen /tdd /review /cat /super /duper : "
        "for each of the 5 skills, explain its purpose, describe how it interacts with the others, "
        "and confirm all were invoked",
        ["tdd", "review", "invoke"],
    ),
}

EXTREME_PROMPTS = {
    "0_subagents": (
        "/listen /tdd /review /expert-review /check-yourself : "
        "list every skill referenced, describe each in detail including its checklist steps, "
        "explain how they complement each other, and produce a summary table of all invocations",
        ["tdd", "review", "expert", "check"],
    ),
    "1_subagent": (
        "/listen /cat : design a 5-step implementation plan for a hypothetical feature, "
        "dispatch a subagent for step 1, have it report back, then summarize the overall status "
        "including what remains to be done",
        ["subagent", "task", "plan", "step"],
    ),
    "2_subagents": (
        "/listen /super-duper-cat : walk through the entire brainstorming-to-implementation "
        "pipeline, explain each phase in detail (brainstorming, worktree setup, TDD cycle, "
        "subagent dispatch), describe the handoffs between phases, and produce a summary of "
        "all skills that were loaded",
        ["brainstorm", "worktree", "subagent", "tdd"],
    ),
    "3_subagents": (
        "/listen /tdd /review /cat : for each skill, produce a detailed breakdown including "
        "its core philosophy, the specific steps it requires, how it interacts with the other "
        "two skills, and a confirmation that it was properly invoked with evidence",
        ["tdd", "review", "cat", "invoke"],
    ),
    "5+_subagents": (
        "/listen /tdd /review /cat /super /duper : "
        "produce a comprehensive report covering all 5 skills: for each, explain its purpose, "
        "enumerate its required steps, describe its interactions with every other skill in the set, "
        "confirm it was invoked, and conclude with a cross-reference matrix showing which skills "
        "complement or depend on each other",
        ["tdd", "review", "invoke", "skill"],
    ),
}

COMPLEXITY_LEVELS = {
    "trivial": TRIVIAL_PROMPTS,
    "simple": SIMPLE_PROMPTS,
    "medium": MEDIUM_PROMPTS,
    "complex": COMPLEX_PROMPTS,
    "extreme": EXTREME_PROMPTS,
}

MODELS = ["haiku", "sonnet", "opus", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]

SUBAGENT_COUNTS = [
    "0_subagents",
    "1_subagent",
    "2_subagents",
    "3_subagents",
    "5+_subagents",
]


def _model_flag(model: str) -> list[str]:
    """Convert model name to CLI flags."""
    return ["--model", model]


def _build_matrix() -> list[tuple[str, str, str, list[str]]]:
    """Build the full test matrix: (test_id, model, prompt, expected_phrases)."""
    matrix = []
    for complexity, prompts in COMPLEXITY_LEVELS.items():
        for subagent_key in SUBAGENT_COUNTS:
            prompt, expected = prompts[subagent_key]
            for model in MODELS:
                model_label = model.replace(".", "-")
                test_id = f"{complexity}-{model_label}-{subagent_key}"
                matrix.append((test_id, model, prompt, expected))
    return matrix


def _invoke_with_model(prompt: str, model: str, timeout: int = 180) -> SkillResult:
    """Invoke skill with model spec that may include flags like --fast."""
    flags = _model_flag(model)
    result = subprocess.run(
        ["claude", "-p", prompt] + flags,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )
    return SkillResult(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )


MATRIX = _build_matrix()


@pytest.mark.parametrize(
    "test_id, model, prompt, expected_phrases",
    MATRIX,
    ids=[m[0] for m in MATRIX],
)
class TestListenMatrix:
    """Exercise /listen across the full 5x5x5 parameter matrix."""

    def test_completes_without_error(
        self,
        test_id: str,
        model: str,
        prompt: str,
        expected_phrases: list[str],  # noqa: ARG002
    ) -> None:
        result = _invoke_with_model(prompt, model)
        assert result.returncode == 0, (
            f"[{test_id}] Non-zero exit code: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )

    def test_produces_output(
        self,
        test_id: str,
        model: str,
        prompt: str,
        expected_phrases: list[str],  # noqa: ARG002
    ) -> None:
        result = _invoke_with_model(prompt, model)
        assert len(result.stdout.strip()) > 0, f"[{test_id}] Empty output"

    def test_shows_skill_evidence(
        self,
        test_id: str,
        model: str,
        prompt: str,
        expected_phrases: list[str],
    ) -> None:
        result = _invoke_with_model(prompt, model)
        output = result.stdout.lower()
        matched = [p for p in expected_phrases if p in output]
        assert len(matched) >= 1, (
            f"[{test_id}] No evidence of skill invocation. "
            f"Expected at least one of {expected_phrases}, "
            f"got:\n{result.stdout[:500]}"
        )
