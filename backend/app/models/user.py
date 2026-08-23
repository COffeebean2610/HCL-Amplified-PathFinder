from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class LearningPreferences(BaseModel):
    style: str = "Project-based"
    pace: str = "Balanced"
    content: str = "Mixed"
    weekly_hours: int = 7


class UserDocument(BaseModel):
    """MongoDB user document schema."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    email: str
    password_hash: str
    education: str = ""
    branch: str = ""
    experience: str = "Intermediate"
    skills: List[str] = []
    interests: List[str] = []
    projects: str = ""
    certifications: str = ""
    target_career: str = ""
    weekly_learning_hours: int = 7
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    onboarding_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
