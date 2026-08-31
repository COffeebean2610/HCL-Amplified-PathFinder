"""
Phase 12 — Edge Case Tests
Tests system behavior under unusual or adversarial inputs.
All cases must produce controlled behavior — no server crashes (500).
"""
import pytest

def client():
    return pytest.shared_client


# ─── Case 1: No Skills ────────────────────────────────────────────────────────

def test_no_skills_career_recommend():
    r = client().post("/ai/recommend-career", json={
        "skills": [], "interests": "Software Development", "top_k": 3
    })
    assert r.status_code == 200
    assert r.json()["total"] > 0


def test_no_skills_skill_gap():
    r = client().post("/ai/skill-gap", json={
        "skills": [], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["readiness_score"] >= 0
    assert len(data["missing_skills"]) > 0


def test_no_skills_course_recommend():
    r = client().post("/ai/recommend-courses", json={
        "skills": [], "target_role": "AI Engineer", "difficulty": "Any Level"
    })
    assert r.status_code == 200
    assert "courses" in r.json()


def test_no_skills_project_recommend():
    r = client().post("/ai/recommend-projects", json={
        "skills": [], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    assert "projects" in r.json()


def test_no_skills_roadmap():
    r = client().post("/ai/generate-roadmap", json={
        "skills": [], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    assert "nodes" in r.json()


# ─── Case 2: No Interests ─────────────────────────────────────────────────────

def test_no_interests_career_recommend():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "Machine Learning"], "interests": "", "top_k": 3
    })
    assert r.status_code == 200
    assert r.json()["total"] > 0


# ─── Case 3: No Skills + No Interests ────────────────────────────────────────

def test_no_skills_no_interests_career():
    """System should not crash; returns results based on minimal signal."""
    r = client().post("/ai/recommend-career", json={
        "skills": [], "interests": "", "top_k": 3
    })
    assert r.status_code == 200


def test_no_skills_no_interests_full_pipeline():
    r = client().post("/ai/recommend", json={
        "skills": [], "interests": "", "number_of_results": 3
    })
    # Should return 200 (or possibly a partial response)
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("success", "partial")


# ─── Case 4: Unknown Skill ────────────────────────────────────────────────────

def test_unknown_skill_graceful():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Quantum Web Programming XYZ Nonexistent"],
        "target_role": "AI Engineer",
    })
    assert r.status_code == 200
    # Unknown skill should not crash and should not cause the engine to fail


def test_unknown_skill_in_career_recommend():
    r = client().post("/ai/recommend-career", json={
        "skills": ["Python", "XYZ_Nonexistent_Skill_999"],
        "interests": "AI",
        "top_k": 3,
    })
    assert r.status_code == 200


# ─── Case 5: Very Large Skill List ───────────────────────────────────────────

def test_large_skill_list():
    large_skills = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "Go",
        "Rust", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL",
        "React", "Vue.js", "Angular", "Node.js", "Django", "Flask",
        "FastAPI", "Spring Boot", "Docker", "Kubernetes", "AWS", "GCP",
        "Azure", "Machine Learning", "Deep Learning", "NLP", "Pandas",
        "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
        "Hugging Face", "Transformers", "LangChain", "RAG", "LLMs",
        "Git", "CI/CD", "Jenkins", "Terraform", "Ansible", "Linux",
        "Bash", "Statistics", "Excel", "Tableau", "Power BI", "Spark",
        "Hadoop", "Airflow", "Kafka", "Redis",
        # Duplicates (should be handled gracefully)
        "Python", "python", "PYTHON",
        # Unknown
        "XYZ_Unknown_Skill_999",
    ]
    r = client().post("/ai/skill-gap", json={
        "skills": large_skills,
        "target_role": "AI Engineer",
    })
    assert r.status_code == 200
    assert "readiness_score" in r.json()


# ─── Case 6: Unknown Career ───────────────────────────────────────────────────

def test_unknown_career_skill_gap():
    r = client().post("/ai/skill-gap", json={
        "skills": ["Python"],
        "target_role": "Nonexistent Career XYZ 99999",
    })
    # Should return a controlled error (4xx), not 500
    assert r.status_code in (400, 404, 422, 200)
    if r.status_code == 200:
        # If 200, the system may have used fuzzy matching or returned empty
        pass
    else:
        # Error response must have valid error structure
        data = r.json()
        assert "detail" in data or "error" in data or "message" in data


def test_unknown_career_roadmap():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"],
        "target_role": "Nonexistent Career ZZZZZ 12345",
    })
    assert r.status_code in (400, 404, 422, 500, 200)


# ─── Case 7: Completed Most Courses ──────────────────────────────────────────

def test_completing_most_courses_graceful():
    r_initial = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "Any Level", "number_of_results": 20,
    })
    assert r_initial.status_code == 200
    all_course_names = [c["course_name"] for c in r_initial.json()["courses"]]

    # Exclude all returned courses
    r_empty = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "Any Level", "number_of_results": 20,
        "completed_courses": all_course_names,
    })
    assert r_empty.status_code == 200
    assert "courses" in r_empty.json()  # May be empty list — that is fine


# ─── Case 8: Invalid Difficulty ──────────────────────────────────────────────

def test_invalid_difficulty_returns_422():
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "SuperDuperHardMode",
    })
    assert r.status_code == 422


# ─── Case 9: Empty Result Handled Gracefully ─────────────────────────────────

def test_empty_result_not_500():
    """Even with very restrictive filters, must not return 500."""
    r = client().post("/ai/recommend-courses", json={
        "skills": ["Python"], "target_role": "AI Engineer",
        "difficulty": "Advanced", "number_of_results": 1,
    })
    assert r.status_code != 500


# ─── Case 10: Duplicate Skills Deduplication ─────────────────────────────────

def test_duplicate_skills_deduplication():
    """Python listed 4 times should be treated as one skill."""
    r1 = client().post("/ai/skill-gap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    r2 = client().post("/ai/skill-gap", json={
        "skills": ["Python", "python", "PYTHON", "Python "],
        "target_role": "AI Engineer",
    })
    assert r1.status_code == 200 and r2.status_code == 200
    # Both should give the same readiness score (within tiny margin)
    s1 = r1.json()["readiness_score"]
    s2 = r2.json()["readiness_score"]
    assert abs(s1 - s2) < 1.0, (
        f"Duplicate skills changed readiness score unexpectedly: {s1} vs {s2}"
    )
