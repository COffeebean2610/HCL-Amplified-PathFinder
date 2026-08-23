import os
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.graph_validator import GraphValidator
from src.dependency.dependency_analyzer import DependencyAnalyzer
from src.dependency.graph_export import export_graph_to_json, export_graph_to_csv, export_graph_to_graphml

def run_pipeline(processed_dir="data/processed", reports_dir="data/reports"):
    """
    Run the complete Skill Dependency Graph pipeline:
    - Build graph
    - Run validation and generate validation report
    - Run topological analysis and generate analysis report
    - Export JSON, CSV, and GraphML outputs
    """
    print("STARTING ROUTEMASTER SKILL DEPENDENCY PIPELINE...")
    
    # 1. Build Graph
    print("Building Skill Dependency Graph...")
    graph_obj = SkillDependencyGraph(processed_dir=processed_dir, force_rebuild=True)
    G = graph_obj.get_graph()
    print(f"  Graph constructed: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # 2. Validate Graph
    print("Executing dependency graph validation checks...")
    validator = GraphValidator(graph_obj)
    is_valid, val_report = validator.validate(report_dir=reports_dir)
    
    # 3. Analyze Graph
    print("Executing topological and centrality analysis...")
    analyzer = DependencyAnalyzer(graph_obj)
    analysis_report = analyzer.generate_analysis_report(report_dir=reports_dir)
    
    # 4. Export Graph Files
    print("Exporting machine-readable graph representations...")
    export_graph_to_json(graph_obj, filepath=os.path.join(processed_dir, "skill_graph.json"))
    export_graph_to_csv(graph_obj, filepath=os.path.join(processed_dir, "skill_dependencies_processed.csv"))
    export_graph_to_graphml(graph_obj, filepath=os.path.join(processed_dir, "skill_graph.graphml"))
    
    # Summary Prints
    roots = analyzer.get_root_skills()
    leaves = analyzer.get_leaf_skills()
    
    print("\n" + "="*50)
    print("SKILL DEPENDENCY PIPELINE COMPLETE")
    print("="*50)
    print(f"Overall Status: {'PASSED' if is_valid else 'FAILED (warnings/errors logged)'}")
    print(f"Total Nodes: {G.number_of_nodes()} skills")
    print(f"Total Edges: {G.number_of_edges()} prerequisites")
    print(f"Foundational (Root) Skills: {len(roots)}")
    print(f"Advanced (Leaf) Skills: {len(leaves)}")
    print(f"Validation Report: '{val_report}'")
    print(f"Analysis Report: '{analysis_report}'")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_pipeline()
