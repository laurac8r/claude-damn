# Changelog

All notable changes to `claude-damn` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Pre-SemVer entries
(`[1.0.0]` and earlier) are grouped by development phase; from 1.7.0 onward,
entries follow standard SemVer (MAJOR / MINOR / PATCH) per the PERSONALIZATION
versioning rule.

## [2.0.1] — 2026-07-22

PATCH: hotfix closing a task-tool blind spot. An experiment flag
(`tengu_vellum_ash`) removes `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` from
the tool surface in interactive sessions on Opus 4.8, Sonnet 5, and Fable 5 —
the tools go missing rather than erroring, leaving `task-list`, `atlas`, and
`check-yourself` with no documented recovery. All three now degrade to a
Markdown table instead of silently dropping task tracking.

### Fixed (v2.0.1)

- `skills/atlas/SKILL.md` — step 5 degrades to a fixed-shape Markdown table
  fallback when the Task tool family is absent, with the never-abort guarantee
  in `## Invariants` extended to explicitly cover the missing-tool case.
- `skills/task-list/SKILL.md` — added the same Markdown-table fallback (fixed
  `#` / `Status` / `Task` columns), and qualified the anti-pattern that banned
  prose checklists so it fires only when the Task tools are actually present
  on the tool surface — the ban was correct in its original context, but as
  written it forbade the one tracking mechanism still available once the
  tools are gated off.
- `skills/check-yourself/SKILL.md` — Step 1 now names the absent Task tools
  and points at the Markdown fallback already in use elsewhere in the
  session; the boundary-check rationalization row was extended so a row
  flipping to `completed` in the fallback table counts as the same boundary a
  `TaskUpdate` status flip would.

### Changed (v2.0.1)

- `.claude-plugin/plugin.json` / `pyproject.toml` — 2.0.0 → 2.0.1.

## [2.0.0] — 2026-07-18

