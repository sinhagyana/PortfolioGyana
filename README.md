# Gyana Sinha — Portfolio + AI Agent

A portfolio site with a chat agent that answers questions about Gyana **in its own words**,
not by pasting resume lines. It's grounded in a structured facts file, not the model's
imagination so it won't invent experience she doesn't have.

**Stack** (matches the skills on her resume):
- Backend: **Python + FastAPI**, `requests` to call the model, no other frameworks.
- Frontend: plain **HTML/CSS/JS** — no build step, no npm, nothing extra to install.
- Model: **Llama 3.3 70B** via the **Groq API** (OpenAI compatible), using Groq for fast and cost effective inference.
  
## How the "own words" part works

`backend/resume_data.py` holds the facts (jobs, projects, skills, education) as plain Python
data — no marketing prose. `build_system_prompt()` turns that into instructions for the model:
answer from these facts, in your own words, conversationally, and say so honestly if something
isn't covered. That system prompt goes to Grok on every request in `main.py`'s `/api/chat`
route, so every answer is generated fresh, grounded in real facts, and never a copy paste of
the resume.

To update the portfolio later (new job, new project), edit `resume_data.py` only — the prompt,
the chat agent, and the eventual answers all update automatically. The website text in
`frontend/index.html` is separate copy, so update that too if you want the static sections in
sync.

## Project layout

```
portfolio-project/
├── backend/
│   ├── main.py             # FastAPI app: serves the frontend + POST /api/chat
│   ├── resume_data.py       # single source of truth for Gyana's facts
│   ├── requirements.txt
│   └── .env         # copy to .env and add your Groq API key
└── frontend/
    ├── index.html
    ├── style.css
    ├── script.js
    └── assets/gyana.jpg
    └── assets/GyanaSinha.pdf
```

## Run it locally

1. Get a key at **https://console.groq.com/** (Grok has a free tier for light use; check current
   limits/pricing there since they change).
2. ```bash
   cd backend
   #create .env file
   cp .env
   # open .env and paste your GROQ_API_KEY and paste GROQ_MODEL
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
3. Open **http://localhost:8000** — FastAPI serves the frontend directly, so there's nothing
   else to start.

## Deploying

Any host that runs a Python process works (Render, Railway, Fly.io, a VPS, etc.):

1. Set the `GROQ_API_KEY` (and optionally `GROQ_MODEL`) as environment variables on the host 
   never commit your real `.env` file.
2. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. That's it  one process serves both the site and the `/api/chat` endpoint, so there's no
   separate frontend deployment or CORS setup to manage.

## Notes

- There's a small in memory rate limit (12 questions/minute per browser tab) on `/api/chat` so
  a single visitor can't burn through the free API quota by accident. It resets if the server
  restarts  fine for a personal portfolio, swap for Redis backed limiting if traffic grows.
- The chat only ever sees `resume_data.py`'s facts plus the last few turns of the conversation
  it has no access to email, phone, or anything not explicitly listed there.
- Grok's exact model names change over time; if `llama-3.3-70b-versatile` stops working, check
  **https://console.groq.com/dashboard/metrics** for current model names and swap `GROQ_MODEL` in `.env`.
