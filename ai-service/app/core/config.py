"""
RouteMaster AI Service — Configuration
Reads from environment variables / .env file via pydantic-settings.
"""
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

# Project root resolution: ai-service/app/core/config.py -> 4 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def resolve_project_path(path_str: str) -> str:
    """Resolve a relative path against PROJECT_ROOT, keeping absolute paths intact."""
    p = Path(path_str)
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()
    return str(p)


class Settings(BaseSettings):
    """All environment-level configuration for the AI service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Service identity ────────────────────────────────────────────────────
    environment: str = "development"
    log_level: str = "INFO"
    ai_service_version: str = "1.0.0"
    ai_service_port: int = 8001

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://app.example.com"
    allowed_origins: str = "http://localhost:3000,http://localhost:5000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ── MongoDB ───────────────────────────────────────────────────────────────
    mongodb_uri: str = ""
    mongodb_database: str = "routemaster"
    mongodb_collection_courses: str = "courses"
    mongodb_collection_careers: str = "careers"
    mongodb_collection_projects: str = "projects"
    mongodb_collection_skills: str = "skills"

    # ── Vector Search ─────────────────────────────────────────────────────────
    vector_search_index: str = "routemaster_vector_index"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # ── AI Engine paths ───────────────────────────────────────────────────────
    processed_dir: str = "data/processed"
    model_dir: str = "model"

    @field_validator("processed_dir", "model_dir", mode="after")
    @classmethod
    def _resolve_paths(cls, v: str) -> str:
        return resolve_project_path(v)

    # ── Default result limits ─────────────────────────────────────────────────
    default_course_results: int = 5
    default_project_results: int = 5
    default_courses_per_skill: int = 3
    default_projects_per_skill: int = 2
    default_career_results: int = 5


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()

