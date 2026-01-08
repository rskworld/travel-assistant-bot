# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
from flask import Flask, render_template, request, jsonify
from services.openai_service import generate_response
from services.flight_service import search_flights
from services.hotel_service import search_hotels
from services.recommendation_service import get_recommendations
from services.weather_service import get_weather
from db import init_db, add_itinerary, list_itineraries, delete_itinerary, ensure_share_support, set_share_token, get_itinerary_by_token
from auth import register_user, login_user, require_auth, get_user_from_token, require_admin
from analytics import log_event, metrics
import os
import time
from typing import Dict
import logging

app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize database and setup logging (Flask 3.0 compatible)
def setup():
    init_db()
    ensure_share_support()
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

# Call setup at module level (replaces deprecated before_first_request)
setup()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

RATE_LIMIT: Dict[str, Dict[str, int]] = {}

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return response

@app.before_request
def rate_limit():
    key = request.remote_addr or "unknown"
    now = int(time.time())
    bucket = RATE_LIMIT.setdefault(key, {"ts": now, "count": 0})
    if now - bucket["ts"] >= 60:
        bucket["ts"] = now
        bucket["count"] = 0
    bucket["count"] += 1
    if bucket["count"] > int(os.getenv("RATE_LIMIT_PER_MIN", "120")):
        return jsonify({"error": "rate limit exceeded"}), 429

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    messages = data.get("messages", [])
    reply = generate_response(messages)
    try:
        log_event("chat", "message")
    except Exception:
        pass
    return jsonify({"reply": reply})


@app.route("/api/flights", methods=["POST"])
def api_flights():
    data = request.get_json(force=True)
    origin = data.get("origin")
    destination = data.get("destination")
    date = data.get("date")
    results = search_flights(origin, destination, date)
    try:
        log_event("flights", "search", f"{origin}-{destination}")
    except Exception:
        pass
    return jsonify({"flights": results})


@app.route("/api/hotels", methods=["POST"])
def api_hotels():
    data = request.get_json(force=True)
    city = data.get("city")
    check_in = data.get("check_in")
    check_out = data.get("check_out")
    results = search_hotels(city, check_in, check_out)
    try:
        log_event("hotels", "search", city or "")
    except Exception:
        pass
    return jsonify({"hotels": results})


@app.route("/api/recommendations", methods=["POST"])
def api_recommendations():
    data = request.get_json(force=True)
    preferences = data.get("preferences", {})
    recs = get_recommendations(preferences)
    return jsonify({"recommendations": recs})


@app.route("/api/weather", methods=["POST"])
def api_weather():
    data = request.get_json(force=True)
    location = data.get("location")
    info = get_weather(location)
    try:
        log_event("weather", "check", location or "")
    except Exception:
        pass
    return jsonify({"weather": info})

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")
    ok, msg = register_user(email, password)
    try:
        log_event("auth", "register", email or "")
    except Exception:
        pass
    code = 201 if ok else 400
    return jsonify({"ok": ok, "message": msg}), code

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")
    ok, token_or_msg = login_user(email, password)
    try:
        log_event("auth", "login", email or "")
    except Exception:
        pass
    code = 200 if ok else 401
    return jsonify({"ok": ok, "token": token_or_msg if ok else None, "message": None if ok else token_or_msg}), code

@app.route("/api/itineraries", methods=["GET"])
def api_list_itineraries():
    user = get_user_from_token(request.headers.get("Authorization"))
    items = list_itineraries()
    if user is not None:
        items = [i for i in items if i.get("user") == user]
    return jsonify({"itineraries": items})


@app.route("/api/itineraries", methods=["POST"])
def api_add_itinerary():
    auth_error = require_auth(request.headers.get("Authorization"))
    if auth_error:
        return jsonify({"error": auth_error}), 401
    data = request.get_json(force=True)
    user = get_user_from_token(request.headers.get("Authorization")) or "guest"
    items = data.get("items", [])
    row = add_itinerary(user, items)
    try:
        log_event("itinerary", "add", user)
    except Exception:
        pass
    return jsonify({"itinerary": row}), 201


@app.route("/api/itineraries/<int:item_id>", methods=["DELETE"])
def api_delete_itinerary(item_id: int):
    auth_error = require_auth(request.headers.get("Authorization"))
    if auth_error:
        return jsonify({"error": auth_error}), 401
    ok = delete_itinerary(item_id)
    return jsonify({"deleted": ok})


@app.route("/api/itineraries/<int:item_id>/share", methods=["POST"])
def api_share_itinerary(item_id: int):
    auth_error = require_auth(request.headers.get("Authorization"))
    if auth_error:
        return jsonify({"error": auth_error}), 401
    row = set_share_token(item_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    token = row.get("share_token")
    try:
        log_event("itinerary", "share", str(item_id))
    except Exception:
        pass
    url = request.host_url.rstrip("/") + f"/share/{token}"
    return jsonify({"share_url": url, "token": token})


@app.route("/share/<token>", methods=["GET"])
def share_page(token: str):
    row = get_itinerary_by_token(token)
    if not row:
        return jsonify({"error": "invalid link"}), 404
    return render_template("share.html", itinerary=row)


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    admin_error = require_admin(request.headers.get("Authorization"))
    if admin_error:
        return jsonify({"error": admin_error}), 401
    return jsonify({"metrics": metrics()})


@app.route("/api/budget", methods=["POST"])
def api_budget():
    data = request.get_json(force=True)
    nights = int(data.get("nights", 0))
    hotel_per_night = float(data.get("hotel_per_night", 0))
    flight_cost = float(data.get("flight_cost", 0))
    extras = float(data.get("extras", 0))
    total = nights * hotel_per_night + flight_cost + extras
    try:
        log_event("itinerary", "budget")
    except Exception:
        pass
    return jsonify({"total_usd": round(total, 2)})


@app.route("/readme")
def readme_page():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("readme.html", content=content)
    except Exception:
        return render_template("readme.html", content="README not found.")


@app.route("/license")
def license_page():
    try:
        with open("LICENSE.md", "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("license.html", content=content)
    except Exception:
        return render_template("license.html", content="LICENSE not found.")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

