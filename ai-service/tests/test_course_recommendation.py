"""
Phase 12 — Course Recommendation Tests
Tests course recommendations for all 4 student profiles.
Validates:
  - Courses returned for each profile
  - Course IDs and names are non-empty
  - relevance_score is in [0.0, 1.0]
  - Results are sorted correctly (descending relevance_score)
  - No duplicate course IDs in a single response
  - difficulty field is populated
  - url field is present
  - number_of_results parameter is respected
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
        "target_career": "Software Engineer",
        "preferred_difficulty": "Intermediate",
    },
    {
        "profile_id": "STU_B",
        "skills": ["Python", "NumPy", "Pandas", "SQL", "Git"],
        "interests": "Artificial Intelligence, Machine Learning, Generative AI",
        "target_career": "AI Engineer",
        "preferred_difficulty": "Intermediate",
    },
    {
        "profile_id": "STU_C",
        "skills": ["Python", "SQL", "Pandas", "Statistics", "Excel"],
        "interests": "Data Analysis, Machine Learning, Statistics",
        "target_career": "Data Scientist",
        "preferred_difficulty": "Any Level",
    },
    {
        "profile_id": "STU_D",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Transformers"],
        "interests": "Generative AI, LLMs, RAG, AI Agents",
        "target_career": "Generative AI Engineer",
        "preferred_difficulty": "Advanced",
    },
]


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_course_returns_results(profile):
    r = client().post("/ai/recommend-courses", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "target_role": profile["target_career"],
        "difficulty": profile["preferred_difficulty"],
        "number_of_results": 5,
    })
    assert r.status_code == 200, r.text
    data = r.json()
    assert "courses" in data
    assert "total" in data
    assert data["total"] > 0


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_course_scores_valid_range(profile):
    r = client().post("/ai/recommend-courses", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
        "difficulty": "Any Level",
        "number_of_results": 10,
    })
    assert r.status_code == 200
    for course in r.json()["courses"]:
        score = course["relevance_score"]
        assert isinstance(score, (int, float))
        assert math.isfinite(score), f"Score not finite: {score}"
        assert 0.0 <= score <= 1.0, f"Score out of [0,1]: {score}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_course_results_sorted_descending(profile):
    r = client().post("/ai/recommend-courses", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
        "difficulty": "Any Level",
        "number_of_results": 10,
    })
    assert r.status_code == 200
    scores = [c["relevance_score"] for c in r.json()["courses"]]
    assert scores == sorted(scores, reverse=True), f"Not sorted: {scores}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_course_no_duplicates(profile):
    r = client().post("/ai/recommend-courses", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
        "difficulty": "Any Level",
        "number_of_results": 10,
    })
    assert r.status_code == 200
    ids = [c["course_id"] for c in r.json()["courses"]]
    assert len(ids) == len(set(ids)), f"Duplicate course IDs: {ids}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_course_required_fields_present(profile):
    r = client().post("/ai/recommend-courses", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
        "difficulty": "Any Level",
        "number_of_results": 3,
    })
    assert r.status_code == 200
    for course in r.json()["courses"]:
        assert course.get("course_id"), "course_id is missing or empty"
        assert course.get("course_name"), "course_name is missing or empty"
        assert course.get("difficulty"), "difficulty is missing or empty"
        assert "url" in course
        assert "relevance_score" in course
        assert "reason" in course


def test_course_number_of_results_respected():
    for n in [1, 3, 5]:
        r = client().post("/ai/recommend-courses", json={
            "skills": ["Python"], "target_role": "AI Engineer",
            "difficulty": "Any Level", "number_of_results": n,
        })
        assert r.status_code == 200
        assert len(r.json()["courses"]) <= n, (
            f"Returned more courses than requested: {len(r.json()['courses'])} > {n}"
        )


def test_course_target_role_field_in_response():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "Any Level",
    })
    assert r.status_code == 200
    assert "target_role" in r.json()
