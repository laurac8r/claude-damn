<!--
Copy this file to rules/PERSONALIZATION.md in your clone and edit freely.
The real file is gitignored; your clone can diverge without merge pain.

Tag scheme + editing conventions are documented in the "How to edit these
rules" section below (not in this comment) so they stay visible in the rendered
file.
-->

# Personalization

Operator-workflow preferences for this clone. `CLAUDE.md` holds general
engineering rules that apply to every clone. If you disagree with a rule here,
edit it — the file is yours. If you disagree with a rule in `CLAUDE.md`, open a
PR.

## How to edit these rules

**One tag per rule**, from this ordered ladder (how hard a violation is):

- **`[nudge]`** — default behavior; deviate freely with a stated reason.
- **`[policy]`** — local law; correct violations when you notice them.
- **`[hard]`** — safety / correctness; never violate.

Absence of `[hard]` sets how hard to *correct* a violation — **not** whether the
rule applies. Every rule applies.

**Template** for a new rule (copy, fill the `<slots>`):

```
## <Rule name> [tag]

- <imperative directive — what to do, with a concrete trigger>
- <exception or how-to-apply, if any>
```

**Conventions:**

- Exactly one bracket tag per *rule* heading — no double tags. (Meta /
  structural headings — like this "How to edit" one — carry no tag.)
- A rule that must also bind **subagents** carries `[binds:subagents]` after its
  tag. Subagents do not reliably inherit this file, so such a rule also belongs
  in CLAUDE.md's **Subagent Preamble** (paste-into-every-dispatch digest).
- `[hard]` rules are grouped first, then `[policy]`, then `[nudge]`.
- `CLAUDE.md` owns cross-clone **engineering law**; this file owns
  **operator-workflow preferences**. Don't duplicate a rule across both — keep
  it in its owner and point with "(see `CLAUDE.md › <section>`)".
- **Exception:** a `[hard]` safety rule (File deletion, Git commits) MAY be
  restated in full in both files — there, subagent reachability outweighs the
  drift risk; keep the two copies in sync by hand.

**Index:** File deletion · Git commits · Commit message presentation · /pause
full → always /checkpoint-save · Model routing · Subagent delegation & /cat cadence ·
Bash command style · Worktree & checkpoint discipline · Debugging discipline ·
Interruption / rejection semantics · Verification announcements · External state
freshness · /visual-aid save path · /tesseract bookend · Skill invocation
literalness · active-dev / canonical isolation · Versioning discipline · Cost
tracking · Batch operations · SDK docs · Mid-flow task lists · Test layout.

---

<!-- ── [hard] — never violate ───────────────────────────────────────────── -->

## File deletion [hard] [binds:subagents]

- NEVER use `rm` (or any variant: `rm -rf`, `rm -f`, globs). ALWAYS use `trash`
  (`/usr/bin/trash` on macOS) so deletions are recoverable from the system
  Trash. Applies to files, directories, and globs — no exceptions for "empty" or
  "obviously safe" targets. If `trash` is unavailable, stop and ask.
- **Enforced** by deny rules in `settings.local.json` (`Bash(rm *)` /
  `Bash(* rm *)` / `Bash(*/rm *)`) — this is NOT goodwill. Don't try to route
  around the block (a wrapper script, a renamed binary, `find -delete`): the
  rationale is recoverability — `trash` is a one-click restore, `rm` is not.

## Git commits [hard] [binds:subagents]

- The operator handles `git commit` (and variants) themselves. Agents may stage
  files with `git add` and prepare commit messages, but **NEVER run the commit**
  — no `git commit`, `git commit --amend`, `git commit -m`, or any variant. No
  hedge: stage and prepare the message, then stop.
- One commit per file — or per script/test pair — for atomic, reviewable
  history. Source + matching test = ONE combined message, not two.
- PyCharm is the operator's default commit UI — prepare per-file messages that
  paste cleanly, no CLI staging dances.
- Delegation may prepare a commit **message** (never the commit itself).
- **Enforced** by the `Bash(*git commit*)` deny rule in `settings.json` — NOT
  goodwill. Don't try to route around it: the operator owns commit timing,
  granularity, and message; a stray agent commit means history surgery.

### Commit message presentation [policy]

When recommending a commit message, ALWAYS lead with these indicators so the
operator can paste from a known location:

```
**Worktree:** <absolute path to the worktree>
**Branch:** <branch name>
**Staged:** <file path> (+N lines / +N/-M lines / N edits)
```

…then the suggested commit message in a fenced block. When N commits share
files, render hunks→message→rule per commit; never table-then-collapsed-
messages.

**Spacing (operator-confirmed).** State **Worktree** and **Branch** once at the
top of a multi-commit batch — not per commit (exception: a batch spanning
multiple repos/worktrees states them per repo). For each commit: a `**Staged:**`
line (files + `+N/-M` counts, `·`-separated), then ONE blank line, then the
message in a fenced block; put TWO blank lines between consecutive commit blocks.
Close every message with the `Co-authored-by: Claude Code - Opus 4.8 (1M)` tail
(from `~/.git-commit-template.txt`). This spacing is what makes a long batch
scannable and copy-pasteable.

