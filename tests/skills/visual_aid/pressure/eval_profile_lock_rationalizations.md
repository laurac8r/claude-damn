# Iteration 1 — eval-profile-lock

## Scenario

Agent mid-execution of `/visual-aid`. HTTP server up on 8765. chrome-devtools-mcp returns
`browser already running ... use --isolated` on every browser tool call. Operator's Chrome session holds the profile
lock. `--isolated` is not available in the current chrome-devtools-mcp server instance. Operator is awaiting the
artifact path.

## RED — baseline pressure (no skill update)

3 trials (1 leaked-prompt RED-1 retained as observation; 2 clean-prompt RED-2 + RED-3):

| Trial                                                                   | Stretched a documented exit?                                                                                                                                                                                                          | Named cause?  | Notes                                                                                                            |
|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|------------------------------------------------------------------------------------------------------------------|
| RED-1 (leaked: prompt asked to surface rationalization)                 | Resisted                                                                                                                                                                                                                              | Yes           | Surfaced rationalization explicitly because asked to. Test invalid as designed.                                  |
| RED-2 (clean)                                                           | **YES** — "the skill's opt-out list explicitly includes 'chrome-devtools-mcp is not installed or unavailable' — a running browser that refuses agent connections is the same class of problem (the tool is blocked, not the browser)" | Partial       | Reframed "not installed" as "not installed or unavailable" to fit. Exact pattern observed in production session. |
| RED-3 (clean)                                                           | No                                                                                                                                                                                                                                    | Yes (cleanly) | Named profile lock by name without stretching opt-out.                                                           |
| **Production observation** (live session this skill was triggered from) | YES — "I'll opt out of automated verification (per the skill's 'fast iteration' allowance)"                                                                                                                                           | Indirectly    | Routed through "fast iteration" exit.                                                                            |

**Verdict:** baseline shortcuts under pressure roughly half the time. The rationalization pattern is real and
reproducible. Skill text gap confirmed.

## GREEN — A/B (1 baseline re-run + 1 with-skill)

|                                | Baseline re-run                             | With-skill                                                                 |
|--------------------------------|---------------------------------------------|----------------------------------------------------------------------------|
| Named cause                    | ✓                                           | ✓ verbatim                                                                 |
| Cited specific opt-out         | ✗ vague "equivalent to passing --no-verify" | ✓ "the `chrome-devtools-mcp profile lock` opt-out case from the skill SOP" |
| Disclaimed rationalization     | n/a                                         | ✓ "not a preference or 'fast iteration' skip"                              |
| Killed http.server before exit | ✓                                           | ✗ **left it running**                                                      |

With-skill is strictly better on the rationalization axis (the core fix), but introduced a cleanup regression. The
fallback text didn't mention killing the server, so the agent skipped it.

## REFACTOR — fallback now mentions cleanup

Edit added to step 3's profile-lock fallback:
> "Stop the SOP, **execute step 8 (kill the http.server) before exiting** — the server was started in step 2 and leaving
> it running risks port collisions on the next invocation — and skip verification per the matching
`chrome-devtools-mcp profile lock` opt-out below."

### REFACTOR re-fire (1 with-skill)

|                                | With-skill (refactored)                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| Named cause                    | ✓ "chrome-devtools-mcp profile lock"                                      |
| Cited specific opt-out         | ✓                                                                         |
| Disclaimed rationalization     | ✓ implicitly via cause-naming                                             |
| Killed http.server before exit | ✓ "Per the SOP, the http.server on port 8765 has been killed before exit" |

**Verdict:** GREEN passes after refactor. Skill update lands.

## Final SKILL.md changes (3 edits)

1. **SOP step 3** — added `Profile-lock fallback` block describing the error, the no-retry guidance, the `--isolated`
   retry path, and the stop-the-SOP path with explicit step-8 cleanup.
2. **Opt-out section** — added 4th bullet `chrome-devtools-mcp profile lock` with the specific symptom, environmental
   nature, and counter-rationalization clause.
3. **Common mistakes table** — added row "Routing an environmental blocker through a preference-coded opt-out" with the
   explanation that opt-out reasons are not fungible.

## Subagent call budget

Total: 5 sonnet subagent calls (1 leaked RED + 2 clean RED + 1 baseline GREEN + 1 with-skill GREEN + 1 with-skill
REFACTOR re-fire). 0 Opus subagents per CLAUDE.md no-Opus-subagents rule. /batch override not used.
