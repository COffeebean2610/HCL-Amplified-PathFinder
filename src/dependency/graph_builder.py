import os
import json
import networkx as nx

from src.path_utils import resolve_path

class SkillDependencyGraph:
    """
    Constructs and caches a NetworkX Directed Graph representing skill dependencies.
    Edge direction is: PREREQUISITE SKILL (source) -> TARGET SKILL (target).
    """
    _cached_graph = None
    _cached_skills = None
    _cached_dependencies = None

    def __init__(self, processed_dir="data/processed", force_rebuild=False):
        self.processed_dir = str(resolve_path(processed_dir))
        self.skills_path = os.path.join(self.processed_dir, "skills.json")
        self.deps_path = os.path.join(self.processed_dir, "skill_dependencies.json")
        
        if force_rebuild or SkillDependencyGraph._cached_graph is None:
            self._build_graph()
            
        self.graph = SkillDependencyGraph._cached_graph
        self.skills = SkillDependencyGraph._cached_skills
        self.dependencies = SkillDependencyGraph._cached_dependencies

    def _build_graph(self):
        """Construct NetworkX DiGraph from processed JSON files."""
        if not os.path.exists(self.skills_path):
            raise FileNotFoundError(f"Canonical skills file not found at: {self.skills_path}")
        if not os.path.exists(self.deps_path):
            raise FileNotFoundError(f"Skill dependencies file not found at: {self.deps_path}")
            
        with open(self.skills_path, "r", encoding="utf-8") as f:
            skills = json.load(f)
            
        with open(self.deps_path, "r", encoding="utf-8") as f:
            dependencies = json.load(f)
            
        G = nx.DiGraph()
        
        # 1. Add all skill nodes from canonical registry
        for s in skills:
            sid = s["skill_id"]
            G.add_node(
                sid,
                skill_id=sid,
                canonical_name=s["skill_name"],
                display_name=s["skill_name"],
                skill_category=s["skill_category"],
                skill_type=s["skill_type"]
            )
            
        # 2. Add edges for dependencies: source_skill_id -> target_skill_id
        for d in dependencies:
            src = d["source_skill_id"]
            tgt = d["target_skill_id"]
            
            # Handle missing nodes defensively (though Phase 1 validator prevents orphans)
            if not G.has_node(src):
                G.add_node(
                    src,
                    skill_id=src,
                    canonical_name=d.get("source_skill_name", "Unknown"),
                    display_name=d.get("source_skill_name", "Unknown"),
                    skill_category=d.get("domain", "Other"),
                    skill_type="other"
                )
            if not G.has_node(tgt):
                G.add_node(
                    tgt,
                    skill_id=tgt,
                    canonical_name=d.get("target_skill_name", "Unknown"),
                    display_name=d.get("target_skill_name", "Unknown"),
                    skill_category=d.get("domain", "Other"),
                    skill_type="other"
                )
                
            G.add_edge(
                src,
                tgt,
                relationship=d["relationship"],
                reason=d["reason"],
                difficulty=d["difficulty"],
                domain=d["domain"],
                dependency_id=d["dependency_id"]
            )
            
        SkillDependencyGraph._cached_graph = G
        SkillDependencyGraph._cached_skills = {s["skill_id"]: s for s in skills}
        SkillDependencyGraph._cached_dependencies = dependencies

    def get_graph(self):
        """Get the cached NetworkX DiGraph."""
        return self.graph

    def get_skills_dict(self):
        """Get the dictionary of canonical skills (id -> skill)."""
        return self.skills

    def get_dependencies_list(self):
        """Get the list of raw dependency dictionaries."""
        return self.dependencies
