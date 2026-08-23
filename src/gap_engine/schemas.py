from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SkillGapRequest(BaseModel):
    """Pydantic request schema for skill gap analysis."""
    current_skills: List[str] = Field(
        default=[], 
        description="List of raw strings representing the learner's current skills."
    )
    target_career: str = Field(
        ..., 
        description="The canonical ID or Title of the target career path (e.g., 'CAR_003' or 'AI Engineer')."
    )

class SkillDetail(BaseModel):
    """Pydantic model representing details of a matching or missing skill."""
    skill_id: str = Field(..., description="Canonical ID of the skill.")
    skill_name: str = Field(..., description="Display name of the skill.")
    skill_category: str = Field(..., description="Topological domain category of the skill.")
    importance: str = Field("Medium", description="Skill importance level (Critical, High, Medium, or soft-skill scores).")

class PrerequisiteGapDetail(BaseModel):
    """Pydantic model representing details of an indirect prerequisite gap."""
    skill_id: str = Field(..., description="Canonical ID of the prerequisite skill.")
    skill_name: str = Field(..., description="Display name of the prerequisite skill.")
    target_skill_id: str = Field(..., description="ID of the downstream skill requiring this prerequisite.")
    target_skill_name: str = Field(..., description="Name of the downstream skill requiring this prerequisite.")
    reason: str = Field(..., description="Explanation of why this skill is a prerequisite.")

class SequenceStep(BaseModel):
    """Pydantic model representing a single step in the recommended learning sequence."""
    sequence_number: int = Field(..., description="Learning order rank.")
    skill_id: str = Field(..., description="Canonical ID of the skill.")
    skill_name: str = Field(..., description="Display name of the skill.")
    skill_type: str = Field(..., description="Type (technical, transferable, or prerequisite).")
    priority: str = Field(..., description="Priority mapping (Critical, High, Medium, Low).")
    reason: str = Field(..., description="Explanation for why this step is recommended.")
    difficulty: str = Field("Intermediate", description="Normal difficulty tier.")
    prerequisites: List[str] = Field(default=[], description="List of immediate prerequisites IDs.")

class SkillGapResponse(BaseModel):
    """Pydantic response schema containing the complete skill gap intelligence report."""
    target_career_id: str = Field(..., description="Canonical ID of the target career.")
    target_career_title: str = Field(..., description="Display title of the target career.")
    target_career_domain: str = Field(..., description="Domain domain area of the career.")
    
    technical_match_percentage: float = Field(..., description="Technical skill coverage match score (0-100%).")
    transferable_match_percentage: float = Field(..., description="Transferable skill coverage match score (0-100%).")
    overall_readiness_score: float = Field(..., description="Combined readiness score (0-100%).")
    
    matched_technical_skills: List[SkillDetail] = Field(default=[], description="Direct required technical skills matching the profile.")
    missing_technical_skills: List[SkillDetail] = Field(default=[], description="Direct required technical skills missing from the profile.")
    
    matched_transferable_skills: List[SkillDetail] = Field(default=[], description="Direct required transferable skills matching the profile.")
    missing_transferable_skills: List[SkillDetail] = Field(default=[], description="Direct required transferable skills missing from the profile.")
    
    prerequisite_gaps: List[PrerequisiteGapDetail] = Field(default=[], description="Indirect missing prerequisite skills.")
    
    priority_gaps: Dict[str, List[SkillDetail]] = Field(
        default={"Critical": [], "High": [], "Medium": [], "Low": []}, 
        description="Gaps (direct + indirect) grouped by priority tiers (Critical, High, Medium, Low)."
    )
    
    learning_sequence: List[SequenceStep] = Field(default=[], description="Topologically ordered sequential learning roadmap.")
