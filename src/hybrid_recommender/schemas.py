from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class RecommendationRequest(BaseModel):
    """Pydantic request schema for hybrid personalized recommendation."""
    interests: Union[str, List[str]] = Field(
        default="", 
        description="Free text interests or lists of keywords representing the learner's interests."
    )
    current_skills: List[str] = Field(
        default=[], 
        description="List of raw strings representing the learner's current skills."
    )
    target_career: str = Field(
        ..., 
        description="The canonical ID or Title of the target career path."
    )
    completed_courses: List[str] = Field(
        default=[], 
        description="List of completed course names to be filtered out."
    )
    difficulty: str = Field(
        default="Any Level", 
        description="Selected difficulty preference: Any Level, Beginner, Intermediate, Advanced."
    )
    top_k: int = Field(
        default=10, 
        description="Number of top results to return."
    )
    weights: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Custom scoring weights (keys: skill_match, semantic_similarity, prerequisite, difficulty)."
    )

class CareerBrief(BaseModel):
    """Summarized target career metrics."""
    career_id: str = Field(..., description="Canonical ID of the career.")
    career_title: str = Field(..., description="Display title of the career.")
    career_match: float = Field(..., description="Calculated profile fit score (0-100%).")

class CourseRecommendationItem(BaseModel):
    """Personalized Course Recommendation item."""
    course_id: str = Field(..., description="Canonical course ID.")
    course_name: str = Field(..., description="Course title.")
    organization: str = Field("", description="Course provider organization.")
    course_difficulty: str = Field(..., description="Difficulty level.")
    course_rating: float = Field(0.0, description="Course average rating.")
    course_url: str = Field("#", description="Direct link URL.")
    
    final_score: float = Field(..., description="Weighted composite match score (0-1.0).")
    skill_match_score: float = Field(..., description="Missing skills coverage score (0-1.0).")
    semantic_score: float = Field(..., description="Semantic text alignment score (0-1.0).")
    prerequisite_score: float = Field(..., description="Prerequisite readiness score (0-1.0).")
    difficulty_score: float = Field(..., description="Difficulty fit score (0-1.0).")
    
    matched_skills: List[str] = Field(default=[], description="User's known skills taught by this course.")
    missing_relevant_skills: List[str] = Field(default=[], description="Missing target career skills taught by this course.")
    prerequisite_status: str = Field("Ready", description="Prerequisite status: 'Ready' or 'Locked'.")
    reason: str = Field(..., description="Structured deterministic matching reason.")

class ProjectRecommendationItem(BaseModel):
    """Personalized Project Recommendation item."""
    project_id: str = Field(..., description="Canonical project ID.")
    project_name: str = Field(..., description="Project title.")
    domain: str = Field(..., description="Project domain category.")
    difficulty: str = Field(..., description="Difficulty level.")
    github_url: str = Field("#", description="Source code link URL.")
    tech_stack: List[str] = Field(default=[], description="Tech stack tags list.")
    
    final_score: float = Field(..., description="Weighted composite match score (0-1.0).")
    skill_match_score: float = Field(..., description="Missing skills coverage score (0-1.0).")
    semantic_score: float = Field(..., description="Semantic text alignment score (0-1.0).")
    prerequisite_score: float = Field(..., description="Prerequisite readiness score (0-1.0).")
    difficulty_score: float = Field(..., description="Difficulty fit score (0-1.0).")
    
    matched_skills: List[str] = Field(default=[], description="User's known skills practiced by this project.")
    missing_relevant_skills: List[str] = Field(default=[], description="Missing target career skills practiced by this project.")
    prerequisite_status: str = Field("Ready", description="Prerequisite status: 'Ready' or 'Locked'.")
    reason: str = Field(..., description="Structured deterministic matching reason.")

class RecommendationResponse(BaseModel):
    """Response payload containing hybrid recommendations."""
    career: CareerBrief = Field(..., description="Target career overview.")
    skill_gaps: List[str] = Field(default=[], description="Missing technical skills for the career.")
    courses: List[CourseRecommendationItem] = Field(default=[], description="Top ranked recommended courses.")
    projects: List[ProjectRecommendationItem] = Field(default=[], description="Top ranked recommended projects.")
