import os
import json
import networkx as nx

class DependencyAnalyzer:
    """
    Analyzes the topological structure, connectivity, depths, and impact metrics
    of the Skill Dependency Graph.
    """
    def __init__(self, skill_graph_obj):
        self.graph_obj = skill_graph_obj
        self.G = skill_graph_obj.get_graph()
        self.skills = skill_graph_obj.get_skills_dict()

    def get_root_skills(self):
        """Root skills: No incoming dependencies, but have outgoing dependencies (excludes orphans)."""
        roots = []
        for node in self.G.nodes():
            if self.G.in_degree(node) == 0 and self.G.out_degree(node) > 0:
                roots.append(node)
        return sorted(roots)

    def get_leaf_skills(self):
        """Leaf skills: Have incoming dependencies, but no outgoing dependencies (excludes orphans)."""
        leaves = []
        for node in self.G.nodes():
            if self.G.out_degree(node) == 0 and self.G.in_degree(node) > 0:
                leaves.append(node)
        return sorted(leaves)

    def get_connected_components(self):
        """Get weakly connected components of the dependency graph (ignoring isolated orphans)."""
        # Create a subgraph excluding isolated orphan nodes
        connected_nodes = [node for node in self.G.nodes() if self.G.in_degree(node) > 0 or self.G.out_degree(node) > 0]
        subgraph = self.G.subgraph(connected_nodes)
        components = list(nx.weakly_connected_components(subgraph))
        return components

    def calculate_depths_and_impact(self):
        """
        Calculate depth, transitive prerequisites, and downstream impact for each skill.
        Only required relations ('prerequisite' and 'strong_prerequisite') are considered.
        """
        # Create a subgraph containing only required edges for strict depth/chain calculations
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)
        
        depths = {}
        # Pre-calculate depths recursively or topologically in G_req
        try:
            topo_order = list(nx.topological_sort(G_req))
            for node in topo_order:
                in_edges = list(G_req.in_edges(node))
                if not in_edges:
                    depths[node] = 0
                else:
                    depths[node] = 1 + max(depths[parent] for parent, _ in in_edges)
        except nx.NetworkXUnfeasible:
            # Graph has cycles, fallback to simple BFS or 0
            for node in G_req.nodes():
                depths[node] = 0
                
        metrics = {}
        for node in self.G.nodes():
            # Standard metrics based on the full graph
            direct_prereqs = list(self.G.predecessors(node))
            direct_dependents = list(self.G.successors(node))
            
            # Transitive metrics based on required subgraph
            total_prereqs = len(nx.ancestors(G_req, node))
            total_dependents = len(nx.descendants(G_req, node))
            
            name = self.skills.get(node, {}).get("skill_name", "Unknown")
            metrics[node] = {
                "skill_id": node,
                "skill_name": name,
                "depth": depths.get(node, 0),
                "direct_prereqs_count": len(direct_prereqs),
                "total_prereqs_count": total_prereqs,
                "direct_dependents_count": len(direct_dependents),
                "downstream_impact_count": total_dependents
            }
            
        return metrics

    def generate_analysis_report(self, report_dir="data/reports"):
        """Run structural analysis and generate markdown report file."""
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "skill_graph_analysis.md")
        
        roots = self.get_root_skills()
        leaves = self.get_leaf_skills()
        components = self.get_connected_components()
        metrics = self.calculate_depths_and_impact()
        
        # Calculate cycles (from NetworkX)
        cycles = list(nx.simple_cycles(self.G))
        
        # Summary metrics
        total_nodes = self.G.number_of_nodes()
        total_edges = self.G.number_of_edges()
        orphan_count = sum(1 for n in self.G.nodes() if self.G.in_degree(n) == 0 and self.G.out_degree(n) == 0)
        
        max_depth = max([m["depth"] for m in metrics.values()]) if metrics else 0
        avg_depth = sum([m["depth"] for m in metrics.values()]) / total_nodes if total_nodes > 0 else 0
        
        # Sort by downstream impact
        sorted_by_impact = sorted(metrics.values(), key=lambda x: x["downstream_impact_count"], reverse=True)
        sorted_by_outdegree = sorted(metrics.values(), key=lambda x: x["direct_dependents_count"], reverse=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# RouteMaster - Skill Dependency Graph Analysis Report\n\n")
            f.write("Generated dynamically. Local time: 2026-08-22\n\n")
            
            # Executive stats
            f.write("## 1. Network Metrics Summary\n\n")
            f.write(f"- **Total Nodes**: {total_nodes} (skills)\n")
            f.write(f"- **Total Edges**: {total_edges} (dependencies)\n")
            f.write(f"- **Foundational / Root Skills**: {len(roots)}\n")
            f.write(f"- **Advanced / Leaf Skills**: {len(leaves)}\n")
            f.write(f"- **Orphan Skills (Isolated)**: {orphan_count}\n")
            f.write(f"- **Connected Graph Components**: {len(components)} (excluding isolated orphans)\n")
            f.write(f"- **Cycles Detected**: {len(cycles)}\n")
            f.write(f"- **Maximum Dependency Depth**: {max_depth}\n")
            f.write(f"- **Average Dependency Depth**: {avg_depth:.2f}\n\n")
            
            # Foundational Skills Table
            f.write("## 2. Foundational / Root Skills\n\n")
            f.write("These skills have outgoing dependencies but no incoming prerequisites. They represent the starting points of learning paths:\n\n")
            f.write("| Skill ID | Skill Name | Category | Out-Degree |\n")
            f.write("| --- | --- | --- | --- |\n")
            for r in roots[:20]:  # limit to top 20
                s_info = self.skills.get(r, {})
                f.write(f"| `{r}` | {s_info.get('skill_name', 'Unknown')} | {s_info.get('skill_category', 'Other')} | {self.G.out_degree(r)} |\n")
            if len(roots) > 20:
                f.write(f"\n*...and {len(roots) - 20} more roots.*\n")
            f.write("\n")
            
            # Leaf Skills Table
            f.write("## 3. Advanced / Leaf Skills\n\n")
            f.write("These skills represent the final goals of existing dependency chains, with no further outgoing prerequisite edges:\n\n")
            f.write("| Skill ID | Skill Name | Category | In-Degree |\n")
            f.write("| --- | --- | --- | --- |\n")
            for l in leaves[:20]:
                s_info = self.skills.get(l, {})
                f.write(f"| `{l}` | {s_info.get('skill_name', 'Unknown')} | {s_info.get('skill_category', 'Other')} | {self.G.in_degree(l)} |\n")
            if len(leaves) > 20:
                f.write(f"\n*...and {len(leaves) - 20} more leaves.*\n")
            f.write("\n")
            
            # High Impact Table
            f.write("## 4. Skills with Highest Downstream Impact\n\n")
            f.write("Impact is measured by the total number of skills that transitively depend on this skill (prerequisite closure size):\n\n")
            f.write("| Skill ID | Skill Name | Direct Dependents | Downstream Impact (Transitive) |\n")
            f.write("| --- | --- | --- | --- |\n")
            for m in sorted_by_impact[:15]:
                f.write(f"| `{m['skill_id']}` | {m['skill_name']} | {m['direct_dependents_count']} | {m['downstream_impact_count']} |\n")
            f.write("\n")
            
            # Most Depended Upon Table
            f.write("## 5. Most Depended-Upon Skills (Direct Out-Degree)\n\n")
            f.write("These skills are direct prerequisites for the largest number of immediate target skills:\n\n")
            f.write("| Skill ID | Skill Name | Direct Out-Degree | Transitive Dependents |\n")
            f.write("| --- | --- | --- | --- |\n")
            for m in sorted_by_outdegree[:15]:
                f.write(f"| `{m['skill_id']}` | {m['skill_name']} | {m['direct_dependents_count']} | {m['downstream_impact_count']} |\n")
            f.write("\n")
            
        print(f"SUCCESS: Dependency analysis report generated at '{report_path}'")
        return report_path
