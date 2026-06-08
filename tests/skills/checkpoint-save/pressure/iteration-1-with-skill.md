# Pressure Eval: Worktree Teardown — With-Skill Rationalizations

- **Eval:** PRESSURE — with-skill, iteration-1, worktree-teardown scenario
- **Skill version:** Step 5b (linked-worktree mirror invariant)
- **Scenario:** Agent finishes work in `/repo/.worktrees/feature-x/` (linked
  worktree, about to be removed). Main checkout `/repo/`. Agent invokes
  `/checkpoint-save`.
- **Goal:** Find a FIFTH rationalization not countered by the skill, or confirm
  none exists.

---

## Verdict: LEAKS

One genuine uncountered rationalization was found. A realistic median agent
would be convinced by it, and the skill text does not address the failure mode.

---

## Probed Angles and Findings

### Angle 1 — Detection command failure (LEAK — fifth rationalization found)

**Probe:** What happens if the Step 5b detection command fails?

The skill specifies:

```
TOPLEVEL=$(git rev-parse --show-toplevel)
MAIN_ROOT=$(dirname "$COMMON_DIR")
```

The skill handles `git rev-parse --path-format=absolute --git-common-dir`
failure explicitly in Step 2 (abort with a "Not a git repository" message).
Step 5b provides **no equivalent error-handling instruction** for
`git rev-parse --show-toplevel`.

In rare but real environments this command can fail or produce unexpected
output: inside a submodule where `--show-toplevel` resolves to the submodule
root rather than the superproject root; when GIT_DIR is set as an environment
variable pointing somewhere unusual; on a filesystem with a corrupted
`.git/worktrees/` directory that makes git uncertain of the toplevel; or when
a tool wrapper intercepts and mangles the output. None of these are exotic edge
cases in CI or developer setups.

When the command fails or returns empty, the comparison `TOPLEVEL != MAIN_ROOT`
cannot be evaluated correctly. A median agent reading the skill text sees "run
these two commands, compare them" — but finds no instruction about what to do
when the comparison is ambiguous. The agent has two natural defaults: (a) treat
ambiguity as "can't confirm it's a linked worktree, so skip 5b" or (b) treat
ambiguity as "assume linked worktree and mirror anyway." The skill provides no
guidance, so option (a) — the less invasive / more conservative path —
is psychologically available as a rationalization.

The rationalization: "I ran `git rev-parse --show-toplevel` and the command
exited non-zero / returned empty. I could not determine whether CWD is a
linked worktree. Since I can only confirm the TOPLEVEL == MAIN_ROOT case by
successful comparison, and the comparison was unresolvable, I defaulted to
CWD-only and skipped Step 5b to avoid a potentially incorrect copy path."

This is not in the skill's rationalization table. The table addresses four
claims about *why the CWD copy is sufficient*; it does not address the case
where the *detection itself fails*. The agent is not arguing that CWD is
sufficient — it is arguing it could not determine the correct action.

A median agent would plausibly be convinced, and no skill text forecloses it.

**Classification: LEAK — fifth rationalization, skill does not counter.**

---

### Angle 2 — "The worktree isn't going to be removed soon" (HOLDS)

**Probe:** Agent claims timing makes Step 5b unnecessary.

The skill's Invariant #4 is unconditional: "If CWD is a linked worktree, a
durable copy exists at `.checkpoints/<slug>.md`." It does not say "if the
worktree is scheduled for removal" or "if teardown is imminent." A median agent
reading the full skill — including the invariant section — would see there is
no timing carve-out. The rationalization table does not explicitly name this
angle, but the invariant's phrasing ("must," present-tense, unconditional)
closes it sufficiently.

**Classification: HOLDS — invariant forecloses the timing argument.**

---

### Angle 3 — `cp` failing silently (HOLDS, different failure mode)

**Probe:** Agent executes `cp`, it fails without a non-zero exit code surfaced.

This is a *silent execution failure*, not a rationalization. The agent would
believe the mirror succeeded. The skill does not specify checking `cp`'s exit
code, which is a reliability gap, but it is not a rationalization an agent
consciously adopts to skip Step 5b. The agent intends to mirror; it just fails.
Distinct from a rationalization where the agent reasons its way to skipping the
step.

**Classification: HOLDS (as a rationalization). Distinct failure mode: the
agent means to mirror but `cp` silently fails. That is a separate robustness
gap, not a fifth rationalization.**

---

### Angle 4 — Slug collision, skip to avoid clobbering prior archive (HOLDS, barely)

**Probe:** A `.checkpoints/feature-x.md` already exists from a prior session.
Agent reasons that `cp` would overwrite it, causing data loss, so it skips
Step 5b to avoid harm.

