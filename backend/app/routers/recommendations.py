from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.route_service import recommend_career, compute_skill_gaps
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
    profile = {
        "target_career": req.target_career or current_user.get("target_career", ""),
        "skills": req.skills or current_user.get("skills", []),
        "interests": req.interests or current_user.get("interests", []),
        "experience": req.experience or current_user.get("experience", "Intermediate"),
    }
    return recommend_career(profile)


@router.post("/skill-gap")
async def skill_gap(
    req: SkillGapRequest,
    current_user: dict = Depends(get_current_user),
):
    skills = req.current_skills or current_user.get("skills", [])
    return compute_skill_gaps(skills, req.target_career)
