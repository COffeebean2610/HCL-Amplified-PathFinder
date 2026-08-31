"""Project recommendation route."""
from fastapi import APIRouter, Depends
from app.schemas.project import ProjectRequest, ProjectResponse
from app.dependencies.services import get_project_service
from app.services.project_service import ProjectService

router = APIRouter(prefix="/ai", tags=["Projects"])


@router.post(
    "/recommend-projects",
    response_model=ProjectResponse,
    summary="Recommend skill-gap-aware engineering projects",
    description=(
        "Uses Phase 8 to recommend projects that help learners practice skills "
        "they already have while developing skills in their gap. Skill gaps are "
        "derived automatically from target_role — no need to supply them manually. "
        "Relevance scores are 0–1.0."
    ),
    responses={
        422: {"description": "Validation error"},
        500: {"description": "Project recommendation engine failure"},
    },
)
async def recommend_projects(
    request: ProjectRequest,
    svc: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return svc.recommend(request)
