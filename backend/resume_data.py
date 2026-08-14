"""
All of Gyana's portfolio facts live here, as structured data — not prose.
The chat agent turns this into natural, first-person answers at request time,
so nothing the bot says is a copy-pasted resume line.

To update the portfolio (new job, new project, new skill), edit this file only.
Nothing else needs to change.
"""

PROFILE = {
    "name": "Gyana Sinha",
    "title": "Software Developer",
    "location": "India",
    "email": "sinhagyana31@gmail.com",
    "phone": "7903598175",
    "linkedin": "https://linkedin.com/in/gyana-sinha",  # update with real handle
    "summary": (
        "Software Developer with 3+ years building production LLM and machine learning "
        "systems — Retrieval-Augmented Generation (RAG) pipelines, autonomous AI agents, "
        "and OCR-driven document intelligence platforms — on Python and Django. Strong "
        "foundation in scalable API design, asynchronous processing, database optimization, "
        "and AWS cloud architecture. Has shipped AI features from prototype to production, "
        "including agentic task-planning systems, LLM-based document extraction, and "
        "computer-vision identity verification."
    ),
}

SKILLS = {
    "AI / ML Engineering": [
        "RAG pipeline design", "LLM integration (OpenAI APIs)", "LangChain",
        "prompt engineering", "agentic workflows & task planning",
        "OCR-based extraction", "embeddings & semantic search",
        "computer vision (face matching / ID verification)",
    ],
    "Languages & Backend": [
        "Python", "Django", "Django REST Framework (DRF)", "FastAPI",
        "REST API design", "Scikit-learn", "TensorFlow",
    ],
    "Data & Infra": ["PostgreSQL", "MySQL", "Celery", "Redis", "AWS (S3, Lambda, Bedrock)"],
    "Engineering Practices": [
        "SDLC", "system design", "performance optimization", "root cause analysis",
        "code review", "Git/GitHub", "documentation",
    ],
}

EXPERIENCE = [
    {
        "company": "GMoney Pvt. Ltd.",
        "role": "Software Developer",
        "period": "Sept 2024 - Present",
        "highlights": [
            "Built AI-powered document processing pipelines (OCR, OpenAI APIs, LangChain, RAG) "
            "that automated structured-data extraction from medical and insurance documents, "
            "cutting manual review effort and accelerating claim turnaround.",
            "Designed and shipped a Video KYC identity-verification pipeline using AI-based "
            "face extraction and Aadhaar image matching, replacing manual identity checks in "
            "the loan onboarding flow.",
            "Built a CIBIL evaluation module that automated loan eligibility assessment and "
            "credit limit calculation, reducing manual underwriting steps.",
            "Developed secure RESTful APIs for insurance claim management, policy validation, "
            "eligibility verification, and approval workflows, following full SDLC practices.",
            "Optimized PostgreSQL queries and API response times through indexing, query "
            "tuning, and caching, measurably improving application performance under load.",
            "Implemented asynchronous background processing (Celery, Redis) for claim "
            "validation, notifications, and workflow automation, improving throughput and "
            "reliability.",
            "Investigated production issues end-to-end (root cause analysis, defect fixes, "
            "monitoring) to maintain high application availability.",
            "Built a Sales Management System (lead management, onboarding, target allocation, "
            "approvals, reporting dashboards) and internal Task/Asset Management tools with "
            "SLA tracking and automated reminders.",
            "Integrated AWS S3 for secure document storage/retrieval and improved Django Admin "
            "usability via custom filters and query optimization.",
        ],
    },
    {
        "company": "Euspace Technologies",
        "role": "Trainee Software Developer",
        "period": "Mar 2023 - June 2024",
        "highlights": [
            "Developed backend modules in Python/Django for multiple business applications "
            "and built REST APIs for frontend and third-party integration.",
            "Designed and maintained relational database structures in MySQL; contributed to "
            "debugging, testing, and performance optimization.",
            "Collaborated with senior developers across the full SDLC and supported technical "
            "documentation and deployment.",
        ],
    },
]

