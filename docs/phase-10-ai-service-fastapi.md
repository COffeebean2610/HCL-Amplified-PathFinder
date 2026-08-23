# Phase 10 — AI Service / FastAPI

## RouteMaster — AI Intelligence Service & SDE Integration Layer

---

## 1. Objective

RouteMaster's AI/ML intelligence (Phases 1–9) was developed as a collection of Python engines callable directly. Phase 10 wraps this intelligence in a **production-ready FastAPI AI service** that can be independently deployed and consumed by the SDE backend (Member 2) over REST + JSON.

This creates a clean separation:

```
React Frontend (Member 3)
        ↓
SDE Backend (Member 2) ← JWT auth, user management, CRUD
        ↓  HTTP POST
AI Service (Member 1) ← FastAPI, port 8001
        ↓
Phase 1–9 AI Engines
        ↓
data/processed/ + model/
```

---

## 2. Existing Problem Being Solved

Before Phase 10, the only existing web layer was a **Flask `app.py`** serving:
- A server-side rendered HTML UI (for demo purposes)
- 3 basic JSON routes with limited structure

Problems:
- No Pydantic validation
- AI engines called inline inside routes
- No service separation
- No structured error handling
- Not independently deployable

Phase 10 creates a purpose-built FastAPI service that addresses all of these.

---

## 3. Architecture

### Service Topology

```
                    RouteMaster
                         │
              ┌──────────┴──────────┐
              │                     │
        SDE Backend            AI Service
        Member 2              Member 1
        (port 5000)           (port 8001)
              │                     │
              │              ┌──────┴──────┐
              │              │             │
              │          Recommendation   ML
              │              Engine      Services
              │              │             │
              │          Career/Gaps    Embeddings
              │          Courses        Vector Search
              │          Projects       Skill Graph
              │          Roadmap
              │              │
              └──── REST + JSON ────────┘
                         │
                    Frontend
                    Member 3
```

### Startup Sequence

```
uvicorn starts
     ↓
FastAPI lifespan event
     ↓
Load Phase 3: CareerRecommender
     ↓
Load Phase 4: SkillGapEngine
     ↓
Load Phase 7: HybridRecommender (loads embeddings + BAAI/bge-small-en-v1.5)
     ↓
Load Phase 8: ProjectRecommender
     ↓
Load Phase 9: RoadmapGenerator
     ↓
Wire 5 service wrappers + 1 orchestration service → app.state
     ↓
Service ready to handle requests
```

---

## 4. Phase 1–9 Integration

| Phase | Component | Consumed By |
|-------|-----------|-------------|
| Phase 1 | AI Knowledge Base (skills, careers, courses) | All phases |
| Phase 2 | Skill Dependency Graph | Gap Engine, Roadmap, Hybrid |
| Phase 3 | CareerRecommender | `CareerService` → `/ai/recommend-career` |
| Phase 4 | SkillGapEngine | `SkillGapService` → `/ai/skill-gap` |
| Phase 5 | Sentence Transformer Embeddings | Loaded by HybridRecommender |
| Phase 6 | Vector Search (RouteMasterVectorSearch) | Used inside HybridRecommender |
| Phase 7 | HybridRecommender | `CourseService` → `/ai/recommend-courses` |
| Phase 8 | ProjectRecommender | `ProjectService` → `/ai/recommend-projects` |
| Phase 9 | RoadmapGenerator | `RoadmapService` → `/ai/generate-roadmap` |

---

## 5. Project Structure

