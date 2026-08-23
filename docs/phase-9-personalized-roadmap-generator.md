# Phase 9 — Personalized Roadmap Generator

**Module**: `src/roadmap_generator/`  
**Phase**: 9 of 9  
**Status**: ✅ Complete  
**Tests**: 11 unit tests — all passing  

---

## 1. Overview

Phase 9 implements the **Personalized Roadmap Generator** — the final intelligence module of the RouteMaster AI/ML layer.

It integrates all previous phases into a single unified pipeline that produces a **topologically ordered, prerequisite-aware learning roadmap** for a given student profile and target career. The output is serialized as **React Flow–compatible nodes and edges**, ready for consumption by the frontend React Flow canvas.

```
Student Profile
      │
      ▼
 Phase 4: SkillGapEngine           ← resolves career skill requirements vs. current skills
      │
      ▼
 Phase 2: PrerequisiteResolver     ← builds induced required prerequisite subgraph
      │
      ▼
 Cycle Detection & DAG Resolution  ← ensures a valid topological sort is always possible
      │
      ▼
 Topological Sort (NetworkX)       ← sequences skills: predecessors before dependents
      │
      ▼
 Phase 7: HybridRecommender        ← attaches relevant courses per skill node
 Phase 8: ProjectRecommender       ← attaches relevant projects per skill node
      │
      ▼
 React Flow Nodes + Edges JSON     ← returned to SDE FastAPI layer
```

---

## 2. Module Structure

```
src/roadmap_generator/
├── __init__.py      ← Package exports (RoadmapGenerator, generate_roadmap_api)
├── schemas.py       ← Pydantic request/response models
└── engine.py        ← Core roadmap generation logic
```

---

## 3. Input Schema

**Endpoint**: `POST /api/generate-roadmap`

```json
{
  "skills": ["Python", "Mathematics"],
  "interests": "AI, Machine Learning",
  "target_role": "AI Engineer",
  "difficulty": "Any Level",
  "completed_courses": ["Introduction to Python"],
  "courses_per_skill": 3,
  "projects_per_skill": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `target_role` | `str` | ✅ | Target career title or ID |
| `skills` | `list[str]` | ❌ | Current learner skills (raw text) |
| `interests` | `str \| list[str]` | ❌ | Learner interests |
| `difficulty` | `str` | ❌ | `Any Level`, `Beginner`, `Intermediate`, `Advanced` |
| `completed_courses` | `list[str]` | ❌ | Courses to exclude from recommendations |
| `courses_per_skill` | `int` | ❌ | Max courses per node (default: 3) |
| `projects_per_skill` | `int` | ❌ | Max projects per node (default: 2) |

---

## 4. Output Schema

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
  "nodes": [ ... ],
  "edges": [ ... ],
  "warnings": []
}
```

### Node Structure

Each node is React Flow–compatible and contains:

```json
{
  "id": "skill-SK_00264",
  "skill_id": "SK_00264",
  "skill_name": "Machine Learning",
  "status": "next",
  "priority": "Critical",
  "sequence": 3,
  "prerequisites": ["SK_00360", "SK_00270"],
  "courses": [
    {
      "course_id": "CRS_1234",
      "course_name": "Machine Learning Specialization",
      "organization": "DeepLearning.AI",
      "difficulty": "Intermediate",
      "rating": 4.9,
      "url": "https://coursera.org/...",
      "relevance_score": 0.88
    }
  ],
  "projects": [
    {
      "project_id": "PRJ_012",
      "project_name": "Sentiment Analysis Pipeline",
      "difficulty": "Intermediate",
      "github_url": "https://github.com/...",
      "relevance_score": 0.75,
      "skills_to_develop": ["Machine Learning", "NLP"]
    }
  ],
  "data": {
    "label": "Machine Learning",
    "status": "next",
    "priority": "Critical",
    "reason": "This skill is ready to learn! All prerequisites are met...",
    "learning_action": "learn_and_practice"
  }
}
```

### Edge Structure

```json
{
  "id": "edge-SK_00360-SK_00264",
  "source": "skill-SK_00360",
  "target": "skill-SK_00264",
  "relationship": "prerequisite"
}
```

---

## 5. Node Status Values

| Status | Meaning |
|---|---|
| `completed` | Learner already has this skill |
| `next` | All required predecessors are completed — ready to learn |
| `locked` | One or more prerequisites are not yet completed |

---

## 6. Learning Action Values

| Action | Meaning |
|---|---|
| `learn_and_practice` | Both courses and projects are available |
| `learn_only` | Only course recommendations available |
| `practice_only` | Only project recommendations available |

---

## 7. Core Algorithm

### Step 1 — Skill Gap Calculation
Delegates to Phase 4 `SkillGapEngine.calculate_gap()` to identify:
- `missing_technical_skills` (career requirements not yet possessed)
- `prerequisite_gaps` (transitive prerequisite deficiencies)
- `matched_technical_skills` (already-owned career-required skills)

### Step 2 — Induced Required Subgraph
Constructs a **NetworkX DiGraph** containing:
- All required career skills for the target career
- All transitive prerequisite ancestors (via `PrerequisiteResolver.get_all_prerequisites()`)
- Only **required edges** (`prerequisite`, `strong_prerequisite`)

