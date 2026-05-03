"""Render the tesseract shelf as a single self-contained HTML visual aid.

Used by the /tesseract --visual flag. Pure-Python, stdlib only. Read-only:
never writes to the shelf or bulk-beings files.

CLI:
    python3 render_visual.py [--shelf DIR] [--bulk FILE] [--out FILE] [--today YYYY-MM-DD]

Defaults point at the operator's live tesseract
(``~/.tesseract/``) and ``/tmp/visual-aid-tesseract.html``.
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

TS_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}Z", re.MULTILINE)
RECORD_RE = re.compile(
    r"^anchor:\s*(?P<anchor>.*?)\s+signal:\s*(?P<signal>.*?)\s+hallways:\s*\d+\s*$",
    re.MULTILINE,
)

HOME = Path.home()
DEFAULT_SHELF = HOME / ".tesseract" / "shelf"
DEFAULT_BULK = HOME / ".tesseract" / "bulk-beings.md"
DEFAULT_OUT = Path("/tmp/visual-aid-tesseract.html")

Heat = str  # "hot" | "warm" | "cool" | "cold"


@dataclass(frozen=True)
class Anchor:
    slug: str
    anchor: str
    visits: int
    first: str | None
    last: str | None
    signals: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "slug": self.slug,
            "anchor": self.anchor,
            "visits": self.visits,
            "first": self.first,
            "last": self.last,
            "signals": list(self.signals),
        }


# ---------- parsing ----------


def parse_shelf(path: Path) -> dict:
    """Parse one shelf file into an anchor record dict."""
    text = path.read_text(encoding="utf-8", errors="replace")
    slug = path.stem
    visits = TS_RE.findall(text)
    records = list(RECORD_RE.finditer(text))
    anchor_name = records[0].group("anchor").strip() if records else slug
    # Shelf prepends → records[0] is newest → visits[-1] is earliest (oldest).
    first = visits[-1][0] if visits else None
    last = visits[0][0] if visits else None
    seen: set[str] = set()
    signals: list[str] = []
    for m in records:
        s = m.group("signal").strip().strip('"')
        if not s or s == "—" or s in seen:
            continue
        seen.add(s)
        signals.append(s)
    return {
        "slug": slug,
        "anchor": anchor_name,
        "visits": len(visits),
        "first": first,
        "last": last,
        "signals": signals,
    }


def load_shelf(shelf_dir: Path) -> list[dict]:
    anchors = [parse_shelf(p) for p in sorted(shelf_dir.glob("*.md"))]
    anchors.sort(key=lambda a: (-a["visits"], a["last"] or ""))
    return anchors


# ---------- heat classifier ----------


def _days_ago(iso: str | None, today: date) -> int | None:
    if not iso:
        return None
    return (today - date.fromisoformat(iso)).days


def classify_heat(visits: int, last: str | None, *, today: date) -> Heat:
    """Bucket an anchor by frequency × recency."""
    d = _days_ago(last, today)
    d_eff = 999 if d is None else d
    if visits >= 4 or (visits >= 2 and d_eff <= 1):
        return "hot"
    if visits >= 2 or d_eff <= 1:
        return "warm"
    if d_eff <= 3:
        return "cool"
    return "cold"


# ---------- rendering ----------


def _rel(iso: str | None, today: date) -> str:
    d = _days_ago(iso, today)
    if d is None:
        return "—"
    if d == 0:
        return "today"
    if d == 1:
        return "1d ago"
    return f"{d}d ago"


def _card(a: dict, today: date) -> str:
    slug = html.escape(a["slug"])
    anchor = html.escape(a["anchor"])
    visits = a["visits"]
    first = a["first"]
    last = a["last"]
    signals = a["signals"][:3]
    heat_class = classify_heat(visits, last, today=today)
    max_dots = 7
    dots = "●" * min(visits, max_dots) + "○" * max(0, max_dots - visits)
    date_line = f"first {_rel(first, today)} · last {_rel(last, today)}"
    if first == last:
        date_line = f"single visit · {_rel(last, today)}"
    sig_html = ""
    if signals:
        chips = "".join(
            f'<li><span class="chip">{html.escape(s)}</span></li>' for s in signals
        )
        sig_html = f'<ul class="sigs" aria-label="recent signals">{chips}</ul>'
    s_plural = "s" if visits != 1 else ""
    return f"""
      <article class="card heat-{heat_class}" aria-labelledby="a-{slug}"
               data-visits="{visits}" data-last="{last or ""}" data-first="{first or ""}" data-slug="{slug}">
        <header class="card-head">
          <h3 id="a-{slug}">{anchor}</h3>
          <p class="meta">
            <span class="visits" aria-label="{visits} visit{s_plural}">
              <span class="dots" aria-hidden="true">{dots}</span>
              <span class="vcount">{visits}×</span>
            </span>
            <span class="dates">{date_line}</span>
          </p>
        </header>
        {sig_html}
      </article>"""


_CSS = """
      :root {
        --bg: #0b0d14; --fg: #e8ecf1; --muted: #9aa3af; --dim: #6b7280;
        --card: #161a26; --card-hot: #2a1d2e; --card-warm: #1f2231;
        --card-cool: #161a26; --card-cold: #11141c;
        --border: #252a3a; --border-hot: #c07aa8; --border-warm: #7cc4ff;
        --accent: #a5c9ff; --accent-2: #ffd8a8; --ring: #ffd866;
        --chip: #1a2132; --chip-fg: #cbd5e1;
        --radius: 12px; --pad: clamp(14px, 3vw, 26px);
      }
      @media (prefers-color-scheme: light) {
        :root {
          --bg: #faf8f2; --fg: #14161c; --muted: #4a5060; --dim: #6b7280;
          --card: #ffffff; --card-hot: #fff4ea; --card-warm: #f2f7ff;
          --card-cool: #ffffff; --card-cold: #f4f2ec;
          --border: #d8dae0; --border-hot: #b45309; --border-warm: #0057b3;
          --accent: #0057b3; --accent-2: #b45309; --ring: #8c5a00;
          --chip: #eef1f7; --chip-fg: #1f2433;
        }
      }
      * { box-sizing: border-box; }
      html, body {
        margin: 0; background: var(--bg); color: var(--fg);
        font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      }
      header.site, footer.site, main {
        max-width: 88ch; margin: 0 auto; padding: var(--pad);
      }
      h1 {
        font-size: clamp(1.8rem, 4vw, 2.6rem); line-height: 1.1;
        margin: 0 0 0.2em; letter-spacing: -0.01em;
      }
      .tagline { color: var(--muted); margin: 0 0 0.6em; font-size: 1rem; }
      .stats {
        display: grid; gap: 0.75rem; list-style: none; padding: 0;
        grid-template-columns: repeat(auto-fit, minmax(min(140px, 100%), 1fr));
        margin: 1rem 0 0.5rem;
      }
      .stats li {
        background: var(--card); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 0.7rem 0.9rem;
      }
      .stats .k { display: block; font-size: 0.78rem; letter-spacing: 0.04em;
        text-transform: uppercase; color: var(--muted); }
      .stats .v { display: block; font-size: 1.5rem; font-weight: 600;
        margin-top: 0.1rem; font-variant-numeric: tabular-nums; }
      .stats .sub { display: block; font-size: 0.85rem; color: var(--dim); }
      h2 { font-size: clamp(1.1rem, 2vw, 1.3rem); margin: 1.8em 0 0.35em; letter-spacing: 0.01em; }
      .hallways {
        display: grid; gap: 0.6rem;
        grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr));
        margin: 0.5rem 0 1.2rem;
      }
      .hallways .hw { background: var(--card); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 0.7rem 0.9rem; }
      .hallways .hw strong { color: var(--accent); }
      .hallways .hw p { margin: 0.15rem 0 0; color: var(--muted); font-size: 0.9rem; }

      .mode-toggle {
        display: inline-flex; gap: 0;
        border: 1px solid var(--border); border-radius: 999px;
        padding: 3px; background: var(--card); margin: 0.6rem 0 0.2rem;
      }
      .mode-toggle button {
        appearance: none; background: transparent; color: var(--fg);
        border: 0; font: inherit; font-size: 0.88rem;
        padding: 0.45rem 0.9rem; border-radius: 999px; cursor: pointer; min-height: 44px;
      }
      .mode-toggle button[aria-pressed="true"] {
        background: var(--accent); color: var(--bg); font-weight: 600;
      }
      .mode-toggle .label {
        align-self: center; padding: 0 0.6rem 0 0.2rem; color: var(--muted);
        font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em;
      }
      body[data-mode="interactive"] .card {
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
      }
      body[data-mode="interactive"] .card:hover,
      body[data-mode="interactive"] .card:focus-within {
        transform: translateY(-2px); border-color: var(--accent);
        box-shadow: 0 6px 20px -10px rgba(0, 0, 0, 0.6);
      }
      .sort-controls { display: none; flex-wrap: wrap; gap: 0.4rem;
        margin: 0.5rem 0 0.4rem; align-items: center; }
      body[data-mode="interactive"] .sort-controls { display: flex; }
      .sort-controls .label {
        color: var(--muted); font-size: 0.82rem;
        text-transform: uppercase; letter-spacing: 0.06em; margin-right: 0.2rem;
      }
      .sort-controls button {
        appearance: none; background: var(--card); color: var(--fg);
        border: 1px solid var(--border); border-radius: 999px; font: inherit;
        font-size: 0.85rem; padding: 0.35rem 0.8rem; cursor: pointer; min-height: 44px;
      }
      .sort-controls button[aria-pressed="true"] {
        background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 600;
      }

      .legend { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem;
        font-size: 0.88rem; color: var(--muted); margin: 0.4rem 0 1rem; }
      .legend .sw { display: inline-block; width: 0.85em; height: 0.85em;
        border-radius: 3px; margin-right: 0.35em; vertical-align: -0.1em;
        border: 1px solid var(--border); }

      .grid {
        display: grid; gap: 0.8rem;
        grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr));
      }
      .card {
        background: var(--card); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 0.8rem 0.95rem 0.9rem;
        position: relative; overflow: hidden;
      }
      .card::before {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0;
        width: 3px; background: var(--border);
      }
      .card.heat-hot  { background: var(--card-hot);  border-color: var(--border-hot); }
      .card.heat-hot::before  { background: var(--border-hot); width: 5px; }
      .card.heat-warm { background: var(--card-warm); border-color: var(--border-warm); }
      .card.heat-warm::before { background: var(--border-warm); width: 4px; }
      .card.heat-cool::before { background: var(--accent); opacity: 0.4; }
      .card.heat-cold { background: var(--card-cold); }
      .card.heat-cold::before { background: var(--dim); }
      .card h3 { font-size: 1.02rem; margin: 0 0 0.35em; line-height: 1.25; word-break: break-word; }
      .card .meta {
        display: flex; flex-wrap: wrap; align-items: center;
        gap: 0.4rem 0.75rem; margin: 0 0 0.35em;
        font-size: 0.85rem; color: var(--muted); font-variant-numeric: tabular-nums;
      }
      .visits { display: inline-flex; align-items: baseline; gap: 0.3rem; }
      .dots { letter-spacing: 0.08em; color: var(--accent-2); font-size: 0.9rem; }
      .card.heat-hot .dots { color: var(--border-hot); }
      .vcount { color: var(--fg); font-weight: 600; }
      .sigs { list-style: none; padding: 0; margin: 0.4em 0 0;
        display: flex; flex-wrap: wrap; gap: 0.35rem; }
      .chip { display: inline-block; background: var(--chip); color: var(--chip-fg);
        font-size: 0.78rem; padding: 0.2em 0.55em; border-radius: 999px;
        border: 1px solid var(--border); max-width: 100%; overflow-wrap: anywhere; }

      :is(a, button, input, select, textarea, summary, [tabindex], [contenteditable]):focus-visible {
        outline: 3px solid var(--ring); outline-offset: 2px; border-radius: 4px;
      }
      a { color: var(--accent); }

      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
          scroll-behavior: auto !important;
        }
      }
      @media print {
        :root {
          --bg: #fff; --fg: #000; --muted: #333; --dim: #555;
          --card: #fff; --card-hot: #fff; --card-warm: #fff;
          --card-cool: #fff; --card-cold: #fff;
          --border: #999; --border-hot: #333; --border-warm: #555;
          --accent: #003a80; --accent-2: #6b3c00; --chip: #f3f3f3;
        }
        .grid { grid-template-columns: 1fr 1fr !important; }
        .stats, .hallways { grid-template-columns: 1fr 1fr !important; }
        .card { break-inside: avoid; }
        main, header.site, footer.site { max-width: 100% !important; padding: 0.8em !important; }
        .mode-toggle, .sort-controls { display: none !important; }
      }
