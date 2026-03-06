#!/usr/bin/env bash
set -euo pipefail
HOST="${HOST:-http://localhost:8000}"
MODEL="${MODEL:-EMPTY}"
MAX_TOKENS="${MAX_TOKENS:-128}"
TEMP="${TEMP:-0.7}"
PROMPT="${1:-What is the capital of France? Answer briefly.}"
echo "==> POST ${HOST}/v1/chat/completions"
echo "    Prompt: ${PROMPT}"
echo "------------------------------------------------------------"
curl -sS "${HOST}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"${MODEL}\",
        \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
        \"max_tokens\": ${MAX_TOKENS},
        \"temperature\": ${TEMP}
    }" | python -m json.tool
echo ""
echo "✅ Done."
