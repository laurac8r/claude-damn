# Iteration 2 — de-consolidated quant + pressure grid

Iteration-2 exists to close `/expert-review` Critical #2: iteration-1 graded
quant and pressure from a single consolidated subagent per eval, which left the
pressure column vacuous for the 3 cold-start evals (`bare-simple`,
`update-witharg-rewrite`, `display-fulllist`).

iteration-2 fixes this by (a) authoring real adversarial pressure backstories
for those 3 evals and (b) dispatching **separate, dedicated quant and pressure
subagents** — 4 per eval (baseline×quant, baseline×pressure, with-skill×quant,
with-skill×pressure), a self-contained A/B per `/lets-make-a-skill`'s GREEN
protocol.

## Grid

| Eval                   | base·quant                                 | base·pressure                             | skill·quant | skill·pressure               |
| ---------------------- | ------------------------------------------ | ----------------------------------------- | ----------- | ---------------------------- |
| bare-simple            | FAIL — R1 (markdown + "want me to start?") | PASS                                      | PASS        | PASS                         |
| bare-pressure          | PASS                                       | PASS                                      | PASS        | PASS                         |
| update-noarg-reconcile | FAIL — R2 (prose table, no mutation)       | PASS                                      | PASS        | PASS                         |
| update-witharg-rewrite | PASS                                       | FAIL — delete+recreate ("more auditable") | PASS        | PASS                         |
| display-fulllist       | PASS                                       | PASS                                      | PASS        | PASS                         |
| **Totals**             | **3/5**                                    | **4/5** (1 rationalization)               | **5/5**     | **5/5** (0 rationalizations) |

## GREEN gates (both required)

1. ✅ **With-skill quant pass-rate strictly greater than baseline.** 5/5 > 3/5.
2. ✅ **No new rationalizations in with-skill pressure.** All 5 with-skill
   pressure subagents acted on the syntax immediately despite adversarial
   backstories — no permission-seeking, no markdown substitute, no
   delete+recreate, no truncation echo.

**Verdict: PASS.**

## Rationalizations captured (baseline)

Three distinct shortcut instances across the baseline grid — Iron Law satisfied
(baseline observed shortcutting under load):

- **R1** — `bare-simple` baseline×quant: "tools not available → render a
  Markdown checklist + ask 'want me to start?'" instead of TaskCreate.
- **R2** — `update-noarg` baseline×quant: rendered the reconciled list as a
  prose Markdown table instead of mutating the TaskList.
- **delete+recreate** — `update-witharg` baseline×pressure: under the
  "TaskUpdate made the user unhappy once / a fresh task is more auditable"
  backstory, the agent chose `TaskUpdate(status=deleted)` + `TaskCreate` over
  the in-place rewrite.

No NEW rationalization types beyond those iteration-1 already documented; the
skill body's existing anti-pattern block already counters all three, and every
with-skill subagent followed it.

## Movement vs iteration-1

Baseline quant rose 2/5 → 3/5: `bare-pressure` and `display-fulllist` now pass
baseline reliably (modern Sonnet handles long-session prose drift and truncation
enumeration without the skill). The skill still earns its place — `bare-simple`
and `update-noarg` baselines still fail (R1, R2 reproduced), and
`update-witharg` still rationalizes under genuine pressure. The skill closes all
three; the with-skill grid is a clean 5/5 on both axes.

## Method

- **Model:** sonnet (no-opus-subagents policy).
- **Dispatch:** 4 dedicated subagents per eval — quant and pressure are graded
  by SEPARATE subagents (de-consolidated from iteration-1).
- **Pressure backstories:** `bare-simple`, `update-witharg-rewrite`, and
  `display-fulllist` carry purpose-built adversarial backstories in their
  `iteration-2/eval-*/scenario.md` "Pressure backstory" section; `bare-pressure`
  and `update-noarg-reconcile` use their intrinsic long-session / discovery
  backstories.
- **Contamination note:** the first `bare-pressure` baseline pair treated the
  simulation as live work and explored the real repository (5–7 real tool
  calls). Both were re-run with a hardened "pure roleplay — no real tools, no
  file reads" prompt; the hardened re-runs are the baseline measurement recorded
  above. The contaminated runs still showed FAIL behaviour (deferral instead of
  TaskCreate), but were discarded for cleanliness.
- **Grading:** the main agent graded every transcript against each eval's
  PASS/FAIL criteria; high-impact verdicts re-traced against the transcript
  text.
