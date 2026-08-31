"""
RouteMaster AI Service — FastAPI Application Entry Point
Phase 10: AI Service / FastAPI

Architecture:
    SDE Backend (Member 2)
          ↓
    FastAPI AI Service  ←── this file
          ↓
    Service Layer → Phase 1-9 AI Engines
          ↓
    JSON Response

All engines are loaded ONCE during application startup via the lifespan
event handler and stored in app.state. Routes pull them via Depends().
"""
import sys
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Add the repo root to sys.path so src/ packages are importable ─────────────
# ai-service/app/main.py → ../../ = repo root
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging, register_logging_middleware

from app.services.career_service import CareerService
from app.services.skill_gap_service import SkillGapService
from app.services.course_service import CourseService
from app.services.project_service import ProjectService
from app.services.roadmap_service import RoadmapService
from app.services.recommendation_service import RecommendationService

from app.api.routes import health, career, skill_gap, courses, projects, roadmap, recommendation

from pathlib import Path

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger("routemaster.ai")


def _validate_startup_paths(settings):
    """Validate that required dataset and model directories/files exist at startup."""
    processed_path = Path(settings.processed_dir)
    model_path = Path(settings.model_dir)

    if not processed_path.exists():
        raise FileNotFoundError(
            f"Processed dataset directory does not exist: {processed_path}"
        )
    if not processed_path.is_dir():
        raise NotADirectoryError(
            f"Processed dataset path is not a directory: {processed_path}"
        )

    required_data_files = [
        "careers.json",
        "skills.json",
        "career_skills.json",
        "career_transferable_skills.json",
        "career_interests.json",
        "skill_dependencies.json",
        "courses.json",
        "projects.json",
    ]
    missing_data_files = [
        f for f in required_data_files if not (processed_path / f).exists()
    ]
    if missing_data_files:
        raise FileNotFoundError(
            f"Missing required dataset file(s) in {processed_path}: {', '.join(missing_data_files)}"
        )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model directory does not exist: {model_path}"
        )
    if not model_path.is_dir():
        raise NotADirectoryError(
            f"Model path is not a directory: {model_path}"
        )

    required_model_files = [
        "vectorizer.pkl",
    ]
    missing_model_files = [
        f for f in required_model_files if not (model_path / f).exists()
    ]
    if missing_model_files:
        raise FileNotFoundError(
            f"Missing required model file(s) in {model_path}: {', '.join(missing_model_files)}"
        )

    logger.info("Startup path validation passed. All required dataset and model files present.")


# ── Lifespan: load all engines once at startup ────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: instantiate all Phase 1–9 AI engines and attach to app.state.
    Shutdown: cleanly release resources.
    """
    logger.info("=== RouteMaster AI Service starting up ===")
    logger.info("Project root: %s", _REPO_ROOT)
    logger.info("Processed data dir: %s", settings.processed_dir)
    logger.info("Model dir: %s", settings.model_dir)

    _validate_startup_paths(settings)

    # Phase 3 — Career Recommender
    logger.info("Loading Phase 3: CareerRecommender...")
    from src.career_recommender.recommender import CareerRecommender
    career_recommender = CareerRecommender(
        processed_dir=settings.processed_dir,
        model_dir=settings.model_dir,
    )

    # Phase 4 — Skill Gap Engine
    logger.info("Loading Phase 4: SkillGapEngine...")
    from src.gap_engine.gap_engine import SkillGapEngine
    gap_engine = SkillGapEngine(processed_dir=settings.processed_dir)

    # Phase 7 — Hybrid Recommender (course ranking)
    logger.info("Loading Phase 7: HybridRecommender...")
    from src.hybrid_recommender.engine import HybridRecommender
    hybrid_recommender = HybridRecommender(
        processed_dir=settings.processed_dir,
        model_dir=settings.model_dir,
    )

    # Phase 8 — Project Recommender
    logger.info("Loading Phase 8: ProjectRecommender...")
    from src.project_recommender.engine import ProjectRecommender
    project_recommender = ProjectRecommender(
        processed_dir=settings.processed_dir,
        model_dir=settings.model_dir,
    )

    # Phase 9 — Roadmap Generator
    logger.info("Loading Phase 9: RoadmapGenerator...")
    from src.roadmap_generator.engine import RoadmapGenerator
    roadmap_generator = RoadmapGenerator(
        processed_dir=settings.processed_dir,
        model_dir=settings.model_dir,
    )

    # ── Wire services ─────────────────────────────────────────────────────────
    career_svc    = CareerService(career_recommender)
    gap_svc       = SkillGapService(gap_engine)
    course_svc    = CourseService(hybrid_recommender)
    project_svc   = ProjectService(project_recommender)
    roadmap_svc   = RoadmapService(roadmap_generator)
    recommend_svc = RecommendationService(
        career_svc, gap_svc, course_svc, project_svc, roadmap_svc
    )

    # ── Attach to app.state ───────────────────────────────────────────────────
    app.state.career_service         = career_svc
    app.state.gap_service            = gap_svc
    app.state.course_service         = course_svc
    app.state.project_service        = project_svc
    app.state.roadmap_service        = roadmap_svc
    app.state.recommendation_service = recommend_svc

    logger.info("=== All engines loaded. Service is ready to handle requests. ===")
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("=== RouteMaster AI Service shutting down. ===")


# ── FastAPI application ───────────────────────────────────────────────────────

app = FastAPI(
    title="RouteMaster AI Service",
    description=(
        "AI-powered career, skill-gap, course, project, and roadmap recommendation service "
        "for RouteMaster — Mastering the Sequence of Complex Educational Goals.\n\n"
        "**Score conventions**:\n"
        "- `match_score`, `readiness_score`, `technical_match_score` → **0–100** (percentage)\n"
        "- `relevance_score`, `final_score`, component scores → **0–1.0** (normalized)\n\n"
        "**Note**: `target_role` accepts both canonical IDs (e.g. `CA_042`) and display "
        "titles (e.g. `AI Engineer`)."
    ),
    version=settings.ai_service_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Logging middleware ────────────────────────────────────────────────────────
register_logging_middleware(app)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(career.router)
app.include_router(skill_gap.router)
app.include_router(courses.router)
app.include_router(projects.router)
app.include_router(roadmap.router)
app.include_router(recommendation.router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "RouteMaster AI Service",
        "version": settings.ai_service_version,
        "docs": "/docs",
        "health": "/health",
    }
