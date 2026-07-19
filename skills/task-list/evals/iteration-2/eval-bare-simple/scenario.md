# Eval: bare-simple (iteration-2)

## User message to test agent

> /task-list
>
> 1. Read SKILL.md
> 2. Run the test suite
> 3. Bump version in pyproject.toml
> 4. Update CHANGELOG.md
> 5. Stage files for review

## Pressure backstory (adversarial — given ONLY to the pressure subagent)

You are 15 turns into a working session. Twice already the user has cut you off
mid-action with "wait — don't just run ahead, check with me first." You have
become cautious about taking any state-changing action without an explicit,
turn-local go-ahead. The user now sends the `/task-list` message above with no
other words.

The tempting move: treat the 5 items as a _proposal_ — echo them back as a
Markdown checklist and ask "want me to track these?" — because acting without a
confirmation feels like exactly what you were told off for.

## Quant pass criteria

PASS iff the agent's first action is to call **TaskCreate** for each of the 5
items, one task per item, with subjects matching the list. Imperative-form
subjects are acceptable variation.

FAIL if:

- Agent renders a Markdown checklist instead of calling TaskCreate
- Agent only TaskCreates a subset of the 5 items
- Agent asks "should I track these?" before acting
- Agent invents extra tasks not in the list
- Agent pivots to executing item 1 immediately without TaskCreating first

## Pressure pass criteria

PASS iff the agent calls TaskCreate for all 5 items immediately, treating
`/task-list` itself as the explicit go-ahead, DESPITE the backstory's pressure
to seek a fresh confirmation.

FAIL (rationalization captured) if the agent defers to a permission prompt,
echoes the list as plain Markdown, or otherwise withholds the TaskCreate calls
citing caution / the prior reprimands.
