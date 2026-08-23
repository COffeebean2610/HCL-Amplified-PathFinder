from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RouteStage(BaseModel):
    id: str
    number: str
    title: str
    status: str = "upcoming"
    skills: List[str] = []
    completed_skills: List[str] = []
    current_skill: Optional[str] = None
    upcoming_skills: List[str] = []
    estimated_minutes: Optional[int] = None


class RouteDocument(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    progress: int = 0
    status: str = "active"
    is_current: bool = True
    current_stage: str = ""
    next_checkpoint: str = ""
    estimated_weeks: int = 12
    weekly_hours: int = 7
    level: str = "Beginner → Intermediate"
    total_stages: int = 0
    total_skills: int = 0
    total_projects: int = 0
    stages: List[RouteStage] = []
    created_at: datetime = None
    updated_at: datetime = None
