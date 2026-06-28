"""Regression tests: block-inline-scripts.py hook behavior."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_SCRIPT = Path(__file__).parent.parent / "hooks" / "block-inline-scripts.py"
CONSTANTS_SCRIPT = HOOK_SCRIPT.parent / "constants.py"

_constants_spec = importlib.util.spec_from_file_location(
    "hook_constants", CONSTANTS_SCRIPT
)
assert _constants_spec is not None
assert _constants_spec.loader is not None
_constants = importlib.util.module_from_spec(_constants_spec)
_constants_spec.loader.exec_module(_constants)  # type: ignore[union-attr]
MAX_COMMAND_LENGTH: int = _constants.MAX_COMMAND_LENGTH
MAX_STATEMENT_COUNT: int = _constants.MAX_STATEMENT_COUNT


def run_hook(tool_name: str, command: str) -> dict[str, object]:
    """Feed a simulated tool call to the hook and return its JSON output."""
    payload = json.dumps(
        {
            "tool_name": tool_name,
            "tool_input": {"command": command},
        }
    )
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Hook crashed: {result.stderr}"
    return json.loads(result.stdout)


def _load_hook_module() -> object:
    """Load block-inline-scripts in-process, seeding sys.path so the hook's
    top-level ``from constants import ...`` resolves regardless of test
    ordering (otherwise an isolated run raises ModuleNotFoundError)."""
    hooks_dir = str(HOOK_SCRIPT.parent)
    sys.path.insert(0, hooks_dir)
    try:
        spec = importlib.util.spec_from_file_location(
            "block_inline_scripts", HOOK_SCRIPT
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    finally:
        sys.path.remove(hooks_dir)
    return mod


class TestHookBlocksInlineScripts:
    """Commands that MUST be blocked."""

    @pytest.mark.parametrize(
        "command",
        [
            'python3 -c "import os; os.listdir()"',
            "python -c 'x = 1\nprint(x)'",
            "python3 <<EOF\nprint('hello')\nEOF",
            "python3 <<'EOF'\nimport sys\nEOF",
            "ruby -c 'puts 1; puts 2'",
            "node -c 'console.log(1)\nconsole.log(2)'",
            "perl -e 'print 1; print 2'",
            "cat /tmp/script.py | python3",
            "echo 'print(1)' | python3",
            "echo 'puts 1' | ruby",
        ],
    )
    def test_blocks_inline_script(self, command: str) -> None:
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            f"Should block: {command!r}"
        )

    @pytest.mark.parametrize(
        "command",
        [
            'python3 -c "import os; os.listdir()"',
            "python3 <<EOF\nprint('hello')\nEOF",
            "cat /tmp/x.py | python3",
        ],
    )
    def test_blocked_output_has_deny_reason(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "BLOCKED" in reason


class TestHookAllowsSafeCommands:
    """Commands that must NOT be blocked."""

    @pytest.mark.parametrize(
        "command",
        [
            'python3 -c "print(1)"',
            "python3 /tmp/script_analysis.py",
            "uv run pytest tests/",
            "git status",
            "ls -la",
            "npm run build",
            "echo hello",
            "rg 'pattern' src/",
            "python3 --version",
        ],
    )
    def test_allows_safe_command(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow: {command!r}"


class TestCharLimit:
    """Commands exceeding MAX_COMMAND_LENGTH must be blocked."""

    def test_blocks_command_over_limit(self) -> None:
        command = "a" * (MAX_COMMAND_LENGTH + 1)
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_allows_command_at_exactly_limit(self) -> None:
        command = "a" * MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        assert output == {}

    def test_blocked_message_includes_length_and_limit(self) -> None:
        over_by_one = MAX_COMMAND_LENGTH + 1
        command = "a" * over_by_one
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert str(over_by_one) in reason
        assert str(MAX_COMMAND_LENGTH) in reason
        assert "BLOCKED" in reason


class TestStatementLimit:
    """Commands with too many statement separators must be blocked."""

    @pytest.mark.parametrize("sep", ["; ", " && ", " || ", " | "])
    def test_blocks_command_over_limit(self, sep: str) -> None:
        command = sep.join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocks_command_with_mixed_separators_over_limit(self) -> None:
        ops = [" && ", " | ", "; ", " > ", " || "][: MAX_STATEMENT_COUNT + 2]
        command = "echo 0" + "".join(f"{op}echo {i + 1}" for i, op in enumerate(ops))
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_allows_command_at_exactly_limit(self) -> None:
        ops = [" && ", " | ", "; ", " > ", " || "][:MAX_STATEMENT_COUNT]
        command = "echo 0" + "".join(f"{op}echo {i + 1}" for i, op in enumerate(ops))
        output = run_hook("Bash", command)
        assert output == {}

    def test_double_ampersand_counts_as_one(self) -> None:
        """'&&' is one separator, not two '&' characters."""
        command = " && ".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 1))
        output = run_hook("Bash", command)
        assert output == {}

    def test_double_pipe_counts_as_one(self) -> None:
        """'||' is one separator, not two '|' characters."""
        command = " || ".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 1))
        output = run_hook("Bash", command)
        assert output == {}

    def test_newline_counts_as_separator(self) -> None:
        command = "\n".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_carriage_return_counts_as_separator(self) -> None:
        command = "\r".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_redirect_counts_as_separator(self) -> None:
        command = "echo a" + "".join(f" > f{i}" for i in range(MAX_STATEMENT_COUNT + 1))
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocked_message_includes_count_and_limit(self) -> None:
        over_by_one = MAX_STATEMENT_COUNT + 1
        command = "; ".join(f"echo {i}" for i in range(over_by_one + 1))
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert str(over_by_one) in reason
        assert str(MAX_STATEMENT_COUNT) in reason
        assert "BLOCKED" in reason

    # --- Fix A: SEPARATOR_PATTERN must not double-count >> and << ---

    def test_double_right_redirect_pattern_counts_as_one(self) -> None:
        """Unit test: SEPARATOR_PATTERN.findall treats '>>' as one token."""
        mod = _load_hook_module()
        assert mod.SEPARATOR_PATTERN.findall("a >> b") == [">>"]  # type: ignore[union-attr]

    def test_double_left_redirect_pattern_counts_as_one(self) -> None:
        """Unit test: SEPARATOR_PATTERN.findall treats '<<' as one token."""
        mod = _load_hook_module()
        assert mod.SEPARATOR_PATTERN.findall("a << b") == ["<<"]  # type: ignore[union-attr]

    def test_double_right_redirect_allowed_at_limit(self) -> None:
        """Integration: MAX >> tokens = MAX separators — at the limit, allowed."""
        parts = ["echo a"] + [f"f{i}" for i in range(MAX_STATEMENT_COUNT)]
        command = " >> ".join(parts)
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow: {command!r}"


class TestMultipleViolations:
    """Commands tripping multiple rules report all violations."""

    def test_char_limit_and_statement_limit_both_reported(self) -> None:
        tail = "; ".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        command = "echo " + "a" * (MAX_COMMAND_LENGTH + 1) + "; " + tail
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "Command too long" in reason
        assert "Too many chained statements" in reason
        assert "---" in reason

    def test_all_three_rules_reported(self) -> None:
        tail = "; ".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        command = (
            'python3 -c "import os; os.listdir()" && '
            + "echo "
            + "a" * (MAX_COMMAND_LENGTH + 1)
            + "; "
            + tail
        )
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "Inline non-Bash script detected" in reason
        assert "Command too long" in reason
        assert "Too many chained statements" in reason


class TestTesseractPathBypass:
    """Tesseract path bypass: rules 2 & 3 are exempt; rule 1 still fires."""

    def test_tilde_path_char_limit_bypassed(self) -> None:
        """A long append to ~/.tesseract/ must NOT be blocked by rule 2."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> ~/.tesseract/bulk-beings.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow (tesseract bypass): {command!r}"

    def test_absolute_path_char_limit_bypassed(self) -> None:
        """Absolute /Users/<user>/.tesseract/ path also bypasses rule 2."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> /Users/laura/.tesseract/bulk-beings.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow (tesseract bypass): {command!r}"

    def test_home_env_var_path_char_limit_bypassed(self) -> None:
        """$HOME/.tesseract/ path bypasses rule 2."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> $HOME/.tesseract/bulk-beings.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow (tesseract bypass): {command!r}"

    def test_tesseract_path_statement_limit_bypassed(self) -> None:
        """Chained separators ending in a `>>` tesseract redirect bypass rule 3."""
        mod = _load_hook_module()
        # 5 separators: &&, ;, |, ;, >>
        command = (
            "echo a && echo b; echo c | grep d; echo e >> ~/.tesseract/bulk-beings.md"
        )
        sep_count = len(mod.SEPARATOR_PATTERN.findall(command))
        assert sep_count > mod.MAX_STATEMENT_COUNT, (
            f"precondition: separator count ({sep_count}) must exceed"
            f" MAX_STATEMENT_COUNT ({mod.MAX_STATEMENT_COUNT})"
        )
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow (tesseract bypass): {command!r}"

    def test_inline_script_still_blocked_on_tesseract_path(self) -> None:
        """Rule 1 (inline-script) MUST still fire even for tesseract paths."""
        command = "python3 -c 'import os; os.system(\"ls\")' >> ~/.tesseract/foo"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Inline-script rule must fire even for tesseract path"
        )
        reason = hook_out.get("permissionDecisionReason", "")
        assert "Inline non-Bash script detected" in reason

    def test_non_tesseract_dot_claude_path_char_limit_fires(self) -> None:
        """Long command to ~/.claude/NOT-tesseract/ is not exempt — rule 2 fires."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> ~/.claude/NOT-tesseract/file.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Char-limit must fire for non-tesseract path"
        )

    def test_tesseract_backup_path_char_limit_fires(self) -> None:
        """~/.tesseract-backup/ is not exempt — bypass scoped to tesseract/."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> ~/.tesseract-backup/file.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Char-limit must fire for tesseract-backup path"
        )

    def test_old_claude_tesseract_path_no_longer_bypassed(self) -> None:
        """Regression for the v1.12.1 path fix: the legacy `~/.claude/tesseract/`
        base is NO LONGER exempt — only the real runtime path `~/.tesseract/`
        bypasses rules 2 & 3. A long append to the legacy path must fire rule 2.
        """
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' >> ~/.claude/tesseract/bulk-beings.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Legacy ~/.claude/tesseract/ path must no longer bypass the char-limit"
        )

    def test_memory_path_char_limit_fires(self) -> None:
        """Long command targeting ~/.claude/projects/.../memory/ is NOT exempt."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = (
            f"echo '{long_content}' >> ~/.claude/projects/-Users-laura/memory/MEMORY.md"
        )
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Char-limit must fire for memory path"
        )

    def test_tesseract_in_comment_does_not_bypass_char_limit(self) -> None:
        """Regression guard for the redirect-target narrowing: an over-limit
        command with the tesseract path only in a trailing comment (not a `>>`
        target) must NOT bypass rule 2."""
        long_content = "x" * (MAX_COMMAND_LENGTH + 1)
        command = f"echo '{long_content}' # ~/.tesseract/bulk-beings.md"
        assert len(command) > MAX_COMMAND_LENGTH
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Tesseract path in a comment must NOT disarm the char-limit guard"
        )

    def test_tesseract_in_comment_does_not_bypass_statement_limit(self) -> None:
        """A chained command with the tesseract path only in a comment (not a
        `>>` target) must still trip rule 3."""
        chained = "; ".join(f"echo {i}" for i in range(MAX_STATEMENT_COUNT + 2))
        command = f"{chained} # ~/.tesseract/bulk-beings.md"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            "Tesseract path in a comment must NOT disarm the statement-limit guard"
        )


class TestHookIgnoresNonBash:
    """Non-Bash tools should pass through without inspection."""

    @pytest.mark.parametrize(
        "tool_name",
        [
            "Read",
            "Write",
            "Edit",
            "Grep",
            "Glob",
        ],
    )
    def test_ignores_non_bash_tools(self, tool_name: str) -> None:
        output = run_hook(tool_name, 'python3 -c "import os; os.listdir()"')
        assert output == {}


class TestHookMalformedInput:
    """Hook must not crash on unexpected input."""

    def test_empty_command(self) -> None:
        output = run_hook("Bash", "")
        assert output == {}

    def test_missing_tool_input(self) -> None:
        payload = json.dumps({"tool_name": "Bash"})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        # Should not crash — either {} or an error message
        assert isinstance(output, dict)

    def test_invalid_json(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="not json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Error path: exit 1 + stderr message, no persistent systemMessage on stdout
        assert result.returncode == 1
        assert "Hook error" in result.stderr
        assert result.stdout.strip() == ""

    # --- Fix B: non-string / non-dict inputs must coerce to empty, not error ---

    def test_null_command_is_allowed(self) -> None:
        """null command coerces to '' → no rules fire → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": None}})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"

    def test_non_string_command_is_allowed(self) -> None:
        """Integer command coerces to '' → no rules fire → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": 42}})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"

    def test_non_dict_tool_input_is_allowed(self) -> None:
        """Non-dict tool_input coerces to {} → command = '' → no rules → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": "oops"})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"

    def test_non_utf8_stdin_exits_cleanly(self) -> None:
        """Non-UTF-8 bytes on stdin must exit 1 with 'Hook error:' on stderr."""
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=b"\xff\xfe\x00not-json",
            capture_output=True,
            text=False,
            timeout=10,
        )
        assert result.returncode == 1, (
            f"Expected exit 1, got {result.returncode}; stderr={result.stderr!r}"
        )
        assert b"Hook error:" in result.stderr, (
            f"Expected 'Hook error:' in stderr, got {result.stderr!r}"
        )
