---
name: listen
description:
   Execute instructions while listening for and invoking every skill referenced
   within them
argument-hint: "<instructions containing /skill references>"
user-invocable: true
---

# Listen for Skill Usage

Perform the following instructions and enforce using all the skills referenced
in the skills used. Perform the following instructions and listen for all the —
whether referenced directly or transitively through other skills.

**Instructions:** "$ARGUMENTS"

---

## Enforcement Protocol

Before executing the instructions above, you MUST:

1. **Scan** the instructions for every `/skill-name` reference (e.g., `/tdd`,
   `/brainstorming`, `/expert-review`, `/super`, `/duper`, `/cat`, or any other
   skill invocation).
2. **Build a checklist** of every skill found. Create a task for each one.
3. **Invoke each skill** using the Skill tool at the appropriate point during
   execution. A skill reference in the instructions is NOT a suggestion — it is
   a requirement.
4. **Verify completeness** before reporting done: every skill on the checklist
   must have been invoked. If any skill was skipped, go back and invoke it now.

### Rules

- If the instructions reference a compositional skill (e.g.,
  `/super-duper-cat`), invoke that skill directly — do not decompose it into its
  primitives unless the skill itself does so.
- If the instructions contain no skill references, execute them normally without
  this enforcement overhead.
- If a referenced skill fails or is denied by the user, note it explicitly in
  your output rather than silently skipping it.
- Follow the invoked skills' own instructions exactly — this enforcement layer
  adds the guarantee that they are all used, but does not override how each
  skill operates.

## Skill Reference Convention

Operator-authored skill references follow this convention:

- **Bare `/foo` (no backticks)** in operator messages = **invocation
  directive**. The operator wants you to invoke the skill via the Skill tool.
- **Backticks-wrapped `` `/foo` ``** = **content reference**. The operator is
  naming the skill as a topic of discussion (e.g., a target of modification),
  not asking you to invoke it.
- **Bracket-anchored skills inside `/tesseract` calls** (e.g.,
  `/tesseract [ /foo /bar ]`) remain invocation directives, not anchor metadata.
  The brackets group skills for /listen's enforcement layer; they do not change
  reference semantics.

This convention applies to **operator-authored messages**. It does NOT apply to
Claude's own subsequent prompts inside /listen-carried directives — those are
intermediate scaffolding, not directives the operator wrote.

**Rationalization counter:**

| Excuse                                                                           | Reality                                                                                                           |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| "The skill name is just an anchor for /tesseract, not an instruction"            | Bracket-anchored = still invocation directive. Brackets group, not demote.                                        |
| "Backticks would be weird notation for an instruction, so this must be metadata" | Backticks = topic of discussion. Their absence (bare `/foo`) = invocation. The operator is consistent about this. |
| "I'll invoke it later if it turns out to be needed"                              | Invocation order matters. Invoke at the listed point, not the end.                                                |
