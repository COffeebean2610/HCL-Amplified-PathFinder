"""
Course service — thin wrapper around Phase 7 HybridRecommender.
"""
import logging
from app.schemas.course import CourseRequest, CourseResponse, CourseItem
from app.core.exceptions import RecommendationEngineError

logger = logging.getLogger("routemaster.ai.courses")


class CourseService:
    """Wraps Phase 7 HybridRecommender for FastAPI consumption."""

    def __init__(self, hybrid_recommender):
        self.recommender = hybrid_recommender

    def recommend(self, req: CourseRequest) -> CourseResponse:
        """Recommend courses for a given student profile and target career."""
        try:
            from src.hybrid_recommender.schemas import RecommendationRequest as EngineReq
            engine_req = EngineReq(
                interests=req.interests,
                current_skills=req.skills,
                target_career=req.target_role,
                completed_courses=req.completed_courses,
                difficulty=req.difficulty,
                top_k=req.number_of_results,
            )
            result = self.recommender.recommend(engine_req)
        except Exception as exc:
            logger.error("HybridRecommender (courses) failed: %s", exc)
            raise RecommendationEngineError(str(exc))

        courses = [
            CourseItem(
                course_id=c.course_id,
                course_name=c.course_name,
                organization=c.organization,
                difficulty=c.course_difficulty,
                rating=c.course_rating,
                url=c.course_url,
                relevance_score=round(c.final_score, 4),
                matched_skills=c.matched_skills,
                missing_skills_covered=c.missing_relevant_skills,
                prerequisite_status=c.prerequisite_status,
                reason=c.reason,
            )
            for c in result.courses
        ]

        return CourseResponse(
            target_role=req.target_role,
            courses=courses,
            total=len(courses),
        )
