"""
03_chat_llm_chat.py
Chat Inference using LLM.chat()
Model: furiosa-ai/Llama-3.1-8B-Instruct (HF license required)
Run ./scripts/02_hf_login.sh first.
"""
from furiosa_llm import LLM, SamplingParams

MODEL_ID = "furiosa-ai/Llama-3.1-8B-Instruct"
sampling_params = SamplingParams(
    max_tokens=800, min_tokens=50, temperature=0.7, top_p=0.9, top_k=50,
)

print(f"Loading model: {MODEL_ID}\n")
llm = LLM(MODEL_ID)

# Single-turn
print("=== Single-turn chat ===")
outputs = llm.chat([
    {"role": "system", "content": "You are a helpful assistant specializing in HPC and AI."},
    {"role": "user",   "content": "What is tensor parallelism and why is it important for LLM inference?"},
], sampling_params=sampling_params)
print(outputs[0].outputs[0].text.strip(), "\n")

# Multi-turn
print("=== Multi-turn chat ===")
outputs = llm.chat([
    {"role": "system",    "content": "You are a concise and helpful assistant."},
    {"role": "user",      "content": "What is an NPU?"},
    {"role": "assistant", "content": "An NPU (Neural Processing Unit) is a specialized chip designed to accelerate AI workloads more efficiently than CPUs or GPUs."},
    {"role": "user",      "content": "How does FuriosaAI's RNGD NPU differ from NVIDIA GPUs for LLM inference?"},
], sampling_params=sampling_params)
print(outputs[0].outputs[0].text.strip())
