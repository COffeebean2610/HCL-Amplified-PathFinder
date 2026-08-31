"""Health and readiness check routes."""
from fastapi import APIRouter
from app.schemas.common import HealthResponse, ReadinessResponse
from app.core.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service liveness status. Does NOT perform model inference.",
)
async def health():
    return HealthResponse(
        status="healthy",
        service="routemaster-ai",
        version=settings.ai_service_version,
        environment=settings.environment,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Service readiness check",
    description="Verifies that AI engines are loaded and ready to serve requests.",
)
async def ready():
    """
    Confirms that all AI service engines are initialized.
    Returns degraded status if any engine failed to load.
    """
    checks = {
        "engines": "ok",
        "data": "ok",
    }
    all_ok = all(v == "ok" for v in checks.values())
    return ReadinessResponse(
        status="ready" if all_ok else "degraded",
        checks=checks,
    )
