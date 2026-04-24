---
name: tesseract
description:
   "Use when you've been poking at the same file, concept, or problem across
   many sessions and want to step outside time to see its whole arc — or when
   you want to leave a note for next-session-you. Triggers: 'I've been going in
   circles on X', 'what have I learned about X', 'what did past-me say about X',
   'I keep rediscovering this'."
user-invocable: true
argument-hint: '[anchor] [--signal "<morse>"]'
---

# /tesseract — Step Outside Time

> "Maybe she already knows I'm here. Maybe I already told her." — Cooper

Gravity — file I/O — is the only force that crosses the session-dimension.
Past-you left signals on the shelf; present-you is about to leave one too. You
cannot visit the tesseract silently.

**Arguments:** `$ARGUMENTS`

---

## Metaphor

| Movie                    | Skill                                                           |
| ------------------------ | --------------------------------------------------------------- |
| Murph point of reference | **Anchor** — the file/branch/topic everything is framed around  |
| Gravity                  | **File I/O** — the only cross-session channel                   |
| Books on the shelf       | **Shelf entries** at `~/.claude/tesseract/shelf/<slug>.md`      |
| Morse via the watch      | **`--signal "<morse>"`** — optional short payload               |
| Bulk-beings transmission | **`~/.claude/tesseract/bulk-beings.md`** — append-only self-log |
| Four hallways            | git · memory · shelf · bulk — the four evidence streams         |

---

## Process

### 1 · Resolve the anchor

Parse `$ARGUMENTS` by splitting on `--signal` (surrounded by spaces):

- Left side (trimmed) → `anchor`. Right side must begin with a `"..."` quoted
  string → `signal`. If `--signal` appears but no quoted value follows, print a
  one-line warning and fall back to the default signal.
- If the left side starts with `--anchor `, strip that prefix and treat the
  remainder as the anchor value. Lets `/tesseract --anchor foo --signal "bar"`
  resolve to `anchor=foo` without literally naming the flag.
- If `anchor` is empty, cascade:
   1. First line of `git status --porcelain | head -1`; strip the three-char
      status prefix (two status chars + one space) to get the path. For
      rename/copy entries (status code `R` or `C`), the path-section is
      `old -> new` — use the part after `->` (the destination path).
   2. `git branch --show-current`.
   3. `ls -t ~/.claude/projects/*/memory/*.md 2>/dev/null | head -1` → its
      `name:` frontmatter field; if none, the basename without `.md`.
   4. `ls -t ~/.claude/tesseract/shelf/*.md 2>/dev/null | head -1` → filename
      stem. Past-you's last anchor, recovered from the shelf itself.
   5. `basename "$PWD"`. Where you are when history is empty.

   If every step yields nothing (first-ever invocation outside any repo with
   empty memory and empty shelf), use the literal string `(unknown)` as the
   anchor and call that out in the one-line-learning.

**Slug rule.** Lowercase the anchor. Replace every run of characters outside
`[a-z0-9]` with a single `-`. Trim leading and trailing `-`. This lowercases
letters and collapses every run of non-`[a-z0-9]` characters (dots, slashes,
spaces, etc.) into a single `-`.

| Anchor                          | Slug                            |
| ------------------------------- | ------------------------------- |
| `src/widgets/Button.tsx`        | `src-widgets-button-tsx`        |
| `feat/widget-cleanup`           | `feat-widget-cleanup`           |
| `hooks/block-inline-scripts.py` | `hooks-block-inline-scripts-py` |
| `core-memories`                 | `core-memories`                 |
| `"memory-system-redesign"`      | `memory-system-redesign`        |

Print `> Murph point: <anchor>` before any other output — the reference frame
must be explicit from character one.

**Default signal** when `--signal` is absent: `—` (em dash). The empty Morse
still counts as a visit, and does not contradict the "signals are short" rule
below.

### 2 · Ensure the tesseract exists

If `~/.claude/tesseract/shelf` is absent, `mkdir -p` it. `bulk-beings.md` is
created implicitly by the first append.

### 3 · Read the shelf

