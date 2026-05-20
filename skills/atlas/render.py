"""Pure renderer for /atlas — AtlasInput and render(inp) -> str."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from skills._shared.anchor import Anchor
from skills._shared.parse_checkpoint import CheckpointDoc
from skills._shared.parse_git import GitState
from skills._shared.parse_shelf import ShelfEntry


@dataclass(frozen=True)
class TaskRecord:
    id: str
    subject: str
    status: Literal["pending", "in_progress", "completed"]
    blocked_by: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AtlasInput:
    anchor: Anchor
    shelf_entries: list[ShelfEntry]
    git_state: GitState | None
    checkpoint: CheckpointDoc | None
    task_list: list[TaskRecord]
    mode: Literal["single", "all"]
    warnings: list[str] = field(default_factory=list)


def render(inp: AtlasInput) -> str:
    sections: list[str] = []
    sections.append(
        f'<section class="anchor"><h1>Anchor: {inp.anchor.slug}</h1></section>'
    )
    sections.append(_render_git_section(inp.git_state))
    sections.append(_render_shelf_section(inp.shelf_entries))
    sections.append(_render_checkpoint_section(inp.checkpoint))
    sections.append(_render_tasks_section(inp.task_list))
    body = "\n".join(sections)
    warnings_html = _render_warnings_section(inp.warnings)
    return _BASELINE.replace("{{BODY}}", body).replace("{{WARNINGS}}", warnings_html)


def _render_tasks_section(tasks: list[TaskRecord]) -> str:
    if not tasks:
        return (
            '<section class="tasks empty"><h2>Tasks</h2>'
            "<p>no active tasks</p></section>"
        )
    items = []
    for t in tasks:
        blocked = (
            '<span class="blocked">blocked by '
            f"{', '.join(_html_escape(b) for b in t.blocked_by)}</span>"
            if t.blocked_by
            else ""
        )
        items.append(
            f'<li class="task status-{t.status}">'
            f'<span class="status">{t.status}</span> '
            f'<span class="subject">{_html_escape(t.subject)}</span> '
            f"{blocked}</li>"
        )
    return f'<section class="tasks"><h2>Tasks</h2><ul>{"".join(items)}</ul></section>'


def _render_warnings_section(warnings: list[str]) -> str:
    if not warnings:
        return ""
    items = "".join(f"<li>{_html_escape(w)}</li>" for w in warnings)
    return f'<section class="warnings"><h2>⚠ Warnings</h2><ul>{items}</ul></section>'


def _render_checkpoint_section(ckpt: CheckpointDoc | None) -> str:
    if ckpt is None:
        return (
            '<section class="checkpoint empty"><h2>Checkpoint</h2>'
            "<p>no checkpoint saved</p></section>"
        )
    if not ckpt.branch and not ckpt.next_steps:
        # parse failed; show raw fallback
        return (
            '<section class="checkpoint warning">'
            "<h2>⚠ Checkpoint (parse failed)</h2>"
            f"<pre>{_html_escape(ckpt.raw)}</pre></section>"
        )
    parts = [
        f'<section class="checkpoint"><h2>Checkpoint — {_html_escape(ckpt.branch)}</h2>'
    ]
    if ckpt.current_state:
        parts.append(f'<p class="state">{_html_escape(ckpt.current_state)}</p>')
    parts.append(_render_list("Next Steps", ckpt.next_steps))
    parts.append(_render_list("Key Decisions", ckpt.key_decisions))
    parts.append(_render_list("Blockers", ckpt.blockers))
    parts.append("</section>")
    return "".join(parts)


def _render_list(title: str, items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{_html_escape(item)}</li>" for item in items)
    return f"<h3>{title}</h3><ul>{lis}</ul>"


def _render_shelf_section(entries: list[ShelfEntry]) -> str:
    if not entries:
        return (
            '<section class="shelf empty"><h2>Shelf</h2>'
            "<p>no shelf entries — first visit at this anchor</p></section>"
        )
    sorted_entries = sorted(entries, key=lambda e: e.date, reverse=True)
    items = "".join(
        f'<article class="shelf-entry"><time>{e.date.isoformat()}</time>'
        f"<pre>{_html_escape(e.body)}</pre></article>"
        for e in sorted_entries
    )
    return f'<section class="shelf"><h2>Shelf</h2>{items}</section>'


def _render_git_section(git: GitState | None) -> str:
    if git is None:
        return (
            '<section class="git empty"><h2>Git</h2><p>not in a git repo</p></section>'
        )
    parts = [f'<section class="git"><h2>Git — {_html_escape(git.branch)}</h2>']
    if git.ahead or git.behind:
        parts.append(f"<p>ahead {git.ahead} / behind {git.behind}</p>")
    if git.dirty:
        items = "".join(f"<li>{_html_escape(p)}</li>" for p in git.dirty)
        parts.append(f'<ul class="dirty">{items}</ul>')
    if git.recent_commits:
        items = "".join(f"<li>{_html_escape(s)}</li>" for s in git.recent_commits)
        parts.append(f'<ul class="commits">{items}</ul>')
    parts.append("</section>")
    return "".join(parts)


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_BASELINE = (
    "<!doctype html>\n"
    '<html lang="en">\n'
    '<head><meta charset="utf-8"><title>atlas</title></head>\n'
    "<body>{{WARNINGS}}{{BODY}}</body>\n"
    "</html>\n"
)
