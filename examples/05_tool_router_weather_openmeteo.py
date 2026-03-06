"""
05_tool_router_weather_openmeteo.py
=====================================
Tool Calling via Python Router + Real Weather API (Open-Meteo)
---------------------------------------------------------------
Demonstrates an offline tool-calling pattern without relying on
llm.chat(tools=...) JSON parsing. Instead:

  1. The Python router inspects the user's message to decide
     whether to call a tool.
  2. If a weather query is detected, the real Open-Meteo API
     is called (no API key required).
  3. The tool result is injected as a role="tool" message.
  4. The LLM generates a final natural-language answer.

This pattern is robust for offline use when the model's built-in
tool-call JSON output is not available or reliable.

APIs used:
  - Open-Meteo Geocoding: https://geocoding-api.open-meteo.com
  - Open-Meteo Forecast:  https://api.open-meteo.com

Model used: furiosa-ai/Llama-3.1-8B-Instruct

Ref:
  https://developer.furiosa.ai/latest/en/furiosa_llm/toolcalling.html
"""

import asyncio
import json
import random
import re
import string
import urllib.parse
import urllib.request
from furiosa_llm import LLM, SamplingParams

# ── Model ────────────────────────────────────────────────────────────────────
MODEL_ID = "furiosa-ai/Llama-3.1-8B-Instruct"

SAMPLING = SamplingParams(
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
)

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "When tool output is provided in the conversation, use it to answer "
    "the user's question accurately."
)

# ── Geocoding cache ───────────────────────────────────────────────────────────
_GEOCODE_CACHE: dict[tuple[str, str], tuple[float, float, str]] = {}


# ── Utilities ─────────────────────────────────────────────────────────────────

