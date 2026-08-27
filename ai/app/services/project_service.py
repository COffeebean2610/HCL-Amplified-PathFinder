"""
Project service — thin wrapper around Phase 8 ProjectRecommender.
"""
import logging
from app.schemas.project import ProjectRequest, ProjectResponse, ProjectItem
from app.core.exceptions import RecommendationEngineError

logger = logging.getLogger("routemaster.ai.projects")


class ProjectService:
    """Wraps Phase 8 ProjectRecommender for FastAPI consumption."""

    def __init__(self, project_recommender):
        self.recommender = project_recommender

    def recommend(self, req: ProjectRequest) -> ProjectResponse:
        """Recommend skill-gap-aware engineering projects."""
        try:
            from src.project_recommender.schemas import ProjectRecommendationRequest as EngineReq
            engine_req = EngineReq(
                skills=req.skills,
                interests=req.interests,
                target_role=req.target_role,
                difficulty=req.difficulty,
                top_k=req.number_of_results,
            )
            result = self.recommender.recommend_projects(engine_req)
        except Exception as exc:
            logger.error("ProjectRecommender failed: %s", exc)
            raise RecommendationEngineError(str(exc))

        projects = [
            ProjectItem(
                project_id=p.project_id,
                project_name=p.project_name,
                domain=p.domain,
                difficulty=p.difficulty,
                github_url=p.github_url,
                relevance_score=round(p.final_score, 4),
                skills_to_develop=p.skills_to_develop,
                matched_existing_skills=p.matched_existing_skills,
                prerequisite_status=p.prerequisite_status,
                reason=p.reason,
            )
            for p in result.projects
        ]

        return ProjectResponse(
            target_role=req.target_role,
            projects=projects,
            total=len(projects),
        )
