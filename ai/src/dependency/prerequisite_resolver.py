import os
import json
import networkx as nx

class PrerequisiteResolver:
    """
    Implements path traversals, prerequisite expansions, gap resolution,
    career-aware dependency analysis, and explainability on the Skill Dependency Graph.
    """
    def __init__(self, skill_graph_obj):
        self.graph_obj = skill_graph_obj
        self.G = skill_graph_obj.get_graph()
        self.skills = skill_graph_obj.get_skills_dict()
        
        self.processed_dir = skill_graph_obj.processed_dir
        self._load_career_data()
        self._prerequisite_cache = {}
        self._required_graph = self._build_required_graph()
        try:
            self._topological_order = list(nx.topological_sort(self.G))
        except nx.NetworkXUnfeasible:
            self._topological_order = list(self.G.nodes())

    def _build_required_graph(self):
        """Build the immutable required-edge view once per resolver instance."""
        graph = nx.DiGraph()
        graph.add_nodes_from(self.G.nodes())
        graph.add_edges_from(
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        )
        return graph

    def _load_career_data(self):
        """Load career-related link tables from disk and cache them."""
        self.careers_dict = {}
        self.career_skills_list = []
        self.career_trans_skills_list = []
        
        careers_path = os.path.join(self.processed_dir, "careers.json")
        cs_path = os.path.join(self.processed_dir, "career_skills.json")
        cts_path = os.path.join(self.processed_dir, "career_transferable_skills.json")
        
        try:
            if os.path.exists(careers_path):
                with open(careers_path, "r", encoding="utf-8") as f:
                    self.careers_dict = {item["career_id"]: item for item in json.load(f)}
            if os.path.exists(cs_path):
                with open(cs_path, "r", encoding="utf-8") as f:
                    self.career_skills_list = json.load(f)
            if os.path.exists(cts_path):
                with open(cts_path, "r", encoding="utf-8") as f:
                    self.career_trans_skills_list = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load career tables in PrerequisiteResolver: {str(e)}")

    def get_direct_prerequisites(self, skill_id):
        """
        Get direct prerequisites of a skill.
        Returns a dict separating 'required' and 'recommended' prerequisites.
        """
        result = {"required": [], "recommended": []}
        if not self.G.has_node(skill_id):
            return result
            
        for parent in self.G.predecessors(skill_id):
            edge_data = self.G.get_edge_data(parent, skill_id)
            rel = edge_data.get("relationship", "prerequisite")
            
            skill_info = {
                "skill_id": parent,
                "skill_name": self.skills.get(parent, {}).get("skill_name", "Unknown"),
                "relationship": rel,
                "reason": edge_data.get("reason", "")
            }
            
            if rel in ["prerequisite", "strong_prerequisite"]:
                result["required"].append(skill_info)
            else:
                result["recommended"].append(skill_info)
                
        return result

    def get_all_prerequisites(self, skill_id):
        """
        Get the complete transitive prerequisite closure for a skill.
        Returns a dict:
          - 'required': transitive closure along required edges ('prerequisite'/'strong_prerequisite')
          - 'recommended': other reachable prerequisites in the overall closure.
        Both lists are returned in a valid topological learning order.
        """
        if skill_id in self._prerequisite_cache:
            return self._prerequisite_cache[skill_id]

        result = {"required": [], "recommended": []}
        if not self.G.has_node(skill_id):
            return result

        # Transitive required closure = ancestors in G_req
        req_ancestors = nx.ancestors(self._required_graph, skill_id)

        # Transitive overall closure = ancestors in full graph G
        all_ancestors = nx.ancestors(self.G, skill_id)

        # Recommended ancestors = overall closure minus required closure
        rec_ancestors = all_ancestors - req_ancestors

        # Filter topological order to preserve dependency constraints
        for node in self._topological_order:
            if node in req_ancestors:
                result["required"].append({
                    "skill_id": node,
                    "skill_name": self.skills.get(node, {}).get("skill_name", "Unknown")
                })
            elif node in rec_ancestors:
                result["recommended"].append({
                    "skill_id": node,
                    "skill_name": self.skills.get(node, {}).get("skill_name", "Unknown")
                })

        self._prerequisite_cache[skill_id] = result
        return result

    def get_dependents(self, skill_id):
        """Get the immediate successor skills that directly depend on this skill."""
        result = []
        if not self.G.has_node(skill_id):
            return result
            
        for child in self.G.successors(skill_id):
            edge_data = self.G.get_edge_data(skill_id, child)
            result.append({
                "skill_id": child,
                "skill_name": self.skills.get(child, {}).get("skill_name", "Unknown"),
                "relationship": edge_data.get("relationship", "prerequisite")
            })
        return result

    def get_dependency_chain(self, skill_id):
        """
        Returns the longest required prerequisite path from any root to the target skill.
        Useful to show a vertical progression chain.
        """
        if not self.G.has_node(skill_id):
            return []

        # Subgraph of required edges
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)

        # Find all ancestors
        req_ancestors = nx.ancestors(G_req, skill_id)
        if not req_ancestors:
            return [skill_id]

        # Find root nodes among ancestors
        roots = [n for n in req_ancestors if G_req.in_degree(n) == 0]
        if not roots:
            # Fallback
            roots = list(req_ancestors)

        longest_path = []
        for r in roots:
            # Find all simple paths from r to skill_id in G_req
            paths = list(nx.all_simple_paths(G_req, r, skill_id))
            for path in paths:
                if len(path) > len(longest_path):
                    longest_path = path

        return longest_path if longest_path else [skill_id]

    def resolve_skill_gap(self, current_skills, target_skills):
        """
        Compare current skills with target skills.
        Expands targets to include all transitive required prerequisites,
        removes any skills already owned, and returns the gap in a valid topological learning order.
        """
        if isinstance(current_skills, str):
            current_skills = [current_skills]
        if isinstance(target_skills, str):
            target_skills = [target_skills]
            
        current_set = set(current_skills)
        needed_set = set()

        # Subgraph of required edges
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)

        # Expand each target skill to get its transitive required prerequisites
        for t in target_skills:
            if self.G.has_node(t):
                needed_set.add(t)
                needed_set.update(nx.ancestors(G_req, t))

        # Skill gap = needed - owned
        gap_set = needed_set - current_set

        # Topological sorting of the gap subgraph to respect dependencies
        sub_g = G_req.subgraph(gap_set)
        try:
            ordered_gap = list(nx.topological_sort(sub_g))
        except nx.NetworkXUnfeasible:
            # Fallback
            ordered_gap = sorted(list(gap_set))

        result = []
        for sid in ordered_gap:
            result.append({
                "skill_id": sid,
                "skill_name": self.skills.get(sid, {}).get("skill_name", "Unknown")
            })
        return result

    def resolve_multi_target_gap(self, current_skills, target_skills):
        """Alias wrapper for resolve_skill_gap to support multiple target skills."""
        return self.resolve_skill_gap(current_skills, target_skills)

    def get_career_dependency_analysis(self, career_id):
        """
        Load career required skills (from technical and transferable lists)
        and expand them using the prerequisite dependency graph.
        Returns a structured roadmap order.
        """
        # Find direct required skills
        direct_skills = []
        
        # Technical skills
        for item in self.career_skills_list:
            if item["career_id"] == career_id:
                direct_skills.append(item["skill_id"])
                
        # Transferable skills
        for item in self.career_trans_skills_list:
            if item["career_id"] == career_id:
                direct_skills.append(item["skill_id"])
                
        # Exclude None/duplicates
        direct_skills = list(set([s for s in direct_skills if s]))
        
        # Expand direct skills to complete set (including prerequisites)
        complete_ordered_set = self.resolve_skill_gap(current_skills=[], target_skills=direct_skills)
        complete_ids = [item["skill_id"] for item in complete_ordered_set]
        
        # Prerequisite expansion = complete_set - direct_skills
        direct_set = set(direct_skills)
        expansion_skills = [
            sid for sid in complete_ids if sid not in direct_set
        ]
        
        career_title = self.careers_dict.get(career_id, {}).get("career_title", "Unknown Career")
        
        return {
            "career_id": career_id,
            "career_title": career_title,
            "career_required_skills": [
                {"skill_id": sid, "skill_name": self.skills.get(sid, {}).get("skill_name", "Unknown")}
                for sid in direct_skills
            ],
            "prerequisite_expansion": [
                {"skill_id": sid, "skill_name": self.skills.get(sid, {}).get("skill_name", "Unknown")}
                for sid in expansion_skills
            ],
            "complete_skill_set": complete_ordered_set
        }

    def get_shared_skill_analysis(self, skill_id):
        """
        Identify which careers utilize a skill, what downstream skills depend on it,
        and assess whether it is a foundational shared skill.
        """
        name = self.skills.get(skill_id, {}).get("skill_name", "Unknown")
        
        # 1. Careers using this skill
        careers_using = []
        seen_careers = set()
        
        # Scan technical
        for item in self.career_skills_list:
            if item["skill_id"] == skill_id:
                cid = item["career_id"]
                if cid not in seen_careers:
                    seen_careers.add(cid)
                    title = self.careers_dict.get(cid, {}).get("career_title", "Unknown")
                    careers_using.append({"career_id": cid, "career_title": title, "type": "technical"})
                    
        # Scan transferable
        for item in self.career_trans_skills_list:
            if item["skill_id"] == skill_id:
                cid = item["career_id"]
                if cid not in seen_careers:
                    seen_careers.add(cid)
                    title = self.careers_dict.get(cid, {}).get("career_title", "Unknown")
                    careers_using.append({"career_id": cid, "career_title": title, "type": "transferable"})
                    
        # 2. Downstream skills depending on this skill
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)
        
        downstream_ids = list(nx.descendants(G_req, skill_id))
        downstream_skills = [
            {"skill_id": sid, "skill_name": self.skills.get(sid, {}).get("skill_name", "Unknown")}
            for sid in sorted(downstream_ids)
        ]
        
        # Foundational check: used by > 3 careers or has > 5 downstream dependents
        is_foundational = len(careers_using) > 3 or len(downstream_ids) > 5
        
        return {
            "skill_id": skill_id,
            "skill_name": name,
            "careers": careers_using,
            "downstream_dependents": downstream_skills,
            "is_foundational": is_foundational
        }

    def explain_dependency(self, source_sid, target_sid):
        """
        Explain the dependency relationship between two skills.
        If a direct edge exists, returns the original reason.
        If a transitive path exists, returns a sequential step explanation.
        """
        src_name = self.skills.get(source_sid, {}).get("skill_name", source_sid)
        tgt_name = self.skills.get(target_sid, {}).get("skill_name", target_sid)
        
        # 1. Direct Edge Check
        if self.G.has_edge(source_sid, target_sid):
            edge_data = self.G.get_edge_data(source_sid, target_sid)
            return {
                "is_dependent": True,
                "is_direct": True,
                "relationship": edge_data.get("relationship", "prerequisite"),
                "difficulty": edge_data.get("difficulty", "Intermediate"),
                "domain": edge_data.get("domain", "General"),
                "explanation": edge_data.get("reason", f"'{src_name}' is a direct prerequisite for '{tgt_name}'.")
            }
            
        # 2. Transitive Path Check (required edges only)
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)
        
        if nx.has_path(G_req, source_sid, target_sid):
            path = nx.shortest_path(G_req, source_sid, target_sid)
            steps = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                u_name = self.skills.get(u, {}).get("skill_name", u)
                v_name = self.skills.get(v, {}).get("skill_name", v)
                edge_data = self.G.get_edge_data(u, v)
                steps.append(f"'{u_name}' -> '{v_name}' (Reason: {edge_data.get('reason', 'Prerequisite')})")
                
            explanation_str = f"'{src_name}' is an indirect prerequisite for '{tgt_name}' through the following path:\n" + "\n".join([f"  Step {idx+1}: {step}" for idx, step in enumerate(steps)])
            
            return {
                "is_dependent": True,
                "is_direct": False,
                "relationship": "transitive_prerequisite",
                "difficulty": "Various",
                "domain": "Various",
                "explanation": explanation_str
            }
            
        return {
            "is_dependent": False,
            "is_direct": False,
            "relationship": None,
            "difficulty": None,
            "domain": None,
            "explanation": f"No dependency relationship found between '{src_name}' and '{tgt_name}'."
        }
