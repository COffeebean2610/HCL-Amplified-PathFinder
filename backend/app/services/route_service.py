from typing import List, Dict, Any


# Career role → required skill stages
CAREER_ROUTES: Dict[str, List[Dict[str, Any]]] = {
    "AI / ML Engineer": {
        "stages": [
            {"id": "stage-1", "number": "01", "title": "Python Fundamentals", "skills": ["Python Basics", "Data Types", "Functions", "OOP"], "estimated_weeks": 2},
            {"id": "stage-2", "number": "02", "title": "Python & Data Handling", "skills": ["Pandas", "NumPy", "Data Cleaning", "Feature Engineering"], "estimated_weeks": 2},
            {"id": "stage-3", "number": "03", "title": "Statistics & Probability", "skills": ["Descriptive Statistics", "Probability", "Distributions", "Hypothesis Testing"], "estimated_weeks": 2},
            {"id": "stage-4", "number": "04", "title": "Machine Learning", "skills": ["Supervised Learning", "Regression", "Classification", "Feature Engineering", "Model Evaluation", "Ensemble Methods", "Model Optimization"], "estimated_weeks": 3},
            {"id": "stage-5", "number": "05", "title": "Deep Learning", "skills": ["Neural Networks", "CNNs", "RNNs", "Transformers"], "estimated_weeks": 3},
            {"id": "stage-6", "number": "06", "title": "MLOps", "skills": ["Docker", "Model Deployment", "Monitoring", "CI/CD for ML"], "estimated_weeks": 2},
        ],
        "level": "Intermediate → Advanced",
        "estimated_weeks": 14,
    },
    "Generative AI Engineer": {
        "stages": [
            {"id": "stage-1", "number": "01", "title": "Python Fundamentals", "skills": ["Python Basics", "Functions", "OOP", "Libraries"], "estimated_weeks": 2},
            {"id": "stage-2", "number": "02", "title": "Machine Learning Basics", "skills": ["Supervised Learning", "Classification", "Model Evaluation"], "estimated_weeks": 2},
            {"id": "stage-3", "number": "03", "title": "LLM Fundamentals", "skills": ["Transformers", "Attention", "Fine-tuning", "Prompt Engineering"], "estimated_weeks": 3},
            {"id": "stage-4", "number": "04", "title": "Embeddings & Vector DBs", "skills": ["Word Embeddings", "Sentence Transformers", "Pinecone", "Chroma"], "estimated_weeks": 2},
            {"id": "stage-5", "number": "05", "title": "RAG Systems", "skills": ["Document Loading", "Chunking", "Retrieval", "Response Generation"], "estimated_weeks": 3},
            {"id": "stage-6", "number": "06", "title": "AI Agents", "skills": ["Agent Frameworks", "Tool Use", "Memory", "Multi-agent Systems"], "estimated_weeks": 3},
            {"id": "stage-7", "number": "07", "title": "Deployment", "skills": ["Docker", "FastAPI", "Cloud Deployment", "Monitoring"], "estimated_weeks": 2},
        ],
        "level": "Intermediate → Advanced",
        "estimated_weeks": 17,
    },
    "Software Development Engineer": {
        "stages": [
            {"id": "stage-1", "number": "01", "title": "Programming Foundations", "skills": ["Python or JavaScript", "Data Structures", "Algorithms", "OOP"], "estimated_weeks": 3},
            {"id": "stage-2", "number": "02", "title": "Web Development", "skills": ["HTML/CSS", "JavaScript", "React", "REST APIs"], "estimated_weeks": 3},
            {"id": "stage-3", "number": "03", "title": "Backend Development", "skills": ["Node.js or FastAPI", "Databases", "Authentication", "Caching"], "estimated_weeks": 3},
            {"id": "stage-4", "number": "04", "title": "System Design", "skills": ["Scalability", "Load Balancing", "Microservices", "Message Queues"], "estimated_weeks": 3},
            {"id": "stage-5", "number": "05", "title": "DevOps", "skills": ["Docker", "CI/CD", "Cloud (AWS/GCP)", "Monitoring"], "estimated_weeks": 3},
        ],
        "level": "Beginner → Intermediate",
        "estimated_weeks": 15,
    },
    "Data Scientist": {
        "stages": [
            {"id": "stage-1", "number": "01", "title": "Python & Statistics", "skills": ["Python", "Statistics", "Probability", "NumPy/Pandas"], "estimated_weeks": 2},
            {"id": "stage-2", "number": "02", "title": "Data Analysis", "skills": ["EDA", "Visualization", "Feature Engineering", "SQL"], "estimated_weeks": 2},
            {"id": "stage-3", "number": "03", "title": "Machine Learning", "skills": ["Regression", "Classification", "Clustering", "Model Evaluation"], "estimated_weeks": 3},
            {"id": "stage-4", "number": "04", "title": "Advanced Analytics", "skills": ["Time Series", "Causal Inference", "A/B Testing", "Bayesian Methods"], "estimated_weeks": 3},
            {"id": "stage-5", "number": "05", "title": "Communication & Tools", "skills": ["Storytelling", "Dashboards", "SQL Advanced", "Spark"], "estimated_weeks": 2},
        ],
        "level": "Beginner → Advanced",
        "estimated_weeks": 12,
    },
}

CAREER_KEYWORDS = {
    "AI / ML Engineer": ["ml", "machine learning", "ai", "deep learning", "neural", "tensorflow", "pytorch", "scikit"],
    "Generative AI Engineer": ["genai", "generative", "llm", "gpt", "rag", "langchain", "embedding", "agents"],
    "Software Development Engineer": ["software", "web", "frontend", "backend", "fullstack", "developer", "react", "node"],
    "Data Scientist": ["data science", "analytics", "statistics", "visualization", "sql"],
}

