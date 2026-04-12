"""Thin wrapper around `git check-ignore` for filtering paths."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitignoreFilter:
    """Check whether paths are ignored by the source repo's .gitignore."""

    root: Path

    def is_ignored(self, relative_path: Path) -> bool:
        if not (self.root / ".git").exists():
            return False
        result = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", "-q", str(relative_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
