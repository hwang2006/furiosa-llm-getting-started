# furiosa-llm-getting-started

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![SDK](https://img.shields.io/badge/Furiosa%20SDK-2026.1.0-brightgreen)](https://developer.furiosa.ai/latest/en/)
[![Platform](https://img.shields.io/badge/NPU-FuriosaAI%20RNGD-orange)](https://developer.furiosa.ai/latest/en/overview/rngd.html)

A **community companion** to the official [Furiosa-LLM Quick Start guide](https://developer.furiosa.ai/latest/en/get_started/furiosa_llm.html).
This repository provides ready-to-run scripts, practical troubleshooting notes,
and extended examples that go beyond the official documentation.

> **Note:** This is an independent companion repository, not an official FuriosaAI product.
> Official documentation: https://developer.furiosa.ai/latest/en/

---

## What's Inside

| Path | Description |
|------|-------------|
| `scripts/` | Shell scripts for environment setup and server testing |
| `examples/` | Runnable Python examples (batch, streaming, chat, tool calling) |
| `docs/` | Extended guides: companion, troubleshooting, model fit matrix, OpenAI server |

---

## Quick Commands

### 1. Install prerequisites (Ubuntu 22.04)
```bash
./scripts/00_system_prereq_ubuntu22.sh
```

### 2. Install Furiosa-LLM
```bash
./scripts/01_install_furiosa_llm_uv_venv.sh
source .venv/bin/activate
```

### 3. (Optional) Hugging Face login
```bash
./scripts/02_hf_login.sh
```

### 4. Run examples
```bash
python examples/01_offline_batch_inference.py
python examples/02_streaming_inference.py
python examples/03_chat_llm_chat.py
python examples/04_stream_chat_loop.py
python examples/05_tool_router_weather_openmeteo.py
```

### 5. Launch OpenAI-compatible server

The server must keep running while the test scripts are executed. Use two terminals.

**Terminal 1 — start the server**

```bash
cd ~/furiosa-llm-getting-started
source .venv/bin/activate

furiosa-llm serve furiosa-ai/Llama-3.1-8B-Instruct
```

Leave this terminal running.

**Terminal 2 — run the tests**

```bash
cd ~/furiosa-llm-getting-started
source .venv/bin/activate

./scripts/test_chat_completion.sh
./scripts/test_chat_stream_pretty.sh "Give me 5 short tips for prompting."
```

If you see `Failed to connect to localhost port 8000`, make sure the server in Terminal 1 is running and ready.


---

## Documentation Index

| Document | Description |
|----------|-------------|
| [docs/QUICKSTART_COMPANION.md](docs/QUICKSTART_COMPANION.md) | Mirrors official Quick Start sections with practical notes |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [docs/MODEL_FIT_MATRIX.md](docs/MODEL_FIT_MATRIX.md) | NPU PE count vs. tensor parallelism table |
| [docs/SERVER_OPENAI_COMPAT.md](docs/SERVER_OPENAI_COMPAT.md) | Running and testing the OpenAI-compatible server |

---

## Repository Structure

```
furiosa-llm-getting-started/
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   ├── 00_system_prereq_ubuntu22.sh
│   ├── 01_install_furiosa_llm_uv_venv.sh
│   ├── 02_hf_login.sh
│   ├── test_chat_completion.sh
│   └── test_chat_stream_pretty.sh
├── examples/
│   ├── 01_offline_batch_inference.py
│   ├── 02_streaming_inference.py
│   ├── 03_chat_llm_chat.py
│   ├── 04_stream_chat_loop.py
│   └── 05_tool_router_weather_openmeteo.py
└── docs/
    ├── QUICKSTART_COMPANION.md
    ├── TROUBLESHOOTING.md
    ├── MODEL_FIT_MATRIX.md
    └── SERVER_OPENAI_COMPAT.md
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

- [FuriosaAI](https://furiosa.ai) for the RNGD NPU and Furiosa-LLM framework
- [Open-Meteo](https://open-meteo.com) for the free weather API used in the tool calling example
- [Hugging Face](https://huggingface.co) for model hosting
