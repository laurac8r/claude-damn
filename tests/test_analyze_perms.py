"""Tests for analyze_perms.py — transcript-driven allowlist suggester."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analyze_perms import (
    ScanResult,
    Suggestion,
    classify_bash_key,
    extract_first_command,
    find_recent_transcripts,
    format_table,
    rank_suggestions,
    scan_transcripts,
)


def _tool_use(name: str, inp: dict) -> dict:
    return {
        "type": "assistant",
        "message": {
            "content": [
                {"type": "tool_use", "name": name, "input": inp},
            ],
        },
    }


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")


class TestExtractFirstCommand:
    def test_simple_single_token(self) -> None:
        assert extract_first_command("ls") == ("ls", "ls")

    def test_command_with_subcommand(self) -> None:
        assert extract_first_command("git status") == ("git", "git status")

    def test_strips_flags_from_second_token(self) -> None:
        assert extract_first_command("git log --oneline") == ("git", "git log")

    def test_drops_leading_env_vars(self) -> None:
        result = extract_first_command("FOO=bar BAZ=1 git status")
        assert result == ("git", "git status")

    def test_drops_sudo(self) -> None:
        assert extract_first_command("sudo systemctl status") == (
            "systemctl",
            "systemctl status",
        )

    def test_drops_nohup(self) -> None:
        result = extract_first_command("nohup python3 foo.py")
        assert result == ("python3", "python3 foo.py")

    def test_drops_timeout_numeric(self) -> None:
        assert extract_first_command("timeout 30 curl example.com") == (
            "curl",
            "curl example.com",
        )

    def test_drops_timeout_flag(self) -> None:
        assert extract_first_command("timeout -s KILL 30 sleep 5") == (
            "sleep",
            "sleep 5",
        )

    def test_pipe_takes_first_segment(self) -> None:
        assert extract_first_command("git log | head -20") == ("git", "git log")

    def test_and_takes_first_segment(self) -> None:
        assert extract_first_command("git fetch && git merge") == ("git", "git fetch")

    def test_semicolon_takes_first_segment(self) -> None:
        assert extract_first_command("pwd; ls") == ("pwd", "pwd")

    def test_or_takes_first_segment(self) -> None:
        assert extract_first_command("test -f foo || echo missing") == (
            "test",
            "test",  # "-f" is a flag, dropped — single token remains
        )

    def test_strips_leading_path(self) -> None:
        assert extract_first_command("/usr/bin/git status") == ("git", "git status")

    def test_empty_string_returns_none(self) -> None:
        assert extract_first_command("") is None

    def test_whitespace_only_returns_none(self) -> None:
        assert extract_first_command("   \t  ") is None

    def test_only_env_vars_returns_none(self) -> None:
        assert extract_first_command("FOO=bar BAZ=1") is None

    def test_drops_env_wrapper(self) -> None:
        assert extract_first_command("env git status") == ("git", "git status")

    def test_drops_env_wrapper_with_assignments(self) -> None:
        result = extract_first_command("env FOO=bar git status")
        assert result == ("git", "git status")

    def test_drops_env_wrapper_with_multiple_assignments(self) -> None:
        result = extract_first_command("env FOO=bar BAZ=1 git status")
        assert result == ("git", "git status")

    def test_drops_env_wrapper_with_i_flag(self) -> None:
        assert extract_first_command("env -i git status") == ("git", "git status")

    def test_drops_env_wrapper_with_u_flag_and_arg(self) -> None:
        result = extract_first_command("env -u PATH git status")
        assert result == ("git", "git status")

    def test_bare_env_returns_none(self) -> None:
        assert extract_first_command("env") is None

    def test_env_with_only_assignments_returns_none(self) -> None:
        assert extract_first_command("env FOO=bar") is None


class TestScanTranscripts:
    def test_counts_bash_calls(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        _write_jsonl(
            jsonl,
            [
                _tool_use("Bash", {"command": "git status"}),
                _tool_use("Bash", {"command": "git status -s"}),
                _tool_use("Bash", {"command": "ls"}),
            ],
        )
        result = scan_transcripts([jsonl])
        assert result.bash["git status"] == 2
        assert result.bash["ls"] == 1

    def test_counts_mcp_calls_verbatim(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        _write_jsonl(
            jsonl,
            [
                _tool_use("mcp__slack__slack_read_thread", {}),
                _tool_use("mcp__slack__slack_read_thread", {}),
                _tool_use("mcp__github__get_issue", {}),
            ],
        )
        result = scan_transcripts([jsonl])
        assert result.mcp["mcp__slack__slack_read_thread"] == 2
        assert result.mcp["mcp__github__get_issue"] == 1

    def test_ignores_non_assistant_events(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        _write_jsonl(
            jsonl,
            [
                {"type": "user", "message": {"content": "hi"}},
                {"type": "system", "message": {}},
                _tool_use("Bash", {"command": "pwd"}),
            ],
        )
        result = scan_transcripts([jsonl])
        assert result.bash["pwd"] == 1

    def test_ignores_non_tool_use_content(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        _write_jsonl(
            jsonl,
            [
                {
                    "type": "assistant",
                    "message": {
                        "content": [{"type": "text", "text": "hello"}],
                    },
                },
            ],
        )
        result = scan_transcripts([jsonl])
        assert result.bash == {}
        assert result.mcp == {}

    def test_skips_blank_lines_and_bad_json(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        jsonl.write_text(
            "\n".join(
                [
                    "",
                    "not-json",
                    json.dumps(_tool_use("Bash", {"command": "git log"})),
                    "",
                ]
            )
            + "\n"
        )
        result = scan_transcripts([jsonl])
        assert result.bash["git log"] == 1

    def test_skips_empty_bash_command(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "session.jsonl"
        _write_jsonl(
            jsonl,
            [
                _tool_use("Bash", {"command": ""}),
                _tool_use("Bash", {"command": "   "}),
            ],
        )
        result = scan_transcripts([jsonl])
        assert result.bash == {}

    def test_aggregates_across_multiple_files(self, tmp_path: Path) -> None:
        a = tmp_path / "a.jsonl"
        b = tmp_path / "b.jsonl"
        _write_jsonl(a, [_tool_use("Bash", {"command": "gh pr view 1"})])
        _write_jsonl(b, [_tool_use("Bash", {"command": "gh pr view 2"})])
        result = scan_transcripts([a, b])
        assert result.bash["gh pr"] == 2

    def test_tool_use_name_null_does_not_raise(self, tmp_path: Path) -> None:
        """A tool_use block with explicit null name must be skipped, not raise."""
        jsonl = tmp_path / "session.jsonl"
        # Write a raw line with name=null (JSON null, not absent key)
        event = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": None, "input": {}},
                ],
            },
        }
        jsonl.write_text(json.dumps(event) + "\n")
        # Must not raise AttributeError; result should be empty
        result = scan_transcripts([jsonl])
        assert result.bash == {}
        assert result.mcp == {}


class TestClassifyBashKey:
    """classify_bash_key returns a verdict tag for a `leading sub` pair.

    - ``auto`` — already auto-allowed by the harness, no rule needed
    - ``mutating`` — writes/deletes/publishes, not eligible
    - ``risky_wildcard`` — would need ``Bash(foo *)`` granting arbitrary exec
    - ``allowlist`` — safe read-only, emit a rule
    """

    @pytest.mark.parametrize(
        "key, expected",
        [
            ("ls", "auto"),
            ("cat", "auto"),
            ("pwd", "auto"),
            ("git status", "auto"),
            ("git log", "auto"),
            ("git diff", "auto"),
            ("gh pr", "auto"),
            ("docker ps", "auto"),
            ("rg", "auto"),
            ("git push", "mutating"),
            ("git commit", "mutating"),
            ("rm", "mutating"),
            ("npm install", "mutating"),
            ("gh pr merge", "mutating"),
            ("uv sync", "mutating"),
            ("python3", "risky_wildcard"),
            ("bash", "risky_wildcard"),
            ("npx", "risky_wildcard"),
            ("bun run", "risky_wildcard"),
            ("ssh", "risky_wildcard"),
            ("make", "risky_wildcard"),
            ("uvx", "risky_wildcard"),
            ("curl", "allowlist"),
            ("open", "allowlist"),
            ("somecustomtool", "allowlist"),
            # Bare pair-family leaves must not fall through to allowlist;
            # `Bash(git *)` would also grant `git push`, etc.
            ("git", "risky_wildcard"),
            ("gh", "risky_wildcard"),
            ("docker", "risky_wildcard"),
            ("npm", "risky_wildcard"),
            ("yarn", "risky_wildcard"),
            ("pnpm", "risky_wildcard"),
            ("bun", "risky_wildcard"),
            ("cargo", "risky_wildcard"),
            ("uv", "risky_wildcard"),
            # Unknown subcommands of pair families also inherit the risky
            # verdict — pair lookups still win for the known-good ones above.
            ("git somenewsubcommand", "risky_wildcard"),
            ("npm somenewsubcommand", "risky_wildcard"),
            # Shell control keywords — `for f in *; do ...` parses to
            # ("for", "for f") and must not emit a `Bash(for f *)` rule.
            ("for f", "risky_wildcard"),
            ("while true", "risky_wildcard"),
            ("if test", "risky_wildcard"),
            ("case $x", "risky_wildcard"),
            ("do something", "risky_wildcard"),
            ("then something", "risky_wildcard"),
            ("function foo", "risky_wildcard"),
        ],
    )
    def test_classify(self, key: str, expected: str) -> None:
        assert classify_bash_key(key) == expected


class TestRankSuggestions:
    def test_single_bash_entry_emits_prefix_pattern(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 5
        out = rank_suggestions(scan)
        assert out == [Suggestion(pattern="Bash(curl *)", count=5, note="curl")]

    def test_pair_key_keeps_space_before_wildcard(self) -> None:
        scan = ScanResult()
        scan.bash["mycli deploy"] = 7
        out = rank_suggestions(scan)
        assert out[0].pattern == "Bash(mycli deploy *)"

    def test_mcp_pattern_is_verbatim_no_wildcard(self) -> None:
        scan = ScanResult()
        scan.mcp["mcp__slack__read_thread"] = 4
        out = rank_suggestions(scan)
        assert out == [
            Suggestion(
                pattern="mcp__slack__read_thread",
                count=4,
                note="MCP tool",
            )
        ]

    def test_drops_auto_allowed_bash_keys(self) -> None:
        scan = ScanResult()
        scan.bash["git status"] = 50  # auto
        scan.bash["curl"] = 3
        out = rank_suggestions(scan)
        patterns = [s.pattern for s in out]
        assert "Bash(git status *)" not in patterns
        assert "Bash(curl *)" in patterns

    def test_drops_mutating_bash_keys(self) -> None:
        scan = ScanResult()
        scan.bash["git push"] = 20
        scan.bash["curl"] = 3
        out = rank_suggestions(scan)
        assert [s.pattern for s in out] == ["Bash(curl *)"]

    def test_drops_risky_wildcard_bash_keys(self) -> None:
        scan = ScanResult()
        scan.bash["python3"] = 15
        scan.bash["bun run"] = 10
        scan.bash["curl"] = 3
        out = rank_suggestions(scan)
        assert [s.pattern for s in out] == ["Bash(curl *)"]

    def test_drops_counts_below_threshold(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 2  # below default min of 3
        scan.bash["wget"] = 3
        out = rank_suggestions(scan)
        assert [s.pattern for s in out] == ["Bash(wget *)"]

    def test_sorts_by_count_desc(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 5
        scan.bash["wget"] = 10
        scan.bash["aria2c"] = 7
        out = rank_suggestions(scan)
        assert [s.count for s in out] == [10, 7, 5]

    def test_caps_at_top_n(self) -> None:
        scan = ScanResult()
        for i in range(25):
            scan.bash[f"tool{i:02d}"] = 100 - i
        out = rank_suggestions(scan, limit=20)
        assert len(out) == 20
        assert out[0].count == 100

    def test_default_limit_is_twenty(self) -> None:
        scan = ScanResult()
        for i in range(30):
            scan.bash[f"tool{i:02d}"] = 100 - i
        out = rank_suggestions(scan)
        assert len(out) == 20

    def test_merges_bash_and_mcp_in_same_ranking(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 5
        scan.mcp["mcp__foo__bar"] = 12
        out = rank_suggestions(scan)
        assert out[0].pattern == "mcp__foo__bar"
        assert out[1].pattern == "Bash(curl *)"

    def test_min_count_override(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 1
        out = rank_suggestions(scan, min_count=1)
        assert [s.pattern for s in out] == ["Bash(curl *)"]

    @pytest.mark.parametrize(
        "noisy_key",
        [
            "shasum ~/.claude/foo.md",  # starts with ~
            "shasum /usr/local/lib",  # starts with /
            "shasum ./relative/path",  # starts with .
            "shasum abc1234",  # 7-char hex hash
            "shasum abc1234def5678",  # 14-char hex
            "shasum notes.md",  # .md extension
            "shasum archive.tar",  # .tar extension
            "shasum file.py",  # .py extension
        ],
    )
    def test_drops_noisy_second_tokens(self, noisy_key: str) -> None:
        scan = ScanResult()
        scan.bash[noisy_key] = 5
        out = rank_suggestions(scan)
        assert out == [], f"expected {noisy_key!r} to be filtered out"

    def test_keeps_plain_second_tokens(self) -> None:
        scan = ScanResult()
        scan.bash["shasum filename"] = 5  # no path/hash/ext markers
        out = rank_suggestions(scan)
        assert out == [
            Suggestion(
                pattern="Bash(shasum filename *)",
                count=5,
                note="shasum filename",
            )
        ]

    def test_noisy_filter_does_not_affect_single_token_bash(self) -> None:
        scan = ScanResult()
        scan.bash["curl"] = 4  # single token, no second; must survive
        out = rank_suggestions(scan)
        assert [s.pattern for s in out] == ["Bash(curl *)"]

    def test_noisy_filter_does_not_affect_mcp(self) -> None:
        scan = ScanResult()
        scan.mcp["mcp__foo__read_file"] = 5  # MCP never has a second token
        out = rank_suggestions(scan)
        assert [s.pattern for s in out] == ["mcp__foo__read_file"]


class TestFindRecentTranscripts:
    def test_returns_jsonl_files_sorted_by_mtime_desc(self, tmp_path: Path) -> None:
        import os

        older = tmp_path / "a.jsonl"
        newer = tmp_path / "b.jsonl"
        older.write_text("{}\n")
        newer.write_text("{}\n")
        os.utime(older, (1_700_000_000, 1_700_000_000))
        os.utime(newer, (1_800_000_000, 1_800_000_000))

        out = find_recent_transcripts(tmp_path, limit=10)
        assert out == [newer, older]

    def test_caps_at_limit(self, tmp_path: Path) -> None:
        for i in range(5):
            (tmp_path / f"s{i}.jsonl").write_text("{}\n")
        out = find_recent_transcripts(tmp_path, limit=3)
        assert len(out) == 3

    def test_skips_pytest_temp_dirs(self, tmp_path: Path) -> None:
        good = tmp_path / "real.jsonl"
        good.write_text("{}\n")
        noisy = tmp_path / "-private-pytest-of-laura-popen-gw0"
        noisy.mkdir()
        (noisy / "ignore.jsonl").write_text("{}\n")

        out = find_recent_transcripts(tmp_path, limit=10)
        assert out == [good]

    def test_recurses_into_project_subdirs(self, tmp_path: Path) -> None:
        proj = tmp_path / "-Users-laura-myproject"
        proj.mkdir()
        f = proj / "session.jsonl"
        f.write_text("{}\n")
        out = find_recent_transcripts(tmp_path, limit=10)
        assert out == [f]

    def test_ignores_non_jsonl_files(self, tmp_path: Path) -> None:
        (tmp_path / "keep.jsonl").write_text("{}\n")
        (tmp_path / "skip.txt").write_text("noise")
        out = find_recent_transcripts(tmp_path, limit=10)
        assert len(out) == 1
        assert out[0].name == "keep.jsonl"


class TestFormatTable:
    def test_empty_list_yields_header_only(self) -> None:
        table = format_table([])
        assert "No suggestions" in table

    def test_renders_rank_pattern_count_note(self) -> None:
        suggestions = [
            Suggestion("Bash(curl *)", 10, "curl"),
            Suggestion("mcp__foo__bar", 4, "MCP tool"),
        ]
        table = format_table(suggestions)
        lines = table.splitlines()
        assert lines[0].startswith("|")  # markdown header
        assert "Bash(curl *)" in table
        assert "10" in table
        assert "mcp__foo__bar" in table
        assert "MCP tool" in table

    def test_rank_numbers_start_at_one(self) -> None:
        suggestions = [
            Suggestion("Bash(a *)", 9, "a"),
            Suggestion("Bash(b *)", 7, "b"),
        ]
        table = format_table(suggestions)
        assert "| 1 |" in table
        assert "| 2 |" in table