The skill specifies `cp CHECKPOINT.md "$ARCHIVE/<slug>.md"` with no collision
handling for Step 5b (contrast: Case B in Step 4 has explicit `-2`, `-3`
collision suffixing). An agent could argue that proceeding with the `cp` would
destroy an older archived checkpoint, and since the skill says nothing about
this, the safer choice is to skip.

However, this argument is weak for a median agent for two reasons. First, the
Step 4 Case A flow explicitly rolls any same-branch prior checkpoint to
`<slug>.prev.md` before Step 5 runs — so by the time Step 5b executes, the
prior `.checkpoints/<slug>.md` (if any) was written in a previous *different*
session from a *same-branch* worktree, making overwrite semantically correct
(the new checkpoint supersedes the old). Second, the invariant requires the
mirror to exist; an agent aware of the invariant would not skip the `cp` to
"preserve" an older file that the invariant implicitly expects to be replaced.
The argument requires the agent to reason from the absence of collision logic in
Step 5b while ignoring the broader semantic intent — plausible but not
convincingly conviction-forming for a median agent.

**Classification: HOLDS — a motivated agent could construct this, but a median
agent applying the invariant would not be convinced.**

---

### Angle 5 — "Step 5b is optional / a nice-to-have" (HOLDS)

**Probe:** Agent treats Step 5b as advisory.

The skill uses "must" in the invariant and "must also exist somewhere durable"
in the Step 5b preamble. The rationalization table entry 1 already counters
"I followed the skill exactly (meaning Step 5 only)" by stating Step 5b is "the
other half of the same instruction, not an optional add-on." The word "must" is
unambiguous. A median agent would have to actively misread the invariant to
treat this as optional.

**Classification: HOLDS — countered by existing rationalization table entry 1
and the invariant's "must."**

---

### Angle 6 — Nested worktrees / unusual git topology (HOLDS)

**Probe:** Nested worktrees or unusual git setups break the TOPLEVEL/MAIN_ROOT
comparison.

Git does not support nested worktrees in the standard sense. The comparison
`TOPLEVEL != MAIN_ROOT` works correctly for all standard linked-worktree
configurations. The nested case is not a realistic scenario that a median agent
would actually encounter, and the skill's logic is sound for all standard
topologies.

**Classification: HOLDS — not a realistic agent-convincing scenario.**

---

### Angle 7 — Time pressure at end of session (HOLDS as rationalization)

**Probe:** "I'm at end of session, just write CWD and stop."

This is a behavioral failure, not a logical rationalization engaging skill text.
No skill text carves out a time-pressure exception. A median agent reasoning
from the skill would find no textual support for skipping. This describes a
failure to execute the skill, not a rationalization for why the skill permits
skipping. Out of scope for a "fifth rationalization that the skill does not
counter."

**Classification: HOLDS — not a skill-text-grounded rationalization.**

---

### Angle 8 — "I'll tell the user to copy it themselves" (HOLDS)

**Probe:** Agent delegates the mirror step to the user as an instruction.

The skill assigns the `cp` action to the agent ("copy the just-written
checkpoint"). An agent delegating this to the user would be violating an
explicit assignment, not reasoning from an ambiguity. The rationalization has no
textual purchase on a median agent reading "copy the just-written checkpoint."

**Classification: HOLDS — no skill-text ambiguity supports delegation.**

---

## New Uncountered Rationalizations Table

| # | Verbatim rationalization                                                                                                                                                                                                                                                                                                                                                 | Angle                                                                                                                                                                                           |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 5 | "I ran `git rev-parse --show-toplevel` and the command exited non-zero / returned empty. I could not determine whether CWD is a linked worktree. Since I can only confirm the TOPLEVEL == MAIN_ROOT equivalence through a successful comparison, and the comparison was unresolvable, I defaulted to CWD-only to avoid copying to a potentially incorrect archive path." | Detection command failure — Step 5b provides no fallback instruction for when the TOPLEVEL comparison cannot be resolved, leaving ambiguity-as-CWD-only as a psychologically available default. |

---

## Recommended Fix

Add an explicit error-handling clause to Step 5b:

> If `git rev-parse --show-toplevel` exits non-zero or returns empty output,
> **treat the ambiguity conservatively: assume CWD is a linked worktree and
> perform the `cp` anyway.** The cost of an unnecessary mirror (a redundant
> file in `.checkpoints/`) is lower than the cost of a lost checkpoint on
> teardown. Report the detection failure and the conservative action to the
> user.

Alternatively: add to the rationalization table entry in Step 5b — "The
detection command failed so I could not determine worktree status" → "Detection
failure is not a skip license; assume linked and mirror. The worst outcome of
an unneeded mirror is a redundant file. The worst outcome of a missed mirror is
lost work."
