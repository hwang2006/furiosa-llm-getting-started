#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${VIRTUAL_ENV:-}" ]] && [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "==> Activated .venv"
fi

python -m pip install --upgrade huggingface_hub

if [[ -n "${HF_TOKEN:-}" ]]; then
    hf auth login --token "$HF_TOKEN"
else
    echo "==> No HF_TOKEN set — launching interactive login..."
    hf auth login
fi

echo "✅ Hugging Face authentication complete."
