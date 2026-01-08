// RSK World - Free Programming Resources & Source Code
// Founder: Molla Samser | Designer & Tester: Rima Khatun
// Website: https://rskworld.in/contact.php | Year: 2026
async function postJSON(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `msg msg-${role}`;
  el.textContent = `${role}: ${text}`;
  document.getElementById("messages").appendChild(el);
  document.getElementById("messages").scrollTop =
    document.getElementById("messages").scrollHeight;
}

// i18n
const i18n = {
  en: {
    title: "Travel Assistant Bot",
    subtitle:
      "Book flights and hotels, get recommendations, plan itineraries, and check weather.",
    tools: "Quick Tools",
    flights: "Search Flights",
    hotels: "Search Hotels",
    weather: "Weather",
    itinerary: "Itinerary",
    send: "Send",
    ask_placeholder: "Ask me anything about your trip...",
  },
  bn: {
    title: "ট্রাভেল অ্যাসিস্ট্যান্ট বট",
    subtitle:
      "ফ্লাইট ও হোটেল বুকিং, পরামর্শ, ভ্রমণ পরিকল্পনা এবং আবহাওয়া তথ্য।",
    tools: "সহজ টুলস",
    flights: "ফ্লাইট খুঁজুন",
    hotels: "হোটেল খুঁজুন",
    weather: "আবহাওয়া",
    itinerary: "ইটিনারি",
    send: "পাঠান",
    ask_placeholder: "ভ্রমণ সম্পর্কে আমাকে যেকোনো প্রশ্ন করুন...",
  },
};

function applyLang(lang) {
  const t = i18n[lang] || i18n.en;
  document.getElementById("title-text").textContent = t.title;
  document.getElementById("subtitle-text").textContent = t.subtitle;
  document.getElementById("tools-title").textContent = t.tools;
  document.getElementById("flights-title").textContent = t.flights;
  document.getElementById("hotels-title").textContent = t.hotels;
  document.getElementById("weather-title").textContent = t.weather;
  document.getElementById("itinerary-title").textContent = t.itinerary;
  document.getElementById("send-btn").textContent = t.send;
  document.getElementById("chat-input").placeholder = t.ask_placeholder;
}

document.getElementById("lang-select").addEventListener("change", (e) => {
  applyLang(e.target.value);
});
applyLang("en");

// dark mode
function applyTheme() {
  const dark = localStorage.getItem("dark") === "1";
  document.body.classList.toggle("dark", dark);
  document.getElementById("dark-toggle").checked = dark;
}
document.getElementById("dark-toggle").addEventListener("change", (e) => {
  localStorage.setItem("dark", e.target.checked ? "1" : "0");
  applyTheme();
});
applyTheme();

const chatMessages = [];
document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const content = input.value.trim();
  if (!content) return;
  chatMessages.push({ role: "user", content });
  addMessage("user", content);
  input.value = "";
  const res = await postJSON("/api/chat", { messages: chatMessages });
  const reply = res.reply;
  chatMessages.push({ role: "assistant", content: reply });
  addMessage("assistant", reply);
});

// auth
let bearerToken = null;
document.getElementById("auth-register").addEventListener("click", async () => {
  const email = document.getElementById("auth-email").value;
  const password = document.getElementById("auth-pass").value;
  const res = await postJSON("/api/auth/register", { email, password });
  addMessage("system", res.message || (res.ok ? "registered" : "error"));
});

document.getElementById("auth-login").addEventListener("click", async () => {
  const email = document.getElementById("auth-email").value;
  const password = document.getElementById("auth-pass").value;
  const res = await postJSON("/api/auth/login", { email, password });
  if (res.ok && res.token) {
    bearerToken = res.token;
    addMessage("system", "login success");
  } else {
    addMessage("system", res.message || "login failed");
  }
});

document.getElementById("flight-search").addEventListener("click", async () => {
  const origin = document.getElementById("flight-origin").value;
  const destination = document.getElementById("flight-destination").value;
  const date = document.getElementById("flight-date").value;
  const res = await postJSON("/api/flights", { origin, destination, date });
  document.getElementById("flight-results").textContent = JSON.stringify(
    res.flights,
    null,
    2
  );
});

document.getElementById("hotel-search").addEventListener("click", async () => {
  const city = document.getElementById("hotel-city").value;
  const check_in = document.getElementById("hotel-checkin").value;
  const check_out = document.getElementById("hotel-checkout").value;
  const res = await postJSON("/api/hotels", { city, check_in, check_out });
  document.getElementById("hotel-results").textContent = JSON.stringify(
    res.hotels,
    null,
    2
  );
});

document.getElementById("weather-check").addEventListener("click", async () => {
  const location = document.getElementById("weather-location").value;
  const res = await postJSON("/api/weather", { location });
  document.getElementById("weather-results").textContent = JSON.stringify(
    res.weather,
    null,
    2
  );
});

document.getElementById("itinerary-list").addEventListener("click", async () => {
  const headers = bearerToken ? { Authorization: `Bearer ${bearerToken}` } : {};
  const r = await fetch("/api/itineraries", { headers });
  const res = await r.json();
  document.getElementById("itinerary-results").textContent = JSON.stringify(
    res.itineraries,
    null,
    2
  );
});

document.getElementById("itinerary-add").addEventListener("click", async () => {
  const headers = bearerToken ? { Authorization: `Bearer ${bearerToken}` } : {};
  const r = await fetch("/api/itineraries", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify({
      items: [
        { type: "flight", ref: "EX123", note: "NYC to SFO" },
        { type: "hotel", ref: "Grand Plaza", note: "2 nights" },
      ],
    }),
  });
  const res = await r.json();
  document.getElementById("itinerary-results").textContent = JSON.stringify(
    res.itinerary,
    null,
    2
  );
});

document.getElementById("budget-calc").addEventListener("click", async () => {
  const nights = Number(document.getElementById("budget-nights").value);
  const hotel_per_night = Number(document.getElementById("budget-hotel").value);
  const flight_cost = Number(document.getElementById("budget-flight").value);
  const extras = Number(document.getElementById("budget-extras").value);
  const res = await postJSON("/api/budget", {
    nights,
    hotel_per_night,
    flight_cost,
    extras,
  });
  document.getElementById("budget-results").textContent = JSON.stringify(res, null, 2);
});

document.getElementById("share-make").addEventListener("click", async () => {
  const id = Number(document.getElementById("share-id").value);
  if (!id) return;
  const headers = bearerToken ? { Authorization: `Bearer ${bearerToken}` } : {};
  const r = await fetch(`/api/itineraries/${id}/share`, { method: "POST", headers });
  const res = await r.json();
  document.getElementById("share-results").textContent = JSON.stringify(res, null, 2);
});
