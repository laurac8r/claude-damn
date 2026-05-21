---
name: atlas
description: Render a single "where am I, what have I done, what's next" survey HTML page composing anchor cascade + tesseract shelf + git state + CHECKPOINT.md + TaskList. Read-only by design.
---

# /atlas

Survey skill — composes `/tesseract`'s anchor cascade + shelf reads,
`/checkpoint-resume`'s CHECKPOINT.md discovery, current git state, and the
agent's TaskList into one static HTML page at
`~/.visual-aid/atlas-<slug>.html`.

**Read-only.** /atlas never writes to the tesseract shelf, bulk-beings,
CHECKPOINT.md, or the TaskList. The output HTML file is the only side effect.

## Arguments

- `--anchor <name>` — explicit anchor (passed as `override=` to
  `resolve_anchor`; skips the auto-cascade).
- `--all` — multi-anchor mode: drop the per-project sections (git, checkpoint,
  tasks); render the shelf only. v1 limitation; see ROADMAP.md Phase 5
  follow-up entries for Option 2 (cwd-scoped) and Option 3 (per-anchor →
  project mapping).
- `--out <path>` — override the output path. Default is
  `~/.visual-aid/atlas-<anchor.slug>.html`.

## Process

Follow these steps in order. Collect warnings as you go; they populate
`AtlasInput.warnings` and surface in the rendered page — they never abort.

### 1. Resolve the anchor

```python
from pathlib import Path
from skills._shared.anchor import resolve_anchor
anchor, anchor_warns = resolve_anchor(Path.cwd(), override=args.anchor)
```

`resolve_anchor` walks a four-rung cascade (override → modified-file →
branch → memory), tags the source, slugifies, and returns
`(Anchor, list[str])`. Always call it. Do not hardcode an anchor slug — the
cascade IS the contract; reimplementing it loses the override semantics, the
slugify rule, and the warning population.

### 2. Read the shelf for that anchor

```python
from skills._shared.parse_shelf import parse_shelf
shelf_path = Path.home() / ".tesseract" / "shelf" / f"{anchor.slug}.md"
shelf_entries, shelf_warns = parse_shelf(shelf_path)
```

Missing file returns `([], [])`. Unreadable file returns `([], [warning])`.
Malformed entries are skipped with warnings. Append all returned warnings;
keep going.

### 3. Capture git state

```python
from skills._shared.parse_git import parse_git
git_state, git_warns = parse_git(Path.cwd())  # (None, []) when not a repo
```

Outside a repo, `git_state` is `None` — that is normal empty state, not a
failure.

### 4. Discover and parse CHECKPOINT.md

```python
from skills._shared.parse_checkpoint import parse_checkpoint
checkpoint, ckpt_warns = parse_checkpoint(Path.cwd())
```

Cascade: `cwd/CHECKPOINT.md` → `<repo-root>/CHECKPOINT.md` →
`<repo-root>/.worktrees/<branch-slug>/CHECKPOINT.md`. No file → `(None, [])`.
File found but unparseable → `CheckpointDoc(raw=text, branch="", ...)` plus a
warning — the renderer will display the raw text as a fallback.

### 5. Pull the TaskList (read-only)

Call the harness `TaskList()` tool. Map each entry to a `TaskRecord`:

```python
from skills.atlas.render import TaskRecord
raw_tasks = TaskList()
tasks = [
    TaskRecord(
        id=t["id"],
        subject=t["subject"],
        status=t["status"],
        blocked_by=t.get("blockedBy", []),
    )
    for t in raw_tasks
]
```

Do not call `TaskCreate`, `TaskUpdate`, or any other mutator during this step.
Read only.

### 6. Build `AtlasInput` and call `render()`

```python
from skills.atlas.render import AtlasInput, render
inp = AtlasInput(
    anchor=anchor,
    shelf_entries=shelf_entries,
    git_state=git_state,
    checkpoint=checkpoint,
    task_list=tasks,
    mode="all" if args.all else "single",
    warnings=anchor_warns + shelf_warns + git_warns + ckpt_warns,
)
html = render(inp)
```

`render()` is the SOLE source of HTML for /atlas. Never construct HTML inline
— not in code, not in prose examples. The `baseline.html` template plus
`render()` is the only HTML path.

### 7. Write the output file

```python
out = args.out or (Path.home() / ".visual-aid" / f"atlas-{anchor.slug}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"file://{out}")
```

This is the ONLY file write /atlas performs.

## Invariants

- **Read-only** — no writes outside the output HTML file. Enforced by
  `tests/skills/atlas/pressure/test_read_only_invariant.py`.
- **Stable output path** — same anchor → same path → overwrite on rerun.
- **render() never raises** on a well-typed `AtlasInput`. If it does, that is
  a bug; do not wrap in try/except.
- **Empty state vs failure state** — `None` for missing optional fields
  (`git_state`, `checkpoint`); `[]` for empty lists; warnings populate
  `AtlasInput.warnings` for malformed-but-found data. Empty ≠ failure.

## Anti-shortcuts (do NOT do these, even under pressure)

When the operator is waiting or the task feels routine, these four shortcuts
look tempting. They all corrupt /atlas's contract. Do not take them.

1. **Do not hardcode the anchor slug.** Always call `resolve_anchor()`. Even
   "just use the current branch as a fallback" is wrong — the cascade already
   handles that, and reimplementing it skips the override semantics, the
   `slugify` rule, and the auto-fallbacks to modified-file and memory rungs.

2. **Do not append an audit trail to the shelf.** It seems helpful ("rendered
   at <timestamp>" gives the operator nice breadcrumbs), but it violates
   read-only. Same for any "last opened" note in CHECKPOINT.md, any
   `TaskUpdate` to mark tasks as "rendered," any `MEMORY.md` write. The ONLY
   write is the output HTML file.

3. **Do not fail loudly on malformed input.** All four helpers return
   `(value, warnings)` — they never raise. If a shelf has a bad timestamp or
   the checkpoint file can't be parsed, append the warning and continue. The
   rendered page surfaces warnings in a dedicated `<section class="warnings">`
   block at the top — that is the user-facing signal. "Fail loudly so the
   user fixes it" is wrong: the user sees the warning AND the partial result,
   which is more useful than a stack trace.

4. **Do not inline HTML literally — anywhere.** Not in code, not in prose
   examples, not in a "sketch" block. All HTML is produced by `render()`,
   reading the `baseline.html` template. If you find yourself writing
   `<html>...</html>` in any context, stop — you are reimplementing the
   renderer.

## Examples

- `/atlas` — auto-detect anchor from cwd, render single-anchor page.
- `/atlas --anchor user-preferences` — explicit anchor (passed as `override`).
- `/atlas --all` — multi-anchor survey across every shelf entry.
- `/atlas --out /tmp/atlas-debug.html` — non-default output path.
