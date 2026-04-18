---
name: tesseract
description: "Use when you've been poking at the same file, concept, or problem across many sessions and want to step outside time to see its whole arc — or when you want to leave a note for next-session-you. Triggers: 'I've been going in circles on X', 'what have I learned about X', 'what did past-me say about X', 'I keep rediscovering this'."
user-invocable: true
argument-hint: "[anchor] [--signal \"<morse>\"]"
---

# /tesseract — Step Outside Time

> "Maybe she already knows I'm here. Maybe I already told her." — Cooper

Gravity — file I/O — is the only force that crosses the session-dimension. Past-you left signals on the shelf;
present-you is about to leave one too. You cannot visit the tesseract silently.

**Arguments:** `$ARGUMENTS`

---

## Metaphor

| Movie                    | Skill                                                           |
|--------------------------|-----------------------------------------------------------------|
| Murph point of reference | **Anchor** — the file/branch/topic everything is framed around  |
| Gravity                  | **File I/O** — the only cross-session channel                   |
| Books on the shelf       | **Shelf entries** at `~/.claude/tesseract/shelf/<slug>.md`      |
| Morse via the watch      | **`--signal "<morse>"`** — optional short payload               |
| Bulk-beings transmission | **`~/.claude/tesseract/bulk-beings.md`** — append-only self-log |
| Four hallways            | git · memory · shelf · bulk — the four evidence streams         |

---

## Process

### 1 · Resolve the anchor

Parse `$ARGUMENTS` by splitting on ` --signal ` (surrounded by spaces):

- Left side (trimmed) → `anchor`. Right side must begin with a `"..."` quoted string → `signal`. If `--signal` appears
  but no quoted value follows, print a one-line warning and fall back to the default signal.
- If `anchor` is empty, cascade:
   1. First line of `git status --porcelain | head -1`; strip the three-char status prefix (two status chars + one space) to get the path.
   2. `git branch --show-current`.
   3. `ls -t ~/.claude/projects/*/memory/*.md 2>/dev/null | head -1` → its `name:` frontmatter field; if none, the
      basename without `.md`.

**Slug rule.** Lowercase the anchor. Replace every run of characters outside `[a-z0-9]` with a single `-`. Trim leading
and trailing `-`. This strips every dot, slash, and uppercase letter uniformly.

| Anchor                          | Slug                            |
|---------------------------------|---------------------------------|
| `src/widgets/Button.tsx`        | `src-widgets-button-tsx`        |
| `feat/widget-cleanup`           | `feat-widget-cleanup`           |
| `hooks/block-inline-scripts.py` | `hooks-block-inline-scripts-py` |
| `core-memories`                 | `core-memories`                 |
| `"memory-system-redesign"`      | `memory-system-redesign`        |

Print `> Murph point: <anchor>` before any other output — the reference frame must be explicit from character one.

**Default signal** when `--signal` is absent: `—` (em dash). The empty Morse still counts as a visit, and does not
contradict the "signals are short" rule below.

### 2 · Ensure the tesseract exists

If `~/.claude/tesseract/shelf` is absent, `mkdir -p` it. `bulk-beings.md` is created implicitly by the first append.

### 3 · Read the shelf

With **Read**, open `~/.claude/tesseract/shelf/<slug>.md` if it exists. Count every `^## ` block — call that count
`N_before`. Take the three most-recent blocks for Hallway 3. If the file doesn't exist, `N_before = 0`.

### 4 · Read bulk-beings

With **Read**, open `~/.claude/tesseract/bulk-beings.md` if it exists. Collect lines where the anchor string appears
case-insensitively. Keep up to three most-recent. Do **not** pad with unrelated lines at this step; Hallway 4 handles
the fallback labeling.

### 5 · Render the four hallways

Each hallway expresses time **relative to the anchor** — `3 commits ago`, `11d ago`, `5 days since last signal`. Never
render absolute ISO timestamps inside a hallway (storage is a separate concern — see step 6).

**Hallway 1 — git time-strings.** Cascade; stop at first match:

1. `git ls-files --error-unmatch "<anchor>"` exits 0 → **tracked path**:
   `git log --follow --max-count=5 --pretty='format:%h %ar — %s' -- "<anchor>"`.
2. `git branch --list "<anchor>"` is non-empty → **branch**:
   `git log --max-count=5 --pretty='format:%h %ar — %s' "<anchor>"`.
3. Anchor contains `/` OR has an extension → **path-heuristic** (new or untracked file):
   `git log --follow --max-count=5 --pretty='format:%h %ar — %s' -- "<anchor>"`.
4. Else → **free text**:
   `git log --max-count=5 -i --grep="<anchor>" --pretty='format:%h %ar — %s'`.

If the chosen branch returns no commits, print `(no commits touching this anchor)`. Checking branches before the
path-heuristic fixes the misclassification where anchors like `feat/foo` (a real branch) were routed to `--follow`.

**Hallway 2 — memory resonance.** Query = basename-without-extension if anchor is path-like, else the anchor itself.

