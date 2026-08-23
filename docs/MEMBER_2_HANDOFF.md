# RouteMaster AI Engine — Member 2 (SDE Backend) Integration Guide & Handoff

**Author**: Member 1 (AI/ML Engineer)  
**Target Audience**: Member 2 (SDE / Backend Team)  
**Service Name**: `routemaster-ai`  
**Base URL**: `http://localhost:8001` (configurable via `AI_SERVICE_URL`)  
**API Reference**: [`docs/API_DOCUMENTATION.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/API_DOCUMENTATION.md)  
**OpenAPI Specification**: [`docs/openapi.json`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/openapi.json)

---

# 1. Executive Overview

The RouteMaster AI Service is an independently deployable microservice providing intelligent recommendations for educational sequencing, career path alignment, skill gap resolution, and roadmap visualization.

### Core Principle
> **Member 2 should NEVER directly import internal Python AI modules (`src/*`).**  
> All communication must occur over HTTP using the standardized JSON REST API contract defined here.

```
                      Integration Architecture
                                 │
   Member 3: React UI            │
           │                     │
           │ (HTTPS / REST)      │
           ▼                     ▼
   Member 2: Main Backend ◄─────────────► MongoDB Atlas (User Profiles, Progress)
           │
           │ (HTTP POST / JSON)
           ▼
   Member 1: FastAPI AI Service
           │
           ├── Skill Dependency Graph (Phase 2)
           ├── Career Matching Engine (Phase 3)
           ├── Skill Gap & Topological Sequencer (Phase 4)
           ├── Dense Vector Search (BGE-small / Phase 5 & 6)
           ├── Hybrid Course Recommender (Phase 7)
           ├── Skill-Gap-Aware Project Recommender (Phase 8)
           └── React Flow Roadmap Generator (Phase 9)
```

---

# 2. Authentication & Network Boundary

- **User Authentication (JWT)**: Member 2 handles user registration, JWT generation, session tokens, and route protection on the main backend.
- **AI Service Security**: The AI Service runs on an internal private network or behind a reverse proxy. It does not validate user JWTs directly.
- **Service-to-Service Protection**: In production, Member 2 can supply a shared header (e.g. `X-API-Key: <token>`) if configured.

---

# 3. Canonical Identifiers (IDs Used Across Datasets)

When storing AI outputs in MongoDB Atlas or passing references between services, use the standardized ID prefixes:

| Entity | ID Format | Example | Storage Collection |
|---|---|---|---|
| **Career** | `CA_xxx` | `CA_042` | `careers` / user target profile |
| **Skill** | `SK_xxxxx` | `SK_00264` | `skills` / master taxonomy |
| **Course** | `C_xxxx` or String | `C_1042` | `courses` / course catalog |
| **Project** | `PROJ_xxx` | `PROJ_042` | `projects` / project catalog |
| **Roadmap Node** | `skill-SK_xxxxx` | `skill-SK_00264` | React Flow Node ID |
| **Roadmap Edge** | `edge-SK_xxx-SK_yyy` | `edge-SK_00360-SK_00264` | React Flow Edge ID |

---

# 4. Recommended Backend Integration Workflow

### Primary Pattern: Single Orchestration Call (`POST /ai/recommend`)

For the standard student dashboard / onboarding flow, call **`POST /ai/recommend`**. This executes the entire intelligence pipeline in one shot and returns everything Member 2 and Member 3 need.

```javascript
// Node.js / Express Example for Member 2 Backend
const axios = require('axios');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8001';

async function generateRecommendationsForStudent(userProfile) {
  try {
    const payload = {
      student_id: userProfile._id.toString(),
      skills: userProfile.skills || [],
      interests: userProfile.interests || '',
      target_role: userProfile.targetRole || null,
      difficulty: userProfile.preferredDifficulty || 'Any Level',
      completed_courses: userProfile.completedCourses || [],
      number_of_results: 5,
      courses_per_skill: 3,
      projects_per_skill: 2
    };

    const response = await axios.post(`${AI_SERVICE_URL}/ai/recommend`, payload, {
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
    });

    const aiData = response.data;
    
    // Check for partial degraded states
    if (aiData.status === 'partial') {
      console.warn('AI service degraded warning:', aiData.warnings);
    }

    return aiData;
  } catch (error) {
    if (error.response) {
      console.error('AI Error Code:', error.response.data.error.code);
      console.error('AI Error Message:', error.response.data.error.message);
    }
    throw error;
  }
}
```

---

# 5. Data Handling: What to Store vs What to Pass

When Member 2 receives the `/ai/recommend` response, use this guidance on persistence:

### 1. Store in User's MongoDB Document (`users` / `roadmaps` collection)
- `career.career_id` and `career.career_title` → Student's active career goal
- `skill_gap.readiness_score` → Current readiness percentage
- `skill_gap.missing_skills` → List of pending skills to track
- `roadmap.summary` → Milestone progress statistics
- `roadmap.nodes` and `roadmap.edges` → Persisted roadmap graph state (so user can update node statuses as they finish courses)

### 2. Pass Directly to Frontend (Member 3)
- `courses` → Render Course Recommendation Carousel / List
- `projects` → Render Engineering Projects Grid
- `roadmap.nodes` & `roadmap.edges` → Feed directly into `<ReactFlow nodes={nodes} edges={edges} />`
- `career.match_score` & `career.reason` → Display match rationale widget

### 3. Internal Metadata (Logging Only)
- Response headers `X-Request-ID` and `X-Process-Time-Ms` → Save in backend application logs for monitoring latency.

---

# 6. Score Interpretation Cheatsheet

| Response Key | Range | Interpretation for UI Display |
|---|---|---|
| `career.match_score` | `0–100` | Display as **"Career Match: 87%"** with progress circle |
| `skill_gap.readiness_score` | `0–100` | Display as **"Role Readiness: 23%"** badge |
| `roadmap.summary.progress_percentage` | `0–100` | Display on **Roadmap Progress Bar** |
| `courses[].relevance_score` | `0.0–1.0` | Multiply by 100 for display (e.g. `0.914` → **"91% Match"**) |
| `projects[].relevance_score` | `0.0–1.0` | Multiply by 100 for display (e.g. `0.887` → **"89% Match"**) |

---

# 7. Error Handling Strategy for Member 2

All AI service error responses return `HTTP 4xx/5xx` with this structured schema:

```json
{
  "success": false,
  "error": {
    "code": "CAREER_NOT_FOUND",
    "message": "Target career 'Cloud Architect' could not be found in the knowledge base."
  }
}
```

### Recommended Handler Mapping in SDE Backend:

```typescript
switch (aiError.code) {
  case 'VALIDATION_ERROR':
    return res.status(400).json({ error: 'Please check your skill and career inputs.' });
    
  case 'CAREER_NOT_FOUND':
    return res.status(404).json({ error: 'The selected career is not currently in our roadmap catalog.' });
    
  case 'RECOMMENDATION_ENGINE_ERROR':
  case 'INTERNAL_SERVER_ERROR':
    return res.status(502).json({ error: 'AI Recommendation Service is temporarily unavailable.' });
    
  default:
    return res.status(500).json({ error: 'An unexpected recommendation error occurred.' });
}
```

---

# 8. Available Endpoints Reference

| Route | Primary Consumer | Purpose |
|---|---|---|
| `POST /ai/recommend` | Main Dashboard / Setup | **Recommended**: Complete end-to-end recommendation payload |
| `POST /ai/recommend-career` | Career Exploration Page | Pure career search & compatibility ranking |
| `POST /ai/skill-gap` | Skill Analytics Widget | Targeted skill gap & prerequisite sequence breakdown |
| `POST /ai/recommend-courses` | Course Catalog Search | Course-only recommendations filtered by skill/career |
| `POST /ai/recommend-projects` | Projects Hub | Engineering projects tailored to missing skills |
| `POST /ai/generate-roadmap` | Roadmap Editor / Viewer | Generates/regenerates React Flow graph for target role |
| `GET /health` | DevOps / Docker / K8s | Health check probe (zero load) |
| `GET /ready` | DevOps / Docker / K8s | Readiness probe (verifies models are in memory) |

---

# 9. Support & Troubleshooting

- **Interactive API Documentation**: Open `http://localhost:8001/docs` in your browser while the AI service is running to test live requests interactively.
- **Sample Request/Response JSONs**: Found in [`docs/api_examples/`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/api_examples/).
- **Starting the AI Service Locally**:
  ```bash
  cd ai-service
  pip install -r requirements-ai-service.txt
  uvicorn app.main:app --reload --port 8001
  ```
