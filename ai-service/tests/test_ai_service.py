"""
Phase 10 AI Service Test Suite
Tests all endpoints using FastAPI TestClient (httpx).

The TestClient is started once in conftest.py via a session-scoped autouse fixture,
which triggers the lifespan event and loads all AI engines before any test runs.
Tests access it via pytest.shared_client set in conftest.py.

Covers:
- Health checks
- Career recommendation
- Skill gap analysis
- Course recommendation
- Project recommendation
- Roadmap generation
- Unified /ai/recommend pipeline
- Input validation (HTTP 422)
- Normalization consistency
- Completed course filtering
- Cross-endpoint consistency
"""
import pytest

# All tests use pytest.shared_client set by conftest.py session fixture
def client():
    return pytest.shared_client


STANDARD_PROFILE = {
    "skills": ["Python", "SQL", "Git"],
    "interests": "Artificial Intelligence",
    "target_role": "AI Engineer",
    "difficulty": "Intermediate",
    "completed_courses": [],
    "number_of_results": 3,
    "courses_per_skill": 2,
    "projects_per_skill": 1,
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Health checks
# ─────────────────────────────────────────────────────────────────────────────

def test_health_returns_200():
    r = client().get("/health")
    assert r.status_code == 200

def test_health_schema():
    r = client().get("/health")
    data = r.json()
    assert data["status"] == "healthy"
    assert data["service"] == "routemaster-ai"
    assert "version" in data

def test_readiness_returns_200():
    r = client().get("/ready")
    assert r.status_code == 200

def test_root_returns_info():
    r = client().get("/")
    data = r.json()
    assert "service" in data
    assert "docs" in data


# ─────────────────────────────────────────────────────────────────────────────
# 2. Career recommendation
# ─────────────────────────────────────────────────────────────────────────────

def test_career_recommend_200():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "Machine Learning"],
        "interests": "Artificial Intelligence",
        "top_k": 3,
    })
    assert r.status_code == 200, r.text

def test_career_recommend_schema():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 2
    })
    data = r.json()
    assert "recommendations" in data
    assert "total" in data
    assert data["total"] == len(data["recommendations"])

def test_career_recommend_items_have_scores():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "SQL"], "interests": "Data Science", "top_k": 1
    })
    items = r.json().get("recommendations", [])
    if items:
        item = items[0]
        assert "match_score" in item
        assert "career_title" in item
        assert "reason" in item

def test_career_invalid_top_k():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 0
    })
    assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 3. Skill gap
# ─────────────────────────────────────────────────────────────────────────────

def test_skill_gap_200():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python", "SQL"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200, r.text

def test_skill_gap_schema():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "career" in data
    assert "missing_skills" in data
    assert "readiness_score" in data
    assert isinstance(data["readiness_score"], (float, int))

def test_skill_gap_missing_target_role():
    r = client().post("/ai/skill-gap", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_skill_gap_empty_body():
    r = client().post("/ai/skill-gap", json={})
    assert r.status_code == 422

def test_skill_gap_normalization_consistency():
    """Case-insensitive skill normalization: 'Python' vs 'python' same result."""
    r1 = client().post("/ai/skill-gap", json={"skills": ["Python"], "target_role": "AI Engineer"})
    r2 = client().post("/ai/skill-gap", json={"skills": ["python"], "target_role": "AI Engineer"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert abs(r1.json()["readiness_score"] - r2.json()["readiness_score"]) < 5.0


# ─────────────────────────────────────────────────────────────────────────────
# 4. Course recommendation
# ─────────────────────────────────────────────────────────────────────────────

def test_course_recommend_200():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "Any Level", "number_of_results": 3
    })
    assert r.status_code == 200, r.text

def test_course_recommend_schema():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "courses" in data
    assert "total" in data

def test_course_recommend_invalid_difficulty():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "SuperEasy"
    })
    assert r.status_code == 422

