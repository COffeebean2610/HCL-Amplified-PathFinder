"""Unified recommendation request/response schemas."""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union, Dict, Any
from .career import CareerRecommendationItem
from .skill_gap import MissingSkill, LearningStep
from .course import CourseItem
from .project import ProjectItem
from .roadmap import RoadmapNode, RoadmapEdge, RoadmapSummary, RoadmapCareer
from .common import Warning


class RecommendationRequest(BaseModel):
    """Request schema for POST /ai/recommend (full orchestration pipeline)."""

    student_id: Optional[str] = Field(
        default=None,
        description="Optional unique student identifier.",
        examples=["STU_1001"]
    )
    skills: List[str] = Field(
        default=[],
        description="Current learner skills.",
        examples=[["Python", "SQL", "Git"]],
    )
    current_skills: Optional[List[str]] = Field(
        default=None,
        description="Alias for 'skills'.",
        examples=[["Python", "SQL", "Git"]],
    )
    interests: Union[str, List[str]] = Field(
        default="",
        description="Learner interests.",
        examples=["Artificial Intelligence, Generative AI"]
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target career. If omitted, the top career recommendation is automatically selected.",
        examples=["AI Engineer"],
    )
    target_career: Optional[str] = Field(
        default=None,
        description="Alias for 'target_role'.",
        examples=["AI Engineer"],
    )
    difficulty: str = Field(
        default="Any Level",
        description="Difficulty preference.",
        examples=["Intermediate"]
    )
    preferred_difficulty: Optional[str] = Field(
        default=None,
        description="Alias for 'difficulty'.",
        examples=["Intermediate"]
    )
    completed_courses: List[str] = Field(
        default=[],
        description="Course names to exclude from recommendations.",
        examples=[["Introduction to Python"]]
    )
    learning_preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extensible learning style preferences dictionary (optional).",
        examples=[{"pacing": "self-paced"}]
    )
    number_of_results: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of course/project results.",
        examples=[5]
    )
    courses_per_skill: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max courses per roadmap skill node.",
        examples=[3]
    )
    projects_per_skill: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Max projects per roadmap skill node.",
        examples=[2]
    )
    top_k_careers: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of career recommendations considered if target_role is not provided.",
        examples=[1]
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


class RecommendationProfile(BaseModel):
    student_id: Optional[str] = Field(default=None, description="Student ID if provided.")
    skills: List[str] = Field(..., description="Active skills recognized in student profile.")
    interests: Union[str, List[str]] = Field(..., description="Interests recognized in student profile.")


class RecommendationSkillGap(BaseModel):
    current_skills: List[str] = Field(..., description="Student's known skills.")
    matched_skills: List[str] = Field(..., description="Career skills student already mastered.")
    missing_skills: List[MissingSkill] = Field(..., description="Direct missing technical skills.")
    readiness_score: float = Field(..., description="Career readiness percentage (0.0–100.0%).", examples=[22.5])


class RecommendationRoadmap(BaseModel):
    career: RoadmapCareer = Field(..., description="Target career details.")
    summary: RoadmapSummary = Field(..., description="Roadmap progression metrics.")
    nodes: List[RoadmapNode] = Field(..., description="React Flow nodes list.")
    edges: List[RoadmapEdge] = Field(..., description="React Flow edges list.")


class RecommendationResponse(BaseModel):
    """Response schema for POST /ai/recommend."""

    status: str = Field(
        default="success",
        description="'success' if all components succeeded, 'partial' if any non-fatal component degraded.",
        examples=["success"]
    )
    profile: RecommendationProfile = Field(..., description="Standardized student profile snapshot.")
    career: CareerRecommendationItem = Field(..., description="Target or top recommended career path.")
    skill_gap: RecommendationSkillGap = Field(..., description="Skill gap analysis summary.")
    courses: List[CourseItem] = Field(..., description="Top ranked course recommendations.")
    projects: List[ProjectItem] = Field(..., description="Top ranked engineering project recommendations.")
    roadmap: Optional[RecommendationRoadmap] = Field(default=None, description="Full personalized learning roadmap graph.")
    warnings: List[Warning] = Field(default=[], description="Structured warnings if partial fallback occurred.")
