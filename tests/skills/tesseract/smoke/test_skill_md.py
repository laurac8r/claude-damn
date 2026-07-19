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
        assert re.search(r"lowercases\s+letters", skill_md), (
            "Slug-rule prose must describe case-normalization via "
            "'lowercases letters' (reflow-tolerant)."
        )

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
        """All `~/.tesseract/...` paths must use the 'tesseract' spelling
        (not 'tessaract'). Earlier PR commits already corrected this.
        """
        assert "tessaract" not in skill_md, (
            "Found pre-fix 'tessaract' (misspelled) — should be 'tesseract'."
        )
        assert "~/.tesseract/shelf" in skill_md
        assert "~/.tesseract/bulk-beings.md" in skill_md


class TestTesseractMultiAnchor:
    """Multi-anchor + plural-flag support — extends step 1 to accept
    `/tesseract --anchors {a,b,c} --signals "<morse>"` and loop the
    book-drop logic per anchor while preserving singular behavior.

    RED-state evidence at write-time: pre-fix SKILL.md §1 only mentions
    `--anchor` (singular) and parses by splitting on " --signal "; literal
    parse of plural-flag invocations produces a single ~100-char garbage
    slug. Each assertion below was confirmed to fail against the pre-fix
    file via direct grep before the SKILL.md edit landed.
    """

    def test_anchors_plural_brace_expansion_documented(self, skill_md: str) -> None:
        """Step 1 must document `--anchors {a,b,c}` brace-expansion form
        as the N-anchor invocation syntax.
        """
        pattern = re.compile(r"--anchors\s+\{[^}]+\}")
        assert pattern.search(skill_md), (
            "Step 1 must document `--anchors {a,b,c}` brace-expansion as the "
            "N-anchor invocation form."
        )

    def test_signals_plural_synonym_documented(self, skill_md: str) -> None:
        """`--signals` (plural) must be documented as a synonym of
        `--signal` (singular). One signal applies to all anchors in the
        multi-anchor case — plural here is purely flag-symmetry, not
        N-signals semantics.
        """
        assert "--signals" in skill_md, "Step 1 must mention `--signals` flag."
        synonym_pattern = re.compile(
            r"--signals.{0,80}(synonym|alias|same as|equivalent)",
            re.IGNORECASE | re.DOTALL,
        )
        assert synonym_pattern.search(skill_md), (
            "Step 1 must explicitly mark `--signals` as a synonym/alias of "
            "`--signal` (one signal applies to all anchors)."
        )

    def test_per_anchor_loop_directive_present(self, skill_md: str) -> None:
        """When N anchors are given, steps 3–7 must execute per anchor —
        one shelf entry and one bulk-beings line each.
        """
        loop_pattern = re.compile(
            r"(loop|repeat|per\s+anchor|each\s+anchor).{0,200}"
            r"(steps?\s+3[-–]7|step\s+[3-7]|book[- ]drop)",
            re.IGNORECASE | re.DOTALL,
        )
        assert loop_pattern.search(skill_md), (
            "SKILL.md must direct that the book-drop logic (steps 3–7) loops "
            "per anchor when `--anchors {a,b,...}` is used."
        )

    def test_anchor_processing_order_left_to_right(self, skill_md: str) -> None:
        """Anchors inside the brace must be processed left-to-right so
        output order matches argument order.
        """
        order_pattern = re.compile(
            r"left[-\s]to[-\s]right|order\s+given|argument\s+order|"
            r"in\s+order",
            re.IGNORECASE,
        )
        assert order_pattern.search(skill_md), (
            "SKILL.md must specify anchor processing order (left-to-right / "
            "argument order) so multi-anchor output is deterministic."
        )

    def test_multi_anchor_output_separator_documented(self, skill_md: str) -> None:
        """Multi-anchor invocations must concatenate per-anchor reports
        separated by `---` (horizontal rule) so the operator can visually
        scan the boundary between reports.
        """
        separator_pattern = re.compile(
            r"(separat|divid|between).{0,100}`?---`?|"
            r"`---`.{0,100}(separat|between|divid)",
            re.IGNORECASE | re.DOTALL,
        )
        assert separator_pattern.search(skill_md), (
            "SKILL.md must document that multi-anchor reports are separated "
            "by `---` (horizontal rule) in the rendered output."
        )

    def test_singular_anchor_behavior_preserved(self, skill_md: str) -> None:
        """The `--anchor` (singular) form and the bare-anchor form must
        remain documented and work bit-for-bit as before. Multi-anchor
        is additive, not replacement.
        """
        assert "--anchor " in skill_md, (
            "Singular `--anchor ` form must remain documented in step 1."
        )
        assert re.search(r"--signal\b", skill_md), (
            "Singular `--signal` flag must remain documented."
        )
        assert re.search(r"em\s+dash|—\s*\(em", skill_md, re.IGNORECASE), (
            "Default-signal em-dash rule must remain in step 1."
        )

    def test_empty_brace_falls_back_to_cascade(self, skill_md: str) -> None:
        """`--anchors {}` (empty brace) is degenerate and must fall back
        to the existing anchor-resolution cascade rather than erroring.
        """
        empty_pattern = re.compile(
            r"`?\{\}`?.{0,150}(cascade|fall\s*back|empty)",
            re.IGNORECASE | re.DOTALL,
        )
        assert empty_pattern.search(skill_md), (
            "SKILL.md must specify behavior for empty `--anchors {}` — "
            "fall back to the anchor-resolution cascade."
        )

    def test_singleton_brace_treated_as_one_anchor(self, skill_md: str) -> None:
        """`--anchors {solo}` (single-element brace) must behave as a
        normal one-anchor invocation — no error, no extra ceremony.
        """
        singleton_pattern = re.compile(
            r"\{[a-z]+\}.{0,150}(single|one\s+anchor|same\s+as|"
            r"behaves?\s+(as|like))",
            re.IGNORECASE | re.DOTALL,
        )
        assert singleton_pattern.search(skill_md), (
            "SKILL.md must specify that single-element brace "
            "`--anchors {solo}` behaves as one-anchor invocation."
        )

    def test_examples_section_includes_multi_anchor(self, skill_md: str) -> None:
        """The Examples section must include at least one multi-anchor
        invocation so the form is discoverable from a quick scan.
        """
        examples_match = re.search(
            r"##\s+Examples\s*\n(.*?)(?=\n##\s|\Z)",
            skill_md,
            re.DOTALL,
        )
        assert examples_match, "Examples section must exist."
        examples_body = examples_match.group(1)
        assert re.search(r"--anchors\s+\{[^}]+\}", examples_body), (
            "Examples section must include at least one `--anchors {a,b}` "
            "multi-anchor invocation."
        )
