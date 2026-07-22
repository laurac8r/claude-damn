# Roadmap — `claude-damn`

Transition the flat `~/.claude` dotfile collection (commands, 61 skills, hooks,
cost tooling) into a first-class Claude Code plugin that installs alongside
`superpowers` from the official marketplace.

## Phase 0 — Baseline (done)

- [x] Slash commands: `/review`, `/expert-review`, `/address-pr-feedback`,
      `/cost`, `/cost-opt`
- [x] Full combinatoric skill catalog: `tdd` / `super` / `duper` /
      `cat` families
- [x] `expert-review` family with multi-language + cloud + security
      specialization (14 variants)
- [x] `checkpoint-save` / `checkpoint-resume` / `check-yourself` lifecycle
      skills
- [x] `extract_cost.py` — session JSONL → token usage + cost via Anthropic
      pricing
- [x] `statusline-command.sh` — per-session cost in statusline
- [x] `settings.json` — permission allow/ask/deny rules, pre-tool hooks
- [x] `policy-limits.json` — remote control restrictions
- [x] `com.claude.sync-theme.plist` — macOS launchd theme sync

## Phase 1 — Plugin packaging (v1.0.0 submitted 2026-04-23; published to the community marketplace v1.12.0; repo at v1.12.2)

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

- [ ] Normalize `SKILL.md` frontmatter across all 61 skills (name, description,
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
- [ ] **`/checkpoint-save` post-squash-merge content-delta verification** —
      add a verification gate for the branch-deleted-post-merge case (symptom:
      `git status` says "Your branch is based on 'origin/<branch>', but the
      upstream is gone"). The skill MUST verify content-delta between any
      "ahead-of-upstream" commits and the merge target before classifying
      them as "not yet shipped." Squash-merges flatten the entire PR HEAD;
      commits made before the squash-cutoff are content-equivalent on the
      target. Add rationalization counter for "these were committed AFTER
      the squash-merge…" → reality: the squash takes the PR HEAD at merge
      time, not the operator's local merge commit. Misfire surfaced
      2026-05-09 during a `/checkpoint-save` invocation on a feature-branch
      worktree post-PR-squash-merge.
- [ ] **`/tesseract` slash-prefixed skill-name anchor handling** — anchor
      cascade Step 3 ("anchor contains `/`") misclassifies slash-prefixed
      skill-name anchors like `/learn` as paths and routes them to
      `git log --follow -- /learn`, which fails with "outside repository".
      Special-case anchors matching `^/[a-z][a-z0-9-]*$` — fall through to
      free-text `--grep` instead of path-heuristic. Misfire surfaced
      2026-05-09 in `/tesseract /learn` invocation.
- [ ] **Pressure-test PERSONALIZATION.example.md rules via
      `/lets-make-a-skill`** — dispatch `/duper`-parallelized
      `/lets-make-a-skill` runs, one per rule in
      `.claude/rules/PERSONALIZATION.example.md`. Each rule gets a
      dedicated pressure-test skill that asserts the rule's expected
      behavior under representative inputs (e.g., the "no Opus
      subagents" rule fires a Task call w/ `model=opus` and asserts
      the `block_opus_subagent.py` hook denies it; the "cd-first"
      Bash rule fires a chained `cd <dir>; <cmd>` and asserts the
      permission-gate response shape). Surfaces drift between
      documented operator personalization and real agent behavior;
      produces a per-rule conformance report. Independent per-rule
      tests → natural fan-out via `/duper`. Output:
      `tests/skills/` coverage matrix mapping each PERSONALIZATION
      rule to ≥1 pressure test.
- [x] **`/atlas` hardening patches surfaced by `/expert-review`** — two
      non-blocking findings on the initial `/atlas` PR. **Resolved inline on
      PR #80** (both Copilot review comments addressed; +4 tests):
      (a) `skills/atlas/render.py:64-65` — `TaskRecord.status` interpolated
      unescaped into `class="status-{t.status}"` and the inner `<span>`;
      `Literal["pending","in_progress","completed"]` is not runtime-
      enforced. **Fixed:** both sites now route through `_html_escape`
      (`test_render_tasks_escapes_status`).
      (b) `skills/_shared/anchor.py:44-45` — `slugify("///")` → `""`;
      `Anchor(slug="", ...)` constructed without validation; downstream
      produced `~/.tesseract/shelf/.md`, `~/.visual-aid/atlas-.html`,
      and a blank `<h1>Anchor:</h1>`. **Fixed:** empty slug falls through to
      `Anchor("void", UNRESOLVED)` with a warning in `resolve_anchor`
      (`test_resolve_anchor_empty_override_is_unresolved`).
- [ ] **`/atlas` smoke/pressure/performance test suites** — helper-level
      coverage is complete (67 tests in `tests/skills/atlas/helpers/`),
      but `tests/skills/atlas/{smoke,pressure,performance}/` currently
      exist as empty `__init__.py` stubs only. Add full-orchestration
      smoke tests (end-to-end SKILL.md steps 1-7 against a fixture
      worktree), pressure tests (read-only-invariant assertions,
      malformed shelf / unparseable CHECKPOINT / non-repo cwd / explicit
      `--anchor "///"` empty-slug paths), and performance tests
      (`render()` latency under realistic shelf/git/commit volumes).
      Tracks the plan's Tasks 19-21 deferred from the initial `/atlas`
      PR boundary. Cross-reference: ROADMAP `/atlas` entry in Phase 5.
- [ ] **Root-cause `/check-yourself` skip-rate → hookify (operator-ratified
      2026-07-11)** — `/check-yourself` fires at only a fraction of its
      enumerated task-boundary triggers (Skill returns, `/proceed` gates,
      test-runs, durable file-writes). Observed 2026-05-16: one long multi-skill
      session invoked it once (at `/pause`), skipping ~15+ boundaries. The skill
      text is already maximal (full trigger enumeration + 11-row rationalization
      table), so brainstorm whether the gap is invocation-discipline, harness
      enforcement, or a structural fix (e.g. hook-based boundary detection).
      Surfaced via `/learn`. **Recurred 2026-07-11** (~10 stale-task
      system-reminders, still fired only at `/pause`); the `/tesseract` `learn`
      shelf shows the same "fired only at /pause" pattern flagged 2026-07-05.
      **Operator ratified the structural fix: hookify** — a hook that detects
      boundary events and forces (or hard-nudges) the invocation, since a
      self-invoked skill can't enforce itself.
- [ ] **Bake the `/tesseract` TaskList bookend into the skill** — the operator's
      "write a TaskList before `/tesseract`, resume from it on exit" rule lives
      only in `PERSONALIZATION.md`, so the skill never enforces it; it was
      skipped 2026-07-11 even though the `feedback_tesseract_task_list_bookend`
      memory surfaced in that same run's Hallway 2. Add a bookend step to the
      skill (guarded/optional so the shippable skill doesn't hardcode operator
      preference). Surfaced via `/learn`.
- [ ] **`checkpoint-save`/`remember` parallel-lane shared-slot handling** — both
      skills say "overwrite the rolling `.remember/` slot" without covering the
      multi-lane case where the slot holds another live lane's handoff. On
      2026-07-11 a session had to verify the per-worktree `CHECKPOINT.md`
      backup before overwriting the shared slot. Add a step:
      before overwriting, confirm the displaced lane's per-worktree checkpoint
      exists (else preserve/append, don't clobber). Surfaced via `/learn`.
- [ ] **`/duper` + `/cat` out-of-anchor subagent worktrees** — spawn subagents
      in worktrees NOT nested under the session-launch dir via `/tmp` scripts.
      The Bash harness resets cwd above the launch anchor (verified 2026-05-30)
      and subagents can't write across worktrees. Re-visit `/cat` +
      `/dispatching-parallel-agents` implications.
- [ ] **`/add-to-roadmap` cross-repo target** — the skill is CWD-bound (walks
      up to the current repo's ROADMAP) and silently resolves to CWD; it can't
      target a different repo. Add an explicit target repo/path arg, or detect +
      warn when the phrasing implies a repo ≠ CWD. Surfaced 2026-05-30 invoking
      it cross-repo from another project's worktree (needed a manual
      absolute-path workaround).
- [ ] **`/visual-aid` focus-preserving verification opt-out** — the default
      chrome-devtools verification foregrounds a browser window, conflicting
      with a reduce-motion / no-focus-steal preference; the enumerated opt-outs
      (not-installed / fast-iteration / profile-lock) don't cover it. Add an
      accessibility / focus-preserving opt-out, or an isolated/headless path
      that doesn't foreground a window. Surfaced 2026-05-30.
- [ ] **Simplify Skill testing harness via Workflows** — explore whether the
      hand-wired worktree-sync test rig (per-skill `tmp_skill_worktree` conftest
      fixtures) can be replaced with `Workflow`-orchestrated fan-out:
      deterministic pipeline stages spawning per-skill test agents with
      structured pass/fail output, cutting bespoke conftest scaffolding.
- [ ] **`/visual-aid` HTTP shutdown endpoint** — add a programmatic shutdown
      route to `/visual-aid`'s local preview/verification server so it can be
      stopped cleanly (e.g. on verification teardown) instead of relying on a
      signal-kill or a lingering process. Deferred second half of the
      `roadmap-visual-atlas-shutdown-endpoint` worktree; follow-up PR after
      `/atlas` PR #80 merges.

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
- [x] **Approved** and listed in the community marketplace
      (`anthropics/claude-plugins-community`) — live at v1.12.0
- [ ] Versioned releases with CHANGELOG entries per skill
- [ ] Per-skill quickstart docs and usage examples
- [ ] **Break down the `docs/index.html` mono-file** — expand `docs/`
      into per-section components, potentially via Flutter (web) instead of
      a single monolithic page. Surfaced 2026-06-26 when the two-tab
      `index.html` (claude-damn overview + rtk evaluation) grew large.

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
- [ ] **Harden `/lets-make-a-skill` eval-subagent dispatch** — eval subagents
      that *simulate* a test agent must run as pure roleplay — no real tool
      calls, no file reads. The `/task-list` iteration-2 build hit subagents
      exploring the real repo and contaminating transcripts; a hardened 'no real
      tools' preamble fixed it on re-run. Bake that preamble into the skill's
      RED/GREEN subagent-dispatch instructions.

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

## Phase 6 — Skill-chain orchestration & enforcement

Beyond individual skill quality (Phases 2 / 5), Phase 6 tackles enforcement
across multi-skill chains — how the harness guarantees that a `/listen`-wrapped
prompt actually invokes every referenced skill, and how SME (subject-matter
expert) Skills can graduate to SME Agents that supervise compositional flows.

- [ ] **`/listen` enforcement hardening** — strengthen `/listen` so it cannot
      silently drop a referenced skill from the chain. Two candidate paths:
      (1) **hook-based** — PreToolUse hook on `Skill` calls inside a
      `/listen`-wrapped turn, tracking referenced-vs-invoked skills and
      blocking end-of-turn until the checklist is complete;
      (2) **agent-based** — once SME (subject-matter-expert) Skills mature
      enough, graduate them to SME Agents that supervise multi-skill
      compositional flows. Triggered by 2026-05-03 `/listen` chain misfire:
      `/listen "/visual-aid from /legalzoom:review-contract of [URL]"` skipped
      `/visual-aid` because the prior skill produced a complete-looking
      markdown deliverable; the rationalization counter table in `/listen`
      doesn't yet cover the analysis→transformation chain pattern.

- [ ] **Goodwill-rule enforcement hooks** — a versioning-bump warn hook
      (ROADMAP mark-off without a manifest bump), and extend
      `block-inline-scripts` to detect inline interpreters (`python3 <<`,
      `node -e $'…\n'`). Each via TDD. Surfaced by rules-followability discovery
      (D13 / D12). (`rm` and `git commit` are already enforced via
      `settings*.json` deny rules — not hooks, so dropped from this item.)

- [ ] **Extend `block-inline-scripts` caps to `chrome-devtools` MCP
      `evaluate_script`** — subagents frequently run inline JavaScript via
      `plugin:chrome-devtools-mcp:chrome-devtools evaluate_script` that far
      exceeds the 400-char / 4-separator caps (`MAX_COMMAND_LENGTH` /
      `MAX_STATEMENT_COUNT`) enforced for Bash. These invocations are MCP
      tool calls, so register the PreToolUse hook on the MCP tool name
      (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__evaluate_script`)
      and cap the `function` argument the way `command` is capped for Bash.
      Decide whether the cap is same-size or a larger dedicated limit
      (browser automation legitimately needs longer snippets). Via TDD, like
      the sibling inline-interpreter item above.

### `*-tdd-cat` family — TDD execution-mode axis

- [x] **A/B TDD execution-mode axis across the nine `*-tdd-cat` compositions**
      — Mode A (split-phase: one RED/GREEN/REFACTOR phase per subagent) vs
      Mode B (micro-cycle: full `/tdd` loop inside each subagent), asked as a
      **third question** in `/cat`'s ONE combined pre-dispatch
      `AskUserQuestion`. Canonical definition + never-default-silently guard in
      `skills/tdd-cat/SKILL.md`, referenced by the other eight; `/cat`
      untouched (it serves non-TDD compositions). Structural suite
      `tests/skills/tdd_cat/` (74 tests, RED→GREEN); RED pressure baseline
      captured the silent-default rationalization ("I decided it myself" under
      dispatch-overhead pressure); GREEN re-probe surfaced all three axes in
      one combined call.
      Completes the tdd+cat family arc (`/tdd` PR #83 → `/cat` PR #89 → this)
      — operator-designated MAJOR ⇒ **v2.0.0**. Shipped 2026-07-18.

### `/atlas` — session-survey skill

- [x] **`/atlas`** — composes `/tesseract` + `/checkpoint-resume` + `/visual-aid`
      into a single "where am I, what have I done, what's next" survey page.
      Single-anchor by default (auto-detected from `cwd`/branch); `--anchor
      <name>` for explicit scope; `--all` for multi-anchor survey across every
      shelf. Output: HTML only, written to `~/.visual-aid/atlas-<slug>.html`.
      Read-only by design (no shelf or bulk-beings writes), like
      `/tesseract --visual`. Concept card already rendered at
      `~/.visual-aid/visual-aid-atlas.html` (2026-04-26) — that page is the
      spec. Shipped via PR #80 (2026-06).

- [ ] **Future exploration — per-project sections in `/atlas --all` mode.**
      v1 `--all` drops the project-scoped sections (git state, CHECKPOINT,
      TaskList) because those are 1:1 with the cwd, not with each anchor.
      Two alternatives surfaced during 2026-04-26 brainstorm Q4 for later
      exploration:
      - **Option 2 — cwd-scoped:** keep one project section in `--all` mode,
        sourced from the current cwd's git/checkpoint/tasks; render it once
        above the per-anchor shelf cards. Cheap to implement; honest about the
        scope (one project, many anchors).
      - **Option 3 — per-anchor → project mapping:** maintain an
        `anchor → project-root` index and render a project section per anchor
        in `--all` mode. Most informative but requires a new persistent
        mapping (where does it live? who writes it?) and a migration path for
        existing shelves. Defer until a concrete need surfaces.

### `/visual-aid` — server lifecycle (Lighthouse SOP)

- [ ] For `/visual-aid` (or `/visual-aid --serve`) add a Python server endpoint
      to safely kill the local audit server without running any `kill*` bash
      commands. Surfaced 2026-04-26: Lighthouse rejects `file://` URLs
      (`INVALID_URL`), forcing a `python3 -m http.server` fallback that we then
      have to `pkill` — fragile (one of those calls failed exit 144) and not
      portable. Replace with an HTTP shutdown endpoint that `httpd.shutdown()`s
      from a worker thread.
