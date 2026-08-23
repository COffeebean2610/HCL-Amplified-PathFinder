from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserPublic
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.database import get_collection
from app.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_public(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user["_id"]),
        name=user.get("name", ""),
        email=user.get("email", ""),
        onboarding_completed=user.get("onboarding_completed", False),
        target_career=user.get("target_career", ""),
        experience=user.get("experience", "Intermediate"),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: RegisterRequest):
    users = get_collection("users")
    email = data.email.lower().strip()

    existing = await users.find_one({"email": email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    doc = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "education": "",
        "branch": "",
        "experience": "Intermediate",
        "skills": [],
        "interests": [],
        "projects": "",
        "certifications": "",
        "target_career": "",
        "weekly_learning_hours": 7,
        "learning_preferences": {"style": "Project-based", "pace": "Balanced", "content": "Mixed"},
        "onboarding_completed": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await users.insert_one(doc)
    doc["_id"] = result.inserted_id

    try:
        await users.create_index("email", unique=True, background=True)
    except Exception:
        pass

    token = create_access_token(str(result.inserted_id))
    return AuthResponse(
        token=token,
        user=_user_to_public(doc),
        onboarding_completed=False,
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    users = get_collection("users")
    email = data.email.lower().strip()

    user = await users.find_one({"email": email})
    if not user or not verify_password(data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(str(user["_id"]))
    return AuthResponse(
        token=token,
        user=_user_to_public(user),
        onboarding_completed=user.get("onboarding_completed", False),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_to_public(current_user)


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
