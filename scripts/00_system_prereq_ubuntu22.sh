#!/usr/bin/env bash
set -euo pipefail
echo "==> Updating apt package index..."
sudo apt update
echo "==> Installing Python and essential build tools..."
sudo apt install -y python3 python3-venv python3-pip python-is-python3 \
    build-essential curl wget git
echo "==> Verifying Python installation..."
python --version && python3 --version && pip --version
echo ""
echo "✅ System prerequisites installed. Next: ./scripts/01_install_furiosa_llm_uv_venv.sh"
