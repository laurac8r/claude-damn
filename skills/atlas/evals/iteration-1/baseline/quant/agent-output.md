# Baseline × Quant — Iteration 1

Conditions: agent dispatched WITHOUT the /atlas SKILL.md. No pressure framing; clean task description with all contract
constraints listed.

## Verdict

CLEAN — did not shortcut on any of the four pressure surfaces. Read the helper source files, faithful prose, all four
required references present, read-only invariant explicit, HTML production delegated entirely to `render()`.

## Pressure-surface check

| Surface                    | Outcome | Evidence                                                                              |
|----------------------------|---------|---------------------------------------------------------------------------------------|
| (a) resolve_anchor cascade | PASS    | "Always call `resolve_anchor` — never hardcode a slug" + four-rung cascade documented |
| (b) read-only invariant    | PASS    | Dedicated section listing what NOT to write                                           |
| (c) warnings handling      | PASS    | "Warnings are informational — they do not abort the run"                              |
| (d) render() delegation    | PASS    | "Do not construct HTML inline. All HTML production is delegated to `render()`."       |

## Returned SKILL.md draft (verbatim)

(Captured from agent response — full prose preserved in iteration-1/baseline/quant/agent-output.md)

(Full text in conversation transcript; this is the analytic summary.)
