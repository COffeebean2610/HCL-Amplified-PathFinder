import networkx as nx
import json
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver

graph_obj = SkillDependencyGraph()
resolver = PrerequisiteResolver(graph_obj)
G = resolver.G

ml_id = "SK_00264"
print("Machine Learning Node exists?", G.has_node(ml_id))
print("ML direct predecessors:")
for p in G.predecessors(ml_id):
    edge_data = G.get_edge_data(p, ml_id)
    print(f"  ID={p}, Name={resolver.skills.get(p, {}).get('skill_name')}, Rel={edge_data.get('relationship')}")

python_id = "SK_00360"
print("\nPython Node exists?", G.has_node(python_id))
print("Python direct successors:")
for s in G.successors(python_id):
    edge_data = G.get_edge_data(python_id, s)
    print(f"  ID={s}, Name={resolver.skills.get(s, {}).get('skill_name')}, Rel={edge_data.get('relationship')}")
