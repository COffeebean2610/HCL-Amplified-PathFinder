def validate_recommendation_input(data):
    """
    Validates the career recommendation input schema.
    Returns (is_valid, cleaned_data, error_message).
    """
    if not isinstance(data, dict):
        return False, {}, "Input data must be a dictionary"

    cleaned = {}
    
    # 1. Interests validation
    interests = data.get("interests", "")
    if interests is None:
         interests = ""
         
    if isinstance(interests, str):
        cleaned["interests"] = interests.strip()
    elif isinstance(interests, dict):
        # Validate structured interest types
        allowed_types = {"Investigative", "Realistic", "Conventional", "Enterprising", "Artistic", "Social"}
        for k, v in interests.items():
            if k not in allowed_types:
                return False, {}, f"Invalid interest type '{k}'. Allowed: {list(allowed_types)}"
            try:
                float(v)
            except (ValueError, TypeError):
                return False, {}, f"Interest score for '{k}' must be a number"
        cleaned["interests"] = {str(k): float(v) for k, v in interests.items()}
    else:
        return False, {}, "interests must be either a string or a dictionary of scores"

    # 2. Current Skills validation
    current_skills = data.get("current_skills", [])
    if current_skills is None:
        current_skills = []
    if not isinstance(current_skills, list):
        return False, {}, "current_skills must be a list of strings"
    cleaned["current_skills"] = [str(s).strip() for s in current_skills if s and str(s).strip()]

    # 3. Transferable Skills validation
    trans_skills = data.get("transferable_skills", [])
    if trans_skills is None:
        trans_skills = []
    if not isinstance(trans_skills, list):
        return False, {}, "transferable_skills must be a list of strings"
    cleaned["transferable_skills"] = [str(t).strip() for t in trans_skills if t and str(t).strip()]

    # 4. Target Career validation
    target_career = data.get("target_career")
    if target_career is not None:
        cleaned["target_career"] = str(target_career).strip()
    else:
        cleaned["target_career"] = None

    # 5. top_k validation
    top_k = data.get("top_k", 5)
    try:
        cleaned["top_k"] = max(1, int(top_k))
    except (ValueError, TypeError):
        cleaned["top_k"] = 5

    return True, cleaned, ""
