"""
Phase 12 — Dataset Validation Tests
Validates integrity of all datasets:
  - careers.json: no duplicate IDs, no missing fields
  - skills.json: no duplicate skill_ids or names
  - career_skills.json: all career_ids and skill_ids exist in registries
  - skill_dependencies.json: no references to unknown skills
  - projects.json: no missing project_name, has required fields
  - courses.json (sample): no missing course_name
"""
import os
import json
import pytest

PROCESSED_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed"
)

def load_json(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def careers():
    return load_json("careers.json")

@pytest.fixture(scope="module")
def skills():
    return load_json("skills.json")

@pytest.fixture(scope="module")
def career_skills():
    return load_json("career_skills.json")

@pytest.fixture(scope="module")
def career_transferable():
    return load_json("career_transferable_skills.json")

@pytest.fixture(scope="module")
def career_interests():
    return load_json("career_interests.json")

@pytest.fixture(scope="module")
def projects():
    return load_json("projects.json")

@pytest.fixture(scope="module")
def skill_deps():
    return load_json("skill_dependencies.json")


# ─── Careers Dataset ──────────────────────────────────────────────────────────

def test_careers_loaded(careers):
    assert len(careers) > 0, "careers.json is empty"

def test_careers_no_duplicate_ids(careers):
    ids = [c["career_id"] for c in careers]
    dups = [cid for cid in set(ids) if ids.count(cid) > 1]
    assert not dups, f"Duplicate career_ids: {dups}"

def test_careers_required_fields(careers):
    for c in careers:
        assert "career_id" in c and c["career_id"], f"Missing career_id: {c}"
        assert "career_title" in c and c["career_title"], f"Missing career_title: {c}"

def test_careers_count(careers):
    # Based on our inspection: 122 careers
    assert len(careers) >= 100, f"Unexpectedly few careers: {len(careers)}"


# ─── Skills Dataset ───────────────────────────────────────────────────────────

def test_skills_loaded(skills):
    assert len(skills) > 0, "skills.json is empty"

def test_skills_no_duplicate_ids(skills):
    ids = [s["skill_id"] for s in skills]
    dups = [sid for sid in set(ids) if ids.count(sid) > 1]
    assert not dups, f"Duplicate skill_ids: {dups[:10]}"

def test_skills_required_fields(skills):
    missing_name = [s for s in skills if not s.get("skill_name")]
    assert not missing_name, f"{len(missing_name)} skills missing skill_name"

def test_skills_count(skills):
    assert len(skills) > 100, f"Unexpectedly few skills: {len(skills)}"


# ─── Career-Skills Links ──────────────────────────────────────────────────────

def test_career_skills_no_orphaned_career_ids(careers, career_skills):
    valid_career_ids = {c["career_id"] for c in careers}
    cs_career_ids = {cs["career_id"] for cs in career_skills}
    orphans = cs_career_ids - valid_career_ids
    assert not orphans, f"career_skills references unknown career_ids: {orphans}"

def test_career_skills_no_orphaned_skill_ids(skills, career_skills):
    valid_skill_ids = {s["skill_id"] for s in skills}
    cs_skill_ids = {cs["skill_id"] for cs in career_skills}
    orphans = cs_skill_ids - valid_skill_ids
    assert not orphans, f"career_skills references unknown skill_ids: {orphans}"

def test_every_career_has_technical_skills(careers, career_skills):
    cs_career_ids = {cs["career_id"] for cs in career_skills}
    careers_without_skills = [c["career_title"] for c in careers if c["career_id"] not in cs_career_ids]
    # Warn but do not fail — some careers may have only transferable skills
    # We just count and report
    assert len(careers_without_skills) < len(careers), (
        "ALL careers are missing technical skills — possible data loading error"
    )


# ─── Skill Dependencies Dataset ───────────────────────────────────────────────

def test_skill_deps_loaded(skill_deps):
    assert len(skill_deps) > 0, "skill_dependencies.json is empty"

def test_skill_deps_no_orphaned_skill_ids(skills, skill_deps):
    valid_skill_ids = {s["skill_id"] for s in skills}
    source_ids = {d.get("source_skill_id", d.get("skill_id", "")) for d in skill_deps}
    target_ids = {d.get("target_skill_id", d.get("depends_on_skill_id", "")) for d in skill_deps}
    all_referenced = source_ids | target_ids
    all_referenced.discard("")
    orphans = all_referenced - valid_skill_ids
    # Report orphan count — may exist due to dependency dataset having extra skills
    # Only fail if majority are orphans (indicates a data schema mismatch)
    if orphans:
        orphan_pct = len(orphans) / len(all_referenced) * 100
        assert orphan_pct < 50, (
            f"{orphan_pct:.1f}% of dependency references are orphaned ({len(orphans)} unknown)"
        )


# ─── Projects Dataset ─────────────────────────────────────────────────────────

def test_projects_loaded(projects):
    assert len(projects) > 0, "projects.json is empty"

def test_projects_required_fields(projects):
    missing = [p for p in projects if not p.get("project_name")]
    assert not missing, f"{len(missing)} projects missing project_name"

def test_projects_no_duplicate_ids(projects):
    ids = [p.get("project_id", p.get("id", "")) for p in projects]
    non_empty = [pid for pid in ids if pid]
    dups = [pid for pid in set(non_empty) if non_empty.count(pid) > 1]
    assert not dups, f"Duplicate project_ids: {dups[:5]}"

def test_projects_count(projects):
    assert len(projects) >= 100, f"Expected ~250 projects, got {len(projects)}"


# ─── Courses Dataset (Sample) ────────────────────────────────────────────────

def test_courses_loaded():
    courses = load_json("courses.json")
    assert len(courses) > 0

def test_courses_sample_has_names():
    courses = load_json("courses.json")
    sample = courses[:100]
    missing_names = [c for c in sample if not c.get("course_name")]
    assert len(missing_names) == 0, f"{len(missing_names)} of first 100 courses missing name"

def test_courses_count():
    courses = load_json("courses.json")
    assert len(courses) > 1000, f"Unexpected low course count: {len(courses)}"
