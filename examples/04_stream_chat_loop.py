"""
04_stream_chat_loop.py
Interactive Streaming Chat Loop (multi-turn)
Model: furiosa-ai/Llama-3.1-8B-Instruct (HF license required)
Commands: /reset  /exit  /quit
"""
import asyncio
from furiosa_llm import LLM, SamplingParams

MODEL_ID  = "furiosa-ai/Llama-3.1-8B-Instruct"
SAMPLING  = SamplingParams(max_tokens=512, temperature=0.7, top_p=0.9, top_k=50)
SYSTEM    = "You are a helpful assistant."


async def stream_one_turn(llm: LLM, messages: list[dict]) -> str:
    prompt = llm.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    full = ""
    async for chunk in llm.stream_generate(prompt, SAMPLING):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full.strip()


async def main() -> None:
    print(f"Loading model: {MODEL_ID}\n")
    llm = LLM(MODEL_ID)
    messages: list[dict] = [{"role": "system", "content": SYSTEM}]

    print("=== Interactive Streaming Chat ===")
    print("Commands: /exit  /quit  /reset")
    print("-" * 60)

    while True:
        try:
            user_text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if not user_text:
            continue
        if user_text.lower() in ("/exit", "/quit"):
            print("Goodbye.")
            return
        if user_text.lower() == "/reset":
            messages = [{"role": "system", "content": SYSTEM}]
            print("(History cleared.)\n")
            continue

        messages.append({"role": "user", "content": user_text})
        print("Assistant> ", end="", flush=True)
        reply = await stream_one_turn(llm, messages)
        messages.append({"role": "assistant", "content": reply})
        print()


if __name__ == "__main__":
    asyncio.run(main())
