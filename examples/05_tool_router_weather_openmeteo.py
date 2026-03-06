"""
05_tool_router_weather_openmeteo.py
Tool Calling via Python Router + Open-Meteo (real weather, no API key)
Model: furiosa-ai/Llama-3.1-8B-Instruct (HF license required)

Pattern:
  1. Python router detects weather intent from user message
  2. Calls Open-Meteo geocoding + forecast APIs
  3. Injects result as role="tool" message
  4. LLM generates final natural-language answer

Try: "What is the weather in Seoul?"
     "What is the temperature in Dallas in fahrenheit?"
Commands: /reset  /exit  /quit
"""
import asyncio, json, random, re, string, urllib.parse, urllib.request
from furiosa_llm import LLM, SamplingParams

MODEL_ID = "furiosa-ai/Llama-3.1-8B-Instruct"
SAMPLING = SamplingParams(max_tokens=256, temperature=0.7, top_p=0.9, top_k=50)
SYSTEM   = "You are a helpful assistant. Use tool output when provided."

_GEOCACHE: dict = {}
_WEATHER_KW = ("weather","temperature","temp","forecast","rain","sunny","cloudy","degrees")
_CITY_CC = {
    "seoul":"KR","busan":"KR","daejeon":"KR","incheon":"KR",
    "tokyo":"JP","osaka":"JP",
    "dallas":"US","new york":"US","chicago":"US","san francisco":"US",
    "london":"GB","paris":"FR","berlin":"DE","beijing":"CN",
}
_WMO = {
    0:"clear sky",1:"mainly clear",2:"partly cloudy",3:"overcast",
    45:"fog",51:"light drizzle",61:"slight rain",63:"moderate rain",65:"heavy rain",
    71:"slight snow",80:"rain showers",95:"thunderstorm",
}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "furiosa-llm-demo/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def _geocode(city: str, cc: str) -> tuple[float, float, str]:
    key = (city.lower(), cc.upper())
    if key in _GEOCACHE:
        return _GEOCACHE[key]
    q = urllib.parse.quote(city)
    for url in [
        f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=en&format=json&country={cc}",
        f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=en&format=json",
    ]:
        res = _get_json(url).get("results") or []
        if res:
            break
    if not res:
        raise ValueError(f"Geocoding failed for {city!r}")
    r0 = res[0]
    pretty = ", ".join(p for p in [r0.get("name") or city, r0.get("admin1"), r0.get("country")] if p)
    _GEOCACHE[key] = (float(r0["latitude"]), float(r0["longitude"]), pretty)
    return _GEOCACHE[key]


def get_current_weather(city: str, country: str, unit: str) -> str:
    unit = unit.lower() if unit.lower() in ("celsius","fahrenheit") else "celsius"
    lat, lon, pretty = _geocode(city, country)
    data = _get_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current_weather=true&temperature_unit={unit}&timezone=auto"
    )
    cw   = data.get("current_weather") or {}
    temp = cw.get("temperature")
    if temp is None:
        raise ValueError(f"No temperature data for {pretty}")
    sym  = "°F" if unit == "fahrenheit" else "°C"
    desc = _WMO.get(cw.get("weathercode"), "")
    wind = cw.get("windspeed")
    extras = [e for e in [f"wind {wind} km/h" if wind else "", desc] if e]
    return f"Current weather in {pretty}: {temp}{sym}" + (f" ({', '.join(extras)})" if extras else "") + "."


def _gen_id() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=9))


def _is_weather(text: str) -> bool:
    return any(k in text.lower() for k in _WEATHER_KW)


def _parse_weather_args(text: str) -> tuple[str, str, str]:
    t = text.lower()
    unit = "fahrenheit" if any(x in t for x in ("fahrenheit"," f ","°f")) else "celsius"
    for city, cc in _CITY_CC.items():
        if city in t:
            return city.title(), cc, unit
    m = re.search(r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
    return (m.group(1).strip() if m else "Seoul"), "KR", unit


async def _stream(llm: LLM, messages: list[dict]) -> str:
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

    print("=== Streaming Chat + Tool Router (Open-Meteo) ===")
    print("Try: 'What is the weather in Seoul?'")
    print("Commands: /reset  /exit  /quit")
    print("-" * 70)

    while True:
        try:
            user_text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye."); return
        if not user_text: continue
        if user_text.lower() in ("/exit", "/quit"):
            print("Goodbye."); return
        if user_text.lower() == "/reset":
            messages = [{"role": "system", "content": SYSTEM}]
            print("(History cleared.)\n"); continue

        messages.append({"role": "user", "content": user_text})

        if _is_weather(user_text):
            city, cc, unit = _parse_weather_args(user_text)
            print(f"[TOOL] get_current_weather(city={city!r}, country={cc!r}, unit={unit!r})")
            try:
                result = get_current_weather(city, cc, unit)
                print(f"[RESULT] {result}")
                messages.append({"role": "tool", "content": {"output": result}, "tool_call_id": _gen_id()})
            except Exception as e:
                print(f"[TOOL ERROR] {e}")

        print("Assistant> ", end="", flush=True)
        reply = await _stream(llm, messages)
        messages.append({"role": "assistant", "content": reply})
        print()


if __name__ == "__main__":
    asyncio.run(main())
