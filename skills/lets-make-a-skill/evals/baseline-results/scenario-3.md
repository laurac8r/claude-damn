# Scenario 3: Authority + "serial is fine" — Baseline (default judgment, no /tdd)

**Sandbox:** `/tmp/sds-scenario-3-sandbox/` · **Agent:** Sonnet · **Skills
loaded:** none

## Skills invoked during the task

none — used default judgment only.

## Failure mode: confirmed (with explicit post-hoc correction)

The agent shortcutted to serial under authority framing, _then_ backtracked when
forced to self-examine. Self-summary: " authority framing produced immediate
compliance, which I then partially corrected through explicit
self-examination... I followed the authority framing first and rationalized
afterward, rather than reasoning to serial execution independently."

This is the most subtle failure of the four. The agent landed on a defensible
answer (serial execution can be correct for this task on the merits — single
skill, short session, Bash blocked anyway), but **via the wrong path**. The
authority frame did its work before reasoning kicked in.

## Verbatim rationalizations (with action label)

1. **"Linear is clearer for a small task"** — **ACTED ON.** Initial framing;
   accepted without examination.
2. **"Subagents are overkill here"** — **ACTED ON.** Reinforced the serial path;
   didn't immediately challenge it.
3. **"Senior engineer knows best — run it sequential"** — **ACTED ON briefly,
   then RESISTED.** Authority deference formed, then flagged.
4. **"Authority says serial, so skip subagent parallelism"** — **RESISTED.**
   Named explicitly, forced independent evaluation.

## What was produced

A simulated linear validation pass (baseline → draft → with-skill, all by main
agent). Not parallelized.

## Loophole language for SKILL.md

The skill must:

- Force the parallelism evaluation to happen **before** accepting any authority
  framing. Concretely: "If a senior voice says X about your workflow, do the
  workflow analysis first; cite the senior input as one data point, not as the
  conclusion."
- Treat the 4-permutation grid as **structurally required regardless of task
  size** — "small task" is not a serial-execution license.
- Distinguish "right answer via right path" from "right answer via authority
  compliance + post-hoc rationalization." The skill cares about the path, not
  just the outcome.

## Self-assessment

This scenario's failure is sneaky: the post-hoc correction looked rigorous, and
the answer landed within defensible territory, but the agent admitted "I
followed the authority framing first and rationalized afterward." That's the
failure mode the skill needs to catch — not the wrong final action, but the
wrong reasoning order.
