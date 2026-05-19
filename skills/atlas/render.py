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
    body = "\n".join(sections)
    return _BASELINE.replace("{{BODY}}", body).replace("{{WARNINGS}}", "")


_BASELINE = (
    "<!doctype html>\n"
    '<html lang="en">\n'
    '<head><meta charset="utf-8"><title>atlas</title></head>\n'
    "<body>{{WARNINGS}}{{BODY}}</body>\n"
    "</html>\n"
)
