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
engineering rules that apply to every clone. If you disagree with a rule
here, edit it — the file is yours. If you disagree with a rule in
`CLAUDE.md`, open a PR.

## Git commits [policy] [soft]

- The operator handles `git commit` (and variants) themselves. Agents may
  stage files with `git add` and prepare commit messages, but stop short of
  committing.
- One commit per file — or per script/test pair — for atomic, reviewable
  history.

## Model routing [default] [soft]

- Sonnet for config edits, dotfile management, short exploratory sessions
  (<10 turns), git operations, file scaffolding, read-heavy research.
- Opus for multi-file refactors with cross-cutting concerns, subtle runtime
  bugs, designing new APIs or data models, and tasks requiring deep
  contextual reasoning across >3 files.
- Avoid short Opus sessions for trivial tasks — cache-creation cost
  (~$0.15-0.35) dominates.

## Subagent delegation [default] [soft]

- In sessions exceeding 20 turns, aim to delegate ≥30% of turns to
  Sonnet/Haiku subagents. File reads, glob/grep searches, test execution,
  boilerplate generation, and commit preparation are all subagent-appropriate.

## Worktrees [policy] [soft]

- Isolation lives at `.worktrees/<slug>/` (hidden, gitignored).
- `CHECKPOINT.md` at worktree root is also gitignored — don't `git add` it.
  <!-- hard in practice: a stray commit leaks session state into branch history -->

## Cost tracking cadence [default] [soft]

- Run `/cost_` after multi-step tasks to log the session's spend.
- Run `/cost-opt` periodically to compact logs and surface optimization
  suggestions.

## Batch operations [default] [soft]

- Group related work into a single session; read all necessary context
  upfront before executing writes, to minimise context-switching tokens.

## SDK docs [default] [soft]

- Prompt the operator for API docs or type stubs for external SDKs.
- If none are supplied, generate your own and reference them from the
  project going forward.
