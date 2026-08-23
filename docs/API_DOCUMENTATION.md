# RouteMaster AI Engine — API Documentation & Contract Specification

**Service**: RouteMaster AI Service  
**Framework**: FastAPI (Python 3.10+)  
**Version**: `1.0.0`  
**Base URL (Development)**: `http://localhost:8001`  
**Base URL (Production)**: Injected via `AI_SERVICE_URL` environment variable  
**OpenAPI Specification**: [`docs/openapi.json`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/openapi.json) / Interactive Swagger at `/docs`

---

# Table of Contents
1. [Global Architecture & Conventions](#global-architecture--conventions)
2. [Canonical Student Profile Schema](#canonical-student-profile-schema)
3. [Score Standardization & Semantics](#score-standardization--semantics)
4. [Standard Enums & Allowed Values](#standard-enums--allowed-values)
5. [Standardized Error Contract](#standardized-error-contract)
6. [Endpoint 1: Career Recommendation (`POST /ai/recommend-career`)](#1-career-recommendation)
7. [Endpoint 2: Skill Gap Analysis (`POST /ai/skill-gap`)](#2-skill-gap-analysis)
8. [Endpoint 3: Course Recommendation (`POST /ai/recommend-courses`)](#3-course-recommendation)
9. [Endpoint 4: Project Recommendation (`POST /ai/recommend-projects`)](#4-project-recommendation)
10. [Endpoint 5: Personalized Roadmap Generator (`POST /ai/generate-roadmap`)](#5-personalized-roadmap-generator)
11. [Endpoint 6: Unified Recommendation Pipeline (`POST /ai/recommend`)](#6-unified-recommendation-pipeline)
12. [Health & Readiness Probes](#health--readiness-probes)

---

# Global Architecture & Conventions

```
                    RouteMaster System Architecture
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
      Member 2: SDE Backend                 Member 1: AI Service
    (Port 5000 / Node/Express/Flask)          (Port 8001 / FastAPI)
              │                                     │
              │ ── HTTP POST /ai/recommend ────────►│
              │ ◄─ Standardized JSON Response ──────│
              │                                     ├── Service Layer
              ▼                                     ├── Phase 1-9 AI Engines
      Member 3: React Frontend                      └── Processed Knowledge Base & Embeddings
```

### Protocol & Content
- All AI endpoints use **HTTP POST** (except `/health` and `/ready` which use `GET`).
- Request and response bodies are strictly formatted as `application/json; charset=utf-8`.
- Response headers include:
  - `X-Request-ID`: Unique 8-character UUID for request tracing.
  - `X-Process-Time-Ms`: High-precision processing duration in milliseconds.

---

# Canonical Student Profile Schema

To simplify integration, all endpoints accept the canonical student profile structure or its subsets. Field aliases are supported gracefully so that frontend or backend naming variations are normalized seamlessly.

```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL", "Git"],
  "current_skills": ["Python", "SQL", "Git"],
  "interests": "Artificial Intelligence, Generative AI",
  "target_role": "AI Engineer",
  "target_career": "AI Engineer",
  "difficulty": "Intermediate",
  "preferred_difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "learning_preferences": {
    "hands_on_ratio": 0.7,
    "pacing": "self-paced"
  },
  "number_of_results": 5,
  "courses_per_skill": 3,
  "projects_per_skill": 2,
  "top_k": 5
}
```

### Field Alias Resolution Table

| Canonical Field | Supported Alias | Description |
|---|---|---|
| `skills` | `current_skills` | List of skills currently known or mastered by the student |
| `target_role` | `target_career` | Target career title (e.g. `"AI Engineer"`) or canonical ID (`"CA_042"`) |
| `difficulty` | `preferred_difficulty` | Preferred difficulty tier filter |

---

# Score Standardization & Semantics

RouteMaster standardizes all score representations across endpoints into two well-defined numerical scales:

| Score Metric | Numerical Range | Format | Description |
|---|---|---|---|
| `match_score` | `0.0` – `100.0` | Percentage (`float`) | Overall career-to-profile alignment score |
| `readiness_score` | `0.0` – `100.0` | Percentage (`float`) | Career readiness based on mastered vs missing required skills |
| `technical_match_score` | `0.0` – `100.0` | Percentage (`float`) | Direct required technical skill coverage percentage |
| `progress_percentage` | `0.0` – `100.0` | Percentage (`float`) | Milestone completion rate along the learning roadmap |
| `relevance_score` | `0.0` – `1.0` | Normalized (`float`) | Course and project composite ranking score |
| `final_score` | `0.0` – `1.0` | Normalized (`float`) | Engine-level multi-factor weighted match score |

---

# Standard Enums & Allowed Values

### Priority Tiers (`PriorityEnum`)
- `"Critical"`: Core foundational skill mandatory for the role; must be learned first.
- `"High"`: Essential domain competence strongly expected by employers.
- `"Medium"`: Supporting technical or workflow competency.
- `"Low"`: Specialized or optional elective skill.

### Difficulty Tiers (`DifficultyEnum`)
- `"Any Level"`: Include courses/projects across all difficulty tiers.
- `"Beginner"`: Introductory material suitable for novices.
- `"Intermediate"`: Applied engineering concepts requiring basic prerequisites.
- `"Advanced"`: Complex architectures, distributed systems, and cutting-edge topics.
- `"Conversant"` / `"Not Calibrated"`: Dataset legacy tiers (mapped safely).

### Roadmap Node Status (`NodeStatusEnum`)
- `"completed"`: Student has already mastered this skill (`user_skills`).
- `"next"`: All prerequisites are satisfied; unlocked and ready for active learning.
- `"locked"`: Predecessor prerequisite skills must be learned before unlocking this node.

### Learning Action (`LearningActionEnum`)
- `"learn_and_practice"`: Node attaches both courses (theory) and engineering projects (practice).
- `"learn_only"`: Theoretical foundational node; courses attached only.
- `"practice_only"`: Hands-on competency node; projects attached only.

---

# Standardized Error Contract

All error responses across the AI service follow this uniform structure:

```json
{
  "success": false,
  "error": {
    "code": "CAREER_NOT_FOUND",
    "message": "Target career 'Cloud Architect' could not be found in the knowledge base."
  }
}
```

### Standard Error Codes

| HTTP Status | Error Code | Trigger Condition |
|---|---|---|
| `400 Bad Request` | `INVALID_REQUEST` | Malformed JSON or incompatible parameter combination |
| `404 Not Found` | `CAREER_NOT_FOUND` | `target_role` does not match any known career in `careers.json` |
| `404 Not Found` | `SKILL_NOT_FOUND` | Explicit skill lookup failed in skill taxonomy |
| `422 Unprocessable Entity` | `VALIDATION_ERROR` | Pydantic constraint violation (e.g. `top_k: 0`, invalid difficulty) |
| `500 Internal Server Error` | `RECOMMENDATION_ENGINE_ERROR` | Failure inside career/course/project recommendation engine |
| `500 Internal Server Error` | `SKILL_GAP_ENGINE_ERROR` | Graph traversal or topological sort failure |
| `500 Internal Server Error` | `ROADMAP_GENERATION_ERROR` | Induced subgraph cycle pruning or layout failure |
| `503 Service Unavailable` | `VECTOR_SEARCH_ERROR` | Semantic vector index unavailable |
| `503 Service Unavailable` | `DATABASE_ERROR` | Knowledge base or MongoDB connection failure |

---

# 1. Career Recommendation

## Endpoint
`POST /ai/recommend-career`

## Purpose
Analyzes the student's current skills and free-text interests against the RouteMaster Career Knowledge Base (Phase 3). Computes a hybrid multi-factor compatibility score (skills match, interest vector dot product, transferable skills, semantic similarity) and returns ranked career suggestions with explainable rationales.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL", "Git"],
  "interests": "Artificial Intelligence, Machine Learning",
  "top_k": 3
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `student_id` | `string` | No | `null` | Optional student ID for telemetry |
| `skills` | `string[]` | No | `[]` | Current learner skills (supports `current_skills` alias) |
| `interests` | `string` \| `string[]` | No | `""` | Free-text interests or list of interest keywords |
| `top_k` | `integer` | No | `5` | Number of recommendations to return (range: `1`–`20`) |

## Response
```json
{
  "recommendations": [
    {
      "career_id": "CA_042",
      "career_title": "AI Engineer",
      "career_domain": "Artificial Intelligence",
      "match_score": 87.4,
      "technical_match_score": 75.0,
      "matched_skills": ["Python", "SQL"],
      "missing_skills": [
        {
          "skill_id": "SK_00264",
          "skill_name": "Machine Learning",
          "importance": "Critical"
        }
      ],
      "reason": "Strong alignment with AI interests. Python and SQL match core engineering requirements."
    }
  ],
  "total": 1
}
```

## Response Fields
| Field | Type | Description |
|---|---|---|
| `recommendations` | `object[]` | List of ranked career items |
| `recommendations[].career_id` | `string` | Canonical career ID (`CA_xxx`) |
| `recommendations[].career_title` | `string` | Official display title of career |
| `recommendations[].career_domain` | `string` | Primary industry domain |
| `recommendations[].match_score` | `float` | Overall fit percentage (`0.0`–`100.0`) |
| `recommendations[].technical_match_score` | `float` | Direct technical skill match percentage (`0.0`–`100.0`) |
| `recommendations[].matched_skills` | `string[]` | Skills student already has for this career |
| `recommendations[].missing_skills` | `object[]` | Required skills student needs to learn |
| `recommendations[].reason` | `string` | Explainable recommendation reason |
| `total` | `integer` | Count of recommendations returned |

## Processing Flow
1. Normalize raw skill inputs against canonical taxonomy (`data/processed/skills.json`).
2. Vectorize user interests with TF-IDF and compute dot-product alignment with RIASEC interest profiles.
3. Compute semantic text similarity between student profile and career descriptions.
4. Apply dynamic cold-start weight adjustment if skills or interests are partially populated.
5. Rank careers descending by hybrid score and generate natural-language explanations.

---

# 2. Skill Gap Analysis

## Endpoint
`POST /ai/skill-gap`

## Purpose
Performs deep graph-theoretic skill gap analysis between a student's profile and a target career (Phase 4). Identifies missing technical skills, resolves transitive prerequisite dependencies through the Skill Dependency Graph, and generates a topologically ordered sequential study path.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL", "Git"],
  "target_role": "AI Engineer"
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `student_id` | `string` | No | `null` | Optional student ID |
| `skills` | `string[]` | No | `[]` | Current learner skills (supports `current_skills` alias) |
| `target_role` | `string` | **Yes** | — | Target career title or ID (supports `target_career` alias) |

## Response
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
  "matched_skills": ["Python", "SQL"],
  "missing_skills": [
    {
      "skill_id": "SK_00264",
      "skill_name": "Machine Learning",
      "skill_category": "AI & ML",
      "priority": "Critical"
    }
  ],
  "prerequisite_gaps": [
    {
      "skill_id": "SK_00360",
      "skill_name": "Python",
      "required_by_skill_id": "SK_00264",
      "required_by_skill_name": "Machine Learning",
      "reason": "Machine Learning requires Python as a programming prerequisite."
    }
  ],
  "learning_sequence": [
    {
      "sequence_number": 1,
      "skill_id": "SK_00264",
      "skill_name": "Machine Learning",
      "skill_type": "technical",
      "priority": "Critical",
      "reason": "Direct critical requirement for target career.",
      "prerequisites": ["SK_00360"]
    }
  ]
}
```

## Response Fields
| Field | Type | Description |
|---|---|---|
| `career` | `object` | Target career summary |
| `readiness_score` | `float` | Overall readiness percentage (`0.0`–`100.0`) |
| `technical_match_pct` | `float` | Direct technical skill match percentage (`0.0`–`100.0`) |
| `current_skills` | `string[]` | Student skills passed in request |
| `matched_skills` | `string[]` | Mastered skills required for career |
| `missing_skills` | `object[]` | Direct missing technical skills |
| `prerequisite_gaps` | `object[]` | Indirect prerequisite skills required upstream |
| `learning_sequence` | `object[]` | Topologically sequenced study sequence |

## Processing Flow
1. Fetch target career requirements from `career_skills.json`.
2. Compute set difference: $\text{Missing} = \text{Required} \setminus \text{Student}$.
3. Traverse Skill Dependency Graph to find transitive prerequisites: $\text{Prereqs}(\text{Missing}) \setminus \text{Student}$.
4. Compute topological ordering using NetworkX DAG resolution.
5. Output structured gap report with importance tier assignments.

---

# 3. Course Recommendation

## Endpoint
`POST /ai/recommend-courses`

## Purpose
Generates personalized course recommendations using the Phase 7 Hybrid Recommender. Blends skill-overlap matching (40%), Sentence Transformer dense vector semantics (`BAAI/bge-small-en-v1.5`, 30%), prerequisite graph readiness (20%), and difficulty alignment (10%). Automatically excludes completed courses.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL"],
  "interests": "Artificial Intelligence",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "number_of_results": 3
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `student_id` | `string` | No | `null` | Optional student ID |
| `skills` | `string[]` | No | `[]` | Current learner skills |
| `interests` | `string` \| `string[]` | No | `""` | Free-text interests |
| `target_role` | `string` | **Yes** | — | Target career title or ID |
| `difficulty` | `string` | No | `"Any Level"` | Allowed: `Any Level`, `Beginner`, `Intermediate`, `Advanced` |
| `completed_courses` | `string[]` | No | `[]` | Course names to filter out of results |
| `number_of_results` | `integer` | No | `5` | Number of courses to return (`1`–`50`) |

## Response
```json
{
  "target_role": "AI Engineer",
  "courses": [
    {
      "course_id": "C_1042",
      "course_name": "Machine Learning Specialization",
      "organization": "DeepLearning.AI",
      "difficulty": "Intermediate",
      "rating": 4.9,
      "url": "https://coursera.org/learn/machine-learning",
      "relevance_score": 0.9142,
      "matched_skills": ["Python"],
      "missing_skills_covered": ["Machine Learning", "Supervised Learning"],
      "prerequisite_status": "Ready",
      "reason": "Teaches 2 critical gap skills (Machine Learning, Supervised Learning) with high rating."
    }
  ],
  "total": 1
}
```

## Response Fields
| Field | Type | Description |
|---|---|---|
| `target_role` | `string` | Target career evaluated |
| `courses` | `object[]` | Ranked course recommendations |
| `courses[].course_id` | `string` | Canonical course ID |
| `courses[].course_name` | `string` | Course title |
| `courses[].organization` | `string` | Provider / University |
| `courses[].difficulty` | `string` | Difficulty tier |
| `courses[].rating` | `float` | Average rating (out of 5.0) |
| `courses[].url` | `string` | Enrollment URL |
| `courses[].relevance_score` | `float` | Hybrid composite match score (`0.0`–`1.0`) |
| `courses[].matched_skills` | `string[]` | Current skills reinforced |
| `courses[].missing_skills_covered` | `string[]` | Target career gap skills taught |
| `courses[].prerequisite_status` | `string` | `"Ready"` or `"Locked"` |
| `courses[].reason` | `string` | Recommendation rationale |
| `total` | `integer` | Count of courses returned |

---

# 4. Project Recommendation

## Endpoint
`POST /ai/recommend-projects`

## Purpose
Recommends hands-on engineering projects designed to bridge skill gaps (Phase 8). The engine selects projects that simultaneously leverage the student's existing skills while developing their missing target career proficiencies. Skill gaps are derived automatically from `target_role`.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL", "Git"],
  "interests": "Computer Vision",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "number_of_results": 3
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `student_id` | `string` | No | `null` | Optional student identifier |
| `skills` | `string[]` | No | `[]` | Current learner skills |
| `interests` | `string` \| `string[]` | No | `""` | Free-text interests |
| `target_role` | `string` | **Yes** | — | Target career title or ID |
| `difficulty` | `string` | No | `"Any Level"` | Allowed: `Any Level`, `Beginner`, `Intermediate`, `Advanced` |
| `number_of_results` | `integer` | No | `5` | Number of projects to return (`1`–`50`) |

## Response
```json
{
  "target_role": "AI Engineer",
  "projects": [
    {
      "project_id": "PROJ_042",
      "project_name": "Autonomous Drone Navigation System",
      "domain": "Robotics & AI",
      "difficulty": "Intermediate",
      "github_url": "https://github.com/example/drone-nav",
      "relevance_score": 0.8875,
      "skills_to_develop": ["Computer Vision", "Reinforcement Learning"],
      "matched_existing_skills": ["Python", "Git"],
      "prerequisite_status": "Ready",
      "reason": "Develops 2 critical missing skills while practicing known Python and Git proficiencies."
    }
  ],
  "total": 1
}
```

---

# 5. Personalized Roadmap Generator

## Endpoint
`POST /ai/generate-roadmap`

## Purpose
Generates a prerequisite-aware, topologically sequenced personalized learning roadmap (Phase 9). Outputs a **React Flow–compatible graph** with `nodes[]` and `edges[]`, where each node represents a competency milestone enriched with attached courses and engineering projects.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "Mathematics"],
  "interests": "Generative AI",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "courses_per_skill": 2,
  "projects_per_skill": 1
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `skills` | `string[]` | No | `[]` | Current learner skills |
| `target_role` | `string` | **Yes** | — | Target career title or ID |
| `difficulty` | `string` | No | `"Any Level"` | Difficulty tier |
| `completed_courses` | `string[]` | No | `[]` | Excluded completed courses |
| `courses_per_skill` | `integer` | No | `3` | Max courses attached per node (`0`–`10`) |
| `projects_per_skill` | `integer` | No | `2` | Max projects attached per node (`0`–`10`) |

## Response (React Flow Compatible)
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
      "courses": [
        {
          "course_id": "C_1042",
          "course_name": "Machine Learning Specialization",
          "organization": "DeepLearning.AI",
          "difficulty": "Intermediate",
          "rating": 4.9,
          "url": "https://coursera.org/...",
          "relevance_score": 0.9142
        }
      ],
      "projects": [
        {
          "project_id": "PROJ_042",
          "project_name": "Predictive Maintenance System",
          "difficulty": "Intermediate",
          "github_url": "https://github.com/...",
          "relevance_score": 0.875,
          "skills_to_develop": ["Machine Learning"]
        }
      ],
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

---

# 6. Unified Recommendation Pipeline

## Endpoint
`POST /ai/recommend` ⭐ **(Primary Orchestration Endpoint)**

## Purpose
Executes the complete RouteMaster AI pipeline in a single, high-performance call. Computes the skill gap once and shares it across course, project, and roadmap engines, eliminating duplicate computation. Supports automatic career selection fallback when `target_role` is omitted.

## Request
```json
{
  "student_id": "STU_84920",
  "skills": ["Python", "SQL", "Git"],
  "interests": "Artificial Intelligence, Generative AI",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "completed_courses": ["Introduction to Python"],
  "number_of_results": 3,
  "courses_per_skill": 2,
  "projects_per_skill": 1,
  "top_k_careers": 1
}
```

## Request Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `student_id` | `string` | No | `null` | Student identifier |
| `skills` | `string[]` | No | `[]` | Current learner skills |
| `interests` | `string` \| `string[]` | No | `""` | Free-text interests |
| `target_role` | `string` | No | `null` | Target career (if omitted, top match is auto-selected) |
| `difficulty` | `string` | No | `"Any Level"` | Difficulty preference |
| `completed_courses` | `string[]` | No | `[]` | Completed courses to exclude |
| `number_of_results` | `integer` | No | `5` | Count of courses/projects to recommend |
| `courses_per_skill` | `integer` | No | `3` | Roadmap courses per skill node |
| `projects_per_skill` | `integer` | No | `2` | Roadmap projects per skill node |
| `top_k_careers` | `integer` | No | `1` | Careers to evaluate if `target_role` is omitted |

## Response
```json
{
  "status": "success",
  "profile": {
    "student_id": "STU_84920",
    "skills": ["Python", "SQL", "Git"],
    "interests": "Artificial Intelligence, Generative AI"
  },
  "career": {
    "career_id": "CA_042",
    "career_title": "AI Engineer",
    "match_score": 87.4,
    "reason": "Strong alignment with AI interests."
  },
  "skill_gap": {
    "current_skills": ["Python", "SQL", "Git"],
    "matched_skills": ["Python", "SQL"],
    "missing_skills": [
      {
        "skill_id": "SK_00264",
        "skill_name": "Machine Learning",
        "priority": "Critical"
      }
    ],
    "readiness_score": 22.5
  },
  "courses": [ ... ],
  "projects": [ ... ],
  "roadmap": {
    "career": { "career_id": "CA_042", "career_title": "AI Engineer" },
    "summary": { "progress_percentage": 11.1, "career_readiness_score": 14.3, ... },
    "nodes": [ ... ],
    "edges": [ ... ]
  },
  "warnings": []
}
```

## Partial Failure Behavior
If a non-critical subsystem (such as project recommendations) encounters an issue, the pipeline returns:
```json
{
  "status": "partial",
  "warnings": [
    {
      "component": "projects",
      "code": "PROJECT_RECOMMENDATION_FAILED",
      "message": "Project recommendation service temporarily unavailable."
    }
  ],
  "career": { ... },
  "skill_gap": { ... },
  "courses": [ ... ],
  "projects": [],
  "roadmap": { ... }
}
```

---

# Health & Readiness Probes

### Liveness Probe
`GET /health`
```json
{
  "status": "healthy",
  "service": "routemaster-ai",
  "version": "1.0.0",
  "environment": "development"
}
```

### Readiness Probe
`GET /ready`
```json
{
  "status": "ready",
  "checks": {
    "engines": "ok",
    "data": "ok"
  }
}
```
