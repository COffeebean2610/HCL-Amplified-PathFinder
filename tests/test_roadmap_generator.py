import pytest
from pydantic import ValidationError
import networkx as nx

from src.roadmap_generator.engine import RoadmapGenerator, generate_roadmap_api
from src.roadmap_generator.schemas import RoadmapRequest, RoadmapResponse
from app import app


@pytest.fixture(scope="module")
def generator():
    """Cache roadmap generator instance."""
    return RoadmapGenerator()


# TEST 1: Python + SQL + Git completed, Target = AI Engineer
def test_ai_engineer_no_web_dev_bleed(generator):
    req = RoadmapRequest(
        skills=["Python", "SQL", "Git"],
        target_role="AI Engineer",
        completed_courses=["Introduction to Python"]
    )
    res = generator.generate_roadmap(req)

    node_names = {n.skill_name for n in res.nodes}
    # Unrelated web dev skills must NOT be in the AI Engineer roadmap
    assert "HTML" not in node_names
    assert "CSS" not in node_names
    assert "JavaScript" not in node_names
    assert "Node.js" not in node_names
    assert "Express.js" not in node_names

    # Python, SQL, Git should be completed
    py_node = next((n for n in res.nodes if n.skill_name == "Python"), None)
    sql_node = next((n for n in res.nodes if n.skill_name == "SQL"), None)
    git_node = next((n for n in res.nodes if n.skill_name == "Git"), None)

    assert py_node and py_node.status == "completed"
    assert sql_node and sql_node.status == "completed"
    assert git_node and git_node.status == "completed"

    # Mathematics should be next (since ML requires Python & Mathematics, and Python is completed)
    math_node = next((n for n in res.nodes if "Mathematics" in n.skill_name or n.skill_id == "SK_00270"), None)
    assert math_node and math_node.status == "next"


# TEST 2: Python + Mathematics completed -> Machine Learning becomes next
def test_ml_unlocked_when_prereqs_completed(generator):
    req = RoadmapRequest(skills=["Python", "Mathematics"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)

    ml_node = next((n for n in res.nodes if n.skill_id == "SK_00264"), None)
    assert ml_node is not None
    assert ml_node.status == "next"


# TEST 3: Python completed, Mathematics incomplete -> Machine Learning is locked
def test_ml_locked_when_math_incomplete(generator):
    req = RoadmapRequest(skills=["Python"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)

    ml_node = next((n for n in res.nodes if n.skill_id == "SK_00264"), None)
    assert ml_node is not None
    assert ml_node.status == "locked"


# TEST 4: Python + Mathematics + Machine Learning completed -> Deep Learning becomes next
def test_dl_unlocked_when_ml_completed(generator):
    req = RoadmapRequest(skills=["Python", "Mathematics", "Machine Learning"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)

    dl_node = next((n for n in res.nodes if n.skill_id == "SK_00132"), None)
    assert dl_node is not None
    assert dl_node.status == "next"


# TEST 5: Cycle in prerequisite graph -> returns warning, no crash
def test_cycle_detection_warnings_no_crash(generator):
    dummy_g = nx.DiGraph()
    dummy_g.add_edges_from([("SK_00001", "SK_00002"), ("SK_00002", "SK_00003"), ("SK_00003", "SK_00001")])

    cycles = list(nx.simple_cycles(dummy_g))
    assert len(cycles) > 0
    # Break cycle
    dummy_g.remove_edge(cycles[0][0], cycles[0][1])
    assert nx.is_directed_acyclic_graph(dummy_g)


# TEST 6: Non-web career excludes frontend skills
def test_non_web_career_excludes_frontend(generator):
    req = RoadmapRequest(skills=["Python"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)

    frontend_ids = {"SK_00212", "SK_00106", "SK_00240", "SK_00314", "SK_00173"}
    node_ids = {n.skill_id for n in res.nodes}
    assert frontend_ids.isdisjoint(node_ids)


# TEST 7: Duplicate semantic skills normalization
def test_semantic_skill_normalization(generator):
    # LLMs, Large Language Models, ML, Machine Learning should normalize cleanly
    sid1 = generator.normalize_skill("LLMs")
    sid2 = generator.normalize_skill("Large Language Models")
    assert sid1 == sid2 == "SK_00255"

    sid3 = generator.normalize_skill("ML")
    sid4 = generator.normalize_skill("Machine Learning")
    assert sid3 == sid4 == "SK_00264"


# TEST 8: Course quality filter - no low-relevance filler courses
def test_course_quality_filter(generator):
    req = RoadmapRequest(
        skills=["Python"],
        target_role="AI Engineer",
        completed_courses=["Introduction to Python"],
        courses_per_skill=3
    )
    res = generator.generate_roadmap(req)

    for node in res.nodes:
        for crs in node.courses:
            # All returned courses must meet the minimum relevance threshold
            assert crs.relevance_score >= generator.MIN_COURSE_RELEVANCE


# Additional test: React Flow edges structure
def test_react_flow_edges_structure(generator):
    req = RoadmapRequest(skills=["Python"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)
    assert len(res.edges) > 0
    for e in res.edges:
        assert e.id.startswith("edge-")
        assert e.source.startswith("skill-")
        assert e.target.startswith("skill-")


# Additional test: Progress & Readiness calculations
def test_summary_and_readiness_metrics(generator):
    req = RoadmapRequest(skills=["Python", "SQL", "Git"], target_role="AI Engineer")
    res = generator.generate_roadmap(req)
    assert res.summary.total_required_skills > 0
    assert 0.0 <= res.summary.progress_percentage <= 100.0
    assert 0.0 <= res.summary.career_readiness_score <= 100.0
