"""
RouteMaster AI Service — Custom Exceptions & Standardized Error Handlers
Phase 11: Unified API Error Contracts
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# ── Exception hierarchy ───────────────────────────────────────────────────────

class AIServiceError(Exception):
    """Base class for all RouteMaster AI service errors."""
    code: str = "AI_SERVICE_ERROR"
    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CareerNotFoundError(AIServiceError):
    code = "CAREER_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, career: str):
        super().__init__(f"Target career '{career}' could not be found in the knowledge base.")


class SkillNotFoundError(AIServiceError):
    code = "SKILL_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, skill: str):
        super().__init__(f"Skill '{skill}' could not be resolved in the skill taxonomy.")


class RecommendationEngineError(AIServiceError):
    code = "RECOMMENDATION_ENGINE_ERROR"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(f"Recommendation engine failure: {message}")


class SkillGapEngineError(AIServiceError):
    code = "SKILL_GAP_ENGINE_ERROR"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(f"Skill gap engine failure: {message}")


class RoadmapGenerationError(AIServiceError):
    code = "ROADMAP_GENERATION_ERROR"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(f"Roadmap generation failure: {message}")


class VectorSearchError(AIServiceError):
    code = "VECTOR_SEARCH_ERROR"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self, message: str):
        super().__init__(f"Vector search unavailable: {message}")


class DatabaseError(AIServiceError):
    code = "DATABASE_ERROR"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self, message: str):
        super().__init__(f"Database connection failure: {message}")


# ── Handler registration ──────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Attach all standardized exception handlers to the FastAPI app."""

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Format human-friendly validation error message
        errors = exc.errors()
        err_messages = []
        for err in errors:
            loc = " -> ".join(str(l) for l in err.get("loc", []) if l != "body")
            msg = err.get("msg", "Invalid value")
            err_messages.append(f"{loc}: {msg}" if loc else msg)
        combined_message = "; ".join(err_messages) if err_messages else "Request validation failed."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": combined_message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        # Never expose Python tracebacks to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal error occurred.",
                }
            },
        )
