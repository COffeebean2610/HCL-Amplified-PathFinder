import os
import json
import pandas as pd
import networkx as nx

def export_graph_to_json(skill_graph_obj, filepath="data/processed/skill_graph.json"):
    """Export nodes and links to a structured JSON format."""
    G = skill_graph_obj.get_graph()
    skills = skill_graph_obj.get_skills_dict()
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    nodes = []
    for node in G.nodes():
        node_attrs = G.nodes[node]
        nodes.append({
            "id": node,
            "name": node_attrs.get("canonical_name", "Unknown"),
            "category": node_attrs.get("skill_category", "Other"),
            "type": node_attrs.get("skill_type", "other")
        })
        
    links = []
    for u, v, attrs in G.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "relationship": attrs.get("relationship", "prerequisite"),
            "reason": attrs.get("reason", ""),
            "difficulty": attrs.get("difficulty", "Intermediate"),
            "domain": attrs.get("domain", "General"),
            "dependency_id": attrs.get("dependency_id", "")
        })
        
    data = {
        "nodes": nodes,
        "links": links
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"SUCCESS: Exported graph JSON to '{filepath}'")
    return filepath

def export_graph_to_csv(skill_graph_obj, filepath="data/processed/skill_dependencies_processed.csv"):
    """Export edges to a flattened CSV format representing processed dependencies."""
    G = skill_graph_obj.get_graph()
    skills = skill_graph_obj.get_skills_dict()
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    records = []
    for u, v, attrs in G.edges(data=True):
        records.append({
            "dependency_id": attrs.get("dependency_id", ""),
            "source_skill_id": u,
            "source_skill_name": skills.get(u, {}).get("skill_name", "Unknown"),
            "target_skill_id": v,
            "target_skill_name": skills.get(v, {}).get("skill_name", "Unknown"),
            "relationship": attrs.get("relationship", "prerequisite"),
            "reason": attrs.get("reason", ""),
            "difficulty": attrs.get("difficulty", "Intermediate"),
            "domain": attrs.get("domain", "General")
        })
        
    df = pd.DataFrame(records)
    # Sort by dependency_id for consistency
    if not df.empty and "dependency_id" in df.columns:
        df.sort_values(by="dependency_id", inplace=True)
        
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"SUCCESS: Exported dependency CSV to '{filepath}'")
    return filepath

def export_graph_to_graphml(skill_graph_obj, filepath="data/processed/skill_graph.graphml"):
    """Export the directed graph using GraphML format for software like Gephi."""
    G = skill_graph_obj.get_graph()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # NetworkX write_graphml requires string attributes
    # We create a copy and convert node/edge attributes to standard types
    G_temp = nx.DiGraph()
    
    for node in G.nodes():
        node_attrs = G.nodes[node]
        G_temp.add_node(
            node,
            label=node_attrs.get("canonical_name", "Unknown"),
            category=node_attrs.get("skill_category", "Other"),
            type=node_attrs.get("skill_type", "other")
        )
        
    for u, v, attrs in G.edges(data=True):
        G_temp.add_edge(
            u,
            v,
            relationship=attrs.get("relationship", "prerequisite"),
            reason=attrs.get("reason", ""),
            difficulty=attrs.get("difficulty", "Intermediate"),
            domain=attrs.get("domain", "General"),
            dependency_id=attrs.get("dependency_id", "")
        )
        
    nx.write_graphml(G_temp, filepath)
    print(f"SUCCESS: Exported GraphML to '{filepath}'")
    return filepath
