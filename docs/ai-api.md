# RouteMaster AI API — SDE Integration Reference

**Version**: 1.0.0  
**Base URL (dev)**: `http://localhost:8001`  
**Base URL (prod)**: Set via `AI_SERVICE_URL` environment variable in SDE backend

---

## Authentication

In development: no auth required.  
In production: Restrict the AI service to the internal network only or implement an API key header:
```
X-API-Key: <service-token>
```
The AI service does **not** validate JWT tokens — that responsibility belongs to the SDE backend.

---

## Score Conventions

| Field | Range | Description |
|-------|-------|-------------|
| `match_score` | 0–100 | Career-profile fit percentage |
| `readiness_score` | 0–100 | Career readiness percentage |
| `technical_match_score` | 0–100 | Technical skills coverage percentage |
| `relevance_score` | 0–1.0 | Composite item relevance (normalized) |

---

## Endpoints

---

### GET /health

**Purpose**: Liveness check — verify the service is running.

**Request**: None

**Response 200**:
```json
{
  "status": "healthy",
  "service": "routemaster-ai",
  "version": "1.0.0",
  "environment": "development"
}
```

---

### GET /ready

**Purpose**: Readiness check — verify engines are loaded.

**Response 200**:
```json
{
  "status": "ready",
  "checks": {
    "engines": "ok",
    "data": "ok"
  }
}
```

---

### POST /ai/recommend-career

**Purpose**: Recommend careers matching the student's skills and interests.

**Request Body**:
```json
{
  "skills": ["Python", "SQL", "Git"],
  "interests": "Artificial Intelligence, Machine Learning",
  "top_k": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skills` | string[] | No | Current learner skills |
| `interests` | string \| string[] | No | Free-text or list of interests |
| `top_k` | integer 1–20 | No (default: 5) | Number of careers to return |

**Response 200**:
```json
{
  "recommendations": [
    {
      "career_id": "CA_042",
      "career_title": "AI Engineer",
      "career_domain": "Artificial Intelligence",
      "match_score": 72.5,
      "technical_match_score": 68.0,
      "matched_skills": ["Python"],
      "missing_skills": [
        { "skill_id": "SK_00264", "skill_name": "Machine Learning", "importance": "Critical" }
      ],
      "reason": "Strong alignment with AI interests. Python is a core skill match."
    }
  ],
  "total": 5
}
```

**Error Responses**:
- `422` — Validation error (e.g., `top_k: 0`)

---

### POST /ai/skill-gap

**Purpose**: Calculate the skill gap between a learner's current skills and a target career.

**Request Body**:
```json
{
  "skills": ["Python", "SQL", "Git"],
  "target_role": "AI Engineer"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skills` | string[] | No | Current learner skills |
| `target_role` | string | **Yes** | Career title or canonical ID |

**Response 200**:
```json
{
  "career": {
    "career_id": "CA_042",
    "career_title": "AI Engineer",
    "career_domain": "Artificial Intelligence"
  },
  "readiness_score": 22.5,
  "technical_match_pct": 18.0,
  "current_skills": ["Python", "SQL", "Git"],
  "matched_skills": ["Python"],
  "missing_skills": [
    {
      "skill_id": "SK_00264",
      "skill_name": "Machine Learning",
      "skill_category": "AI",
      "priority": "Critical"
    }
  ],
  "prerequisite_gaps": [
    {
      "skill_id": "SK_00360",
      "skill_name": "Python",
      "required_by_skill_id": "SK_00264",
      "required_by_skill_name": "Machine Learning",
      "reason": "Machine Learning requires Python as a prerequisite."
    }
  ],
  "learning_sequence": [
    {
      "sequence_number": 1,
      "skill_id": "SK_00264",
      "skill_name": "Machine Learning",
      "skill_type": "technical",
      "priority": "Critical",
      "reason": "Core career requirement.",
      "prerequisites": ["SK_00360"]
    }
  ]
}
```

