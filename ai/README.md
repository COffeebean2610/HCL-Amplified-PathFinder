# RouteMaster AI Service

**Phase 10 — FastAPI AI Service**

Independent REST API service exposing all RouteMaster AI/ML intelligence (Phases 1–9) for consumption by the SDE backend (Member 2).

---

## Architecture

```
SDE Backend (Member 2)
       ↓  HTTP POST
FastAPI AI Service (Port 8001)
       ↓
Service Layer
       ↓
Phase 1-9 AI Engines
       ↓
data/processed/ + model/
```

---

## Quick Start

```bash
# From the repo root
cd ai-service

# Install dependencies
pip install -r requirements-ai-service.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start development server
uvicorn app.main:app --reload --port 8001

# Production
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/ready` | Readiness check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |
| `POST` | `/ai/recommend-career` | Career recommendations (Phase 3) |
| `POST` | `/ai/skill-gap` | Skill gap analysis (Phase 4) |
| `POST` | `/ai/recommend-courses` | Course recommendations (Phase 7) |
| `POST` | `/ai/recommend-projects` | Project recommendations (Phase 8) |
| `POST` | `/ai/generate-roadmap` | Personalized roadmap (Phase 9) |
| `POST` | `/ai/recommend` | **Complete AI pipeline** (all phases) |

---

## SDE Integration (Member 2)

```python
import requests

AI_SERVICE_URL = "http://localhost:8001"  # or your deployed URL

# Full pipeline — recommended for most use cases
response = requests.post(
    f"{AI_SERVICE_URL}/ai/recommend",
    json={
        "skills": ["Python", "SQL", "Git"],
        "interests": "Artificial Intelligence",
        "target_role": "AI Engineer",
        "difficulty": "Intermediate",
        "number_of_results": 5,
    }
)
data = response.json()
# data["career"]    → matched career
# data["skill_gap"] → missing skills
# data["courses"]   → top-5 courses
# data["projects"]  → top-5 projects
# data["roadmap"]   → React Flow nodes + edges
```

---

## Score Conventions

| Field | Range | Description |
|-------|-------|-------------|
| `match_score` | 0–100 | Career-profile fit (%) |
| `readiness_score` | 0–100 | Career readiness (%) |
| `technical_match_score` | 0–100 | Technical skill coverage (%) |
| `relevance_score` | 0–1.0 | Item composite score (normalized) |
| `final_score` | 0–1.0 | Engine composite score |

---

## Environment Variables

See `.env.example` for all configuration options.

**Never commit `.env` to version control.**

---

## Testing

```bash
# From repo root
cd ai-service
python -m pytest tests/test_ai_service.py -v
```

---

## Directory Structure

```
ai-service/
├── app/
│   ├── main.py              ← FastAPI entry point + lifespan
│   ├── api/routes/          ← Thin route handlers
│   ├── schemas/             ← Pydantic request/response models
│   ├── services/            ← Engine wrappers + orchestration
│   ├── core/                ← Config, logging, exceptions
│   └── dependencies/        ← FastAPI Depends() injectors
├── tests/
│   ├── conftest.py          ← Session-scoped TestClient
│   └── test_ai_service.py   ← Full test suite
├── .env.example
├── requirements-ai-service.txt
└── README.md
```

---

## Security Notes

- CORS origins configured via `ALLOWED_ORIGINS` env var — restrict to SDE backend in production
- No raw embeddings, MongoDB credentials, or stack traces exposed in API responses
- Service-to-service authentication: restrict AI service to internal network or use API key header in production
