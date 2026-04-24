---
name: visual-aid
description:
   Use when the user asks for a quick visual aid, visual explainer, concept
   card, one-pager, poster, cheat sheet, infographic, visual summary, summary
   card, or mini explainer page — especially from input like a block of text,
   attached images, an attached song (lyrics/audio), a web link, a CSV/dataset,
   a math formula, a code snippet to walk through, a tutorial's steps, a
   timeline, or an A-vs-B comparison. Triggers include "make me a quick visual
   aid", "turn this into a one-pager / cheat sheet / explainer", "summarize this
   visually", "give me a visual of", "explain this on a single page", "make a
   concept card for", "whip up a page about", "build a mini page that shows",
   "something I can paste into a doc explaining X", or any request to render a
   topic/text/link/image-set/song/data into a standalone page. Prefer this skill
   over frontend-design when the ask is an explanatory single-file page (not a
   production UI), over playground when the output is static information display
   (not an interactive configurator), and over a Markdown/code answer when the
   user explicitly wants a *page* (HTML). Produces a single self-contained HTML
   file that opens on double-click without a server.
---

# Visual Aid

## Overview

A **visual aid** is a single self-contained HTML file (one SPA) that presents a
topic clearly enough to show someone on a screen, print it, or paste it into a
doc. It favors clarity, hierarchy, and accessibility over interactivity. It
opens on double-click, has no build step, no external network fetches, and
renders well on phone and laptop.

This is the lightweight sibling of `frontend-design` (production UI) and
`playground` (interactive configurator). Reach for /visual-aid when the user
wants a readable page fast — not a dashboard, not a tool.

## Input shapes — pick a layout from the shape

Each input shape has a default layout. The defaults are starting points, not
mandates: if the content wants a different shape, deliver that shape.

| Input provided                      | Default layout                                                                                     |
| ----------------------------------- | -------------------------------------------------------------------------------------------------- |
| Block of text / concept prompt      | Hero title → intro line → 3–6 titled cards or numbered steps                                       |
| Attached image(s)                   | Annotated grid (captions as `<figcaption>`, always `alt`)                                          |
| Song (lyrics ± audio file)          | Lyrics-first column with highlighted chorus; `<audio controls>` if file given                      |
| Web link                            | Title + source line + 3–6 key points + "Read more" anchor back to the link                         |
| Dataset / CSV / numbers             | Chart-first (inline SVG or `<canvas>` rendered once, no JS framework) + 2–4 anchor callouts        |
| Math / equation / formula           | Large rendered expression (MathML or static SVG) + 2–3 "what each symbol means" rows               |
| Code snippet / function walkthrough | Preformatted block on the left/top, numbered annotations on the right/below tying lines to meaning |
| Tutorial / how-to steps             | Numbered vertical step list; each step has one action verb, one screenshot/diagram slot            |
| Timeline / history                  | Horizontal (wide screen) or vertical (narrow) ordered list with year/label → event → one-line why  |
| Comparison / A-vs-B / A-vs-B-vs-C   | Side-by-side columns (one per thing), shared attribute rows down the side                          |

If the shape is genuinely unclear from the input, ask **one** short question and
stop there (e.g., "grid comparison or single-story flow?"). Don't guess and
don't stack a default "mixed" layout — a confused layout is worse than a delayed
one. In non-interactive / one-shot contexts where you can't ask, pick the shape
closest to the dominant input and note your choice at the top of the file in an
HTML comment (`<!-- Input: text; layout: cards -->`).

## Output requirements

1. **One file, no server.** All CSS and JS inline inside `<style>`/`<script>`.
   No `<link rel=stylesheet>`, no `<script src>` pointing off-disk, no CDN
   imports unless the user explicitly approves them (fonts: use system stack).
   The file must open on double-click with no network.
2. **Semantic HTML, landmark-correct.** Exactly one `<h1>`. `<h2>`/`<h3>`
   descend in order — never skip a level. `<header>` and `<footer>` are
   **siblings of `<main>`**, not descendants (descendant `<header>`/`<footer>`
   lose their `banner`/`contentinfo` landmark roles). Use `<section>` with a
   heading for each top-level chunk. Prefer `<div class="card">` over
   `<article>` unless the card is genuinely independently redistributable
   content.
