from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from app.services.ai_service import AIServiceError, ai_service

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECTS = [
    {"id": "proj-1", "title": "Spam Detection Model", "status": "completed", "stage": "Machine Learning", "skills": ["Python", "NLP", "Classification", "Scikit-learn"], "difficulty": "Beginner", "estimated_hours": 4, "description": "Build a text classification model to detect spam emails."},
    {"id": "proj-2", "title": "Customer Churn Predictor", "status": "current", "stage": "Machine Learning", "skills": ["Python", "ML", "Feature Engineering", "Evaluation"], "difficulty": "Intermediate", "estimated_hours": 6, "description": "Predict customer churn using feature engineering and ensemble methods.", "milestones": [{"title": "Data preprocessing", "done": True}, {"title": "Feature engineering", "done": True}, {"title": "Model training", "done": False}, {"title": "Evaluation & report", "done": False}], "progress": 64},
    {"id": "proj-3", "title": "AI Recommendation Engine", "status": "upcoming", "stage": "Deep Learning", "skills": ["Recommendation Systems", "Embeddings", "RAG", "Python"], "difficulty": "Advanced", "estimated_hours": 10, "description": "Build an AI-powered recommendation engine using embeddings and RAG."},
    {"id": "proj-4", "title": "Predictive Maintenance System", "status": "recommended", "stage": "Machine Learning", "skills": ["Python", "Machine Learning", "Pandas", "Scikit-learn"], "difficulty": "Intermediate", "estimated_hours": 6, "description": "Build a system that predicts equipment failures before they happen.", "why": "Builds skills required for Model Evaluation and Feature Engineering."},
]


@router.get("")
async def get_projects(current_user: dict = Depends(get_current_user)):
    try:
        return ai_service.projects(current_user)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/recommended")
async def get_recommended(current_user: dict = Depends(get_current_user)):
    try:
        return ai_service.projects(current_user)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{project_id}")
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    try:
        project = next((p for p in ai_service.projects(current_user) if p["id"] == project_id), None)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return project
