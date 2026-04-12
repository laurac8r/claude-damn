from pathlib import Path

from pytest_mock import MockerFixture

from skills.sync.scripts.prompt import PromptOptions, approve_ops
from skills.sync.scripts.types import FileOp


def _op(path: str) -> FileOp:
    return FileOp(Path(path), "add", "src→tgt", "only in source")


def test_yes_flag_auto_approves(mocker: MockerFixture) -> None:
    mocker.patch("builtins.input", side_effect=AssertionError("should not prompt"))
    ops = (_op("dirA/a.txt"), _op("dirB/b.txt"))
    result = approve_ops(ops, PromptOptions(yes=True))
    assert result == ops


def test_limit_caps_approved_ops(mocker: MockerFixture) -> None:
    ops = (_op("dirA/a.txt"), _op("dirA/b.txt"), _op("dirA/c.txt"))
    result = approve_ops(ops, PromptOptions(yes=True, limit=2))
    assert len(result) == 2


def test_y_approves_directory_only(mocker: MockerFixture) -> None:
    mocker.patch("builtins.input", side_effect=["y", "n"])
    ops = (_op("dirA/a.txt"), _op("dirB/b.txt"))
    result = approve_ops(ops, PromptOptions())
    assert result == (_op("dirA/a.txt"),)


def test_a_approves_remaining_without_prompts(mocker: MockerFixture) -> None:
    inputs = iter(["a"])
    mocker.patch("builtins.input", lambda *_: next(inputs))
    ops = (_op("dirA/a.txt"), _op("dirB/b.txt"), _op("dirC/c.txt"))
    result = approve_ops(ops, PromptOptions())
    assert result == ops


def test_n_skips_directory(mocker: MockerFixture) -> None:
    mocker.patch("builtins.input", side_effect=["n", "y"])
    ops = (_op("dirA/a.txt"), _op("dirB/b.txt"))
    result = approve_ops(ops, PromptOptions())
    assert result == (_op("dirB/b.txt"),)
