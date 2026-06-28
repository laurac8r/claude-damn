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
        """The shelf/ledger live under `~/.tesseract/` (directly under $HOME,
        not `~/.claude/`), spelled 'tesseract' (not 'tessaract'). The legacy
        `~/.claude/tesseract/` base must not reappear.
        """
        assert "tessaract" not in skill_md, (
            "Found misspelled 'tessaract' — should be 'tesseract'."
        )
        assert "~/.tesseract/shelf" in skill_md
        assert "~/.tesseract/bulk-beings.md" in skill_md
        assert "~/.claude/tesseract/" not in skill_md, (
            "Tesseract paths must be ~/.tesseract/, not ~/.claude/tesseract/."
        )

    def test_skill_md_references_shared_helpers(self, skill_md: str) -> None:
        """SKILL.md must point at skills/_shared/ as the canonical home for
        slugify, anchor, parse_shelf so future Python entrypoints reuse the
        shared modules instead of inlining copies (drift prevention).
        """
        assert "skills/_shared" in skill_md


class TestTesseractRetroFlag:
    """`--retro` flag: pure observation mode. The flag must turn the skill
    into a read-only invocation — no shelf prepend, no bulk-beings append,
    no book dropped. Spec'd in feat/tesseract-retro.

    RED state was proven against pre-feature SKILL.md (no `--retro` mention
    anywhere). Most assertions below therefore fail on `main` and pass on
    the GREEN skill update; one assertion is a guardrail rather than a
    strict RED-state check.
    """

    def test_retro_in_argument_hint(self, frontmatter: dict) -> None:
        """argument-hint must advertise `--retro` so slash-command tab
        completion surfaces it alongside `--signal`.
        """
        hint = frontmatter.get("argument-hint", "")
        assert "--retro" in hint, f"argument-hint must mention --retro; got: {hint!r}"

    def test_retro_documented_in_process(self, skill_md: str) -> None:
        """The Process section must explicitly document `--retro` parsing —
        otherwise step 1's argument-resolution prose is silently wrong about
        what flags exist.
        """
        process_match = re.search(
            r"^## Process\b.*?(?=^## \S|\Z)", skill_md, re.MULTILINE | re.DOTALL
        )
        assert process_match, "SKILL.md must contain a ## Process section."

        process_section = process_match.group(0)
        assert re.search(r"`--retro`", process_section), (
            "Process must reference the `--retro` flag in argument-parsing prose."
        )

    def test_retro_skips_step_2_mkdir(self, skill_md: str) -> None:
        """Step 2 (`Ensure the tesseract exists`) runs `mkdir -p` to create
        the shelf directory. In retro mode that is still a write — file-
        system state changes from "absent" to "present empty dir" — so the
        observation-only invariant is violated unless step 2 is explicitly
        retro-gated. Convergent finding from two independent offline
        reviewers (Conf 85/88), separate from the GitHub Copilot inline
        review.
        """
        step_2_match = re.search(
            r"^### 2 · .*?(?=^### \d+ · |\Z)",
            skill_md,
            re.MULTILINE | re.DOTALL,
        )
        assert step_2_match, "Step 2 (`### 2 · ...`) is missing from SKILL.md."
        step_2 = step_2_match.group(0)
        pattern = re.compile(
            r"retro\b[^\n]{0,200}\b(skip|do not|don't|no)\b",
            re.IGNORECASE,
        )
        assert pattern.search(step_2), (
            "Step 2 must explicitly retro-gate the mkdir (e.g., 'if "
            "retro=true, skip this step'). Without this, retro invocations "
            "create the shelf directory and violate the observation-only "
            "invariant."
        )

    def test_retro_skips_shelf_prepend(self, skill_md: str) -> None:
        """Step 6 (or its retro branch) must explicitly state that retro
        skips the shelf prepend. Without this, agents will follow the
        'every invocation drops a book' rule and write anyway.
        """
        # Look for a sentence that pairs "retro" with "shelf" + a skip verb.
        pattern = re.compile(
            r"retro\b[^\n]{0,200}\b(skip|do not|don't|no)\b[^\n]{0,80}\bshelf\b"
            r"|\bshelf\b[^\n]{0,200}\b(skip|do not|don't|no)\b[^\n]{0,80}\bretro\b",
            re.IGNORECASE,
        )
        assert pattern.search(skill_md), (
            "Spec must say retro skips shelf prepend (sentence pairing "
            "'retro' with 'skip/don't/no shelf')."
        )

    def test_retro_skips_bulk_beings_append(self, skill_md: str) -> None:
        """Same for bulk-beings — retro must NOT append a line."""
        pattern = re.compile(
            r"retro\b[^\n]{0,200}\b(skip|do not|don't|no)\b[^\n]{0,80}"
            r"bulk[- ]?beings"
            r"|bulk[- ]?beings[^\n]{0,200}\b(skip|do not|don't|no)\b"
            r"[^\n]{0,80}\bretro\b",
            re.IGNORECASE,
        )
        assert pattern.search(skill_md), (
            "Spec must say retro skips bulk-beings append (sentence pairing "
            "'retro' with 'skip/don't/no bulk-beings')."
        )

    def test_retro_signal_combination_warning_specced(self, skill_md: str) -> None:
        """`--retro` + `--signal "..."` is a contradiction. Spec must say
        what happens (warn-and-discard/ignore) — and the assertion must
        be scoped to the bullet that documents the combination, not a
        wider DOTALL window. A wide window false-positives by matching
        retro/signal/verb stems across unrelated paragraphs (mutation-
        proven against `/tmp/tesseract_mutation_test` M2 fixture).
        """
        marker = "**`--retro` + `--signal` combination.**"
        start = skill_md.find(marker)
        assert start >= 0, (
            f"Step 1 must contain the bullet '{marker}' that documents "
            "the --retro + --signal combination."
        )
        rest = skill_md[start + len(marker) :]
        end_match = re.search(r"\n- |\n\n", rest)
        body = rest[: end_match.start()] if end_match else rest
        assert re.search(r"\b(warn\w*|ignor\w*|discard\w*)\b", body, re.IGNORECASE), (
            "The --retro + --signal combination bullet must specify a "
            "behavioral verb (warn|ignor|discard stem) inside the bullet "
            "body — not just rely on nearby paragraphs."
        )

    def test_retro_footer_replaces_dropped_a_book(self, skill_md: str) -> None:
        """In retro mode the footer must REPLACE the `📉 Dropped a book`
        header — not coexist alongside it. The fenced output template
        following `**Retro mode (`retro=true`):**` must contain
        'Observed only' AND must NOT contain '📉 Dropped a book' as a
        standalone header. A document-wide 'Observed only' search passes
        vacuously if both headers appear (mutation-proven against
        `/tmp/tesseract_mutation_test` M1 fixture).
        """
        intro = "**Retro mode (`retro=true`):**"
        intro_idx = skill_md.find(intro)
        assert intro_idx >= 0, (
            f"Step 7 must contain the retro template intro '{intro}'."
        )
        after_intro = skill_md[intro_idx:]
        fence_match = re.search(r"```text\n(.*?)\n```", after_intro, re.DOTALL)
        assert fence_match, (
            "The retro template intro must be followed by a ```text fenced "
            "block containing the retro-mode output template."
        )
        fence_body = fence_match.group(1)
        assert "Observed only" in fence_body, (
            "Retro fenced template must contain an 'Observed only' footer."
        )
        assert "📉 Dropped a book" not in fence_body, (
            "Retro fenced template must NOT contain '📉 Dropped a book' — "
            "that header is being replaced, not coexisting."
        )

    def test_retro_header_marker(self, skill_md: str) -> None:
        """The `> Murph point.` header line must show a retro marker so the
        rendered output makes the read-only mode obvious from line one.
        """
        # Accept either a bracketed retro marker or an explicit "[retro" form.
        assert re.search(r"\[retro\b[^\]]*\]", skill_md), (
            "Header line must include a `[retro …]` marker for retro-mode rendering."
        )

    def test_rule_of_bulk_acknowledges_retro_exemption(self, skill_md: str) -> None:
        """The 'Every invocation drops a book' rule must be amended so it
        no longer reads as absolute. Otherwise the rule contradicts the
        retro flag and agents will rationalize their way back to writing.
        """
        # The pre-feature absolute phrasing should no longer be the standalone
        # bullet header.
        absolute_phrase = "**Every invocation drops a book.**"
        if absolute_phrase in skill_md:
            # If it's still there, it must be qualified within ~120 chars
            # by a retro carve-out.
            idx = skill_md.index(absolute_phrase)
            window = skill_md[idx : idx + 400]
            assert re.search(r"retro", window, re.IGNORECASE), (
                "If the absolute 'Every invocation drops a book' bullet is "
                "kept, it must carry an inline retro carve-out within the "
                "same bullet."
            )
        else:
            # Otherwise, the amended rule (e.g., 'Every non-retro invocation')
            # must appear somewhere in the rules block.
            assert re.search(
                r"non[- ]?retro|except.*retro|retro.*exempt|retro.*exception",
                skill_md,
                re.IGNORECASE,
            ), (
                "Rules-of-bulk must explicitly carve out retro from the "
                "'every invocation drops a book' invariant."
            )

    def test_retro_example_present(self, skill_md: str) -> None:
        """At least one Examples bullet must demonstrate `--retro`. Without
        a worked example, agents won't know the intended call shape.
        """
        # Find the Examples section and check for a --retro bullet inside it.
        ex_match = re.search(
            r"^## Examples\s*\n(.*?)(?=^## |\Z)",
            skill_md,
            re.MULTILINE | re.DOTALL,
        )
        assert ex_match, "Examples section is missing."
        examples_block = ex_match.group(1)
        assert "--retro" in examples_block, (
            "Examples section must include at least one `--retro` invocation."
        )

    def test_retro_does_not_alter_n_before_semantics(self, skill_md: str) -> None:
        """N_before counts shelf entries from BEFORE this invocation's
        write. Retro performs no write, so the count is just 'shelf entries'.
        The spec must not contradict this — i.e., must not say retro
        increments anything.
        """
        # Negative assertion: the words 'retro' and 'increment' must not
        # co-occur in a sentence claiming retro adds to anything.
        bad = re.compile(
            r"retro\b[^.\n]{0,200}\b(increment|adds? to|append.*shelf)\b",
            re.IGNORECASE,
        )
        assert not bad.search(skill_md), (
            "Spec must not say retro increments N_before or appends to shelf."
        )
