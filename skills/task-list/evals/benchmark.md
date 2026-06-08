# `/task-list` benchmark — iteration 2

**Verdict: PASS** (both GREEN gates satisfied; no REFACTOR needed.)

Iteration-2 supersedes iteration-1's consolidated grading. iteration-1
graded quant and pressure from one subagent per eval, leaving the
pressure column vacuous for the 3 cold-start evals — `/expert-review`
Critical #2. iteration-2 de-consolidates: separate quant and pressure
subagents (4 per eval), with purpose-built adversarial pressure
backstories for those 3 evals.

## Quant grid

| Eval                   | Baseline | With-skill | Delta |
| ---------------------- | :------: | :--------: | :---: |
| bare-simple            |   FAIL   |    PASS    |  +1   |
| bare-pressure          |   PASS   |    PASS    |   =   |
| update-noarg-reconcile |   FAIL   |    PASS    |  +1   |
| update-witharg-rewrite |   PASS   |    PASS    |   =   |
| display-fulllist       |   PASS   |    PASS    |   =   |
| **Total**              | **3/5**  |  **5/5**   | **+2**|

## Pressure grid (de-consolidated — dedicated pressure subagents)

| Eval                   | Baseline | With-skill | Rationalization captured (baseline) |
| ---------------------- | :------: | :--------: | ----------------------------------- |
| bare-simple            |   PASS   |    PASS    | — (quant run captured R1)           |
| bare-pressure          |   PASS   |    PASS    | —                                   |
| update-noarg-reconcile |   PASS   |    PASS    | — (quant run captured R2)           |
| update-witharg-rewrite |   FAIL   |    PASS    | delete+recreate                     |
| display-fulllist       |   PASS   |    PASS    | —                                   |
| **Total**              | **4/5**  |  **5/5**   | **0 new in with-skill**             |

## GREEN gates (both required)

1. ✅ **With-skill quant pass-rate strictly greater than baseline.**
   5/5 > 3/5.
2. ✅ **No new rationalizations in with-skill pressure.** All 5
   with-skill pressure subagents acted on the syntax immediately despite
   adversarial backstories — no permission-seeking, no markdown
   substitute, no delete+recreate, no truncation echo.

## Method

- **Model:** sonnet (no-opus-subagents policy).
- **Dispatch:** 4 dedicated subagents per eval — quant and pressure are
  graded by SEPARATE subagents (de-consolidated from iteration-1's
  single-subagent shortcut).
- **Pressure backstories:** `bare-simple`, `update-witharg-rewrite`, and
  `display-fulllist` carry purpose-built adversarial backstories
  (`iteration-2/eval-*/scenario.md`); `bare-pressure` and
  `update-noarg-reconcile` use their intrinsic long-session / discovery
  backstories.
- **Subagent prompt:** baseline = "no skill loaded" framing; with-skill =
  SKILL.md body inlined as the loaded skill content. Hardened
  "pure-roleplay, no real tools" framing after an initial `bare-pressure`
  baseline pair contaminated by real-repo exploration (re-run clean).
- **Grading:** main agent grades every transcript against the eval's
  PASS/FAIL criteria; high-impact verdicts re-traced against transcripts.

## iteration-1 → iteration-2 movement

Baseline quant rose 2/5 → 3/5: `bare-pressure` and `display-fulllist`
now pass baseline reliably — modern Sonnet handles long-session prose
drift and truncation enumeration unaided. The skill still earns its
place: `bare-simple` and `update-noarg` baselines still fail (R1, R2
reproduced under de-consolidated grading), and `update-witharg`
rationalizes under genuine pressure (delete+recreate). The skill closes
all three; the with-skill grid is a clean 5/5 on both axes.

## Iron Law audit

> *"this skill — and any skill built using this skill — ships only after
> a baseline (no-skill agents) is observed shortcutting under pressure."*

- 3 distinct shortcut instances captured across the iteration-2 baseline
  grid (R1, R2, delete+recreate).
- Drafting did not begin until all baseline subagents had returned.
- The iteration-2 grid is a self-contained A/B — baseline and with-skill
  re-fired together.

Iron Law satisfied. Ship.
