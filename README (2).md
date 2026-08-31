# PathFinder

## AI Career PathFinder

> A personalized AI-powered career guidance platform that analyzes a learner's skills, interests, career goals, and progress to generate adaptive learning routes, course recommendations, skill-gap insights, and practical project recommendations.

---

## Project Overview

PathFinder helps learners answer:

- What career should I pursue?
- What skills do I already have?
- What skills am I missing?
- What should I learn next?
- Which courses are relevant to my goals?
- Which projects should I build?
- How am I progressing toward my career goal?

The platform combines a web application, backend API, and dedicated AI recommendation service to create a personalized learning journey.

---

## Key Features

### Personalized Career Recommendation

Analyzes user preferences, interests, skills, and goals to recommend suitable career directions.

### Adaptive Learning Routes

Generates a structured sequence of learning stages based on the learner's current skills and target career.

### Skill Gap Analysis

Identifies missing or developing skills required for the learner's target career.

### AI Course Recommendations

Recommends relevant learning resources using content similarity, skill matching, difficulty, and learner context.

### Project Recommendations

Suggests practical projects that help learners apply the skills required for their target career.

### Progress Tracking

Tracks completed learning stages, projects, skills, and overall route progress.

### Dynamic Dashboard

The dashboard provides a personalized overview of:

- Current learning stage
- Daily learning focus
- Route progress
- Skill development
- Recommended resources
- Projects on the learner's route

### Resource Discovery

Learners can browse and filter learning resources and open detailed resource pages.

---

# System Architecture

PathFinder uses a multi-service architecture:

```text
                    +---------------------+
                    |      Frontend       |
                    |   React + Vite      |
                    +----------+----------+
                               |
                               | REST API
                               v
                    +---------------------+
                    |      Backend        |
                    | FastAPI / Python    |
                    |                     |
                    | Authentication      |
                    | Users               |
                    | Routes              |
                    | Skills              |
                    | Projects            |
                    | Resources           |
                    +----------+----------+
                               |
                               | AI Requests
                               v
                    +---------------------+
                    |     AI Service      |
                    |      FastAPI        |
                    |                     |
                    | Career              |
                    | Recommendations     |
                    | Courses             |
                    | Projects            |
                    | Roadmaps            |
                    | Skill Gaps          |
                    +---------------------+
```

---

# Project Structure

```text
PathFinder/
|
+-- frontend/
|   +-- src/
|   |   +-- components/
|   |   +-- context/
|   |   +-- pages/
|   |   +-- services/
|   |   +-- App.jsx
|   |   +-- App.css
|   |   +-- index.css
|   |   +-- main.jsx
|   |
|   +-- package.json
|   +-- vite.config.js
|
+-- backend/
|   +-- app/
|   |   +-- routers/
|   |   |   +-- auth.py
|   |   |   +-- projects.py
|   |   |   +-- recommendations.py
|   |   |   +-- resources.py
|   |   |   +-- routes.py
|   |   |   +-- skills.py
|   |   |
|   |   +-- schemas/
|   |   +-- services/
|   |   +-- main.py
|   |
|   +-- requirements.txt
|
+-- ai-service/
|   +-- app/
|   |   +-- api/
|   |   |   +-- routes/
|   |   |       +-- career.py
|   |   |       +-- courses.py
|   |   |       +-- health.py
|   |   |       +-- projects.py
|   |   |       +-- recommendation.py
|   |   |       +-- roadmap.py
|   |   |       +-- skill_gap.py
|   |   |
|   |   +-- core/
|   |   +-- dependencies/
|   |   +-- schemas/
|   |   +-- services/
|   |   +-- main.py
|   |
|   +-- requirements-ai-service.txt
|   +-- Procfile
|   +-- README.md
|
+-- README.md
+-- .gitignore
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Styling | CSS + Tailwind CSS |
| UI Animation | Framer Motion |
| Icons | Lucide React |
| Data Visualization | Recharts |
| Interactive Route Visualization | React Flow |
| Backend | Python |
| Backend API | FastAPI |
| AI Service | FastAPI |
| Machine Learning | Python / scikit-learn |
| NLP | TF-IDF / text processing |
| Data Processing | pandas / NumPy |
| API Communication | REST |
| Version Control | Git / GitHub |

---

# AI Recommendation System

The AI service provides several recommendation capabilities.

## 1. Career Recommendation

```text
User Profile
     |
     +-- Interests
     +-- Existing Skills
     +-- Preferences
     +-- Career Goals
            |
            v
     AI Recommendation
            |
            v
     Career Suggestions
