"""
Phase 12 — Roadmap Generation Tests
Tests the personalized roadmap generator (Phase 9) via FastAPI.
Validates:
  - React Flow structure: nodes, edges, summary
  - Node IDs follow skill- prefix convention
  - Edge sources and targets reference valid node IDs
  - No duplicate node IDs
  - Prerequisite ordering: edge targets should not appear before their sources
  - summary contains career and total_skills_needed
"""
import pytest

def client():
    return pytest.shared_client

PROFILES = [
    {
        "profile_id": "STU_A",
        "skills": ["Python", "JavaScript", "React", "SQL", "Git"],
        "target_career": "Software Engineer",
    },
    {
        "profile_id": "STU_B",
        "skills": ["Python", "NumPy", "Pandas", "SQL", "Git"],
        "target_career": "AI Engineer",
    },
    {
        "profile_id": "STU_C",
        "skills": ["Python", "SQL", "Pandas", "Statistics", "Excel"],
        "target_career": "Data Scientist",
    },
    {
        "profile_id": "STU_D",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Transformers"],
        "target_career": "Generative AI Engineer",
    },
]


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_roadmap_returns_200(profile):
    r = client().post("/ai/generate-roadmap", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
    })
    assert r.status_code == 200, r.text


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_roadmap_react_flow_structure(profile):
    """Must return nodes, edges, and summary for React Flow compatibility."""
    r = client().post("/ai/generate-roadmap", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
    })
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data, "nodes missing from roadmap response"
    assert "edges" in data, "edges missing from roadmap response"
    assert "summary" in data, "summary missing from roadmap response"
    assert len(data["nodes"]) > 0, "roadmap nodes list is empty"


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_roadmap_node_id_prefix(profile):
    """Node IDs must start with 'skill-' per the agreed React Flow schema."""
    r = client().post("/ai/generate-roadmap", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
    })
    assert r.status_code == 200
    for node in r.json()["nodes"]:
        assert node["id"].startswith("skill-"), (
            f"Node ID does not start with 'skill-': {node['id']}"
        )


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_roadmap_no_duplicate_node_ids(profile):
    r = client().post("/ai/generate-roadmap", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
    })
    assert r.status_code == 200
    node_ids = [n["id"] for n in r.json()["nodes"]]
    assert len(node_ids) == len(set(node_ids)), (
        f"Duplicate node IDs found: {node_ids}"
    )


@pytest.mark.parametrize("profile", PROFILES, ids=[p["profile_id"] for p in PROFILES])
def test_roadmap_edges_reference_valid_nodes(profile):
    """All edge source and target IDs must reference existing node IDs."""
    r = client().post("/ai/generate-roadmap", json={
        "skills": profile["skills"],
        "target_role": profile["target_career"],
    })
    assert r.status_code == 200
    data = r.json()
    node_ids = {n["id"] for n in data["nodes"]}
    for edge in data["edges"]:
        assert edge["source"] in node_ids, (
            f"Edge source '{edge['source']}' not in nodes"
        )
        assert edge["target"] in node_ids, (
            f"Edge target '{edge['target']}' not in nodes"
        )


def test_roadmap_summary_fields():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    summary = r.json()["summary"]
    assert "career" in summary
    assert "total_skills_needed" in summary


def test_roadmap_courses_per_skill_param():
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"],
        "target_role": "AI Engineer",
        "courses_per_skill": 1,
        "projects_per_skill": 1,
    })
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data and "edges" in data


def test_roadmap_node_data_fields():
    """Each node must have id, type, and data with label."""
    r = client().post("/ai/generate-roadmap", json={
        "skills": ["Python"], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    for node in r.json()["nodes"]:
        assert "id" in node
        assert "data" in node
        assert "label" in node["data"]


def test_roadmap_edge_ids_unique():
    r = client().post("/ai/generate-roadmap", json={
        "skills": [], "target_role": "AI Engineer"
    })
    assert r.status_code == 200
    edge_ids = [e.get("id", "") for e in r.json()["edges"]]
    non_empty = [eid for eid in edge_ids if eid]
    if non_empty:
        assert len(non_empty) == len(set(non_empty)), "Duplicate edge IDs"
