#!/usr/bin/env bash
set -euo pipefail
HOST="${HOST:-http://localhost:8000}"
MODEL="${MODEL:-EMPTY}"
MAX_TOKENS="${MAX_TOKENS:-256}"
TEMP="${TEMP:-0.7}"
PROMPT="${1:-Give me 5 short tips for effective prompting with LLMs.}"
echo "==> Streaming from ${HOST}/v1/chat/completions"
echo "    Prompt: ${PROMPT}"
echo "------------------------------------------------------------"
curl -sS -N "${HOST}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"${MODEL}\",
        \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
        \"max_tokens\": ${MAX_TOKENS},
        \"temperature\": ${TEMP},
        \"stream\": true
    }" \
    | sed -n 's/^data: //p' \
    | while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        [[ "$line" == "[DONE]" ]] && break
        echo "$line" | python3 - <<'PY'
import sys, json
try:
    d = json.load(sys.stdin)
    print(d["choices"][0]["delta"].get("content", ""), end="", flush=True)
except Exception:
    pass
PY
    done
echo ""
echo "✅ Stream complete."
