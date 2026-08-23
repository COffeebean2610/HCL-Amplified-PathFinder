"""Course recommendation route."""
from fastapi import APIRouter, Depends
from app.schemas.course import CourseRequest, CourseResponse
from app.dependencies.services import get_course_service
from app.services.course_service import CourseService

router = APIRouter(prefix="/ai", tags=["Courses"])


@router.post(
    "/recommend-courses",
    response_model=CourseResponse,
    summary="Recommend courses for a target career",
    description=(
        "Uses the Phase 7 Hybrid Recommender (skill matching + Sentence Transformer "
        "semantic search + prerequisite graph + difficulty alignment) to rank courses. "
        "Completed courses are excluded. Relevance scores are 0–1.0."
    ),
    responses={
        422: {"description": "Validation error — check difficulty value"},
        500: {"description": "Course recommendation engine failure"},
    },
)
async def recommend_courses(
    request: CourseRequest,
    svc: CourseService = Depends(get_course_service),
) -> CourseResponse:
    return svc.recommend(request)
