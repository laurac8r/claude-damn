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
     plugin's `lighthouse_audit` tool, if installed). A score below 90 should
     be treated as a fail — see the Verification SOP below.
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

The full HTML skeleton lives in the sibling file `skills/visual-aid/baseline.html`.
When scaffolding a new visual aid, **copy** `baseline.html` as your starting point,
then fill in the content slots and prune any unused blocks. Never drop the a11y
guards (motion, focus, contrast, print).

### Slot conventions

The template uses placeholder slots that you must replace before saving. **The
list below names the structural slots; the rule is broader: every `{{...}}`
pattern in `baseline.html` must be replaced with real content (or the
surrounding block deleted) before shipping. Grep the output for `{{` as a final
check — any survivor is a bug.**

Slots in `baseline.html`:

- `{{Title}}` — the page title, used in both `<title>{{Title}}</title>` and the
  visible `<h1>`.
- `{{one-line prompt summary}}` — a brief description of the user's request,
  placed in the traceability comment
  `<!-- Generated from: "{{one-line prompt summary}}" -->` at the very top.
- `{{X}}`, `{{Y}}`, `{{Z}}` — the 3–6 anchor points you curated from the source,
  listed in `<!-- Anchors: {{X}}, {{Y}}, {{Z}} -->` so the user can see what was
  included and what was left out.
- `{{One-line intro — what this page is and who it's for}}` — the lede
  paragraph under the `<h1>`. Replace with a real sentence; do not leave the
  hint text.
- `{{Point 1}}`, `{{Point 2}}`, `{{Point 3}}` — card titles in the default
  three-card layout. Add or remove cards to match your chosen shape from the
  Input shapes table; don't pad to three if the source has two.
- `{{…}}` — card body text under each card title. One per card; replace with
  the curated content for that anchor.
- `{{link or "—"}}` — the source link in the footer. Use the URL the user
  provided, or replace with `—` (em dash) if there's no canonical source.

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

Layout (automated) and print (manual) checks:

- [ ] Renders sanely at 320px width and at 200% browser zoom — **automated**
      via mobile-viewport screenshot in the chrome-devtools verification step
      below.
- [ ] Printed preview looks right — **manual**: run the OS print-to-PDF flow
      (see `reference_html_to_pdf_sop`) after the chrome-devtools verification
      passes. The chrome-devtools SOP does not cover print rendering.

## Verification (chrome-devtools)

Automated browser verification runs **by default** on every `/visual-aid`
invocation. It drives Chrome via the `chrome-devtools-mcp` plugin. Pass
`--no-verify` to skip (e.g., when chrome-devtools-mcp is not installed, or
for rapid iteration where you only want the HTML output).

### SOP

> **Note on artifact vs verification URL.** The HTTP server below exists
> *only* for the verification pass. The final artifact the agent surfaces to
> the user is always the durable `file://` path to the on-disk HTML — the
> localhost URL disappears the moment the server stops in step 8.

1. **Resolve slug + dirs.** Lowercase the prompt, replace spaces/punctuation
   with dashes. Create `/tmp/visual-aid/<slug>/` (`mkdir -p`).

2. **Start a local HTTP server.** Pick an unused high port (e.g., 8765), then
   run `python3 -m http.server <port>` rooted at the *directory containing the
   output HTML* in the background. Capture the PID/job id so you can stop it
   in step 8. *Why HTTP:* Lighthouse rejects `file://` URLs with `INVALID_URL`
   and requires an HTTP origin — a bare `file://` path causes the Lighthouse
   audit to fail before it can score the page.

3. **Open in browser.** Use `navigate_page` to load
   `http://localhost:<port>/<filename>` (not the `file://` URL).

   **Profile-lock fallback.** If `new_page` / `navigate_page` / `list_pages`
   return the error
   `The browser is already running for <userDataDir>. Use --isolated to run multiple browser instances`,
   the operator's own Chrome session is holding the profile lock and you cannot
   drive a second instance against the same `userDataDir`. Do **not** retry the
   same call — it will keep returning the same error. Either:
   - Retry chrome-devtools-mcp invocations with the `--isolated` flag (creates
     a separate ephemeral profile dir, no conflict with the operator's
     session), then resume the SOP from step 3, **or**
   - Stop the SOP, **execute step 8 (kill the http.server) before exiting** —
     the server was started in step 2 and leaving it running risks port
     collisions on the next invocation — and skip verification per the matching
     `chrome-devtools-mcp profile lock` opt-out below. Name the actual cause in
     your response — do **not** repackage a profile-lock under "fast iteration"
     or "not installed."

4. **Desktop screenshot.** Use `take_screenshot` — save to
   `/tmp/visual-aid/<slug>/desktop.png`.

5. **Mobile viewport screenshot.** Use `resize_page` (width 375, height 812)
   to switch to a mobile viewport, then `take_screenshot` — save to
   `/tmp/visual-aid/<slug>/mobile.png`. This covers the "renders sanely at
   320 px / small viewport" self-check.

6. **Console check.** Use `list_console_messages`. If any error-level console
   errors are present, abort and attach the console errors to the response.
   Do not emit the file path until all console errors are resolved.

7. **Lighthouse a11y audit.** Use `lighthouse_audit` (threshold 90) against
   the same `http://localhost:<port>/<filename>` URL. If the accessibility
   score is below 90, abort and attach the failing audits. A score below that
   threshold means the page ships with real a11y defects — fix them before
   surfacing the output.

8. **Stop the server.** Kill the background `http.server` job (e.g.,
   `pkill -f "http.server <port>"`). The server is one-shot — leaving it
   running risks port collisions on subsequent invocations.

9. **Surface artifacts.** On success, print the artifact paths inline:
   - `file://<absolute-path-to-output.html>` ← the durable on-disk HTML
   - `file:///tmp/visual-aid/<slug>/desktop.png`
   - `file:///tmp/visual-aid/<slug>/mobile.png`

   The screenshots are ephemeral — `/tmp/visual-aid/` is not persisted across
   reboots. The HTML output is durable at its original write path.

### Opt-out

Pass `--no-verify` when:

- `chrome-devtools-mcp` is not installed in the current environment.
- Fast iteration: you want the raw HTML first and will verify manually.
- CI / headless environments without a browser.
- **chrome-devtools-mcp profile lock** — the operator's own Chrome session is
  already running on the same `userDataDir` and the plugin returns
  `browser already running ... use --isolated`. The plugin IS installed and
  the environment IS interactive; the blocker is environmental (a held profile
  lock), not a preference. First try retrying chrome-devtools-mcp with
  `--isolated` if available; if not, skip verification and **name the
  profile-lock cause in your response** — do not silently route through "fast
  iteration" or "not installed."

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
| Routing an environmental blocker through a preference-coded opt-out (e.g. citing "fast iteration" when chrome-devtools-mcp returned a profile-lock error, or stretching "not installed" to cover "installed but blocked") | The opt-out reasons aren't fungible — each names a specific cause. Repackaging a profile-lock as "fast iteration" hides the real failure mode from the operator and from future-you reading the response. The skill defines a `chrome-devtools-mcp profile lock` opt-out for exactly this case — use it and name the cause verbatim. If a new environmental blocker doesn't match any listed opt-out, surface that as a gap rather than stretching the closest preference-coded exit to fit. |

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