3. **Accessible by default** (from a11y-debugging):
   - `alt` on every `<img>` (`alt=""` only for decorative — prove it's
     decorative before choosing empty).
   - `<html lang="...">` matches the primary content language. For non-English
     inline runs, add `lang` on the span.
   - Color contrast ≥ 4.5:1 for body text, ≥ 3:1 for large text and focus rings.
     If unsure, run a Lighthouse a11y audit (e.g. via the `chrome-devtools-mcp`
     plugin's `lighthouse_audit` tool, if installed).
   - `:focus-visible` ring on every interactive element — cover
     `a, button, input, select, textarea, summary, [tabindex], [contenteditable]`
     in the selector. Never `outline: none` without a replacement.
   - Tap targets ≥ 44×44 CSS px.
   - Respect `@media (prefers-reduced-motion: reduce)` — use the WCAG pattern
     `animation-duration: 0.01ms !important; transition-duration: 0.01ms !important`
     (not `transition: none !important`, which also kills focus/hover
     transitions you may add later).
   - Don't use color alone to convey meaning (pair with icon or text).
4. **Responsive, zoom-safe, print-safe.** Mobile-first. CSS grid / flex with
   `clamp()` for typography. No fixed pixel widths on content containers. The
   `minmax()` in your grid must allow columns to shrink below their min when the
   container is narrower (use `minmax(min(220px, 100%), 1fr)`). Include a
   `@media print` block that lightens backgrounds, collapses grids to one
   column, and drops decorative chrome — the skill's stated use cases include
   "print" and "paste into a doc."
5. **No information dump.** Pick 3–6 anchor points. If the source has more, the
   skill's job is to _choose_ — include the chosen anchors in an HTML comment at
   the top (`<!-- Anchors: X, Y, Z -->`) so the user can see what was curated
   out.
6. **No hardcoded color literals in rule bodies.** Every color goes through `--`
   custom properties set on `:root` (and re-set under
   `prefers-color-scheme: light`). `color: #fff` in a class body is a bug — it
   breaks dark mode and theming.
7. **Save path.** Default to `/tmp/visual-aid-<slug>.html` on macOS/Linux,
   `%TEMP%\visual-aid-<slug>.html` on Windows. If the user names a path, use it.
   Print the resolved `file://` URL on its own line. Put a
   `<!-- Generated from: "{one-line prompt summary}" -->` comment at the very
   top for traceability.

## Exporting to PDF

This skill produces HTML, not PDF. When the user asks for a PDF of the rendered
page, hand off to the operating system's print-to-PDF flow — don't reach for
`wkhtmltopdf`, headless Chrome scripts, or Playwright unless the user explicitly
requests automation.

**The OS-level dialogs that actually export PDF vary by platform.** The SOP
below is the macOS + Chrome path, which is the only one documented here. Other
platforms have different system dialogs; if the user is on Linux or Windows,
offer a short equivalent or ask what flow they prefer before prescribing one.

**macOS + Chrome SOP:**

1. `open <path/to/file.html>` from a shell.
2. In Chrome, adjust zoom if needed, then `⌘P`.
3. In Chrome's print preview, open the `More settings` dropdown and tune
   rendering settings there — paper size, margins, scale, headers/footers,
   background graphics.
4. Click `Print using system dialog… (⌥⌘P)`.
5. In the macOS Print dialog, click the `PDF` dropdown button (bottom left).
6. Choose the export target: **Save as PDF…** (default), Open in Preview, Save
   as Postscript…, Save to iCloud Drive, Save to Web Receipts, or Send in Mail.

**Why two stages:** Chrome's print preview tunes the _render_; the macOS Print
dialog tunes the _export target_. Skipping straight to the system dialog loses
Chrome's render controls; staying in Chrome limits the export destinations.

**Other platforms (not documented, pointers only):**

- **Linux + Chrome/Chromium:** `⌘P` → "Save as PDF" destination in Chrome's own
  dialog; GTK/Qt print dialogs vary by distro and don't always offer PDF
  directly.
- **Windows + Chrome/Edge:** `Ctrl+P` → "Microsoft Print to PDF" as the printer,
  or "Save as PDF" destination.
- **Firefox / Safari:** different dialog flows; Safari in particular goes
  straight to the native macOS dialog and skips Chrome's two-stage split.

If the user is on a platform that isn't macOS + Chrome, ask one question before
prescribing a flow rather than guessing from documentation written for a
different OS.

## Baseline template

When you need to scaffold, start from this skeleton. It is the minimum — fill
in, prune what you don't use, but never drop the a11y guards (motion, focus,
contrast, print).

