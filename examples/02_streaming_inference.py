"""
02_streaming_inference.py
Streaming Inference with Furiosa-LLM
Model: furiosa-ai/Qwen2.5-0.5B-Instruct (no HF license required)
"""
import asyncio
from furiosa_llm import LLM, SamplingParams

MODEL_ID = "furiosa-ai/Qwen2.5-0.5B-Instruct"
sampling_params = SamplingParams(max_tokens=256, temperature=0.7, top_p=0.9, top_k=50)


async def stream_response(llm: LLM, question: str) -> None:
    message = [{"role": "user", "content": question}]
    prompt = llm.tokenizer.apply_chat_template(
        message, tokenize=False, add_generation_prompt=True
    )
    print(f"Q: {question}")
    print("A: ", end="", flush=True)
    async for chunk in llm.stream_generate(prompt, sampling_params):
        print(chunk, end="", flush=True)
    print("\n")


async def main() -> None:
    print(f"Loading model: {MODEL_ID}\n")
    llm = LLM(MODEL_ID)
    questions = [
        "What is quantum computing? Explain briefly.",
        "What are the main advantages of NPUs over GPUs for LLM inference?",
    ]
    for q in questions:
        await stream_response(llm, q)


if __name__ == "__main__":
    asyncio.run(main())
