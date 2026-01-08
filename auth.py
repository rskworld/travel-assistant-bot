# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
import os
import hmac
import hashlib
import base64
import json
from typing import Optional, Tuple
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("travel.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change")


def _conn():
    return sqlite3.connect(DB_PATH)


def _init_users():
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    try:
        cur.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT "user"')
        conn.commit()
    except Exception:
        pass
    conn.close()


_init_users()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + password).encode()).hexdigest()


def register_user(email: Optional[str], password: Optional[str]) -> Tuple[bool, str]:
    if not email or not password:
        return False, "email and password required"
    conn = _conn()
    cur = conn.cursor()
    salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
    ph = _hash_password(password, salt)
    try:
        cur.execute(
            "INSERT INTO users(email, password_hash, salt, created_at, role) VALUES (?, ?, ?, ?, ?)",
            (email.strip().lower(), ph, salt, datetime.utcnow().isoformat(), "user"),
        )
        conn.commit()
        return True, "registered"
    except sqlite3.IntegrityError:
        return False, "email already exists"
    finally:
        conn.close()


def login_user(email: Optional[str], password: Optional[str]) -> Tuple[bool, str]:
    if not email or not password:
        return False, "email and password required"
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, salt FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "invalid credentials"
    uid, ph, salt = row
    if _hash_password(password, salt) != ph:
        return False, "invalid credentials"
    token = create_jwt({"sub": email.strip().lower(), "uid": uid})
    return True, token


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def create_jwt(payload: dict, exp_minutes: int = 60 * 24) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = dict(payload)
    payload["exp"] = int((datetime.utcnow() + timedelta(minutes=exp_minutes)).timestamp())
    head = _b64url(json.dumps(header, separators=(",", ":")).encode())
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    msg = f"{head}.{body}".encode()
    sig = hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest()
    return f"{head}.{body}.{_b64url(sig)}"


def verify_jwt(token: Optional[str]) -> Optional[dict]:
    if not token:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        head, body, sig = parts
        msg = f"{head}.{body}".encode()
        expected = _b64url(hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=="))
        if int(datetime.utcnow().timestamp()) > int(payload.get("exp", 0)):
            return None
        return payload
    except Exception:
        return None


def get_user_from_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = verify_jwt(token)
    return payload.get("sub") if payload else None


def require_auth(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return "missing bearer token"
    token = authorization.split(" ", 1)[1]
    payload = verify_jwt(token)
    if not payload:
        return "invalid or expired token"
    return None


def require_admin(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return "missing bearer token"
    token = authorization.split(" ", 1)[1]
    payload = verify_jwt(token)
    if not payload:
        return "invalid or expired token"
    email = payload.get("sub")
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    role = row[0] if row else "user"
    if role != "admin":
        return "admin required"
    return None
