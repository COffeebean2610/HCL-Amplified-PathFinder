# Phase 11 — API Contract & Documentation

## RouteMaster — Mastering the Sequence of Complex Educational Goals
**Engineering Milestone Record: AI/ML Recommendation & Intelligence Engine Handoff**

---

## 1. Objective

Phase 11 formalizes, stabilizes, freezes, and documents the complete **REST API Contract** between the RouteMaster AI/ML service and the main application backend (Member 2). 

The goal of this phase is to ensure that Member 2 and Member 3 can consume all intelligence modules (career recommendation, skill gap analysis, prerequisite graph sequencing, hybrid course ranking, project recommendations, and React Flow roadmaps) through predictable, implementation-ready, type-safe API endpoints without needing to understand or access the internal AI codebase.

---

## 2. Starting Point

Prior to Phase 11:
- Phase 10 established the FastAPI service skeleton (`ai-service/app/main.py`) and basic endpoint routes.
- Initial request and response schemas existed but lacked canonical normalization aliases (`skills` vs `current_skills`, `target_role` vs `target_career`, `difficulty` vs `preferred_difficulty`).
- Error responses did not have a uniform `{ "success": false, "error": { "code": "...", "message": "..." } }` contract for 422 validation errors.
- No machine-readable OpenAPI specification file (`docs/openapi.json`) or concrete JSON example repository (`docs/api_examples/`) existed.
- SDE handoff documentation was fragmented across phase notes rather than unified in a dedicated integration reference.

---

## 3. Work Completed

1. **Schema Standardization & Canonical Profile**:
   - Defined `CanonicalStudentProfile` in `app/schemas/common.py` with multi-alias support.
   - Standardized all Pydantic request models (`CareerRequest`, `SkillGapRequest`, `CourseRequest`, `ProjectRequest`, `RoadmapRequest`, `RecommendationRequest`) with automated pre-validation alias resolution.
2. **Unified Error Contract**:
   - Standardized all custom and framework exceptions to emit uniform `{ "success": false, "error": { "code": "...", "message": "..." } }` structures across 400, 404, 422, 500, and 503 HTTP status codes.
   - Implemented custom `RequestValidationError` formatting for human-friendly field-level error messages.
3. **Score Standardization**:
   - Formally documented and standardized all score fields (0–100 for career match, readiness, technical coverage; 0.0–1.0 for normalized composite relevance scores).
4. **Machine-Readable OpenAPI Contract**:
   - Generated and exported [`docs/openapi.json`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/openapi.json) directly from the live FastAPI application metadata.
5. **Sample Request/Response Library**:
   - Generated 12 real-data JSON samples in [`docs/api_examples/`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/api_examples/) across all 6 core endpoints.
