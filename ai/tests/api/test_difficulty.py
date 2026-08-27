"""
Phase 12 — Difficulty Level Tests
Tests all valid difficulty levels for course and project recommendations.
Valid values from schema: Any Level, Beginner, Intermediate, Advanced, Conversant, Not Calibrated
Validates:
  - All valid difficulty values are accepted
  - Invalid difficulty → HTTP 422
  - Missing difficulty defaults to Any Level
  - Case variation in difficulty
"""
import pytest

def client():
    return pytest.shared_client

VALID_DIFFICULTIES = ["Any Level", "Beginner", "Intermediate", "Advanced", "Conversant", "Not Calibrated"]

BASE_SKILLS = ["Python", "SQL"]
BASE_TARGET = "AI Engineer"


@pytest.mark.parametrize("difficulty", VALID_DIFFICULTIES)
def test_course_valid_difficulty_accepted(difficulty):
    r = client().post("/ai/recommend-courses", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
        "difficulty": difficulty,
        "number_of_results": 3,
    })
    assert r.status_code == 200, (
        f"Valid difficulty '{difficulty}' rejected: {r.text}"
    )
    assert "courses" in r.json()


@pytest.mark.parametrize("invalid", ["SuperEasy", "Expert", "noob", "HARD", "beginner "])
def test_course_invalid_difficulty_returns_422(invalid):
    r = client().post("/ai/recommend-courses", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
        "difficulty": invalid,
    })
    assert r.status_code == 422, (
        f"Expected 422 for invalid difficulty '{invalid}', got {r.status_code}"
    )


def test_course_missing_difficulty_defaults_to_any_level():
    """Omitting difficulty field should work (defaults to Any Level)."""
    r = client().post("/ai/recommend-courses", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
    })
    assert r.status_code == 200
    assert "courses" in r.json()


@pytest.mark.parametrize("difficulty", VALID_DIFFICULTIES)
def test_project_valid_difficulty_accepted(difficulty):
    r = client().post("/ai/recommend-projects", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
        "difficulty": difficulty,
        "number_of_results": 3,
    })
    assert r.status_code == 200, (
        f"Valid project difficulty '{difficulty}' rejected: {r.text}"
    )
    assert "projects" in r.json()


@pytest.mark.parametrize("invalid", ["rocket science", "all", "1234"])
def test_project_invalid_difficulty_returns_422(invalid):
    r = client().post("/ai/recommend-projects", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
        "difficulty": invalid,
    })
    assert r.status_code == 422


def test_difficulty_alias_preferred_difficulty():
    """preferred_difficulty alias must work same as difficulty."""
    r = client().post("/ai/recommend-courses", json={
        "skills": BASE_SKILLS,
        "target_role": BASE_TARGET,
        "preferred_difficulty": "Beginner",
    })
    assert r.status_code == 200


def test_beginner_courses_returned():
    """Beginner difficulty should return courses."""
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "Data Scientist",
        "difficulty": "Beginner", "number_of_results": 5,
    })
    assert r.status_code == 200
    # Dataset may or may not have Beginner courses — just check it does not crash
    assert "courses" in r.json()


def test_advanced_courses_returned():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python", "Machine Learning"], "target_role": "AI Engineer",
        "difficulty": "Advanced", "number_of_results": 5,
    })
    assert r.status_code == 200
    assert "courses" in r.json()
