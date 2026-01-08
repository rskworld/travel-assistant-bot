# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
from typing import List, Dict, Optional
from datetime import datetime


def search_flights(
    origin: Optional[str], destination: Optional[str], date: Optional[str]
) -> List[Dict]:
    if not origin or not destination or not date:
        return []
    try:
        _ = datetime.fromisoformat(date)
    except Exception:
        pass
    # Placeholder results; replace with actual travel API integration
    return [
        {
            "airline": "Example Air",
            "flight_number": "EX123",
            "origin": origin.upper(),
            "destination": destination.upper(),
            "date": date,
            "price_usd": 249.99,
            "duration": "3h 10m",
        },
        {
            "airline": "Sample Airlines",
            "flight_number": "SA456",
            "origin": origin.upper(),
            "destination": destination.upper(),
            "date": date,
            "price_usd": 279.5,
            "duration": "3h 25m",
        },
    ]