"""

_JS = """
      (function () {
        var body = document.body;
        var toggle = document.querySelector('.mode-toggle');
        var sortCtrls = document.querySelector('.sort-controls');
        var grid = document.querySelector('.grid');
        if (!toggle || !grid) return;

        function setMode(mode) {
          body.setAttribute('data-mode', mode);
          toggle.querySelectorAll('button').forEach(function (b) {
            b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
          });
          try { localStorage.setItem('tesseract-mode', mode); } catch (e) {}
        }

        toggle.addEventListener('click', function (e) {
          var t = e.target.closest('button[data-mode]');
          if (t) setMode(t.dataset.mode);
        });

        var saved = null;
        try { saved = localStorage.getItem('tesseract-mode'); } catch (e) {}
        setMode(saved === 'interactive' ? 'interactive' : 'non-interactive');

        if (!sortCtrls) return;
        var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
        var sorters = {
          visits: function (a, b) {
            return (+b.dataset.visits) - (+a.dataset.visits) || (b.dataset.last || '').localeCompare(a.dataset.last || '');
          },
          recent: function (a, b) { return (b.dataset.last || '').localeCompare(a.dataset.last || ''); },
          oldest: function (a, b) { return (a.dataset.first || '').localeCompare(b.dataset.first || ''); },
          alpha:  function (a, b) { return (a.dataset.slug || '').localeCompare(b.dataset.slug || ''); }
        };
        sortCtrls.addEventListener('click', function (e) {
          var t = e.target.closest('button[data-sort]');
          if (!t) return;
          var key = t.dataset.sort;
          sortCtrls.querySelectorAll('button').forEach(function (b) {
            b.setAttribute('aria-pressed', String(b === t));
          });
          cards.sort(sorters[key]);
          var frag = document.createDocumentFragment();
          cards.forEach(function (c) { frag.appendChild(c); });
          grid.appendChild(frag);
        });
      })();
