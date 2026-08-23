"""
Career service — thin wrapper around Phase 3 CareerRecommender.
"""
import logging
from typing import List, Union
from app.schemas.career import CareerRequest, CareerResponse, CareerRecommendationItem, MissingSkillBrief
from app.core.exceptions import RecommendationEngineError

logger = logging.getLogger("routemaster.ai.career")


class CareerService:
    """Wraps Phase 3 CareerRecommender for FastAPI consumption."""

    def __init__(self, career_recommender):
        self.recommender = career_recommender

    def recommend(self, req: CareerRequest) -> CareerResponse:
        """Recommend careers matching the student's profile."""
        try:
            interests = req.interests if isinstance(req.interests, str) else ", ".join(req.interests)
            # CareerRecommender.recommend() takes a dict profile, not kwargs
            profile = {
                "interests": interests,
                "current_skills": req.skills,
                "transferable_skills": [],
                "target_career": None,
                "top_k": req.top_k,
            }
            output = self.recommender.recommend(profile, top_k=req.top_k)
        except Exception as exc:
            logger.error("CareerRecommender failed: %s", exc)
            raise RecommendationEngineError(str(exc))

        # Engine returns {"profile_summary": ..., "recommendations": [...], "target_career_evaluation": ...}
        raw_list = output.get("recommendations", [])
        items = []
        for r in raw_list:
            # Engine uses "career" (not "career_title") and "missing_technical_skills" (list of strings)
            missing_names = r.get("missing_technical_skills", [])
            missing = [
                MissingSkillBrief(
                    skill_id="",  # not provided at this level by engine
                    skill_name=name,
                    importance="Medium",
                )
                for name in missing_names
                if isinstance(name, str)
            ]
            items.append(
                CareerRecommendationItem(
                    career_id=r.get("career_id", ""),
                    career_title=r.get("career", r.get("career_title", "")),
                    career_domain=r.get("domain", ""),
                    match_score=round(float(r.get("match_score", 0.0)), 2),
                    technical_match_score=round(
                        float(r.get("score_breakdown", {}).get("technical_skill_match", 0.0)), 2
                    ),
                    matched_skills=r.get("matched_technical_skills", []),
                    missing_skills=missing,
                    reason=r.get("explanation", ""),
                )
            )

        return CareerResponse(recommendations=items, total=len(items))