SKILL_MAPPINGS = {
    "Python": ["Python Basics", "Python Fundamentals", "OOP"],
    "JavaScript": ["JavaScript", "Web Development"],
    "SQL": ["SQL", "Databases"],
    "React": ["React", "Frontend"],
    "Machine Learning": ["Supervised Learning", "Regression", "Classification"],
    "Deep Learning": ["Neural Networks", "CNNs", "Transformers"],
    "Pandas": ["Data Cleaning", "Data Analysis", "EDA"],
    "NumPy": ["NumPy", "Numerical Computing"],
    "Statistics": ["Descriptive Statistics", "Probability", "Distributions"],
    "Docker": ["Docker", "DevOps", "Containerization"],
}


def recommend_career(profile: dict) -> list:
    target = (profile.get("target_career") or "").lower()
    interests = [i.lower() for i in (profile.get("interests") or [])]
    skills = [s.lower() for s in (profile.get("skills") or [])]

    scores = {}
    for career, keywords in CAREER_KEYWORDS.items():
        score = 50  # base score
        for kw in keywords:
            if kw in target:
                score += 20
            if any(kw in i for i in interests):
                score += 10
            if any(kw in s for s in skills):
                score += 5
        scores[career] = min(score, 98)

    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for i, (career, match) in enumerate(ranked[:4]):
        career_data = CAREER_ROUTES.get(career, {})
        reasons = []
        if skills:
            reasons.append(f"You already know {', '.join(list(s.capitalize() for s in skills[:2]))}")
        if interests:
            reasons.append(f"Aligned with your interest in {interests[0].title()}")
        if career.lower() in target:
            reasons.append("Directly matches your stated career goal")
        if not reasons:
            reasons = ["Matches your current skill profile", "Strong demand in the industry"]

        results.append({
            "id": f"career-{i+1}",
            "title": career,
            "match": match,
            "is_primary": i == 0,
            "reasons": reasons[:3],
            "description": f"Build and deploy intelligent systems as a {career}. High demand, excellent compensation, and rapid growth in 2024–2026.",
        })
    return results


def generate_route(profile: dict, career_title: str) -> dict:
    """Generate a personalized learning route."""
    from datetime import datetime

    career_data = CAREER_ROUTES.get(career_title, CAREER_ROUTES["AI / ML Engineer"])
    user_skills = [s.lower() for s in (profile.get("skills") or [])]
    weekly_hours = profile.get("weekly_learning_hours", 7)

    # Build stages with status based on existing skills
    stages = []
    first_incomplete_found = False

    for raw_stage in career_data["stages"]:
        stage_skills = raw_stage["skills"]
        completed = [s for s in stage_skills if any(s.lower() in us or us in s.lower() for us in user_skills)]
        
        if len(completed) == len(stage_skills):
            status = "completed"
            upcoming = []
        elif not first_incomplete_found:
            status = "current"
            first_incomplete_found = True
            upcoming = [s for s in stage_skills if s not in completed][1:]
        else:
            status = "upcoming"
            completed = []
            upcoming = stage_skills

        stages.append({
            "id": raw_stage["id"],
            "number": raw_stage["number"],
            "title": raw_stage["title"],
            "status": status,
            "skills": stage_skills,
            "completed_skills": completed,
            "current_skill": (
                ([s for s in stage_skills if s not in completed][0] if [s for s in stage_skills if s not in completed] else None)
                if status == "current" else None
            ),
            "upcoming_skills": upcoming,
            "estimated_minutes": raw_stage.get("estimated_weeks", 2) * weekly_hours * 60 // 4,
        })

    completed_stages = sum(1 for s in stages if s["status"] == "completed")
    progress = int((completed_stages / len(stages)) * 100) if stages else 0
    current_stage = next((s["title"] for s in stages if s["status"] == "current"), stages[0]["title"] if stages else "")
    next_checkpoint = next((s["current_skill"] or s["title"] for s in stages if s["status"] == "current"), "")

    return {
        "title": career_title,
        "progress": progress,
        "status": "active",
        "is_current": True,
        "current_stage": current_stage,
        "next_checkpoint": next_checkpoint,
        "estimated_weeks": career_data["estimated_weeks"],
        "weekly_hours": weekly_hours,
        "level": career_data["level"],
        "total_stages": len(stages),
        "total_skills": sum(len(s["skills"]) for s in stages),
        "total_projects": len(stages),
        "stages": stages,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def compute_skill_gaps(user_skills: list, target_career: str) -> dict:
    career_data = CAREER_ROUTES.get(target_career, CAREER_ROUTES["AI / ML Engineer"])
    all_required = []
    for stage in career_data["stages"]:
        all_required.extend(stage["skills"])

    user_lower = [s.lower() for s in user_skills]
    current = [s for s in all_required if any(s.lower() in u or u in s.lower() for u in user_lower)]
    missing = [s for s in all_required if s not in current]

    gaps = []
    priorities = ["HIGH", "UPCOMING", "FUTURE"]
    for i, skill in enumerate(missing[:6]):
        gaps.append({
            "skill": skill,
            "current": max(0, 50 - i * 8),
            "required": 75,
            "gap": 25 + i * 5,
            "priority": priorities[min(i // 2, 2)],
        })

    return {
        "current_skills": current,
        "required_skills": all_required,
        "skill_gaps": gaps,
    }
