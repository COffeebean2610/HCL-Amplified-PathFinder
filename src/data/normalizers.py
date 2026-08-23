import re

# Deterministic alias mapping for skills (lowercase -> canonical display name)
SKILL_ALIASES = {
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural-language-processing": "Natural Language Processing",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "generative-ai": "Generative AI",
    "deep-learning": "Deep Learning",
    "react.js": "React",
    "reactjs": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "js": "JavaScript",
    "ts": "TypeScript",
    "dbms": "Database Management Systems",
    "powerbi": "Power BI",
    "aws": "Amazon Web Services",
    "ui": "UI/UX Design",
    "ux": "UI/UX Design",
    "ui/ux": "UI/UX Design",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "xml": "XML",
    "api": "API",
    "rtos": "RTOS",
}

# Central canonical skill ID lookup (lowercase string -> canonical skill ID)
CANONICAL_SKILL_ID_ALIASES = {
    "llm": "SK_00255",
    "llms": "SK_00255",
    "large language model": "SK_00255",
    "large language models": "SK_00255",
    "ml": "SK_00264",
    "machine learning": "SK_00264",
    "dl": "SK_00132",
    "deep learning": "SK_00132",
    "nlp": "SK_00316",
    "natural language processing": "SK_00316",
    "aws": "SK_00046",
    "amazon web services": "SK_00046",
    "js": "SK_00240",
    "javascript": "SK_00240",
    "py": "SK_00360",
    "python": "SK_00360",
    "sql": "SK_00435",
    "git": "SK_00189",
    "docker": "SK_00145",
    "pytorch": "SK_00361",
    "tensorflow": "SK_00457",
    "generative ai": "SK_00188",
    "genai": "SK_00188",
    "rest apis": "SK_00382",
    "rest api": "SK_00382",
    "api": "SK_00382",
    "math": "SK_00270",
    "mathematics": "SK_00270",
    "statistics": "SK_00443",
    "flask": "SK_00179",
    "fastapi": "SK_00174",
}

def clean_text(text):
    """Normalize basic text spacing, casing, and trailing whitespace."""
    if not isinstance(text, str) or not text.strip():
        return ""
    # Normalize repeated whitespace and strip
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_skills(skills_text, source=None):
    """
    Parse a multi-valued skill string into a list of clean, trimmed skill strings.
    Handles double-space separators for Coursera and comma/semicolon/pipe separators for others.
    """
    if not isinstance(skills_text, str) or not skills_text.strip():
        return []
    
    # Strip list bracket strings if any
    s_text = re.sub(r"[\[\]'\"{}]", "", skills_text)
    
    if source == "coursera":
        # Coursera skills are separated by double-spaces or more
        parts = re.split(r'\s{2,}', s_text)
    else:
        # Others are comma, semicolon, or pipe separated
        parts = re.split(r'[,;|]', s_text)
        
    cleaned = []
    for p in parts:
        p_clean = clean_text(p)
        if p_clean:
            cleaned.append(p_clean)
    return cleaned

def normalize_skill_name(raw_name, known_skills_map=None):
    """
    Normalize a skill name to its canonical display form.
    - Resolves known aliases (e.g., 'ml' -> 'Machine Learning').
    - Looks up lowercase name in known_skills_map (which maps lowercase -> display name) to preserve exact database names.
    - Fallback: Capitalizes first letters nicely.
    """
    if not raw_name:
        return "", ""
        
    cleaned = clean_text(raw_name)
    norm_key = cleaned.lower()
    
    # 1. Check explicit aliases
    if norm_key in SKILL_ALIASES:
        canonical_name = SKILL_ALIASES[norm_key]
        return canonical_name, canonical_name.lower()
        
    # 2. Check if it matches a known skill display name
    if known_skills_map and norm_key in known_skills_map:
        canonical_name = known_skills_map[norm_key]
        return canonical_name, norm_key
        
    # 3. Fallback: formatted capitalization
    # If the word is entirely uppercase (like SQL, API, CSS, HTML, RTOS), preserve it
    if cleaned.isupper() and len(cleaned) <= 5:
        canonical_name = cleaned
    else:
        # Title case, but keep special camelcase (e.g. SpringBoot -> SpringBoot)
        # For simplicity, do title case if it's all lower, otherwise capitalize first letter
        if cleaned.islower():
            canonical_name = cleaned.title()
        else:
            canonical_name = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 0 else cleaned
            
    return canonical_name, canonical_name.lower()

def normalize_difficulty(difficulty_str):
    """
    Normalize difficulty values to standard vocabulary:
    Beginner, Intermediate, Advanced, Conversant, Not Calibrated, Any Level.
    """
    if not isinstance(difficulty_str, str) or not difficulty_str.strip():
        return "Not Calibrated"
        
    clean_diff = clean_text(difficulty_str).lower()
    
    mapping = {
        "beginner": "Beginner",
        "easy": "Beginner",
        "basic": "Beginner",
        "intermediate": "Intermediate",
        "medium": "Intermediate",
        "mixed": "Intermediate",
        "advanced": "Advanced",
        "hard": "Advanced",
        "difficult": "Advanced",
        "conversant": "Conversant",
        "not calibrated": "Not Calibrated",
        "any level": "Any Level",
        "any": "Any Level"
    }
    
    return mapping.get(clean_diff, "Not Calibrated")