MAJOR (operator-designated milestone): completes the tdd+cat family arc —
`/tdd` micro-cycle (PR #83) → `/cat` SDD+parallel combination (PR #89) → this
release: the A/B TDD execution-mode axis across all nine `*-tdd-cat`
compositions.

### Added (v2.0.0)

- `skills/tdd-cat/SKILL.md` — rewritten as the canonical home of the TDD
  execution-mode axis: **Mode A** (split-phase: one RED/GREEN/REFACTOR phase
  per subagent) vs **Mode B** (micro-cycle: full `/tdd` loop inside each
  subagent), asked as a **third question** in `/cat`'s ONE combined
  pre-dispatch `AskUserQuestion`; standalone bare invocations of `/tdd` +
  `/cat`; orthogonality note (within a behavior, RED precedes GREEN — phases
  of the same behavior never parallelize); and a "No Shortcut — Never Default
  the TDD Mode Silently" guard with rationalization-counter table.
- Axis reference blocks in the other eight compositions: `duper-tdd-cat`,
  `super-tdd-cat`, `super-duper-tdd-cat`, `super-duper-fixer-tdd-cat`,
  `expert-tdd-cat-review`, `expert-duper-tdd-cat-review`,
  `expert-super-tdd-cat-review`, `expert-super-duper-tdd-cat-review`.
- `tests/skills/tdd_cat/` — 74 structural tests (RED→GREEN: 43 observed
  failing pre-edit; axis + guard + mode↔semantics swap-guards + 8×7 family
  references incl. column-0 heading pins + `/cat`-untouched pin).

### Notes (v2.0.0)

- `/cat` deliberately untouched — it serves non-TDD compositions; the axis
  rides its combined question from the tdd side only.
- Proportionate eval per the `/cat` precedent: a RED pressure probe of the
  as-written skills silently self-assigned the phase↔subagent mapping under
  dispatch-overhead pressure ("I decided it myself"); the GREEN re-probe
  against the rewrite surfaced all three axes in one combined call and quoted
  the guard as what stopped the skip.

## [1.13.0] — 2026-07-06

MINOR: manual canonical → active-dev sync (136 files vs `main`). Ships the
canonical install's hook, settings, rules, and skill-prose evolution into the
repo, and repairs everything the sync run itself broke (default suite went from
126 failures/errors back to 839 green).

### Added (v1.13.0)

- `hooks/block_opus_subagent.py` — PreToolUse Task guard denying Opus-model
  subagent dispatches (`CLAUDE_BATCH_MODE` env / `[BATCH_OVERRIDE]` sentinel
  escapes), with wire test `tests/hooks/test_block_opus_subagent.sh`.
- `hooks/check_git_rev_parse.py` — warn-mode PreToolUse Bash guard flagging
  unsafe `git rev-parse` patterns (unquoted `$VAR`, `--parseopt` + `eval`), with
  pytest suite and companion doc `rules/git_rev_parse_safety.md`.
- `hooks/ensure_remember_logs_dir.py` — SessionStart hook pre-creating
  `.remember/` log dirs so the remember plugin survives fresh worktrees.
- `sync-claude-settings.sh` — one-way canonical `settings.json` →
  `settings.local.json` sync with dry-run/diff preview, y/N confirm, and
  trash-based (never `rm`) backup.
- `scripts/parse_lighthouse.py` (Lighthouse a11y score extraction) and
  `scripts/strip_html.py` (HTML → plain text for legal-doc clause diffing).
- Root `statusline-command.sh` (canonical status-line variant, alongside the
  existing `src/statusline-command.sh`).
- Test suites: `tests/extra_cost/` (22 tests for `src/extract_cost.py`),
  `skills/tesseract/tests/test_render_visual.py` (19 tests + synthetic
  fixtures), tesseract smoke `test_skill_md.py` (20 tests, incl.
  `--anchors {a,b,c}` multi-anchor specs), hook test suites, and per-skill
  test-layout scaffolding (`helpers/`, `performance/`, `pressure/`).

### Changed (v1.13.0)

- Tracked settings migrated `settings.json` → `settings.local.json` with a
  permissions overhaul: broader `git commit` deny (`Bash(*git commit*)`), new
  `rm` deny triple enforcing the trash-only rule, `gh issue` mutations deny →
  ask, blanket `gh api` ask replaced by granular read-only allows,
  filesystem-wide Read allows, tesseract/chrome-devtools/flutter allows, and the
  three new hooks registered.
- Inline-script caps raised in `hooks/constants.py`: `MAX_COMMAND_LENGTH` 400 →
  500, `MAX_STATEMENT_COUNT` 4 → 10.
- `CLAUDE.md` restructured around the `[nudge]` < `[policy]` < `[hard]` severity
  ladder with a paste-verbatim Subagent Preamble;
  `rules/PERSONALIZATION.example.md` rewritten (~63 → ~291 lines).
- `argument-hint` frontmatter added to 35 SKILL.md files; `/check-yourself`
  boundary triggers enumerated with gated Steps 5/6; `/expert-review` gains
  mandatory re-trace of ≥90-confidence findings and artifact-shaped custom
  output; `/super-duper-tdd-cat` gains a subagent-dispatch discipline section (+
  evals); fixer family gains an explore-only operator override; `/listen` gains
  satisfaction semantics; `/tesseract` accepts `--signal {…}`; `/visual-aid`
  default save path moved `/tmp` → `~/.visual-aid/`.

### Fixed (v1.13.0)

- `skills/sync/scripts/apply.py` restored after the sync run clobbered it with
  `diff.py`'s content (net diff vs `main` now zero for `skills/sync/scripts/`).
- `tests/conftest.py` repointed at `settings.local.json`; permission regression
  tests realigned to the canonical-synced semantics.
- Stale duplicate `tests/hooks/test_hook_inline_scripts.py` removed (53
  path-broken tests superseded by the limit-agnostic flat suite);
  separator-limit tests made relative to `MAX_STATEMENT_COUNT` (the old
  5-element slice silently under-generated at the new limit).
- `/cat` bare skill-invocation lines made prettier-proof via `prettier-ignore`,
  restoring the tested invocation-literalness invariant.

## [1.12.2] — 2026-06-29

PATCH: `/cat` reworked from "ask for auto-accept, then the agent self-selects
the dispatch shape" into the **explicit combination** of both superpowers skills
it composes — `/subagent-driven-development` (sequential, review-gated) and
`/dispatching-parallel-agents` (independent fan-out) — fronted by **one combined
pre-dispatch `AskUserQuestion`** over two orthogonal axes: execution mode (3
presets — Full parallel / Hybrid / Strict sequential) and edit approval
(Auto-accept vs Manual-approve). The "No Shortcut for Trivial Edits" guard is
preserved and extended with an explicit manual-approve closure (foreground /
manual-approve changes who _approves_ an edit, not who _makes_ it). Built in a
worktree off `main`.

Note: `/lets-make-a-skill`'s baseline-first pressure grid did **not** bind — a
RED baseline (4 agents under manual-approve pressure against the current `/cat`)
produced 0 shortcuts: the existing rationalization-counter table already
generalized to the new framing, so the Iron Law (ship only after a baseline
rationalizes) is satisfied without a new behavioral guard, exactly as for
`/expert-final-review` (1.12.0). A structural test suite was added in its place;
the manual-approve closure ships as explicitness (removing a derivation step),
not as a proven-necessary guard. Also corrected an outdated assumption while
drafting: backgrounded subagents **do** surface permission prompts (Claude Code
v2.1.186+), so the edit-approval axis turns on auto-accepted-vs-approve-each,
not background-vs-foreground.

### Added (v1.12.2)

- `tests/skills/cat/` — structural test suite (`conftest.py`,
  `test_skill_md.py`, `__init__.py`): 16 assertions covering frontmatter, both
  composed-skill bare invocations, the combined pre-dispatch question (3
  presets + 2 approval modes), and the No-Shortcut manual-approve closure +
  ordering.

### Changed (v1.12.2)

- `skills/cat/SKILL.md` — combined pre-dispatch `AskUserQuestion`; explicit
  dual-skill composition with bare invocations; manual-approve × execution-mode
  reconciliation matrix; manual-approve closure in the No-Shortcut section.
- `.claude-plugin/plugin.json` / `pyproject.toml` / `uv.lock` — 1.12.1 → 1.12.2.

## [1.12.1] — 2026-06-27

PATCH: Documentation-drift sync plus a tesseract path-consistency fix.
Reconciles `README.md`, `ROADMAP.md`, and `skills/README.md` against the current
repo (catalog grew to 61 skills; marketplace at v1.12.0, working tree v1.12.1),
and corrects the tesseract shelf/ledger base path from `~/.claude/tesseract/` to
the real runtime `~/.tesseract/` across the skill doc AND the inline-scripts
hook. Surfaced by a 5-agent doc-drift audit workflow.

### Changed (v1.12.1)

- **`README.md`** — status block now reflects the live v1.12.0 marketplace
  publish (was frozen at "v1.0.0 live / v1.7.0 pending review"); test count
  `422` → `719` (777 total); the non-existent `/super-debug-and-fix` family
  corrected to the real `fixer` family; Expert Review `10` → `14` combinatoric
  variants plus `/expert-final-review`; utility-skill list refreshed (`/atlas`,
  `/learn`, `/pause`, `/review`, `/sme-test`, `/task-list`, `/tesseract`,
  `/visual-aid`, …); project-tree variant count corrected; Privacy section
  tesseract paths corrected to `~/.tesseract/`.
- **`ROADMAP.md`** — skill count `38` → `61`; expert-review `10` → `14`
  variants; Phase 1/4 marketplace status updated from "awaiting review" to
  published; `/atlas` checked off (shipped PR #80).
- **`skills/README.md`** — replaced the four broken `/super-debug-and-fix*` rows
  (skills that never existed) with the real `fixer` family; added the four
  missing `expert-super-tdd*` review rows, an `/expert-final-review` row, a
  `fixer` modifier row, and 17 standalone skills to the Other Skills table.

### Fixed (v1.12.1)

- **Tesseract base path `~/.claude/tesseract/` → `~/.tesseract/`.** The skill's
  Metaphor table and resume-anchor cascade, and the `block-inline-scripts.py`
  `TESSERACT_REDIRECT_PATTERN`, all keyed on `~/.claude/tesseract/` — but the
  skill's operative steps (and the real runtime) read/write `~/.tesseract/`
  directly under `$HOME`. As shipped, the v1.11.0 rules-2&3 redirect-bypass
  therefore never matched a genuine bulk-beings append. Repointed the regex and
  the SKILL.md references to `~/.tesseract/` (redirect-target scoping preserved;
  comment-only mentions still don't disarm the guards), with the structural +
  hook tests updated and a regression asserting the legacy path is no longer
  exempt. Also narrowed the bypass to the one legitimate target
  `~/.tesseract/bulk-beings.md` (the shelf is written via the Write tool, not
  Bash), shrinking the exemption surface — per pre-merge review feedback.

## [1.12.0] — 2026-06-26

MINOR: New skill `/expert-final-review` — a final pre-merge gate that composes
the existing review skills in sequence: `/fast-pr-final-self-review` (confirm
all PR peer feedback on the current branch is addressed) then
`/expert-review all` (full multi-phase sweep — bugs, security, simplification,
error handling, type design), aggregated into one go / no-go merge summary.
Joins the `expert-*-review` composition family alongside `expert-cat-review` /
`expert-tdd-review`, matching their minimalist single-body style. Built in a
worktree off `main`. Note: `/lets-make-a-skill`'s baseline-first pressure grid
was intentionally **skipped** — a pure A-then-B composition has no
rationalization surface for a no-skill baseline to shortcut on, so the Iron Law
(ship only after observing a baseline rationalize) does not bind; no sibling
composition skill was built through the grid either. A structural smoke test was
added in its place. Manifests bumped 1.11.1 → 1.12.0 in lockstep.

### Added (v1.12.0)

- `skills/expert-final-review/SKILL.md` — composition body sequencing
  `/fast-pr-final-self-review` → `/expert-review all`.
- `tests/skills/expert_final_review/` — structural smoke test (`conftest.py`,
  `test_skill_md.py`, `__init__.py`) validating frontmatter + both
  composed-skill references.
- `.claude-plugin/plugin.json` keyword `expert-final-review`.

## [1.11.1] — 2026-06-24

PATCH: `/tdd` promoted from a one-line shim into an explicit one-at-a-time TDD
micro-cycle skill — one test → RED → minimal code → GREEN → refactor → repeat,
run once per behavior. Still delegates to `/test-driven-development` for the
RED→GREEN core via a bare invocation on its own line (canonical skill untouched;
active-dev/canonical isolation). Adds the all-tests-upfront anti-pattern, an
8-row rationalization table, and red flags. Validated via `/lets-make-a-skill`
eval grid (Sonnet, parse-duration): baseline 0/5 quant → with-skill 5/5;
iteration-2 refactor closed the general-solution-at-first-combined leak (3/3
pressure held). Eval reports in `skills/tdd/evals/`. First of three sequential
PRs (1.11.1 → 1.11.2 → 2.0.0). Manifests bumped 1.11.0 → 1.11.1 in lockstep.

## [1.11.0] — 2026-06-08

MINOR: `hooks/block-inline-scripts.py` — Tesseract **redirect-target** bypass.
Commands that append (`>>`) into a `~/.claude/tesseract/` path are now exempt
from rule 2 (command-length) and rule 3 (statement-separator count) so long,
chained "bulk-beings" appends to that directory aren't blocked; rule 1 (inline
non-Bash scripts) still fires. The match is scoped to the redirect **target**
rather than a free substring: a `/expert-review` 3-tier panel (haiku + sonnet +
opus, unanimous `NARROW`) confirmed the original substring form let any
over-limit or heavily-chained command (e.g. a `cat … | curl …` exfil pipeline)
disarm rules 2 & 3 by merely carrying the path in a trailing
`# ~/.claude/tesseract/` comment — and "rule 1 still fires" is **not** a
sufficient backstop, since rule 1 matches only `python/ruby/node/perl/php`, not
pure-Bash pipelines. Also fixed the accompanying tests: `> 300` length
preconditions sat below the real `MAX_COMMAND_LENGTH = 400` (3 deny-tests
shipped red, 3 bypass-tests passed vacuously), a contradictory
`returncode == 1`/`== 0` pair in `test_non_string_command_is_allowed`, and a
`sys.path`-seeding gap that let the statement-limit bypass test pass only via
test-ordering pollution (`_load_hook_module` promoted to module scope). +2
regression tests pin the comment-form denial. 64/64 hook tests pass. Manifests
bumped 1.10.0 → 1.11.0 in lockstep.

## [1.10.0] — 2026-06-08

MINOR: `/atlas` hardening — resolved the two non-blocking findings surfaced by
`/expert-review` and Copilot on PR #80, completing the ROADMAP Phase 2 "`/atlas`
hardening patches" item. (a) `render.py` now routes `TaskRecord.status` through
`_html_escape` at both the `class="status-{…}"` and inner `<span>` interpolation
sites, closing an injection/markup-break surface (`Literal[…]` is not
runtime-enforced). (b) `resolve_anchor` guards an empty-slug override
(`--anchor "///"` → `""`): it now falls through to `Anchor("void", UNRESOLVED)`
with a warning rather than constructing invalid downstream paths like
`~/.visual-aid/atlas-.html`. +4 tests (`test_render_tasks_escapes_status`,
`test_resolve_anchor_empty_override_is_unresolved` ×3 params); 71/71 atlas tests
pass. Manifests bumped 1.9.0 → 1.10.0 in lockstep.

## [1.9.0] — 2026-05-16

MINOR: New skill `/task-list` — renders and reconciles the session TaskList in
response to `/task-list` (bare invocation → TaskCreate per item; `--update` →
derive-and-reconcile; `--update <#> :: <new>` → in-place rewrite preserving the
task ID; `--display` → render the full list past default truncation). Built via
`/lets-make-a-skill`'s baseline-first gate: a RED baseline showed no-skill
agents echo the list as plain Markdown or defer behind a permission prompt
rather than calling TaskCreate/TaskUpdate. The skill body counters those
rationalizations and a GREEN with-skill run passed 5/5 on both the quant and
pressure axes. iteration-2 de-consolidated the eval grid into separate quant and
pressure subagents with purpose-built adversarial pressure backstories, closing
an `/expert-review` methodology finding. Manifests bumped 1.8.0 → 1.9.0 in
lockstep.

### Added (v1.9.0)

- `skills/task-list/SKILL.md` — four-mode skill with an anti-pattern block keyed
  to the captured baseline rationalizations.
- `skills/task-list/evals/` — `/lets-make-a-skill` eval workspace: iteration-1
  and iteration-2 grids, `benchmark.{json,md}`, `rationalizations.md`, and the
  persisted `/expert-review` findings.

## [1.8.0] — 2026-05-15

MINOR: New skill `/legal-visual-aid` — composes `/legalzoom:review-contract`
(contract review, by reference to the legalzoom plugin) with `/visual-aid`
(single-page HTML explainer): review a contract, then render the risk-scored
findings as an accessible visual aid. Built via `/lets-make-a-skill`'s
baseline-first gate — a RED baseline showed no-skill agents drop the
`/visual-aid` accessibility guards under "quick / rough" contract-review
pressure; the skill body counters that rationalization and a GREEN with-skill
run held all six a11y guards. Manifests bumped 1.7.2 → 1.8.0 in lockstep.

### Added (v1.8.0)

- `skills/legal-visual-aid/SKILL.md` — composition skill with an
  accessibility-floor discipline section and a 5-row rationalization table.

## [1.7.2] — 2026-05-05

PATCH: `/tesseract` SKILL.md — Hallway 1 no-git-repo precondition + smoke
regression. Brings `uv.lock` to 1.7.2 in two steps: a catch-up sync 1.0.0 →
1.7.0 (commit `c2a06d7`, aligning with manifests bumped in `04fc3c4`), then the
1.7.2 PATCH bump alongside `plugin.json` and `pyproject.toml`.

### Added (v1.7.2)

- `tests/skills/tesseract/smoke/test_hallway1_precondition.py` — 4 static
  text-presence regression assertions (PR #21 `TestTesseractRegressions`
  pattern) covering: precondition probe, fixed silent-skip line, both
  anti-pattern callouts (no-cwd-leak + no-grep-fallthrough), ordering
  (precondition must appear textually before the cascade).

### Fixed (v1.7.2)

- `skills/tesseract/SKILL.md` Hallway 1: adds explicit
  `git rev-parse --is-inside-work-tree 2>/dev/null` precondition; on non-zero
  exit prints fixed line `(not in a git repository — Hallway 1 silent)` and
  skips the cascade. Closes a spec gap where Hallway 1 implicitly assumed a git
  repo at cwd; pre-fix paths either errored noisily, leaked cwd via a
  synthesized message, or fell through to the free-text grep branch.
- `uv.lock`: 1.0.0 → 1.7.2 in two steps. Package manifests bumped to 1.7.0 in
  `04fc3c4` but uv.lock was still at 1.0.0 in this worktree (pre-existing
  drift). Step 1: catch-up sync 1.0.0 → 1.7.0 (commit `c2a06d7`). Step 2: 1.7.0
  → 1.7.2 alongside the lockstep PATCH bump of the manifests.

## [1.7.1] — 2026-05-05

PATCH: `/visual-aid` SKILL.md — profile-lock opt-out + rationalization counter.

### Added (v1.7.1)

- `tests/skills/visual_aid/pressure/eval_profile_lock_rationalizations.md` —
  RED→GREEN→REFACTOR evidence log for the `chrome-devtools-mcp` profile-lock
  opt-out fix (6 sonnet subagents per CLAUDE.md no-Opus-subagents rule: 1 leaked
  RED + 2 clean RED + 1 baseline GREEN + 1 with-skill GREEN + 1 REFACTOR
  re-fire).

### Fixed (v1.7.1)

- `skills/visual-aid/SKILL.md`: 3 coordinated edits closing a rationalization
  gap where the `chrome-devtools-mcp` profile-lock error was being routed
  through unrelated opt-outs ("fast iteration", "not installed") instead of
  named verbatim. Adds explicit profile-lock fallback (SOP step 3),
  `chrome-devtools-mcp profile lock` opt-out bullet (with `--isolated` retry
  path + step-8 cleanup requirement), and common-mistakes table row flagging
  environmental-blocker repackaging as a preference-coded opt-out.

## [1.7.0] — 2026-05-03

Phase 5 skill catalog expansion + Phase 6 `/listen` enforcement + plugin
manifest bump to v1.7.0. Each new skill ships through TDD discipline (RED tests
first, then SKILL.md) and the
`tests/skills/<skill>/{helpers,smoke,pressure,performance}/` test taxonomy.

### Added

- **`/add-to-roadmap` (v1, prose)** — appends a checkbox task to the project's
  `ROADMAP.md` under a fuzzy-resolved `## Phase` or `### Subsection` header.
  Walks up from CWD to repo root, fuzzy contains-match (case-insensitive),
  bottom-of-section insertion, unified-diff confirmation gate before write.
  Pure-prose v1; deterministic Python helper roadmapped for v2. (PR #58)
- `tests/skills/add_to_roadmap/` — 28 tests across 4 layers (structural 9, smoke
  9, pressure 7, performance 2). Doc-length budget calibrated on observed
  sibling-skill rates (`tesseract` ~270 lines, `checkpoint-save` ~80). (PR #58)
- **`/skill-creator-super-duper-cat` (the supercreator)** — composed-skill
  dispatcher for the skill-creation workflow. (PR #62)
- **`/cat` parallel-dispatch decision branch** + active-dev/canonical isolation
  rule baked into the skill body. (PR #61)
- **Phase-6 `/listen` enforcement** — additional rationalization counters for
  the listen workflow. (PR #68)
- `ROADMAP.md` Phase 5: `/add-to-roadmap` helper-script entry under "Flag
  additions to existing skills" — first dogfood-eat of the new skill (added
  manually since the skill couldn't add itself). (PR #58)

### Changed

- **Rename `/skill-creator` → `/lets-make-a-skill`** — final naming for the
  create-a-skill flow. Internal references and test fixtures updated. (PR #66)
- `ROADMAP.md`: added `/tesseract --input` file-mode entry under Phase 2. (PR
  #59)
- `ROADMAP.md`: expanded with checkpoint-system persistence-layer details. (PR
  #60)
- `ROADMAP.md`: Phase 5 expansion entries. (PR #56)
- `README.md`: marketplace-install flow + listing copy updated for v1.7.0. (PR
  #69)
- `.claude-plugin/plugin.json`, `pyproject.toml`: version bumped to 1.7.0
  (`04fc3c4`, PR #67).

### Fixed

- `tests/performance/test_learn.py`, `tests/smoke/test_learn.py`: trailing-
  newline / whitespace fixes from `uv run ruff format` (no behavior change).

## [1.0.0] — 2026-04-23 (submitted, review pending)

v1.0.0 **submitted** to the official Claude Code marketplace on 2026-04-23 as a
standalone plugin alongside `superpowers`. Currently **awaiting Anthropic
review** — not yet listed. Until approval, install via `git clone` +
`claude --plugin-dir` (see README). This section will be updated with an
"(approved)" note and the effective install command once the submission lands.

### Added (v1.0.0)

- `.claude-plugin/plugin.json` manifest (v1.0.0, MIT, author + keywords set for
  marketplace discovery).
- `hooks/hooks.json` registering PreToolUse Bash hook for the existing
  `block-inline-scripts.py` guardrail via `${CLAUDE_PLUGIN_ROOT}`.
- Privacy policy section in `README.md` documenting that skills, hooks, and
  cost-tracking run entirely locally — no data collection or transmission by the
  plugin itself.
- README rewrite for marketplace-install flow: top-of-file
  `/plugin install claude-damn@claude-plugins-official`, Companion plugins
  table, Quickstart section, updated Project structure.

### Fixed (v1.0.0)

- `skills/cost-opt/SKILL.md` frontmatter: multi-line unquoted `description`
  (invalid YAML) rewritten as single-line quoted scalar so
  `claude plugin validate .` parses it.
- `skills/sme-test/SKILL.md`: added GFM header-separator rows to two tables that
  prettier was collapsing into prose.
- `pyproject.toml` consolidated two duplicate `dev = [...]` keys (the fuller
  list was incorrectly nested under `[tool.pytest.ini_options]` where `uv sync`
  never picked it up).
- `tests/test_hook_inline_scripts.py`: deleted buggy shadowed F811 duplicates of
  `test_null_command_is_allowed`, `test_non_string_command_is_allowed`,
  `test_non_dict_tool_input_is_allowed` — the first copy had contradictory
  assertions from a half-done PR #37 refactor; the second copy matches current
  hook behavior.
- `src/extract_cost.py`: `sorted(PRICING, key=len)` →
  `sorted(PRICING.keys(), key=lambda k: len(k))` to preserve `_T = str` through
  ty's overload resolution.
- `tests/conftest.py` fixture: return annotation `Path | None` →
  `Iterator[Path | None]` for yield-based fixture.
- `tests/test_skill_helpers.py` `_FakeRun`: `last_args: tuple | None` →
  `tuple = ()` (same for `last_kwargs`) to remove needless `None` narrowing
  burden.

### Tooling (v1.0.0)

- Linters at zero: ruff 11 → 0, ty 12 → 0, prettier 17 → 0.
- Tests green: pytest 422 passed, 58 deselected.
- `.prettierignore` covers `.pytest_cache/` (auto-generated) and
  `rules/PERSONALIZATION.example.md` (prettier 3.8.2 idempotency bug on HTML
  comment inside list with `tabWidth: 3`).

## [0.2.0] — `feat/transition-to-plugin` pre-ship

The plugin packaging phase: introducing `uv`, `pyproject.toml`, a real test
tree, and the first spec-plan-test skill (`sme-test`).

### Added

- **Plugin scaffolding**
   - `pyproject.toml` + `uv.lock` — uv-managed `.venv`, Python ≥ 3.14. All
     test/dev packages (`pytest`, `pyyaml`, `pytest-xdist`, `ruff`) in
     `[dependency-groups] dev`, no runtime dependencies.
   - `tests/` tree with `conftest.py` and shared helpers.

- **Harness test coverage**
   - `tests/test_extract_cost.py` — session JSONL parsing and Anthropic-pricing
     cost math, including fast-mode pricing branches.
   - `tests/test_checkpoint_archive.bats` — checkpoint archive rotation across
     branches.
   - `tests/test_hook_inline_scripts.py` — pre-tool hook that blocks multiline
     non-Bash scripts from the Bash tool.
   - `tests/test_permissions.py` — `settings.json` allow/ask/deny permission
     lists.
   - `tests/test_settings_structure.py` — `settings.json` schema invariants.
   - `tests/test_sync_theme.bats` — launchd theme-sync behaviour.

- **sme-test v1** skill at `skills/sme-test/` — Subject Matter Expert TDD coach
  with three modes (`coach` default, `expert` via `-x`, `expert-auto` via
  `-xa`).
   - `SKILL.md` entry point with frontmatter, mode docs, and shared-memory
     contract.
   - 5 prompt files: `coach-dispatch`, `three-whys`, `gwt-formulation`,
     `test-writer`, `red-gate`.
   - 2 runner adapters: `adapters/python/` and `adapters/bats/` implementing the
     4-capability contract.
   - `errors/error-handlers.md` covering 5 error classes with recovery paths.
   - 132 structural tests across `tests/skills/sme_test/` (SKILL.md, prompts,
     errors, adapters, cross-file integration). Layer 4 (dogfood) deferred to
     first real usage.
   - Approved design spec at
     `docs/superpowers/specs/2026-04-05-sme-test-design.md` and 12-task
     implementation plan at `docs/superpowers/plans/2026-04-05-sme-test.md`.

- **`/proceed` skill** at `skills/proceed/SKILL.md` — single-use user-invocable
  signal that authorizes Claude to pass the current approval gate only (design
  review, plan approval, risky-action confirmation). Body carries the literal
  phrase "Aligned and approved" and an explicit single-gate scope clarification
  so it does not grant standing authorization.
   - 5-level regression coverage under
     `tests/{structural,behavioral,integration,smoke,performance}/test_proceed.py`
     (23 default tests + 15 marker-gated smoke/performance cells). Mirrors the
     `/listen` test pattern. Behavioral layer uses TDD mutation checks.

- **`/tesseract` skill** at `skills/tesseract/SKILL.md` — user-invocable
  cross-session reflection tool. Resolves an anchor (file/branch/topic), reads
  four "hallways" of evidence (git, memory, shelf, bulk-beings), and writes back
  a shelf entry plus a one-line learning to `~/.claude/tesseract/`. Solo skill —
  no subagents, no shared memory, communicates with its own past and future only
  via file I/O.
   - Structural + regression coverage at
     `tests/skills/tesseract/test_skill_md.py` (11 tests: 5 regressions for the
     PR #21 review fixes — slug-rule prose accuracy, `git log --grep -F`,
     porcelain rename handling, `printf` append form — plus 6 structural
     invariants for frontmatter, hallway count, process-step numbering, and
     skill-dir/spec-name alignment).

- **Docs**
   - `README.md` — project overview, skill catalog, setup, project structure.
   - `ROADMAP.md` — 4-phase plugin transition plan.
   - `CHANGELOG.md` — this file.

- **PR review fixes** (PR #7 feedback)
   - `tests/test_pyproject.py` — regression test asserting test-only packages
     stay in dev dependency group.
   - `tests/skills/expert_review/` — structural tests for expert-review SKILL.md
     (duplicate bullet, Phase 0 numbering).
   - `scripts/test-isolated.sh` — error guards on worktree setup commands.

- **PR review fixes** (PR #19 feedback)
   - `tests/performance/test_proceed.py` — corrected matrix docstring (actual
     matrix is complexity × prompt kind × model, not 2×3).
   - `tests/smoke/test_proceed.py` — tightened `test_not_standing_authorization`
     to require explicit negation of "standing" or a current-gate-only phrase in
     proximity, so the test no longer passes on incidental occurrences of
     "current"/"single"/"only".

### Changed

- `expert-review` guidelines — added Java plus comprehensive language, security,
  and cloud specialization references.
- `expert-review` SKILL.md — removed duplicate "You combine the roles of..."
  bullet; fixed Phase 0 step numbering (1-5 sequential).
- `CLAUDE.md` — clarified agent directives: model routing, batch operations, no
  inline non-Bash scripts via heredocs, git-commit opt-out.
- `hooks/block-inline-scripts.py` — deny feedback moved from top-level
  `systemMessage` (persistent `<system-reminder>`) to
  `hookSpecificOutput.permissionDecisionReason` so the block message is scoped
  to the denied Bash call and no longer leaks into subsequent unrelated tool
  uses. Exception path now writes to stderr with exit 1 instead of emitting a
  persistent `systemMessage`. Tests updated.
- `CLAUDE.md` — documented the PreToolUse hook output contract (use
  `permissionDecisionReason`, not `systemMessage`); noted the repo hook's Bash
  limits (400 chars / 4 statement separators); documented the `.worktrees/`
  convention and gitignored `CHECKPOINT.md`.

## [Baseline] — Pre-plugin (`~/.claude` dotfiles)

The state the plugin transition inherits from: a flat `~/.claude` directory with
commands, skills, and tooling.

### Added

- **Slash commands:** `/review`, `/expert-review`, `/address-pr-feedback`,
  `/cost`, `/cost-opt`.
- **Skill catalog (38 skills)** composed from four modifiers (`tdd`, `super`,
  `duper`, `cat`):
   - **TDD family:** `/tdd`, `/tdd-cat`, `/duper-tdd`, `/duper-tdd-cat`.
   - **Brainstorm + TDD:** `/super`, `/super-cat`, `/super-duper`,
     `/super-duper-cat`.
   - **Debug + Brainstorm + TDD:** `/super-debug-and-fix` and the `duper` /
     `cat` variants.
   - **Expert Review:** `/expert-review` through
     `/expert-super-duper-cat-review` (10 variants).
   - **Debug + Brainstorm + TDD:** `/super-debug-and-fix` and the `duper` /
     `cat` variants.
   - **Expert Review:** `/expert-review` through
     `/expert-super-duper-cat-review` (10 variants).
   - **Lifecycle:** `/checkpoint-save`, `/checkpoint-resume`, `/check-yourself`,
     `/continue`.
   - **PR feedback:** `/fast-pr-feedback-to-me`, `/fast-pr-feedback-to-others`,
     `/fast-pr-final-self-review`.
   - **Utility:** `/cost_`, `/cost-opt`, `/draft-cmt-msg-4-below`, `/enforce`.
   - Full combinatoric table in `skills/README.md`.
- `extract_cost.py` — parses Claude Code session JSONL files, computes real
  token usage and cost via Anthropic pricing, logs to `~/.claude/cost-log/` as
  JSONL.
- `statusline-command.sh` — shell statusline showing per-session cost.
- `settings.json` — permission allow/ask/deny rules, pre-tool hooks, script
  execution policy.
- `policy-limits.json` — remote control restrictions.
- `com.claude.sync-theme.plist` — macOS launchd plist for theme-sync service.
- `CLAUDE.md` — opinionated project rules for model routing, testing standards,
  Python style, and FastAPI architecture.
- MIT `LICENSE`.

### Changed

- Renamed project `awesome-bruno` → `awesome-claude` → `claude-damn`.
- Flattened nested directories out of the symlinked tree; removed stray
  symlinks.
- `.gitignore` added to exclude IDE config.
