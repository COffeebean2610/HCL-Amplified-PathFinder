import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

from .schemas import (
    ProjectRecommendationRequest, ProjectRecommendationResponse, CareerSummary, RecommendedProjectItem
)
from src.gap_engine.gap_engine import SkillGapEngine
from src.gap_engine.schemas import SkillGapRequest
from src.vector_search.searcher import RouteMasterVectorSearch
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver

# Cached singleton
_global_project_recommender = None

from src.path_utils import resolve_path

class ProjectRecommender:
    """
    Personalized ranking engine for engineering projects. Analyzes skill gaps,
    applies critical skill importance weighting, computes semantic similarity,
    evaluates required prerequisite structures, and performs greedy skill diversification.
    """
    def __init__(self, processed_dir="data/processed", model_dir="model"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))
        
        # Load registry datasets
        self._load_datasets()
        
        # Initialize sub-engines
        self.gap_engine = SkillGapEngine(processed_dir=self.processed_dir)
        
        try:
            self.vector_search = RouteMasterVectorSearch(
                processed_dir=self.processed_dir, 
                model_dir=self.model_dir
            )
            self.vector_search_available = True
        except Exception as e:
            print(f"WARNING: Vector search unavailable ({e}). Fallback to skill-based retrieval active.")
            self.vector_search_available = False
            
        self.graph_obj = SkillDependencyGraph(processed_dir=self.processed_dir)
        self.resolver = PrerequisiteResolver(self.graph_obj)

        # Configurable ranking weights
        self.default_weights = {
            "skill_gap_coverage": 0.45,
            "semantic_similarity": 0.25,
            "prerequisite_readiness": 0.20,
            "difficulty_compatibility": 0.10
        }

    def _load_datasets(self):
        """Loads and cleans the projects registry."""
        with open(os.path.join(self.processed_dir, "skills.json"), "r", encoding="utf-8") as f:
            skills = json.load(f)
        self.skills_dict = {s["skill_id"]: s for s in skills}

        with open(os.path.join(self.processed_dir, "projects.json"), "r", encoding="utf-8") as f:
            raw_projects = json.load(f)
            
        # Dynamic data cleaning
        self.projects_dict = {}
        for p in raw_projects:
            pid = p.get("project_id")
            if not pid or pid in self.projects_dict:
                continue
                
            # Normalize difficulty values
            diff = p.get("difficulty") or "Intermediate"
            diff = diff.strip().capitalize()
            if diff not in ["Beginner", "Intermediate", "Advanced"]:
                diff = "Intermediate"
                
            # Validate GitHub URLs
            github = p.get("github_url") or "#"
            if not (github.startswith("http://") or github.startswith("https://")):
                github = "#"
                
            clean_proj = {
                "project_id": pid,
                "project_name": p.get("project_name") or "Unnamed Project",
                "domain": p.get("domain") or "General Engineering",
                "difficulty": diff,
                "github_url": github,
                "description": p.get("description") or "",
                "tech_stack": p.get("tech_stack") or [],
                "tags": p.get("tags") or [],
                "skills": p.get("skills") or []
            }
            self.projects_dict[pid] = clean_proj
            
        self.projects_list = list(self.projects_dict.values())

    def recommend_projects(self, request: ProjectRecommendationRequest) -> ProjectRecommendationResponse:
        """Computes skill-gap-aware engineering project recommendations."""
        # 1. Custom weight override and normalization
        weights = self.default_weights.copy()
        if request.weights:
            for k in weights.keys():
                if k in request.weights:
                    weights[k] = request.weights[k]
            w_sum = sum(weights.values())
            if w_sum > 0:
                weights = {k: v / w_sum for k, v in weights.items()}

        # 2. Trace Skill Gaps (Phase 4 integration)
        gap_request = SkillGapRequest(
            current_skills=request.skills,
            target_career=request.target_role
        )
        gap_report = self.gap_engine.calculate_gap(gap_request)
        
        career_id = gap_report.target_career_id
        career_title = gap_report.target_career_title
        
        # Student skills mapping
        user_skill_ids = self.gap_engine.normalize_user_skills(request.skills)
        missing_tech_ids = {s.skill_id for s in gap_report.missing_technical_skills}
        prereq_gap_ids = {p.skill_id for p in gap_report.prerequisite_gaps}
        
        # All gaps combined
        all_gap_ids = missing_tech_ids.union(prereq_gap_ids)
        
        # List of missing names for API response
        skill_gaps_names = [s.skill_name for s in gap_report.missing_technical_skills]

        # Skill importance weight mapper
        importance_weights = {
            "critical": 3.0,
            "high": 2.0,
            "medium": 1.0,
            "low": 1.0
        }
        
        # Map all required career skills and weights
        career_skill_weights = {}
        for s in gap_report.matched_technical_skills + gap_report.missing_technical_skills:
            imp = s.importance.lower() if hasattr(s, "importance") else "medium"
            career_skill_weights[s.skill_id] = importance_weights.get(imp, 1.0)
            
        for s in gap_report.prerequisite_gaps:
            career_skill_weights[s.skill_id] = 1.0  # default weight for prerequisite gaps

        # 3. Candidate Retrieval Generation
        candidates = self._retrieve_candidates(request, all_gap_ids)

        # 4. Feature Scoring
        scored_candidates = []
        for pid in candidates:
            proj = self.projects_dict[pid]
            proj_skills = set(proj.get("skills", []))
            
            # Subsets
            matched_subset = proj_skills.intersection(user_skill_ids)
            missing_subset = proj_skills.intersection(all_gap_ids)
            
            matched_names = [self.skills_dict[sid]["skill_name"] for sid in matched_subset if sid in self.skills_dict]
            missing_names = [self.skills_dict[sid]["skill_name"] for sid in missing_subset if sid in self.skills_dict]

            # A. Weighted Skill Gap Coverage Score
            # Sum weight of covered missing skills / Sum weight of all gaps
            if all_gap_ids:
                covered_weight = sum(career_skill_weights.get(sid, 1.0) for sid in missing_subset)
                total_weight = sum(career_skill_weights.get(sid, 1.0) for sid in all_gap_ids)
                gap_coverage = covered_weight / total_weight if total_weight > 0 else 0.0
            else:
                gap_coverage = 1.0
                
            # B. Project Skill Match (Coverage + Career relevance + Known alignment)
            # Career relevance = project skills that are required/prerequisites for the career
            career_skills_subset = proj_skills.intersection(career_skill_weights.keys())
            career_relevance = len(career_skills_subset) / len(proj_skills) if proj_skills else 0.0
            known_alignment = len(matched_subset) / len(proj_skills) if proj_skills else 0.0
            
            skill_match = 0.50 * gap_coverage + 0.25 * career_relevance + 0.25 * known_alignment

            # C. Semantic Similarity Score
            semantic = self._compute_semantic_similarity(proj, request)

            # D. Prerequisite Readiness Score
            prereq_score, status = self._compute_prerequisites(proj_skills, user_skill_ids)

            # E. Difficulty Compatibility Score
            diff_score = self._compute_difficulty(proj["difficulty"], request.difficulty)

            # Composite weighted final score
            final = (
                weights["skill_gap_coverage"] * gap_coverage +
                weights["semantic_similarity"] * semantic +
                weights["prerequisite_readiness"] * prereq_score +
                weights["difficulty_compatibility"] * diff_score
            )
            
            # Deterministic reasoning
            reason = self._generate_reason(
                proj["project_name"], missing_names, matched_names, 
                prereq_score, status, diff_score, proj["difficulty"]
            )

            rec_item = RecommendedProjectItem(
                project_id=pid,
                project_name=proj["project_name"],
                domain=proj["domain"],
                difficulty=proj["difficulty"],
                github_url=proj["github_url"],
                final_score=round(final, 4),
                skill_gap_coverage_score=round(gap_coverage, 4),
                semantic_score=round(semantic, 4),
                prerequisite_score=round(prereq_score, 4),
                difficulty_score=round(diff_score, 4),
                matched_existing_skills=matched_names,
                skills_to_develop=missing_names,
                prerequisite_status=status,
                reason=reason
            )
            scored_candidates.append(rec_item)

        # 5. Greedy Diversification Re-Ranking
        diversified_results = self._diversify_projects(scored_candidates, request.top_k)

        return ProjectRecommendationResponse(
            career=CareerSummary(
                career_id=career_id,
                career_title=career_title
            ),
            skill_gaps=skill_gaps_names,
            projects=diversified_results
        )

    def _retrieve_candidates(self, request: ProjectRecommendationRequest, gaps: set) -> List[str]:
        """Candidate retrieval fetching up to 30 skills-based and 30 semantic-based projects."""
        candidates = set()

        # Pathway A: Skills-based retrieval (projects teaching at least one missing skill/prerequisite)
        skills_candidates = []
        for p in self.projects_list:
            p_skills = set(p.get("skills", []))
            if p_skills.intersection(gaps):
                skills_candidates.append(p["project_id"])
        candidates.update(skills_candidates[:30])

        # Pathway B: Vector search retrieval (top 30 matches)
        if self.vector_search_available:
            q_str = f"Practice project for target role: {request.target_role}. Gaps: {', '.join(list(gaps)[:5])}."
            if isinstance(request.interests, list):
                q_str += f" Interests: {', '.join(request.interests)}."
            elif request.interests:
                q_str += f" Interests: {request.interests}."
                
            try:
                res = self.vector_search.search("projects", q_str, top_k=30)
                candidates.update([r["entity_id"] for r in res])
            except Exception as e:
                print(f"WARNING: Semantic search retrieval failed ({e}). Fallback to skills-only active.")

        # Pathway C: Fallback to fill candidate pool if empty
        if not candidates:
            # Grab first 30 projects
            candidates.update([p["project_id"] for p in self.projects_list[:30]])

        return list(candidates)

    def _compute_semantic_similarity(self, proj: dict, request: ProjectRecommendationRequest) -> float:
        """Calculates BGE cosine similarity matching vectors locally."""
        if not self.vector_search_available:
            return 0.0
            
        id_map = self.vector_search.local_id_maps.get("projects", {})
        embeddings_matrix = self.vector_search.local_embeddings.get("projects", None)
        pid = proj["project_id"]
        
        if not id_map or embeddings_matrix is None or pid not in id_map:
            return 0.0
            
        idx = id_map[pid]
        proj_vec = embeddings_matrix[idx]

        # Formulate query text
        q_str = f"Practice project for target role: {request.target_role}."
        if isinstance(request.interests, list):
            q_str += f" Interests: {', '.join(request.interests)}."
        elif request.interests:
            q_str += f" Interests: {request.interests}."
            
        try:
            q_vec = self.vector_search.embedder.encode(q_str)[0]
            sim = float(np.dot(proj_vec, q_vec))
            return max(0.0, min(1.0, sim))
        except Exception:
            return 0.0

    def _compute_prerequisites(self, teaches: set, known: set) -> tuple:
        """Computes prerequisite readiness percentage and sets Locking status."""
        prereqs = set()
        for sid in teaches:
            if self.resolver:
                closures = self.resolver.get_all_prerequisites(sid)
                req_ids = [p["skill_id"] for p in closures.get("required", [])]
                prereqs.update(req_ids)

        if not prereqs:
            return 1.0, "Ready"
            
        covered = prereqs.intersection(known)
        ratio = len(covered) / len(prereqs)
        status = "Ready" if ratio >= 0.7 else "Locked"
        return ratio, status

    def _compute_difficulty(self, proj_diff: str, pref: str) -> float:
        """Calculates project difficulty fit scores."""
        pref_clean = pref.lower().strip()
        if pref_clean in ["any", "any level", "any_level"]:
            return 1.0
            
        diff_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }
        
        p_level = diff_levels.get(proj_diff.lower().strip(), 2)
        u_level = diff_levels.get(pref_clean, 2)
        
        diff = abs(p_level - u_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.5
        else:
            return 0.1

    def _generate_reason(
        self, title: str, missing: List[str], matched: List[str], 
        prereq: float, status: str, diff_score: float, diff_val: str
    ) -> str:
        """Deterministic explainability builder based on scores."""
        reasons = []
        if missing:
            reasons.append(f"helps you develop: {', '.join(missing[:2])}")
        if matched:
            reasons.append(f"practices your existing skills: {', '.join(matched[:2])}")
        if status == "Ready":
            reasons.append("you possess all prerequisites")
        else:
            reasons.append(f"prerequisites are locked (readiness: {int(prereq*100)}%)")
        if diff_score == 1.0:
            reasons.append(f"perfectly fits your preferred {diff_val} level")
        else:
            reasons.append(f"is offered at a different {diff_val} level")

        return f"This project is recommended because it " + ", plus it ".join(reasons) + "."

    def _diversify_projects(self, candidates: List[RecommendedProjectItem], top_k: int) -> List[RecommendedProjectItem]:
        """
        Greedily selects projects, penalizing subsequent candidates 
        that share excess skill tags with already-selected ones.
        """
        selected = []
        remaining = candidates.copy()
        selected_skills = set()

        while len(selected) < top_k and remaining:
            best_idx = -1
            best_score = -999.0
            
            for idx, item in enumerate(remaining):
                # Retrieve actual skill IDs
                proj_skills = set(self.projects_dict[item.project_id].get("skills", []))
                
                # Apply penalty for skill overlap: 0.1 penalty per shared skill tag
                overlap_count = len(proj_skills.intersection(selected_skills))
                penalty = 0.1 * overlap_count
                
                penalized_score = item.final_score - penalty
                
                if penalized_score > best_score:
                    best_score = penalized_score
                    best_idx = idx
            
            if best_idx == -1:
                break
                
            selected_item = remaining.pop(best_idx)
            selected.append(selected_item)
            
            # Add its skills to the selected skills pool
            selected_skills.update(self.projects_dict[selected_item.project_id].get("skills", []))

        return selected

def recommend_projects_api(request_data: Dict[str, Any], processed_dir="data/processed", model_dir="model") -> Dict[str, Any]:
    """
    FastAPI/Flask integration wrapper caching a singleton orchestrator.
    """
    global _global_project_recommender
    if _global_project_recommender is None:
        _global_project_recommender = ProjectRecommender(processed_dir=processed_dir, model_dir=model_dir)
        
    req = ProjectRecommendationRequest(**request_data)
    res = _global_project_recommender.recommend_projects(req)
    return res.model_dump()
