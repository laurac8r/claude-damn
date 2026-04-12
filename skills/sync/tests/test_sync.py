"""Tests for the /sync CLI entrypoint (skills.sync.scripts.sync)."""

import subprocess
from pathlib import Path

import pytest

from skills.sync.scripts import sync as sync_cli
from skills.sync.scripts.exceptions import InvalidModeError, RsyncFailedError

# ---------------------------------------------------------------------------
# 1. Missing target errors usefully
# ---------------------------------------------------------------------------


def test_missing_target_errors_usefully(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        sync_cli.main([])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "target" in captured.err.lower()


# ---------------------------------------------------------------------------
# 2. Positional and --to conflict
# ---------------------------------------------------------------------------


def test_positional_and_to_conflict_errors(tmp_path: Path) -> None:
    tgt = tmp_path / "tgt"
    tgt.mkdir()
    alt = tmp_path / "alt"
    alt.mkdir()
    with pytest.raises(SystemExit) as exc:
        sync_cli.main([str(tgt), "--to", str(alt)])
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# 3. Plan mode prints render and returns zero
# ---------------------------------------------------------------------------


def test_plan_mode_prints_render_and_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.txt").write_text("hi")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "plan"])
    assert result == 0
    captured = capsys.readouterr()
    assert "Sync plan (plan):" in captured.out
    # Nothing should be copied in plan mode
    assert not (tgt / "hello.txt").exists()


# ---------------------------------------------------------------------------
# 4. Push mode copies files
# ---------------------------------------------------------------------------


def test_push_mode_copies_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "push", "--yes"])
    assert result == 0
    assert (tgt / "a.txt").read_text() == "hello"


# ---------------------------------------------------------------------------
# 5. Missing source exits 1 (runtime, not argparse)
# ---------------------------------------------------------------------------


def test_missing_source_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main(
        [str(tgt), "--from", "/nonexistent/xyz/does/not/exist", "--mode", "plan"]
    )
    assert result == 1
    captured = capsys.readouterr()
    assert "source not found" in captured.err


# ---------------------------------------------------------------------------
# 6. Positional target works
# ---------------------------------------------------------------------------


def test_positional_target_works(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "push", "--yes"])
    assert result == 0
    assert (tgt / "a.txt").exists()


# ---------------------------------------------------------------------------
# 7. --to flag works
# ---------------------------------------------------------------------------


def test_to_flag_works(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main(
        ["--from", str(src), "--to", str(tgt), "--mode", "push", "--yes"]
    )
    assert result == 0
    assert (tgt / "a.txt").exists()


# ---------------------------------------------------------------------------
# 8. Default source is cwd
# ---------------------------------------------------------------------------


def test_default_source_is_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "x.txt").write_text("cwd-test")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    monkeypatch.chdir(src)
    result = sync_cli.main([str(tgt), "--mode", "plan"])
    assert result == 0
    captured = capsys.readouterr()
    assert str(src) in captured.out


# ---------------------------------------------------------------------------
# 9. --include and --exclude are repeatable
# ---------------------------------------------------------------------------


def test_include_exclude_are_repeatable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")
    (src / "c.txt").write_text("c")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    # Include only a.txt and b.txt
    result = sync_cli.main(
        [
            str(tgt),
            "--from",
            str(src),
            "--mode",
            "plan",
            "--include",
            "a.txt",
            "--include",
            "b.txt",
        ]
    )
    assert result == 0
    out = capsys.readouterr().out
    assert "a.txt" in out
    assert "b.txt" in out
    assert "c.txt" not in out

    # Exclude a.txt and b.txt — only c.txt should appear
    result2 = sync_cli.main(
        [
            str(tgt),
            "--from",
            str(src),
            "--mode",
            "plan",
            "--exclude",
            "a.txt",
            "--exclude",
            "b.txt",
        ]
    )
    assert result2 == 0
    out2 = capsys.readouterr().out
    assert "c.txt" in out2
    assert "a.txt" not in out2
    assert "b.txt" not in out2


# ---------------------------------------------------------------------------
# 10. --claude flag plumbs through (overrides gitignore for CLAUDE.md)
# ---------------------------------------------------------------------------


def test_claude_flag_plumbs_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    # Init git repo so gitignore is respected
    subprocess.run(
        ["git", "init", "-q", str(src)], check=True, capture_output=True, text=True
    )
    (src / ".gitignore").write_text("CLAUDE.md\n")
    (src / "CLAUDE.md").write_text("# claude context")
    (src / "regular.txt").write_text("regular")

    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "plan", "--claude"])
    assert result == 0
    out = capsys.readouterr().out
    assert "CLAUDE.md" in out


# ---------------------------------------------------------------------------
# 11. rsync failure exits 1 with stderr
# ---------------------------------------------------------------------------


def test_rsync_failure_exits_one_with_stderr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    def _raise_rsync(*args: object, **kwargs: object) -> None:
        raise RsyncFailedError("boom", stderr="rsync says nope")

    monkeypatch.setattr(sync_cli, "run_apply", _raise_rsync)

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "push", "--yes"])
    assert result == 1
    err = capsys.readouterr().err
    assert "boom" in err
    assert "rsync says nope" in err


# ---------------------------------------------------------------------------
# 12. --dry-run leaves target untouched
# ---------------------------------------------------------------------------


def test_dry_run_leaves_target_untouched(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    result = sync_cli.main(
        [str(tgt), "--from", str(src), "--mode", "push", "--dry-run", "--yes"]
    )
    assert result == 0
    assert not (tgt / "a.txt").exists()


# ---------------------------------------------------------------------------
# 13. Generic SyncError exits 1
# ---------------------------------------------------------------------------


def test_generic_sync_error_exits_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    tgt = tmp_path / "tgt"
    tgt.mkdir()

    def _raise_invalid(*args: object, **kwargs: object) -> None:
        raise InvalidModeError("bogus")

    monkeypatch.setattr(sync_cli, "build_plan", _raise_invalid)

    result = sync_cli.main([str(tgt), "--from", str(src), "--mode", "plan"])
    assert result == 1
    err = capsys.readouterr().err
    assert "/sync:" in err
    assert "bogus" in err