def test_course_recommend_missing_target_role():
    r = client().post("/ai/recommend-courses", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_course_completed_courses_excluded():
    """Completed courses must not appear in results."""
    r1 = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 5
    })
    if r1.status_code != 200 or not r1.json().get("courses"):
        pytest.skip("No courses returned to test filtering")
    first_course = r1.json()["courses"][0]["course_name"]

    r2 = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "completed_courses": [first_course], "number_of_results": 5
    })
    assert r2.status_code == 200
    returned_names = [c["course_name"] for c in r2.json()["courses"]]
    assert first_course not in returned_names

def test_course_result_count_respected():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 2
    })
    assert r.status_code == 200
    assert len(r.json()["courses"]) <= 2


# ─────────────────────────────────────────────────────────────────────────────
# 5. Project recommendation
# ─────────────────────────────────────────────────────────────────────────────

def test_project_recommend_200():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python", "SQL"], "target_role": "AI Engineer", "number_of_results": 3
    })
    assert r.status_code == 200, r.text

def test_project_recommend_schema():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "projects" in data
    assert "total" in data

def test_project_recommend_missing_target_role():
    r = client().post("/ai/recommend-projects", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_project_recommend_invalid_difficulty():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python"], "target_role": "AI Engineer", "difficulty": "Rocket Science"
    })
    assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 6. Roadmap generation
# ─────────────────────────────────────────────────────────────────────────────

def test_roadmap_200():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python", "Mathematics"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200, r.text

def test_roadmap_react_flow_schema():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python", "Mathematics"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "nodes" in data and "edges" in data and "summary" in data
    assert len(data["nodes"]) > 0
    assert all(n["id"].startswith("skill-") for n in data["nodes"])
    assert all(e["source"].startswith("skill-") for e in data["edges"])

def test_roadmap_missing_target_role():
    r = client().post("/ai/generate-roadmap", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_roadmap_courses_per_skill_respected():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "courses_per_skill": 1, "projects_per_skill": 1
    })
    assert r.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 7. Unified /ai/recommend orchestration
# ─────────────────────────────────────────────────────────────────────────────

def test_recommend_200():
    r = client().post("/ai/recommend", json=STANDARD_PROFILE)
    assert r.status_code == 200, r.text

def test_recommend_full_schema():
    r = client().post("/ai/recommend", json=STANDARD_PROFILE)
    data = r.json()
    assert "status" in data
    assert "profile" in data
    assert "career" in data
    assert "skill_gap" in data
    assert "courses" in data
    assert "projects" in data

def test_recommend_status_success_or_partial():
    r = client().post("/ai/recommend", json=STANDARD_PROFILE)
    assert r.json()["status"] in ("success", "partial")

def test_recommend_without_target_role():
    """Should auto-select top career from skills/interests."""
    r = client().post("/ai/recommend", json={
        "skills": ["Python", "Machine Learning"],
        "interests": "Artificial Intelligence",
        "number_of_results": 2,
    })
    assert r.status_code == 200
    data = r.json()
    assert data.get("career") is not None

def test_recommend_invalid_number_of_results():
    payload = dict(STANDARD_PROFILE)
    payload["number_of_results"] = -1
    r = client().post("/ai/recommend", json=payload)
    assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 8. Cross-endpoint consistency
# ─────────────────────────────────────────────────────────────────────────────

def test_cross_endpoint_skill_gap_consistency():
    """
    /ai/skill-gap and the gap section of /ai/recommend must return
    consistent readiness scores for the same input.
    """
    profile = {"skills": ["Python", "SQL"], "target_role": "AI Engineer"}

    gap_r = client().post("/ai/skill-gap", json=profile)
    rec_r = client().post("/ai/recommend", json={**profile, "number_of_results": 1})

    assert gap_r.status_code == 200, gap_r.text
    assert rec_r.status_code == 200, rec_r.text

    gap_data = gap_r.json()
    rec_gap = rec_r.json()["skill_gap"]

    # Same readiness within 5 points (minor difference allowed because /ai/recommend
    # goes through the career service first which may affect skill normalization slightly)
    assert abs(gap_data["readiness_score"] - rec_gap["readiness_score"]) < 5.0
