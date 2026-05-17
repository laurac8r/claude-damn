#!/bin/bash
# Validate settings.local.json parses; wire-test block_opus_subagent hook.
set -e
uv --directory ~/.claude run python -m json.tool ~/.claude/settings.local.json > /dev/null
echo "JSON_OK"
echo '---deny case (opus)---'
echo '{"tool_name":"Task","tool_input":{"model":"claude-opus-4-7","prompt":"hi"}}' | python3 ~/.claude/hooks/block_opus_subagent.py
echo '---allow case (sonnet)---'
echo '{"tool_name":"Task","tool_input":{"model":"sonnet"}}' | python3 ~/.claude/hooks/block_opus_subagent.py
echo '---override case (opus + sentinel)---'
echo '{"tool_name":"Task","tool_input":{"model":"opus","prompt":"[BATCH_OVERRIDE] run"}}' | python3 ~/.claude/hooks/block_opus_subagent.py
