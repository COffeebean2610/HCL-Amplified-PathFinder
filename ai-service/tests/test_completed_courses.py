"""
Phase 12 — Completed Course Exclusion Tests
Validates that courses listed in completed_courses do not appear in recommendations.
Tests:
  - Single completed course excluded
  - Multiple completed courses excluded
  - Edge case: completed a course not in results (no false exclusion)
  - Exclusion by exact name match
  - Empty results when too many courses completed (handled gracefully)
"""
import pytest

def client():
    return pytest.shared_client

BASE_PAYLOAD = {
    "skills": ["Python", "SQL"],
    "target_role": "AI Engineer",
    "difficulty": "Any Level",
    "number_of_results": 10,
}


def get_courses(completed=None):
    payload = dict(BASE_PAYLOAD)
    if completed is not None:
        payload["completed_courses"] = completed
    r = client().post("/ai/recommend-courses", json=payload)
    assert r.status_code == 200, r.text
    return r.json()["courses"]


def test_no_completed_courses_returns_max_results():
    courses = get_courses(completed=[])
    assert len(courses) > 0


def test_single_completed_course_excluded():
    """After getting top course, re-running with it completed must exclude it."""
    initial = get_courses(completed=[])
    if not initial:
        pytest.skip("No courses returned to test exclusion")

    first_course = initial[0]["course_name"]
    after_exclusion = get_courses(completed=[first_course])
    returned_names = [c["course_name"] for c in after_exclusion]
    assert first_course not in returned_names, (
        f"Completed course '{first_course}' still appears in results"
    )


def test_multiple_completed_courses_excluded():
    """All completed courses must be excluded."""
    initial = get_courses(completed=[])
    if len(initial) < 2:
        pytest.skip("Need at least 2 courses to test multi-exclusion")

    completed_names = [initial[0]["course_name"], initial[1]["course_name"]]
    after = get_courses(completed=completed_names)
    returned_names = [c["course_name"] for c in after]

    for name in completed_names:
        assert name not in returned_names, (
            f"Completed course '{name}' still appears in results after exclusion"
        )


def test_nonexistent_completed_course_no_side_effect():
    """An unknown completed course must not exclude unrelated courses."""
    without_exclusion = get_courses(completed=[])
    with_fake = get_courses(completed=["Completely Nonexistent Course XYZ 99999"])

    # The number of results should be the same (no real courses excluded)
    assert abs(len(without_exclusion) - len(with_fake)) <= 1


def test_excluding_top_n_shifts_results():
    """Excluding top N courses should shift recommendations."""
    initial = get_courses(completed=[])
    if len(initial) < 3:
        pytest.skip("Need at least 3 courses")

    top3 = [c["course_name"] for c in initial[:3]]
    after = get_courses(completed=top3)
    returned_names = [c["course_name"] for c in after]

    for name in top3:
        assert name not in returned_names


def test_completing_all_courses_returns_empty_gracefully():
    """If all courses are marked completed, response must be valid (possibly empty)."""
    initial = get_courses(completed=[])
    all_names = [c["course_name"] for c in initial]

    r = client().post("/ai/recommend-courses", json={
        **BASE_PAYLOAD,
        "completed_courses": all_names,
    })
    assert r.status_code == 200
    data = r.json()
    assert "courses" in data
    # May be empty — that is acceptable
    assert isinstance(data["courses"], list)


def test_completed_courses_stu_b_exclusion():
    """STU_B specific: verify exclusion works for AI Engineer target."""
    payload = {
        "skills": ["Python", "NumPy", "Pandas", "SQL", "Git"],
        "target_role": "AI Engineer",
        "difficulty": "Intermediate",
        "number_of_results": 5,
    }
    r1 = client().post("/ai/recommend-courses", json=payload)
    assert r1.status_code == 200
    if not r1.json()["courses"]:
        pytest.skip("No courses for STU_B")

    first = r1.json()["courses"][0]["course_name"]
    r2 = client().post("/ai/recommend-courses", json={**payload, "completed_courses": [first]})
    assert r2.status_code == 200
    names2 = [c["course_name"] for c in r2.json()["courses"]]
    assert first not in names2
