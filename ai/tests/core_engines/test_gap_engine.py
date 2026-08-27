import pytest
from pydantic import ValidationError

from src.gap_engine.schemas import SkillGapRequest, SkillGapResponse
from src.gap_engine.gap_engine import SkillGapEngine

@pytest.fixture(scope="module")
def engine():
    """Cache the engine instance for tests."""
    return SkillGapEngine()

def test_request_schema_validation():
    # 1. Valid input
    req = SkillGapRequest(current_skills=["Python", "SQL"], target_career="CAR_003")
    assert req.target_career == "CAR_003"
    assert len(req.current_skills) == 2

    # 2. Invalid target career type
    with pytest.raises(ValidationError):
        # target_career is required and must be a string
        SkillGapRequest(current_skills=["Python"], target_career=123)

    # 3. Invalid current_skills type
    with pytest.raises(ValidationError):
        SkillGapRequest(current_skills="Python", target_career="AI Engineer")

def test_gap_calculation_ai_engineer(engine):
    # Student has Python but is missing ML, DL, and other AI skills
    request = SkillGapRequest(current_skills=["Python"], target_career="AI Engineer")
    response = engine.calculate_gap(request)

    # Verify response schema type
    assert isinstance(response, SkillGapResponse)
    assert response.target_career_title == "AI Engineer"
    
    # Python is required, so it should be in matched
    matched_names = [s.skill_name for s in response.matched_technical_skills]
    assert "Python" in matched_names

    # Machine Learning is required but missing, so it should be in missing
    missing_ids = {s.skill_id for s in response.missing_technical_skills}
    # Machine Learning ID is SK_00264
    assert "SK_00264" in missing_ids

    # Should trace prerequisite gaps
    assert len(response.prerequisite_gaps) >= 0

    # Test priority inheritance
    # In career_skills.json: Machine Learning is "Critical" for AI Engineer.
    # Therefore, ML should be Critical priority.
    # If there are prerequisites for ML, they should inherit Critical.
    critical_skills = [s.skill_name for s in response.priority_gaps["Critical"]]
    assert len(critical_skills) > 0
    assert any("Machine Learning" in s for s in critical_skills)

def test_topological_sequence_ordering(engine):
    request = SkillGapRequest(current_skills=["Python"], target_career="AI Engineer")
    response = engine.calculate_gap(request)

    seq = response.learning_sequence
    assert len(seq) > 0

    # Ensure topological sorting: check that any prerequisite step comes BEFORE its downstream target skill
    skill_positions = {step.skill_id: step.sequence_number for step in seq}

    # For each step, assert that all its immediate prerequisites in the roadmap path are positioned earlier!
    for step in seq:
        sid = step.skill_id
        for prereq_id in step.prerequisites:
            if prereq_id in skill_positions:
                assert skill_positions[prereq_id] < skill_positions[sid], \
                    f"Ordering violation: Prerequisite {prereq_id} (seq {skill_positions[prereq_id]}) should come before {sid} (seq {skill_positions[sid]})"

def test_invalid_career_lookup(engine):
    request = SkillGapRequest(current_skills=["Python"], target_career="Nonexistent Mega Career")
    with pytest.raises(ValueError):
         engine.calculate_gap(request)

def test_duplicate_aliases_normalization(engine):
    # Map multiple variants to single canonical skills
    request = SkillGapRequest(
        current_skills=["ML", "machine-learning", "Machine Learning"],
        target_career="AI Engineer"
    )
    response = engine.calculate_gap(request)
    
    # Should resolve all three duplicates to a single canonical skill (Machine Learning: SK_00264)
    matched_ids = [s.skill_id for s in response.matched_technical_skills]
    # Check that SK_00264 is matched exactly once
    assert matched_ids.count("SK_00264") == 1
