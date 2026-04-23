"""Walk a source tree and emit the set of relative paths that should be synced.

Filter composition (in order):
    1. Skip .git/ always
    2. If respect_gitignore: drop gitignored paths
    3. If claude_allowlist: re-allow matching paths (overrides step 2)
    4. Apply --include (if any): drop non-matching
    5. Apply --exclude: drop matching
"""

import fnmatch
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .claude_allowlist import ClaudeAllowlist
from .gitignore import GitignoreFilter


@dataclass(frozen=True)
class DiscoverOptions:
    respect_gitignore: bool = True
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)
    claude_allowlist: ClaudeAllowlist | None = None


def discover(root: Path, opts: DiscoverOptions) -> Iterator[Path]:
    """Yield relative paths under `root` that pass all filters."""
    gi = GitignoreFilter(root=root) if opts.respect_gitignore else None

    all_rels = [absolute.relative_to(root) for absolute in _walk_files(root)]

    # Batch gitignore check: one subprocess call for the whole tree.
    ignored: frozenset[Path] = (
        gi.batch_ignored(all_rels) if gi is not None else frozenset()
    )

    for rel in all_rels:
        if _first_part(rel) == ".git":
            continue
        if gi is not None and rel in ignored:
            if opts.claude_allowlist is None or not opts.claude_allowlist.matches(rel):
                continue
        if opts.include and not any(fnmatch.fnmatch(str(rel), g) for g in opts.include):
            continue
        if any(fnmatch.fnmatch(str(rel), g) for g in opts.exclude):
            continue
        yield rel


def _walk_files(root: Path) -> Iterator[Path]:
    for child in sorted(root.rglob("*")):
        if child.is_file() or child.is_symlink():
            yield child


def _first_part(p: Path) -> str:
    parts = p.parts
    return parts[0] if parts else ""
