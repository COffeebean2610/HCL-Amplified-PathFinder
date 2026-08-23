import pytest
import networkx as nx
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.graph_validator import GraphValidator
from src.dependency.dependency_analyzer import DependencyAnalyzer
from src.dependency.prerequisite_resolver import PrerequisiteResolver

@pytest.fixture
def mock_graph_data():
    """Create a mock graph for testing resolver and validator logic in isolation."""
    class MockGraphObj:
        def __init__(self):
            # Define 5 mock skills
            self.skills = {
                "SK_001": {"skill_id": "SK_001", "skill_name": "Python", "skill_category": "Programming", "skill_type": "technical"},
                "SK_002": {"skill_id": "SK_002", "skill_name": "Maths", "skill_category": "Maths", "skill_type": "technical"},
                "SK_003": {"skill_id": "SK_003", "skill_name": "Machine Learning", "skill_category": "AI/ML", "skill_type": "technical"},
                "SK_004": {"skill_id": "SK_004", "skill_name": "Deep Learning", "skill_category": "AI/ML", "skill_type": "technical"},
                "SK_005": {"skill_id": "SK_005", "skill_name": "LLMs", "skill_category": "AI/ML", "skill_type": "technical"},
            }
            
            # Define dependencies
            self.dependencies = [
                # Python -> ML (required)
                {"dependency_id": "D_001", "source_skill_id": "SK_001", "source_skill_name": "Python", "target_skill_id": "SK_003", "target_skill_name": "Machine Learning", "relationship": "prerequisite", "reason": "Python is core.", "difficulty": "Beginner", "domain": "AI/ML"},
                # Maths -> ML (recommended)
                {"dependency_id": "D_002", "source_skill_id": "SK_002", "source_skill_name": "Maths", "target_skill_id": "SK_003", "target_skill_name": "Machine Learning", "relationship": "recommended_prerequisite", "reason": "Linear algebra helps.", "difficulty": "Intermediate", "domain": "AI/ML"},
                # ML -> DL (strong required)
                {"dependency_id": "D_003", "source_skill_id": "SK_003", "source_skill_name": "Machine Learning", "target_skill_id": "SK_004", "target_skill_name": "Deep Learning", "relationship": "strong_prerequisite", "reason": "DL needs ML foundation.", "difficulty": "Intermediate", "domain": "AI/ML"},
                # DL -> LLMs (required)
                {"dependency_id": "D_004", "source_skill_id": "SK_004", "source_skill_name": "Deep Learning", "target_skill_id": "SK_005", "target_skill_name": "LLMs", "relationship": "prerequisite", "reason": "Transformers are neural nets.", "difficulty": "Advanced", "domain": "AI/ML"},
            ]
            
            # Build DiGraph representation
            G = nx.DiGraph()
            for sid, s in self.skills.items():
                G.add_node(sid, skill_id=sid, canonical_name=s["skill_name"], display_name=s["skill_name"], skill_category=s["skill_category"], skill_type=s["skill_type"])
            for d in self.dependencies:
                G.add_edge(d["source_skill_id"], d["target_skill_id"], relationship=d["relationship"], reason=d["reason"], difficulty=d["difficulty"], domain=d["domain"], dependency_id=d["dependency_id"])
            self.graph = G
            self.processed_dir = "data/processed"
            self.career_skills_list = []
            self.career_trans_skills_list = []
            self.careers_dict = {}
            
        def get_graph(self):
            return self.graph
        def get_skills_dict(self):
            return self.skills
        def get_dependencies_list(self):
            return self.dependencies
            
    return MockGraphObj()

def test_graph_properties(mock_graph_data):
    G = mock_graph_data.get_graph()
    assert G.number_of_nodes() == 5
    assert G.number_of_edges() == 4
    assert G.has_edge("SK_001", "SK_003")

def test_analyzer_roots_leaves(mock_graph_data):
    analyzer = DependencyAnalyzer(mock_graph_data)
    roots = analyzer.get_root_skills()
    leaves = analyzer.get_leaf_skills()
    
    assert "SK_001" in roots
    assert "SK_002" in roots
    assert "SK_005" in leaves
    assert "SK_003" not in roots
    assert "SK_003" not in leaves

def test_resolver_direct_prereqs(mock_graph_data):
    resolver = PrerequisiteResolver(mock_graph_data)
    prereqs = resolver.get_direct_prerequisites("SK_003")
    
    required_ids = [p["skill_id"] for p in prereqs["required"]]
    recommended_ids = [p["skill_id"] for p in prereqs["recommended"]]
    
    assert "SK_001" in required_ids
    assert "SK_002" in recommended_ids
    assert len(required_ids) == 1
    assert len(recommended_ids) == 1

def test_resolver_transitive_prereqs(mock_graph_data):
    resolver = PrerequisiteResolver(mock_graph_data)
    prereqs = resolver.get_all_prerequisites("SK_005")
    
    required_ids = [p["skill_id"] for p in prereqs["required"]]
    recommended_ids = [p["skill_id"] for p in prereqs["recommended"]]
    
    # Transitive required: DL -> ML -> Python
    assert "SK_004" in required_ids  # DL
    assert "SK_003" in required_ids  # ML
    assert "SK_001" in required_ids  # Python
    
    # Transitive recommended: Maths (prereq of ML)
    assert "SK_002" in recommended_ids
    
    # Check topological order: Python (001) -> ML (003) -> DL (004)
    python_idx = required_ids.index("SK_001")
    ml_idx = required_ids.index("SK_003")
    dl_idx = required_ids.index("SK_004")
    assert python_idx < ml_idx
    assert ml_idx < dl_idx

def test_resolver_skill_gap(mock_graph_data):
    resolver = PrerequisiteResolver(mock_graph_data)
    # Target: LLMs (005)
    # Current: Python (001)
    # Missing: ML (003), DL (004), LLMs (005)
    gap = resolver.resolve_skill_gap(current_skills=["SK_001"], target_skills=["SK_005"])
    gap_ids = [g["skill_id"] for g in gap]
    
    assert "SK_003" in gap_ids
    assert "SK_004" in gap_ids
    assert "SK_005" in gap_ids
    assert "SK_001" not in gap_ids  # Owned
    assert gap_ids.index("SK_003") < gap_ids.index("SK_004")

def test_explain_dependency(mock_graph_data):
    resolver = PrerequisiteResolver(mock_graph_data)
    
    # Direct explanation
    direct_exp = resolver.explain_dependency("SK_001", "SK_003")
    assert direct_exp["is_direct"] is True
    assert "Python is core." in direct_exp["explanation"]
    
    # Transitive explanation
    trans_exp = resolver.explain_dependency("SK_001", "SK_005")
    assert trans_exp["is_direct"] is False
    assert trans_exp["is_dependent"] is True
    assert "Python" in trans_exp["explanation"]
    assert "LLMs" in trans_exp["explanation"]

def test_validator_cycles_and_loops(mock_graph_data, tmp_path):
    # Add a self-loop
    mock_graph_data.graph.add_edge("SK_005", "SK_005", relationship="prerequisite", reason="Self loop", difficulty="Beginner", domain="General", dependency_id="D_ERR_1")
    
    # Add a cycle
    mock_graph_data.graph.add_edge("SK_005", "SK_001", relationship="prerequisite", reason="Cycle", difficulty="Beginner", domain="General", dependency_id="D_ERR_2")
    
    validator = GraphValidator(mock_graph_data)
    is_valid, _ = validator.validate(report_dir=str(tmp_path))
    
    assert is_valid is False