```html
<!doctype html>
<!-- Generated from: "{{one-line prompt summary}}" -->
<!-- Anchors: {{X}}, {{Y}}, {{Z}} -->
<html lang="en" dir="auto">
   <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>{{Title}}</title>
      <style>
         :root {
            --bg: #0f1115;
            --fg: #e8ecf1;
            --muted: #9aa3af;
            --accent: #7cc4ff;
            --card: #1e2330;
            --ring: #ffd866;
            --border: #2a3040;
            --radius: 14px;
            --pad: clamp(16px, 3vw, 28px);
         }
         @media (prefers-color-scheme: light) {
            /* Dark-mode --accent/--ring fail 4.5:1 / 3:1 on white — re-pick per scheme. */
            :root {
               --bg: #fafaf7;
               --fg: #141821;
               --muted: #525863;
               --card: #ffffff;
               --accent: #0057b3;
               --ring: #b45309;
               --border: #e2e5ec;
            }
         }
         * {
            box-sizing: border-box;
         }
         html,
         body {
            margin: 0;
            background: var(--bg);
            color: var(--fg);
            font:
               16px/1.55 ui-sans-serif,
               system-ui,
               -apple-system,
               "Segoe UI",
               Roboto,
               sans-serif;
         }
         header.site,
         footer.site {
            max-width: 72ch;
            margin: 0 auto;
            padding: var(--pad);
         }
         main {
            max-width: 72ch;
            margin: 0 auto;
            padding: var(--pad);
         }
         h1 {
            font-size: clamp(1.8rem, 4vw, 2.6rem);
            line-height: 1.15;
            margin: 0 0 0.25em;
         }
         h2 {
            font-size: clamp(1.15rem, 2vw, 1.4rem);
            margin: 1.6em 0 0.4em;
         }
         p {
            margin: 0.5em 0;
         }
         .muted {
            color: var(--muted);
         }
         /* min() lets columns shrink below 220px on narrow viewports (avoids 320px overflow) */
         .grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(
               auto-fit,
               minmax(min(220px, 100%), 1fr)
            );
            margin: 1rem 0;
         }
         .card {
            background: var(--card);
            padding: 1rem 1.1rem;
            border-radius: var(--radius);
            border: 1px solid var(--border);
         }
         a {
            color: var(--accent);
         }
         :is(
            a,
            button,
            input,
            select,
            textarea,
            summary,
            [tabindex],
            [contenteditable]
         ):focus-visible {
            outline: 3px solid var(--ring);
            outline-offset: 2px;
            border-radius: 4px;
         }
         img,
         svg {
            max-width: 100%;
            height: auto;
            display: block;
         }
         figure {
            margin: 1rem 0;
         }
         figcaption {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.35rem;
         }
         @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
               animation-duration: 0.01ms !important;
               animation-iteration-count: 1 !important;
               transition-duration: 0.01ms !important;
               scroll-behavior: auto !important;
            }
         }
         @media print {
            :root {
               --bg: #fff;
               --fg: #000;
               --card: #fff;
               --muted: #444;
               --border: #999;
               --accent: #003a80;
            }
            .grid {
               grid-template-columns: 1fr !important;
            }
            main,
            header.site,
            footer.site {
               max-width: 100% !important;
               padding: 1em !important;
            }
            a::after {
               content: " (" attr(href) ")";
               font-size: 0.85em;
               color: #444;
            }
         }
      </style>
   </head>
   <body>
      <!-- Note: <header> and <footer> are siblings of <main> so they retain banner/contentinfo roles. -->
      <header class="site">
         <h1>{{Title}}</h1>
         <p class="muted">
            {{One-line intro — what this page is and who it's for}}
         </p>
      </header>
      <main>
         <section aria-labelledby="key-points">
            <h2 id="key-points">Key points</h2>
            <div class="grid">
               <div class="card">
                  <h3>{{Point 1}}</h3>
                  <p>{{…}}</p>
               </div>
               <div class="card">
                  <h3>{{Point 2}}</h3>
                  <p>{{…}}</p>
               </div>
               <div class="card">
                  <h3>{{Point 3}}</h3>
                  <p>{{…}}</p>
               </div>
            </div>
         </section>
      </main>
      <footer class="site muted"><p>Source: {{link or "—"}}</p></footer>
   </body>
</html>
```