"""


def render_html(anchors: list[dict], *, bulk_lines: int, today: date) -> str:
    total = len(anchors)
    visits = sum(a["visits"] for a in anchors)
    if not anchors:
        return _empty_doc(today)
    buckets = {"hot": 0, "warm": 0, "cool": 0, "cold": 0}
    for a in anchors:
        buckets[classify_heat(a["visits"], a["last"], today=today)] += 1
    first_ever = min(anchors, key=lambda a: a["first"] or "9999")
    newest = max(anchors, key=lambda a: a["last"] or "")
    most_visited = max(anchors, key=lambda a: a["visits"])
    dated = [a["first"] for a in anchors if a["first"]]
    first_date = min(dated) if dated else today.isoformat()
    last_date = (
        max(a["last"] for a in anchors if a["last"]) if dated else today.isoformat()
    )
    span_days = (
        date.fromisoformat(last_date) - date.fromisoformat(first_date)
    ).days + 1
    cards = "\n".join(_card(a, today) for a in anchors)
    return f"""<!doctype html>
<!-- Generated by /tesseract --visual -->
<!-- Anchors: {total} · Visits: {visits} · Bulk lines: {bulk_lines} -->
<html lang="en" dir="auto">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Tesseract — full view ({total} anchors)</title>
    <style>{_CSS}</style>
  </head>
  <body>
    <header class="site">
      <h1>🧊 Tesseract — full view</h1>
      <p class="tagline">Every anchor on the shelf, sized by visit density. The four hallways collapse into one wall.</p>
      <div class="mode-toggle" role="group" aria-label="Display mode">
        <span class="label" id="mode-label">Mode</span>
        <button type="button" data-mode="non-interactive" aria-pressed="true" aria-describedby="mode-label">Non-interactive (a11y)</button>
        <button type="button" data-mode="interactive" aria-pressed="false" aria-describedby="mode-label">Interactive</button>
      </div>
      <ul class="stats" aria-label="Summary">
        <li><span class="k">Anchors</span><span class="v">{total}</span><span class="sub">books on the shelf</span></li>
        <li><span class="k">Visits</span><span class="v">{visits}</span><span class="sub">gravity signals dropped</span></li>
        <li><span class="k">Bulk lines</span><span class="v">{bulk_lines}</span><span class="sub">cross-anchor transmissions</span></li>
        <li><span class="k">Span</span><span class="v">{span_days}d</span><span class="sub">{first_date} → {last_date}</span></li>
      </ul>
    </header>
    <main>
      <section aria-labelledby="hallways">
        <h2 id="hallways">The four hallways</h2>
        <div class="hallways">
          <div class="hw"><strong>git</strong><p>commits touching the anchor — past-you in version control</p></div>
          <div class="hw"><strong>memory</strong><p>persistent notes citing the anchor — past-you in MEMORY.md</p></div>
          <div class="hw"><strong>shelf</strong><p>prior /tesseract visits to this anchor (one file per anchor)</p></div>
          <div class="hw"><strong>bulk-beings</strong><p>single append-only ledger of cross-anchor transmissions</p></div>
        </div>
      </section>

      <section aria-labelledby="highlights">
        <h2 id="highlights">Highlights</h2>
        <div class="hallways">
          <div class="hw"><strong>Most-visited</strong><p>{html.escape(most_visited["anchor"])} · {most_visited["visits"]}× · last {_rel(most_visited["last"], today)}</p></div>
          <div class="hw"><strong>Most recent</strong><p>{html.escape(newest["anchor"])} · last {_rel(newest["last"], today)}</p></div>
          <div class="hw"><strong>Oldest first-visit</strong><p>{html.escape(first_ever["anchor"])} · first {_rel(first_ever["first"], today)}</p></div>
          <div class="hw"><strong>Heat distribution</strong><p>hot {buckets["hot"]} · warm {buckets["warm"]} · cool {buckets["cool"]} · cold {buckets["cold"]}</p></div>
        </div>
      </section>

      <section aria-labelledby="shelf">
        <h2 id="shelf">The shelf — all {total} anchor{"s" if total != 1 else ""}</h2>
        <div class="sort-controls" role="group" aria-label="Sort anchors">
          <span class="label">Sort</span>
          <button type="button" data-sort="visits" aria-pressed="true">Visits</button>
          <button type="button" data-sort="recent" aria-pressed="false">Most recent</button>
          <button type="button" data-sort="oldest" aria-pressed="false">Oldest first-visit</button>
          <button type="button" data-sort="alpha" aria-pressed="false">A → Z</button>
        </div>
        <p class="legend" role="note">
          <span><span class="sw" style="background:var(--border-hot);"></span>hot (recent + revisited)</span>
          <span><span class="sw" style="background:var(--border-warm);"></span>warm</span>
          <span><span class="sw" style="background:var(--accent);opacity:0.4;"></span>cool</span>
          <span><span class="sw" style="background:var(--dim);"></span>cold (single, older)</span>
          <span aria-hidden="true">●</span><span>= one visit · dots cap at 7</span>
        </p>
        <div class="grid" role="list">{cards}
        </div>
      </section>
    </main>
    <footer class="site">
      <p style="color:var(--muted);font-size:0.85rem;margin:0;">
        Source: <code>~/.tesseract/shelf/*.md</code> &amp; <code>~/.tesseract/bulk-beings.md</code> · rendered {today.isoformat()}
      </p>
    </footer>
    <script>{_JS}</script>
  </body>
</html>
"""


def _empty_doc(today: date) -> str:
    return f"""<!doctype html>
<html lang="en" dir="auto">
  <head><meta charset="utf-8" /><title>Tesseract — empty shelf</title></head>
  <body><h1>🧊 Tesseract — empty shelf</h1>
  <p>No anchors yet. Run <code>/tesseract &lt;anchor&gt;</code> to drop the first book.</p>
  <p>Rendered {today.isoformat()}.</p></body></html>
"""


# ---------- orchestration ----------


def render_from_shelf(
    *, shelf_dir: Path, bulk_path: Path, out_path: Path, today: date
) -> Path:
    anchors = load_shelf(shelf_dir)
    bulk_lines = (
        bulk_path.read_text(encoding="utf-8", errors="replace").count("\n")
        if bulk_path.exists()
        else 0
    )
    doc = render_html(anchors, bulk_lines=bulk_lines, today=today)
    out_path.write_text(doc, encoding="utf-8")
    return out_path


# ---------- CLI ----------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Render the tesseract shelf as HTML.")
    p.add_argument("--shelf", type=Path, default=DEFAULT_SHELF, help="Shelf directory")
    p.add_argument("--bulk", type=Path, default=DEFAULT_BULK, help="Bulk-beings file")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output HTML path")
    p.add_argument(
        "--today",
        type=date.fromisoformat,
        default=None,
        help="Override today for relative dates (YYYY-MM-DD)",
    )
    args = p.parse_args(argv)
    today = args.today or date.today()
    out = render_from_shelf(
        shelf_dir=args.shelf, bulk_path=args.bulk, out_path=args.out, today=today
    )
    print(f"file://{out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
