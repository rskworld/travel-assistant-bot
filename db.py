# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import base64
import os

DB_PATH = Path("travel.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            items TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    try:
        cur.execute('ALTER TABLE itineraries ADD COLUMN share_token TEXT')
        conn.commit()
    except Exception:
        pass
    conn.close()

def ensure_share_support():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('ALTER TABLE itineraries ADD COLUMN share_token TEXT')
        conn.commit()
    except Exception:
        pass
    conn.close()

def add_itinerary(user: str, items: List[Dict[str, Any]]):
    conn = get_conn()
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO itineraries(user, items, created_at) VALUES (?, ?, ?)",
        (user, json.dumps(items), created_at),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "user": user, "items": items, "created_at": created_at}


def list_itineraries():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user, items, created_at FROM itineraries ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append(
            {
                "id": r[0],
                "user": r[1],
                "items": json.loads(r[2]),
                "created_at": r[3],
            }
        )
    return result


def delete_itinerary(item_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM itineraries WHERE id = ?", (item_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def set_share_token(itinerary_id: int) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    token = base64.urlsafe_b64encode(os.urandom(18)).decode().rstrip("=")
    cur.execute("UPDATE itineraries SET share_token = ? WHERE id = ?", (token, itinerary_id))
    conn.commit()
    cur.execute("SELECT id, user, items, created_at, share_token FROM itineraries WHERE id = ?", (itinerary_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "id": row[0],
        "user": row[1],
        "items": json.loads(row[2]),
        "created_at": row[3],
        "share_token": row[4],
    }


def get_itinerary_by_token(token: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user, items, created_at, share_token FROM itineraries WHERE share_token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "id": row[0],
        "user": row[1],
        "items": json.loads(row[2]),
        "created_at": row[3],
        "share_token": row[4],
    }