**Error Responses**:
- `404` — Career not found
- `422` — `target_role` missing

---

### POST /ai/recommend-courses

**Purpose**: Recommend courses using the hybrid engine (Phase 7).

**Request Body**:
```json
{
  "skills": ["Python", "SQL"],
  "interests": "Artificial Intelligence",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "number_of_results": 5
}
```

| Field | Type | Required | Valid Values |
|-------|------|----------|-------------|
| `skills` | string[] | No | Any skills |
| `interests` | string \| string[] | No | Free text |
| `target_role` | string | **Yes** | Career title/ID |
| `difficulty` | string | No (default: Any Level) | `Any Level`, `Beginner`, `Intermediate`, `Advanced`, `Conversant`, `Not Calibrated` |
| `completed_courses` | string[] | No | Course names to exclude |
| `number_of_results` | integer 1–50 | No (default: 5) | Result limit |

**Response 200**:
```json
{
  "target_role": "AI Engineer",
  "courses": [
    {
      "course_id": "C001",
      "course_name": "Machine Learning Specialization",
      "organization": "DeepLearning.AI",
      "difficulty": "Intermediate",
      "rating": 4.9,
      "url": "https://coursera.org/...",
      "relevance_score": 0.91,
      "matched_skills": ["Python"],
      "missing_skills_covered": ["Machine Learning", "Scikit-learn"],
      "prerequisite_status": "Ready",
      "reason": "Covers 3 critical missing skills for AI Engineer."
    }
  ],
  "total": 5
}
```

**Error Responses**:
- `422` — Invalid difficulty or missing `target_role`

---

### POST /ai/recommend-projects

**Purpose**: Recommend engineering projects that develop skill gaps (Phase 8).

**Request Body**:
```json
{
  "skills": ["Python", "SQL"],
  "interests": "Machine Learning",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "number_of_results": 5
}
```

> **Note**: Skill gaps are derived automatically from `target_role`. You do NOT need to supply them manually.

**Response 200**:
```json
{
  "target_role": "AI Engineer",
  "projects": [
    {
      "project_id": "PROJ_042",
      "project_name": "Predictive Maintenance System",
      "domain": "Machine Learning",
      "difficulty": "Intermediate",
      "github_url": "https://github.com/...",
      "relevance_score": 0.87,
      "skills_to_develop": ["Machine Learning", "Pandas", "Scikit-learn"],
      "matched_existing_skills": ["Python"],
      "prerequisite_status": "Ready",
      "reason": "Develops 3 gap skills while leveraging existing Python knowledge."
    }
  ],
  "total": 5
}
```

---

### POST /ai/generate-roadmap

**Purpose**: Generate a personalized React Flow–compatible learning roadmap (Phase 9).

**Request Body**:
```json
{
  "skills": ["Python", "SQL", "Git"],
  "interests": "Generative AI",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "courses_per_skill": 3,
  "projects_per_skill": 2
}
```

**Response 200** (React Flow compatible):
```json
{
  "career": {
    "career_id": "CA_042",
    "career_title": "AI Engineer"
  },
  "summary": {
    "total_required_skills": 18,
    "completed_skills": 2,
    "remaining_skills": 16,
    "progress_percentage": 11.1,
    "critical_skills_remaining": 5,
    "career_readiness_score": 14.3
  },
  "nodes": [
    {
      "id": "skill-SK_00264",
      "skill_id": "SK_00264",
      "skill_name": "Machine Learning",
      "status": "next",
      "priority": "Critical",
      "sequence": 3,
      "prerequisites": ["skill-SK_00360"],
      "courses": [...],
      "projects": [...],
      "data": {
        "label": "Machine Learning",
        "status": "next",
        "priority": "Critical",
        "reason": "Core skill required for AI Engineer.",
        "learning_action": "learn_and_practice"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-SK_00360-SK_00264",
      "source": "skill-SK_00360",
      "target": "skill-SK_00264",
      "relationship": "prerequisite"
    }
  ],
  "warnings": []
}
```

