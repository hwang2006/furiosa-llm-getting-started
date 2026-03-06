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
    | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line or line == '[DONE]':
        continue
    try:
        d = json.loads(line)
        content = d['choices'][0]['delta'].get('content', '')
        if content:
            print(content, end='', flush=True)
    except Exception:
        pass
print()
"
echo ""
echo "✅ Stream complete."