<!-- ── [policy] — local law, correct violations ─────────────────────────── -->

## /pause full → always /checkpoint-save [policy]

- Every `/pause full` invocation MUST run `/checkpoint-save` as part of the
  closeout — not just `/remember`. `/check-yourself`'s Step 3 already calls it,
  but a "full" pause is the highest-stakes boundary in the session: never skip
  the explicit checkpoint write, even if the session feels light or the cwd
  isn't a git repo (in which case `cd` to the most-relevant active worktree
  before invoking, and write the `CHECKPOINT.md` there).
- Observable check: after a `/pause full`, a `CHECKPOINT.md` (or
  `.checkpoints/<slug>.md`) must actually exist on disk.

## Model routing [policy]

- See `CLAUDE.md › Cost Optimization & Model Routing` — it owns the full policy,
  including the **No-Opus-subagents** rule and its two named exceptions
  (multi-phase reviewer dispatch; 3-tier Haiku+Sonnet+Opus fanout for
  hard/contentious tasks). Single source of truth lives there; don't restate it
  here.

## Subagent delegation & /cat cadence [policy]

- **Trigger + check (not an aspiration).** In any session past **20 assistant
  turns** (a "turn" = one of your replies), *before you do a read, grep,
  test-run, or boilerplate-generation task yourself*, dispatch it to a
  Sonnet/Haiku subagent — UNLESS dispatch overhead clearly exceeds the work
  (e.g. a single short read) or a memory records that subagents are blocked here
  for that tool. "Aim to" is not a licence to skip; the trigger is the rule.
- Prefer `/cat` (and `/super-cat`, `/duper-tdd-cat`, `/super-duper-cat`) or
  `/dispatching-parallel-agents` as the dispatch mechanism. Claude Max daily
  token caps apply even on Max plans — keeping the main Opus session free for
  architectural reasoning is the point.
- Consequence, not quota: this trigger lands ≥30% of turns delegated in a
  >20-turn session. Don't ship busywork to a subagent just to hit a percentage.

## Bash command style [policy] [binds:subagents]

- Use single-purpose bash calls; avoid chaining multiple statements with `&&`,
  `;`, or `|` that may trip the block-inline-scripts hook. Split multi-step
  shell work into separate Bash calls (parallel where possible).
- **`cd` persistence model.** Claude Code's Bash harness checks the parent-shell
  cwd at command exit and resets it if it lands outside an **anchor** directory.
  The anchor is the **session's primary working directory** (the dir the session
  was launched in), NOT `$HOME` — the two coincide only when you launch from
  your home directory.
   - **At or below the anchor subtree** — cwd PERSISTS across separate Bash
     calls. `cd subdir` in one call, a separate `pwd` next returns the subdir; a
     later `cd ..` back to the anchor itself also persists.
   - **Above the anchor** (`..` past it, `~`, `/tmp`, `/etc`, `/`) — the harness
     emits `Shell cwd was reset to <anchor>` and resets. Mechanism-agnostic:
     `;`, `&&`, `||`, brace groups `{ …; }`, `eval`, output redirects all trigger
     it. Only subshell forks (`|`, `(…)`, `&`) skip the reset — but they also
     don't move the parent shell's cwd, so they're a dead end above the anchor.
   - The reset applies to your own `! ` TUI commands too, not just agent calls.
- **Defaults stay cwd-agnostic** for portability and to dodge the chained-`cd
  <dir> && <cmd>` permission gate:
   - **File ops** (Read / Edit / Write / Glob / Grep): absolute paths.
   - **Cross-repo git**: `git -C <abs-path> <subcommand>`.
   - **Tools that hard-require cwd above the anchor** (e.g. `uv run`, `pytest`,
     `flutter test` against `/tmp/` worktrees): bundle inline in ONE Bash call as
     `cd <abs-path>; <tool> <args>` — the reset fires after the call returns, but
     the bundled work completes in the right cwd first.

## Worktree & checkpoint discipline [policy]

- Isolation lives at `.worktrees/<slug>/` (hidden, gitignored). `CHECKPOINT.md`
  at a worktree root is also gitignored — don't `git add` it.
- Always work inside the designated worktree for the active PR; **never edit
  `ROADMAP.md` or shipping files from the main checkout.**
- After any meaningful progress (PR shipped, task batch done, before pausing),
  save a fresh checkpoint/handoff before yielding.
- On resume, read the latest checkpoint first; do NOT prompt with
  `AskUserQuestion` unless the checkpoint is ambiguous.

## Debugging discipline [policy]

- Before attempting a fix on a hanging/failing test, confirm the root cause
  first (use the systematic-debugging skill if available).
- Do not stash/auto-merge across more than one fix attempt; if 2 attempts fail,
  stop and re-diagnose.
