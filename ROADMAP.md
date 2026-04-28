# Roadmap — `claude-damn`

Transition the flat `~/.claude` dotfile collection (commands, 38 skills, hooks,
cost tooling) into a first-class Claude Code plugin that installs alongside
`superpowers` from the official marketplace.

## Phase 0 — Baseline (done)

- [x] Slash commands: `/review`, `/expert-review`, `/address-pr-feedback`,
      `/cost`, `/cost-opt`
- [x] Full combinatoric skill catalog (38 skills): `tdd` / `super` / `duper` /
      `cat` families
- [x] `expert-review` family with multi-language + cloud + security
      specialization (10 variants)
- [x] `checkpoint-save` / `checkpoint-resume` / `check-yourself` lifecycle
      skills
- [x] `extract_cost.py` — session JSONL → token usage + cost via Anthropic
      pricing
- [x] `statusline-command.sh` — per-session cost in statusline
- [x] `settings.json` — permission allow/ask/deny rules, pre-tool hooks
- [x] `policy-limits.json` — remote control restrictions
- [x] `com.claude.sync-theme.plist` — macOS launchd theme sync

## Phase 1 — Plugin packaging (v1.0.0 submitted 2026-04-23; awaiting Anthropic review)

- [x] Introduce `pyproject.toml` + `uv.lock` (uv-managed `.venv`, Python ≥ 3.14)
- [x] Stand up `tests/` tree with `pytest` + `ruff`
   - [x] `test_extract_cost.py` — cost parser coverage including fast-mode
         pricing
   - [x] `test_checkpoint_archive.bats` — checkpoint archive rotation
   - [x] `test_hook_inline_scripts.py` — inline-script hook guardrail
   - [x] `test_permissions.py` — settings.json permission lists
   - [x] `test_settings_structure.py` — settings schema
   - [x] `test_sync_theme.bats` — launchd theme-sync
   - [x] `tests/skills/sme_test/` — 132 structural tests for sme-test v1
- [x] **sme-test v1** — first skill built with spec-plan-test discipline (see
      `docs/superpowers/specs/2026-04-05-sme-test-design.md`)
- [ ] Dogfood sme-test on itself (Layer 4 — manual coaching run on its own
      files)
- [ ] Structural test coverage for the rest of the skill catalog (`sme-test`,
      `expert-review`, and `tesseract` have structural tests; other skills are
      ad-hoc markdown)
- [ ] **sme-review v1** — coaching-driven sibling to sme-test, interactive
      alternative to `/expert-review`. Spec brainstorm in progress; see
      `CHECKPOINT.md` and `.remember/remember.md` for current state. Will
      refactor `/expert-review` to source phase prompts from
      `skills/_shared/review-phases/` so both skills compose the same building
      blocks. Tests adopt the 6-layer pyramid pattern (structural, behavioral,
      integration, smoke, performance, yolo) modeled on `/listen`'s test suite,
      with observed-rate-calibrated pass gates.
- [x] Claude Code plugin manifest at `.claude-plugin/plugin.json` (v1.0.0,
      skills auto-discovered, validated via `claude plugin validate .`)
- [x] Namespace: **standalone plugin** submitted to
      `claude-plugins-official/external_plugins` (overlay-on-superpowers was
      investigated and ruled out — plugins don't overlay)
- [x] PreToolUse hook wired via `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}`
- [x] Privacy policy section in README for Anthropic Verified Status

## Phase 2 — Skill hardening

- [ ] Normalize `SKILL.md` frontmatter across all 38 skills (name, description,
      user-invocable, argument-hint)
- [ ] Port hand-wired shared-memory conventions into a reusable skill helper
- [ ] Add integration coverage for the `super` / `duper` / `cat` modifier
      composition rules documented in `skills/README.md`
- [ ] Canonicalize the error-handling contract from `sme-test/errors/` as a
      shared skill pattern
- [ ] `/tesseract` file-input mode: accept `--input <path>` (e.g.
      `/tesseract --input ./scratch/thread-dump.txt`) and read the artifact via
      the Read tool instead of expecting inline content. Error clearly when
      input >50KB and suggest file mode.

## Phase 3 — Harness integration

- [ ] Formalize pre/post tool-use hooks in `settings.json` with a typed schema
- [ ] Surface cost + policy-limit warnings through the statusline (not just
      cost)
- [ ] Theme-sync launchd plist → plugin-managed lifecycle (install/uninstall
      hooks)
- [ ] Generalize the inline-script guardrail into a shared hook the plugin can
      install
- [ ] **Checkpoint-system persistence layer** — define JSON schema for
      `.checkpoints/latest.json` (`worktree`, `branch`, `task_list`,
      `next_action`, `timestamp`); update `/checkpoint-save` to write it; update
      `/checkpoint-resume` to read it and continue without `AskUserQuestion`;
      add a `Stop` hook that auto-saves on session end. Build via
      `/writing-skills` (TDD; spec-doc layout per `feedback_spec_doc_layout.md`;
      frozen-dataclass tests per `feedback_frozen_dataclass_test_exception.md`).
      Fixes the 2026-04-28 `/checkpoint-save` Step-3 delayed-invocation misfire
      (bulk-302).

## Phase 4 — Distribution

- [x] Install via Claude Code's plugin mechanism (pre-approval: `git clone` +
      `claude --plugin-dir`; post-approval:
      `/plugin install claude-damn@claude-plugins-official`) rather than
      `cp -r skills/* ~/.claude/skills/`