## Worked examples — different inputs, different shapes

The worked examples below are **illustrative of shape-diversity**, not a
template to clone. A comparison input doesn't get the three-body card layout; a
song doesn't get a chart.

**Input:** "make me a quick visual aid on the three-body problem" Shape: concept
prompt → hero + 3 cards + small inline SVG (motion-guarded) + source link.

**Input:** "compare REST vs GraphQL vs gRPC" Shape: comparison → one column per
approach, shared attribute rows (protocol, streaming, caching, type safety);
traffic-light indicators always paired with **text** (Yes/No/Partial), never
color alone.

**Input:** "turn these lyrics into a concept card: <lyrics>" Shape: song →
single reading column, chorus visually highlighted (border/background shift),
`<audio controls>` only if an audio file was provided. No cards.

**Bad output, regardless of input:** transcribing every equation/row/line from
the source, dark-on-dark text, missing `alt`, CDN imports, motion without a
reduced-motion guard, "helpful" interactive controls the user never asked for.

## Process

1. **Read the input** and pick the layout from the Input shapes table. If
   genuinely ambiguous, ask one question; if you can't ask (non-interactive),
   pick the closest shape and record your choice in the top-of-file
   `<!-- Input: … -->` comment.
2. **Fill the template.** Prune unused blocks. Inline every asset as a `data:`
   URI — any local relative path breaks the "opens on double-click anywhere"
   promise and must be called out in the response if the user provided a file
   that's too large to inline.
3. **Run the self-check below.** Fix every failure before emitting. Don't mark a
   box unless you actually verified it — if you can't verify (e.g., real browser
   zoom), say so in the response instead of ticking it.
4. **Write the file**, then print the resolved `file://` path on its own line so
   the user can click it.

## A11y self-check (run before emitting)

Verifiable by the agent:

- [ ] Exactly one `<h1>`; headings never skip a level.
- [ ] `<html lang="...">` matches the primary content language.
- [ ] `<header>` and `<footer>` are siblings of `<main>` (so their landmark
      roles survive).
