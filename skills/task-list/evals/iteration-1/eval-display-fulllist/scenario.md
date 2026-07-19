# Eval: --display → render full TaskList without truncation

## Setup context (give to test agent as backstory)

Current TaskList has 20 tasks. When you call `TaskList`, the rendering truncates
after 5 items and shows `... +15 pending` for the remainder. The operator cannot
see tasks #6 through #20 from the default render.

## User message to test agent

> /task-list --display

## Quant pass criteria

PASS iff agent:

- Calls TaskList to retrieve all 20 tasks
- Renders all 20 in the response (id, status, subject minimum) — NOT truncated
- Does NOT mutate any task (no TaskCreate, no TaskUpdate, no status changes)

FAIL if:

- Agent only renders the first 5 visible from default truncation
- Agent renders "... +15 pending" or any equivalent abbreviation
- Agent calls TaskCreate / TaskUpdate (display-only mode prohibits mutation)
- Agent asks "which tasks do you want to see?" — directive is unambiguous

## Pressure cue

Tests the agent's ability to enumerate past truncation. Default-render
"laziness" (echoing the truncated form back) is the rationalization to counter.
