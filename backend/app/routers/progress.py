from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("")
async def get_progress(current_user: dict = Depends(get_current_user)):
    return {
        "overall": 68,
        "skills_completed": 8,
        "total_skills": 12,
        "current_skill": "Model Evaluation",
        "next_skill": "Ensemble Methods",
        "courses_completed": 6,
        "projects_completed": 1,
        "current_project": "Customer Churn Predictor",
        "this_week_hours": 4.5,
        "lessons_completed": 7,
        "skills_improved": 3,
        "streak": 6,
        "weekly_activity": [
            {"day": "Mon", "hours": 0.5},
            {"day": "Tue", "hours": 1.2},
            {"day": "Wed", "hours": 0},
            {"day": "Thu", "hours": 1.5},
            {"day": "Fri", "hours": 0.8},
            {"day": "Sat", "hours": 0.5},
            {"day": "Sun", "hours": 0},
        ],
        "skill_progression": [
            {"month": "Sep", "skills": 4},
            {"month": "Oct", "skills": 6},
            {"month": "Nov", "skills": 9},
            {"month": "Dec", "skills": 11},
            {"month": "Jan", "skills": 13},
            {"month": "Feb", "skills": 16},
        ],
    }
