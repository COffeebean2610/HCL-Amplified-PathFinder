from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])

# Static skill catalog (in production, these would be per-user from DB)
SKILL_CATALOG = [
    {"id": "s1", "name": "Python", "category": "Programming", "proficiency": 92, "status": "strong"},
    {"id": "s2", "name": "SQL", "category": "Programming", "proficiency": 88, "status": "strong"},
    {"id": "s3", "name": "JavaScript", "category": "Programming", "proficiency": 72, "status": "developing"},
    {"id": "s4", "name": "Pandas", "category": "Data", "proficiency": 84, "status": "strong"},
    {"id": "s5", "name": "NumPy", "category": "Data", "proficiency": 82, "status": "strong"},
    {"id": "s6", "name": "Data Cleaning", "category": "Data", "proficiency": 79, "status": "strong"},
    {"id": "s7", "name": "Feature Engineering", "category": "Data", "proficiency": 61, "status": "developing"},
    {"id": "s8", "name": "Statistics", "category": "Data", "proficiency": 78, "status": "developing"},
    {"id": "s9", "name": "Supervised Learning", "category": "Machine Learning", "proficiency": 70, "status": "developing"},
    {"id": "s10", "name": "Classification", "category": "Machine Learning", "proficiency": 68, "status": "developing"},
    {"id": "s11", "name": "Regression", "category": "Machine Learning", "proficiency": 65, "status": "developing"},
    {"id": "s12", "name": "Model Evaluation", "category": "Machine Learning", "proficiency": 48, "status": "needs_attention"},
    {"id": "s13", "name": "Neural Networks", "category": "AI / Deep Learning", "proficiency": 34, "status": "needs_attention"},
    {"id": "s14", "name": "Deep Learning", "category": "AI / Deep Learning", "proficiency": 31, "status": "needs_attention"},
    {"id": "s15", "name": "Transformers", "category": "AI / Deep Learning", "proficiency": 14, "status": "needs_attention"},
    {"id": "s16", "name": "Docker", "category": "MLOps", "proficiency": 22, "status": "needs_attention"},
    {"id": "s17", "name": "Deployment", "category": "MLOps", "proficiency": 19, "status": "needs_attention"},
    {"id": "s18", "name": "Monitoring", "category": "MLOps", "proficiency": 18, "status": "needs_attention"},
]

SKILL_GAPS = [
    {"skill": "Model Evaluation", "current": 48, "required": 75, "gap": 27, "priority": "HIGH", "stage": "Machine Learning", "reason": "Currently blocking your next route stage"},
    {"skill": "Deep Learning", "current": 31, "required": 70, "gap": 39, "priority": "UPCOMING", "stage": "Deep Learning", "reason": "Required for the next route stage after Machine Learning"},
    {"skill": "MLOps", "current": 18, "required": 60, "gap": 42, "priority": "FUTURE", "stage": "MLOps", "reason": "Required for final production-ready AI systems"},
]


@router.get("")
async def get_skills(current_user: dict = Depends(get_current_user)):
    # In a full implementation, merge user skills with the catalog
    user_skills = current_user.get("skills", [])
    if not user_skills:
        return SKILL_CATALOG
    
    # Enrich catalog with user's proficiency
    catalog = []
    for skill in SKILL_CATALOG:
        if any(skill["name"].lower() in s.lower() or s.lower() in skill["name"].lower() for s in user_skills):
            catalog.append({**skill, "status": "strong", "proficiency": min(skill["proficiency"] + 10, 99)})
        else:
            catalog.append(skill)
    return catalog


@router.get("/gaps")
async def get_skill_gaps(current_user: dict = Depends(get_current_user)):
    target = current_user.get("target_career", "AI / ML Engineer")
    user_skills = current_user.get("skills", [])
    from ..services.route_service import compute_skill_gaps
    return compute_skill_gaps(user_skills, target)


@router.get("/target-profile")
async def get_target_profile(current_user: dict = Depends(get_current_user)):
    return {"target_career": current_user.get("target_career", ""), "skills": SKILL_CATALOG}
