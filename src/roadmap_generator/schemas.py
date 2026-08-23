from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class RoadmapRequest(BaseModel):
    """Pydantic request schema for generating personalized learning roadmaps."""
    skills: List[str] = Field(
        default=[], 
        description="List of raw strings representing the learner's current skills."
    )
    interests: Union[str, List[str]] = Field(
        default="", 
        description="Free text interests or lists of keywords representing the learner's interests."
    )
    target_role: str = Field(
        ..., 
        description="The canonical ID or Title of the target career path."
    )
    difficulty: str = Field(
        default="Any Level", 
        description="Selected difficulty preference: Any Level, Beginner, Intermediate, Advanced."
    )
    completed_courses: List[str] = Field(
        default=[], 
        description="List of completed course names to filter out."
    )
    courses_per_skill: int = Field(
        default=3, 
        description="Maximum number of course recommendations to attach to each skill node."
    )
    projects_per_skill: int = Field(
        default=2, 
        description="Maximum number of project recommendations to attach to each skill node."
    )

class CareerBrief(BaseModel):
    """Target career metadata summary."""
    career_id: str = Field(..., description="Canonical ID of the career.")
    career_title: str = Field(..., description="Display title of the career.")

class RoadmapSummary(BaseModel):
    """Deterministic progress and completion metrics."""
    total_required_skills: int = Field(..., description="Total required technical and prerequisite skills in roadmap subgraph.")
    completed_skills: int = Field(..., description="Number of required skills already possessed by the student.")
    remaining_skills: int = Field(..., description="Number of remaining skills to learn.")
    progress_percentage: float = Field(..., description="Roadmap progress percentage (0-100%).")
    critical_skills_remaining: int = Field(..., description="Number of Critical importance gaps remaining.")
    career_readiness_score: float = Field(..., description="Profile readiness fit percentage (0-100%).")

class CompactCourse(BaseModel):
    """Compact Course metadata attached to a roadmap node."""
    course_id: str = Field(..., description="Canonical course ID.")
    course_name: str = Field(..., description="Course title.")
    organization: str = Field(..., description="Course provider organization.")
    difficulty: str = Field(..., description="Difficulty level.")
    rating: float = Field(..., description="Average rating.")
    url: str = Field(..., description="Direct course URL.")
    relevance_score: float = Field(..., description="Matching score (0-1.0).")

class CompactProject(BaseModel):
    """Compact Project metadata attached to a roadmap node."""
    project_id: str = Field(..., description="Canonical project ID.")
    project_name: str = Field(..., description="Project title.")
    difficulty: str = Field(..., description="Difficulty level.")
    github_url: str = Field(..., description="Source code repository URL.")
    relevance_score: float = Field(..., description="Matching score (0-1.0).")
    skills_to_develop: List[str] = Field(default=[], description="Skills this project will help develop.")

class ReactFlowData(BaseModel):
    """Visual properties matching React Flow node standards."""
    label: str = Field(..., description="Label shown on the visual node.")
    status: str = Field(..., description="Completion state: completed, in_progress, next, locked.")
    priority: str = Field(..., description="Skill importance category.")
    reason: str = Field(..., description="Explainable reason text.")
    learning_action: str = Field(..., description="Action recommendation: learn_and_practice, learn_only, practice_only.")

class RoadmapNode(BaseModel):
    """Roadmap node representing a specific skill element."""
    id: str = Field(..., description="React Flow node ID (e.g. 'skill-SK_00001').")
    skill_id: str = Field(..., description="Canonical unique skill ID.")
    skill_name: str = Field(..., description="Display title of the skill.")
    status: str = Field(..., description="Learning state: completed, next, locked.")
    priority: str = Field(..., description="Skill priority level: Critical, High, Medium, Low.")
    sequence: int = Field(..., description="Learner order rank in roadmap topological sequence.")
    prerequisites: List[str] = Field(default=[], description="List of immediate prerequisite skill IDs.")
    courses: List[CompactCourse] = Field(default=[], description="Top courses attached to this skill.")
    projects: List[CompactProject] = Field(default=[], description="Top projects attached to this skill.")
    data: ReactFlowData = Field(..., description="Visual data bindings for React Flow frontend rendering.")

class RoadmapEdge(BaseModel):
    """Roadmap required connection representing a prerequisite path."""
    id: str = Field(..., description="React Flow edge ID (e.g. 'edge-SK_00001-SK_00002').")
    source: str = Field(..., description="Source React Flow node ID (predecessor prerequisite).")
    target: str = Field(..., description="Target React Flow node ID (dependent downstream skill).")
    relationship: str = Field(default="prerequisite", description="Type of connection.")

class RoadmapResponse(BaseModel):
    """Roadmap response payload containing React Flow compatible nodes, edges, and statistics."""
    career: CareerBrief = Field(..., description="Target career metadata.")
    summary: RoadmapSummary = Field(..., description="Roadmap progress metrics.")
    nodes: List[RoadmapNode] = Field(default=[], description="React Flow compatible skill nodes.")
    edges: List[RoadmapEdge] = Field(default=[], description="React Flow compatible connections.")
    warnings: List[str] = Field(default=[], description="Warnings log detailing cycles or degraded fallbacks.")