```
ai-service/
├── app/
│   ├── main.py                      ← FastAPI app + lifespan + CORS + middleware
│   ├── api/
│   │   └── routes/
│   │       ├── health.py            ← GET /health, GET /ready
│   │       ├── career.py            ← POST /ai/recommend-career
│   │       ├── skill_gap.py         ← POST /ai/skill-gap
│   │       ├── courses.py           ← POST /ai/recommend-courses
│   │       ├── projects.py          ← POST /ai/recommend-projects
│   │       ├── roadmap.py           ← POST /ai/generate-roadmap
│   │       └── recommendation.py   ← POST /ai/recommend
│   ├── schemas/
│   │   ├── common.py               ← Error, Warning, Health models
│   │   ├── career.py               ← CareerRequest / CareerResponse
│   │   ├── skill_gap.py            ← SkillGapRequest / SkillGapResponse
│   │   ├── course.py               ← CourseRequest / CourseResponse
│   │   ├── project.py              ← ProjectRequest / ProjectResponse
│   │   ├── roadmap.py              ← RoadmapRequest / RoadmapResponse
│   │   └── recommendation.py      ← RecommendationRequest / RecommendationResponse
│   ├── services/
│   │   ├── career_service.py       ← Wraps CareerRecommender
│   │   ├── skill_gap_service.py    ← Wraps SkillGapEngine
│   │   ├── course_service.py       ← Wraps HybridRecommender
│   │   ├── project_service.py      ← Wraps ProjectRecommender
│   │   ├── roadmap_service.py      ← Wraps RoadmapGenerator
│   │   └── recommendation_service.py ← Orchestrates all 5 services
│   ├── core/
│   │   ├── config.py               ← pydantic-settings Settings class
│   │   ├── exceptions.py           ← Custom exceptions + HTTP handlers
│   │   └── logging.py              ← Structured request/response logging
│   └── dependencies/
│       └── services.py             ← FastAPI Depends() injectors
├── tests/
│   ├── conftest.py                 ← Session-scoped TestClient
│   └── test_ai_service.py          ← 34 tests
├── .env.example
├── requirements-ai-service.txt
└── README.md
```

---

## 6. FastAPI Architecture

### Why FastAPI

| Concern | FastAPI | Flask | Django REST |
|---------|---------|-------|-------------|
| Async support | ✓ Native | ✗ Requires ext | ✓ |
| Pydantic validation | ✓ Built-in | ✗ Manual | ✓ Serializers |
| OpenAPI generation | ✓ Automatic | ✗ Extensions | ✓ Partial |
| Type hints | ✓ First-class | ✗ Optional | ✗ Optional |
| Performance | Excellent | Good | Good |
| Startup/init control | ✓ Lifespan | ✗ Manual | ✓ AppConfig |

FastAPI was chosen for automatic OpenAPI docs, Pydantic v2 validation without extra libraries, and the lifespan hook for clean engine initialization.

### Route Design

Routes are thin (≤15 lines) — they only handle HTTP concerns:
```python
@router.post("/recommend-career", response_model=CareerResponse)
async def recommend_career(request: CareerRequest, svc = Depends(get_career_service)):
    return svc.recommend(request)
```

All AI logic lives in the service layer.

---

## 7–11. Endpoint Implementations

### `/ai/recommend-career` (Phase 3)
- Calls `CareerRecommender.recommend(interests, current_skills, top_k)`
- Translates raw dict output to `CareerRecommendationItem` Pydantic models
- Returns ranked list with `match_score` (0–100), matched/missing skills, and explanation

### `/ai/skill-gap` (Phase 4)
- Calls `SkillGapEngine.calculate_gap(SkillGapRequest)`
- Maps `SkillGapResponse` Pydantic model from engine to API schema
- Returns `readiness_score`, `missing_skills`, `prerequisite_gaps`, and topological `learning_sequence`

### `/ai/recommend-courses` (Phase 7)
- Calls `HybridRecommender.recommend(RecommendationRequest)`
- Passes `completed_courses` for filtering — the engine excludes them
- Returns `relevance_score` (0–1.0) reflecting weighted hybrid score

### `/ai/recommend-projects` (Phase 8)
- Calls `ProjectRecommender.recommend(ProjectRecommendationRequest)`
- Skill gaps derived internally from `target_role` — client only needs to provide `skills` + `target_role`
- Returns `skills_to_develop` — career gap skills the project teaches

### `/ai/generate-roadmap` (Phase 9)
- Calls `RoadmapGenerator.generate_roadmap(RoadmapRequest)`
- Returns React Flow–compatible `nodes[]` + `edges[]`
- Node statuses: `completed` → `next` → `locked`
- Cycle warnings in `warnings[]` without crashing