```

---

## 2. Course Recommendation

The course recommendation system considers learner context and course information to identify relevant resources.

```text
User Interests
      +
Existing Skills
      +
Target Career
      +
Learning Requirements
      |
      v
Feature Representation
      |
      v
Content Similarity
      +
Skill Matching
      |
      v
Ranking
      |
      v
Recommended Courses
```

For the underlying course recommendation component, content-based matching and skills-based matching are used to rank relevant courses.

---

## 3. Skill Gap Analysis

```text
Current Skills
      +
Target Career Requirements
      |
      v
Skill Comparison
      |
      v
Missing Skills
      |
      v
Priority Skill Gaps
      |
      v
Recommended Learning
```

This allows the platform to determine what the learner should focus on next.

---

## 4. Learning Roadmap

The AI service generates a learning sequence based on the learner's current state and target career.

```text
Current Skill Level
        |
        v
Skill Gap Analysis
        |
        v
Learning Requirements
        |
        v
Ordered Learning Stages
        |
        v
Personalized Roadmap
```

---

## 5. Project Recommendation

Projects are recommended according to the skills and learning stages associated with the learner's route.

```text
Target Career
      +
Skill Gaps
      +
Learning Progress
      |
      v
Project Matching
      |
      v
Practical Projects
```

---

# Course Recommendation Model

The course recommendation component uses content-based filtering and skills matching.

### Content Similarity

TF-IDF can be used to represent course information such as:

- Course title
- Course description
- Skills

Cosine similarity is then used to measure similarity between the learner's learning requirements and available courses.

### Skill Matching

The learner's existing skills are compared with the skills associated with courses.

A Jaccard-based overlap score can be used to measure skill similarity.

### Ranking

The recommendation score combines content relevance and skill relevance, with additional ranking considerations such as course difficulty and rating where applicable.

```text
User Profile
     |
     v
Text Representation
     |
     +---------------+
     v               v
Content Score    Skill Score
     |               |
     +-------+-------+
             v
       Final Ranking
             |
             v
       Top Recommendations
```

---

# Frontend Application

The frontend provides the learner-facing experience.

## Main Pages

| Page | Purpose |
|---|---|
| Landing | Introduces PathFinder |
| Login | User authentication |
| Register | Account creation |
| Onboarding | Collects learner information |
| Recommendation | Presents career recommendations |
| Overview | Personalized learner dashboard |
| My Routes | Displays learning routes |
| Route Details | Visualizes route stages |
| Skills | Tracks skill development |
| Resources | Displays recommended learning resources |
| Course Detail | Shows detailed resource information |
| Projects | Displays recommended projects |
| Project Detail | Shows project information |
| Progress | Tracks learner progress |
| Settings | User preferences |
| Guide | Platform guidance |

---

# API Structure

The backend provides APIs for the main application features.

```text
/api
|
+-- Authentication
+-- Recommendations
+-- Routes
+-- Skills
+-- Resources
+-- Projects
```

The AI service provides specialized endpoints for:

```text
AI Service
|
+-- Career Recommendation
+-- Course Recommendation
+-- Project Recommendation
+-- Roadmap Generation
+-- Skill Gap Analysis
+-- General Recommendation
+-- Health Check
```

---

# User Workflow

The complete learner workflow is:

```text
                  START
                    |
                    v
              Create Account
                    |
                    v
                Onboarding
                    |
                    v
        Enter Skills & Preferences
                    |
                    v
          Select Career Goal
                    |
                    v
        AI Career Recommendation
                    |
                    v
          Skill Gap Analysis
                    |
                    v
        Personalized Learning Route
                    |
          +---------+---------+
          v         v         v
       Courses   Projects   Skills
          |         |         |
          +---------+---------+
                    |
                    v
             Track Progress
                    |
                    v
          Adapt Learning Route
                    |
                    v
                   END
