import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

from .schemas import (
    RecommendationRequest, RecommendationResponse, CareerBrief, 
    CourseRecommendationItem, ProjectRecommendationItem
)
from src.gap_engine.gap_engine import SkillGapEngine
from src.gap_engine.schemas import SkillGapRequest
from src.vector_search.searcher import RouteMasterVectorSearch
from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver
from src.path_utils import resolve_path

# Global cached instance
_global_hybrid_recommender = None


class HybridRecommender:
    """
    Personalized ranking engine utilizing candidate retrieval, set-based skill overlap,
    vector semantics, prerequisite graph validations, and difficulty alignment metrics.
    """
    MIN_COURSE_RELEVANCE = 0.70
    MIN_PROJECT_RELEVANCE = 0.60

    def __init__(self, processed_dir="data/processed", model_dir="model"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))
        self.embeddings_dir = os.path.join(self.model_dir, "embeddings")
        
        self._load_datasets()
        
        self.gap_engine = SkillGapEngine(processed_dir=self.processed_dir)
        try:
            self.vector_search = RouteMasterVectorSearch(
                processed_dir=self.processed_dir, 
                model_dir=self.model_dir
            )
            self.vector_search_available = True
        except Exception as e:
            print(f"WARNING: Vector search unavailable in HybridRecommender ({e}).")
            self.vector_search_available = False

        self.graph_obj = SkillDependencyGraph(processed_dir=self.processed_dir)
        self.resolver = PrerequisiteResolver(self.graph_obj)
        self.G_req = self.resolver.G

        self.default_weights = {
            "skill_match": 0.45,
            "semantic_similarity": 0.25,
            "prerequisite": 0.20,
            "difficulty": 0.10
        }

    def _load_datasets(self):
        """Load JSON datasets into memory."""
        with open(os.path.join(self.processed_dir, "skills.json"), "r", encoding="utf-8") as f:
            self.skills_list = json.load(f)
        self.skills_dict = {s["skill_id"]: s for s in self.skills_list}

        with open(os.path.join(self.processed_dir, "careers.json"), "r", encoding="utf-8") as f:
            self.careers_list = json.load(f)
        self.careers_dict = {c["career_id"]: c for c in self.careers_list}

        with open(os.path.join(self.processed_dir, "courses.json"), "r", encoding="utf-8") as f:
            self.courses_list = json.load(f)
        self.courses_dict = {c["course_id"]: c for c in self.courses_list}

        with open(os.path.join(self.processed_dir, "projects.json"), "r", encoding="utf-8") as f:
            self.projects_list = json.load(f)
        self.projects_dict = {p["project_id"]: p for p in self.projects_list}

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """Computes hybrid course and project recommendations."""
        weights = self.default_weights.copy()
        if request.weights:
            for k in weights.keys():
                if k in request.weights:
                    weights[k] = request.weights[k]
            w_sum = sum(weights.values())
            if w_sum > 0:
                weights = {k: v / w_sum for k, v in weights.items()}

        # 1. Skill Gap Tracing
        gap_request = SkillGapRequest(
            current_skills=request.current_skills,
            target_career=request.target_career
        )
        gap_report = self.gap_engine.calculate_gap(gap_request)
        
        career_id = gap_report.target_career_id
        career_title = gap_report.target_career_title
        career_match = gap_report.overall_readiness_score
        
        user_skill_ids = self.gap_engine.normalize_user_skills(request.current_skills)
        missing_tech_ids = {s.skill_id for s in gap_report.missing_technical_skills}
        prereq_gap_ids = {p.skill_id for p in gap_report.prerequisite_gaps}
        
        all_target_gap_ids = missing_tech_ids.union(prereq_gap_ids)
        skill_gaps_names = [s.skill_name for s in gap_report.missing_technical_skills]

        # 2. Candidate Retrieval
        course_candidates = self._retrieve_course_candidates(request, all_target_gap_ids)
        project_candidates = self._retrieve_project_candidates(request, all_target_gap_ids)

        # 3. Feature Scoring & Ranking — Courses
        recommended_courses = []
        for crs_id in course_candidates:
            crs = self.courses_dict[crs_id]
            crs_skills = set(crs.get("skills", []))
            
            matched_subset = crs_skills.intersection(user_skill_ids)
            missing_subset = crs_skills.intersection(all_target_gap_ids)

            # Skip course if it teaches zero target skills
            if not missing_subset and not matched_subset:
                continue
            
            matched_names = [self.skills_dict[sid]["skill_name"] for sid in matched_subset if sid in self.skills_dict]
            missing_names = [self.skills_dict[sid]["skill_name"] for sid in missing_subset if sid in self.skills_dict]

            # 1. Skill Match Score
            if all_target_gap_ids:
                skill_score = len(missing_subset) / len(all_target_gap_ids)
            else:
                skill_score = 1.0
                
            # 2. Semantic Similarity Score
            semantic_score = self._compute_local_similarity("courses", crs_id, request)

            # 3. Prerequisite Readiness
            prereq_score, status = self._compute_prerequisite_readiness(crs_skills, user_skill_ids)

            # 4. Difficulty Compatibility
            diff_score = self._compute_difficulty_compatibility(crs.get("difficulty", "Intermediate"), request.difficulty)

            final = (
                weights["skill_match"] * skill_score +
                weights["semantic_similarity"] * semantic_score +
                weights["prerequisite"] * prereq_score +
                weights["difficulty"] * diff_score
            )

            # Quality Threshold
            if final < self.MIN_COURSE_RELEVANCE and len(missing_subset) == 0:
                continue

            reason = self._generate_explanation(
                entity_title=crs["course_name"],
                missing_subset_names=missing_names,
                prereq_score=prereq_score,
                status=status,
                difficulty_fit=diff_score,
                difficulty_val=crs.get("difficulty", "Intermediate")
            )

            rec_item = CourseRecommendationItem(
                course_id=crs_id,
                course_name=crs["course_name"],
                organization=crs.get("organization") or "Coursera Provider",
                course_difficulty=crs.get("difficulty") or "Intermediate",
                course_rating=round(float(crs.get("rating") or 0.0), 1),
                course_url=crs.get("url") or "#",
                final_score=round(final, 4),
                skill_match_score=round(skill_score, 4),
                semantic_score=round(semantic_score, 4),
                prerequisite_score=round(prereq_score, 4),
                difficulty_score=round(diff_score, 4),
                matched_skills=matched_names,
                missing_relevant_skills=missing_names,
                prerequisite_status=status,
                reason=reason
            )
            recommended_courses.append(rec_item)

        # Feature Scoring & Ranking — Projects
        recommended_projects = []
        for proj_id in project_candidates:
            proj = self.projects_dict[proj_id]
            proj_skills = set(proj.get("skills", []))
            
            matched_subset = proj_skills.intersection(user_skill_ids)
            missing_subset = proj_skills.intersection(all_target_gap_ids)

            if not missing_subset and not matched_subset:
                continue
            
            matched_names = [self.skills_dict[sid]["skill_name"] for sid in matched_subset if sid in self.skills_dict]
            missing_names = [self.skills_dict[sid]["skill_name"] for sid in missing_subset if sid in self.skills_dict]

            if all_target_gap_ids:
                skill_score = len(missing_subset) / len(all_target_gap_ids)
            else:
                skill_score = 1.0
                
            semantic_score = self._compute_local_similarity("projects", proj_id, request)
            prereq_score, status = self._compute_prerequisite_readiness(proj_skills, user_skill_ids)
            diff_score = self._compute_difficulty_compatibility(proj.get("difficulty") or "Intermediate", request.difficulty)

            final = (
                weights["skill_match"] * skill_score +
                weights["semantic_similarity"] * semantic_score +
                weights["prerequisite"] * prereq_score +
                weights["difficulty"] * diff_score
            )

            if final < self.MIN_PROJECT_RELEVANCE and len(missing_subset) == 0:
                continue

            reason = self._generate_explanation(
                entity_title=proj["project_name"],
                missing_subset_names=missing_names,
                prereq_score=prereq_score,
                status=status,
                difficulty_fit=diff_score,
                difficulty_val=proj.get("difficulty") or "Intermediate",
                is_project=True
            )

            rec_item = ProjectRecommendationItem(
                project_id=proj_id,
                project_name=proj["project_name"],
                domain=proj.get("domain") or "General Engineering",
                difficulty=proj.get("difficulty") or "Intermediate",
                github_url=proj.get("github_url") or "#",
                tech_stack=proj.get("tech_stack") or [],
                final_score=round(final, 4),
                skill_match_score=round(skill_score, 4),
                semantic_score=round(semantic_score, 4),
                prerequisite_score=round(prereq_score, 4),
                difficulty_score=round(diff_score, 4),
                matched_skills=matched_names,
                missing_relevant_skills=missing_names,
                prerequisite_status=status,
                reason=reason
            )
            recommended_projects.append(rec_item)

        recommended_courses.sort(key=lambda x: (-x.final_score, x.course_id))
        recommended_projects.sort(key=lambda x: (-x.final_score, x.project_id))

        return RecommendationResponse(
            career=CareerBrief(
                career_id=career_id,
                career_title=career_title,
                career_match=round(career_match, 1)
            ),
            skill_gaps=skill_gaps_names,
            courses=recommended_courses[:request.top_k],
            projects=recommended_projects[:request.top_k]
        )

    def _retrieve_course_candidates(self, request: RecommendationRequest, gaps: set) -> List[str]:
        """Gathers deduplicated candidate course IDs using skills overlap and exact exclusions."""
        candidates = set()

        for crs in self.courses_list:
            crs_skills = set(crs.get("skills", []))
            if crs_skills.intersection(gaps):
                candidates.add(crs["course_id"])

        # Fallback if gaps pool is small
        if len(candidates) < 10:
            for crs in self.courses_list[:50]:
                candidates.add(crs["course_id"])

        completed_clean = {c.lower().strip() for c in request.completed_courses}
        filtered_candidates = []
        for cid in candidates:
            crs = self.courses_dict[cid]
            c_name = crs["course_name"].lower().strip()
            if c_name not in completed_clean:
                filtered_candidates.append(cid)
                
        return filtered_candidates

    def _retrieve_project_candidates(self, request: RecommendationRequest, gaps: set) -> List[str]:
        """Gathers deduplicated candidate project IDs."""
        candidates = set()

        for proj in self.projects_list:
            proj_skills = set(proj.get("skills", []))
            if proj_skills.intersection(gaps):
                candidates.add(proj["project_id"])

        if len(candidates) < 10:
            for proj in self.projects_list[:30]:
                candidates.add(proj["project_id"])

        return list(candidates)

    def _compute_local_similarity(self, entity_type: str, item_id: str, request: RecommendationRequest) -> float:
        """Calculates cosine similarity between query and candidate embedding locally."""
        if not self.vector_search_available:
            return 0.0
            
        id_map = self.vector_search.local_id_maps.get(entity_type, {})
        embeddings_matrix = self.vector_search.local_embeddings.get(entity_type, None)
        
        if not id_map or embeddings_matrix is None or item_id not in id_map:
            return 0.0
            
        idx = id_map[item_id]
        item_vec = embeddings_matrix[idx]

        q_str = f"Target career: {request.target_career}."
        if isinstance(request.interests, list):
            q_str += f" Interests: {', '.join(request.interests)}."
        elif request.interests:
            q_str += f" Interests: {request.interests}."
            
        q_vec = self.vector_search.embedder.encode(q_str)[0]

        sim = float(np.dot(item_vec, q_vec))
        return max(0.0, min(1.0, sim))

    def _compute_prerequisite_readiness(self, teaches: set, known: set) -> tuple:
        """Determines prerequisite coverage ratio and status (Ready vs Locked)."""
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

    def _compute_difficulty_compatibility(self, course_diff: str, pref: str) -> float:
        """Aligns difficulty tiers."""
        pref_clean = pref.lower().strip()
        if pref_clean in ["any", "any level", "any_level"]:
            return 1.0
            
        diff_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }
        
        c_level = diff_levels.get(course_diff.lower().strip(), 2)
        u_level = diff_levels.get(pref_clean, 2)
        
        diff = abs(c_level - u_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.5
        else:
            return 0.1

    def _generate_explanation(
        self, entity_title: str, missing_subset_names: List[str], 
        prereq_score: float, status: str, difficulty_fit: float, 
        difficulty_val: str, is_project: bool = False
    ) -> str:
        """Assembles explanation reasoning based on scores."""
        target_name = "practice project" if is_project else "course"
        
        reasons = []
        if missing_subset_names:
            reasons.append(f"teaches critical gaps: {', '.join(missing_subset_names[:2])}")
            
        if status == "Ready":
            reasons.append("prerequisites are fully satisfied")
        else:
            reasons.append(f"prerequisites are locked (readiness: {int(prereq_score*100)}%)")
            
        if difficulty_fit == 1.0:
            reasons.append(f"matches your preferred difficulty ({difficulty_val})")
        else:
            reasons.append(f"offered at a different level ({difficulty_val})")

        return f"This {target_name} is recommended because it " + ", and it ".join(reasons) + "."


def recommend_hybrid(request_data: Dict[str, Any], processed_dir="data/processed", model_dir="model") -> Dict[str, Any]:
    """Exposes a clean wrapper API function for Phase 7 hybrid recommendations."""
    global _global_hybrid_recommender
    if _global_hybrid_recommender is None:
        _global_hybrid_recommender = HybridRecommender(processed_dir=processed_dir, model_dir=model_dir)
        
    req = RecommendationRequest(**request_data)
    res = _global_hybrid_recommender.recommend(req)
    return res.model_dump()
