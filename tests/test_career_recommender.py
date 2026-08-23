import pytest
from src.career_recommender.recommender import CareerRecommender

@pytest.fixture(scope="module")
def recommender():
    """Build and cache single recommender instance for the test suite."""
    return CareerRecommender()

def test_ai_oriented_learner(recommender):
    profile = {
        "interests": "I enjoy artificial intelligence, machine learning and building intelligent applications.",
        "current_skills": ["Python", "SQL", "Machine Learning"],
        "transferable_skills": ["Problem Solving", "Analytical Thinking"],
        "target_career": None,
        "top_k": 3
    }
    output = recommender.recommend(profile)
    
    assert "recommendations" in output
    recs = output["recommendations"]
    assert len(recs) > 0
    
    # Check that AI/ML careers are in top recommendations
    top_titles = [r["career"].lower() for r in recs]
    assert any("ai" in t or "machine learning" in t or "data" in t for t in top_titles)
    assert recs[0]["confidence"] == "High"

def test_web_developer(recommender):
    profile = {
        "interests": "I enjoy web design, frontend interface construction, building reactive web sites and HTML markup.",
        "current_skills": ["HTML", "CSS", "JavaScript", "React"],
        "transferable_skills": ["Communication"],
        "target_career": None,
        "top_k": 3
    }
    output = recommender.recommend(profile)
    recs = output["recommendations"]
    
    top_titles = [r["career"].lower() for r in recs]
    assert any("frontend" in t or "web" in t or "software developer" in t for t in top_titles)

def test_data_oriented_learner(recommender):
    profile = {
        "interests": "I enjoy databases, data warehousing, statistics, data pipelines, and analytics.",
        "current_skills": ["Python", "SQL", "Pandas", "Statistics"],
        "transferable_skills": ["Problem Solving"],
        "target_career": None,
        "top_k": 3
    }
    output = recommender.recommend(profile)
    recs = output["recommendations"]
    
    top_titles = [r["career"].lower() for r in recs]
    assert any("data" in t or "analyst" in t or "database" in t for t in top_titles)

def test_interest_heavy_profile(recommender):
    # Passions are provided but absolutely no skills are supplied
    profile = {
        "interests": "I want to research deep neural networks, computer vision, transformers, and build generative AI models.",
        "current_skills": [],
        "transferable_skills": [],
        "target_career": None,
        "top_k": 3
    }
    output = recommender.recommend(profile)
    recs = output["recommendations"]
    
    # Recommendations should still load successfully
    assert len(recs) == 3
    # Tech match score should be 0.0, but interest match should be positive
    assert recs[0]["score_breakdown"]["technical_skill_match"] == 0.0
    assert recs[0]["score_breakdown"]["interest_match"] > 0.0
    
    # Confidence level should be Low or Medium due to zero skill inputs
    assert recs[0]["confidence"] in ["Medium", "Low"]

def test_skill_heavy_profile(recommender):
    # User provides skills but absolutely no interest information
    profile = {
        "interests": "",
        "current_skills": ["Python", "SQL", "Machine Learning"],
        "transferable_skills": ["Problem Solving"],
        "target_career": None,
        "top_k": 3
    }
    output = recommender.recommend(profile)
    recs = output["recommendations"]
    
    assert len(recs) == 3
    # Tech match should be high, interest match should be 0.0
    assert recs[0]["score_breakdown"]["technical_skill_match"] > 0.0
    assert recs[0]["score_breakdown"]["interest_match"] == 0.0

def test_unknown_skill(recommender):
    profile = {
        "interests": "software developer",
        "current_skills": ["Python", "NonexistentFakeMegaSkillXYZ", "SQL"],
        "transferable_skills": [],
        "target_career": None,
        "top_k": 2
    }
    # Should run successfully without crashing
    output = recommender.recommend(profile)
    assert len(output["recommendations"]) == 2

def test_target_career(recommender):
    profile = {
        "interests": "I enjoy training deep learning models, natural language processing and neural networks.",
        "current_skills": ["Python"],
        "transferable_skills": [],
        "target_career": "AI Engineer", # Target career specified
        "top_k": 2
    }
    output = recommender.recommend(profile)
    
    assert "target_career_evaluation" in output
    target = output["target_career_evaluation"]
    assert target is not None
    assert "target_fit_score" in target
    assert "recommended_alternatives" in target
    assert len(target["prerequisite_gaps"]) > 0  # Should trace prerequisite gaps for AI Engineer required skills

def test_duplicate_skill_aliases(recommender):
    profile = {
        "interests": "machine learning developer",
        "current_skills": ["ML", "machine-learning", "Machine Learning"],
        "transferable_skills": [],
        "target_career": None,
        "top_k": 2
    }
    output = recommender.recommend(profile)
    detected_skills = output["profile_summary"]["skills_detected"]
    
    # Should resolve all three duplicate aliases to the single canonical skill ID and name
    # Total unique detected skills should be 1
    assert len(detected_skills) == 1
    assert detected_skills[0] == "Machine Learning"
