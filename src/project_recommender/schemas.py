from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class ProjectRecommendationRequest(BaseModel):
    """Pydantic request schema for personalized engineering project recommendations."""
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
    top_k: int = Field(
        default=5, 
        description="Number of top results to return."
    )
    weights: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Custom scoring weights (keys: skill_gap_coverage, semantic_similarity, prerequisite_readiness, difficulty_compatibility)."
    )

class CareerSummary(BaseModel):
    """Target career identifier."""
    career_id: str = Field(..., description="Canonical ID of the career.")
    career_title: str = Field(..., description="Display title of the career.")

class RecommendedProjectItem(BaseModel):
    """Personalized Engineering Project item."""
    project_id: str = Field(..., description="Canonical project ID.")
    project_name: str = Field(..., description="Project title.")
    domain: str = Field(..., description="Project domain category.")
    difficulty: str = Field(..., description="Difficulty level.")
    github_url: str = Field("#", description="Source code link URL.")
    
    final_score: float = Field(..., description="Weighted composite match score (0-1.0).")
    skill_gap_coverage_score: float = Field(..., description="Missing skills weighted coverage score (0-1.0).")
    semantic_score: float = Field(..., description="Semantic text alignment score (0-1.0).")
    prerequisite_score: float = Field(..., description="Prerequisite readiness score (0-1.0).")
    difficulty_score: float = Field(..., description="Difficulty fit score (0-1.0).")
    
    matched_existing_skills: List[str] = Field(default=[], description="User's known skills practiced by this project.")
    skills_to_develop: List[str] = Field(default=[], description="Missing target career skills practiced by this project.")
    prerequisite_status: str = Field("Ready", description="Prerequisite status: 'Ready' or 'Locked'.")
    reason: str = Field(..., description="Structured deterministic matching reason.")

class ProjectRecommendationResponse(BaseModel):
    """Response payload containing personalized project recommendations."""
    career: CareerSummary = Field(..., description="Target career details.")
    skill_gaps: List[str] = Field(default=[], description="Missing technical skills for the career.")
    projects: List[RecommendedProjectItem] = Field(default=[], description="Top ranked recommended projects.")
