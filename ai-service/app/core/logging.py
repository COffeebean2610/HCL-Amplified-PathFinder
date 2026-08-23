"""
RouteMaster AI Service — Structured Request Logging Middleware
"""
import time
import uuid
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger("routemaster.ai")


def setup_logging(log_level: str = "INFO") -> None:
    """Configure root logger with structured format."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def register_logging_middleware(app: FastAPI) -> None:
    """Attach request/response logging middleware."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        logger.info(
            "REQUEST  id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "RESPONSE id=%s status=%s latency=%.1fms",
            request_id,
            response.status_code,
            elapsed_ms,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response
