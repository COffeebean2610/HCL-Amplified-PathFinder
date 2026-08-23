import re

CAREER_SCHEMA = {
    "career_id": {"type": str, "required": True, "regex": r"^CAR_\d{3}$"},
    "career_title": {"type": str, "required": True},
    "career_domain": {"type": str, "required": True},
    "career_description": {"type": str, "required": True},
}

SKILL_SCHEMA = {
    "skill_id": {"type": str, "required": True, "regex": r"^SK_\d{5}$"},
    "skill_name": {"type": str, "required": True},
    "normalized_name": {"type": str, "required": True},
    "skill_category": {"type": str, "required": True},
    "skill_type": {"type": str, "required": True, "allowed": ["technical", "transferable", "other"]},
}

COURSE_SCHEMA = {
    "course_id": {"type": str, "required": True, "regex": r"^CRS_\d{4}$"},
    "course_name": {"type": str, "required": True},
    "organization": {"type": str, "required": True},
    "difficulty": {"type": str, "required": True, "allowed": ["Beginner", "Intermediate", "Advanced", "Conversant", "Not Calibrated", "Any Level"]},
    "original_difficulty": {"type": str, "required": True},
    "rating": {"type": (float, type(None)), "required": False},
    "original_rating": {"type": str, "required": True},
    "url": {"type": str, "required": True},
    "description": {"type": str, "required": True},
    "skills": {"type": list, "required": True},  # List of canonical skill IDs
    "skills_raw": {"type": str, "required": True}
}

PROJECT_SCHEMA = {
    "project_id": {"type": str, "required": True, "regex": r"^PROJ_\d{3}$"},
    "project_name": {"type": str, "required": True},
    "domain": {"type": str, "required": True},
    "difficulty": {"type": str, "required": True, "allowed": ["Beginner", "Intermediate", "Advanced"]},
    "github_url": {"type": (str, type(None)), "required": False},
    "description": {"type": str, "required": True},
    "tech_stack": {"type": list, "required": True},
    "tags": {"type": list, "required": True},
    "skills": {"type": list, "required": True},
    "skills_raw": {"type": str, "required": True}
}

DEPENDENCY_SCHEMA = {
    "dependency_id": {"type": str, "required": True, "regex": r"^DEP_\d{3}$"},
    "source_skill_id": {"type": str, "required": True, "regex": r"^SK_\d{5}$"},
    "source_skill_name": {"type": str, "required": True},
    "target_skill_id": {"type": str, "required": True, "regex": r"^SK_\d{5}$"},
    "target_skill_name": {"type": str, "required": True},
    "relationship": {"type": str, "required": True, "allowed": ["prerequisite", "recommended_prerequisite", "strong_prerequisite"]},
    "reason": {"type": str, "required": True},
    "difficulty": {"type": str, "required": True, "allowed": ["Beginner", "Intermediate", "Advanced"]},
    "domain": {"type": str, "required": True}
}

CAREER_INTEREST_SCHEMA = {
    "career_interest_id": {"type": str, "required": True, "regex": r"^CI_\d{3}$"},
    "career_id": {"type": str, "required": True, "regex": r"^CAR_\d{3}$"},
    "interest_type": {"type": str, "required": True},
    "interest_score": {"type": float, "required": True},
    "interest_description": {"type": str, "required": True}
}

CAREER_SKILL_SCHEMA = {
    "career_skill_id": {"type": str, "required": True, "regex": r"^CS_\d{4}$"},
    "career_id": {"type": str, "required": True, "regex": r"^CAR_\d{3}$"},
    "skill_id": {"type": str, "required": True, "regex": r"^SK_\d{5}$"},
    "importance": {"type": str, "required": True},
    "in_demand": {"type": str, "required": True},  # Yes/No
    "hot_technology": {"type": str, "required": True},  # Yes/No
    "description": {"type": str, "required": True}
}

CAREER_TRANSFERABLE_SKILL_SCHEMA = {
    "career_trans_id": {"type": str, "required": True, "regex": r"^CTS_\d{4}$"},
    "career_id": {"type": str, "required": True, "regex": r"^CAR_\d{3}$"},
    "skill_id": {"type": str, "required": True, "regex": r"^SK_\d{5}$"},
    "importance_score": {"type": float, "required": True},
    "data_value": {"type": str, "required": True},
    "description": {"type": str, "required": True}
}