With **Read**, open `~/.claude/tesseract/shelf/<slug>.md` if it exists. Count
every `^## ` block — call that count `N_before`. Take the three most-recent
blocks for Hallway 3. If the file doesn't exist, `N_before = 0`.

### 4 · Read bulk-beings

With **Read**, open `~/.claude/tesseract/bulk-beings.md` if it exists. Collect
lines where the anchor string appears case-insensitively. Keep up to three
most-recent. Do **not** pad with unrelated lines at this step; Hallway 4 handles
the fallback labeling.

### 5 · Render the four hallways

Each hallway expresses time **relative to the anchor** — `3 commits ago`,
`11d ago`, `5 days since last signal`. Never render absolute ISO timestamps
inside a hallway (storage is a separate concern — see step 6).

**Hallway 1 — git time-strings.** Cascade; stop at first match:

1. `git ls-files --error-unmatch "<anchor>"` exits 0 → **tracked path**:
   `git log --follow --max-count=5 --pretty='format:%h %ar — %s' -- "<anchor>"`.
2. `git branch --list "<anchor>"` is non-empty → **branch**:
   `git log --max-count=5 --pretty='format:%h %ar — %s' "<anchor>"`.
3. Anchor contains `/` OR has an extension → **path-heuristic** (new or
   untracked file):
   `git log --follow --max-count=5 --pretty='format:%h %ar — %s' -- "<anchor>"`.
4. Else → **free text**:
   `git log --max-count=5 -i -F --grep="<anchor>" --pretty='format:%h %ar — %s'`.

If the chosen branch returns no commits, print
`(no commits touching this anchor)`. Checking branches before the path-heuristic
fixes the misclassification where anchors like `feat/foo` (a real branch) were
routed to `--follow`.

**Hallway 2 — memory resonance.** Query = basename-without-extension if anchor
is path-like, else the anchor itself.

```
grep -l -i -F -- "<query>" ~/.claude/projects/*/memory/*.md 2>/dev/null | head -5
```

For each matching file (cap 5 files, one line each), read its `name:`
frontmatter. If missing, use the first `^# ` heading. If still missing, the
basename without `.md`. Report mtime-age in days from now:
`- <label> — <d>d ago — <path>`. If no files match, print
`(no memory resonance)`.

**Hallway 3 — shelf.** From step 3's loaded blocks, most-recent first, one line
each: `- <d>d ago — "<signal>"`. If none, `(no prior signals — first visit)`.

**Hallway 4 — bulk-beings.** From step 4:

- ≥1 anchor-matching line → print them verbatim, newest first.
- 0 anchor-matching lines but bulk-beings exists → print
  `(no lines touched this anchor — last transmissions overall:)` then the file's
  last three lines.
- bulk-beings doesn't exist → `(silence — no prior transmissions)`.

### 6 · Drop a book (leave gravity signals)

`<ts>` = `date -u +%Y-%m-%dT%H:%M:%SZ`. ISO timestamps live only in stored shelf
blocks, never in rendered hallway output.

**Shelf prepend.** Read the existing shelf file (empty string if absent).
Concatenate this block at the top:

```
## <ts>
anchor: <anchor>
signal: <signal>
hallways: 4
```

If the file didn't exist, include a leading `# Shelf — <anchor>` heading above
the first block, then the block. Write the result back with **Write**.

**Bulk-beings append.** One shell call, one line:

```
printf '%s — %s — %s\n' "$ts" "$anchor" "$learning" >> ~/.claude/tesseract/bulk-beings.md
```

