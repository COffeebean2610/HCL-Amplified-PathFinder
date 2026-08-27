import os
import json
import networkx as nx
from typing import List, Dict, Any

from .schemas import SkillGapRequest, SkillGapResponse, SkillDetail, PrerequisiteGapDetail, SequenceStep
from src.data.normalizers import normalize_skill_name
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver

from src.path_utils import resolve_path

# Global cached instance
_global_gap_engine_instance = None

class SkillGapEngine:
    """
    Computes technical and transferable skill gaps, traces prerequisite paths,
    resolves priority inheritance, and yields topologically ordered learning roadmaps.
    """
    def __init__(self, processed_dir="data/processed"):
        self.processed_dir = str(resolve_path(processed_dir))
        self._load_datasets()

    def _load_datasets(self):
        """Load registries and dependency graphs from disk."""
        # 1. Careers
        with open(os.path.join(self.processed_dir, "careers.json"), "r", encoding="utf-8") as f:
            self.careers = json.load(f)
        self.careers_dict = {c["career_id"]: c for c in self.careers}

        # 2. Skills
        with open(os.path.join(self.processed_dir, "skills.json"), "r", encoding="utf-8") as f:
            self.skills = json.load(f)
        self.skills_dict = {s["skill_id"]: s for s in self.skills}
        
        # Build normalization lookup maps
        self.known_skills_map = {}
        self.skills_by_name = {}
        for s in self.skills:
            sid = s["skill_id"]
            name = s["skill_name"]
            norm_name = s.get("normalized_name", name.lower().strip())
            self.known_skills_map[norm_name] = name
            self.skills_by_name[norm_name] = sid

        # 3. Career-Skills Links
        with open(os.path.join(self.processed_dir, "career_skills.json"), "r", encoding="utf-8") as f:
            self.career_skills = json.load(f)

        # 4. Career-Transferable Links
        with open(os.path.join(self.processed_dir, "career_transferable_skills.json"), "r", encoding="utf-8") as f:
            self.career_trans_skills = json.load(f)

        # 5. Dependency Resolver
        self.graph_obj = SkillDependencyGraph(processed_dir=self.processed_dir)
        self.resolver = PrerequisiteResolver(self.graph_obj)
        self.G = self.graph_obj.get_graph()

    def get_career_by_id_or_title(self, target: str):
        """Lookup career by exact ID or title match."""
        target_clean = target.lower().strip()
        for c in self.careers:
            if c["career_id"].lower() == target_clean or c["career_title"].lower() == target_clean:
                return c
        return None

    def normalize_user_skills(self, current_skills: List[str]) -> set:
        """Map user's input skill strings to canonical skill IDs."""
        normalized_ids = set()
        for raw_s in current_skills:
            if not raw_s or not str(raw_s).strip():
                continue
            # Normalize casing and aliases
            _, norm_key = normalize_skill_name(raw_s, self.known_skills_map)
            
            if norm_key in self.skills_by_name:
                normalized_ids.add(self.skills_by_name[norm_key])
            else:
                # Fallback direct string match across all skills
                for s in self.skills:
                    if s["skill_name"].lower().strip() == norm_key:
                        normalized_ids.add(s["skill_id"])
                        break
        return normalized_ids

    def calculate_gap(self, request: SkillGapRequest) -> SkillGapResponse:
        """Calculate complete prerequisite-aware gaps and return a verified Pydantic model."""
        # 1. Resolve career
        career = self.get_career_by_id_or_title(request.target_career)
        if not career:
            raise ValueError(f"Target career '{request.target_career}' not found in registry.")
            
        cid = career["career_id"]
        career_title = career["career_title"]
        career_domain = career["career_domain"]

        # 2. Normalize skills
        user_skill_ids = self.normalize_user_skills(request.current_skills)

        # 3. Gather career required technical skills
        req_tech = [cs for cs in self.career_skills if cs["career_id"] == cid]
        matched_tech_list = []
        missing_tech_list = []
        
        tech_weights = {"critical": 3.0, "high": 2.0, "medium": 1.0}
        total_tech_weight = 0.0
        matched_tech_weight = 0.0
        
        for cs in req_tech:
            sid = cs["skill_id"]
            importance = cs.get("importance", "Medium")
            s_name = self.skills_dict.get(sid, {}).get("skill_name", "Unknown Skill")
            s_cat = self.skills_dict.get(sid, {}).get("skill_category", "Other")
            
            weight = tech_weights.get(importance.lower(), 1.0)
            total_tech_weight += weight
            
            detail = SkillDetail(
                skill_id=sid,
                skill_name=s_name,
                skill_category=s_cat,
                importance=importance
            )
            
            if sid in user_skill_ids:
                matched_tech_weight += weight
                matched_tech_list.append(detail)
            else:
                missing_tech_list.append(detail)

        # 4. Gather career required transferable skills
        req_trans = [cts for cts in self.career_trans_skills if cts["career_id"] == cid]
        matched_trans_list = []
        missing_trans_list = []
        
        total_trans_weight = 0.0
        matched_trans_weight = 0.0
        
        for cts in req_trans:
            sid = cts["skill_id"]
            imp_score = float(cts.get("importance_score", 4.0))
            data_val = cts.get("data_value", "High")
            s_name = self.skills_dict.get(sid, {}).get("skill_name", "Unknown Soft Skill")
            s_cat = self.skills_dict.get(sid, {}).get("skill_category", "Soft Skills")
            
            total_trans_weight += imp_score
            
            detail = SkillDetail(
                skill_id=sid,
                skill_name=s_name,
                skill_category=s_cat,
                importance=data_val
            )
            
            if sid in user_skill_ids:
                matched_trans_weight += imp_score
                matched_trans_list.append(detail)
            else:
                missing_trans_list.append(detail)

        # Compute percentages
        tech_score = (matched_tech_weight / total_tech_weight) * 100.0 if total_tech_weight > 0 else 100.0
        trans_score = (matched_trans_weight / total_trans_weight) * 100.0 if total_trans_weight > 0 else 100.0
        
        # Overall readiness
        if total_trans_weight > 0:
            overall_readiness = (tech_score * 0.7) + (trans_score * 0.3)
        else:
            overall_readiness = tech_score

        # 5. Prerequisite gap tracing (indirect missing skills)
        prereq_gaps_set = set()
        prereq_details = []
        
        # Subgraph of required edges (from Phase 2)
        required_edges = [
            (u, v) for u, v, attrs in self.G.edges(data=True)
            if attrs.get("relationship") in ["prerequisite", "strong_prerequisite"]
        ]
        G_req = nx.DiGraph()
        G_req.add_nodes_from(self.G.nodes())
        G_req.add_edges_from(required_edges)
        
        direct_missing_ids = {s.skill_id for s in missing_tech_list}
        
        for m in missing_tech_list:
            sid = m.skill_id
            if self.resolver:
                # Find all transitive required prerequisites
                closures = self.resolver.get_all_prerequisites(sid)
                req_prereqs = [p["skill_id"] for p in closures.get("required", [])]
                
                for p_id in req_prereqs:
                    if p_id not in user_skill_ids and p_id not in direct_missing_ids:
                        prereq_gaps_set.add(p_id)
                        
                        # Find the direct edge reason why p_id leads to sid (shortest path required)
                        path = nx.shortest_path(G_req, p_id, sid)
                        # We describe the immediate step in the path
                        next_step = path[1]
                        edge_data = self.G.get_edge_data(path[0], next_step)
                        reason = edge_data.get("reason", f"Required foundation for {self.skills_dict.get(next_step, {}).get('skill_name', next_step)}")
                        
                        p_detail = PrerequisiteGapDetail(
                            skill_id=p_id,
                            skill_name=self.skills_dict.get(p_id, {}).get("skill_name", "Unknown Prerequisite"),
                            target_skill_id=next_step,
                            target_skill_name=self.skills_dict.get(next_step, {}).get("skill_name", next_step),
                            reason=reason
                        )
                        
                        # Keep unique records
                        if p_detail not in prereq_details:
                            prereq_details.append(p_detail)

        # 6. Priority Assignment with Priority Inheritance
        # Map direct missing skills to initial priorities
        # Critical -> Priority 1, High -> Priority 2, Medium -> Priority 3
        skill_priorities = {}
        for m in missing_tech_list:
            skill_priorities[m.skill_id] = m.importance.lower()  # critical / high / medium

        # Priority inheritance: prerequisite gap inherits the maximum priority of any downstream required skill it supports
        for p_id in prereq_gaps_set:
            inherited = "medium"
            # Find downstream descendants in G_req that are in direct_missing_ids
            supported_targets = [
                t_id for t_id in direct_missing_ids
                if nx.has_path(G_req, p_id, t_id)
            ]
            
            if supported_targets:
                # Find max priority (Critical > High > Medium)
                target_priorities = [
                    self.career_skills_importance_level(t_id, cid)
                    for t_id in supported_targets
                ]
                
                if "critical" in target_priorities:
                    inherited = "critical"
                elif "high" in target_priorities:
                    inherited = "high"
                    
            skill_priorities[p_id] = inherited

        # Transferable skills get priorities based on database values
        for m in missing_trans_list:
            skill_priorities[m.skill_id] = m.importance.lower()

        # Group gaps by priority levels
        priority_gaps = {"Critical": [], "High": [], "Medium": [], "Low": []}
        
        # Populate direct technical gaps
        for m in missing_tech_list:
            p_val = skill_priorities.get(m.skill_id, "medium").capitalize()
            if p_val not in priority_gaps:
                p_val = "Medium"
            priority_gaps[p_val].append(m)
            
        # Populate transferable gaps
        for m in missing_trans_list:
            p_val = skill_priorities.get(m.skill_id, "medium").capitalize()
            if p_val not in priority_gaps:
                p_val = "Medium"
            priority_gaps[p_val].append(m)

        # Populate prerequisite gaps
        for p_id in prereq_gaps_set:
            p_val = skill_priorities.get(p_id, "medium").capitalize()
            if p_val not in priority_gaps:
                p_val = "Medium"
                
            s_name = self.skills_dict.get(p_id, {}).get("skill_name", "Unknown Skill")
            s_cat = self.skills_dict.get(p_id, {}).get("skill_category", "Other")
            
            detail = SkillDetail(
                skill_id=p_id,
                skill_name=s_name,
                skill_category=s_cat,
                importance="Prerequisite"
            )
            priority_gaps[p_val].append(detail)

        # 7. Topological Learning Sequence
        # Create a directed subgraph containing all missing technical + prerequisite gaps
        all_missing_tech_ids = direct_missing_ids.union(prereq_gaps_set)
        sub_g = G_req.subgraph(all_missing_tech_ids)
        
        try:
            ordered_tech_ids = list(nx.topological_sort(sub_g))
        except nx.NetworkXUnfeasible:
            # Fallback if cycles exist
            ordered_tech_ids = sorted(list(all_missing_tech_ids))

        learning_sequence = []
        seq_num = 1
        
        for sid in ordered_tech_ids:
            s_name = self.skills_dict.get(sid, {}).get("skill_name", sid)
            
            # Type classification
            is_direct = sid in direct_missing_ids
            s_type = "technical" if is_direct else "prerequisite"
            
            # Fetch priority
            priority_str = skill_priorities.get(sid, "medium").capitalize()
            
            # Fetch reason
            if is_direct:
                # Find matching description from career tech skills
                desc = next((cs["description"] for cs in req_tech if cs["skill_id"] == sid), "")
                reason = f"Directly required for {career_title}. Description: {desc}"
            else:
                # Find which target skill triggered this prerequisite
                trigger = next((p for p in prereq_details if p.skill_id == sid), None)
                if trigger:
                    reason = f"Foundational prerequisite for learning {trigger.target_skill_name}. Reason: {trigger.reason}"
                else:
                    reason = f"Foundational prerequisite for downstream {career_title} technical skills."

            # Fetch difficulty from graph edges
            in_edges = list(self.G.in_edges(sid, data=True))
            diff_level = "Intermediate"
            if in_edges:
                diff_level = in_edges[0][2].get("difficulty", "Intermediate")
                
            # Get immediate prerequisites in the gap subgraph
            imm_prereqs = list(sub_g.predecessors(sid))

            step = SequenceStep(
                sequence_number=seq_num,
                skill_id=sid,
                skill_name=s_name,
                skill_type=s_type,
                priority=priority_str,
                reason=reason,
                difficulty=diff_level,
                prerequisites=imm_prereqs
            )
            learning_sequence.append(step)
            seq_num += 1

        # Append transferable soft skills at the end of the learning path
        for m in missing_trans_list:
            step = SequenceStep(
                sequence_number=seq_num,
                skill_id=m.skill_id,
                skill_name=m.skill_name,
                skill_type="transferable",
                priority=m.importance.capitalize() if m.importance.capitalize() in ["Critical", "High", "Medium"] else "Medium",
                reason=f"Transferable core soft skill required for {career_title}.",
                difficulty="Any Level",
                prerequisites=[]
            )
            learning_sequence.append(step)
            seq_num += 1

        # Assemble and validate response model
        response_model = SkillGapResponse(
            target_career_id=cid,
            target_career_title=career_title,
            target_career_domain=career_domain,
            technical_match_percentage=round(tech_score, 1),
            transferable_match_percentage=round(trans_score, 1),
            overall_readiness_score=round(overall_readiness, 1),
            matched_technical_skills=matched_tech_list,
            missing_technical_skills=missing_tech_list,
            matched_transferable_skills=matched_trans_list,
            missing_transferable_skills=missing_trans_list,
            prerequisite_gaps=prereq_details,
            priority_gaps=priority_gaps,
            learning_sequence=learning_sequence
        )

        return response_model

    def career_skills_importance_level(self, skill_id: str, career_id: str) -> str:
        """Helper to lookup direct technical skill importance level."""
        for cs in self.career_skills:
            if cs["career_id"] == career_id and cs["skill_id"] == skill_id:
                return cs.get("importance", "Medium").lower()
        return "medium"

def analyze_skill_gap(current_skills: List[str], target_career: str, processed_dir="data/processed") -> Dict[str, Any]:
    """
    Standalone function API suitable for FastAPI consumption.
    Reuses a cached singleton instance of SkillGapEngine to avoid reloading data.
    """
    global _global_gap_engine_instance
    if _global_gap_engine_instance is None:
        _global_gap_engine_instance = SkillGapEngine(processed_dir=processed_dir)
        
    request = SkillGapRequest(current_skills=current_skills, target_career=target_career)
    response = _global_gap_engine_instance.calculate_gap(request)
    # Return serializable dict (Pydantic model dump)
    return response.model_dump()
