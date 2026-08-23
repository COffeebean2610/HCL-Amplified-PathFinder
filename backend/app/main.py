from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import close_database, get_database
from app.routers import auth, users, routes, skills, resources, projects, progress, recommendations, ai_guide


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure indexes
    db = get_database()
    await db["users"].create_index("email", unique=True, background=True)
    print("✅ RouteMaster API started — MongoDB connected")
    yield
    # Shutdown
    await close_database()
    print("RouteMaster API shutting down")


app = FastAPI(
    title="RouteMaster API",
    version="1.0.0",
    description="AI Career PathFinder — Full-Stack API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(routes.router)
app.include_router(skills.router)
app.include_router(resources.router)
app.include_router(projects.router)
app.include_router(progress.router)
app.include_router(recommendations.router)
app.include_router(ai_guide.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "RouteMaster API"}
