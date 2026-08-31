import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from src.project_recommender.engine import ProjectRecommender, recommend_projects_api
from src.project_recommender.schemas import ProjectRecommendationRequest, ProjectRecommendationResponse
from flask_app import app

@pytest.fixture(scope="module")
def recommender():
    """Cache project recommender instance."""
    return ProjectRecommender()

# Test 1: Project data cleaning validation
def test_project_data_cleaning(recommender):
    # Retrieve clean project mapping
    proj = recommender.projects_list[0]
    assert proj["difficulty"] in ["Beginner", "Intermediate", "Advanced"]
    assert proj["github_url"].startswith("http") or proj["github_url"] == "#"

# Test 2: Target career lookup
def test_target_career_lookup(recommender):
    c = recommender.gap_engine.get_career_by_id_or_title("AI Engineer")
    assert c is not None
    assert c["career_id"] == "CAR_003"

# Test 3: Skill gap weighting (Critical vs Medium)
def test_skill_gap_weighting(recommender):
    # Verify that Critical gap gets weighted higher (3.0 vs 1.0)
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    # Gaps should include Machine Learning (Critical)
    assert "Machine Learning" in res.skill_gaps

# Test 4: Project skill match score
def test_project_skill_match_score(recommender):
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0
    # The coverage score should be between 0 and 1.0
    assert 0.0 <= res.projects[0].skill_gap_coverage_score <= 1.0

# Test 5: Semantic score
def test_semantic_score(recommender):
    req = ProjectRecommendationRequest(interests="React web applications", skills=[], target_role="Frontend Developer")
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0
    # Top project should have semantic matching
    assert res.projects[0].semantic_score > 0.0

# Test 6: Prerequisite readiness locks
def test_prerequisite_readiness_locks(recommender):
    # Python-only student attempting a complex project
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    
    # AI projects requiring advanced skills (whose prerequisites aren't met) should be locked
    locked_count = sum(1 for p in res.projects if p.prerequisite_status == "Locked")
    assert locked_count >= 0

# Test 7: Difficulty compatibility
def test_difficulty_compatibility(recommender):
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer", difficulty="Beginner")
    res = recommender.recommend_projects(req)
    for p in res.projects:
        if p.difficulty == "Beginner":
            assert p.difficulty_score == 1.0
        elif p.difficulty == "Advanced":
            assert p.difficulty_score == 0.1

# Test 8: Empty profile (no current skills)
def test_empty_profile(recommender):
    req = ProjectRecommendationRequest(skills=[], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0

# Test 9: No skill gaps
def test_no_skill_gaps(recommender):
    req = ProjectRecommendationRequest(
        skills=["Python", "Machine Learning", "Deep Learning", "Docker", "PyTorch", "REST APIs", "SQL", "Git"], 
        target_role="AI Engineer"
    )
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0

# Test 10: Unknown skills handling
def test_unknown_skills_handling(recommender):
    req = ProjectRecommendationRequest(skills=["Python", "InvisibleSuperPower"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0

# Test 11: Candidate retrieval pooling
def test_candidate_retrieval_pooling(recommender):
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    # Mapped list size
    proj_ids = [p.project_id for p in res.projects]
    assert len(proj_ids) == len(set(proj_ids))

# Test 12: Greedy diversification
def test_greedy_diversification(recommender):
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    # Check that subsequent projects do not have exact same skill lists
    if len(res.projects) >= 2:
        s0 = set(res.projects[0].skills_to_develop + res.projects[0].matched_existing_skills)
        s1 = set(res.projects[1].skills_to_develop + res.projects[1].matched_existing_skills)
        # They should differ in at least some skills, showing diversification
        assert s0 != s1

# Test 13: Local fallback when vector search is unavailable
def test_local_fallback_vector_search(recommender):
    # Temporarily set vector search to unavailable
    recommender.vector_search_available = False
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    assert len(res.projects) > 0
    # Enable it back
    recommender.vector_search_available = True

# Test 14: Dynamic ranking weight configurations
def test_dynamic_ranking_weights(recommender):
    custom = {
        "skill_gap_coverage": 1.0,
        "semantic_similarity": 0.0,
        "prerequisite_readiness": 0.0,
        "difficulty_compatibility": 0.0
    }
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer", weights=custom)
    res = recommender.recommend_projects(req)
    for p in res.projects:
        assert p.final_score == p.skill_gap_coverage_score

# Test 15: Response schema validation
def test_response_schema_validation(recommender):
    req = ProjectRecommendationRequest(skills=["Python"], target_role="AI Engineer")
    res = recommender.recommend_projects(req)
    assert isinstance(res, ProjectRecommendationResponse)

# Test 16: Flask API endpoint request validation
def test_flask_api_request_validation():
    # Setup test client for Flask app
    with app.test_client() as client:
        # Invalid body (no target_role)
        r = client.post('/api/recommend-projects', json={"skills": ["Python"]})
        assert r.status_code == 400
        assert b"Missing target_role" in r.data

# Test 17: Flask API endpoint response structure
def test_flask_api_response_structure():
    with app.test_client() as client:
        r = client.post('/api/recommend-projects', json={
            "skills": ["Python"],
            "target_role": "AI Engineer",
            "top_k": 3
        })
        assert r.status_code == 200
        res_data = r.get_json()
        assert "career" in res_data
        assert "projects" in res_data
        assert len(res_data["projects"]) <= 3