**Node statuses**: `completed` · `next` · `locked`  
**Learning actions**: `learn_and_practice` · `learn_only` · `practice_only`

---

### POST /ai/recommend ⭐ Primary Endpoint

**Purpose**: Run the **complete AI pipeline** in a single request.

**Request Body**:
```json
{
  "skills": ["Python", "SQL", "Git"],
  "interests": "Artificial Intelligence, Generative AI",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "number_of_results": 5,
  "courses_per_skill": 3,
  "projects_per_skill": 2,
  "top_k_careers": 1
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skills` | string[] | No | Current skills |
| `interests` | string \| string[] | No | Interests |
| `target_role` | string | No | If omitted, auto-selected from top career |
| `difficulty` | string | No | Difficulty preference |
| `completed_courses` | string[] | No | Courses to exclude |
| `number_of_results` | int 1–50 | No | Courses + projects count |
| `courses_per_skill` | int 0–10 | No | Roadmap courses per skill node |
| `projects_per_skill` | int 0–10 | No | Roadmap projects per skill node |
| `top_k_careers` | int 1–10 | No | Careers considered if no target_role |

**Response 200**:
```json
{
  "status": "success",
  "profile": {
    "skills": ["Python", "SQL", "Git"],
    "interests": "Artificial Intelligence, Generative AI"
  },
  "career": {
    "career_id": "CA_042",
    "career_title": "AI Engineer",
    "match_score": 72.5,
    "reason": "..."
  },
  "skill_gap": {
    "current_skills": ["Python", "SQL", "Git"],
    "matched_skills": ["Python"],
    "missing_skills": [...],
    "readiness_score": 22.5
  },
  "courses": [...],
  "projects": [...],
  "roadmap": {
    "career": {...},
    "summary": {...},
    "nodes": [...],
    "edges": [...]
  },
  "warnings": []
}
```

**Partial failure** (when a component fails):
```json
{
  "status": "partial",
  "warnings": [
    {
      "component": "projects",
      "code": "PROJECT_RECOMMENDATION_FAILED",
      "message": "Project recommendation engine unavailable."
    }
  ],
  ...
}
```

---

## Error Response Format

All errors use this consistent format:
```json
{
  "error": {
    "code": "CAREER_NOT_FOUND",
    "message": "Target career 'XYZ' could not be found in the knowledge base."
  }
}
```

| Code | HTTP Status |
|------|------------|
| `CAREER_NOT_FOUND` | 404 |
| `SKILL_NOT_FOUND` | 404 |
| `RECOMMENDATION_ENGINE_ERROR` | 500 |
| `SKILL_GAP_ENGINE_ERROR` | 500 |
| `ROADMAP_GENERATION_ERROR` | 500 |
| `VECTOR_SEARCH_ERROR` | 503 |
| `DATABASE_ERROR` | 503 |
| `INTERNAL_SERVER_ERROR` | 500 |

Validation errors return `422` with FastAPI's standard Pydantic error format.

---

## Python Integration Example (Member 2)

```python
import os
import requests

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

def get_full_recommendation(student_profile: dict) -> dict:
    """Call the RouteMaster AI service for a complete recommendation."""
    response = requests.post(
        f"{AI_SERVICE_URL}/ai/recommend",
        json=student_profile,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

def get_career_recommendations(skills: list, interests: str, top_k: int = 5) -> dict:
    response = requests.post(
        f"{AI_SERVICE_URL}/ai/recommend-career",
        json={"skills": skills, "interests": interests, "top_k": top_k},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

def get_skill_gap(skills: list, target_role: str) -> dict:
    response = requests.post(
        f"{AI_SERVICE_URL}/ai/skill-gap",
        json={"skills": skills, "target_role": target_role},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

---

## Response Headers

Every response includes:
```
X-Request-ID: <8-char UUID>
X-Process-Time-Ms: <milliseconds>
```

Use `X-Request-ID` for logging and support correlation.