6. **Documentation & Handoff Suite**:
   - Authoritative API Reference: [`docs/API_DOCUMENTATION.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/API_DOCUMENTATION.md).
   - SDE Integration Guide: [`docs/MEMBER_2_HANDOFF.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/MEMBER_2_HANDOFF.md).
   - Phase Engineering Record: [`docs/PHASE_11_API_CONTRACT_DOCUMENTATION.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/PHASE_11_API_CONTRACT_DOCUMENTATION.md).

---

## 4. API Architecture

```
                                RouteMaster System Topology
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      │                                                                             │
Member 3: React Frontend                                              Member 2: Main Application Backend
(React Flow, Tailwind UI)                                              (Node/Express or Flask, MongoDB Atlas)
      │                                                                             │
      │ ◄────────── HTTP REST (Application User CRUD & Auth) ───────────────────────►│
      │                                                                             │
      │                                                                             │ (HTTP POST / JSON)
      │                                                                             ▼
      │                                                               Member 1: FastAPI AI Service
      │                                                               (Port 8001, Standalone Process)
      │                                                                             │
      │                                                                             ├── Lifespan Singletons
      │                                                                             ├── Pydantic v2 Validators
      │                                                                             ├── Service Layer Orchestration
      │                                                                             └── Phase 1–9 AI Engines
      ▼                                                                             │
React Flow Nodes & Edges ◄──────────────────────────────────────────────────────────┘
```

---

## 5. Endpoints Implemented

| Endpoint | HTTP Method | Schema Request Model | Schema Response Model | Description |
|---|---|---|---|---|
| `/health` | `GET` | — | `HealthResponse` | Liveness check |
| `/ready` | `GET` | — | `ReadinessResponse` | Engine memory readiness check |
| `/ai/recommend-career` | `POST` | `CareerRequest` | `CareerResponse` | Profile-to-career recommendation |
| `/ai/skill-gap` | `POST` | `SkillGapRequest` | `SkillGapResponse` | Skill gap analysis & topological ordering |
| `/ai/recommend-courses` | `POST` | `CourseRequest` | `CourseResponse` | Hybrid course ranking & completed filtering |
| `/ai/recommend-projects` | `POST` | `ProjectRequest` | `ProjectResponse` | Skill-gap-aware engineering project recommendations |
| `/ai/generate-roadmap` | `POST` | `RoadmapRequest` | `RoadmapResponse` | React Flow node/edge graph generator |
| `/ai/recommend` | `POST` | `RecommendationRequest` | `RecommendationResponse` | **Primary Unified Orchestration Pipeline** |

---

## 6. Request Schema Design

To minimize client-side formatting bugs, all request models inherit standardized alias resolution via Pydantic model validators:
- `skills` ⟷ `current_skills`
- `target_role` ⟷ `target_career`
- `difficulty` ⟷ `preferred_difficulty`
- `student_id` (optional string for user tracking)

If a client sends either key, the validator populates both without raising validation errors.

---

## 7. Response Schema Design

Response structures are tailored to the exact consumers:
- **`CareerResponse`**: Exposes `match_score` (0–100), `technical_match_score`, `matched_skills`, `missing_skills`, and natural language `reason`.
- **`SkillGapResponse`**: Exposes `readiness_score` (0–100), `prerequisite_gaps`, and ordered `learning_sequence`.
- **`CourseResponse`**: Exposes ranked `courses[]` with `relevance_score` (0–1.0), `missing_skills_covered`, and `prerequisite_status`.
- **`ProjectResponse`**: Exposes ranked `projects[]` with `skills_to_develop`, `matched_existing_skills`, and GitHub URLs.
- **`RoadmapResponse`**: Strictly adheres to React Flow node/edge format:
  - `nodes[].id`: `"skill-SK_xxxxx"`
  - `nodes[].data`: `{ label, status, priority, reason, learning_action }`
  - `edges[].id`: `"edge-SK_xxx-SK_yyy"`
- **`RecommendationResponse`**: Combines all outputs in a unified JSON payload with `status` (`"success"` | `"partial"`) and structured `warnings[]`.

---

## 8. Pydantic Models

All schemas are implemented using **Pydantic v2** with:
- Strict typing (`List[str]`, `Optional[str]`, `float`, `int`, `Enum`)
- Range constraints (`ge=1`, `le=50`, `ge=0`, `le=10`)
- Enums (`DifficultyEnum`, `PriorityEnum`, `NodeStatusEnum`, `LearningActionEnum`)
- Rich field descriptions and realistic OpenAPI examples

---

## 9. Error Handling

All errors return structured JSON with uniform keys:

```json
{
  "success": false,
  "error": {
    "code": "CAREER_NOT_FOUND",
    "message": "Target career 'Cloud Architect' could not be found in the knowledge base."
  }
}
```

### Standardized Status Codes:
- `400`: `INVALID_REQUEST`
- `404`: `CAREER_NOT_FOUND`, `SKILL_NOT_FOUND`
- `422`: `VALIDATION_ERROR` (Detailed field-level messages)
- `500`: `RECOMMENDATION_ENGINE_ERROR`, `SKILL_GAP_ENGINE_ERROR`, `ROADMAP_GENERATION_ERROR`, `INTERNAL_SERVER_ERROR`
- `503`: `VECTOR_SEARCH_ERROR`, `DATABASE_ERROR`

---

## 10. Score Standardization

| Metric | Range | Precision | Interpretation |
|---|---|---|---|
| `career.match_score` | 0.0 – 100.0 | 1 decimal | Overall profile fit percentage |
| `skill_gap.readiness_score` | 0.0 – 100.0 | 1 decimal | Role readiness score |
| `roadmap.summary.progress_percentage` | 0.0 – 100.0 | 1 decimal | Milestone progress rate |
| `courses[].relevance_score` | 0.0 – 1.0 | 4 decimals | Composite course relevance |
| `projects[].relevance_score` | 0.0 – 1.0 | 4 decimals | Composite project relevance |

---

## 11. API Documentation

Interactive Swagger documentation is exposed at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI Schema**: `http://localhost:8001/openapi.json`

---

## 12. Member 2 Integration Contract

Member 2 communicates exclusively with the AI Service over HTTP:
```python
import os, requests

AI_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

def get_recommendations(profile: dict) -> dict:
    resp = requests.post(f"{AI_URL}/ai/recommend", json=profile, timeout=60)
    resp.raise_for_status()
    return resp.json()
```

---

## 13. Testing

- **Testing Tools**: `pytest`, `httpx`, `fastapi.testclient.TestClient`.
- **Test Suite**: `ai-service/tests/test_ai_service.py` (33 tests).
- **Execution Time**: ~9.5 minutes (includes full embedding model initialization).
- **Pass Rate**: **33 / 33 passed (100%)**.

---

## 14. Sample Inputs & Outputs

All 12 authentic JSON sample files are saved in [`docs/api_examples/`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/api_examples/):
- `recommend-career-request.json` & `recommend-career-response.json`
- `skill-gap-request.json` & `skill-gap-response.json`
- `recommend-courses-request.json` & `recommend-courses-response.json`
- `recommend-projects-request.json` & `recommend-projects-response.json`
- `generate-roadmap-request.json` & `generate-roadmap-response.json`
- `recommend-request.json` & `recommend-response.json`

---

## 15. Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| [`ai-service/app/schemas/common.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/common.py) | Modified | Added `CanonicalStudentProfile`, enums, and `ErrorResponse` |
| [`ai-service/app/schemas/career.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/career.py) | Modified | Added alias support and documentation metadata |
| [`ai-service/app/schemas/skill_gap.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/skill_gap.py) | Modified | Added alias support and documentation metadata |
| [`ai-service/app/schemas/course.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/course.py) | Modified | Added alias support and documentation metadata |
| [`ai-service/app/schemas/project.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/project.py) | Modified | Added alias support and documentation metadata |
| [`ai-service/app/schemas/roadmap.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/roadmap.py) | Modified | Added alias support and React Flow schema annotations |
| [`ai-service/app/schemas/recommendation.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/schemas/recommendation.py) | Modified | Added alias support and student_id tracking |
| [`ai-service/app/core/exceptions.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/ai-service/app/core/exceptions.py) | Modified | Standardized error handler for custom errors & 422 validations |
| [`docs/openapi.json`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/openapi.json) | Created | Machine-readable OpenAPI 3.1 specification |
| [`docs/API_DOCUMENTATION.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/API_DOCUMENTATION.md) | Created | Primary SDE API Reference document |
| [`docs/MEMBER_2_HANDOFF.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/MEMBER_2_HANDOFF.md) | Created | Member 2 SDE Integration & Architecture Handoff |
| [`docs/PHASE_11_API_CONTRACT_DOCUMENTATION.md`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/PHASE_11_API_CONTRACT_DOCUMENTATION.md) | Created | Phase 11 Engineering Milestone Record |
| [`docs/api_examples/*.json`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/docs/api_examples/) (12 files) | Created | Authentic request/response JSON payload examples |

---

## 16. Design Decisions & Trade-Offs

| Decision | Selected Choice | Alternative Considered | Rationale & Trade-off |
|---|---|---|---|
| **Validation Layer** | Pydantic v2 | Manual dict validation / Marshmallow | Pydantic v2 provides compiled C-speed validation, auto-generated OpenAPI documentation, and model-level alias resolution. |
| **Integration Boundary** | REST / JSON | Shared Python imports / gRPC | Member 2's backend may run on Node.js/TypeScript. Direct Python imports would create fragile coupling. REST provides language-agnostic isolation. |
| **Orchestration Model** | Single Unified Endpoint (`/ai/recommend`) | Multiple sequential client-side calls | Calling gap, course, project, and roadmap engines separately would recompute skill gaps 4 times. Unified pipeline computes gaps once and shares results in memory. |
| **Error Format** | Uniform `{ success: false, error: { code, message } }` | Raw framework tracebacks / strings | Eliminates security risks from stack trace leakage and allows Member 2 to build clean `switch (code)` error dispatchers. |
| **Roadmap Graph Contract** | Native React Flow `nodes[]` & `edges[]` | Custom nested tree hierarchy | Member 3 uses React Flow directly. Providing flat `nodes[]` and `edges[]` avoids client-side recursive tree-flattening. |

---

## 17. Results & Verification

- **API Service Test Suite**: `33 passed, 0 failed (100% pass rate)`
- **Foundational Regression Suite**: `83 passed, 0 failed (100% pass rate)`
- **Total Project Test Suite**: `116 passed, 0 failed (100% pass rate)`
- **Contract Synchronization**: Live FastAPI schemas, OpenAPI export, and markdown documentation are 100% aligned.

---

## 18. Deliverables Completed

- [x] **54. Freeze request JSON format**: Frozen with Pydantic v2 schemas and alias compatibility.
- [x] **55. Freeze response JSON format**: Standardized score scales (0–100 & 0.0–1.0) and React Flow graph structures.
- [x] **56. Create sample requests**: 6 realistic request JSON files in `docs/api_examples/`.
- [x] **57. Create sample responses**: 6 realistic response JSON files in `docs/api_examples/`.
- [x] **58. Document all AI endpoints**: Complete documentation in `docs/API_DOCUMENTATION.md`.
- [x] **59. Give API documentation to Member 2**: Comprehensive handoff guide in `docs/MEMBER_2_HANDOFF.md`.

---

## 19. Known Limitations

- **Single Active Career Target in Pipeline**: Multi-route career pursuit schemas are supported in request models, but the roadmap generator currently sequences one primary `target_role` per execution.
- **Cold-Start Duration**: The first startup of the AI service takes ~35–50 seconds to initialize Sentence Transformer weights and vector search caches.

---

## 20. Phase Completion Checklist

- [x] Canonical Student Profile defined (`CanonicalStudentProfile`)
- [x] Alias resolution enabled (`skills`/`current_skills`, `target_role`/`target_career`, `difficulty`/`preferred_difficulty`)
- [x] Request JSON contracts frozen
- [x] Response JSON contracts frozen
- [x] Unified error handling contract implemented (`{ success: false, error: { code, message } }`)
- [x] Score scales standardized and documented
- [x] Machine-readable OpenAPI spec generated (`docs/openapi.json`)
- [x] 12 sample JSON request/response files created in `docs/api_examples/`
- [x] SDE API reference documentation created (`docs/API_DOCUMENTATION.md`)
- [x] Member 2 integration handoff created (`docs/MEMBER_2_HANDOFF.md`)
- [x] Phase 11 milestone documentation created (`docs/PHASE_11_API_CONTRACT_DOCUMENTATION.md`)
- [x] 33 AI Service tests passing with zero errors
- [x] 83 Foundational regression tests passing with zero errors
- [x] Zero regressions across all 11 phases
