"""
Portfolio backend.

- Serves the static frontend (index.html / style.css / script.js / assets).
- Exposes POST /api/chat, which forwards the visitor's question + short
  conversation history to Grok (x.ai), together with a system prompt built
  from resume_data.py, and returns Gyana's answer in her own words.

Run locally:
    cp .env.example .env      # then fill in XAI_API_KEY
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Open http://localhost:8000 in a browser.
"""

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from resume_data import build_system_prompt

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = build_system_prompt()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Gyana Sinha — Portfolio API")

# Wide-open CORS is fine here: this is a public read-only chat endpoint with
# no auth and no user data at rest. Tighten allow_origins if you deploy the
# frontend on a different domain than the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# --- very small in-memory rate limiter so the free Grok quota doesn't get hammered ---
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 12
_request_log: dict[str, list[float]] = {}


def _check_rate_limit(client_id: str) -> None:
    now = time.time()
    recent = [t for t in _request_log.get(client_id, []) if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    if len(recent) >= _RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many questions — please wait a minute and try again.")
    recent.append(now)
    _request_log[client_id] = recent


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)
    request_id: str = "anonymous"  # per-browser-tab id from the frontend, used for rate limiting only


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server isn't configured with an GROQ_API_KEY yet. Add one to backend/.env.",
        )

    _check_rate_limit(payload.request_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in payload.history[-8:]:
        if turn.role in ("user", "assistant"):
            messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": payload.message})

    try:
        response = requests.post(
    GROQ_API_URL,
    headers={
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": GROQ_MODEL,
        "messages": messages,
    },
    timeout=60,
)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the AI model: {exc}") from exc

    data = response.json()
    try:
        reply = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise HTTPException(status_code=502, detail="Unexpected response from the AI model.") from exc

    return ChatResponse(reply=reply)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": XAI_MODEL, "configured": bool(XAI_API_KEY)}


# --- static frontend ---
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/style.css")
def style():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js")
def script():
    return FileResponse(FRONTEND_DIR / "script.js")

# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# api_key = os.getenv("XAI_API_KEY")
# model = os.getenv("XAI_MODEL", "grok-4.5")

# print("API KEY LOADED:", bool(api_key))
# print("MODEL:", model)

# response = requests.post(
#     "https://api.x.ai/v1/chat/completions",
#     headers={
#         "Authorization": "Bearer " + api_key,
#         "Content-Type": "application/json",
#     },
#     json={
#         "model": model,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Say hello"
#             }
#         ]
#     },
#     timeout=60
# )

# print("STATUS:", response.status_code)
# print("RESPONSE:", response.text)