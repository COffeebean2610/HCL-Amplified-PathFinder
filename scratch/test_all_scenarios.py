import json
import sys
import os

sys.path.insert(0, ".")
sys.path.insert(0, "ai-service")

from src.career_recommender.recommender import CareerRecommender
from src.gap_engine.gap_engine import SkillGapEngine
from src.hybrid_recommender.engine import HybridRecommender
from src.project_recommender.engine import ProjectRecommender
from src.roadmap_generator.engine import RoadmapGenerator
from src.roadmap_generator.schemas import RoadmapRequest
from src.hybrid_recommender.schemas import RecommendationRequest as CourseReq
from src.project_recommender.schemas import ProjectRecommendationRequest as ProjReq
from src.gap_engine.schemas import SkillGapRequest


def run_pipeline_test(name: str, payload: dict):
    print(f"\n==================================================", flush=True)
    print(f"TEST SCENARIO: {name}", flush=True)
    print(f"==================================================", flush=True)
    
    # 1. Career Recommender
    print("\n--- 1. Career Recommendation ---", flush=True)
    cr = CareerRecommender()
    career_res = cr.recommend({"current_skills": payload["skills"], "interests": payload["interests"], "top_k": 3})
    top_career = career_res["recommendations"][0] if career_res.get("recommendations") else None
    career_title = (top_career.get("career") or top_career.get("career_title")) if top_career else "AI Engineer"
    print("Top Career:", career_title, "| Match Score:", top_career.get("match_score") if top_career else "N/A", flush=True)

    # 2. Skill Gap
    print("\n--- 2. Skill Gap Analysis ---", flush=True)
    ge = SkillGapEngine()
    target_role = payload.get("target_role") or career_title
    gap_res = ge.calculate_gap(SkillGapRequest(current_skills=payload["skills"], target_career=target_role))
    missing_names = [s.skill_name for s in gap_res.missing_technical_skills]
    print(f"Target Role: {target_role}", flush=True)
    print(f"Matched Skills ({len(gap_res.matched_technical_skills)}): {[s.skill_name for s in gap_res.matched_technical_skills]}", flush=True)
    print(f"Missing Skills ({len(missing_names)}): {missing_names}", flush=True)
    print(f"Readiness Score: {gap_res.overall_readiness_score}%", flush=True)

    # 3. Courses
    print("\n--- 3. Course Recommendations ---", flush=True)
    hr = HybridRecommender()
    course_res = hr.recommend(CourseReq(current_skills=payload["skills"], target_career=target_role, top_k=3, completed_courses=payload.get("completed_courses", [])))
    print(f"Recommended Courses ({len(course_res.courses)}):", flush=True)
    for c in course_res.courses:
        print(f"  - {c.course_name} (Score: {c.final_score}, Teaches: {c.missing_relevant_skills})", flush=True)

    # 4. Projects
    print("\n--- 4. Project Recommendations ---", flush=True)
    pr = ProjectRecommender()
    proj_res = pr.recommend_projects(ProjReq(skills=payload["skills"], target_role=target_role, top_k=2))
    print(f"Recommended Projects ({len(proj_res.projects)}):", flush=True)
    for p in proj_res.projects:
        print(f"  - {p.project_name} (Score: {p.final_score}, Develops: {p.skills_to_develop})", flush=True)

    # 5. Roadmap
    print("\n--- 5. Personalized Roadmap ---", flush=True)
    rg = RoadmapGenerator()
    roadmap_res = rg.generate_roadmap(RoadmapRequest(skills=payload["skills"], target_role=target_role, completed_courses=payload.get("completed_courses", [])))
    print(f"Total Nodes: {len(roadmap_res.nodes)} | Edges: {len(roadmap_res.edges)}", flush=True)
    print(f"Summary: {roadmap_res.summary.completed_skills}/{roadmap_res.summary.total_required_skills} completed ({roadmap_res.summary.progress_percentage}%) | Readiness: {roadmap_res.summary.career_readiness_score}%", flush=True)
    
    node_summary = []
    for n in roadmap_res.nodes:
        node_summary.append(f"{n.skill_name} ({n.status})")
    print(f"Sequence: {' -> '.join(node_summary)}", flush=True)
    print(f"Warnings: {roadmap_res.warnings}", flush=True)
    print("STATUS: PASS (Scenario executed cleanly)", flush=True)


def main():
    scenarios = {
        "Scenario A: Beginner AI Engineer": {
            "skills": ["Python"],
            "interests": "Artificial Intelligence",
            "target_role": "AI Engineer",
            "completed_courses": ["Introduction to Python"]
        },
        "Scenario B: Intermediate AI Engineer": {
            "skills": ["Python", "SQL", "Git", "Mathematics"],
            "interests": "Generative AI, LLMs",
            "target_role": "AI Engineer",
            "completed_courses": ["Introduction to Python"]
        },
        "Scenario C: Generative AI Learner": {
            "skills": ["Python", "Mathematics", "Machine Learning", "Deep Learning", "NLP"],
            "interests": "LLMs, RAG, Fine-tuning",
            "target_role": "Generative AI Engineer",
            "completed_courses": ["Neural Networks and Deep Learning"]
        },
        "Scenario D: SDE Learner": {
            "skills": ["Python", "Git", "SQL"],
            "interests": "Backend Development, Cloud",
            "target_role": "Software Development Engineer",
            "completed_courses": []
        }
    }

    for name, payload in scenarios.items():
        run_pipeline_test(name, payload)


if __name__ == "__main__":
    main()