---

## 12. `/ai/recommend` — Complete Orchestration

```
Student Profile
     │
     ▼
Career (Phase 3)  ← from target_role or auto-selected
     │
     ▼
Skill Gap (Phase 4)  ← computed ONCE, shared below
     │
     ├──→ Courses (Phase 7)
     ├──→ Projects (Phase 8)
     └──→ Roadmap (Phase 9)
     │
     ▼
Unified JSON Response
```

Key design decisions:
- **Skill gap computed once** and passed downstream — no duplicate engine calls
- **Partial failure**: if Projects fail, Career/Gap/Courses/Roadmap still returned with `status: "partial"`
- **Performance logged**: each component's latency measured and logged at INFO level

---

## 13–14. Request/Response Schemas

All schemas use **Pydantic v2** with:
- Field-level descriptions used by OpenAPI
- `field_validator` for business rules (e.g., difficulty whitelist)
- Optional fields with sensible defaults

Score ranges documented explicitly in field descriptions.

---

## 15. Error Handling

Custom exception hierarchy:
```
AIServiceError (base)
├── CareerNotFoundError   → HTTP 404
├── SkillNotFoundError    → HTTP 404
├── RecommendationEngineError → HTTP 500
├── SkillGapEngineError   → HTTP 500
├── RoadmapGenerationError → HTTP 500
├── VectorSearchError     → HTTP 503
└── DatabaseError         → HTTP 503
```

All errors return:
```json
{"error": {"code": "CAREER_NOT_FOUND", "message": "..."}}
```

Python tracebacks are never exposed.

---

## 16. Validation

Pydantic v2 handles:
- Type checking and coercion
- `ge`/`le` constraints (e.g., `number_of_results: int = Field(default=5, ge=1, le=50)`)
- Custom validators for difficulty whitelist
- `422 Unprocessable Entity` on any violation

---

## 17. Model Loading

**The Sentence Transformer model (`BAAI/bge-small-en-v1.5`) is loaded ONCE** during FastAPI's lifespan startup event when `HybridRecommender.__init__()` is called. It is stored in `app.state.course_service.recommender` (a singleton).

Every subsequent request reuses the already-loaded model — no per-request model loading.

---

## 18. Database Connection

MongoDB connection is managed by `pymongo.MongoClient` inside the engine constructors. The engines are singletons in `app.state`, so there is one connection pool shared across all requests.

---

## 19. Vector Search

`RouteMasterVectorSearch` (Phase 6) is instantiated once inside `HybridRecommender.__init__()`. The embedding index is loaded into memory at startup and reused for all semantic similarity queries.

---

## 20. Performance

Startup time: ~30–60 seconds (sentence transformer + embedding index loading).

Per-request latency (approximate, measured at development time):

| Component | Latency |
|-----------|---------|
| Career | ~100–200ms |
| Skill Gap | ~30–80ms |
| Courses | ~200–500ms |
| Projects | ~200–400ms |
| Roadmap | ~300–600ms |
| **Total `/ai/recommend`** | **~800–1800ms** |

The dominant cost is the hybrid course recommender (semantic embedding search).

---

## 21. Testing

**Test suite**: `ai-service/tests/test_ai_service.py`

**34 tests** covering:
- Health checks (4)
- Career recommendation (4)
- Skill gap (5)
- Course recommendation (6)
- Project recommendation (4)
- Roadmap generation (4)
- Unified recommendation (5)
- Cross-endpoint consistency (1)
- Completed course filtering (1)

Run:
```bash
cd ai-service
python -m pytest tests/test_ai_service.py -v
```

---

## 22. Security

### CORS
Configured via `ALLOWED_ORIGINS` env var. In production, set to the SDE backend URL only:
```
ALLOWED_ORIGINS=https://api.routemaster.example.com
```
Do NOT use `*` in production.

### Secrets
Never committed. Use `.env` locally; use Render/Railway secret management in production.

