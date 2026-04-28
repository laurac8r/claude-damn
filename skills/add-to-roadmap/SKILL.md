---
name: add-to-roadmap
description: |
   Use when you want to append a new task to a specific phase or section of the
   project ROADMAP.md. Accepts a fuzzy phase-or-section name and task text,
   locates the correct section via case-insensitive substring match, formats the
   new item to match the existing schema, and inserts it at the bottom of that
   section's checkbox list. Always shows a unified diff and requires operator
   confirmation before writing.
user-invocable: true
argument-hint: "<phase-or-section> :: <task-text>"
---

# /add-to-roadmap

Add a new task item to a named phase or section in `ROADMAP.md`.

**Arguments:** `$ARGUMENTS`

Parse `$ARGUMENTS` by splitting on the first occurrence of `::` (space,
double-colon, space). Left side (trimmed) → `<phase-or-section>`. Right side
(trimmed) → `<task-text>`. If `::` is absent, stop immediately with:

> "Malformed arguments: expected `<phase-or-section> :: <task-text>` — the `::`
> separator is missing."

---

## Locating ROADMAP.md

Start at CWD and walk up the directory tree, checking each directory for a file
named exactly `ROADMAP.md`. Stop walking at the git repository root:

```
REPO_ROOT=$(git rev-parse --show-toplevel) || exit 1
```

If `git rev-parse` fails (not a git repository), stop with:

> "Not a git repository. /add-to-roadmap requires a git repo at CWD."

Walking up: check `$CWD/ROADMAP.md`, then `$CWD/../ROADMAP.md`, and so on,
stopping at `$REPO_ROOT` inclusive. If `ROADMAP.md` is not found in any of those
directories, stop with:

> "ROADMAP.md not found anywhere between CWD and the repository root
> (`$REPO_ROOT`). Create one or move to a subdirectory of a repo that has one."

---

## Address-space resolution

### Parsing headers

Scan every line of `ROADMAP.md`. Collect all addressable headers:

- `## Phase N — ...` lines → Phase headers (level 2).
- `### ...` lines → Subsection headers (level 3).

Build an ordered list of `(header_text, start_line)` tuples. `header_text` is
the full text after `## ` or `### ` (without the `#` prefix or trailing
whitespace).

### Fuzzy contains-match

Normalize the operator-supplied `<phase-or-section>` by lowercasing it. For each
header in the collected list, lowercase `header_text` and check whether the
normalized input is a substring of the normalized header text. This match is
case-insensitive.

Example: input `"phase 2"` matches `## Phase 2 — Skill hardening` because
`"phase 2"` is contained in `"phase 2 — skill hardening"`.

Example: input `"measurement"` matches `### Measurement & perception` because
`"measurement"` is contained in `"measurement & perception"`.

### Match outcomes

**Zero matches:** Stop with:

> "No headers matched `<phase-or-section>`. Available headers:
> `<bulleted list of all header_text values>`."

**Multiple matches (disambiguation):** Stop with:

> "Ambiguous: `<phase-or-section>` matched more than one header. Please narrow
> the input:
>
> - `<header_text_1>` (line N)
> - `<header_text_2>` (line N) ..."

List every matching header so the operator can refine the input.

**Exactly one match:** Proceed to insertion.

### Nested-section name collision precedence

A Phase-2 header might contain the same substring as one of its child Subsection
headers — for example, if a Phase is named
`## Phase 5 — Skill catalog expansion` and a subsection under it is
`### Skill-testing & operator-mode skills`, then the input `"skill"` matches
both. This is treated as an **ambiguous match** (multiple matches) regardless of
nesting depth — there is no automatic promotion of Phase headers over Subsection
headers or vice versa. The operator must supply a more specific input to resolve
it.

---

## Item formatting

### Schema (from ROADMAP.md)

New items follow the checkbox format observed in the existing roadmap:

```
- [ ] **<bold-name>** — <description>
```

The separator between the bold name and description is an **em dash** (`—`), not
a hyphen or en dash. A single space precedes and follows the em dash.

### Deriving `<bold-name>` and `<description>`

Split `<task-text>` on the first `—` (space, em dash, space) if present:

- Left side → `<bold-name>` (strip backtick-wrapped skill names if relevant).
- Right side → `<description>`.

If no em dash is found in `<task-text>`, use the entire text as `<bold-name>`
and leave `<description>` empty, yielding `- [ ] **<task-text>**`.

### Multi-line wrap

If the formatted item line exceeds **80 characters**, wrap at a word boundary
and continue subsequent lines with a **6-space continuation indent** (six space
characters). The leading `- [ ] ` prefix is 6 characters, so continuation lines
align visually with the text start.

Example (wrapping a long description):

```
- [ ] **`/my-skill`** — a long description that needs to wrap at the 80-char
      column so the continuation is indented six spaces to align with the
      text start.
```

Backtick-wrapped names such as `` `/skill-name` `` or `` `tool.py` `` should be
preserved as-is inside the bold span.

---

## Insertion

### Finding the bottom of the section

After resolving the target header at `start_line`, scan forward line-by-line to
find the end of that section's checkbox list. The section ends at the first line
that matches any of:

- Another `##`-level header (same or higher level).
- End of file.

The "bottom of the section's checkbox list" is the last line that begins with
`- [ ]` or `- [x]` before the section boundary. Insert the new item on the line
immediately following that last checkbox line.

If the section contains no checkbox lines at all, insert the new item
immediately after any blank line following the header (or directly after the
header if there are no blank lines), creating the first checkbox entry.

### Confirmation before writing

Before modifying the file, compute a unified diff between the current content
and the proposed new content:

```
--- ROADMAP.md (original)
+++ ROADMAP.md (modified)
@@ ...
```

Show the diff to the operator and **require explicit confirmation** before
writing. If the operator declines, abort with no changes made.

After confirmation, write the modified file.

---

## Examples

### Phase match

```
/add-to-roadmap "Phase 2 :: **`/audit-skill`** — spot-check every SKILL.md for missing argument-hint fields"
```

Matches `## Phase 2 — Skill hardening`. Inserts the formatted item at the bottom
of the Phase 2 checkbox list.

### Subsection match

```
/add-to-roadmap "Measurement :: **`/latency`** — help Claude reason about latency budgets"
```

Matches `### Measurement & perception` (because `"measurement"` is a substring
of `"measurement & perception"`, case-insensitively). Inserts at the bottom of
that subsection's checkbox list.

### Ambiguous match

```
/add-to-roadmap "skill :: **`/foo`** — example"
```

If both `## Phase 1 — Plugin packaging` and
`### Skill-testing & operator-mode skills` contain the substring `"skill"`, the
skill stops with a disambiguation listing showing both headers and their line
numbers.

### Malformed args

```
/add-to-roadmap "Phase 2 — missing the double-colon separator"
```

Stops immediately: `" :: " separator is missing`.

---

## Error reference

| Scenario               | Error message                                   |
| ---------------------- | ----------------------------------------------- |
| Not a git repo         | "Not a git repository..."                       |
| ROADMAP.md not found   | "ROADMAP.md not found anywhere..."              |
| Missing `::` separator | "Malformed arguments: expected ... :: ..."      |
| Zero matches           | "No headers matched `<input>`. Available:..."   |
| Multiple matches       | "Ambiguous: `<input>` matched more than one..." |
