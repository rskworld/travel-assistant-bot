# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import os
from typing import List, Dict

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # fallback when library not present


def _fallback(messages: List[Dict]):
    last = messages[-1]["content"] if messages else ""
    text = last.lower()
    if any(k in text for k in ["flight", "flights", "book flight"]):
        return "To search flights, provide origin, destination, and date."
    if any(k in text for k in ["hotel", "hotels", "stay"]):
        return "To search hotels, provide city, check-in, and check-out dates."
    if "weather" in text:
        return "To get weather, provide a city or location name."
    if any(k in text for k in ["plan", "itinerary"]):
        return "Tell me your trip goals; I can build an itinerary."
    return "I can help with flights, hotels, recommendations, itinerary, and weather."


def generate_response(messages: List[Dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return _fallback(messages)
    client = OpenAI(api_key=api_key)
    try:
        chat = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.4,
        )
        return chat.choices[0].message.content or _fallback(messages)
    except Exception:
        return _fallback(messages)

