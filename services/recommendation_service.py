# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
from typing import Dict, List


def get_recommendations(preferences: Dict) -> List[Dict]:
    budget = preferences.get("budget", "medium")
    style = preferences.get("style", "relaxed")
    city = preferences.get("city", "unknown")
    if style == "adventure":
        items = ["Hiking trail", "River rafting", "Local food market"]
    elif style == "luxury":
        items = ["Fine dining", "Spa retreat", "Exclusive city tour"]
    else:
        items = ["City park", "Museum visit", "Neighborhood walk"]
    return [
        {"city": city, "budget": budget, "style": style, "suggestions": items},
    ]

