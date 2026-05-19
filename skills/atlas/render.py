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
    body = "\n".join(sections)
    return _BASELINE.replace("{{BODY}}", body).replace("{{WARNINGS}}", "")


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
