"""
Skill gap service — thin wrapper around Phase 4 SkillGapEngine.
"""
import logging
from app.schemas.skill_gap import (
    SkillGapRequest, SkillGapResponse, SkillGapCareer,
    MissingSkill, PrerequisiteGap, LearningStep,
)
from app.core.exceptions import SkillGapEngineError, CareerNotFoundError

logger = logging.getLogger("routemaster.ai.skill_gap")


class SkillGapService:
    """Wraps Phase 4 SkillGapEngine for FastAPI consumption."""

    def __init__(self, gap_engine):
        self.engine = gap_engine

    def calculate(self, req: SkillGapRequest) -> SkillGapResponse:
        """Calculate skill gaps for the given student profile and target career."""
        try:
            from src.gap_engine.schemas import SkillGapRequest as EngineRequest
            engine_req = EngineRequest(
                current_skills=req.skills,
                target_career=req.target_role,
            )
            report = self.engine.calculate_gap(engine_req)
        except Exception as exc:
            msg = str(exc)
            if "not found" in msg.lower() or "career" in msg.lower():
                raise CareerNotFoundError(req.target_role)
            logger.error("SkillGapEngine failed: %s", exc)
            raise SkillGapEngineError(msg)

        missing = [
            MissingSkill(
                skill_id=s.skill_id,
                skill_name=s.skill_name,
                skill_category=s.skill_category,
                priority=s.importance,
            )
            for s in report.missing_technical_skills
        ]

        prereq_gaps = [
            PrerequisiteGap(
                skill_id=p.skill_id,
                skill_name=p.skill_name,
                required_by_skill_id=p.target_skill_id,
                required_by_skill_name=p.target_skill_name,
                reason=p.reason,
            )
            for p in report.prerequisite_gaps
        ]

        sequence = [
            LearningStep(
                sequence_number=step.sequence_number,
                skill_id=step.skill_id,
                skill_name=step.skill_name,
                skill_type=step.skill_type,
                priority=step.priority,
                reason=step.reason,
                prerequisites=step.prerequisites,
            )
            for step in report.learning_sequence
        ]

        matched_names = [s.skill_name for s in report.matched_technical_skills]

        return SkillGapResponse(
            career=SkillGapCareer(
                career_id=report.target_career_id,
                career_title=report.target_career_title,
                career_domain=report.target_career_domain,
            ),
            readiness_score=round(report.overall_readiness_score, 2),
            technical_match_pct=round(report.technical_match_percentage, 2),
            current_skills=req.skills,
            matched_skills=matched_names,
            missing_skills=missing,
            prerequisite_gaps=prereq_gaps,
            learning_sequence=sequence,
        )
