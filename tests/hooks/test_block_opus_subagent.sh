#!/bin/bash
# Validate settings.local.json parses; wire-test block_opus_subagent hook.
# Runs against the in-repo copies (resolved from this script's location) so the
# test is hermetic — no dependency on a ~/.claude install. The hook uses PEP 758
# except-tuple syntax, so it must run under the repo's pinned Python 3.14: invoke
# via `uv --directory "$REPO_ROOT" run python`, not a bare system python3.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/block_opus_subagent.py"
SETTINGS="$REPO_ROOT/settings.local.json"
PY=(uv --directory "$REPO_ROOT" run python)

"${PY[@]}" -m json.tool "$SETTINGS" >/dev/null
echo "JSON_OK"
echo '---deny case (opus)---'
echo '{"tool_name":"Task","tool_input":{"model":"claude-opus-4-7","prompt":"hi"}}' | "${PY[@]}" "$HOOK"
echo '---allow case (sonnet)---'
echo '{"tool_name":"Task","tool_input":{"model":"sonnet"}}' | "${PY[@]}" "$HOOK"
echo '---override case (opus + sentinel)---'
echo '{"tool_name":"Task","tool_input":{"model":"opus","prompt":"[BATCH_OVERRIDE] run"}}' | "${PY[@]}" "$HOOK"
