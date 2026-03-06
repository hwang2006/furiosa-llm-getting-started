# OpenAI-Compatible Server Guide

Official reference: https://developer.furiosa.ai/latest/en/furiosa_llm/furiosa-llm-serve.html

## Start the Server
```bash
furiosa-llm serve furiosa-ai/Llama-3.1-8B-Instruct
# Custom host/port:
furiosa-llm serve furiosa-ai/Llama-3.1-8B-Instruct --host 127.0.0.1 --port 9000
```
Ready when you see: `INFO: Application startup complete.`

## Non-Streaming Request
```bash
./scripts/test_chat_completion.sh "What is an NPU?"
```
Or manually:
```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"EMPTY","messages":[{"role":"user","content":"Hello"}],"max_tokens":128}'
```

## Streaming Request
```bash
./scripts/test_chat_stream_pretty.sh "Explain tensor parallelism."
```

## OpenAI Python Client
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
resp = client.chat.completions.create(
    model="EMPTY",
    messages=[{"role": "user", "content": "What is an NPU?"}],
    max_tokens=256,
)
print(resp.choices[0].message.content)
```

## Tool Calling via Server
```bash
furiosa-llm serve furiosa-ai/Llama-3.1-8B-Instruct --tool-call-parser llama
```

| Model family | Parser flag |
|-------------|-------------|
| Llama 3.1 / 3.2 | `--tool-call-parser llama` |
| Qwen3, EXAONE-4.0 | `--tool-call-parser hermes` |

## Health Check
```bash
curl http://localhost:8000/health   # returns 200 OK when ready
```

## Server Options
| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8000` | Listen port |
| `--tensor-parallel-size` | model default | NPU PEs for TP |
| `--tool-call-parser` | model default | Tool call output parser |

```bash
furiosa-llm serve --help   # full option list
```
