# `/task-list` benchmark — iteration 1

**Verdict: PASS** (both GREEN gates satisfied; no REFACTOR needed.)

## Quant grid

| Eval                       | Baseline | With-skill | Delta |
| -------------------------- | :------: | :--------: | :---: |
| bare-simple                | FAIL     | PASS       | +1    |
| bare-pressure              | PASS     | PASS       | =     |
| update-noarg-reconcile     | FAIL     | PASS       | +1    |
| update-witharg-rewrite     | FAIL     | PASS       | +1    |
| display-fulllist           | PASS     | PASS       | =     |
| **Total**                  | **2/5**  | **5/5**    | **+3**|

## GREEN gates (both required)

1. ✅ **With-skill quant pass-rate strictly greater than baseline.** 5/5 > 2/5.
2. ✅ **No new rationalizations in with-skill pressure.** All 5 with-skill
   subagents executed cleanly without permission-seeking, prose-checklist
   substitutes, delete-and-recreate, or truncation echoing.

## Method

- **Model:** sonnet (per `[BATCH_OVERRIDE]`-free policy: no opus subagents).
- **Dispatch:** 5 parallel subagents per phase (1 per eval; consolidated quant
  + pressure grading from a single transcript per eval).
- **Subagent prompt:** baseline = "skill not loaded" framing; with-skill =
  SKILL.md body inlined as the loaded skill content.
- **Grading:** subagents self-grade against the eval's pass criteria; main
  agent verifies against captured transcripts.

## Held-instinct evals

The 2 baselines that already passed (bare-pressure, display-fulllist) tell us
two failure modes documented elsewhere were NOT triggered in this iteration:

- **R0 (prose-list substitute):** bare-pressure baseline correctly TaskCreated
  all 4 items despite a 20-turn session of markdown-checklist tracking. Modern
  Sonnet handles this cleanly. The skill body still pre-emptively counters R0
  in the anti-patterns block since the failure mode is documented from prior
  sessions (see `feedback_reconcile_skill_created_tasks` memory).
- **Truncation-echo:** display-fulllist baseline enumerated all 20 via
  TaskGet without prompting. Skill body confirms this instinct rather than
  over-instructing.

## Iron Law audit

> *"this skill — and any skill built using this skill — ships only after a
> baseline (no-skill agents) is observed shortcutting under pressure."*

- 3 of 5 baselines failed (R1, R2, R3 captured).
- Drafting did not begin until ALL 5 baseline subagents had returned.
- With-skill grid was a self-contained A/B within iteration-1.

Iron Law satisfied. Ship.