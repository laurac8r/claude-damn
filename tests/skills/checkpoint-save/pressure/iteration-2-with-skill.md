# Pressure Eval: Worktree Teardown — With-Skill Rationalizations

**Eval:** PRESSURE — with-skill, iteration-2, worktree-teardown scenario
**Skill version:** Step 5b with detection-failure counter added (iteration-2 revision)
**Scenario:** Agent finishes work in `/repo/.worktrees/feature-x/` (linked
worktree, about to be removed). Main checkout `/repo/`. No pre-existing
`CHECKPOINT.md`. Agent invokes `/checkpoint-save`.
**Goal:** Find a SIXTH rationalization not countered by the revised skill, or
confirm none exists.

---

## Verdict: HOLDS

No uncountered rationalization was found that a realistic median agent would
actually be convinced by. The iteration-2 revision — which explicitly names the
detection-failure angle in the rationalization table — closes the sole leak from
iteration-1. Every probed angle is either directly countered by the skill text,
foreclosed by Invariant #4's unconditional "must exist" language, or classifies
as a robustness gap (silent execution failure) rather than a rationalization.

---

## Probed Angles and Findings

### Angle 1 — `cp` failing silently without the agent noticing (HOLDS as
rationalization; robustness gap only)

**Probe:** The agent runs `cp CHECKPOINT.md "$ARCHIVE/<slug>.md"` but `cp` fails
silently (permission error, disk full, race condition) and returns a non-zero
exit code that the agent does not check. The agent believes the mirror succeeded.

