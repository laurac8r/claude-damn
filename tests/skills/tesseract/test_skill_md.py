"""Structural and regression tests for skills/tesseract/SKILL.md.

`TestTesseractRegressions` guards against re-introducing the four bugs fixed
in PR #21 (Copilot inline comments + expert-review findings). Each test's
RED state was proven against pre-fix HEAD content via direct grep checks
at write-time; assertions here verify the post-fix state.

`TestTesseractStructure` guards against accidental section deletions or
spec drift (frontmatter fields, hallway count, slug-name/dir alignment).
"""

from __future__ import annotations

import re
from pathlib import Path


class TestTesseractRegressions:
    """Regressions for the four PR #21 fixes."""

    def test_1_slug_rule_prose_does_not_say_strips_uppercase(
        self, skill_md: str
    ) -> None:
        """Fix 1 (Copilot #4): slug-rule prose must accurately describe the
        algorithm. Pre-fix sentence claimed uppercase letters were stripped,
        but they're case-normalized.
        """
        assert "strips every dot, slash, and uppercase letter" not in skill_md
        assert "lowercases letters" in skill_md

    def test_2_free_text_grep_uses_fixed_strings(self, skill_md: str) -> None:
        """Fix 2 (Copilot #5): the free-text Hallway 1 must use -F (or
        --fixed-strings) so anchors with regex metacharacters don't error
        or misfire.
        """
        free_text_line_pattern = re.compile(
            r"git log --max-count=5\s+-i\s+(-F|--fixed-strings)\s+--grep="
        )
        assert free_text_line_pattern.search(skill_md), (
            "Hallway 1 free-text branch must pass -F/--fixed-strings to git log "
            "so regex metachars in <anchor> are treated as literals."
        )

    def test_3_porcelain_cascade_handles_renames(self, skill_md: str) -> None:
        """Fix 3 (Expert #4): the `git status --porcelain` step must explain
        how to handle rename/copy entries (R/C status), where the post-strip
        path is `old -> new` rather than a plain path.
        """
        # The fix mentions both the status codes and the ` -> ` separator.
        assert re.search(r"`R`.*`C`|`R` or `C`", skill_md), (
            "Step 1 must mention rename (R) and copy (C) status codes."
        )
        assert " -> " in skill_md, (
            "Step 1 must reference the ` -> ` separator used by porcelain."
        )

    def test_4a_bulk_beings_append_uses_printf_not_echo(self, skill_md: str) -> None:
        """Fix 4 (Copilot #1): bulk-beings append uses printf '%s' (which
        does not expand $/`/\\) instead of echo (which does).
        """
        # No raw `echo "<...>" >> ...bulk-beings...` line should remain.
        assert not re.search(
            r'^echo\s+"[^"]*"\s*>>.*bulk-beings\.md', skill_md, re.MULTILINE
        ), "Pre-fix `echo` form for bulk-beings append must be replaced with printf."
        # printf with %s format and bulk-beings target must be present.
        assert re.search(r"printf\s+'%s.*?'\s+.*bulk-beings\.md", skill_md), (
            "bulk-beings append must use printf '%s' for shell-safe interpolation."
        )

    def test_4b_sanitize_rule_narrowed_to_newlines(self, skill_md: str) -> None:
        """Fix 4 cascade: with printf, the only metacharacter still dangerous
        is the literal newline (would smuggle a second log line). The pre-fix
        rule also stripped `"`, `$`, `` ` ``, `\\` — those are no longer
        needed.
        """
        # The replacement bullet should reference newline/CR explicitly.
        assert re.search(r"\\n.*\\r|newline.*CR|newlines? in.*<anchor>", skill_md), (
            "Sanitize rule must still cover newline/CR (they would smuggle log lines)."
        )
        # The pre-fix bullet name 'Sanitize before echo' must be gone.
        assert "Sanitize before echo" not in skill_md, (
            "'Sanitize before echo' is the pre-fix bullet name — should be "
            "renamed (e.g., 'Strip newlines before append')."
        )


class TestTesseractStructure:
    """Structural invariants — would catch accidental section deletions."""

    def test_frontmatter_has_required_fields(self, frontmatter: dict) -> None:
        """Frontmatter must declare name, description, user-invocable, and
        argument-hint — the four fields the skill loader and slash-command
        renderer rely on.
        """
        assert frontmatter.get("name") == "tesseract"
        assert isinstance(frontmatter.get("description"), str)
        assert len(frontmatter["description"]) > 0
        assert frontmatter.get("user-invocable") is True
        assert "argument-hint" in frontmatter

    def test_skill_dir_name_matches_frontmatter_name(
        self, skill_root: Path, frontmatter: dict
    ) -> None:
        """Skill directory name must match the frontmatter `name:` field —
        otherwise the slash-command name and the on-disk path diverge,
        which Copilot already flagged once on this PR.
        """
        assert skill_root.name == frontmatter["name"], (
            f"Directory '{skill_root.name}' does not match frontmatter "
            f"name '{frontmatter['name']}'."
        )

    def test_all_seven_process_steps_present(self, skill_md: str) -> None:
        """The /tesseract process is defined as 7 numbered steps. Missing
        any of them is a major spec break.
        """
        for step in range(1, 8):
            pattern = rf"^### {step} · "
            assert re.search(pattern, skill_md, re.MULTILINE), (
                f"Process step {step} (### {step} · ...) is missing."
            )

    def test_all_four_hallways_present(self, skill_md: str) -> None:
        """The 'four hallways' is the central metaphor — losing one means
        a hallway of evidence is silently dropped.
        """
        for n in range(1, 5):
            pattern = rf"\*\*Hallway {n} —"
            assert re.search(pattern, skill_md), (
                f"Hallway {n} section header is missing."
            )

    def test_final_output_template_uses_n_prior_visits_phrasing(
        self, skill_md: str
    ) -> None:
        """The final-output template uses `<N> prior visits` where `<N>` is
        N_before. Copilot already caught a phrasing inconsistency here once
        — guard it.
        """
        assert "<N> prior visits on the shelf" in skill_md, (
            "Final output template should keep the '<N> prior visits' phrasing "
            "(N is N_before, not N_before+1)."
        )

    def test_paths_use_consistent_tesseract_spelling(self, skill_md: str) -> None:
        """All `~/.claude/...` paths must use the 'tesseract' spelling
        (not 'tessaract'). Earlier PR commits already corrected this.
        """
        assert "~/.claude/tessaract" not in skill_md, (
            "Found pre-fix '~/.claude/tessaract' (misspelled) — should be "
            "'~/.claude/tesseract'."
        )
        assert "~/.claude/tesseract/shelf" in skill_md
        assert "~/.claude/tesseract/bulk-beings.md" in skill_md