Recommended-only edges are excluded to keep the roadmap focused.

### Step 3 — Cycle Detection & Resolution
The induced subgraph is checked with `nx.is_directed_acyclic_graph()`. If cycles are found:
- `nx.simple_cycles()` identifies all cycles
- The first edge of each cycle is removed (feedback arc pruning)
- A `warnings` entry is added to the response for transparency
- Topological sort then proceeds on the pruned DAG

### Step 4 — Topological Sort
`nx.topological_sort()` guarantees that every predecessor skill appears before its dependent skills. This is the canonical learning sequence.

### Step 5 — Node Status Assignment
For each node in topological order:
- If `skill_id ∈ user_skill_ids` → `"completed"`
- Else if all direct predecessors are in `user_skill_ids` → `"next"`
- Else → `"locked"`

### Step 6 — Course & Project Attachment
For non-completed nodes:
- **Courses**: Filtered by `skill_id` match in course skill list, sorted by relevance (rating × difficulty fit), completed courses excluded
- **Projects**: Filtered by `skill_id` match in project skill list, sorted by relevance (difficulty fit × skill count)
- Top-K items per node are attached (configurable)

### Step 7 — Edge Construction
All edges in the subgraph DiGraph are serialized as React Flow edge objects with `source` and `target` referencing `"skill-{skill_id}"` formatted node IDs.

---

## 8. REST API Endpoint

### `POST /api/generate-roadmap`

**Request Body**: JSON matching `RoadmapRequest` schema.

**Response**: JSON matching `RoadmapResponse` schema.

**Error Cases**:
- `400` — Missing `target_role` or empty request body
- `500` — Internal engine error (logged with message)

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Mathematics"],
    "target_role": "AI Engineer",
    "difficulty": "Intermediate",
    "courses_per_skill": 3,
    "projects_per_skill": 2
  }'
```

---

## 9. Files Created / Modified

| File | Action | Description |
|---|---|---|
| [`src/roadmap_generator/__init__.py`](../src/roadmap_generator/__init__.py) | Created | Package exports |
| [`src/roadmap_generator/schemas.py`](../src/roadmap_generator/schemas.py) | Created | Pydantic request/response schemas |
| [`src/roadmap_generator/engine.py`](../src/roadmap_generator/engine.py) | Created | Core roadmap generation engine |
| [`tests/test_roadmap_generator.py`](../tests/test_roadmap_generator.py) | Created | 11 unit & integration tests |
| [`app.py`](../app.py) | Modified | Registered `POST /api/generate-roadmap` |

---

## 10. Tests

**Test file**: `tests/test_roadmap_generator.py`  
**Coverage**: 11 tests — all passing ✅

| # | Test | Description |
|---|---|---|
| 1 | `test_roadmap_subgraph_nodes` | Verifies career subgraph contains expected skill IDs |
| 2 | `test_topological_sorting_order` | Python → ML → Deep Learning sequence order |
| 3 | `test_cycle_detection_warnings` | NetworkX cycle detection and feedback arc removal |
| 4 | `test_prerequisite_status_values` | `completed` / `next` / `locked` status assignments |
| 5 | `test_course_attachments` | Completed courses excluded; per-node course count respected |
| 6 | `test_project_attachments` | Per-node project count limits |
| 7 | `test_roadmap_personalization_differs` | Beginner vs. intermediate profiles produce different completion counts |
| 8 | `test_progress_metrics_calculations` | Progress percentage arithmetic verified |
| 9 | `test_react_flow_edges_structure` | Edge IDs and source/target prefixes are React Flow–compatible |
| 10 | `test_flask_endpoint_request_validation` | Missing `target_role` returns HTTP 400 |
| 11 | `test_flask_endpoint_response_schema` | Valid request returns nodes, edges, and summary |

**Run tests**:
```bash
python -m pytest tests/test_roadmap_generator.py -v
```

**Run full suite**:
```bash
python -m pytest tests/ -q
# 83 passed, 12 warnings
```

---

## 11. SDE Integration Notes

The SDE FastAPI team should proxy to:

```
POST /api/generate-roadmap
```

The `generate_roadmap_api()` function in `src/roadmap_generator/engine.py` can also be imported and called directly from FastAPI route handlers:

```python
from src.roadmap_generator.engine import generate_roadmap_api

result = generate_roadmap_api({
    "skills": user.skills,
    "target_role": user.target_career,
    "difficulty": user.difficulty_preference,
    "completed_courses": user.completed_courses,
    "courses_per_skill": 3,
    "projects_per_skill": 2
})
```

The singleton `RoadmapGenerator` instance is cached on first call — no re-initialization overhead on subsequent requests.

---

## 12. Phase Dependencies

| Phase | Component | Usage in Phase 9 |
|---|---|---|
| Phase 1 | Skill Taxonomy + Registries | `skills.json`, `courses.json`, `projects.json`, `career_skills.json` |
| Phase 2 | PrerequisiteResolver | `get_all_prerequisites()` for transitive closure |
| Phase 4 | SkillGapEngine | `calculate_gap()` for matched/missing skill detection |
| Phase 7 | HybridRecommender | Referenced in engine (optional direct attachment) |
| Phase 8 | ProjectRecommender | Referenced in engine (optional direct attachment) |
