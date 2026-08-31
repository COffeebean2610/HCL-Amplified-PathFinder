from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from app.services.ai_service import AIServiceError, ai_service

router = APIRouter(prefix="/resources", tags=["resources"])

RESOURCES = [
    {"id": "res-1", "title": "Machine Learning Model Evaluation", "subtitle": "Scikit-learn Documentation + Guided Module", "type": "course", "duration": "45 min", "level": "Intermediate", "skills": ["Model Evaluation", "Machine Learning"], "relevance": 92, "is_current": True, "description": "Master the complete model evaluation workflow.", "url": "#"},
    {"id": "res-2", "title": "Cross Validation Explained", "type": "article", "duration": "12 min", "level": "Intermediate", "skills": ["Model Evaluation"], "relevance": 88, "url": "#"},
    {"id": "res-3", "title": "Classification Metrics Deep Dive", "type": "video", "duration": "28 min", "level": "Intermediate", "skills": ["Classification", "Model Evaluation"], "relevance": 85, "url": "#"},
    {"id": "res-4", "title": "Hands-on Model Evaluation", "type": "practice", "duration": "40 min", "level": "Intermediate", "skills": ["Model Evaluation", "Machine Learning"], "relevance": 91, "url": "#"},
    {"id": "res-5", "title": "Feature Engineering for ML", "type": "course", "duration": "90 min", "level": "Intermediate", "skills": ["Feature Engineering", "Pandas"], "relevance": 78, "url": "#"},
    {"id": "res-6", "title": "Ensemble Methods Explained", "type": "video", "duration": "35 min", "level": "Intermediate", "skills": ["Ensemble Methods", "Machine Learning"], "relevance": 74, "url": "#"},
    {"id": "res-7", "title": "Introduction to Deep Learning", "type": "course", "duration": "120 min", "level": "Advanced", "skills": ["Deep Learning", "Neural Networks"], "relevance": 65, "url": "#"},
    {"id": "res-8", "title": "Statistics for Machine Learning", "type": "book", "duration": "3 hrs", "level": "Intermediate", "skills": ["Statistics", "Probability"], "relevance": 70, "url": "#"},
    {"id": "res-9", "title": "Docker for ML Engineers", "type": "documentation", "duration": "60 min", "level": "Advanced", "skills": ["Docker", "MLOps"], "relevance": 55, "url": "#"},
]


@router.get("")
async def get_resources(current_user: dict = Depends(get_current_user)):
    try:
        return ai_service.resources(current_user)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/recommended")
async def get_recommended(current_user: dict = Depends(get_current_user)):
    try:
        return ai_service.resources(current_user)[:5]
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{resource_id}")
async def get_resource(resource_id: str, current_user: dict = Depends(get_current_user)):
    try:
        resource = next((r for r in ai_service.resources(current_user) if r["id"] == resource_id), None)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not resource:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
