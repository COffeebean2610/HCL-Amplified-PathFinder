import os
import json
import networkx as nx

class GraphValidator:
    """
    Validates a Skill Dependency Graph for logical, structural, and metadata integrity.
    Generates a detailed markdown validation report.
    """
    def __init__(self, skill_graph_obj):
        self.graph_obj = skill_graph_obj
        self.G = skill_graph_obj.get_graph()
        self.skills = skill_graph_obj.get_skills_dict()
        self.dependencies = skill_graph_obj.get_dependencies_list()

    def validate(self, report_dir="data/reports"):
        """Run all validation checks and return results and report path."""
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "dependency_validation_report.md")
        
        errors = []
        warnings = []
        info_notes = []
        
        # 1. Structural Cycle & Self-Loop Checks
        cycles = list(nx.simple_cycles(self.G))
        self_loops = list(nx.nodes_with_selfloops(self.G))
        
        if cycles:
            for cycle in cycles:
                # Find names for cycle nodes
                names = [self.skills.get(n, {}).get("skill_name", n) for n in cycle]
                errors.append(f"Cycle detected: {' -> '.join(names)} -> {names[0]}")
        
        if self_loops:
            for node in self_loops:
                name = self.skills.get(node, {}).get("skill_name", node)
                errors.append(f"Self-referencing loop detected on skill: '{name}' ({node})")
                
        # 2. Duplicate and Contradictory Dependency Checks (using raw dependency records)
        seen_relationships = {}  # (src, tgt) -> list of relations
        for idx, d in enumerate(self.dependencies):
            src = d["source_skill_id"]
            tgt = d["target_skill_id"]
            rel = d["relationship"]
            dep_id = d["dependency_id"]
            
            pair = (src, tgt)
            if pair in seen_relationships:
                seen_relationships[pair].append((rel, dep_id))
                warnings.append(f"Duplicate/overlapping relationship in raw records: {src} -> {tgt} ({rel} in {dep_id})")
            else:
                seen_relationships[pair] = [(rel, dep_id)]
                
        # Check contradictory/multiple edges in raw records
        for pair, relations in seen_relationships.items():
            if len(relations) > 1:
                rel_types = set([r[0] for r in relations])
                if len(rel_types) > 1:
                    errors.append(f"Contradictory relationships between {pair[0]} and {pair[1]}: {rel_types}")
                    
        # 3. Node & Edge Metadata Integrity
        allowed_relations = ["prerequisite", "strong_prerequisite", "recommended_prerequisite"]
        
        for idx, d in enumerate(self.dependencies):
            dep_id = d["dependency_id"]
            src = d["source_skill_id"]
            tgt = d["target_skill_id"]
            src_name = d["source_skill_name"]
            tgt_name = d["target_skill_name"]
            rel = d["relationship"]
            reason = d["reason"]
            diff = d["difficulty"]
            domain = d["domain"]
            
            # Check relation types
            if rel not in allowed_relations:
                errors.append(f"Record {dep_id}: Invalid relationship type '{rel}'")
                
            # Check empty fields
            if not reason or not reason.strip():
                warnings.append(f"Record {dep_id}: Missing explanation reason for dependency.")
            if not diff or not diff.strip():
                warnings.append(f"Record {dep_id}: Missing difficulty metadata.")
            if not domain or not domain.strip():
                warnings.append(f"Record {dep_id}: Missing domain metadata.")
                
            # Check unknown IDs
            if src not in self.skills:
                errors.append(f"Record {dep_id}: Source skill ID '{src}' does not exist in canonical skills registry.")
            if tgt not in self.skills:
                errors.append(f"Record {dep_id}: Target skill ID '{tgt}' does not exist in canonical skills registry.")
                
            # Check name consistency with Canonical Registry
            if src in self.skills:
                canon_name = self.skills[src]["skill_name"]
                if src_name.lower().strip() != canon_name.lower().strip():
                    warnings.append(f"Record {dep_id}: Source skill name '{src_name}' differs from canonical name '{canon_name}'")
            if tgt in self.skills:
                canon_name = self.skills[tgt]["skill_name"]
                if tgt_name.lower().strip() != canon_name.lower().strip():
                    warnings.append(f"Record {dep_id}: Target skill name '{tgt_name}' differs from canonical name '{canon_name}'")
                    
        # 4. Orphan Node Checks
        orphans = []
        for node in self.G.nodes():
            if self.G.in_degree(node) == 0 and self.G.out_degree(node) == 0:
                orphans.append(node)
                
        if orphans:
            info_notes.append(f"Found {len(orphans)} orphan skill nodes (skills with no prerequisites or downstream dependencies). These are mostly Coursera course-imported skills.")

        # Write Markdown validation report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# RouteMaster - Skill Dependency Graph Validation Report\n\n")
            f.write("Generated dynamically. Local time: 2026-08-22\n\n")
            
            # Executive summary status
            status = "PASSED" if not errors else "FAILED"
            status_emoji = "✅" if not errors else "❌"
            f.write(f"**Overall Validation Status**: {status_emoji} {status}\n")
            f.write(f"- **Total Errors**: {len(errors)}\n")
            f.write(f"- **Total Warnings**: {len(warnings)}\n")
            f.write(f"- **Total Information Notes**: {len(info_notes)}\n\n")
            
            # Graph Metrics
            f.write("## Graph Structure Metrics\n\n")
            f.write(f"- **Total Skill Nodes**: {self.G.number_of_nodes()}\n")
            f.write(f"- **Total Prerequisite Edges**: {self.G.number_of_edges()}\n")
            f.write(f"- **Self-loops Detected**: {len(self_loops)}\n")
            f.write(f"- **Cycles Detected**: {len(cycles)}\n\n")
            
            # Cycle section
            f.write("## Structural Validation Results\n\n")
            if cycles:
                f.write("### ❌ Dependency Cycles\n")
                for c in errors:
                    if "Cycle detected" in c:
                        f.write(f"- {c}\n")
                f.write("\n")
            else:
                f.write("### ✅ Cycle Checks\n")
                f.write("No cycles detected. The dependency graph forms a valid Directed Acyclic Graph (DAG).\n\n")
                
            if self_loops:
                f.write("### ❌ Self-Loops\n")
                for s in errors:
                    if "Self-referencing" in s:
                        f.write(f"- {s}\n")
                f.write("\n")
                
            # Errors detail
            f.write("## Validation Errors\n\n")
            if errors:
                for e in errors:
                    f.write(f"- ❌ {e}\n")
            else:
                f.write("No validation errors found! Graph is structurally sound.\n")
            f.write("\n")
            
            # Warnings detail
            f.write("## Validation Warnings\n\n")
            if warnings:
                f.write(f"Total Warnings: {len(warnings)}. First 30 warnings shown below:\n\n")
                for w in warnings[:30]:
                    f.write(f"- ⚠️ {w}\n")
                if len(warnings) > 30:
                    f.write(f"- *...and {len(warnings) - 30} more warnings.*\n")
            else:
                f.write("No validation warnings found.\n")
            f.write("\n")
            
            # Info notes
            f.write("## Informational Notes\n\n")
            for i in info_notes:
                f.write(f"- ℹ️ {i}\n")
                
        print(f"SUCCESS: Dependency validation report generated at '{report_path}'. Status: {'FAILED' if errors else 'PASSED'}")
        return len(errors) == 0, report_path
