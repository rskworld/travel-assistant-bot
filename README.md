<!-- RSK World - Free Programming Resources & Source Code -->
<!-- Founder: Molla Samser | Designer & Tester: Rima Khatun -->
<!-- Website: https://rskworld.in/contact.php | Year: 2026 -->
# Travel Assistant Bot

A web-ready chatbot for flights, hotels, recommendations, itineraries, and weather.

Features:
- JWT auth, admin metrics, rate-limit
- Flight/Hotel placeholder adapters
- Weather via OpenWeather (with caching)
- Shareable itinerary links
- Budget calculator
- Multilingual UI (English/Bengali)
- Dark mode

Environment:
- OPENAI_API_KEY, OPENAI_MODEL
- OPENWEATHER_API_KEY
- JWT_SECRET, RATE_LIMIT_PER_MIN

Run:
```
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

