"""Roadmap generation route."""
from fastapi import APIRouter, Depends
from app.schemas.roadmap import RoadmapRequest, RoadmapResponse
from app.dependencies.services import get_roadmap_service
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/ai", tags=["Roadmap"])


@router.post(
    "/generate-roadmap",
    response_model=RoadmapResponse,
    summary="Generate a personalized prerequisite-aware learning roadmap",
    description=(
        "Combines Phase 9 with Phases 2, 4, 7, and 8 to produce a React Flow–compatible "
        "node/edge graph representing the learner's personalized study path. "
        "Node statuses: completed | next | locked. "
        "Cycle warnings are returned in the warnings[] field without crashing."
    ),
    responses={
        422: {"description": "Validation error"},
        500: {"description": "Roadmap generation failure"},
    },
)
async def generate_roadmap(
    request: RoadmapRequest,
    svc: RoadmapService = Depends(get_roadmap_service),
) -> RoadmapResponse:
    return svc.generate(request)