- [x] **Submitted** to the official Claude Code marketplace 2026-04-23 via
      `clau.de/plugin-directory-submission`
- [ ] **Approved** and listed in `claude-plugins-official/external_plugins/` —
      awaiting Anthropic review
- [ ] Versioned releases with CHANGELOG entries per skill
- [ ] Per-skill quickstart docs and usage examples

## Phase 5 — Skill catalog expansion (post-v1.0.0)

Next wave of skill additions after marketplace approval. Each new skill must go
through `/brainstorming` → `/writing-plans` → `/test-driven-development` →
`/writing-skills` before implementation — the catalog-hardening workflow is the
authoring contract.

### Measurement & perception

- [ ] **`/time`** — help Claude understand time, timings, speed, rates; how to
      use, verify, apply. Companion to the existing `/space` skill (gives Claude
      a consistent mental model for wall-clock vs. elapsed, time-of-day vs.
      duration, rates of change, when sleeping is productive vs. wasteful).
- [ ] **`/spacetime`** — wrapper composing `/space` + `/time` for tasks
      implicating both dimensions (scheduling, performance timing within a
      spatial layout, spatiotemporal data).
- [ ] **`/whats-color`** — help Claude understand color: WCAG contrast formula,
      sRGB vs. linearized channels, perceptual vs. mathematical luminance,
      palette selection, color-blindness mappings. Directly addresses the
      2026-04-24 `/learn` finding on `/visual-aid`'s contrast-formula misfire.

### Control triad (chemical-engineering inspired)

Feedforward controllers intervene before a disturbance reaches the plant;
feedback controllers measure error after the fact and correct; retrospective
review closes the loop by learning from past cycles. Give the operator
declarative control over when a named set of skills applies to ongoing work:

