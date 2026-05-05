"""Spec-gap regression: Hallway 1 must hard-skip when cwd is not a git repo.

Pre-fix, /tesseract Hallway 1 implicitly assumed a git repo at cwd. With no
repo, the cascade either errored noisily, leaked cwd via a synthesized
message, or fell through to the free-text `git log --grep` branch (which
also errored). The fix adds a `git rev-parse --is-inside-work-tree`
precondition with a fixed silent-skip line and explicit anti-pattern
callouts. These tests pin the prose against re-regression.
"""

from __future__ import annotations

import re


class TestHallway1NoRepoPrecondition:
    """Hallway 1 must declare and enforce its no-git-repo precondition."""

    def test_precondition_command_documented(self, skill_md: str) -> None:
        """The precondition probe must be the documented command — exact form
        matters because agents copy-paste it. `2>/dev/null` is required to
        suppress the stderr `fatal: not a git repository` diagnostic when
        outside a repo.
        """
        assert "git rev-parse --is-inside-work-tree 2>/dev/null" in skill_md, (
            "Hallway 1 must document the exact precondition probe "
            "`git rev-parse --is-inside-work-tree 2>/dev/null` so agents "
            "do not invent a noisier variant."
        )

    def test_silent_skip_line_is_fixed_string(self, skill_md: str) -> None:
        """The skip-output line must be the exact fixed string. A free-form
        message risks leaking cwd (e.g. `not in a git repo at /path/x`),
        which breaks the no-cwd-leak invariant the precondition exists to
        enforce.
        """
        assert "(not in a git repository — Hallway 1 silent)" in skill_md, (
            "Hallway 1 silent-skip output must be the exact fixed string "
            "`(not in a git repository — Hallway 1 silent)` — anything "
            "templated risks leaking cwd or other context."
        )

    def test_anti_patterns_called_out(self, skill_md: str) -> None:
        """The fix must explicitly close the two known wrong-paths:
        synthesizing a custom message (leaks cwd), or falling through to
        the free-text grep cascade (errors + noise). Both rationalizations
        were observed pre-fix.
        """
        assert re.search(
            r"do\s+\*\*not\*\*\s+synthesize a custom message",
            skill_md,
            re.IGNORECASE,
        ), (
            "Anti-pattern callout for cwd-leaking synthesized messages must "
            "be present in Hallway 1."
        )
        assert re.search(
            r"do\s+\*\*not\*\*\s+fall through to the free-text grep",
            skill_md,
            re.IGNORECASE,
        ), (
            "Anti-pattern callout for free-text-grep fallthrough must be "
            "present in Hallway 1."
        )

    def test_precondition_appears_before_cascade(self, skill_md: str) -> None:
        """Order matters — the precondition has to be read (and enforced)
        before the four-step cascade, otherwise agents resolve the cascade
        first and the precondition becomes dead text.
        """
        precondition_idx = skill_md.find(
            "git rev-parse --is-inside-work-tree 2>/dev/null"
        )
        cascade_idx = skill_md.find("1. `git ls-files --error-unmatch")
        assert precondition_idx != -1, "precondition probe missing"
        assert cascade_idx != -1, "Hallway 1 cascade step 1 missing"
        assert precondition_idx < cascade_idx, (
            "Precondition probe must appear textually before the cascade "
            "(step 1 onward) — otherwise it reads as a post-hoc footnote."
        )
