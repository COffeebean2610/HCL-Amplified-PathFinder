"""Project recommendation request/response schemas."""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Union, Any

VALID_DIFFICULTIES = {
    "Any Level", "Beginner", "Intermediate", "Advanced",
    "Conversant", "Not Calibrated"
}


class ProjectRequest(BaseModel):
    """Request schema for POST /ai/recommend-projects."""

    student_id: Optional[str] = Field(
        default=None,
        description="Optional unique student identifier.",
        examples=["STU_1001"]
    )
    skills: List[str] = Field(
        default=[],
        description="Current learner skills.",
        examples=[["Python", "SQL"]],
    )
    current_skills: Optional[List[str]] = Field(
        default=None,
        description="Alias for 'skills'.",
        examples=[["Python", "SQL"]],
    )
    interests: Union[str, List[str]] = Field(
        default="",
        description="Learner interests (free text or list).",
        examples=["Computer Vision, Autonomous Systems"]
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target career — skill gaps are derived automatically from this.",
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
    number_of_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of projects to return (1–50).",
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


class ProjectItem(BaseModel):
    project_id: str = Field(..., description="Unique project ID from dataset.", examples=["PROJ_042"])
    project_name: str = Field(..., description="Engineering project title.", examples=["Autonomous Drone Navigation System"])
    domain: str = Field(default="", description="Engineering domain category.", examples=["Robotics & AI"])
    difficulty: str = Field(..., description="Project difficulty tier.", examples=["Intermediate"])
    github_url: str = Field(..., description="GitHub repository reference URL.", examples=["https://github.com/example/drone-nav"])
    relevance_score: float = Field(
        description="Skill-gap-aware composite match score (0.0–1.0 scale).",
        examples=[0.8875]
    )
    skills_to_develop: List[str] = Field(
        default=[],
        description="Target career missing skills developed by completing this project.",
        examples=[["Computer Vision", "Reinforcement Learning"]]
    )
    matched_existing_skills: List[str] = Field(
        default=[],
        description="Current skills the student can practice in this project.",
        examples=[["Python", "Git"]]
    )
    prerequisite_status: str = Field(
        default="Ready",
        description="Readiness status ('Ready' or 'Locked').",
        examples=["Ready"]
    )
    reason: str = Field(
        ...,
        description="Explainable recommendation reason emphasizing gap coverage.",
        examples=["Develops 2 critical missing skills while practicing known Python and Git proficiencies."]
    )


class ProjectResponse(BaseModel):
    """Response schema for POST /ai/recommend-projects."""

    target_role: str = Field(..., description="Target career evaluated.", examples=["AI Engineer"])
    projects: List[ProjectItem] = Field(..., description="Ranked list of engineering projects.")
    total: int = Field(..., description="Total count of projects returned.", examples=[5])
