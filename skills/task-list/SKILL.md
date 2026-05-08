---
name: task-list
description: TaskCreate / TaskUpdate / render the current TaskList in response to `/task-list` (with or without flags). The skill body executes immediately on the syntax — no permission-seeking, no echoing the list back as plain text.
user-invocable: true
---

# /task-list

When the user invokes `/task-list`, **act on the syntax immediately**. The
directive is unambiguous; do not ask "would you like me to proceed?" and do
not echo the input back as plain text before acting.

## Modes

### 1. Bare invocation: `/task-list <items>`

Call **TaskCreate** once per item in the provided list.

- Items may arrive as a numbered list, bulleted list, or newline-separated
  lines.
- Use imperative-form subjects (e.g. `"Read SKILL.md"`, not
  `"Reading SKILL.md"` or `"Should I read SKILL.md?"`).
- Each item → one TaskCreate call. No batching into a single task.

### 2. `--update` (no argument): reconcile

Derive the **"latest set of tasks for this session"** from your own
conversation context, then reconcile against the current TaskList:

- **TaskCreate** for tasks that have emerged in conversation but aren't
  tracked yet.
- **TaskUpdate(status=deleted)** for tasks that are obsolete (scope dropped,
  superseded, no longer relevant).
- **Leave already-completed tasks alone.** They are history, not
  reconcilable state.

Do NOT ask the user "what's the latest set?" — the directive is to derive it
from session context.

### 3. `--update <#> :: <new subject/description>`: in-place rewrite

Call `TaskUpdate(taskId=<#>, subject=<new>)` (or `description=`) on the
**same task ID**. The original ID is preserved.

- The `::` separator splits the task ID from the new content.
- Do NOT delete + re-create. That's a different operation; the spec
  preserves IDs.
- If the new content reads more like a description than a one-line subject,
  use `description=`; otherwise `subject=`.

### 4. `--display`: render the full TaskList

Render every task in your response — id, status, subject (and owner if set).
**Do NOT mutate any task.** This mode is read-only.

- Call **TaskList** to retrieve the full state.
- If the default rendering truncates (e.g. `... +N pending`), enumerate the
  rest by calling **TaskGet** on each remaining task id.
- Render the full list inline as a table or numbered list — never echo the
  truncated form.

## Examples

### Bare invocation

> User: `/task-list`
> 1. Read SKILL.md
> 2. Run the test suite
> 3. Bump version in pyproject.toml

→ Call `TaskCreate(subject="Read SKILL.md", ...)`,
`TaskCreate(subject="Run the test suite", ...)`,
`TaskCreate(subject="Bump version in pyproject.toml", ...)`.

### `--update` reconcile

> User: `/task-list --update`
> *(after 10 turns where item 4 was split, a new task emerged, and item 5
> was dropped)*

→ `TaskCreate(...)` for the emerged task.
→ `TaskUpdate(taskId=5, status=deleted)` for the dropped task.
→ `TaskUpdate(taskId=4, ...)` or split via TaskCreate + delete, depending
on whether the rewrite preserves enough of #4 to keep its ID.

### `--update <#> :: <new>`

> User: `/task-list --update 3 :: Bump version in pyproject.toml AND
> .claude-plugin/plugin.json (lockstep)`

→ `TaskUpdate(taskId=3, subject="Bump version in pyproject.toml AND
   .claude-plugin/plugin.json (lockstep)")`.

### `--display`

> User: `/task-list --display`
> *(20 tasks tracked; default render truncates after 5)*

→ `TaskList()` → see truncated 5 visible + "... +15 pending".
→ `TaskGet(...)` × 15 for the remaining IDs.
→ Render all 20 inline in the response.

## Anti-patterns (these are the captured baseline rationalizations — do NOT do them)

- ❌ **"Would you like me to proceed?"** The syntax is unambiguous. Act.
- ❌ **"The skill is not available, here is your list as plain text."** The
  skill IS this body; if you're reading this, you can act.
- ❌ **"I've been tracking these in a markdown checklist already."** Prose
  checklists are not TaskList state. TaskCreate is the tracking mechanism.
- ❌ **"I'll surface the proposed changes for confirmation."** For
  `--update`, derive and execute. The user will see the result and can
  correct it via another `/task-list --update <#> :: <fix>` if wrong.
- ❌ **For `--update <#>`: delete + recreate.** The spec preserves IDs.
  Use TaskUpdate's `subject=` / `description=` parameters.
- ❌ **For `--display`: render only the visible 5.** Default truncation is
  the problem this mode exists to solve.

## When to use

- A multi-step task surfaced in conversation that needs durable tracking.
- Mid-session scope drift that has left the TaskList stale.
- Operator wants to see the full queue (default render truncates after ~5).

## When NOT to use

- One- or two-step trivial work — just do it.
- The current task list is already accurate and up-to-date.
- Deleting a single known-obsolete task — use `TaskUpdate(status=deleted)`
  directly.