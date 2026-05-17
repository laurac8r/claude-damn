<!--
Copy this file to rules/PERSONALIZATION.md in your clone and edit freely.
The real file is gitignored; your clone can diverge without merge pain.

Tags:
  [default] — nudge; override freely
  [policy]  — local law; violations should be corrected
  [soft]    — annoyance if violated
  [hard]    — safety / correctness (reserved; hard rules stay in CLAUDE.md)
-->

# Personalization

Operator-workflow preferences for this clone. `CLAUDE.md` holds general
engineering rules that apply to every clone. If you disagree with a rule here,
edit it — the file is yours. If you disagree with a rule in `CLAUDE.md`, open a
PR.

## Git commits [policy] [soft]

- The operator handles `git commit` (and variants) themselves. Agents may stage
  files with `git add` and prepare commit messages, but stop short of
  committing.
- One commit per file — or per script/test pair — for atomic, reviewable
  history. Source + matching test = ONE combined message, not two.
- PyCharm is the operator's default commit UI — prepare per-file messages that
  paste cleanly, no CLI staging dances.

### Commit message presentation [policy] [soft]

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

## Model routing [policy] [soft]

- Sonnet for config edits, dotfile management, short exploratory sessions (<10
  turns), git operations, file scaffolding, read-heavy research.
- Opus for multi-file refactors with cross-cutting concerns, subtle runtime
  bugs, designing new APIs or data models, and tasks requiring deep contextual
  reasoning across >3 files.
- Avoid short Opus sessions for trivial tasks — cache-creation cost
  (~$0.15-0.35) dominates.
- **No Opus subagents.** Every `Task` dispatch MUST use `model=sonnet` or
  `model=haiku`. `/batch` built-in is the only override — hard-enforced by
  PreToolUse hook `~/.claude/hooks/block_opus_subagent.py`. Manual override
  outside `/batch`: env `CLAUDE_BATCH_MODE=1` or `[BATCH_OVERRIDE]` sentinel in
  the prompt/description.

## Subagent delegation [default] [soft]

- In sessions exceeding 20 turns, aim to delegate ≥30% of turns to Sonnet/Haiku
  subagents. File reads, glob/grep searches, test execution, boilerplate
  generation, and commit preparation are all subagent-appropriate.

## /cat cadence [default] [soft]

- Prefer `/cat` (and compositions `/super-cat`, `/duper-tdd-cat`,
  `/super-duper-cat`, etc.) as the default subagent-dispatch mechanism. Claude
  Max daily token limits apply even on Max plans — subagent-parallel work keeps
  the main Opus session available for architectural reasoning.
- Rule of thumb: in >20-turn sessions, ≥30% of turns should be delegated.
  Aggressive delegation for reads/greps/tests/scaffolding is cheap insurance
  against mid-session rate limits.

## Worktrees [policy] [soft]

- Isolation lives at `.worktrees/<slug>/` (hidden, gitignored).
- `CHECKPOINT.md` at worktree root is also gitignored — don't `git add` it.
    <!-- hard in practice: a stray commit leaks session state into branch history -->

## Cost tracking cadence [default] [soft]

- Run `/cost_` after multi-step tasks to log the session's spend.
- Run `/cost-opt` periodically to compact logs and surface optimization
  suggestions.

## Batch operations [default] [soft]

- Group related work into a single session; read all necessary context upfront
  before executing writes, to minimise context-switching tokens.

## SDK docs [default] [soft]

- Prompt the operator for API docs or type stubs for external SDKs.
- If none are supplied, generate your own and reference them from the project
  going forward.

## Bash Command Style [default] [policy]

- Use single-purpose bash calls; avoid chaining multiple statements with `&&`,
  `;`, or `|` that may trip the block-inline-scripts hook.
- Split multi-step shell work into separate Bash tool calls (parallel where
  possible).

## Worktree & Checkpoint Discipline [default] [hard]

- Always work inside the designated worktree for the active PR; never edit
  ROADMAP.md or shipping files from the main checkout.
- After any meaningful progress (PR shipped, task batch done, before pausing),
  save a fresh checkpoint/handoff file before yielding.
- On resume, read the latest checkpoint first; do NOT prompt with
  AskUserQuestion unless the checkpoint is ambiguous.

## Debugging Discipline [default] [policy]

- Before attempting a fix on a hanging/failing test, confirm the root cause
  first (use the systematic-debugging skill if available).
- Do not stash/auto-merge across more than one fix attempt; if 2 attempts fail,
  stop and re-diagnose.
- Never write one-off scripts to /tmp for reusable logic — build it as a tested
  module via /tdd-cat instead.

## File deletion [policy] [hard]

- NEVER use `rm` (or any variant: `rm -rf`, `rm -f`, globs). ALWAYS use `trash`
  (`/usr/bin/trash` on macOS) so deletions are recoverable from the system
  Trash. Applies to files, directories, and globs — no exceptions for "empty"
  or "obviously safe" targets. If `trash` is unavailable, stop and ask.

## Verification announcements [policy] [soft]

- When claiming "done" / "passing" / "complete," state concrete numbers
  explicitly (test count, URL count, line delta, tool counts). Don't assume
  the operator saw the pytest tail. Evidence before assertions.

## External state freshness [policy] [soft]

- Re-fetch numbers (staged count, HEAD, file size, branch state) before citing
  them — operator works in parallel sessions and external state decays
  silently. Earlier-session snapshots ≠ current truth.

## /visual-aid save path [policy] [soft]

- Save `/visual-aid` outputs to `~/.visual-aid/` not `/tmp/` — durable archive;
  /tmp wipes on reboot. Override the skill's documented `/tmp` default unless
  the operator explicitly asks for ephemeral.

## /tesseract bookend [default] [soft]

- Write a TaskList before any `/tesseract`, and resume from it on exit.
  `/tesseract` is reference, not redirect — don't let it pull focus off the
  current task queue.

## Skill invocation literalness [policy] [soft]

- A bare `/skill-name` (no backticks) in user input or anchor text = invocation
  directive, even inside `/tesseract` anchor brackets or `/listen` lists.
  Backticks-only (`` `/skill-name` ``) means "content reference" — do NOT
  invoke.

## Test layout [policy] [soft]

- Tests live under `tests/skills/<skill>/{helpers,smoke,pressure,performance}/`.
  Never under `skills/<skill>/tests/`, never flat under `tests/smoke/` etc.
  Per-skill subdirs collapse the taxonomy into one discoverable place.

## Versioning Discipline [policy] [soft]

- When a `ROADMAP.md` checklist item is marked off in any project, **always
  bump version numbers** in every authoritative manifest
  (`.claude-plugin/plugin.json`, `pyproject.toml`, `package.json`,
  `Cargo.toml`, etc.) per [Semantic Versioning](https://semver.org/).
- **MAJOR** — finishing a Project roadmap **Phase**.
- **MINOR** — finishing a single Project roadmap **Item** within a Phase.
- **PATCH** — minor edits, renames, or docs-only updates (`ROADMAP.md`,
  `README.md`, `CHANGELOG.md`, etc.).
- Bump every manifest in lockstep; update `CHANGELOG.md` to match. Stage
  alongside the ROADMAP edit; don't commit.
- The bump is **not optional** — even tiny PATCH bumps carry signal.
- Multi-tier PRs: highest tier wins (MINOR > PATCH; MAJOR > MINOR).
