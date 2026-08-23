import os
import json
import pickle
import math
import pandas as pd

from .schemas import validate_recommendation_input
from .interest_matcher import InterestMatcher
from .skill_matcher import SkillMatcher
from .transferable_matcher import TransferableMatcher
from .semantic_matcher import SemanticMatcher
from .gap_analyzer import GapAnalyzer
from .scoring import ScoringEngine
from .explanation import ExplanationGenerator

from src.dependency.graph_builder import SkillDependencyGraph
from src.dependency.prerequisite_resolver import PrerequisiteResolver

from src.path_utils import resolve_path

# Global cache for a single CareerRecommender instance to speed up consecutive calls
_global_recommender_instance = None

class CareerRecommender:
    """
    Main recommendation orchestrator for RouteMaster careers.
    Loads and caches data foundations, computes hybrid scores, gap profiles,
    and returns stable JSON recommendations.
    """
    def __init__(self, processed_dir="data/processed", model_dir="model"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))
        self._load_datasets()
        self._init_submodules()

    def _load_datasets(self):
        """Loads canonical knowledge registries from disk."""
        # 1. Careers Registry
        with open(os.path.join(self.processed_dir, "careers.json"), "r", encoding="utf-8") as f:
            self.careers_list = json.load(f)
            
        # 2. Skills Registry
        with open(os.path.join(self.processed_dir, "skills.json"), "r", encoding="utf-8") as f:
            self.skills_list = json.load(f)
            
        # 3. Career-Skills Links
        with open(os.path.join(self.processed_dir, "career_skills.json"), "r", encoding="utf-8") as f:
            self.career_skills_list = json.load(f)
            
        # 4. Career-Transferable Links
        with open(os.path.join(self.processed_dir, "career_transferable_skills.json"), "r", encoding="utf-8") as f:
            self.career_trans_list = json.load(f)
            
        # 5. Career-Interests Links
        with open(os.path.join(self.processed_dir, "career_interests.json"), "r", encoding="utf-8") as f:
            self.career_interests_list = json.load(f)

        # 6. Load TF-IDF Vectorizer (Embedding Infrastructure)
        vec_path = os.path.join(self.model_dir, "vectorizer.pkl")
        if os.path.exists(vec_path):
            with open(vec_path, "rb") as f:
                self.vectorizer = pickle.load(f)
        else:
            print("Warning: vectorizer.pkl not found. Semantic similarity will be disabled.")
            self.vectorizer = None

        # 7. Initialize Graph Resolver from Phase 2
        try:
            self.graph_obj = SkillDependencyGraph(processed_dir=self.processed_dir)
            self.prereq_resolver = PrerequisiteResolver(self.graph_obj)
        except Exception as e:
            print(f"Warning: Failed to load Skill Prerequisite Graph: {str(e)}")
            self.prereq_resolver = None

    def _init_submodules(self):
        """Instantiate helper matching submodules."""
        self.interest_matcher = InterestMatcher(self.career_interests_list, self.vectorizer)
        self.skill_matcher = SkillMatcher(self.skills_list, self.career_skills_list)
        self.trans_matcher = TransferableMatcher(self.skills_list, self.career_trans_list)
        
        self.semantic_matcher = SemanticMatcher(
            self.careers_list, self.skills_list, self.career_skills_list,
            self.career_trans_list, self.career_interests_list, self.vectorizer
        )
        
        self.gap_analyzer = GapAnalyzer(self.prereq_resolver)
        self.scoring_engine = ScoringEngine()

    def get_career_by_id_or_title(self, target):
        """Lookup a career in registry by exact ID or title match."""
        if not target:
            return None
        target_clean = str(target).lower().strip()
        for c in self.careers_list:
            if c["career_id"].lower() == target_clean or c["career_title"].lower() == target_clean:
                return c
        return None

    def recommend(self, profile, top_k=None):
        """
        Orchestrates the complete career recommendation pipeline.
        Returns a JSON-compatible structured recommendation profile.
        """
        # Step 1: Input Validation
        is_valid, cleaned, err = validate_recommendation_input(profile)
        if not is_valid:
            raise ValueError(f"Invalid recommendation profile: {err}")

        user_raw_interests = cleaned["interests"]
        user_raw_skills = cleaned["current_skills"]
        user_raw_trans = cleaned["transferable_skills"]
        target_career_name = cleaned["target_career"]
        
        if top_k is None:
            top_k = cleaned["top_k"]

        # Step 2: Signal extraction and normalization
        user_skill_ids, unknown_skills = self.skill_matcher.normalize_user_skills(user_raw_skills)
        user_trans_ids = self.trans_matcher.normalize_user_transferable(user_raw_trans)
        user_riasec = self.interest_matcher.match_interests(user_raw_interests)

        # Detect signal presence for cold-start weight scaling
        has_skills = len(user_skill_ids) > 0
        has_interests = (isinstance(user_raw_interests, str) and len(user_raw_interests.strip()) > 0) or \
                        (isinstance(user_raw_interests, dict) and sum(user_riasec.values()) > 0)
        has_trans = len(user_trans_ids) > 0

        # Step 3: Semantic profile mapping
        # Convert user skills and trans to name strings for the TF-IDF representation
        user_skill_names = [self.skills_list[idx]["skill_name"] for idx in user_skill_ids if idx in self.skills_list] # fallback check
        if not user_skill_names:
            # Fallback if resolver matches unknown
            user_skill_names = list(user_skill_ids)
            
        user_trans_names = list(user_trans_ids) # placeholder or names
        
        semantic_similarities = self.semantic_matcher.match_profile(
            user_interests=user_raw_interests,
            user_skills=user_raw_skills,
            user_trans=user_raw_trans
        )

        # Step 4: Component calculations for each career
        all_career_evals = []
        
        for c in self.careers_list:
            cid = c["career_id"]
            title = c["career_title"]
            domain = c["career_domain"]
            
            # A. Technical Skill Matching
            tech_match = self.skill_matcher.match_technical_skills(cid, user_skill_ids)
            
            # B. Transferable Skill Matching
            trans_match = self.trans_matcher.match_transferable_skills(cid, user_trans_ids)
            
            # C. Interest Compatibility
            # Compute compatibility score based on career interests
            career_riasec = {}
            for item in self.career_interests_list:
                if item["career_id"] == cid:
                    career_riasec[item["interest_type"]] = item["interest_score"]
            
            # Vector dot product compatibility between RIASEC vectors
            total_dot = 0.0
            sum_user_sq = 0.0
            sum_career_sq = 0.0
            for r_type in self.interest_matcher.riasec_types:
                u_score = user_riasec.get(r_type, 0.0)
                c_score = career_riasec.get(r_type, 0.0)
                total_dot += u_score * c_score
                sum_user_sq += u_score ** 2
                sum_career_sq += c_score ** 2
                
            interest_score = 0.0
            if sum_user_sq > 0 and sum_career_sq > 0:
                interest_score = (total_dot / (math.sqrt(sum_user_sq) * math.sqrt(sum_career_sq))) * 100.0
                
            # D. Semantic similarity
            semantic_score = semantic_similarities.get(cid, 0.0)
            
            # E. Market Signal static metric
            market_score = self.scoring_engine.calculate_market_signal(cid, self.career_skills_list)
            
            # Combine component scores
            component_scores = {
                "technical": tech_match["score"],
                "transferable": trans_match["score"],
                "interest": interest_score,
                "semantic": semantic_score,
                "market": market_score
            }
            
            # Dynamic weights adjustment
            active_weights = self.scoring_engine.get_active_weights(has_skills, has_interests, has_trans)
            
            # Compute overall hybrid match score
            final_match_score = self.scoring_engine.compute_hybrid_score(component_scores, active_weights)
            
            # F. Prerequisite-aware gap analysis
            gap_analysis = self.gap_analyzer.analyze_gaps(
                user_skill_ids=user_skill_ids,
                matched_tech=tech_match["matched_skills"],
                missing_tech=tech_match["missing_skills"]
            )
            
            # G. Explanation Generation
            explanation = ExplanationGenerator.generate_explanation(
                career_title=title,
                match_score=final_match_score,
                component_scores=component_scores,
                matched_tech=tech_match["matched_skills"],
                missing_tech=tech_match["missing_skills"],
                matched_trans=trans_match["matched_skills"],
                prereqs=gap_analysis["prerequisite_gaps"]
            )
            
            eval_record = {
                "career_id": cid,
                "career": title,
                "domain": domain,
                "match_score": final_match_score,
                "score_breakdown": {
                    "technical_skill_match": round(tech_match["score"], 1),
                    "transferable_skill_match": round(trans_match["score"], 1),
                    "interest_match": round(interest_score, 1),
                    "semantic_similarity": round(semantic_score, 1),
                    "market_signal": round(market_score, 1)
                },
                "matched_technical_skills": [s["skill_name"] for s in tech_match["matched_skills"]],
                "missing_technical_skills": [s["skill_name"] for s in tech_match["missing_skills"]],
                "critical_missing_skills": [s["skill_name"] for s in tech_match["critical_missing_skills"]],
                "matched_transferable_skills": [t["skill_name"] for t in trans_match["matched_skills"]],
                "missing_transferable_skills": [t["skill_name"] for t in trans_match["missing_skills"]],
                "prerequisite_gaps": gap_analysis["prerequisite_gaps"],
                "complete_roadmap_path": gap_analysis["complete_roadmap_path"],
                "explanation": explanation
            }
            all_career_evals.append(eval_record)

        # Sort careers deterministically by match_score descending, with career ID as alphabetical tie-breaker
        all_career_evals.sort(key=lambda x: (-x["match_score"], x["career_id"]))
        
        # Assign rank index and confidence
        confidence = self.scoring_engine.calculate_confidence(user_skill_ids, user_riasec, user_trans_ids)
        
        ranked_recommendations = []
        for idx, rec in enumerate(all_career_evals[:top_k]):
            rec["rank"] = idx + 1
            rec["confidence"] = confidence
            ranked_recommendations.append(rec)

        # Step 5: Handle Target Career Support
        target_eval = None
        if target_career_name:
            target_career = self.get_career_by_id_or_title(target_career_name)
            if target_career:
                t_id = target_career["career_id"]
                # Find its evaluation from pre-calculated list
                t_eval = None
                for rec in all_career_evals:
                    if rec["career_id"] == t_id:
                        t_eval = rec
                        break
                
                if t_eval:
                    t_score = t_eval["match_score"]
                    if t_score >= 85:
                        fit_lvl = "Strong"
                    elif t_score >= 60:
                        fit_lvl = "Medium"
                    else:
                        fit_lvl = "Weak"
                        
                    # Find alternatives (top ranked recommendations that scored higher than the target)
                    alternatives = []
                    for r in ranked_recommendations:
                        if r["career_id"] != t_id and r["match_score"] > t_score:
                            alternatives.append({
                                "career_id": r["career_id"],
                                "career": r["career"],
                                "match_score": r["match_score"]
                            })
                            
                    target_eval = {
                        "target_career_id": t_id,
                        "target_career_title": t_eval["career"],
                        "target_fit_score": t_score,
                        "fit_level": fit_lvl,
                        "matched_technical_skills": t_eval["matched_technical_skills"],
                        "missing_technical_skills": t_eval["missing_technical_skills"],
                        "critical_missing_skills": t_eval["critical_missing_skills"],
                        "prerequisite_gaps": t_eval["prerequisite_gaps"],
                        "complete_roadmap_path": t_eval["complete_roadmap_path"],
                        "recommended_alternatives": alternatives[:3],
                        "explanation": t_eval["explanation"]
                    }

        # Step 6: Format output contract
        profile_summary = {
            "skills_detected": [self.skills_list.get(sid, {}).get("skill_name", sid) for sid in user_skill_ids] if isinstance(self.skills_list, dict) else [],
            "interests_detected": user_riasec,
            "transferable_skills_detected": [self.skills_list.get(tid, {}).get("skill_name", tid) for tid in user_trans_ids] if isinstance(self.skills_list, dict) else []
        }
        
        # Fallback names lookup for profile summary
        if isinstance(self.skills_list, list):
            s_dict = {s["skill_id"]: s["skill_name"] for s in self.skills_list}
            profile_summary["skills_detected"] = [s_dict.get(sid, sid) for sid in user_skill_ids]
            profile_summary["transferable_skills_detected"] = [s_dict.get(tid, tid) for tid in user_trans_ids]

        output = {
            "profile_summary": profile_summary,
            "recommendations": ranked_recommendations,
            "target_career_evaluation": target_eval
        }
        
        return output

def recommend_careers(profile, top_k=5, processed_dir="data/processed"):
    """
    Standalone function API ready for FastAPI consumption.
    Reuses a cached singleton instance of CareerRecommender to avoid reloading data.
    """
    global _global_recommender_instance
    if _global_recommender_instance is None:
        _global_recommender_instance = CareerRecommender(processed_dir=processed_dir)
    return _global_recommender_instance.recommend(profile, top_k=top_k)
