from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from app.database import get_collection
from app.services.ai_service import AIServiceError, ai_service
from bson import ObjectId
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/routes", tags=["routes"])


class GenerateRouteRequest(BaseModel):
    career_title: Optional[str] = None
    goal: Optional[str] = None


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id", doc.get("id", "")))
    doc.pop("user_id", None)
    # Serialize any remaining datetime objects
    for k, v in doc.items():
        if hasattr(v, 'isoformat'):
            doc[k] = v.isoformat()
    return doc


@router.get("")
async def get_routes(current_user: dict = Depends(get_current_user)):
    routes_col = get_collection("routes")
    user_id = str(current_user["_id"])
    cursor = routes_col.find({"user_id": user_id})
    routes = []
    async for doc in cursor:
        routes.append(_serialize(doc))
    return routes


@router.get("/{route_id}")
async def get_route(route_id: str, current_user: dict = Depends(get_current_user)):
    routes_col = get_collection("routes")
    user_id = str(current_user["_id"])
    try:
        doc = await routes_col.find_one({"_id": ObjectId(route_id), "user_id": user_id})
    except Exception:
        doc = None
    if not doc:
        raise HTTPException(status_code=404, detail="Route not found")
    return _serialize(doc)


@router.post("/generate")
async def generate_user_route(
    req: GenerateRouteRequest,
    current_user: dict = Depends(get_current_user),
):
    routes_col = get_collection("routes")
    user_id = str(current_user["_id"])
    career_title = req.career_title or req.goal or current_user.get("target_career") or "AI / ML Engineer"

    try:
        route_data = ai_service.route(current_user, career_title)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    await routes_col.update_many({"user_id": user_id}, {"$set": {"is_current": False}})

    doc = {
        "user_id": user_id,
        **route_data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await routes_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.post("")
async def create_route(
    req: GenerateRouteRequest,
    current_user: dict = Depends(get_current_user),
):
    return await generate_user_route(req, current_user)


@router.patch("/{route_id}/pause")
async def pause_route(route_id: str, current_user: dict = Depends(get_current_user)):
    routes_col = get_collection("routes")
    user_id = str(current_user["_id"])
    await routes_col.update_one(
        {"_id": ObjectId(route_id), "user_id": user_id},
        {"$set": {"status": "paused", "updated_at": datetime.utcnow()}},
    )
    return {"success": True}


@router.patch("/{route_id}/resume")
async def resume_route(route_id: str, current_user: dict = Depends(get_current_user)):
    routes_col = get_collection("routes")
    user_id = str(current_user["_id"])
    await routes_col.update_one(
        {"_id": ObjectId(route_id), "user_id": user_id},
        {"$set": {"status": "active", "updated_at": datetime.utcnow()}},
    )
    return {"success": True}
