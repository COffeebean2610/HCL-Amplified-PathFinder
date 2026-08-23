"""Course recommendation request/response schemas."""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Union, Any


VALID_DIFFICULTIES = {
    "Any Level", "Beginner", "Intermediate", "Advanced",
    "Conversant", "Not Calibrated"
}


class CourseRequest(BaseModel):
    """Request schema for POST /ai/recommend-courses."""

    student_id: Optional[str] = Field(
        default=None,
        description="Optional unique student identifier.",
        examples=["STU_1001"]
    )
    skills: List[str] = Field(
        default=[],
        description="Current learner skills.",
        examples=[["Python", "Machine Learning"]],
    )
    current_skills: Optional[List[str]] = Field(
        default=None,
        description="Alias for 'skills'.",
        examples=[["Python", "Machine Learning"]],
    )
    interests: Union[str, List[str]] = Field(
        default="",
        description="Learner interests (free text or list).",
        examples=["Artificial Intelligence, Deep Learning"]
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target career title or canonical ID.",
        examples=["AI Engineer"],
    )
    target_career: Optional[str] = Field(
        default=None,
        description="Alias for 'target_role'.",
        examples=["AI Engineer"],
    )
    difficulty: str = Field(
        default="Any Level",
        description="Difficulty filter: Any Level | Beginner | Intermediate | Advanced.",
        examples=["Intermediate"]
    )
    preferred_difficulty: Optional[str] = Field(
        default=None,
        description="Alias for 'difficulty'.",
        examples=["Intermediate"]
    )
    completed_courses: List[str] = Field(
        default=[],
        description="Course names to exclude from recommendation results.",
        examples=[["Introduction to Python"]]
    )
    number_of_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of courses to return (1–50).",
        examples=[5]
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

            if not data.get("target_role") and not data.get("target_career"):
                raise ValueError("Field 'target_role' or 'target_career' is required.")

        return data

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if v not in VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty '{v}'. Must be one of: {sorted(VALID_DIFFICULTIES)}"
            )
        return v


class CourseItem(BaseModel):
    course_id: str = Field(..., description="Unique course identifier in catalog.", examples=["C_1042"])
    course_name: str = Field(..., description="Official title of the course.", examples=["Machine Learning Specialization"])
    organization: str = Field(default="", description="Course provider or university.", examples=["DeepLearning.AI"])
    difficulty: str = Field(..., description="Difficulty level.", examples=["Intermediate"])
    rating: Optional[float] = Field(default=None, description="Average learner rating (out of 5.0).", examples=[4.9])
    url: str = Field(..., description="Direct URL to enroll/view course.", examples=["https://coursera.org/learn/machine-learning"])
    relevance_score: float = Field(
        description="Hybrid recommendation composite match score (0.0–1.0 scale).",
        examples=[0.9142]
    )
    matched_skills: List[str] = Field(
        default=[],
        description="Skills learner already possesses that are strengthened by this course.",
        examples=[["Python"]]
    )
    missing_skills_covered: List[str] = Field(
        default=[],
        description="Target career gap skills taught by this course.",
        examples=[["Machine Learning", "Supervised Learning"]]
    )
    prerequisite_status: str = Field(
        default="Ready",
        description="Prerequisite graph readiness: 'Ready' if prerequisites met, else 'Locked'.",
        examples=["Ready"]
    )
    reason: str = Field(
        ...,
        description="Explainable deterministic matching reason.",
        examples=["Teaches 2 critical gap skills (Machine Learning, Supervised Learning) with high rating."]
    )


class CourseResponse(BaseModel):
    """Response schema for POST /ai/recommend-courses."""

    target_role: str = Field(..., description="Target career role evaluated.", examples=["AI Engineer"])
    courses: List[CourseItem] = Field(..., description="Ranked list of course recommendations.")
    total: int = Field(..., description="Total count of returned courses.", examples=[5])
