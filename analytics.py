# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict

DB_PATH = Path("travel.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_events():
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            action TEXT NOT NULL,
            meta TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_events()


def log_event(category: str, action: str, meta: str = ""):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events(category, action, meta, created_at) VALUES (?, ?, ?, ?)",
        (category, action, meta, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def metrics() -> Dict[str, int]:
    conn = _conn()
    cur = conn.cursor()
    counts = {}
    for cat in ["chat", "flights", "hotels", "weather", "itinerary", "auth"]:
        cur.execute("SELECT COUNT(*) FROM events WHERE category = ?", (cat,))
        counts[cat] = cur.fetchone()[0]
    conn.close()
    return counts