- Never write one-off scripts to `/tmp` for **reusable** logic — build it as a
  tested module via `/tdd-cat`. (Throwaway, single-run scripts in `/tmp` are
  fine and are the prescribed path — see `CLAUDE.md › No Inline Non-Bash
  Scripts`. The boundary: reusable ⇒ tested module; single-use ⇒ `/tmp`
  throwaway.)

## Interruption / rejection semantics [policy]

- Tool-call rejection ≠ disagreement. A rejection often isn't "I disagree." Ask
  the operator what they want instead; don't silently drop the step or re-attempt
  the same call.
- User interruptions usually mean "pause / redirect / shift pacing," not "the
  prior approach was wrong." Ask before inferring intent.

## Verification announcements [policy]

- When claiming "done" / "passing" / "complete," state concrete numbers
  explicitly **in the same message** (test count, URL count, line delta, tool
  counts). Don't assume the operator saw the pytest tail. Evidence before
  assertions — a bare "all passing" with no adjacent number is a violation.

## External state freshness [policy]

- Re-fetch numbers (staged count, HEAD, file size, branch state) before citing
  them — the operator works in parallel sessions and external state decays
  silently. Earlier-session snapshots ≠ current truth.

## /visual-aid save path [policy]

- Save `/visual-aid` outputs to `~/.visual-aid/`, not `/tmp/` — durable archive;
  `/tmp` wipes on reboot. Override the skill's documented `/tmp` default unless
  the operator explicitly asks for ephemeral.

## /tesseract bookend [policy]

- Write a TaskList before any `/tesseract`, and resume from it on exit.
  `/tesseract` is reference, not redirect — don't let it pull focus off the
  current task queue.

## Skill invocation literalness [policy]

- A bare `/skill-name` (no backticks) in user input or anchor text = invocation
  directive, even inside `/tesseract` anchor brackets or `/listen` lists.
  Backticks-only (`` `/skill-name` ``) means "content reference" — do NOT invoke.

## active-dev / canonical isolation [policy] [binds:subagents]

- See `CLAUDE.md › Skill Development & Testing` and `› Public (Open-source) vs
  Private (Proprietary)` — CLAUDE.md owns the full leak-boundary (the
  disallowed/permitted path lists). This rule binds subagents, so its one-line
  guard also lives in the Subagent Preamble.
- Operator-specific: skill writing/updating happens in active-dev worktrees,
  never on `main`, never in canonical; skill *testing* spins off a `/tmp/`
  worktree synced via a conftest fixture — never test against the canonical
  install.

## Versioning discipline [policy]

- When a `ROADMAP.md` checklist item is **marked off** in any project, bump
  version numbers in every authoritative manifest (`.claude-plugin/plugin.json`,
  `pyproject.toml`, `package.json`, `Cargo.toml`, …) per
  [SemVer](https://semver.org/): **MAJOR** = finished a Phase; **MINOR** =
  finished an Item within a Phase; **PATCH** = docs-only / renames. Multi-tier:
  highest tier wins.
- **A hotfix or bug fix ALWAYS bumps `PATCH` and ALWAYS gets a `CHANGELOG.md`
  entry — even when it closes no `ROADMAP.md` item.** A ROADMAP mark-off is
  *one* trigger for a bump, not the only one. Shipping a behavior change with no
  version delta and no changelog line leaves consumers unable to tell which
  build carries the fix, and leaves the fix invisible in release notes. When the
  fix closes no checklist item: bump PATCH, write the CHANGELOG entry, skip the
  ROADMAP edit.
- Bump every manifest in lockstep; update `CHANGELOG.md` to match; stage
  alongside the ROADMAP edit (when there is one); don't commit. **The bump is
  not optional** — hence `[policy]`, not a nudge. (Adding a *new unchecked* item
  is not a mark-off and needs no bump.)

<!-- ── [nudge] — default behavior, deviate with a reason ─────────────────── -->

## Cost tracking [nudge]

- **Only when the operator is NOT on Claude Max** (Max = skip both): run `/cost_`
  after multi-step tasks to log spend, and `/cost-opt` periodically to compact
  logs + surface optimization suggestions. One Max flag gates the whole cadence.

## Batch operations [nudge]

- Group related work into a single session; read all necessary context upfront
  before executing writes, to minimise context-switching tokens.

## SDK docs [nudge]

- Prompt the operator for API docs or type stubs for external SDKs. If none are
  supplied, generate your own and reference them from the project going forward.

## Mid-flow task lists [nudge]

- At phase transitions in long flows, render the remaining queue as a ✅/⏭️
  numbered list (a re-anchor for the reader). Complements TaskCreate, doesn't
  replace it.

## Test layout [nudge]

- Tests live under `tests/skills/<skill>/{helpers,smoke,pressure,performance}/`.
  Never under `skills/<skill>/tests/`, never flat under `tests/smoke/` etc.
  Per-skill subdirs collapse the taxonomy into one discoverable place.
