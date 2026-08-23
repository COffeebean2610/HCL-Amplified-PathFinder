"""
Roadmap service — thin wrapper around Phase 9 RoadmapGenerator.
"""
import logging
from app.schemas.roadmap import (
    RoadmapRequest, RoadmapResponse, RoadmapCareer, RoadmapSummary,
    RoadmapNode, RoadmapEdge, RoadmapNodeData, RoadmapCourse, RoadmapProject,
)
from app.core.exceptions import RoadmapGenerationError

logger = logging.getLogger("routemaster.ai.roadmap")


class RoadmapService:
    """Wraps Phase 9 RoadmapGenerator for FastAPI consumption."""

    def __init__(self, roadmap_generator):
        self.generator = roadmap_generator

    def generate(self, req: RoadmapRequest) -> RoadmapResponse:
        """Generate a React Flow–compatible personalized learning roadmap."""
        try:
            from src.roadmap_generator.schemas import RoadmapRequest as EngineReq
            engine_req = EngineReq(
                skills=req.skills,
                interests=req.interests,
                target_role=req.target_role,
                difficulty=req.difficulty,
                completed_courses=req.completed_courses,
                courses_per_skill=req.courses_per_skill,
                projects_per_skill=req.projects_per_skill,
            )
            result = self.generator.generate_roadmap(engine_req)
        except Exception as exc:
            logger.error("RoadmapGenerator failed: %s", exc)
            raise RoadmapGenerationError(str(exc))

        nodes = []
        for n in result.nodes:
            courses = [
                RoadmapCourse(
                    course_id=c.course_id,
                    course_name=c.course_name,
                    organization=c.organization,
                    difficulty=c.difficulty,
                    rating=c.rating,
                    url=c.url,
                    relevance_score=c.relevance_score,
                )
                for c in n.courses
            ]
            projects = [
                RoadmapProject(
                    project_id=p.project_id,
                    project_name=p.project_name,
                    difficulty=p.difficulty,
                    github_url=p.github_url,
                    relevance_score=p.relevance_score,
                    skills_to_develop=p.skills_to_develop,
                )
                for p in n.projects
            ]
            nodes.append(
                RoadmapNode(
                    id=n.id,
                    skill_id=n.skill_id,
                    skill_name=n.skill_name,
                    status=n.status,
                    priority=n.priority,
                    sequence=n.sequence,
                    prerequisites=n.prerequisites,
                    courses=courses,
                    projects=projects,
                    data=RoadmapNodeData(
                        label=n.data.label,
                        status=n.data.status,
                        priority=n.data.priority,
                        reason=n.data.reason,
                        learning_action=n.data.learning_action,
                    ),
                )
            )

        edges = [
            RoadmapEdge(id=e.id, source=e.source, target=e.target, relationship=e.relationship)
            for e in result.edges
        ]

        return RoadmapResponse(
            career=RoadmapCareer(
                career_id=result.career.career_id,
                career_title=result.career.career_title,
            ),
            summary=RoadmapSummary(
                total_required_skills=result.summary.total_required_skills,
                completed_skills=result.summary.completed_skills,
                remaining_skills=result.summary.remaining_skills,
                progress_percentage=result.summary.progress_percentage,
                critical_skills_remaining=result.summary.critical_skills_remaining,
                career_readiness_score=result.summary.career_readiness_score,
            ),
            nodes=nodes,
            edges=edges,
            warnings=result.warnings,
        )
