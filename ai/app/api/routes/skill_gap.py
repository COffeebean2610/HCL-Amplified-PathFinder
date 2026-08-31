"""Skill gap analysis route."""
from fastapi import APIRouter, Depends
from app.schemas.skill_gap import SkillGapRequest, SkillGapResponse
from app.dependencies.services import get_gap_service
from app.services.skill_gap_service import SkillGapService

router = APIRouter(prefix="/ai", tags=["Skill Gap"])


@router.post(
    "/skill-gap",
    response_model=SkillGapResponse,
    summary="Calculate skill gap for a target career",
    description=(
        "Identifies missing technical skills and transitive prerequisite gaps "
        "between the learner's current profile and a target career (Phase 4). "
        "Returns prioritized missing skills and a topologically ordered learning sequence. "
        "Readiness scores are 0–100."
    ),
    responses={
        404: {"description": "Target career not found in knowledge base"},
        422: {"description": "Validation error"},
        500: {"description": "Skill gap engine failure"},
    },
)
async def skill_gap(
    request: SkillGapRequest,
    svc: SkillGapService = Depends(get_gap_service),
) -> SkillGapResponse:
    return svc.calculate(request)
