"""Exception hierarchy for the /sync skill."""


class SyncError(Exception):
    """Base class for all /sync errors."""


class SourceNotFoundError(SyncError):
    """Raised when the source path is missing or unreadable."""


class TargetNotWritableError(SyncError):
    """Raised when the target path is missing or not writable."""


class InvalidModeError(SyncError):
    """Raised when --mode is not one of the supported values."""


class RsyncFailedError(SyncError):
    """Raised when rsync exits non-zero. Wraps stderr."""

    def __init__(self, message: str, stderr: str) -> None:
        super().__init__(message)
        self.stderr = stderr