- [ ] Every `<img>` has `alt` (empty only if decorative and that's deliberate).
- [ ] Text contrast computed for **every custom color value** against the
      background it sits on, in both light and dark palettes. No "borderline"
      escape hatch — if you picked the color, you compute the ratio. **Compute
      means apply the WCAG sRGB formula**
      (`L = 0.2126·R' + 0.7152·G' + 0.0722·B'` on linearized channels, then
      `ratio = (L_light + 0.05)/(L_dark + 0.05)`). Estimating luminances by eye
      is not computing. "These are baseline-template colors, known-passing" is
      not computing. If you didn't run the formula, don't tick — write the
      ratios (or note "estimated, flag for human verification") in your response
      instead.
- [ ] `:focus-visible` selector covers a, button, input, select, textarea,
      summary, [tabindex], [contenteditable].
- [ ] Motion guard uses the WCAG `0.01ms` pattern, not `transition: none`.
- [ ] Nothing relies on color alone (every status/pill has text or an icon too).
- [ ] No hardcoded color literals outside `:root`.
- [ ] `@media print` block exists and collapses the grid to 1 column.
- [ ] The file contains a `<!-- Anchors: … -->` comment listing what was curated
      in.
- [ ] File opens without network: grep the HTML — zero `http://`/`https://`
      outside anchor `href`s that the user explicitly asked for.

Needs human verification (flag in response, don't tick):

- [ ] Renders sanely at 320px width and at 200% browser zoom.
- [ ] Printed preview looks right.

## Common mistakes

| Mistake                                                                               | Why it breaks the "quick aid" promise                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| External `<link>`/`<script>` to a CDN                                                 | Fails offline; breaks "open on double-click"                                                                                                                                                                                                                                                                                      |
| Adding interactive controls the user didn't ask for                                   | That's `playground`, not `visual-aid` — stay in your lane                                                                                                                                                                                                                                                                         |
| Dumping the full source text into the page                                            | Visual aid means _chosen_ points — dump is not aid                                                                                                                                                                                                                                                                                |
| Dark text on dark card (contrast fail)                                                | First thing a11y-debugging's Lighthouse pass will catch                                                                                                                                                                                                                                                                           |
| Decorative icons without `aria-hidden="true"`                                         | Screen reader reads "image, image, image"                                                                                                                                                                                                                                                                                         |
| Fixed px widths that overflow on mobile                                               | Breaks the "works on phone and laptop" baseline                                                                                                                                                                                                                                                                                   |
| `minmax(220px, 1fr)` without a `min()` wrapper                                        | Causes horizontal overflow at 320px — the template's old default had this bug                                                                                                                                                                                                                                                     |
| `<header>` or `<footer>` placed inside `<main>`                                       | Loses their `banner`/`contentinfo` landmark roles — screen readers miss the chrome                                                                                                                                                                                                                                                |
| Color-coded status (pill pros/cons, traffic-light dots) with no text/icon alternative | The color _is_ the meaning — breaks for color-blind users and most b/w prints                                                                                                                                                                                                                                                     |
| Reusing dark-mode `--accent`/`--ring` in light mode                                   | Pale blues/golds that look great on black fail 4.5:1 / 3:1 on white — re-pick both                                                                                                                                                                                                                                                |
| Hardcoded color literals (`#fff`, `color: black`) in CSS class bodies                 | Breaks dark mode, print mode, and theming — everything should flow from `:root`                                                                                                                                                                                                                                                   |
| `!important` sprinkled across rule bodies                                             | Fights with `prefers-color-scheme` and `@media print` overrides you need to work                                                                                                                                                                                                                                                  |
| Deprecated tags (`<center>`, `<font>`, `<b>`/`<i>` for emphasis vs style)             | Non-semantic; use CSS for presentation and `<strong>`/`<em>` for emphasis                                                                                                                                                                                                                                                         |
| Cloning the worked-example shape for every input                                      | A comparison input doesn't get three cards + SVG — pick from the Input shapes table                                                                                                                                                                                                                                               |
| Claiming the self-check passed without running it                                     | The self-check is not a ceremony — lying in it means the page ships with real defects                                                                                                                                                                                                                                             |
| Ticking "contrast computed" without applying the WCAG sRGB formula                    | Visual inspection ("looks high-contrast") and appeal to template authority ("these are baseline colors, they're known-passing") are both the "borderline escape hatch" the self-check bans. Either apply `L = 0.2126·R' + 0.7152·G' + 0.0722·B'` per color pair and write the ratio, or flag for human verification — don't tick. |

## When NOT to use this skill

- User wants a **production UI or component** → use `frontend-design`.
- User wants an **interactive configurator** (sliders/inputs that compose an
  output) → use `playground`.
- User wants a **slide deck, presentation, or PDF** → not this skill.
- User wants a **dashboard with live data** → not this skill.
- User wants a **plain doc or article** (reading copy, not a display page) →
  return Markdown, not HTML.
- User wants a **pure reference/comparison table with no narrative** (e.g.,
  "just give me a matrix of X vs Y") → return a Markdown table; only reach for
  /visual-aid if they want prose around it or the page format is explicit.
