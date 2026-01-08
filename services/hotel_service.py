# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
from typing import List, Dict, Optional


def search_hotels(
    city: Optional[str], check_in: Optional[str], check_out: Optional[str]
) -> List[Dict]:
    if not city or not check_in or not check_out:
        return []
    # Placeholder results; replace with actual hotel API integration
    return [
        {
            "name": "Grand Plaza",
            "city": city.title(),
            "check_in": check_in,
            "check_out": check_out,
            "price_usd_per_night": 120.0,
            "rating": 4.3,
        },
        {
            "name": "City Comfort Inn",
            "city": city.title(),
            "check_in": check_in,
            "check_out": check_out,
            "price_usd_per_night": 85.0,
            "rating": 4.0,
        },
    ]

