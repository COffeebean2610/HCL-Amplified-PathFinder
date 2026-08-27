import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, patch

from src.hybrid_recommender.engine import HybridRecommender, recommend_hybrid
from src.hybrid_recommender.schemas import RecommendationRequest, RecommendationResponse
from recommender import CourseRecommender

@pytest.fixture(scope="module")
def recommender():
    """Cache hybrid recommender instance for testing."""
    return HybridRecommender()

# Test 1: Skill normalization
def test_skill_normalization(recommender):
    norm_ids = recommender.gap_engine.normalize_user_skills(["ML", "machine-learning"])
    assert "SK_00264" in norm_ids  # Machine Learning canonical ID

# Test 2: Career resolution
def test_career_resolution(recommender):
    c = recommender.gap_engine.get_career_by_id_or_title("AI Engineer")
    assert c is not None
    assert c["career_id"] == "CAR_003"

# Test 3: Skill-gap integration
def test_skill_gap_integration(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    # Target career required skills should list Machine Learning as gap
    assert "Machine Learning" in res.skill_gaps

# Test 4: Skill-match score
def test_skill_match_score(recommender):
    # A candidate teaching missing skills should get a positive skill_match_score
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    assert len(res.courses) > 0
    # At least one recommended course should teach a missing target skill
    assert any(c.skill_match_score > 0.0 for c in res.courses)

# Test 5: Semantic score
def test_semantic_score(recommender):
    # Course on web development should align with React interests
    req = RecommendationRequest(interests="React development", current_skills=[], target_career="Frontend Developer")
    res = recommender.recommend(req)
    assert len(res.courses) > 0
    assert res.courses[0].semantic_score > 0.0

# Test 6: Prerequisite score
def test_prerequisite_score(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    
    # A course requiring Python should be "Ready" (prerequisite_score = 1.0)
    # A course requiring Machine Learning (which is missing) should be lower / "Locked"
    for course in res.courses:
        if "Deep Learning" in course.course_name:
            # Requires Machine Learning (which is missing) -> Locked
            assert course.prerequisite_status == "Locked"

# Test 7: Difficulty score
def test_difficulty_score(recommender):
    # If student difficulty is Beginner, Beginner courses should get difficulty_score = 1.0
    # Advanced courses should get difficulty_score = 0.1
    req = RecommendationRequest(current_skills=[], target_career="AI Engineer", difficulty="Beginner")
    res = recommender.recommend(req)
    for c in res.courses:
        if c.course_difficulty == "Beginner":
            assert c.difficulty_score == 1.0
        elif c.course_difficulty == "Advanced":
            assert c.difficulty_score == 0.1

# Test 8: Completed-course filtering
def test_completed_course_filtering(recommender):
    # Ensure completed courses are not returned
    req = RecommendationRequest(
        current_skills=["Python"], 
        target_career="AI Engineer", 
        completed_courses=["Introduction to Machine Learning", "Machine Learning"]
    )
    res = recommender.recommend(req)
    titles = [c.course_name.lower().strip() for c in res.courses]
    assert "machine learning" not in titles

# Test 9: Score normalization
def test_score_normalization(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    for c in res.courses:
        assert 0.0 <= c.skill_match_score <= 1.0
        assert 0.0 <= c.semantic_score <= 1.0
        assert 0.0 <= c.prerequisite_score <= 1.0
        assert 0.0 <= c.difficulty_score <= 1.0
        assert 0.0 <= c.final_score <= 1.0

# Test 10: Weighted final score
def test_weighted_final_score(recommender):
    # Custom weights
    custom_weights = {
        "skill_match": 0.50,
        "semantic_similarity": 0.50,
        "prerequisite": 0.0,
        "difficulty": 0.0
    }
    req = RecommendationRequest(
        current_skills=["Python"], 
        target_career="AI Engineer",
        weights=custom_weights
    )
    res = recommender.recommend(req)
    for c in res.courses:
        expected = 0.5 * c.skill_match_score + 0.5 * c.semantic_score
        assert pytest.approx(c.final_score, abs=1e-4) == expected

# Test 11: Duplicate candidate removal
def test_duplicate_candidate_removal(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    course_ids = [c.course_id for c in res.courses]
    assert len(course_ids) == len(set(course_ids))

# Test 12: Prerequisite ordering
def test_prerequisite_ordering(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    # Verify that Machine Learning (prerequisite) ranks higher than Deep Learning (dependent)
    ml_rank = None
    dl_rank = None
    for idx, c in enumerate(res.courses):
        if "Machine Learning" in c.course_name and "Deep" not in c.course_name:
            ml_rank = idx
        if "Deep Learning" in c.course_name:
            dl_rank = idx
            
    if ml_rank is not None and dl_rank is not None:
        assert ml_rank < dl_rank

# Test 13: No current skills
def test_no_current_skills(recommender):
    req = RecommendationRequest(current_skills=[], target_career="AI Engineer")
    res = recommender.recommend(req)
    assert len(res.courses) > 0

# Test 14: No skill gaps
def test_no_skill_gaps(recommender):
    # If student knows all skills, matching count should handle cleanly
    req = RecommendationRequest(
        current_skills=["Python", "Machine Learning", "Deep Learning", "Docker", "PyTorch", "TensorFlow", "SQL", "Git", "REST APIs", "Large Language Models", "Generative AI"], 
        target_career="AI Engineer"
    )
    res = recommender.recommend(req)
    assert len(res.courses) > 0

# Test 15: All courses completed
def test_all_courses_completed(recommender):
    # Make completed list equal to all candidate titles
    all_titles = [c["course_name"] for c in recommender.courses_list]
    req = RecommendationRequest(
        current_skills=["Python"],
        target_career="AI Engineer",
        completed_courses=all_titles[:1000]  # large block
    )
    res = recommender.recommend(req)
    # Will drop completed, still returns some if not all match
    assert isinstance(res.courses, list)

# Test 16: Unknown skill
def test_unknown_skill(recommender):
    req = RecommendationRequest(current_skills=["Python", "FakeUltraSkill"], target_career="AI Engineer")
    res = recommender.recommend(req)
    assert len(res.courses) > 0

# Test 17: No candidates
def test_no_candidates(recommender):
    # Mock candidate retrieval to return empty
    with patch.object(recommender, "_retrieve_course_candidates", return_value=[]):
        req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
        res = recommender.recommend(req)
        assert len(res.courses) == 0

# Test 18: API validation
def test_api_validation():
    # Verify request validation works
    with pytest.raises(ValidationError):
        RecommendationRequest(interests=["AI"], current_skills="Python", target_career=123)

# Test 19: API response structure
def test_api_response_structure(recommender):
    req = RecommendationRequest(current_skills=["Python"], target_career="AI Engineer")
    res = recommender.recommend(req)
    assert isinstance(res, RecommendationResponse)
    assert hasattr(res.career, "career_id")
    assert hasattr(res.career, "career_title")
    assert hasattr(res.career, "career_match")

def test_tfidf_vs_hybrid_comparison(recommender):
    # Run recommend using our legacy wrapper on the course recommender object (TF-IDF vs Hybrid)
    # Let's verify that the wrapper delegates successfully
    # Set up payload
    from recommender import CourseRecommender
    from model import load_model
    vectorizer, tfidf_matrix, similarity_matrix, df = load_model('model/')
    legacy_rec = CourseRecommender(vectorizer, tfidf_matrix, similarity_matrix, df)
    
    # 1. Hybrid recommendation
    res_hybrid = legacy_rec.recommend(
        interests="deep learning",
        user_skills=["Python"],
        target_career="AI Engineer",
        top_n=3
    )
    
    # 2. Legacy recommendation (target_career is None)
    res_legacy = legacy_rec.recommend(
        interests="deep learning",
        user_skills=["Python"],
        top_n=3
    )
    
    assert len(res_hybrid) > 0
    assert len(res_legacy) > 0
    # The hybrid results contain prerequisite score and reasons
    assert "prerequisite_score" in res_hybrid[0]
    assert "reason" in res_hybrid[0]
    # Legacy results do NOT contain prerequisite score
    assert "prerequisite_score" not in res_legacy[0]