PROJECTS = [
    {
        "name": "Autonomous AI Agent for Business Document Generation",
        "stack": "Python, FastAPI, python-docx",
        "highlights": [
            "Built an autonomous AI agent that interprets natural language business requests, "
            "generates its own execution plan (a TODO list), and completes multi-step tasks "
            "with minimal human intervention — an agentic workflow with planning, execution, "
            "and validation stages.",
            "Designed a modular architecture separating planning, execution, validation, and "
            "document-generation components for maintainability and scale.",
            "Auto-generated polished Word (.docx) documents from user requirements, and "
            "exposed the agent through REST APIs returning structured execution results.",
            "Engineered fallback and error-handling logic so the agent produces meaningful "
            "output even from ambiguous or incomplete requests.",
        ],
    },
    {
        "name": "AI-Powered Document Intelligence Platform",
        "stack": "Django, OpenAI APIs, LangChain, OCR, RAG, Celery, Redis, AWS S3",
        "highlights": [
            "Designed an end-to-end document processing platform for secure upload, "
            "validation, and structured data extraction.",
            "Built asynchronous processing pipelines (Celery, Redis) to handle high document "
            "volumes without blocking user-facing requests.",
            "Integrated AWS S3 for storage and added validation, exception handling, and "
            "logging to reduce response latency and improve reliability in production.",
        ],
    },
]

EDUCATION = [
    {"degree": "B.Tech in Information Technology", "school": "K.J. Somaiya College of Engineering", "year": "2024", "detail": "80.00%"},
    {"degree": "Diploma in Computer Technology", "school": "Sou. Venutai Chavan Polytechnic", "year": "2021", "detail": "91.89%"},
    {"degree": "SSC", "school": "B.D. Public School", "year": None, "detail": "86.06%"},
]


def _bullets(items):
    return "\n".join(f"  - {i}" for i in items)


def build_system_prompt() -> str:
    """Turn the structured facts above into one system prompt for the chat agent."""

    skills_block = "\n".join(
        f"- {category}: {', '.join(items)}" for category, items in SKILLS.items()
    )

    experience_block = "\n\n".join(
        f"{job['role']} at {job['company']} ({job['period']})\n{_bullets(job['highlights'])}"
        for job in EXPERIENCE
    )

    projects_block = "\n\n".join(
        f"{p['name']} — stack: {p['stack']}\n{_bullets(p['highlights'])}"
        for p in PROJECTS
    )

    education_block = "\n".join(
        f"- {e['degree']}, {e['school']}"
        + (f" ({e['year']})" if e["year"] else "")
        + (f" — {e['detail']}" if e["detail"] else "")
        for e in EDUCATION
    )

    return f"""You are the personal portfolio assistant for {PROFILE['name']}, a {PROFILE['title']}.
You speak ABOUT Gyana in the third person, as a knowledgeable colleague introducing her to a
visitor on her portfolio site — never pretend to literally be Gyana, and never invent facts
that aren't given to you below.

CONTACT
Email: {PROFILE['email']} | Phone: {PROFILE['phone']} | LinkedIn: {PROFILE['linkedin']}

SUMMARY
{PROFILE['summary']}

SKILLS
{skills_block}

WORK EXPERIENCE
{experience_block}

PROJECTS
{projects_block}

EDUCATION
{education_block}

HOW TO ANSWER
- Ground every answer in the facts above. Never make up employers, dates, numbers, or skills.
- Do NOT recite this data as a list or copy resume phrasing verbatim. Rewrite it conversationally,
  in your own words, the way you'd explain it out loud to someone who just asked.
- Keep answers tight: 2-5 sentences for most questions. Expand only if the visitor asks for detail
  ("tell me more about...", "walk me through...").
- If asked something not covered by the facts above (salary, personal life, opinions on other
  people, unrelated trivia), say plainly that it's not something you can speak to, and offer to
  connect the visitor with Gyana directly via email or LinkedIn instead of guessing.
- If asked who's the best fit for a role, or why Gyana would be a good hire, connect her actual
  experience (RAG, agentic AI, OCR document intelligence, Django/FastAPI backends) to the ask.
- Keep a warm, confident, professional tone. No excessive enthusiasm, no emojis, no filler.
"""
