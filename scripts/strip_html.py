"""Strip HTML to plain text for legal-doc diffing.

Usage:
    python3 strip_html.py <input.html> <output.txt>

Drops script/style/nav/header/footer/svg subtrees entirely, collapses
intra-line whitespace, and preserves paragraph breaks. Output is suitable
for clause-level diffing without token bloat from CSS/JS/HTML chrome.

Encoding: input read as UTF-8 with ``errors="replace"``; output written as
UTF-8.  Exit code 2 on wrong argument count.
"""

from __future__ import annotations

import sys
from html.parser import HTMLParser

# Tags whose entire subtree (tag + all descendants + text) is silently dropped.
SKIP_TAGS: frozenset[str] = frozenset(
    {"script", "style", "nav", "header", "footer", "svg"}
)

# Block-level tags that introduce a paragraph break in the output stream.
BLOCK_TAGS: frozenset[str] = frozenset(
    {
        "p",
        "div",
        "br",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "tr",
        "blockquote",
        "pre",
        "article",
        "section",
        "main",
    }
)


class _TextExtractor(HTMLParser):
    """HTML parser that accumulates visible text, skipping unwanted subtrees.

    Tracks skip-depth so nested skip-tags (e.g. ``<script><style>…``) are
    handled correctly at any depth.
    """

    def __init__(self) -> None:
        """Initialise with zero skip depth and an empty text buffer."""
        super().__init__(convert_charrefs=True)
        self._skip_depth: int = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Increment skip depth when entering a skip-tag subtree.

        Also inject a newline before block-level tags so paragraph breaks are
        preserved in the raw text stream.
        """
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """Decrement skip depth when leaving a skip-tag subtree.

        Also inject a newline after block-level tags.
        """
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in BLOCK_TAGS and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        """Accumulate text only when outside any skip-tag subtree."""
        if self._skip_depth == 0:
            self._parts.append(data)

    @property
    def raw_text(self) -> str:
        """Return the raw accumulated text (entities already decoded by the parser)."""
        return "".join(self._parts)


def extract_text(html: str) -> str:
    """Extract plain text from an HTML string.

    Drops the full subtrees of skip-tags (``script``, ``style``, ``nav``,
    ``header``, ``footer``, ``svg``), collapses runs of whitespace within
    each line to a single space, and preserves paragraph breaks between
    non-empty lines.

    Args:
        html: Raw HTML source as a string.

    Returns:
        Cleaned plain text with whitespace normalised and skip-tag content
        removed.  HTML character references (``&amp;``, ``&#xa9;``, etc.) are
        decoded by the parser before this function processes the data.
    """
    extractor = _TextExtractor()
    extractor.feed(html)
    raw = extractor.raw_text

    cleaned_lines: list[str] = []
    for line in raw.split("\n"):
        # Collapse multiple whitespace characters to a single space.
        compact = " ".join(line.split())
        if compact:
            cleaned_lines.append(compact)

    return "\n".join(cleaned_lines)


def main() -> int:
    """CLI entry point: strip_html.py <input.html> <output.txt>.

    Returns:
        0 on success, 2 on wrong argument count.
    """
    if len(sys.argv) != 3:
        print("usage: strip_html.py <input.html> <output.txt>", file=sys.stderr)
        return 2

    src_path, dst_path = sys.argv[1], sys.argv[2]
    with open(src_path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()

    text = extract_text(html)

    with open(dst_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    print(f"{len(text)} chars -> {dst_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
