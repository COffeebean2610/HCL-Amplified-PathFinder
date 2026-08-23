import json
import sys
import os

sys.path.insert(0, ".")
sys.path.insert(0, "ai-service")

from src.roadmap_generator.engine import RoadmapGenerator
from src.roadmap_generator.schemas import RoadmapRequest

def main():
    generator = RoadmapGenerator()
    req_data = {
        "student_id": "STU_1001",
        "skills": ["Python", "SQL", "Git"],
        "current_skills": ["Python", "SQL", "Git"],
        "interests": "Generative AI, LLMs",
        "target_role": "AI Engineer",
        "target_career": "AI Engineer",
        "difficulty": "Intermediate",
        "preferred_difficulty": "Intermediate",
        "completed_courses": ["Introduction to Python"],
        "courses_per_skill": 3,
        "projects_per_skill": 2
    }
    req = RoadmapRequest(**req_data)
    res = generator.generate_roadmap(req)
    res_dict = res.model_dump()
    print("=== ROADMAP GENERATED SUCCESSFULLY ===")
    print(json.dumps(res_dict, indent=2))

if __name__ == "__main__":
    main()
