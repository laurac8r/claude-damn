"""Parse a Lighthouse JSON report; surface accessibility score and any failed audits.

CLI usage::

    python3 parse_lighthouse.py <report.json>

Exit codes:
    0 — success
    2 — wrong argument count or runtimeError present in report
"""

from __future__ import annotations

import json
import sys

#: Audit score-display modes that are skipped when the audit score is None.
_SKIP_MODES: frozenset[str] = frozenset({"manual", "notApplicable", "informative"})


def _collect_failed_audits(
    a11y: dict,
    audits: dict,
) -> list[tuple[str, str, float]]:
    """Return a list of (id, title, score) for every failed accessibility audit.

    An audit is **skipped** (not counted as failed) only when BOTH:
    - ``audit.score is None``, AND
    - ``audit.scoreDisplayMode`` is in ``_SKIP_MODES``.

    An audit is **failed** when its score is not None and is less than 1.
    Audits with a numeric score in (0, 1) are always counted even if their
    ``scoreDisplayMode`` is ``informative`` — the mode alone is insufficient
    to suppress a failing audit.
    """
    failed: list[tuple[str, str, float]] = []
    for ref in a11y.get("auditRefs", []):
        audit_id: str = ref.get("id", "")
        audit: dict = audits.get(audit_id, {})
        audit_score: float | None = audit.get("score")
        score_mode: str | None = audit.get("scoreDisplayMode")
        # Skip: score is None AND mode is in the skip-set.
        if audit_score is None and score_mode in _SKIP_MODES:
            continue
        # Count as failed: score is present and below perfect.
        if audit_score is not None and audit_score < 1:
            title: str = audit.get("title", "")
            failed.append((audit_id, title, audit_score))
    return failed


def main(path: str) -> int:
    """Parse *path* (Lighthouse 4.x JSON) and print accessibility results to stdout.

    Returns exit code 0 on success, 2 on runtimeError.
    Raises ``json.JSONDecodeError`` for malformed JSON (no special handling).
    """
    with open(path, encoding="utf-8") as fh:
        report: dict = json.load(fh)

    # runtimeError check — must happen before any other output.
    runtime_error: dict = report.get("runtimeError") or {}
    if runtime_error.get("code"):
        print(f"runtimeError: {runtime_error.get('code')}", file=sys.stderr)
        print(f"message: {runtime_error.get('message')}", file=sys.stderr)
        return 2

    categories: dict = report.get("categories", {})
    a11y: dict = categories.get("accessibility", {})
    score: float | None = a11y.get("score")

    print(f"Accessibility score: {score}")
    if score is not None:
        score_int: int = round(score * 100)
        print(f"Accessibility score (0-100): {score_int}")

    audits: dict = report.get("audits", {})
    failed = _collect_failed_audits(a11y, audits)

    if failed:
        print(f"\n{len(failed)} failed audit(s):")
        for audit_id, title, audit_score in failed:
            print(f"  - [{audit_id}] {title} (score={audit_score})")
    else:
        print("\nNo failed audits.")

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: parse_lighthouse.py <report.json>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
