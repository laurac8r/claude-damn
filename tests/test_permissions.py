"""Regression tests: permission allow/deny/ask patterns."""

import pytest


class TestAllowPatterns:
    """Critical allow rules that must remain present."""

    @pytest.mark.parametrize(
        "pattern",
        [
            "Bash(git status)",
            "Bash(git log *)",
            "Bash(git diff *)",
            "Bash(git show *)",
            "Bash(ls *)",
            "Bash(uv run pytest*)",
            "Bash(uv run ruff check*)",
            "Bash(uv run ruff format*)",
            "Bash(uv sync*)",
            "Bash(bats *)",
            "Bash(npm run build)",
            "Bash(npm run test *)",
            "Bash(flutter test*)",
        ],
    )
    def test_essential_allow_patterns_present(
        self, allow_list: list[str], pattern: str
    ) -> None:
        assert pattern in allow_list, f"Missing allow pattern: {pattern}"

    @pytest.mark.parametrize(
        "pattern",
        [
            "Read(~/.claude/**)",
            "Write(~/.claude/cost-log/**)",
            "Search(~/.claude/**)",
        ],
    )
    def test_claude_dir_access_allowed(
        self, allow_list: list[str], pattern: str
    ) -> None:
        assert pattern in allow_list, f"Missing claude dir access: {pattern}"


class TestDenyPatterns:
    """Critical deny rules that must never be removed."""

    @pytest.mark.parametrize(
        "pattern",
        [
            "Bash(*git commit *)",
            "Bash(*gh pr create*)",
            "Bash(*gh pr merge*)",
            "Bash(*gh pr close*)",
            "Bash(*gh issue create*)",
            "Bash(*gh issue close*)",
            "Bash(*gh issue delete*)",
            "Bash(gh repo create*)",
            "Bash(gh repo delete*)",
            "Bash(gh release create*)",
            "Bash(gh release delete*)",
            "Bash(gh gist create*)",
            "Bash(gh gist delete*)",
        ],
    )
    def test_destructive_gh_commands_denied(
        self, deny_list: list[str], pattern: str
    ) -> None:
        assert pattern in deny_list, f"Missing deny pattern: {pattern}"

    @pytest.mark.parametrize(
        "pattern",
        [
            "Bash(gh api *-X POST*)",
            "Bash(gh api *-X PUT*)",
            "Bash(gh api *-X PATCH*)",
            "Bash(gh api *-X DELETE*)",
            "Bash(gh api *--method POST*)",
            "Bash(gh api *--method PUT*)",
            "Bash(gh api *--method PATCH*)",
            "Bash(gh api *--method DELETE*)",
        ],
    )
    def test_mutating_api_calls_denied(
        self, deny_list: list[str], pattern: str
    ) -> None:
        assert pattern in deny_list, f"Missing API deny pattern: {pattern}"

    def test_git_commit_denied(self, deny_list: list[str]) -> None:
        assert "Bash(*git commit *)" in deny_list


class TestAskPatterns:
    """Commands that require explicit confirmation."""

    @pytest.mark.parametrize(
        "pattern",
        [
            "Bash(gh api*)",
            "Bash(find*-delete*)",
            "Bash(find*-exec*)",
            "Bash(sed*-i*)",
        ],
    )
    def test_dangerous_commands_require_ask(
        self, ask_list: list[str], pattern: str
    ) -> None:
        assert pattern in ask_list, f"Missing ask pattern: {pattern}"


class TestSkillWorkflowWrites:
    """Allow rules for skill-driven content directories (no prompt needed)."""

    def test_brainstorm_content_writable(self, allow_list: list[str]) -> None:
        assert "Write(**/.superpowers/brainstorm/**)" in allow_list


class TestNoOverlap:
    """Deny must not contain patterns also in allow (deny takes priority,
    but overlaps signal config mistakes)."""

    def test_no_allow_deny_exact_overlap(
        self, allow_list: list[str], deny_list: list[str]
    ) -> None:
        overlap = set(allow_list) & set(deny_list)
        assert not overlap, f"Pattern in both allow and deny: {overlap}"
