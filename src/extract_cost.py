#!/usr/bin/env python3
"""Extract cost data from Claude Code session JSONL files.

Parses assistant messages for token usage, calculates cost using current
Anthropic pricing, and outputs a compact JSON summary to stdout.

Usage:
    python3 extract_cost.py <session_jsonl_path> [--append-log]
    python3 extract_cost.py --all-since <ISO_timestamp> [--append-log]
    python3 extract_cost.py --latest <project_dir> [--append-log]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Pricing per 1M tokens (as of 2026-03 Anthropic API pricing)
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {
        "input": 15.00,
        "output": 75.00,
        "cache_read": 1.50,
        "cache_create": 18.75,
    },
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_create": 3.75,
    },
    "claude-opus-4-6-fast": {
        "input": 30.00,
        "output": 150.00,
        "cache_read": 30.00,
        "cache_create": 30.00,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.00,
        "cache_read": 0.08,
        "cache_create": 1.00,
    },
}

# Fallback for unknown models — use Sonnet pricing as default
DEFAULT_PRICING = PRICING["claude-sonnet-4-6"]

COST_LOG_DIR = Path.home() / ".claude" / "cost-log"


def model_key(model_name: str) -> str:
    """Normalize model name to pricing key."""
    if not model_name:
        return ""
    name = model_name.lower()
    for key in sorted(PRICING, key=len, reverse=True):
        if key in name or key.replace("-", "") in name.replace("-", ""):
            return key
    # Fuzzy match
    if "opus" in name and "fast" in name:
        return "claude-opus-4-6-fast"
    if "opus" in name:
        return "claude-opus-4-6"
    if "sonnet" in name:
        return "claude-sonnet-4-6"
    if "haiku" in name:
        return "claude-haiku-4-5"
    return model_name


def calc_cost(model: str, usage: dict) -> float:
    """Calculate USD cost from a usage dict."""
    prices = PRICING.get(model_key(model), DEFAULT_PRICING)
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)

    cost = (
        (input_tokens / 1_000_000) * prices["input"]
        + (output_tokens / 1_000_000) * prices["output"]
        + (cache_read / 1_000_000) * prices["cache_read"]
        + (cache_create / 1_000_000) * prices["cache_create"]
    )
    return cost


def parse_session(jsonl_path: Path) -> dict:
    """Parse a session JSONL and return aggregated cost data."""
    totals: dict[str, dict[str, int]] = {}  # model -> {field: count}
    total_cost = 0.0
    turn_count = 0
    first_ts = None
    last_ts = None
    session_id = None
    project_dir = None
    last_prompt = None

    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = entry.get("timestamp")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            if not session_id:
                session_id = entry.get("sessionId")
            if not project_dir:
                cwd = entry.get("cwd", "")
                if cwd:
                    project_dir = cwd

            # Capture last user prompt for context
            if entry.get("type") == "last-prompt":
                last_prompt = entry.get("content", entry.get("message", ""))
                if isinstance(last_prompt, dict):
                    content = last_prompt.get("content", "")
                    if isinstance(content, list):
                        last_prompt = " ".join(
                            c.get("text", "") for c in content if isinstance(c, dict)
                        )
                    else:
                        last_prompt = str(content)

            if entry.get("type") != "assistant":
                continue

            msg = entry.get("message", {})
            usage = msg.get("usage")
            if not usage:
                continue

            model = msg.get("model", "unknown")
            mk = model_key(model)
            turn_count += 1

            if mk not in totals:
                totals[mk] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                    "turns": 0,
                }

            totals[mk]["input_tokens"] += usage.get("input_tokens", 0)
            totals[mk]["output_tokens"] += usage.get("output_tokens", 0)
            totals[mk]["cache_read_input_tokens"] += usage.get(
                "cache_read_input_tokens", 0
            )
            totals[mk]["cache_creation_input_tokens"] += usage.get(
                "cache_creation_input_tokens", 0
            )
            totals[mk]["turns"] += 1

            total_cost += calc_cost(model, usage)

    return {
        "session_id": session_id,
        "project": project_dir,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "turns": turn_count,
        "total_cost_usd": round(total_cost, 4),
        "models": {
            m: {**v, "cost_usd": round(sum(
                calc_cost(m, {k: v[k] for k in v if k != "turns" and k != "cost_usd"})
                for _ in [1]  # just calc once from totals
            ), 4)}
            for m, v in totals.items()
        },
        "last_prompt": (last_prompt or "")[:120],
    }


def _purge_session_entries(session_id: str) -> None:
    """Remove all existing log entries for a session_id across all log files."""
    if not session_id or not COST_LOG_DIR.is_dir():
        return
    for log_file in COST_LOG_DIR.glob("*.jsonl"):
        lines_to_keep: list[str] = []
        changed = False
        with open(log_file) as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entry = json.loads(stripped)
                except json.JSONDecodeError:
                    lines_to_keep.append(stripped)
                    continue
                if entry.get("session_id") == session_id:
                    changed = True
                else:
                    lines_to_keep.append(stripped)
        if changed:
            if lines_to_keep:
                with open(log_file, "w") as f:
                    f.write("\n".join(lines_to_keep) + "\n")
            else:
                log_file.unlink()


def write_log_entry(data: dict) -> Path:
    """Write a cost log entry to the cost-log directory.

    Deduplicates by removing any prior entries for the same session_id
    before writing the latest snapshot.
    """
    COST_LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Purge stale entries for this session across all log files
    session_id = data.get("session_id")
    if session_id:
        _purge_session_entries(session_id)

    ts = data.get("last_ts") or datetime.now(timezone.utc).isoformat()
    # Parse timestamp for filename
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        dt = datetime.now(timezone.utc)

    # Build filename: YYYY-MM-DD_HHmm_{session_short}.jsonl
    session_short = (session_id or "unknown")[:8]
    fname = f"{dt.strftime('%Y-%m-%d_%H%M')}_{session_short}.jsonl"
    fpath = COST_LOG_DIR / fname

    with open(fpath, "w") as f:
        f.write(json.dumps(data) + "\n")

    return fpath


def find_latest_session(project_dir: str) -> Path | None:
    """Find the most recently modified session JSONL for a project."""
    proj_path = Path(project_dir)
    if not proj_path.is_dir():
        return None
    jsonls = sorted(proj_path.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return jsonls[-1] if jsonls else None


def find_sessions_since(timestamp: str) -> list[Path]:
    """Find all session JSONLs modified since a given ISO timestamp."""
    try:
        since = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        print(f"Invalid timestamp: {timestamp}", file=sys.stderr)
        return []

    projects_dir = Path.home() / ".claude" / "projects"
    results = []
    for jsonl in projects_dir.rglob("*.jsonl"):
        # Skip subagent files
        if "subagents" in str(jsonl):
            continue
        try:
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime, tz=timezone.utc)
            if mtime >= since:
                results.append(jsonl)
        except OSError:
            continue
    return sorted(results, key=lambda p: p.stat().st_mtime)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Claude Code session costs")
    parser.add_argument("session_path", nargs="?", help="Path to session JSONL file")
    parser.add_argument("--latest", help="Project dir to find latest session in")
    parser.add_argument("--all-since", help="ISO timestamp; process all sessions since")
    parser.add_argument(
        "--append-log",
        action="store_true",
        help="Write results to cost-log directory",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Only output on --append-log write"
    )

    args = parser.parse_args()

    paths: list[Path] = []

    if args.session_path:
        paths = [Path(args.session_path)]
    elif args.latest:
        p = find_latest_session(args.latest)
        if p:
            paths = [p]
        else:
            print(f"No sessions found in {args.latest}", file=sys.stderr)
            sys.exit(1)
    elif args.all_since:
        paths = find_sessions_since(args.all_since)
        if not paths:
            print(f"No sessions found since {args.all_since}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default: find all sessions from today
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        paths = find_sessions_since(today.isoformat())
        if not paths:
            print("No sessions found today", file=sys.stderr)
            sys.exit(1)

    all_results = []
    for p in paths:
        data = parse_session(p)
        if data["turns"] == 0:
            continue
        all_results.append(data)

        if args.append_log:
            log_path = write_log_entry(data)
            if not args.quiet:
                print(f"Logged: {log_path}", file=sys.stderr)

    if not args.quiet:
        print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()