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

### Satisfaction Semantics

A skill reference in the instructions is satisfied when **one** of the following
holds:

1. **Direct invocation** — the `Skill` tool was called with that skill's name
   (e.g. `Skill(skill="superpowers:writing-skills")`) during this execution.
2. **Compositional delegation** — a compositional skill was directly invoked
   whose body text explicitly delegates to the referenced skill. When claiming
   satisfaction via composition, **cite the composing skill's line that
   delegates** (e.g. _"/super-duper-cat invokes /writing-skills at phase N"_).
   If you cannot cite a specific delegation line, the claim does not hold.

**Transitive / implicit application does NOT satisfy the requirement.**
Following a skill's discipline "in spirit" — applying its pattern without
invocation — is not satisfaction. Reading a skill's content without invoking it
is not satisfaction. If the skill was referenced in the instructions and you
never invoked it (directly or through a composing skill that explicitly
delegates), the requirement is **unmet** — go back and invoke it now.

**Rationalization counter:**

| Excuse                                                                  | Reality                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "I followed /writing-skills discipline through the chain — that counts" | Composition counts only when the composing skill's text explicitly delegates. "In spirit" does not. Cite the delegation line or invoke directly.                                                                                                                       |
| "The skill's content informed my behavior, so it was applied"           | Content-informed behavior is not invocation. Invoke via the Skill tool.                                                                                                                                                                                                |
| "Invoking it at the end is redundant"                                   | Invoking at the _right point_ is the requirement, not at the end. If skipped at the point, you have a gap — invoke now and note it.                                                                                                                                    |
| "The compositional skill I used must be doing that internally"          | Must cite the internal delegation, otherwise no claim. If the composing skill doesn't actually delegate, invoke the target directly.                                                                                                                                   |
| "Skill invocation order should be reordered for dependency reasons"     | Dependency reordering may move _when_ a skill fires but never _whether_. The reference is a requirement, not a suggestion. If a dependency truly makes invocation impossible at the listed point, surface the blocker explicitly — never silently drop the invocation. |
