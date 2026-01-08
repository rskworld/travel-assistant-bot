# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import os
from typing import Dict, Optional
import requests
from .cache import get as cache_get, set as cache_set


def get_weather(location: Optional[str]) -> Dict:
    if not location:
        return {"error": "location required"}
    key = f"weather:{location.lower()}"
    cached = cache_get(key)
    if cached:
        return cached
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {
            "location": location,
            "note": "Provide OPENWEATHER_API_KEY to fetch live weather.",
        }
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        data = r.json()
        main = data.get("main", {})
        weather = (data.get("weather") or [{}])[0]
        result = {
            "location": location,
            "temp_c": main.get("temp"),
            "description": weather.get("description"),
            "humidity": main.get("humidity"),
        }
        cache_set(key, result, ttl=300)
        return result
    except Exception:
        return {"location": location, "error": "failed to fetch weather"}
