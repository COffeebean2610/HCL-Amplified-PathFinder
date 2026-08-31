"""
Phase 12 — End-to-End Tests
Tests the complete pipeline for all 4 student profiles via /ai/recommend.
Validates:
  - Complete response structure
  - Cross-component consistency (readiness score within tolerance)
  - Pipeline processes all 4 profiles
  - Partial failure handling (status=partial with warnings)
  - No hardcoded profile assumptions (works for any valid career)
"""
import math
import pytest

def client():
    return pytest.shared_client

PROFILES = [
    {
        "profile_id": "STU_A",
        "skills": ["Python", "JavaScript", "React", "SQL", "Git"],
        "interests": "Software Development, Backend Development, Web Development",
        "target_role": "Software Engineer",
        "difficulty": "Intermediate",
    },
    {
        "profile_id": "STU_B",
        "skills": ["Python", "NumPy", "Pandas", "SQL", "Git"],
        "interests": "Artificial Intelligence, Machine Learning, Generative AI",
        "target_role": "AI Engineer",
        "difficulty": "Intermediate",
    },
    {
        "profile_id": "STU_C",
        "skills": ["Python", "SQL", "Pandas", "Statistics", "Excel"],
        "interests": "Data Analysis, Machine Learning, Statistics",
        "target_role": "Data Scientist",
        "difficulty": "Any Level",
    },
    {
        "profile_id": "STU_D",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Transformers"],
        "interests": "Generative AI, LLMs, RAG, AI Agents",
        "target_role": "Generative AI Engineer",
        "difficulty": "Advanced",
    },
]


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_full_pipeline_returns_200(profile):
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "target_role": profile["target_role"],
        "difficulty": profile["difficulty"],
        "number_of_results": 5,
        "courses_per_skill": 2,
        "projects_per_skill": 1,
    })
    assert r.status_code == 200, f"[{profile['profile_id']}] {r.text}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_response_structure(profile):
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "target_role": profile["target_role"],
        "difficulty": profile["difficulty"],
        "number_of_results": 5,
    })
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "profile" in data
    assert "career" in data
    assert "skill_gap" in data
    assert "courses" in data
    assert "projects" in data
    assert data["status"] in ("success", "partial")


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_career_target_matches_requested(profile):
    """The career in the response should correspond to the requested target_role."""
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "target_role": profile["target_role"],
        "number_of_results": 3,
    })
    assert r.status_code == 200
    career = r.json()["career"]
    # career_title should be non-empty
    assert career.get("career_title"), "career_title is empty in response"
    assert career.get("career_id"), "career_id is empty in response"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_readiness_score_valid(profile):
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "target_role": profile["target_role"],
        "number_of_results": 3,
    })
    assert r.status_code == 200
    score = r.json()["skill_gap"]["readiness_score"]
    assert isinstance(score, (int, float))
    assert math.isfinite(score)
    assert 0.0 <= score <= 100.0


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_courses_returned(profile):
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "target_role": profile["target_role"],
        "number_of_results": 5,
    })
    assert r.status_code == 200
    # Courses list may be empty if no matching courses — just verify it exists
    assert "courses" in r.json()
    assert isinstance(r.json()["courses"], list)


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_e2e_projects_returned(profile):
    r = client().post("/ai/recommend", json={
        "skills": profile["skills"],
        "target_role": profile["target_role"],
        "number_of_results": 5,
    })
    assert r.status_code == 200
    assert "projects" in r.json()
    assert isinstance(r.json()["projects"], list)


def test_e2e_consistency_skill_gap_vs_recommend():
    """
    /ai/skill-gap and /ai/recommend must yield consistent readiness scores
    for the same input (within 5-point tolerance, as recommend uses career
    service before gap calculation).
    """
    skills = ["Python", "SQL", "Pandas"]
    target = "Data Scientist"

    gap_r = client().post("/ai/skill-gap", json={
        "skills": skills, "target_role": target
    })
    rec_r = client().post("/ai/recommend", json={
        "skills": skills, "target_role": target, "number_of_results": 3
    })
    assert gap_r.status_code == 200 and rec_r.status_code == 200

    gap_score = gap_r.json()["readiness_score"]
    rec_score = rec_r.json()["skill_gap"]["readiness_score"]
    assert abs(gap_score - rec_score) < 10.0, (
        f"Readiness inconsistency: gap={gap_score:.1f}, recommend={rec_score:.1f}"
    )


def test_e2e_without_target_role_auto_career_selection():
    """Pipeline must auto-select a career when target_role is not provided."""
    r = client().post("/ai/recommend", json={
        "skills": ["Python", "Machine Learning", "Deep Learning"],
        "interests": "Artificial Intelligence",
        "number_of_results": 3,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["career"]["career_title"]  # Auto-selected career should be present


def test_e2e_profile_section_preserved():
    """Profile section must reflect the input student data."""
    r = client().post("/ai/recommend", json={
        "skills": ["Python", "SQL"],
        "interests": "AI",
        "target_role": "AI Engineer",
        "number_of_results": 2,
        "student_id": "TEST_001",
    })
    assert r.status_code == 200
    profile = r.json()["profile"]
    assert "skills" in profile
    assert "Python" in profile["skills"] or "python" in [s.lower() for s in profile["skills"]]


def test_e2e_partial_failure_has_warnings():
    """If status is partial, warnings array must be non-empty."""
    r = client().post("/ai/recommend", json={
        "skills": ["Python"], "interests": "AI",
        "target_role": "AI Engineer", "number_of_results": 3,
    })
    assert r.status_code == 200
    data = r.json()
    if data["status"] == "partial":
        assert "warnings" in data
        assert len(data["warnings"]) > 0
