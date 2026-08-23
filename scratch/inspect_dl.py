import networkx as nx
import json
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver

graph_obj = SkillDependencyGraph()
resolver = PrerequisiteResolver(graph_obj)
G = resolver.G

dl_id = "SK_00257"
print("Deep Learning Node exists?", G.has_node(dl_id))
print("DL direct predecessors:")
for p in G.predecessors(dl_id):
    edge_data = G.get_edge_data(p, dl_id)
    print(f"  ID={p}, Name={resolver.skills.get(p, {}).get('skill_name')}, Rel={edge_data.get('relationship')}")

print("\nDL direct successors:")
for s in G.successors(dl_id):
    edge_data = G.get_edge_data(dl_id, s)
    print(f"  ID={s}, Name={resolver.skills.get(s, {}).get('skill_name')}, Rel={edge_data.get('relationship')}")
