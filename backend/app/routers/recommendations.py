from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.services.ai_service import AIServiceError, ai_service
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class CareerRecommendationRequest(BaseModel):
    target_career: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    experience: Optional[str] = None


class SkillGapRequest(BaseModel):
    target_career: str
    current_skills: Optional[List[str]] = None


@router.post("/career")
async def career_recommendation(
    req: CareerRecommendationRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return ai_service.career_recommendations(current_user, req.model_dump())
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/skill-gap")
async def skill_gap(
    req: SkillGapRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return ai_service.skill_gaps({**current_user, "skills": req.current_skills or current_user.get("skills", [])}, req.target_career)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