- [ ] **`/feedforward-control`** — proactively apply listed skills to everything
      to come (e.g., "apply `/verification-before-completion` and
      `/check-yourself` to every response this session").
- [ ] **`/feedback-control`** — retroactively apply listed skills to everything
      done so far (e.g., "apply `/writing-skills` to every `SKILL.md` edit in
      the last 30 minutes").
- [ ] **`/stop-control`** — halt any active `/*control*` skills. Deregisters
      standing feedforward / feedback orders so they don't bleed into the next
      task.
- [ ] **Alias: `/retrospective-control` → existing `/learn`.** `/learn` IS
      retrospective control — reviews which skills fired, were ignored, or
      misfired in past work, and updates the mental model. Registering the alias
      completes the triad vocabulary (feedforward / feedback / retrospective) so
      the operator can speak the same language across all three.

### Skill-testing & operator-mode skills

- [ ] **`/test-under-pressure`** — pressure-test a Claude skill. Runs subagent
      pressure scenarios (time, authority, sunk-cost, exhaustion — singly and
      combined) against a target skill's rationalizations. Extracts the
      skill-testing methodology currently embedded inside `/writing-skills` into
      a standalone invocation so skills can be pressure-tested independently of
      authoring.

### Compositional / algebraic skills

- [ ] **`/ops`** — CAS-meets-skills: declarative algebraic operators on skills.
      Symbols: `x`, `u`, `+`, `-`, `{}`, `[]`. Purpose: compose skills with
      explicit algebra instead of nested `/super-duper-tdd-cat`-style
      combinators. Operator semantics (what `x` / `u` mean precisely; set vs.
      sequence semantics for `{}` vs. `[]`) must be nailed down in
      `/brainstorming` before spec.
- [ ] **`/bra-ket`** — quantum bra-ket syntax for skill composition:
      `<LHS | RHS>`, where the LHS bra operates on the RHS ket. Purpose: give
      the operator a physics-native way to express "this skill applies to this
      work" when `/ops`'s CAS syntax doesn't fit the operation. Needs
      `/brainstorming` for full operator semantics — including how `/ops` and
      `/bra-ket` coexist vs. compete.

### Flag additions to existing skills

- [ ] **`/learn --visual`** — render `/learn` retrospective findings as a
      single-file visual-aid HTML in the same card-grid format as
      `~/.visual-aid/visual-aid-learn-findings.html`. Not a new skill; a new
      flag on the existing `/learn`. Added to the roadmap 2026-04-24 after
      operator positively flagged the card-grid render produced on-the-fly
      during that session's retrospective; the flag makes it the canonical
      rendering path for future `/learn` runs rather than a one-off.
- [ ] **`/add-to-roadmap` helper script** — replace the v1 prose-skill with a
      deterministic Python helper at `skills/add-to-roadmap/insert_item.py` so
      the skill can be invoked non-interactively (CI, hooks, scripted batch
      ROADMAP updates). v1 is pure-prose (Claude reads ROADMAP.md and applies
      the Edit tool); the helper version takes `<phase-or-section>` and
      `<task-text>` as argv, performs the same fuzzy-match + bottom-of-section
      insertion deterministically, and emits a unified diff to stdout. Added to
      the roadmap 2026-04-27 as the v1 skill's first dogfood-eat — the entry was
      authored by hand in the same PR that introduces the skill, since the skill
      didn't yet exist to add itself.

### SOLID & SWE composition

Added to the roadmap 2026-04-25 from the `self-improvement` tesseract anchor.
Lands AFTER the PERSONALIZATION SOLID section (below) so `/solid` has a
canonical principle reference to read from.

- [ ] **`/solid`** — single skill enforcing SOLID principles across three
      temporal modes, mapped to the 5.2 control-triad vocabulary: -
      **feed-forward** (before writing) — suggest SOLID-compliant designs
      upfront; flag violations during `/brainstorming`. - **feed-back** (during
      writing) — catch SOLID violations as code is being written; emit warnings
      during the implementation phase of `/tdd` GREEN. - **retro-active** (after
      writing) — scan existing code for refactor candidates (god classes, fat
      interfaces, hidden coupling); produce `/super-swe`-ready findings.
- [ ] **`/swe`** — composite skill `/solid ⨷ /tdd ⨷ /fixer`. Standard operating
      loop for non-trivial software-engineering work: design under SOLID, drive
      via TDD, debug via systematic-debugging. The `⨷` tensor-product is the
      composition operator from `/ops` / `/bra-ket` (5.4) — `/swe` will need to
      reconcile its informal-`⨷` notation with whatever `/ops` formalizes.
- [ ] **SWE combinatoric family** — derived skills following the existing `/tdd`
      and `/fixer` family density. Proposed initial 8 (cardinality matched to
      existing families; full 2^N permutation deferred to `/ops` 5.4 when that
      lands): - `/super-swe` — brainstorm + swe - `/duper-swe` — worktree +
      swe - `/swe-cat` — swe + subagent-driven-development - `/super-cat-swe` —
      brainstorm + cat + swe - `/duper-tdd-swe` — worktree + tdd + swe
      (TDD-explicit on top of swe's tdd, for cases where the tdd phase is the
      primary surface) - `/super-duper-swe-tdd-cat` — full stack -
      `/expert-swe-review` — expert review through SOLID lens -
      `/super-fixer-swe` — expert-debug + fix via swe

### PERSONALIZATION & rules updates

- [ ] **SOLID emphasis in PERSONALIZATION** — add a
      `## SOLID Software Engineering [policy] [soft]` section to all three:
      `~/.claude/rules/PERSONALIZATION.md` (operator runtime),
      `~/.claude/rules/PERSONALIZATION.example.md` (active-dev clone), and this
      repo's `rules/PERSONALIZATION.example.md` (canonical, public). Five
      principles (SRP / OCP / LSP / ISP / DIP) with one-line when-to-apply each.
      Lands BEFORE `/solid` is implemented — `/solid` reads from this section as
      its principle source.

### `/learn` scope extension

- [ ] **`/learn` config-surface coverage** — extend `/learn` beyond Skills to
      also produce learnings against `CLAUDE.md`, `PERSONALIZATION.md`, hookify
      rules, and `settings.json`. Three new emit modes: - **rule findings** →
      propose edits to CLAUDE.md / PERSONALIZATION.md. - **hook findings** →
      propose hookify rules (delegate to `/hookify:writing-rules`). - **settings
      findings** → stage context for `/update-config` rather than editing
      settings.json directly. `/learn` produces the WHAT (which key) and WHY
      (which session evidence); operator runs `/update-config` to apply.
