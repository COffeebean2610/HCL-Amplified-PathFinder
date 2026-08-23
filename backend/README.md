# RouteMaster Backend

FastAPI backend for RouteMaster — AI Career PathFinder.

## Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and set your MONGODB_URI and JWT_SECRET

# Run
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | — | Create account |
| POST | /auth/login | — | Sign in |
| GET | /auth/me | ✅ | Current user |
| GET | /users/me | ✅ | Full profile |
| PUT | /users/me | ✅ | Update profile |
| GET | /routes | ✅ | User routes |
| POST | /routes/generate | ✅ | Generate route |
| GET | /skills | ✅ | Skill profile |
| GET | /skills/gaps | ✅ | Skill gaps |
| GET | /resources | ✅ | Resources |
| GET | /projects | ✅ | Projects |
| GET | /progress | ✅ | Progress data |
| POST | /recommendations/career | ✅ | Career recommendation |
| POST | /recommendations/skill-gap | ✅ | Skill gap analysis |
| POST | /ai-guide/chat | ✅ | AI guide chat |

## Environment Variables

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=routemaster
JWT_SECRET=your-secret-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:5173
```
