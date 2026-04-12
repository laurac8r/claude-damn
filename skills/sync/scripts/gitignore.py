"""Thin wrapper around `git check-ignore` for filtering paths."""

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitignoreFilter:
    """Check whether paths are ignored by the source repo's .gitignore."""

    root: Path

    def _in_git_repo(self) -> bool:
        """Return True if *root* is inside a git working tree.

        Uses ``git rev-parse --git-dir`` so it works from any subdirectory
        of a repo, not just the root that owns a ``.git`` entry.
        """
        result = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def batch_ignored(self, relative_paths: Iterable[Path]) -> frozenset[Path]:
        """Return the subset of *relative_paths* that git considers ignored.

        Sends all paths to a single ``git check-ignore --stdin`` invocation
        to avoid per-path subprocess overhead on large trees.
        """
        if not self._in_git_repo():
            return frozenset()
        paths = list(relative_paths)
        if not paths:
            return frozenset()
        stdin_input = "\n".join(str(p) for p in paths)
        result = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", "--stdin"],
            input=stdin_input,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode not in (0, 1):
            # Unexpected error — treat nothing as ignored rather than crashing.
            return frozenset()
        ignored_strs = set(result.stdout.splitlines())
        return frozenset(p for p in paths if str(p) in ignored_strs)

    def is_ignored(self, relative_path: Path) -> bool:
        return relative_path in self.batch_ignored([relative_path])
