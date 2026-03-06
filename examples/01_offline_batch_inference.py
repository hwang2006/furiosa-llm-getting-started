"""
01_offline_batch_inference.py
Offline Batch Inference with Furiosa-LLM
Model: furiosa-ai/Qwen2.5-0.5B-Instruct (no HF license required)
"""
from furiosa_llm import LLM, SamplingParams

MODEL_ID = "furiosa-ai/Qwen2.5-0.5B-Instruct"

sampling_params = SamplingParams(
    max_tokens=256, min_tokens=10, temperature=0.7, top_p=0.9, top_k=50,
)

print(f"Loading model: {MODEL_ID}")
llm = LLM(MODEL_ID)

conversations = [
    [{"role": "user", "content": "What is the capital of France?"}],
    [{"role": "user", "content": "Explain what an NPU is in two sentences."}],
    [{"role": "user", "content": "Write a one-line Python function that reverses a string."}],
]

prompts = [
    llm.tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=True)
    for c in conversations
]

print(f"\nRunning batch inference on {len(prompts)} prompts...\n")
responses = llm.generate(prompts, sampling_params)

for i, (conv, resp) in enumerate(zip(conversations, responses)):
    print(f"[{i+1}] Q: {conv[0]['content']}")
    print(f"     A: {resp.outputs[0].text.strip()}\n")
