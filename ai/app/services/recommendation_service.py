"""
Orchestration recommendation service — Phase 10 unified pipeline.
Shares computed results across components to avoid redundant computation.
"""
import time
import logging
from typing import Optional

from app.schemas.recommendation import (
    RecommendationRequest, RecommendationResponse,
    RecommendationProfile, RecommendationSkillGap, RecommendationRoadmap,
)
from app.schemas.career import CareerRecommendationItem, MissingSkillBrief
from app.schemas.skill_gap import SkillGapRequest, MissingSkill
from app.schemas.course import CourseRequest, CourseItem
from app.schemas.project import ProjectRequest, ProjectItem
from app.schemas.roadmap import RoadmapRequest, RoadmapCareer, RoadmapSummary
from app.schemas.common import Warning
from app.services.career_service import CareerService
from app.services.skill_gap_service import SkillGapService
from app.services.course_service import CourseService
from app.services.project_service import ProjectService
from app.services.roadmap_service import RoadmapService

logger = logging.getLogger("routemaster.ai.recommend")


class RecommendationService:
    """
    Orchestrates the complete RouteMaster AI pipeline.
    Components share gap computations — no redundant engine calls.
    """

    def __init__(
        self,
        career_svc: CareerService,
        gap_svc: SkillGapService,
        course_svc: CourseService,
        project_svc: ProjectService,
        roadmap_svc: RoadmapService,
    ):
        self.career_svc = career_svc
        self.gap_svc = gap_svc
        self.course_svc = course_svc
        self.project_svc = project_svc
        self.roadmap_svc = roadmap_svc

    def recommend(self, req: RecommendationRequest) -> RecommendationResponse:
        warnings: list[Warning] = []
        timings: dict[str, float] = {}

        # ── 1. Career ────────────────────────────────────────────────────────
        target_role = req.target_role
        career_item: Optional[CareerRecommendationItem] = None

        t0 = time.perf_counter()
        if target_role:
            # Build a synthetic CareerRecommendationItem when target_role is explicit
            try:
                from app.schemas.career import CareerRequest
                career_res = self.career_svc.recommend(
                    CareerRequest(skills=req.skills, interests=req.interests, top_k=1)
                )
                # Try to find the matching career in results
                career_item = next(
                    (c for c in career_res.recommendations
                     if target_role.lower() in c.career_title.lower()),
                    career_res.recommendations[0] if career_res.recommendations else None,
                )
            except Exception as exc:
                logger.warning("Career lookup failed for explicit target: %s", exc)
                warnings.append(Warning(
                    component="career",
                    code="CAREER_LOOKUP_FAILED",
                    message=str(exc),
                ))
        else:
            try:
                from app.schemas.career import CareerRequest
                career_res = self.career_svc.recommend(
                    CareerRequest(skills=req.skills, interests=req.interests, top_k=req.top_k_careers)
                )
                career_item = career_res.recommendations[0] if career_res.recommendations else None
                if career_item:
                    target_role = career_item.career_title
            except Exception as exc:
                logger.error("Career recommendation failed: %s", exc)
                warnings.append(Warning(
                    component="career",
                    code="CAREER_RECOMMENDATION_FAILED",
                    message=str(exc),
                ))

        timings["career_ms"] = (time.perf_counter() - t0) * 1000

        if not target_role or not career_item:
            # Cannot proceed without a target — return partial
            return RecommendationResponse(
                status="partial",
                profile=RecommendationProfile(student_id=req.student_id, skills=req.skills, interests=req.interests),
                career=career_item or CareerRecommendationItem(
                    career_id="", career_title="Unknown", match_score=0.0,
                    technical_match_score=0.0, reason="No career could be determined.",
                ),
                skill_gap=RecommendationSkillGap(
                    current_skills=req.skills, matched_skills=[],
                    missing_skills=[], readiness_score=0.0,
                ),
                courses=[], projects=[], roadmap=None,
                warnings=warnings + [Warning(
                    component="pipeline",
                    code="NO_TARGET_CAREER",
                    message="Could not determine a target career. Provide target_role or valid skills/interests.",
                )],
            )

        # ── 2. Skill Gap (computed once, reused by courses/projects/roadmap) ─
        gap_result = None
        t0 = time.perf_counter()
        try:
            gap_result = self.gap_svc.calculate(
                SkillGapRequest(skills=req.skills, target_role=target_role)
            )
        except Exception as exc:
            logger.error("Skill gap failed: %s", exc)
            warnings.append(Warning(
                component="skill_gap",
                code="SKILL_GAP_FAILED",
                message=str(exc),
            ))
        timings["skill_gap_ms"] = (time.perf_counter() - t0) * 1000

        skill_gap_summary = RecommendationSkillGap(
            current_skills=req.skills,
            matched_skills=gap_result.matched_skills if gap_result else [],
            missing_skills=gap_result.missing_skills if gap_result else [],
            readiness_score=gap_result.readiness_score if gap_result else 0.0,
        )

        # ── 3. Courses ────────────────────────────────────────────────────────
        courses: list[CourseItem] = []
        t0 = time.perf_counter()
        try:
            course_res = self.course_svc.recommend(CourseRequest(
                skills=req.skills,
                interests=req.interests,
                target_role=target_role,
                difficulty=req.difficulty,
                completed_courses=req.completed_courses,
                number_of_results=req.number_of_results,
            ))
            courses = course_res.courses
        except Exception as exc:
            logger.error("Course recommendation failed: %s", exc)
            warnings.append(Warning(
                component="courses",
                code="COURSE_RECOMMENDATION_FAILED",
                message=str(exc),
            ))
        timings["courses_ms"] = (time.perf_counter() - t0) * 1000

        # ── 4. Projects ───────────────────────────────────────────────────────
        projects: list[ProjectItem] = []
        t0 = time.perf_counter()
        try:
            project_res = self.project_svc.recommend(ProjectRequest(
                skills=req.skills,
                interests=req.interests,
                target_role=target_role,
                difficulty=req.difficulty,
                number_of_results=req.number_of_results,
            ))
            projects = project_res.projects
        except Exception as exc:
            logger.error("Project recommendation failed: %s", exc)
            warnings.append(Warning(
                component="projects",
                code="PROJECT_RECOMMENDATION_FAILED",
                message=str(exc),
            ))
        timings["projects_ms"] = (time.perf_counter() - t0) * 1000

        # ── 5. Roadmap ────────────────────────────────────────────────────────
        roadmap: Optional[RecommendationRoadmap] = None
        t0 = time.perf_counter()
        try:
            roadmap_res = self.roadmap_svc.generate(RoadmapRequest(
                skills=req.skills,
                interests=req.interests,
                target_role=target_role,
                difficulty=req.difficulty,
                completed_courses=req.completed_courses,
                courses_per_skill=req.courses_per_skill,
                projects_per_skill=req.projects_per_skill,
            ))
            roadmap = RecommendationRoadmap(
                career=roadmap_res.career,
                summary=roadmap_res.summary,
                nodes=roadmap_res.nodes,
                edges=roadmap_res.edges,
            )
        except Exception as exc:
            logger.error("Roadmap generation failed: %s", exc)
            warnings.append(Warning(
                component="roadmap",
                code="ROADMAP_GENERATION_FAILED",
                message=str(exc),
            ))
        timings["roadmap_ms"] = (time.perf_counter() - t0) * 1000

        total_ms = sum(timings.values())
        logger.info(
            "Pipeline complete | career=%.0fms gap=%.0fms courses=%.0fms "
            "projects=%.0fms roadmap=%.0fms total=%.0fms",
            timings["career_ms"], timings["skill_gap_ms"],
            timings["courses_ms"], timings["projects_ms"],
            timings["roadmap_ms"], total_ms,
        )

        status = "partial" if warnings else "success"
        return RecommendationResponse(
            status=status,
            profile=RecommendationProfile(student_id=req.student_id, skills=req.skills, interests=req.interests),
            career=career_item,
            skill_gap=skill_gap_summary,
            courses=courses,
            projects=projects,
            roadmap=roadmap,
            warnings=warnings,
        )
