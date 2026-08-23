"""Skill gap request/response schemas."""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any


class SkillGapRequest(BaseModel):
    """Request schema for POST /ai/skill-gap."""

    student_id: Optional[str] = Field(
        default=None,
        description="Optional unique student identifier.",
        examples=["STU_1001"]
    )
    skills: List[str] = Field(
        default=[],
        description="Current learner skills (raw text — normalized internally).",
        examples=[["Python", "SQL", "Git"]],
    )
    current_skills: Optional[List[str]] = Field(
        default=None,
        description="Alias for 'skills'.",
        examples=[["Python", "SQL", "Git"]],
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target career title or canonical ID (e.g. 'AI Engineer' or 'CA_042').",
        examples=["AI Engineer"],
    )
    target_career: Optional[str] = Field(
        default=None,
        description="Alias for 'target_role'.",
        examples=["AI Engineer"],
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

            # Validate target presence
            if not data.get("target_role") and not data.get("target_career"):
                raise ValueError("Field 'target_role' or 'target_career' is required.")

        return data


class SkillGapCareer(BaseModel):
    career_id: str = Field(..., description="Canonical ID of the target career.", examples=["CA_042"])
    career_title: str = Field(..., description="Display title of the target career.", examples=["AI Engineer"])
    career_domain: str = Field(default="", description="Domain category.", examples=["Artificial Intelligence"])


class MissingSkill(BaseModel):
    skill_id: str = Field(..., description="Canonical skill identifier.", examples=["SK_00264"])
    skill_name: str = Field(..., description="Display name of the missing skill.", examples=["Machine Learning"])
    skill_category: str = Field(default="Technical", description="Taxonomy domain category.", examples=["AI & ML"])
    priority: str = Field(description="Priority tier: Critical | High | Medium | Low", examples=["Critical"])


class PrerequisiteGap(BaseModel):
    skill_id: str = Field(..., description="Canonical prerequisite skill ID.", examples=["SK_00360"])
    skill_name: str = Field(..., description="Prerequisite skill name.", examples=["Python"])
    required_by_skill_id: str = Field(..., description="Downstream skill requiring this prerequisite.", examples=["SK_00264"])
    required_by_skill_name: str = Field(..., description="Downstream skill title.", examples=["Machine Learning"])
    reason: str = Field(..., description="Prerequisite dependency rationale.", examples=["Machine Learning requires Python as a programming prerequisite."])


class LearningStep(BaseModel):
    sequence_number: int = Field(..., description="Topological rank in recommended study sequence.", examples=[1])
    skill_id: str = Field(..., description="Canonical skill identifier.", examples=["SK_00264"])
    skill_name: str = Field(..., description="Display name of the skill.", examples=["Machine Learning"])
    skill_type: str = Field(default="technical", description="Skill type (technical | transferable | prerequisite).", examples=["technical"])
    priority: str = Field(description="Priority ranking.", examples=["Critical"])
    reason: str = Field(..., description="Sequencing explanation.", examples=["Direct critical requirement for target career."])
    prerequisites: List[str] = Field(default=[], description="List of immediate required skill IDs.", examples=[["SK_00360"]])


class SkillGapResponse(BaseModel):
    """Response schema for POST /ai/skill-gap."""

    career: SkillGapCareer = Field(..., description="Target career overview.")
    readiness_score: float = Field(description="Overall career readiness score (0–100 scale).", examples=[25.0])
    technical_match_pct: float = Field(description="Direct technical skill coverage percentage (0–100 scale).", examples=[20.0])
    current_skills: List[str] = Field(default=[], description="Input skills provided by student.")
    matched_skills: List[str] = Field(default=[], description="Skills already mastered by student.")
    missing_skills: List[MissingSkill] = Field(default=[], description="Direct required skills currently missing.")
    prerequisite_gaps: List[PrerequisiteGap] = Field(default=[], description="Transitive prerequisite dependencies identified.")
    learning_sequence: List[LearningStep] = Field(default=[], description="Prerequisite-ordered topological learning sequence.")
