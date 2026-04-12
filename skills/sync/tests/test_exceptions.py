from skills.sync.scripts.exceptions import (
    InvalidModeError,
    RsyncFailedError,
    SourceNotFoundError,
    SyncError,
    TargetNotWritableError,
)


def test_all_subclass_sync_error() -> None:
    for cls in (
        SourceNotFoundError,
        TargetNotWritableError,
        InvalidModeError,
        RsyncFailedError,
    ):
        assert issubclass(cls, SyncError)


def test_rsync_failed_error_carries_stderr() -> None:
    err = RsyncFailedError("rsync died", stderr="permission denied")
    assert err.stderr == "permission denied"
    assert "rsync died" in str(err)