def _http_get_json(url: str, timeout: int = 10) -> dict:
    """Fetch a URL and return parsed JSON."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "furiosa-llm-tool-demo/1.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _geocode_city(city: str, country: str) -> tuple[float, float, str]:
    """
    Resolve city + country to (latitude, longitude, pretty_name).
    Results are cached to avoid repeated API calls.
    """
    key = (city.strip().lower(), country.strip().upper())
    if key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[key]

    q  = urllib.parse.quote(city.strip())
    cc = urllib.parse.quote(country.strip().upper())

    # Try with country filter first, then without
    for url in [
        f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=en&format=json&country={cc}",
        f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=en&format=json",
    ]:
        data = _http_get_json(url)
        results = data.get("results") or []
        if results:
            break

    if not results:
        raise ValueError(f"Geocoding failed for city={city!r}, country={country!r}")

    r0  = results[0]
    lat = float(r0["latitude"])
    lon = float(r0["longitude"])

    parts = [p for p in [r0.get("name") or city, r0.get("admin1"), r0.get("country")] if p]
    pretty = ", ".join(parts)

    _GEOCODE_CACHE[key] = (lat, lon, pretty)
    return lat, lon, pretty


def _weathercode_to_text(code: int | None) -> str | None:
    """Convert WMO weather code to a human-readable description."""
    if code is None:
        return None
    mapping = {
        0: "clear sky",         1: "mainly clear",      2: "partly cloudy",
        3: "overcast",          45: "fog",               48: "depositing rime fog",
        51: "light drizzle",    53: "moderate drizzle",  55: "dense drizzle",
        61: "slight rain",      63: "moderate rain",     65: "heavy rain",
        71: "slight snow",      73: "moderate snow",     75: "heavy snow",
        80: "rain showers",     81: "moderate showers",  82: "violent showers",
        95: "thunderstorm",     96: "thunderstorm/hail", 99: "thunderstorm/heavy hail",
    }
    return mapping.get(code, f"weather code {code}")


def get_current_weather(city: str, country: str, unit: str) -> str:
    """
    Fetch current weather from Open-Meteo for the given city.
    Returns a formatted string suitable for injection as a tool result.
    """
    unit = (unit or "celsius").strip().lower()
    if unit not in ("celsius", "fahrenheit"):
        unit = "celsius"

    lat, lon, pretty = _geocode_city(city, country)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        f"&temperature_unit={urllib.parse.quote(unit)}"
        "&timezone=auto"
    )
    data = _http_get_json(url)
    cw   = data.get("current_weather") or {}

    temp  = cw.get("temperature")
    wind  = cw.get("windspeed")
    wcode = cw.get("weathercode")

    if temp is None:
        raise ValueError(f"Open-Meteo returned no temperature for {pretty}")

    unit_symbol = "°F" if unit == "fahrenheit" else "°C"
    desc        = _weathercode_to_text(wcode)

    extras = []
    if wind is not None:
        extras.append(f"wind {wind} km/h")
    if desc is not None:
        extras.append(desc)

    extra_str = f" ({', '.join(extras)})" if extras else ""
    return f"Current weather in {pretty}: {temp}{unit_symbol}{extra_str}."


def _gen_id(n: int = 9) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


# ── Router helpers ────────────────────────────────────────────────────────────

# Mapping of city names (lowercase) to ISO country codes
CITY_COUNTRY_MAP: dict[str, str] = {
    "seoul": "KR", "busan": "KR", "incheon": "KR", "daejeon": "KR",
    "tokyo": "JP", "osaka": "JP", "kyoto": "JP",
    "dallas": "US", "new york": "US", "chicago": "US", "san francisco": "US",
    "london": "GB", "paris": "FR", "berlin": "DE", "beijing": "CN",
}

WEATHER_KEYWORDS = ("weather", "temperature", "temp", "forecast", "rain", "sunny",
                    "cloudy", "hot", "cold", "degrees", "humidity")


def _is_weather_query(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in WEATHER_KEYWORDS)


def _extract_city_and_unit(text: str) -> tuple[str, str, str]:
    """
    Heuristically extract city name, country code, and temperature unit
    from the user's message.
    """
    t = text.lower()

    # Temperature unit
    if "fahrenheit" in t or " f " in t or t.endswith(" f"):
        unit = "fahrenheit"
    else:
        unit = "celsius"

    # City name: try known cities first, then regex fallback
    for city_lower, country in CITY_COUNTRY_MAP.items():
        if city_lower in t:
            return city_lower.title(), country, unit

    # Regex fallback: "in <CityName>"
    m = re.search(r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
    if m:
        city = m.group(1).strip()
        return city, "US", unit

    return "Seoul", "KR", unit


# ── Streaming helper ──────────────────────────────────────────────────────────

async def _stream_response(llm: LLM, messages: list[dict]) -> str:
    prompt = llm.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    full = ""
    async for chunk in llm.stream_generate(prompt, SAMPLING):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full.strip()


# ── Main chat loop ────────────────────────────────────────────────────────────

async def main() -> None:
    print(f"Loading model: {MODEL_ID}\n")
    llm = LLM(MODEL_ID)

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("=== Streaming Chat + Tool Router (Open-Meteo real weather) ===")
    print("Try: 'What is the weather in Seoul?'")
    print("     'What is the temperature in Dallas in fahrenheit?'")
    print("Commands: /reset  → clear history | /exit or /quit → end")
    print("-" * 70)

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
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("(Conversation history cleared.)\n")
            continue

        messages.append({"role": "user", "content": user_text})

        # ── Tool routing ──────────────────────────────────────────────────────
        if _is_weather_query(user_text):
            city, country, unit = _extract_city_and_unit(user_text)
            print(f"[TOOL] get_current_weather(city={city!r}, country={country!r}, unit={unit!r})")
            try:
                tool_result = get_current_weather(city=city, country=country, unit=unit)
                print(f"[TOOL RESULT] {tool_result}")
                messages.append({
                    "role":        "tool",
                    "content":     {"output": tool_result},
                    "tool_call_id": _gen_id(),
                })
            except Exception as exc:
                print(f"[TOOL ERROR] {type(exc).__name__}: {exc}")
                # Continue without tool result; LLM will respond without it

        # ── Generate final response ───────────────────────────────────────────
        print("Assistant> ", end="", flush=True)
        assistant_text = await _stream_response(llm, messages)
        messages.append({"role": "assistant", "content": assistant_text})
        print()


if __name__ == "__main__":
    asyncio.run(main())
