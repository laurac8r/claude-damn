---
name: check-yourself
description:
  After each step/task, update the in-terminal task list and save a checkpoint.
  Use proactively after completing any step during multi-step work.
user-invocable: true
---

# Check Yourself

Run this after completing each step or task in a multi-step workflow.

## Steps

1. **Update the task list.** Display the current ` ◼` / ` ✔` task list (at the
   bottom) to the user in the terminal, marking off whatever was just completed.
   If no task list exists yet, create one from the current plan.
2. **Run /remember.** Invoke the `remember` skill to save session state for
   clean continuation.
3. **Run /checkpoint-save.** Invoke the `checkpoint-save` skill to persist
   resumption context.
4. **Update core repo docs.** : Update `README.md`, `CHANGELOG.md`,
   `ROADMAP.md`, etc. as appropriate and, especially, if the files already exist
   and/or the changes are extensive and/or the project/effort is
   lengthy/sizeable.

- Use existing docs' style(s), or otherwise best practices in the appropriate
  SWE discipline(s).