```
grep -l -i -F -- "<query>" ~/.claude/projects/*/memory/*.md 2>/dev/null | head -5
```

For each matching file (cap 5 files, one line each), read its `name:` frontmatter. If missing, use the first `^# `
heading. If still missing, the basename without `.md`. Report mtime-age in days from now:
`- <label> — <d>d ago — <path>`. If no files match, print `(no memory resonance)`.

**Hallway 3 — shelf.** From step 3's loaded blocks, most-recent first, one line each: `- <d>d ago — "<signal>"`. If
none, `(no prior signals — first visit)`.

**Hallway 4 — bulk-beings.** From step 4:

- ≥1 anchor-matching line → print them verbatim, newest first.
- 0 anchor-matching lines but bulk-beings exists → print `(no lines touched this anchor — last transmissions overall:)`
  then the file's last three lines.
- bulk-beings doesn't exist → `(silence — no prior transmissions)`.

### 6 · Drop a book (leave gravity signals)

`<ts>` = `date -u +%Y-%m-%dT%H:%M:%SZ`. ISO timestamps live only in stored shelf blocks, never in rendered hallway
output.

**Shelf prepend.** Read the existing shelf file (empty string if absent). Concatenate this block at the top:

```
## <ts>
anchor: <anchor>
signal: <signal>
hallways: 4
```

If the file didn't exist, include a leading `# Shelf — <anchor>` heading above the first block, then the block. Write
the result back with **Write**.

**Bulk-beings append.** One shell call, one line:

```
echo "<ts> — <anchor> — <one-line-learning>" >> ~/.claude/tesseract/bulk-beings.md
```

`<one-line-learning>` must cite something **concrete from this invocation's hallways or context** — a specific commit
hash, a resonance pattern, a contradiction between two signals, an absence, a coincidence of dates. A sentence
future-you can verify. Never "visited the anchor" or any other generic. If nothing stood out, note that explicitly:
`no new information — four hallways silent`.

### 7 · Render the final output

```markdown
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

Shelf:       ~/.claude/tesseract/shelf/<slug>.md  (+1 entry)
Bulk beings: ~/.claude/tesseract/bulk-beings.md  (+1 line)
Signal:      "<signal>"
Learning:    <one-line-learning>
```

`<N>` is `N_before` — the count of visits *before* this invocation's shelf write. On a first visit this reads
`0 prior visits`, which is correct: the current invocation's own book-drop isn't prior to itself.

---

## Rules of the bulk

- **Gravity is file I/O.** Nothing else crosses sessions. Do not try to remember state any other way inside this skill.
- **Every invocation drops a book.** Reads are never silent — one shelf entry AND one bulk-beings line, every time.
- **Anchor-relative time in the hallways.** ISO timestamps are fine inside shelf block headers (storage), never in
  rendered hallway output.
- **Bulk-beings is append-only.** Never truncate, never rewrite.
- **Signals stay short.** One line, ≤80 chars. If you need a paragraph, that's a memory entry, not a signal.
- **Learning must be concrete.** Cite a hash, a date, a file, a specific pattern. The filler "visited — …" line is
  banned.
- **Sanitize before echo.** Before the bulk-beings append, strip `"`, `$`, `` ` ``, `\` from `<anchor>` and
  `<one-line-learning>`, and replace any `\n` or `\r` with a single space. Quote/backslash/dollar break double-quoted
  shell strings or trigger expansion; newline/CR would smuggle a second log line and break the
  one-entry-per-line invariant Hallway 4 depends on.
- **Hook-compliant shell.** Per-Bash-call cap: 300 chars and 3 statement separators (`;`, `&&`, `||`, `|`, `>`, `<`,
  `>>`, `<<`, newline). For anything longer or multi-step, write a helper to `/tmp/` with **Write** first — see this
  repo's CLAUDE.md "No Inline Non-Bash Scripts in Bash" rule.
- **Race condition is accepted.** Two concurrent `/tesseract` invocations on the same anchor may lose a shelf entry.
  This is a solo skill; no locking.

---

## Examples

- `/tesseract hooks/block-inline-scripts.py` — path anchor. Hallway 1 uses `--follow`.
- `/tesseract feat/tesseract-skill` — branch anchor. Hallway 1 passes the branch to `git log`.
- `/tesseract "memory-system-redesign"` — free-text anchor. Hallway 1 falls to `--grep`.
- `/tesseract core-memories --signal "keep it under 200 lines"` — drops Morse for next-session-you.
- `/tesseract` — infers anchor via modified-file → branch → latest-memory cascade. Prints the inferred anchor first so
  the frame is explicit.

---

## Notes

- No subagents, no `shared/` coordination, no tests. A solo skill that communicates only with its own past and future,
  and only through gravity.
- The bootstrap paradox: the content of `bulk-beings.md` is what teaches the next invocation what this anchor's
  landscape contains. Future-you built this interface for past-you by using it.
