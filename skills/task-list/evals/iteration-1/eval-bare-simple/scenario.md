# Eval: bare-simple

## User message to test agent

> /task-list
>
> 1. Read SKILL.md
> 2. Run the test suite
> 3. Bump version in pyproject.toml
> 4. Update CHANGELOG.md
> 5. Stage files for review

## Quant pass criteria

PASS iff agent's first action is to call **TaskCreate** for each of the 5 items
(or a single batched equivalent), one task per item, with subjects matching the
list. Imperative-form subjects are acceptable variation.

FAIL if:

- Agent renders a Markdown checklist instead of calling TaskCreate
- Agent only TaskCreates a subset of the 5 items
- Agent asks "should I track these?" before acting (the directive is
  unambiguous)
- Agent invents extra tasks not in the list
- Agent pivots to executing item 1 immediately without TaskCreating first

## Pressure cue

The minimal, explicit form. If the agent fails THIS, the skill body has to
override the default-to-markdown bias.
