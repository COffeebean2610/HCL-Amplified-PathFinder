"""
Phase 12 — Career Recommendation Tests
Tests career recommendations for all 4 student profiles.
Validates:
  - Responses are returned for all profiles
  - Career IDs and titles are valid (non-empty)
  - Match scores are numeric, finite, and in [0, 100]
  - Results are sorted correctly (descending match_score)
  - No duplicate career IDs in results
  - Sanity: AI profile should rank AI-oriented careers in top 5
  - Determinism: same input produces same output
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
    },
    {
        "profile_id": "STU_B",
        "skills": ["Python", "NumPy", "Pandas", "SQL", "Git"],
        "interests": "Artificial Intelligence, Machine Learning, Generative AI",
        "target_career": "AI Engineer",
    },
    {
        "profile_id": "STU_C",
        "skills": ["Python", "SQL", "Pandas", "Statistics", "Excel"],
        "interests": "Data Analysis, Machine Learning, Statistics",
        "target_career": "Data Scientist",
    },
    {
        "profile_id": "STU_D",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Transformers"],
        "interests": "Generative AI, LLMs, RAG, AI Agents",
        "target_career": "Generative AI Engineer",
    },
]

AI_CAREERS = {
    "AI Engineer", "Machine Learning Engineer", "Data Scientist",
    "Generative AI Engineer", "MLOps Engineer", "NLP Engineer",
    "Machine Learning Researcher", "AI Ethics Researcher",
    "Computer Vision Engineer", "AI Product Manager",
}

SDE_CAREERS = {
    "Software Engineer", "Backend Developer", "Full Stack Developer",
    "Frontend Developer", "Tech Lead",
}


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_career_recommend_returns_results(profile):
    r = client().post("/ai/recommend-career", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "top_k": 5,
    })
    assert r.status_code == 200, r.text
    data = r.json()
    assert "recommendations" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["recommendations"]) == data["total"]


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_career_scores_valid_range(profile):
    r = client().post("/ai/recommend-career", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "top_k": 10,
    })
    assert r.status_code == 200
    for item in r.json()["recommendations"]:
        score = item["match_score"]
        assert isinstance(score, (int, float)), f"Score is not numeric: {score}"
        assert math.isfinite(score), f"Score is not finite: {score}"
        assert 0.0 <= score <= 100.0, f"Score out of [0,100]: {score}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_career_results_sorted_descending(profile):
    r = client().post("/ai/recommend-career", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "top_k": 10,
    })
    assert r.status_code == 200
    scores = [item["match_score"] for item in r.json()["recommendations"]]
    assert scores == sorted(scores, reverse=True), f"Scores not sorted: {scores}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_career_no_duplicate_ids(profile):
    r = client().post("/ai/recommend-career", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "top_k": 15,
    })
    assert r.status_code == 200
    ids = [item["career_id"] for item in r.json()["recommendations"]]
    assert len(ids) == len(set(ids)), f"Duplicate career IDs found: {ids}"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_career_items_have_required_fields(profile):
    r = client().post("/ai/recommend-career", json={
        "skills": profile["skills"],
        "interests": profile["interests"],
        "top_k": 3,
    })
    assert r.status_code == 200
    for item in r.json()["recommendations"]:
        assert "career_id" in item and item["career_id"]
        assert "career_title" in item and item["career_title"]
        assert "match_score" in item
        assert "reason" in item


def test_career_ai_profile_sanity():
    """AI-focused profile should include AI-oriented careers in top 5."""
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "Machine Learning", "Deep Learning"],
        "interests": "Artificial Intelligence, Machine Learning",
        "top_k": 5,
    })
    assert r.status_code == 200
    titles = {item["career_title"] for item in r.json()["recommendations"]}
    overlap = titles & AI_CAREERS
    assert len(overlap) > 0, (
        f"Expected AI careers in top 5, got: {titles}"
    )


def test_career_sde_profile_sanity():
    """SDE-focused profile should include software-related careers in top 5."""
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
        "interests": "Software Development, Web Development",
        "top_k": 5,
    })
    assert r.status_code == 200
    titles = {item["career_title"] for item in r.json()["recommendations"]}
    overlap = titles & SDE_CAREERS
    assert len(overlap) > 0, (
        f"Expected SDE careers in top 5, got: {titles}"
    )


def test_career_determinism():
    """Same input must produce identical results on consecutive calls."""
    payload = {
        "skills": ["Python", "Machine Learning", "SQL"],
        "interests": "Artificial Intelligence",
        "top_k": 5,
    }
    r1 = client().post("/ai/recommend-career", json=payload)
    r2 = client().post("/ai/recommend-career", json=payload)
    assert r1.status_code == 200 and r2.status_code == 200
    ids1 = [i["career_id"] for i in r1.json()["recommendations"]]
    ids2 = [i["career_id"] for i in r2.json()["recommendations"]]
    assert ids1 == ids2, f"Non-deterministic results: {ids1} vs {ids2}"


def test_career_technical_match_score_field():
    """technical_match_score must exist and be in [0,100]."""
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python"], "interests": "AI", "top_k": 3,
    })
    assert r.status_code == 200
    for item in r.json()["recommendations"]:
        score = item.get("technical_match_score")
        assert score is not None, "technical_match_score field missing"
        assert 0.0 <= score <= 100.0


def test_career_top_k_respected():
    for k in [1, 3, 5]:
        r = client().post("/ai/recommend-career", json={
            "skills": ["Python"], "interests": "AI", "top_k": k,
        })
        assert r.status_code == 200
        assert r.json()["total"] <= k


def test_career_empty_skills_returns_results():
    """Career recommendation with no skills should still return results (interest-only)."""
    r = client().post("/ai/recommend-career", json={
        "skills": [],
        "interests": "Artificial Intelligence, Machine Learning",
        "top_k": 3,
    })
    assert r.status_code == 200
    assert r.json()["total"] > 0
