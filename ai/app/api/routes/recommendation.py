"""Unified orchestration recommendation route."""
from fastapi import APIRouter, Depends
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.dependencies.services import get_recommendation_service
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/ai", tags=["Recommendation"])


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Full AI pipeline: career → gap → courses → projects → roadmap",
    description=(
        "The primary orchestration endpoint. Runs the complete RouteMaster AI pipeline "
        "in a single request. If target_role is provided it is used directly; otherwise "
        "the top career recommendation is selected automatically.\n\n"
        "Skill gap results are computed once and shared across course, project, and roadmap "
        "engines — no redundant computation.\n\n"
        "If any component fails, status='partial' and the failure is described in warnings[]. "
        "Successful components are still returned."
    ),
    responses={
        422: {"description": "Validation error"},
        500: {"description": "Critical pipeline failure"},
    },
)
async def recommend(
    request: RecommendationRequest,
    svc: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    return svc.recommend(request)
