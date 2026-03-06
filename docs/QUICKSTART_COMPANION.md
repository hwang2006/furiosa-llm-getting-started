# Furiosa-LLM Quick Start Companion

Mirrors the official Quick Start sections with practical notes and tested commands.

Official guide: https://developer.furiosa.ai/latest/en/get_started/furiosa_llm.html

---

## 1. Installing Prerequisites

```bash
./scripts/00_system_prereq_ubuntu22.sh
```

> **Note:** `python-is-python3` is required on Ubuntu 22.04 to create the `python` symlink.

---

## 2. Installing Furiosa-LLM

```bash
./scripts/01_install_furiosa_llm_uv_venv.sh
source .venv/bin/activate
```

> **Note:** If `uv: command not found`, run: `export PATH="$HOME/.local/bin:$PATH"`

---

## 3. Authorizing Hugging Face Hub (Optional)

```bash
export HF_TOKEN=hf_your_token_here
./scripts/02_hf_login.sh
```

Models that do NOT require login: `Qwen2.5-0.5B-Instruct`, `Qwen3-32B-FP8`.
Models that DO require login: `Llama-3.1-8B-Instruct` and other Meta models.

---

## 4. Offline Batch Inference

```bash
python examples/01_offline_batch_inference.py
```

Key points:
- Always set `max_tokens` explicitly (default can be as low as 16).
- Use `add_generation_prompt=True` in `apply_chat_template`.

---

## 5. Streaming Inference

```bash
python examples/02_streaming_inference.py
```

Key points:
- Use `stream_generate()` — it is an `async` generator.
- Wrap in `async def main()` and call via `asyncio.run(main())`.

| Scenario | Method |
|----------|--------|
| Interactive / chatbot | `stream_generate` |
| Bulk offline processing | `generate` (batched) |
| Production server | `furiosa-llm serve` + SSE |

---

## 6. Chat Inference

```bash
python examples/03_chat_llm_chat.py
python examples/04_stream_chat_loop.py
```

`llm.chat()` applies the chat template internally.
For multi-turn, append each turn to `messages` manually before calling `chat()` again.

---

## 7. Tool Calling (Offline Python Router Pattern)

```bash
python examples/05_tool_router_weather_openmeteo.py
```

```
User message → Python router detects intent
    → Execute external tool (API call)
    → Inject as {"role": "tool", "content": {"output": ...}}
    → LLM generates final natural-language answer
```

For the official `llm.chat(tools=...)` approach:
https://developer.furiosa.ai/latest/en/furiosa_llm/toolcalling.html

---

## 8. Launching the OpenAI-Compatible Server

```bash
furiosa-llm serve furiosa-ai/Llama-3.1-8B-Instruct
./scripts/test_chat_completion.sh
./scripts/test_chat_stream_pretty.sh "Give me 5 LLM prompting tips."
```

See [SERVER_OPENAI_COMPAT.md](SERVER_OPENAI_COMPAT.md) for full details.
See [MODEL_FIT_MATRIX.md](MODEL_FIT_MATRIX.md) for TP vs. PE requirements.
