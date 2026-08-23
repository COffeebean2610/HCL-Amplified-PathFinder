"""Roadmap request/response schemas (React Flow compatible)."""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union, Any


class RoadmapRequest(BaseModel):
    """Request schema for POST /ai/generate-roadmap."""

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
        examples=["Generative AI, LLMs"]
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
        description="Course names already completed — excluded from recommendations.",
        examples=[["Introduction to Python"]]
    )
    courses_per_skill: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max course recommendations per skill node (0–10).",
        examples=[3]
    )
    projects_per_skill: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Max project recommendations per skill node (0–10).",
        examples=[2]
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


class RoadmapCareer(BaseModel):
    career_id: str = Field(..., description="Canonical ID of the target career.", examples=["CA_042"])
    career_title: str = Field(..., description="Display title of the target career.", examples=["AI Engineer"])


class RoadmapSummary(BaseModel):
    total_required_skills: int = Field(..., description="Total nodes in the personalized roadmap subgraph.", examples=[18])
    completed_skills: int = Field(..., description="Number of required skills already mastered.", examples=[2])
    remaining_skills: int = Field(..., description="Number of skills still needing mastery.", examples=[16])
    progress_percentage: float = Field(..., description="Milestone completion rate (0.0–100.0%).", examples=[11.1])
    critical_skills_remaining: int = Field(..., description="Count of unmastered Critical-priority skills.", examples=[5])
    career_readiness_score: float = Field(..., description="Readiness percentage score (0.0–100.0).", examples=[14.3])


class RoadmapNodeData(BaseModel):
    label: str = Field(..., description="Display label for React Flow node.", examples=["Machine Learning"])
    status: str = Field(..., description="State: completed | next | locked", examples=["next"])
    priority: str = Field(..., description="Priority: Critical | High | Medium | Low", examples=["Critical"])
    reason: str = Field(..., description="Pedagogical rationale for this node.", examples=["Core skill required for AI Engineer."])
    learning_action: str = Field(..., description="Action: learn_and_practice | learn_only | practice_only", examples=["learn_and_practice"])


class RoadmapCourse(BaseModel):
    course_id: str = Field(..., description="Unique course identifier.", examples=["C_1042"])
    course_name: str = Field(..., description="Course title.", examples=["Machine Learning Specialization"])
    organization: str = Field(default="", description="Provider organization.", examples=["DeepLearning.AI"])
    difficulty: str = Field(..., description="Course difficulty level.", examples=["Intermediate"])
    rating: float = Field(default=0.0, description="Average rating score.", examples=[4.9])
    url: str = Field(..., description="Course URL.", examples=["https://coursera.org/..."])
    relevance_score: float = Field(..., description="Relevance score (0.0–1.0).", examples=[0.9142])


class RoadmapProject(BaseModel):
    project_id: str = Field(..., description="Unique project identifier.", examples=["PROJ_042"])
    project_name: str = Field(..., description="Project title.", examples=["Predictive Maintenance System"])
    difficulty: str = Field(..., description="Project difficulty.", examples=["Intermediate"])
    github_url: str = Field(..., description="Source code URL.", examples=["https://github.com/..."])
    relevance_score: float = Field(..., description="Relevance score (0.0–1.0).", examples=[0.875])
    skills_to_develop: List[str] = Field(default=[], description="Skills targeted by this project.", examples=[["Machine Learning", "Scikit-learn"]])


class RoadmapNode(BaseModel):
    id: str = Field(..., description="React Flow node identifier (e.g. 'skill-SK_00264').", examples=["skill-SK_00264"])
    skill_id: str = Field(..., description="Canonical taxonomy skill ID.", examples=["SK_00264"])
    skill_name: str = Field(..., description="Display name of the skill.", examples=["Machine Learning"])
    status: str = Field(..., description="Learning status: 'completed' (mastered), 'next' (unlocked, ready to learn), or 'locked' (missing prereqs).", examples=["next"])
    priority: str = Field(..., description="Skill importance tier (Critical | High | Medium | Low).", examples=["Critical"])
    sequence: int = Field(..., description="Topological sequence order rank.", examples=[1])
    prerequisites: List[str] = Field(default=[], description="List of immediate predecessor node IDs.", examples=[["skill-SK_00360"]])
    courses: List[RoadmapCourse] = Field(default=[], description="Top recommended courses attached to this node.")
    projects: List[RoadmapProject] = Field(default=[], description="Top recommended projects attached to this node.")
    data: RoadmapNodeData = Field(..., description="React Flow standard custom node data payload.")


class RoadmapEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier (e.g. 'edge-SK_00360-SK_00264').", examples=["edge-SK_00360-SK_00264"])
    source: str = Field(..., description="Source predecessor node ID.", examples=["skill-SK_00360"])
    target: str = Field(..., description="Target successor node ID.", examples=["skill-SK_00264"])
    relationship: str = Field(default="prerequisite", description="Dependency relationship type.", examples=["prerequisite"])


class RoadmapResponse(BaseModel):
    """Response schema for POST /ai/generate-roadmap (React Flow compatible)."""

    career: RoadmapCareer = Field(..., description="Target career overview.")
    summary: RoadmapSummary = Field(..., description="Summary statistics for learner's roadmap progression.")
    nodes: List[RoadmapNode] = Field(..., description="React Flow nodes list.")
    edges: List[RoadmapEdge] = Field(..., description="React Flow edges list.")
    warnings: List[str] = Field(default=[], description="Any cycle-breaking or graph resolution warnings.")
