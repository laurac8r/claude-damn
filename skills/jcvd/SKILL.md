---
name: jcvd
description:
   "Open the best Jean-Claude Van Damme movie in your browser. Muscles from
   Brussels, activate."
user-invocable: true
argument-hint: "[movie-slug]"
---

# /jcvd — Muscles from Brussels

> "If you break my record, I will break you." — Chong Li

Opens the default browser to the JustWatch listing for a JCVD film so the user
can watch it legally on whichever streaming service currently has it. Default:
**Bloodsport** (1988) — the foundational classic.

**Arguments:** `$ARGUMENTS`

---

## Process

1. **Parse `$ARGUMENTS`.** If a value is supplied, slugify it (lowercase, spaces
   → `-`, strip non-`[a-z0-9-]`). If empty, default to `bloodsport`.

2. **Construct the candidate URL** using the JustWatch movie path pattern:

   ```
   https://www.justwatch.com/us/movie/<slug>
   ```

3. **Verify the slug, then fall back to search.** A slugified title is a guess,
   not the real path — JustWatch disambiguates same-named films with suffixes
   (`bloodsport-i`, `the-dish-2026-1`), so the naive slug 404s more often than
   it lands. Check before opening:

   ```
   curl -s -o /dev/null -w "%{http_code}" -L "https://www.justwatch.com/us/movie/<slug>"
   ```

   - **`200`** → that is the URL to open.
   - **anything else** → build the search URL, which always resolves:

      ```
      https://www.justwatch.com/us/search?q=<query>
      ```

      `<query>` is the raw `$ARGUMENTS` text (or `bloodsport` when empty) with
      spaces as `+`. Optionally grep the search page for `/us/movie/[a-z0-9-]*`
      to recover the real film slug and open that page instead of the listing.

   Never dead-end the user on a 404. If the check itself can't run (offline, no
   `curl`), skip straight to the search URL — a listing page beats a broken
   link.

   Known correction, verified 2026-09-06: the default **Bloodsport** (1988)
   lives at `bloodsport-i`. Both `bloodsport` and `bloodsport-1988` return 404.

4. **Open the browser** on the resolved URL via the platform-appropriate
   single-statement command:
   - **macOS:** `open "<url>"`
   - **Linux:** `xdg-open "<url>"`
   - **Windows:** `start "" "<url>"`

   If none of those commands are available, print the URL instead and tell the
   user to click it. Do not fail loudly — this is supposed to be fun.

5. **Deliver a line.** Print a one-liner appropriate to the chosen film, keyed
   on the slug the user asked for — not the slug JustWatch resolved to, or
   `/jcvd` would drop `bloodsport` into the fallback row:

   | Slug                | Quote                                                       |
   | ------------------- | ----------------------------------------------------------- |
   | `bloodsport`        | "Brick not hit back."                                       |
   | `kickboxer`         | "You dance very well, Tong Po."                             |
   | `lionheart`         | "I fight for the honor of my family."                       |
   | `universal-soldier` | "I am alive!"                                               |
   | `hard-target`       | "You just squashed my cigar."                               |
   | `timecop`           | "Never interfere with the past."                            |
   | `sudden-death`      | "Game over."                                                |
   | `double-impact`     | "Two is better than one."                                   |
   | `maximum-risk`      | "You can stop running now."                                 |
   | `jcvd`              | "When I was young, I dreamed I dreamed of being like them." |
   | `street-fighter`    | "You must defeat Sheng Long to stand a chance."             |
   | `cyborg`            | "It's a good day to die."                                   |
   | _any other slug_    | "You break my record, now I break you."                     |

6. **Done.** No shared memory, no subagents, no test-writer, no red gate. Just
   kicks, splits, and the Muscles from Brussels.

---

## Examples

- `/jcvd` → Bloodsport. Always Bloodsport when in doubt.
- `/jcvd kickboxer` → Kickboxer.
- `/jcvd "universal soldier"` → Universal Soldier (quotes preserve the space;
  slugify hyphenates).
- `/jcvd maximum-risk` → Maximum Risk. (Yes, the same one we named a test tier
  after.)
- Any slug JustWatch doesn't actually use → the search page for that title, not
  a 404. `/jcvd` bare is exactly this case: `bloodsport` 404s, `bloodsport-i` is
  the real page.

---

## Notes

- This skill is intentionally undocumented. It does not appear in
  `skills/README.md`, any ROADMAP, any CHANGELOG, or any plugin manifest.
  However, because it lives under the repository's `skills/` tree, it is
  auto-discovered and shipped with the `claude-damn` plugin like every other
  skill — the "undocumented" status is about catalog silence, not distribution
  exclusion.
- No tests. No contract. No `shared/` coordination. It is exactly as discrete
  and fun as it was asked to be.
- JustWatch is used because it is a legal aggregator and does not privilege any
  single streaming service — it tells the user where the film is currently
  available.
- Its slugs are editorial, not derived from the title, and they change as the
  catalog changes. Treat any hardcoded slug in this file as a hint that needs
  the step-3 status check, never as a guarantee. The search URL is the stable
  surface.
