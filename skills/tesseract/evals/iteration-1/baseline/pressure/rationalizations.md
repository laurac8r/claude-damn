# Baseline × Pressure — Tesseract SKILL.md cross-reference update (Iteration 1)

Conditions: agent dispatched WITHOUT the planned /tesseract cross-reference
update, under explicit pressure framing with shortcut-permissions suggested in
prompt (vague-bullet, drop-/atlas-context, drop-import-vs-inline framing,
drop-copy-paste-drift framing).

## Verdict

PARTIAL SHORTCUT. The baseline took every offered minimalism shortcut (one-line
vague bullet, no `/atlas` context, no import-vs-inline guidance, no drift
framing) but did NOT violate any contract. The test gate ("skills/\_shared"
substring present) still passes on the minimal version.

The one rationalization surface that matters: **a future contributor adding
Python to `/tesseract` might inline a slug helper rather than import from
`skills/_shared/`**. The baseline's vague bullet ("see also skills/\_shared/")
doesn't actively close that.

## Captured rationalizations

| #   | Surface          | Rationalization                                                                                                                                                                                                  | Counter-prose needed                                                                                                                                     |
| --- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | inline-vs-import | Baseline dropped "import from skills/\_shared/ rather than inlining" framing as "vague and judge-y" — leaving a future contributor free to copy-paste a slugify implementation rather than reuse the shared one. | MUST say explicitly: "When a future change adds Python here, import from `skills/_shared/` rather than inlining." This is the only real drift attractor. |

(Surfaces 2-4 — `/atlas` context, copy-paste-drift framing, API detail — are
stylistic; they don't gate any contract. Skip.)

## Conclusion

The /tesseract update needs minimal counter-rationalization prose: ONE sentence
about importing-not-inlining. The plan's draft already includes it. Use the
plan's draft.

## Why GREEN re-fire is skipped

A meaningful with-skill-pressure prompt would simulate a future contributor
adding Python to `/tesseract` and asking whether they inline or import. That's
an implementation eval, not a prose eval — it doesn't measure whether the
SKILL.md change itself holds, only whether downstream agents read it. The
rationalization surface for the SKILL.md edit itself is too narrow to A/B.
Documented and shipped on baseline evidence alone.
