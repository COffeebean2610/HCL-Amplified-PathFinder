"""
Common shared response models, canonical student profile, and standardized enums.
Phase 11: Standardized API Contracts
"""
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any, Union


# ── Standard Enums ────────────────────────────────────────────────────────────

class DifficultyEnum(str, Enum):
    ANY_LEVEL = "Any Level"
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    CONVERSANT = "Conversant"
    NOT_CALIBRATED = "Not Calibrated"


class PriorityEnum(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class NodeStatusEnum(str, Enum):
    COMPLETED = "completed"
    NEXT = "next"
    LOCKED = "locked"


class LearningActionEnum(str, Enum):
    LEARN_AND_PRACTICE = "learn_and_practice"
    LEARN_ONLY = "learn_only"
    PRACTICE_ONLY = "practice_only"


# ── Standardized Error & Status Schemas ───────────────────────────────────────

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Standardized error code (e.g., CAREER_NOT_FOUND, VALIDATION_ERROR)")
    message: str = Field(..., description="Human-readable explanation of the error")


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Always false for error responses")
    error: ErrorDetail


class Warning(BaseModel):
    component: str = Field(..., description="Subsystem that generated the warning (e.g., career, courses, projects)")
    code: str = Field(..., description="Machine-readable warning code")
    message: str = Field(..., description="Description of the degraded component")


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    service: str = "routemaster-ai"
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str = Field(..., examples=["ready", "degraded"])
    checks: Dict[str, str]


# ── Canonical Student Profile ─────────────────────────────────────────────────

class CanonicalStudentProfile(BaseModel):
    """
    Standardized Canonical Student Profile representation.
    Supports flexible aliases across all AI service endpoints.
    """
    student_id: Optional[str] = Field(
        default=None,
        description="Unique student identifier in the host LMS/platform (optional).",
        examples=["STU_10928"]
    )
    skills: List[str] = Field(
        default=[],
        description="List of student's current technical or soft skills.",
        examples=[["Python", "SQL", "Git"]]
    )
    current_skills: Optional[List[str]] = Field(
        default=None,
        description="Alias for 'skills'. If provided, will populate 'skills'.",
        examples=[["Python", "SQL", "Git"]]
    )
    interests: Union[str, List[str]] = Field(
        default="",
        description="Free-text interests or list of interest keywords.",
        examples=["Artificial Intelligence, Generative AI"]
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target career title or canonical ID (e.g., 'AI Engineer' or 'CA_042').",
        examples=["AI Engineer"]
    )
    target_career: Optional[str] = Field(
        default=None,
        description="Alias for 'target_role'. If provided, will populate 'target_role'.",
        examples=["AI Engineer"]
    )
    difficulty: str = Field(
        default="Any Level",
        description="Preferred course/project difficulty level.",
        examples=["Intermediate"]
    )
    preferred_difficulty: Optional[str] = Field(
        default=None,
        description="Alias for 'difficulty'.",
        examples=["Intermediate"]
    )
    completed_courses: List[str] = Field(
        default=[],
        description="List of course titles already completed by the student (excluded from recommendations).",
        examples=[["Introduction to Python"]]
    )
    learning_preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extensible learning style preferences dictionary (optional).",
        examples=[{"pacing": "self-paced", "hands_on_weight": 0.8}]
    )
    number_of_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of course and project recommendations to return (1–50)."
    )
    courses_per_skill: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max courses attached per roadmap skill node (0–10)."
    )
    projects_per_skill: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Max projects attached per roadmap skill node (0–10)."
    )

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize skills vs current_skills
            if "current_skills" in data and ("skills" not in data or not data["skills"]):
                data["skills"] = data["current_skills"]
            elif "skills" in data and ("current_skills" not in data or not data["current_skills"]):
                data["current_skills"] = data["skills"]

            # Normalize target_role vs target_career
            if "target_career" in data and ("target_role" not in data or not data["target_role"]):
                data["target_role"] = data["target_career"]
            elif "target_role" in data and ("target_career" not in data or not data["target_career"]):
                data["target_career"] = data["target_role"]

            # Normalize difficulty vs preferred_difficulty
            if "preferred_difficulty" in data and ("difficulty" not in data or not data["difficulty"]):
                data["difficulty"] = data["preferred_difficulty"]
            elif "difficulty" in data and ("preferred_difficulty" not in data or not data["preferred_difficulty"]):
                data["preferred_difficulty"] = data["difficulty"]

        return data