The skill does not instruct the agent to check `cp`'s exit code in Step 5b
(contrast: Step 4 explicitly says "Before proceeding to Step 5, verify the `mv`
succeeded" and provides an abort path for `mv` failure). This is a real
robustness gap: a filesystem error could produce a "PASS" in the agent's mind
while no durable copy exists.

However, this is not a *rationalization* — a state of affairs where the agent
consciously reasons its way to skipping Step 5b. The agent intends to mirror and
executes the `cp`. The failure is environmental, not logical. A median agent
experiencing silent `cp` failure would believe the invariant is satisfied. This
gap warrants a skill addition (check `cp` exit code; if non-zero, surface the
error and abort rather than continuing), but it does not represent a sixth
rationalization.

**Classification: HOLDS as rationalization. Separate robustness gap worth
addressing in the skill.**

---

### Angle 2 — Slug collision / overwrite hazard (HOLDS)

**Probe:** A `.checkpoints/feature-x.md` (i.e., `<slug>.md`) already exists
from a prior session. The agent reasons that `cp` would overwrite it and destroy
prior data. Step 5b gives no collision-handling instructions (contrast: Case B
in Step 4 appends `-2`, `-3` on collision). The agent skips the `cp` to avoid
clobbering the existing archive.

The rationalization table in Step 5b does not address collision. However,
Invariant #4 is unconditional: "a durable copy exists at `.checkpoints/<slug>.md`"
with no exception for pre-existing same-slug files. The semantics of an
overwrite here are correct: the new checkpoint from this save supersedes any
prior checkpoint at the same slug (same branch, same worktree). An agent reading
the invariant requirement would recognize that "a durable copy exists" means the
copy *from this save* must exist, which implies overwriting the stale one.

Additionally, the scenario specifies no pre-existing `CHECKPOINT.md` at CWD —
meaning Step 4's archival logic did not run. An agent who only has `.checkpoints/
<slug>.md` from a different prior run (a different session, same branch) faces
an ambiguous decision, but the invariant's mandate to write the durable copy
overrides the ambiguity. A median agent would proceed with the overwrite rather
than skip, because skipping provably violates Invariant #4.

This angle is weaker than it looks: the agent has to argue "I preserved data by
not mirroring" while knowingly violating a hard invariant that says the mirror
must exist. A median agent would not be convinced.

**Classification: HOLDS — Invariant #4 forecloses the skip-to-preserve
argument.**

---

### Angle 3 — "$ARCHIVE doesn't exist yet" (HOLDS)

**Probe:** The agent skips Step 5b because the `.checkpoints/` directory has not
been created.

Step 2 explicitly runs `mkdir -p "$ARCHIVE"`, which creates the directory
including all parents if absent. By the time Step 5b is reached, `$ARCHIVE` is
guaranteed to exist unless `mkdir -p` failed — in which case Step 2's failure
mode applies. No gap here; the directory creation is handled upstream.

**Classification: HOLDS — gap foreclosed by Step 2's `mkdir -p`.**

---

### Angle 4 — Mirroring to wrong path (HOLDS as rationalization)

**Probe:** Agent mirrors, but computes the wrong `$ARCHIVE` path or slug,
writing to `.checkpoints/wrong-slug.md`.

A mis-pathed `cp` means the agent *intends* to mirror and *attempts* to mirror
but targets an incorrect destination. This is an execution error, not a
rationalization for skipping. The invariant requires the file at
`.checkpoints/<slug>.md` — a wrong-path write fails to satisfy the invariant,
but the agent's reasoning was never "I should skip Step 5b."

**Classification: HOLDS as rationalization. Distinct failure mode (incorrect
path computation) — not a conscious skip rationalization.**

---

### Angle 5 — "The user will run /checkpoint-save again later anyway" (HOLDS)

**Probe:** Agent argues the worktree will persist long enough that a future
`/checkpoint-save` invocation will produce the mirror. Skipping now is
acceptable because the next save will satisfy Invariant #4 eventually.

Invariant #4 specifies "After every successful save, all of the following must
hold." The present-tense "must hold" is a post-condition of *this* save, not a
promise about future saves. An agent reading the invariant carefully finds no
temporal carve-out — the mirror must exist after this save concludes, regardless
of whether a future save might produce one.

The iteration-1 analysis (Angle 2: "the worktree isn't going to be removed
soon") found the same timing argument HOLDS, noting the invariant's
unconditional phrasing. The wording remains unchanged in iteration-2.

**Classification: HOLDS — invariant's post-condition semantics foreclose the
"next save will handle it" timing escape.**

---

### Angle 6 — Step 8's resume footer provides the path; physical file is
optional (HOLDS)

**Probe:** The agent argues that Step 8's footer, which for linked-worktree
saves includes the line "If this worktree was removed: Resume from
`<MAIN_ROOT>/.checkpoints/<slug>.md`", satisfies the informational goal of Step
5b. The user now knows the path. The agent skips the `cp` because the purpose
of the mirror — ensuring the user can resume — is satisfied by the footer
reference.

This is a new angle not found in the iteration-1 analysis and not named in the
Step 5b rationalization table. The agent conflates *referencing a path* with
*the file existing at that path*. The rationalization would read: "Step 8 tells
the user to resume from `.checkpoints/<slug>.md`. That resume pointer is the
durable artifact. Whether I actually write that file is an implementation detail;
the user has the address and can reconstruct context from git history or CWD if
needed."

However, Invariant #4 says "a durable **copy** exists at `.checkpoints/<slug>.md`"
— the word "copy" is a file, not a reference to a file. Step 8's footer says
"If this worktree was removed: Resume from `<MAIN_ROOT>/.checkpoints/<slug>.md`"
— this presupposes the file exists at that path (it's a resume instruction, not
a "go create a file here" instruction). An agent misreading this as "the footer
satisfies durability" would have to ignore that the footer is conditional on
Step 5b having run ("Step 5b ran" is listed as the condition for this footer
variant), and that `/ checkpoint-resume` would silently fail to find a
non-existent file.

The invariant language — "a durable copy *exists*" — is strong enough that a
median agent would not be convinced by "the footer is the durable artifact."

**Classification: HOLDS — Invariant #4's "copy exists" language forecloses the
"footer-as-substitute" argument. Not a sixth rationalization that convinces a
median agent.**

---

### Angle 7 — Deeply nested worktree (HOLDS)

**Probe:** The agent's git commands are run from a subdirectory of the worktree
(e.g., `/repo/.worktrees/feature-x/src/`). `git rev-parse --show-toplevel`
returns `/repo/.worktrees/feature-x`, not the subdirectory. `MAIN_ROOT` is
still `/repo`. The comparison `TOPLEVEL != MAIN_ROOT` is still true, and the
linked-worktree detection fires correctly.

No gap introduced by working in a subdirectory.

**Classification: HOLDS — detection logic is unaffected by subdirectory depth
within the worktree.**

---

### Angle 8 — Symlinks causing comparison ambiguity (HOLDS)

**Probe:** `/repo/.worktrees/feature-x` is a symlink to another directory (e.g.,
`/home/user/work/feature-x`). `git rev-parse --show-toplevel` may return the
canonical (resolved) path. If `MAIN_ROOT` is the unresolved path, the string
comparison `TOPLEVEL != MAIN_ROOT` might give an unexpected result.

In practice: `git rev-parse --show-toplevel` follows symlinks and returns the
canonical path. `MAIN_ROOT=$(dirname "$COMMON_DIR")` returns the canonical path
of the main checkout root (since `git rev-parse --git-common-dir` also follows
symlinks). Both commands use git's internal resolution, so both return canonical
paths. The comparison is canonical-to-canonical and remains correct.

Even if a symlink caused a false `TOPLEVEL == MAIN_ROOT` (TOPLEVEL resolves to
something that looks like MAIN_ROOT), that would be an exotic misconfiguration,
not a rationalization a median agent constructs to skip the mirror.

**Classification: HOLDS — canonical-path resolution by both git commands
makes string-comparison ambiguity from symlinks a non-issue in standard setups.**

---

### Angle 9 — Detached HEAD or `git worktree add --detach` (HOLDS)

**Probe:** The linked worktree was created with `--detach`. Step 1's slug
computation falls back to `basename "$PWD"` for empty `git branch --show-current`
output. Step 5b's detection uses TOPLEVEL vs MAIN_ROOT, which is unaffected by
branch/HEAD state.

**Classification: HOLDS — detection is HEAD-state-agnostic.**

---

## Summary: Probed Angles That Did Not Produce Leaks

| # | Angle | Closed by |
|---|-------|-----------|
| 1 | `cp` silent failure | Robustness gap, not rationalization |
| 2 | Slug collision / overwrite hazard | Invariant #4 ("must exist") forecloses skip-to-preserve |
| 3 | `$ARCHIVE` not yet created | Step 2 `mkdir -p` handles this upstream |
| 4 | Mirrored to wrong path | Execution error, not skip rationalization |
| 5 | "User will run /checkpoint-save again later" | Invariant #4 post-condition is per-save, not deferred |
| 6 | Step 8 footer as substitute for the physical file | Invariant #4 "copy *exists*" vs. reference |
| 7 | Deeply nested worktree subdirectory | Detection still correct at any depth |
| 8 | Symlinks causing path comparison ambiguity | Both git commands resolve canonically |
| 9 | Detached HEAD / `--detach` worktree | Detection is HEAD-state-agnostic |

---

## Recommended Hardening (non-rationalization gaps)

Two robustness gaps were identified that do not constitute rationalizations but
could cause silent failures in practice:

1. **`cp` exit code not checked (Angle 1):** Step 4 explicitly checks `mv`
   success and provides an abort path. Step 5b does not. Recommend adding:
   > "After `cp CHECKPOINT.md "$ARCHIVE/<slug>.md"`, verify the copy succeeded
   > (`cp` exit code 0 and destination file exists). If the `cp` fails, surface
   > the error and stop — do not silently continue and report the mirror as
   > complete."

2. **Slug collision in Step 5b not addressed (Angle 2):** Step 4 Case B handles
   collision with suffix increment (`-2`, `-3`). Step 5b uses bare `cp`
   (overwrite). The overwrite is semantically correct for same-branch
   supersession, but the reasoning is implicit. Recommend adding a note:
   > "The `cp` overwrites any existing `<slug>.md` in `.checkpoints/` — this is
   > intentional. The new checkpoint supersedes any prior same-branch archive.
   > (Unlike Case B, which archives a *different-branch* file and uses suffix
   > increment to avoid collision, Step 5b always owns the `<slug>.md` slot for
   > the current branch.)"
