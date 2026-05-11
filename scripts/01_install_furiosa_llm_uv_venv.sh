#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing furiosa-compiler..."
sudo apt install -y furiosa-compiler

echo "==> Installing uv..."
python3 -m pip install --user --upgrade uv
export PATH="$HOME/.local/bin:$PATH"

echo "==> Creating virtual environment at .venv ..."
uv venv .venv
source .venv/bin/activate

echo "==> Ensuring pip in .venv..."
python -m ensurepip --upgrade || true

echo "==> Installing furiosa-llm..."
python -m pip install --upgrade pip setuptools wheel uv
python -m uv pip install --upgrade --torch-backend=auto furiosa-llm

echo "==> Smoke test..."
python -c "import furiosa_llm; print('furiosa_llm imported OK:', furiosa_llm.__version__)"

echo ""
echo "✅ Done. Activate with: source .venv/bin/activate"