### Service Boundary
The AI service exposes only AI endpoints. No raw MongoDB queries, no embedding vectors, no debug endpoints.

### Authentication
The SDE backend authenticates users via JWT. The AI service trusts calls from the SDE backend (internal network). In production, implement one of:
- Internal VPC network restriction
- Shared API key header (`X-API-Key`)
- mTLS

---

## 23. Deployment

### Render / Railway

**Procfile**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Start directory**: `ai-service/`

**Environment variables**: Set all from `.env.example` in the Render/Railway dashboard.

**Build command**:
```bash
pip install -r requirements-ai-service.txt
```

**Note**: First startup takes 30–60s due to sentence transformer loading. Configure health check timeout accordingly (≥120s).

### Development

```bash
cd ai-service
uvicorn app.main:app --reload --port 8001
```

---

## 24. SDE Handoff

Member 2's backend should set:
```
AI_SERVICE_URL=http://localhost:8001   # dev
AI_SERVICE_URL=https://ai.routemaster.example.com  # prod
```

Then call:
```python
import requests, os

AI_URL = os.getenv("AI_SERVICE_URL")

def get_recommendation(profile):
    return requests.post(f"{AI_URL}/ai/recommend", json=profile, timeout=60).json()
```

Full examples in `docs/ai-api.md`.

---

## 25. Frontend Handoff

Member 3 receives AI data **through Member 2's backend** — they do NOT call the AI service directly. The roadmap `nodes[]` and `edges[]` in `/ai/recommend` or `/ai/generate-roadmap` are React Flow–compatible and can be used directly with `<ReactFlow nodes={...} edges={...} />`.

---

## 26. Limitations

- **Cold start**: ~30–60s on first startup due to sentence transformer loading
- **Single-career**: `/ai/recommend` supports one `target_role` at a time; multi-career is architecturally feasible but not implemented
- **No caching**: Results are not cached between requests; same input recomputes
- **MongoDB optional**: The AI service uses local file-based data (`data/processed/`); MongoDB integration is configured but not required for core functionality
- **No rate limiting**: Should be added before public production deployment

---

## 27. Future Improvements

- API versioning (`/api/v1/ai/...`)
- Response caching (Redis)
- Async inference for concurrent pipeline execution
- Multi-career roadmap orchestration
- Background processing with task queues (Celery/Dramatiq)
- Model optimization (ONNX quantization)
- Observability (OpenTelemetry traces)
- Service-to-service auth (mTLS or API keys)
- Rate limiting middleware
- Model hot-reload without restart

---

## 28. Deliverables Checklist

- [x] FastAPI AI service (`ai-service/app/main.py`)
- [x] Modular route structure (`app/api/routes/`)
- [x] Service layer (`app/services/`)
- [x] Pydantic request schemas (6 schemas)
- [x] Pydantic response schemas (6 schemas)
- [x] GET /health
- [x] GET /ready
- [x] POST /ai/recommend-career
- [x] POST /ai/skill-gap
- [x] POST /ai/recommend-courses
- [x] POST /ai/recommend-projects
- [x] POST /ai/generate-roadmap
- [x] POST /ai/recommend (orchestration)
- [x] Unified orchestration (RecommendationService)
- [x] Skill normalization integration (via engine)
- [x] Completed course filtering integration
- [x] Project recommendation integration
- [x] Roadmap integration (React Flow compatible)
- [x] Engine singleton lifecycle management (lifespan)
- [x] Environment configuration (pydantic-settings)
- [x] CORS configuration
- [x] Structured error handling
- [x] Request/response logging with X-Request-ID
- [x] Pydantic validation (HTTP 422 on violation)
- [x] OpenAPI documentation (/docs, /redoc)
- [x] Unit + integration tests (34 tests)
- [x] Cross-endpoint consistency test
- [x] Partial failure handling (warnings[])
- [x] Deployment configuration (Procfile + README)
- [x] API documentation (`docs/ai-api.md`)
- [x] SDE integration examples
- [x] Phase documentation (this file)
