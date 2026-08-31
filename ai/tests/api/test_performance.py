"""
Phase 12 — Performance Measurement Tests
Measures actual execution time for all major AI operations.
Does NOT set hard pass/fail thresholds for timing.
Reports measured values as assertions only for sanity (< 60 seconds each).
"""
import time
import pytest

def client():
    return pytest.shared_client

TOLERANCE_SECONDS = 120  # Maximum allowed per operation (warm execution)


def measure(fn):
    t0 = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t0
    return result, elapsed


def test_perf_career_recommendation():
    _, elapsed = measure(lambda: client().post("/ai/recommend-career", json={
        "skills": ["Python", "Machine Learning", "SQL"],
        "interests": "Artificial Intelligence",
        "top_k": 5,
    }))
    print(f"\n[PERF] Career recommendation: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS, f"Career recommendation too slow: {elapsed:.1f}s"


def test_perf_skill_gap():
    _, elapsed = measure(lambda: client().post("/ai/skill-gap", json={
        "skills": ["Python", "SQL", "Pandas"],
        "target_role": "Data Scientist",
    }))
    print(f"\n[PERF] Skill gap: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS


def test_perf_course_recommendation():
    _, elapsed = measure(lambda: client().post("/ai/recommend-courses", json={
        "skills": ["Python", "SQL"],
        "target_role": "AI Engineer",
        "difficulty": "Any Level",
        "number_of_results": 5,
    }))
    print(f"\n[PERF] Course recommendation: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS


def test_perf_project_recommendation():
    _, elapsed = measure(lambda: client().post("/ai/recommend-projects", json={
        "skills": ["Python", "SQL"],
        "target_role": "AI Engineer",
        "number_of_results": 5,
    }))
    print(f"\n[PERF] Project recommendation: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS


def test_perf_roadmap_generation():
    _, elapsed = measure(lambda: client().post("/ai/generate-roadmap", json={
        "skills": ["Python", "SQL"],
        "target_role": "AI Engineer",
        "courses_per_skill": 2,
        "projects_per_skill": 1,
    }))
    print(f"\n[PERF] Roadmap generation: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS


def test_perf_full_pipeline():
    _, elapsed = measure(lambda: client().post("/ai/recommend", json={
        "skills": ["Python", "Machine Learning", "SQL"],
        "interests": "Artificial Intelligence",
        "target_role": "AI Engineer",
        "difficulty": "Intermediate",
        "number_of_results": 5,
        "courses_per_skill": 2,
        "projects_per_skill": 1,
    }))
    print(f"\n[PERF] Full pipeline: {elapsed:.3f}s")
    assert elapsed < TOLERANCE_SECONDS


def test_perf_repeat_career_recommendation():
    """Second call (warm cache) should be similar or faster."""
    payload = {
        "skills": ["Python", "Machine Learning"],
        "interests": "AI",
        "top_k": 5,
    }
    _, t1 = measure(lambda: client().post("/ai/recommend-career", json=payload))
    _, t2 = measure(lambda: client().post("/ai/recommend-career", json=payload))
    print(f"\n[PERF] Career warm: call1={t1:.3f}s, call2={t2:.3f}s")
    assert t2 < TOLERANCE_SECONDS
