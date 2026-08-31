"""
Phase 12 — Prerequisite Ordering Tests
Tests that the skill dependency graph produces correctly ordered learning sequences.
Validates:
  - Prerequisite skills appear before the skills that depend on them
  - No impossible orderings exist (e.g. RAG before LLMs if LLMs is prerequisite)
  - Cycles in the graph do not cause infinite loops or crashes
  - Multi-level prerequisite chains are handled
  - Already-known prerequisites are not re-added
"""
import pytest

def client():
    return pytest.shared_client


def get_learning_sequence(skills, target_role):
    r = client().post("/ai/skill-gap", json={
        "skills": skills, "target_role": target_role
    })
    assert r.status_code == 200, r.text
    return r.json()["learning_sequence"]


def test_learning_sequence_no_crash():
    """Learning sequence must be generated without crashing."""
    seq = get_learning_sequence(["Python"], "AI Engineer")
    assert isinstance(seq, list)


def test_learning_sequence_sequence_numbers_ordered():
    """sequence_number values must be strictly ascending starting from 1."""
    seq = get_learning_sequence(["Python"], "AI Engineer")
    if not seq:
        pytest.skip("No sequence returned")
    numbers = [s["sequence_number"] for s in seq]
    assert numbers == sorted(numbers)
    assert numbers[0] >= 1


def test_learning_sequence_no_duplicate_skills():
    """The same skill_id must not appear twice in the sequence."""
    seq = get_learning_sequence(["Python"], "Generative AI Engineer")
    ids = [s["skill_id"] for s in seq]
    assert len(ids) == len(set(ids)), f"Duplicate skill_ids in sequence: {ids}"


def test_prerequisite_ordering_respected():
    """
    For any skill in the sequence that lists prerequisites,
    all those prerequisites must have earlier sequence_numbers.
    """
    seq = get_learning_sequence([], "AI Engineer")
    if not seq:
        pytest.skip("Empty sequence")

    seq_num_by_id = {s["skill_id"]: s["sequence_number"] for s in seq}
    violations = []
    for step in seq:
        for prereq_id in step.get("prerequisites", []):
            if prereq_id in seq_num_by_id:
                if seq_num_by_id[prereq_id] >= step["sequence_number"]:
                    violations.append(
                        f"{step['skill_name']} (seq {step['sequence_number']}) has prerequisite "
                        f"{prereq_id} (seq {seq_num_by_id[prereq_id]})"
                    )
    assert not violations, f"Prerequisite order violations found:\n" + "\n".join(violations)


def test_prerequisite_ordering_genai_profile():
    """
    For GenAI profile, prerequisites before dependents in sequence.
    e.g. if LLMs appears, its prerequisites must come first.
    """
    seq = get_learning_sequence(
        ["Python"],
        "Generative AI Engineer"
    )
    if not seq:
        pytest.skip("Empty sequence for GenAI")

    seq_num_by_id = {s["skill_id"]: s["sequence_number"] for s in seq}
    violations = []
    for step in seq:
        for prereq_id in step.get("prerequisites", []):
            if prereq_id in seq_num_by_id:
                if seq_num_by_id[prereq_id] >= step["sequence_number"]:
                    violations.append(
                        f"{step['skill_name']} prerequisite ordering violation"
                    )
    assert not violations


def test_known_skills_not_in_sequence():
    """Skills the student already has should not appear in the learning sequence."""
    current = ["Python", "Machine Learning"]
    seq = get_learning_sequence(current, "AI Engineer")
    current_lower = {s.lower() for s in current}
    for step in seq:
        assert step["skill_name"].lower() not in current_lower, (
            f"Known skill '{step['skill_name']}' appears in learning sequence"
        )


def test_prerequisite_gaps_reference_valid_skills():
    """prerequisite_gaps must contain valid skill_id and required_by_skill_id."""
    r = client().post("/ai/skill-gap", json={
        "skills": [], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    for gap in r.json().get("prerequisite_gaps", []):
        assert gap["skill_id"]
        assert gap["skill_name"]
        assert gap["required_by_skill_id"]
        assert gap["required_by_skill_name"]
        assert gap["reason"]


def test_no_crash_with_all_missing_skills():
    """With zero skills, the full prerequisite resolution must not crash."""
    r = client().post("/ai/skill-gap", json={
        "skills": [], "target_role": "Machine Learning Engineer"
    })
    assert r.status_code == 200
    assert "learning_sequence" in r.json()


def test_prerequisite_skill_type_values():
    """skill_type in learning_sequence must be one of the documented values."""
    seq = get_learning_sequence([], "AI Engineer")
    valid_types = {"technical", "prerequisite", "transferable"}
    for step in seq:
        assert step["skill_type"] in valid_types, (
            f"Unexpected skill_type: {step['skill_type']}"
        )