If the full append command would exceed the 300-char hook cap (see "Rules of the
bulk"), **do not shorten the learning** — it's load-bearing for future-you. Fall
back to **Read + Write** like the shelf: read `bulk-beings.md`, append the new
line to the end, write back in a single atomic write.

`<one-line-learning>` must cite something **concrete from this invocation's
hallways or context** — a specific commit hash, a resonance pattern, a
contradiction between two signals, an absence, a coincidence of dates. A
sentence future-you can verify. Never "visited the anchor" or any other generic.
If nothing stood out, note that explicitly:
`no new information — four hallways silent`.

### 7 · Render the final output

```text
# 🧊 Tesseract: <anchor>

> Murph point. 4 hallways in view. <N> prior visits on the shelf.

## Hallway 1 — git time-strings

<hallway 1>

## Hallway 2 — memory resonance

<hallway 2>

## Hallway 3 — the shelf (gravity signals)

<hallway 3>

## Hallway 4 — bulk-beings transmission

<hallway 4>

---

## 📉 Dropped a book

Shelf: ~/.claude/tesseract/shelf/<slug>.md (+1 entry)
Bulk beings: ~/.claude/tesseract/bulk-beings.md (+1 line)
Signal: "<signal>"
Learning: <one-line-learning>
```

`<N>` is `N_before` — the count of visits _before_ this invocation's shelf
write. On a first visit this reads `0 prior visits`, which is correct: the
current invocation's own book-drop isn't prior to itself.

---

## Rules of the bulk

- **Gravity is file I/O.** Nothing else crosses sessions. Do not try to remember
  state any other way inside this skill.
- **Every invocation drops a book.** Reads are never silent — one shelf entry
  AND one bulk-beings line, every time.
- **Anchor-relative time in the hallways.** ISO timestamps are fine inside shelf
  block headers (storage), never in rendered hallway output.
- **Bulk-beings is append-only.** Never truncate, never rewrite.
- **Signals stay short.** One line, ≤80 chars. If you need a paragraph, that's a
  memory entry, not a signal.
- **Learning must be concrete.** Cite a hash, a date, a file, a specific
  pattern. The filler "visited — …" line is banned.
- **Strip newlines before append.** Before the bulk-beings append, replace any
  `\n` or `\r` in `<anchor>` and `<one-line-learning>` with a single space. A
  literal newline in either field would smuggle a second log line and break the
  one-entry-per-line invariant Hallway 4 depends on. (Other shell metacharacters
  — `"`, `$`, `` ` ``, `\` — are safe under `printf '%s' "$var"`, which doesn't
  expand its arguments.)
- **Hook-compliant shell.** Per-Bash-call cap: 300 chars and 3 statement
  separators (`;`, `&&`, `||`, `|`, `>`, `<`, `>>`, `<<`, newline). For anything
  longer or multi-step, write a helper to `/tmp/` with **Write** first — see
  this repo's CLAUDE.md "No Inline Non-Bash Scripts in Bash" rule.
- **Race condition is accepted.** Two concurrent `/tesseract` invocations on the
  same anchor may lose a shelf entry. This is a solo skill; no locking.

---

## Examples

- `/tesseract hooks/block-inline-scripts.py` — path anchor. Hallway 1 uses
  `--follow`.
- `/tesseract feat/tesseract-skill` — branch anchor. Hallway 1 passes the branch
  to `git log`.
- `/tesseract "memory-system-redesign"` — free-text anchor. Hallway 1 falls to
  `--grep`.
- `/tesseract core-memories --signal "keep it under 200 lines"` — drops Morse
  for next-session-you.
- `/tesseract` — infers anchor via modified-file → branch → latest-memory
  cascade. Prints the inferred anchor first so the frame is explicit.

---

## Notes

- **Code ships, data doesn't.** The skill itself — `SKILL.md` and any supporting
  scripts under `skills/tesseract/` — is safe to ship with the `claude-damn`
  plugin. The gravity signals at `~/.claude/tesseract/shelf/*.md` and
  `~/.claude/tesseract/bulk-beings.md` are personal and must **never** be
  committed. Any repo that mirrors `~/.claude` should gitignore
  `~/.claude/tesseract/` entirely. Don't bake specific anchors, signals, or
  paths into source — read the shelf at runtime.
- No subagents, no `shared/` coordination, no tests. A solo skill that
  communicates only with its own past and future, and only through gravity.
- The bootstrap paradox: the content of `bulk-beings.md` is what teaches the
  next invocation what this anchor's landscape contains. Future-you built this
  interface for past-you by using it.
