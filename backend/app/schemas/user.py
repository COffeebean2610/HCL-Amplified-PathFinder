from pydantic import BaseModel
from typing import Optional, List


class LearningPreferencesUpdate(BaseModel):
    style: Optional[str] = None
    pace: Optional[str] = None
    content: Optional[str] = None
    weekly_hours: Optional[int] = None


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    branch: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    target_career: Optional[str] = None
    weekly_learning_hours: Optional[int] = None
    onboarding_completed: Optional[bool] = None
    learning_preferences: Optional[LearningPreferencesUpdate] = None


class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    education: str = ""
    branch: str = ""
    experience: str = "Intermediate"
    skills: List[str] = []
    interests: List[str] = []
    projects: str = ""
    certifications: str = ""
    target_career: str = ""
    weekly_learning_hours: int = 7
    onboarding_completed: bool = False
    learning_preferences: dict = {}
