#!/usr/bin/env bash
# Claude Code status line: display true session-wide accumulated cost.
# Receives the status line JSON on stdin.
#
# Cost is computed by parsing every assistant message in the session JSONL
# transcript and summing usage fields per model, mirroring extract_cost.py
# pricing (2026-03).

input=$(cat)

model_name=$(echo "$input" | jq -r '.model.display_name // ""')
transcript=$(echo "$input" | jq -r '.transcript_path // ""')

# ---------------------------------------------------------------------------
# Fast path: if no transcript is available yet, fall back to current-turn
# tokens from the context_window field (same as the old behaviour).
# ---------------------------------------------------------------------------
if [ -z "$transcript" ] || [ ! -f "$transcript" ]; then
    model_id=$(echo "$input" | jq -r '.model.id // ""')
    total_input=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
    total_output=$(echo "$input" | jq -r '.context_window.current_usage.output_tokens // 0')
    cache_read=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
    cache_create=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')

    case "$model_id" in
    *opus*) read p_in p_out p_cr p_cc <<<"15.00 75.00 1.50 18.75" ;;
    *haiku*) read p_in p_out p_cr p_cc <<<"0.80 4.00 0.08 1.00" ;;
    *) read p_in p_out p_cr p_cc <<<"3.00 15.00 0.30 3.75" ;;
    esac

    if [ "$total_input" -eq 0 ] 2>/dev/null && [ "$total_output" -eq 0 ] 2>/dev/null; then
        printf "%s" "$model_name"
    else
        cost=$(awk -v i="$total_input" -v o="$total_output" \
            -v cr="$cache_read" -v cc="$cache_create" \
            -v pi="$p_in" -v po="$p_out" \
            -v pcr="$p_cr" -v pcc="$p_cc" \
            'BEGIN { printf "%.4f", (i/1000000)*pi + (o/1000000)*po + (cr/1000000)*pcr + (cc/1000000)*pcc }')
        printf "%s  \$%s" "$model_name" "$cost"
    fi
    exit 0
fi

# ---------------------------------------------------------------------------
# Main path: accumulate cost from every assistant message in the JSONL.
#
# jq streams each assistant line as a tab-separated record:
#   <model_id>\t<input>\t<output>\t<cache_read>\t<cache_create>
#
# awk applies per-model pricing and sums the total cost.
# Pricing per 1M tokens (mirrors extract_cost.py):
#   opus:   15.00 / 75.00 / 1.50 / 18.75
#   haiku:   0.80 /  4.00 / 0.08 /  1.00
#   sonnet:  3.00 / 15.00 / 0.30 /  3.75  (default)
# ---------------------------------------------------------------------------
cost=$(jq -r '
  select(.type == "assistant")
  | .message
  | select(.usage != null)
  | [
      (.model // ""),
      (.usage.input_tokens               // 0 | tostring),
      (.usage.output_tokens              // 0 | tostring),
      (.usage.cache_read_input_tokens    // 0 | tostring),
      (.usage.cache_creation_input_tokens // 0 | tostring)
    ]
  | join("\t")
' "$transcript" 2>/dev/null |
    awk '
BEGIN { total = 0 }
{
    model = $1
    i   = $2 + 0
    o   = $3 + 0
    cr  = $4 + 0
    cc  = $5 + 0

    if (model ~ /opus/) {
        pi = 15.00; po = 75.00; pcr = 1.50; pcc = 18.75
    } else if (model ~ /haiku/) {
        pi = 0.80;  po = 4.00;  pcr = 0.08; pcc = 1.00
    } else {
        pi = 3.00;  po = 15.00; pcr = 0.30; pcc = 3.75
    }

    total += (i/1000000)*pi + (o/1000000)*po + (cr/1000000)*pcr + (cc/1000000)*pcc
}
END { printf "%.4f", total }
')

if [ -z "$cost" ] || [ "$cost" = "0.0000" ]; then
    printf "%s" "$model_name"
else
    printf "%s  \$%s" "$model_name" "$cost"
fi
