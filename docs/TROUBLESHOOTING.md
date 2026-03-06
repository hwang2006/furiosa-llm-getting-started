# Troubleshooting

## 1. `uv: command not found`
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## 2. `uv pip` — "No virtual environment found"
```bash
uv venv .venv && source .venv/bin/activate
```

## 3. `python: command not found` (Ubuntu 22.04)
```bash
sudo apt install -y python-is-python3
```

## 4. `furiosa-compiler` not found via apt
Configure the FuriosaAI apt repository first:
https://developer.furiosa.ai/latest/en/get_started/prerequisites.html

## 5. "Not enough PEs to be grouped for tensor parallelism"
```bash
furiosa-smi status   # check available PEs
furiosa-smi ps       # check processes holding PEs
```
Build a custom artifact with lower TP:
```bash
furiosa-llm build --model furiosa-ai/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 4 --output-dir ./artifacts/llama-tp4
```
See [MODEL_FIT_MATRIX.md](MODEL_FIT_MATRIX.md).

## 6. Empty or truncated responses
Always include `"max_tokens"` in requests. The server default can be as low as 16.

## 7. curl streaming mixed with progress meter
Use `curl -sS -N` (silent + no buffering). See `scripts/test_chat_stream_pretty.sh`.

## 8. Hugging Face gated model error
Accept the license at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct,
then run `./scripts/02_hf_login.sh`.

## 9. `import furiosa_llm` fails
```bash
source .venv/bin/activate
python -c "import furiosa_llm; print(furiosa_llm.__version__)"
```
Reinstall if needed: `uv pip install --upgrade --torch-backend=auto furiosa-llm`

## 10. Slow model download
```bash
export HF_HOME=/path/to/fast/storage/.cache/huggingface
huggingface-cli download furiosa-ai/Llama-3.1-8B-Instruct
```
