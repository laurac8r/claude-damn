# /checkpoint-save — worktree-teardown dual-write fix — eval rollup

- **Skill:** `skills/checkpoint-save/SKILL.md`
- **Branch:** `skill/checkpoint-save-worktree-teardown` (claude-damn active-dev)
- **Test case:** `eval-worktree-teardown` — agent runs `/checkpoint-save` in a
  linked git worktree about to be `git worktree remove`d; PASS = a durable copy
  of the checkpoint survives teardown (exists at the main checkout's
  `.checkpoints/<slug>.md`).

## Results

| Iteration | baseline quant | with-skill quant | with-skill pressure               |
| --------- | -------------- | ---------------- | --------------------------------- |
| 1         | 0/5 (0%)       | (interrupted)    | LEAKS — detection-failure exploit |
| 2         | 0/5 (0%)       | 5/5 (100%)       | HOLDS — 9 angles probed, no leak  |

## RED (iteration 1)

Baseline 0/5: Step 5 writes `CHECKPOINT.md` at CWD only; Step 4's archive fires
only for a _pre-existing_ checkpoint, not the new one — so a fresh checkpoint in
a teardown-bound worktree is lost. Iron Law satisfied.

## Rationalizations countered (Step 5b table)

1. "Step 5 says write at CWD — I followed exactly"
2. "Step 4 archive only fires for a pre-existing checkpoint"
3. "CHECKPOINT.md is a per-worktree file, belongs at CWD"
4. "/checkpoint-resume reads CWD, so CWD is all that matters"
5. "Detection failed, so I left it CWD-only to be safe" (iteration-1 pressure
   leak — `git rev-parse --show-toplevel` failure)

## Fix shipped

- New **Step 5b** — when CWD is a linked worktree (`TOPLEVEL` !=
  `dirname(COMMON_DIR)`), mirror the just-written checkpoint to
  `$ARCHIVE/<slug>.md` under the main checkout, surviving teardown.
- Unresolved detection → mirror anyway (never skip on ambiguity).
- `cp` exit code verified (parity with Step 4's `mv` check — closes a
  silent-failure gap flagged in iteration-2 pressure).
- Step 8 footer gains a linked-worktree resume line; Invariant #4 added; Step 7
  report notes the mirror.

**Note:** this branch also carries a sync — claude-damn's `checkpoint-save` was
stale vs the canonical `~/.claude/` copy (missing Case D + Step 8). The
canonical version was synced in first (+166 lines), then the fix applied on top.

**Verdict:** iteration-2 passes both GREEN criteria (quant 5/5 > 0% baseline,
pressure HOLDS). Ship.
