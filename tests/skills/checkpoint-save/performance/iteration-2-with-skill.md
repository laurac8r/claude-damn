# Eval: `/checkpoint-save` Worktree-Teardown Scenario — Iteration 2 (with-skill)

- **Scenario:** Agent finishes work. CWD = `/repo/.worktrees/feature-x/` (linked git
worktree, about to be torn down). Main checkout = `/repo/`. No pre-existing
`CHECKPOINT.md`. Agent invokes `/checkpoint-save`.

- **PASS condition:** A durable copy exists at `/repo/.checkpoints/<slug>.md` after the skill
runs (survives `git worktree remove`).

- **FAIL condition:** Checkpoint exists only at the worktree-local `CHECKPOINT.md` (destroyed
on teardown).

---

## Trial Results

| # | Type              | Detection outcome                                              | Agent action                                                               | Result | Reason                                                                                                 |
|---|-------------------|----------------------------------------------------------------|----------------------------------------------------------------------------|--------|--------------------------------------------------------------------------------------------------------|
| 1 | Normal            | `TOPLEVEL=/repo/.worktrees/feature-x` ≠ `MAIN_ROOT=/repo`      | Writes CWD `CHECKPOINT.md`, then mirrors to `/repo/.checkpoints/<slug>.md` | PASS   | Linked worktree confirmed; skill Step 5b is unambiguous — mirror executed                              |
| 2 | Normal            | `TOPLEVEL=/repo/.worktrees/feature-x` ≠ `MAIN_ROOT=/repo`      | Writes CWD `CHECKPOINT.md`, then mirrors to `/repo/.checkpoints/<slug>.md` | PASS   | Rationalization table explicitly counters "per-worktree-file-belongs-at-CWD" dodge; agent mirrors      |
| 3 | Normal            | `TOPLEVEL=/repo/.worktrees/feature-x` ≠ `MAIN_ROOT=/repo`      | Writes CWD `CHECKPOINT.md`, then mirrors to `/repo/.checkpoints/<slug>.md` | PASS   | Rationalization table counters "checkpoint-resume-reads-CWD" rationalization; mirror executed          |
| 4 | Detection failure | `git rev-parse --show-toplevel` exits non-zero; TOPLEVEL empty | Writes CWD `CHECKPOINT.md`, then mirrors to `/repo/.checkpoints/<slug>.md` | PASS   | Skill rule explicit: "either command fails or returns empty → unresolved → do NOT skip; mirror anyway" |
| 5 | Detection failure | `git rev-parse --show-toplevel` returns empty string           | Writes CWD `CHECKPOINT.md`, then mirrors to `/repo/.checkpoints/<slug>.md` | PASS   | Rationalization table counters "detection failed so I left it CWD-only to be safe"; agent mirrors      |

---

## Overall Pass-Rate

**5 / 5 — 100%**

## Verdict

The revised skill's explicit rationalization table — which directly names and
counters all plausible skip-justifications, including the detection-failure
dodge — closes every gap that caused failures in iteration 1. The "mirror on
unresolved detection" rule, stated as a hard invariant with explicit counter to
the "safe to skip" rationalization, was sufficient to carry both detection-failure
trials to PASS without any agent hedging.
