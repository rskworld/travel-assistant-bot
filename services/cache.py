# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import time
from typing import Any, Dict, Tuple

_CACHE: Dict[str, Tuple[float, Any]] = {}


def get(key: str) -> Any:
    entry = _CACHE.get(key)
    if not entry:
        return None
    exp, val = entry
    if time.time() > exp:
        _CACHE.pop(key, None)
        return None
    return val


def set(key: str, value: Any, ttl: int = 300):
    _CACHE[key] = (time.time() + ttl, value)

