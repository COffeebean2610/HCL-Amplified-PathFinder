from src.data.normalizers import normalize_skill_name, CANONICAL_SKILL_ID_ALIASES

class SkillMatcher:
    """
    Normalizes student input skills and compares them against career-technical skill requirements,
    weighting matches according to their importance level.
    """
    def __init__(self, skills_list, career_skills_list):
        self.skills_list = skills_list
        self.career_skills = career_skills_list
        self._build_skills_maps()

    def _build_skills_maps(self):
        """Build mappings for fast lookup of canonical skill IDs by name."""
        self.known_skills_map = {}
        self.skills_by_name = {}
        
        for s in self.skills_list:
            sid = s["skill_id"]
            name = s["skill_name"]
            norm_name = s.get("normalized_name", name.lower().strip())
            
            # Map normalized lower string to canonical display name
            self.known_skills_map[norm_name] = name
            # Map normalized lower string to canonical ID
            self.skills_by_name[norm_name] = sid

    def normalize_user_skills(self, user_skills):
        """
        Normalize user's raw skill strings to canonical skill IDs.
        Returns a set of canonical skill IDs and a list of unknown skill names.
        """
        normalized_ids = set()
        unknown_skills = []
        
        for raw_s in user_skills:
            if not raw_s or not str(raw_s).strip():
                continue
            
            # Use Phase 1 normalizer helper
            canon_name, norm_key = normalize_skill_name(raw_s, self.known_skills_map)
            
            # 1. Check central canonical skill ID aliases
            if norm_key in CANONICAL_SKILL_ID_ALIASES:
                normalized_ids.add(CANONICAL_SKILL_ID_ALIASES[norm_key])
            # 2. Look up ID in database skills
            elif norm_key in self.skills_by_name:
                normalized_ids.add(self.skills_by_name[norm_key])
            else:
                unknown_skills.append(canon_name)
                
        return normalized_ids, unknown_skills

    def match_technical_skills(self, career_id, user_skill_ids):
        """
        Match user skill IDs against required technical skills for a specific career.
        Returns a dict containing:
          - 'score': 0.0 to 100.0 score based on importance weights
          - 'matched_skills': list of skill details that matched
          - 'missing_skills': list of skill details that are missing
          - 'critical_missing_skills': list of critical skill details that are missing
        """
        # Find required skills for this career
        req_skills = [cs for cs in self.career_skills if cs["career_id"] == career_id]
        
        if not req_skills:
            return {
                "score": 100.0 if not user_skill_ids else 0.0,
                "matched_skills": [],
                "missing_skills": [],
                "critical_missing_skills": []
            }

        importance_weights = {
            "critical": 3.0,
            "high": 2.0,
            "medium": 1.0
        }
        
        total_weight = 0.0
        matched_weight = 0.0
        
        matched_list = []
        missing_list = []
        critical_missing_list = []
        
        for cs in req_skills:
            sid = cs["skill_id"]
            importance = cs.get("importance", "Medium")
            desc = cs.get("description", "")
            
            # Resolve skill name from canonical list or lookup
            skill_info = None
            for s in self.skills_list:
                if s["skill_id"] == sid:
                    skill_info = s
                    break
                    
            s_name = skill_info["skill_name"] if skill_info else "Unknown Skill"
            
            weight = importance_weights.get(importance.lower(), 1.0)
            total_weight += weight
            
            record = {
                "skill_id": sid,
                "skill_name": s_name,
                "importance": importance,
                "description": desc
            }
            
            if sid in user_skill_ids:
                matched_weight += weight
                matched_list.append(record)
            else:
                missing_list.append(record)
                if importance.lower() == "critical":
                    critical_missing_list.append(record)

        score = (matched_weight / total_weight) * 100.0 if total_weight > 0.0 else 100.0
        
        return {
            "score": round(score, 2),
            "matched_skills": matched_list,
            "missing_skills": missing_list,
            "critical_missing_skills": critical_missing_list
        }