```

---

# Personalized Dashboard

The dashboard provides a single view of the learner's current journey.

It includes:

### Your Current Stage

Shows the learner's current position in the learning route.

### Daily Focus

Displays the recommended learning resource for the learner's current focus.

### Your Route Overview

Shows completed, current, and upcoming learning stages.

### Skills at a Glance

Provides a quick overview of tracked skills and their development status.

### Projects on Your Route

Displays projects associated with the learner's current learning journey.

---

# Data Flow

```text
User
 |
 v
React Frontend
 |
 v
Backend API
 |
 +--------------------> Database / Application Data
 |
 +--------------------> AI Service
                              |
                              +-- Career Recommendation
                              +-- Course Recommendation
                              +-- Skill Gap Analysis
                              +-- Roadmap Generation
                              +-- Project Recommendation
                                       |
                                       v
                                 AI Results
                                       |
                                       v
                                 Backend API
                                       |
                                       v
                                 React Frontend
```

---

# Setup

## Prerequisites

Install:

- Node.js
- npm
- Python
- pip
- Git

---

# 1. Clone the Repository

```bash
git clone <repository-url>
cd PathFinder
```

---

# 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 3. Backend Setup

From the project root:

```bash
cd backend
```

Create and activate a Python virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend using the project's configured FastAPI entry point.

---

# 4. AI Service Setup

From the project root:

```bash
cd ai-service
```

Install the AI service dependencies:

```bash
pip install -r requirements-ai-service.txt
```

Configure the environment variables using:

```text
.env.example
```

Then start the AI service using the configured FastAPI entry point.

---

# Environment Variables

The project uses environment variables for service configuration.

Example:

```text
# Backend
DATABASE_URL=...
SECRET_KEY=...

# AI Service
AI_SERVICE_URL=...
```

Do not commit actual secrets or API keys to Git.

Use `.env.example` as the configuration template.

---

# Running the Complete System

For local development, run the services separately.

### Terminal 1 — Backend

```bash
cd backend
# activate virtual environment
# start backend
```

### Terminal 2 — AI Service

```bash
cd ai-service
# activate virtual environment
# start AI service
```

### Terminal 3 — Frontend

```bash
cd frontend
npm run dev
```

The architecture is:

```text
Frontend
   |
   v
Backend
   |
   v
AI Service
```

---

# Evaluation

The recommendation component can be evaluated using measures such as:

- Catalogue size
- Coverage@10
- Average intra-list diversity
- Recommendation relevance
- Skill-match quality

The AI service also contains automated tests covering recommendation and API functionality.

---

# Challenges Faced

During development, the major challenges included:

### Personalization

Creating recommendations that reflect the learner's individual skills, preferences, and career goals.

### Skill Gap Identification

Mapping current learner capabilities against the skills required for a target career.

### Recommendation Quality

Combining multiple signals such as content relevance and skill overlap to produce useful recommendations.

### Service Integration

Connecting the frontend, application backend, and dedicated AI service while keeping responsibilities separated.

### Dynamic Learning Routes

Representing a learner's journey as stages that can evolve with their progress.

### Frontend Integration

Maintaining a consistent user experience while integrating recommendation and learning functionality across multiple pages.

---

# Future Improvements

Possible future enhancements include:

- More advanced embedding-based recommendations
- Continuous route adaptation using learner feedback
- Improved recommendation evaluation
- More career domains
- Real-time learning analytics
- Personalized project difficulty
- Recommendation explanations
- Learning-resource freshness detection
- Improved diversity and novelty of recommendations
- Integration with additional learning platforms

---

# Project Goals

PathFinder is designed to move beyond a simple course recommendation system.

Instead of answering only:

> "Which course should I take?"

the platform aims to answer:

> "What should I learn, in what order, why does it matter, and what should I build next to reach my career goal?"

---

# Team Development

The project follows a Git-based development workflow with feature branches and integration between frontend, backend, and AI-service components.

```text
main
 |
 +-- Frontend development
 |
 +-- AI / ML development
 |
 +-- Integration
       |
       v
    PathFinder
```

---

# License

This project is developed as an academic/project submission.
