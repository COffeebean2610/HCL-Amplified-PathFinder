"""Career recommendation route."""
from fastapi import APIRouter, Depends
from app.schemas.career import CareerRequest, CareerResponse
from app.dependencies.services import get_career_service
from app.services.career_service import CareerService

router = APIRouter(prefix="/ai", tags=["Career"])


@router.post(
    "/recommend-career",
    response_model=CareerResponse,
    summary="Recommend careers matching a student profile",
    description=(
        "Analyzes the student's current skills and interests against the RouteMaster "
        "career knowledge base (Phase 3). Returns ranked career matches with gap analysis "
        "and explainable reasons. Scores are 0–100."
    ),
    responses={
        422: {"description": "Validation error — invalid request body"},
        500: {"description": "Recommendation engine failure"},
    },
)
async def recommend_career(
    request: CareerRequest,
    svc: CareerService = Depends(get_career_service),
) -> CareerResponse:
    return svc.recommend(request)
