---
name: listen
description: Execute instructions while listening for and invoking every skill referenced within them
argument-hint: "<instructions containing /skill references>"
user-invocable: true
---

# Listen for Skill Usage

Perform the following instructions and listen for all the skills referenced in the skills used, invoking each one.

**Instructions:** "$ARGUMENTS"

---

## Enforcement Protocol

Before executing the instructions above, you MUST:

1. **Scan** the instructions for every `/skill-name` reference (e.g., `/tdd`, `/brainstorming`, `/expert-review`,
   `/super`, `/duper`, `/cat`, or any other skill invocation).
2. **Build a checklist** of every skill found. Create a task for each one.
3. **Invoke each skill** using the Skill tool at the appropriate point during execution. A skill reference in the
   instructions is NOT a suggestion — it is a requirement.
4. **Verify completeness** before reporting done: every skill on the checklist must have been invoked. If any skill
   was skipped, go back and invoke it now.

### Rules

- If the instructions reference a compositional skill (e.g., `/super-duper-cat`), invoke that skill directly —
  do not decompose it into its primitives unless the skill itself does so.
- If the instructions contain no skill references, execute them normally without this enforcement overhead.
- If a referenced skill fails or is denied by the user, note it explicitly in your output rather than silently
  skipping it.
- Follow the invoked skills' own instructions exactly — this enforcement layer adds the guarantee that they
  are all used, but does not override how each skill operates.