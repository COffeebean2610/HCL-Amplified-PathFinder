"""
Phase 12 — API Validation Tests
Tests all endpoints for correct HTTP status, schema compliance, and error handling.
Endpoints:
  GET  /health
  GET  /ready
  POST /ai/recommend-career
  POST /ai/skill-gap
  POST /ai/recommend-courses
  POST /ai/recommend-projects
  POST /ai/generate-roadmap
  POST /ai/recommend
"""
import pytest

def client():
    return pytest.shared_client


# ─── Health ───────────────────────────────────────────────────────────────────

def test_api_health_status_200():
    r = client().get("/health")
    assert r.status_code == 200

def test_api_health_schema():
    r = client().get("/health")
    data = r.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert data["status"] == "healthy"

def test_api_ready_status_200():
    r = client().get("/ready")
    assert r.status_code == 200


# ─── Career Recommendation API ───────────────────────────────────────────────

def test_api_career_200():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 3
    })
    assert r.status_code == 200

def test_api_career_response_schema():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 3
    })
    data = r.json()
    assert "recommendations" in data
    assert "total" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["recommendations"], list)

def test_api_career_item_schema():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "Machine Learning"], "interests": "AI", "top_k": 1
    })
    item = r.json()["recommendations"][0]
    required = ["career_id", "career_title", "match_score", "technical_match_score", "reason"]
    for field in required:
        assert field in item, f"Missing field: {field}"

def test_api_career_top_k_zero_returns_422():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 0
    })
    assert r.status_code == 422

def test_api_career_top_k_too_large_returns_422():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 100
    })
    assert r.status_code == 422


# ─── Skill Gap API ───────────────────────────────────────────────────────────

def test_api_skill_gap_200():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200

def test_api_skill_gap_response_schema():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    required = ["career", "readiness_score", "missing_skills", "matched_skills", "learning_sequence"]
    for field in required:
        assert field in data, f"Missing field: {field}"

def test_api_skill_gap_career_schema():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    career = r.json()["career"]
    assert "career_id" in career
    assert "career_title" in career

def test_api_skill_gap_missing_target_returns_422():
    r = client().post("/ai/skill-gap", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_api_skill_gap_empty_body_returns_422():
    r = client().post("/ai/skill-gap", json={})
    assert r.status_code == 422


# ─── Course Recommendation API ───────────────────────────────────────────────

def test_api_courses_200():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200

def test_api_courses_response_schema():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "courses" in data
    assert "total" in data
    assert "target_role" in data

def test_api_courses_item_schema():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 1
    })
    if not r.json()["courses"]:
        pytest.skip("No courses returned")
    item = r.json()["courses"][0]
    required = ["course_id", "course_name", "difficulty", "url", "relevance_score", "reason"]
    for field in required:
        assert field in item, f"Missing course field: {field}"

def test_api_courses_invalid_difficulty_422():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer", "difficulty": "GOD_MODE"
    })
    assert r.status_code == 422

def test_api_courses_missing_target_role_422():
    r = client().post("/ai/recommend-courses", json={"skills": ["Python"]})
    assert r.status_code == 422

def test_api_courses_number_of_results_boundary():
    # number_of_results must be >= 1
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 0
    })
    assert r.status_code == 422


# ─── Project Recommendation API ──────────────────────────────────────────────

def test_api_projects_200():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200

def test_api_projects_response_schema():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "projects" in data
    assert "total" in data

def test_api_projects_item_schema():
    r = client().post("/ai/recommend-projects", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 1
    })
    if not r.json()["projects"]:
        pytest.skip("No projects returned")
    item = r.json()["projects"][0]
    required = ["project_id", "project_name", "difficulty", "relevance_score"]
    for field in required:
        assert field in item, f"Missing project field: {field}"

def test_api_projects_missing_target_role_422():
    r = client().post("/ai/recommend-projects", json={"skills": ["Python"]})
    assert r.status_code == 422


# ─── Roadmap API ─────────────────────────────────────────────────────────────

def test_api_roadmap_200():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200

def test_api_roadmap_response_schema():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    data = r.json()
    assert "nodes" in data
    assert "edges" in data
    assert "summary" in data

def test_api_roadmap_missing_target_role_422():
    r = client().post("/ai/generate-roadmap", json={"skills": ["Python"]})
    assert r.status_code == 422


# ─── Unified Recommendation API ──────────────────────────────────────────────

def test_api_recommend_200():
    r = client().post("/ai/recommend", json={
        "skills": ["Python", "SQL"],
        "interests": "AI",
        "target_role": "AI Engineer",
        "difficulty": "Intermediate",
        "number_of_results": 3,
    })
    assert r.status_code == 200

def test_api_recommend_response_schema():
    r = client().post("/ai/recommend", json={
        "skills": ["Python"], "interests": "AI",
        "target_role": "AI Engineer", "number_of_results": 2,
    })
    data = r.json()
    required = ["status", "profile", "career", "skill_gap", "courses", "projects"]
    for field in required:
        assert field in data, f"Missing field in /ai/recommend response: {field}"

def test_api_recommend_status_values():
    r = client().post("/ai/recommend", json={
        "skills": ["Python"], "interests": "AI",
        "target_role": "AI Engineer", "number_of_results": 2,
    })
    assert r.json()["status"] in ("success", "partial")

def test_api_recommend_invalid_number_of_results_422():
    r = client().post("/ai/recommend", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "number_of_results": -5,
    })
    assert r.status_code == 422

def test_api_recommend_skill_gap_section_schema():
    r = client().post("/ai/recommend", json={
        "skills": ["Python"], "target_role": "AI Engineer", "number_of_results": 2
    })
    assert r.status_code == 200
    sg = r.json()["skill_gap"]
    assert "readiness_score" in sg
    assert "missing_skills" in sg
    assert "matched_skills" in sg
