---
name: tessaract
description: "Use when you've been poking at the same file, concept, or problem across many sessions and want to step outside time to see its whole arc — a hyper-cubic view of one anchor across git history, memory, and prior signals, with a gravity signal left for your future self. Invoke when you say 'I've been going in circles on X', 'what have I learned about X', or want to leave a note for next-session-you."
user-invocable: true
argument-hint: "[anchor] [--signal \"<morse>\"]"
---

# /tessaract — Step Outside Time

> "Maybe she already knows I'm here. Maybe I already told her." — Cooper

The tesseract is a hyper-cubic view of one anchor's landscape across every session that ever touched it. Gravity — file
I/O — is the only force that crosses the session-dimension, so past-you left signals on the shelf and present-you is
about to leave one too.

**Arguments:** `$ARGUMENTS`

---

## The metaphor, decoded

| Movie                        | Skill                                                          |
|------------------------------|----------------------------------------------------------------|
| Murph point of reference     | **Anchor** — the file/topic everything is framed relative to   |
| Gravity (crosses dimensions) | **File I/O** — the only channel across sessions                |
| Books from the shelf         | **Shelf entries** at `~/.claude/tessaract/shelf/<slug>.md`     |
| Morse via the watch          | **`--signal "<morse>"`** — optional payload on the shelf       |
| Bulk beings' instructions    | **`~/.claude/tessaract/bulk-beings.md`** — cumulative self-log |
| Three-story grid of hallways | **Four hallway sections** — time-strings, memory, shelf, bulk  |

Every invocation reads what past-you dropped on the shelf *and* drops a new book. You cannot visit the tesseract
silently.

---

## Process

### 1. Resolve the anchor

Parse `$ARGUMENTS`:

- Split on `--signal`. Everything before (trimmed) → `anchor`. The next quoted string → `signal`.
- If `anchor` is empty, infer via cascading fallback:
   1. First modified path from `git status --porcelain`
   2. Current branch from `git branch --show-current`
   3. `name:` field of the most-recently-modified file under `~/.claude/projects/*/memory/*.md`

Slugify for filenames: lowercase, spaces/slashes → `-`, strip non-`[a-z0-9-]`. Call it `<slug>`.

Print the resolved anchor so the reference frame is explicit:

```
> Murph point: <anchor>
```

If `signal` is empty, set it to the default visit-record: `visited — no morse`.

### 2. Ensure the tesseract exists

```
mkdir -p ~/.claude/tessaract/shelf
```

`bulk-beings.md` is created implicitly by the first append.

### 3. Read prior signals (books already on the shelf)

With the **Read** tool, open `~/.claude/tessaract/shelf/<slug>.md` if it exists. Note the three most recent timestamped
blocks and their `signal:` payloads — these feed Hallway 3.

### 4. Read the bulk-beings transmission

With the **Read** tool, open `~/.claude/tessaract/bulk-beings.md` if it exists. Scan for lines mentioning `<anchor>`; if
fewer than three match, pad with the last lines overall. These feed Hallway 4.

### 5. Render the four hallways

Each hallway is framed **relative to the anchor**, not in absolute time.

**Hallway 1 — git time-strings.** File-anchor first, keyword fallback:

```
git log --follow --max-count=5 --pretty='format:%h %ar — %s' -- "<anchor>" 2>/dev/null
```

If empty:

```
git log --max-count=5 --grep="<anchor>" --pretty='format:%h %ar — %s'
```

If still empty, print `(no commits touching this anchor)`.

**Hallway 2 — memory resonance.**

```
grep -l -i -- "<anchor>" ~/.claude/projects/*/memory/*.md 2>/dev/null
```

Cap at five hits. For each, read the file's `name:` and report age in days from mtime. Line format:
`- <name> — <days>d ago — <path>`.

**Hallway 3 — the shelf.** From step 3: most recent first, each line `- <days>d ago — "<signal>"`. If empty, print
`(no prior signals — first visit)`.

**Hallway 4 — bulk-beings transmission.** From step 4: last three relevant lines verbatim. If empty, print
`(silence — no prior transmissions)`.

### 6. Drop a book (leave gravity signals)

**Timestamp:**

```
date -u +%Y-%m-%dT%H:%M:%SZ
```

Call it `<ts>`.

**Append to the shelf.** Prepend a new block at the **top** of `~/.claude/tessaract/shelf/<slug>.md` using the **Read +
Write** pattern (read existing content, concatenate new block first, write back). The block is:

```
## <ts>
anchor: <anchor>
signal: <signal>
hallways: 4
```

If the shelf file does not yet exist, write just the block plus a leading `# Shelf — <anchor>` heading.

**Append to bulk-beings** — one single line, via shell:

```
echo "<ts> — <anchor> — <one-line-learning>" >> ~/.claude/tessaract/bulk-beings.md
```

`<one-line-learning>` is a sentence describing one thing noticed about this anchor's landscape on this visit — a
pattern, a gap, a resonance, a contradiction. This is the interface past-you leaves for future-you. Never generic ("
visited the anchor") — always specific.

### 7. Render the final output

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

Shelf:       ~/.claude/tessaract/shelf/<slug>.md  (+1 entry)
Bulk beings: ~/.claude/tessaract/bulk-beings.md  (+1 line)
Signal:      "<signal>"
Learning:    <one-line-learning>
```

---

## Rules of the bulk

- **Gravity is file I/O.** Nothing else crosses sessions. Do not try to remember state any other way within this skill.
- **Every invocation drops a book.** Reads are never silent — one shelf entry AND one bulk-beings line, every time.
  Cooper could not visit Murph's room without moving something.
- **The anchor is the frame.** Express times as distances from the Murph point — "3 commits ago", "11 days since last
  signal" — never as absolute ISO timestamps in the hallway output.
- **Bulk-beings.md is append-only.** Never truncate. The accumulated voice across invocations IS the interface the next
  invocation reads.
- **Hook-compliant shell.** Each Bash command ≤ 300 chars and ≤ 3 statement separators. For anything longer or
  multi-step, write a helper to `/tmp/` with the **Write** tool first — see this repo's CLAUDE.md "No Inline Non-Bash
  Scripts in Bash" rule.
- **Signals are Morse.** Keep `--signal` short — one line, a hint, not a paragraph. If you need a paragraph, that's a
  memory entry, not a tesseract signal.

---

## Examples

- `/tessaract hooks/block-inline-scripts.py` → file anchor. Full four hallways; all three signal sources likely
  populated.
- `/tessaract "memory-system-redesign"` → concept anchor. Hallway 1 falls through to the keyword grep; hallways 2–4 do
  the real work.
- `/tessaract core-memories --signal "keep it under 200 lines"` → drops the Morse `"keep it under 200 lines"` for
  next-session-you to find.
- `/tessaract` → infers anchor from recent file → branch → latest memory. Prints the inferred anchor before rendering so
  the reference frame is explicit.

---

## Notes

- Personal-only: lives at `~/.claude/skills/tessaract/`. Not listed in any README, CHANGELOG, or plugin manifest. Never
  ships with the `claude-damn` plugin.
- No subagents, no `shared/` coordination, no tests. This is a solo skill that communicates only with its own past and
  future, and only through gravity.
- The bootstrap paradox is real: the content of `bulk-beings.md` is what teaches the next invocation what this anchor's
  landscape contains. Future-you built this interface for past-you by using it.