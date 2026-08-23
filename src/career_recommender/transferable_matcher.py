class TransferableMatcher:
    """
    Normalizes and matches student transferable (soft) skills against career requirements,
    weighting them by their importance score.
    """
    def __init__(self, skills_list, career_transferable_skills_list):
        self.skills_list = skills_list
        self.career_trans_skills = career_transferable_skills_list
        self._build_transferable_maps()

    def _build_transferable_maps(self):
        """Build maps for lookup of canonical transferable skill IDs by name."""
        self.known_trans_map = {}
        self.trans_by_name = {}
        
        for s in self.skills_list:
            if s.get("skill_type") == "transferable" or s.get("skill_category") in ["Soft Skills", "Transferable Skills", "Core Skills"]:
                sid = s["skill_id"]
                name = s["skill_name"]
                norm_name = s.get("normalized_name", name.lower().strip())
                
                self.known_trans_map[norm_name] = name
                self.trans_by_name[norm_name] = sid

    def normalize_user_transferable(self, user_trans_skills):
        """Normalize user transferable skill strings to canonical skill IDs."""
        normalized_ids = set()
        for raw_t in user_trans_skills:
            if not raw_t or not str(raw_t).strip():
                continue
            norm_key = str(raw_t).lower().strip()
            
            # Simple direct matching or alias lookup
            if norm_key in self.trans_by_name:
                normalized_ids.add(self.trans_by_name[norm_key])
            else:
                # Direct check across all canonical skills just in case
                for s in self.skills_list:
                    if s["skill_name"].lower().strip() == norm_key:
                        normalized_ids.add(s["skill_id"])
                        break
        return normalized_ids

    def match_transferable_skills(self, career_id, user_trans_ids):
        """
        Compare user transferable skill IDs against career requirements.
        Returns a dict with 'score', 'matched_skills', and 'missing_skills'.
        """
        req_trans = [cts for cts in self.career_trans_skills if cts["career_id"] == career_id]
        
        if not req_trans:
            return {
                "score": 100.0 if not user_trans_ids else 0.0,
                "matched_skills": [],
                "missing_skills": []
            }
            
        total_importance = 0.0
        matched_importance = 0.0
        
        matched_list = []
        missing_list = []
        
        for cts in req_trans:
            sid = cts["skill_id"]
            imp_score = float(cts.get("importance_score", 4.0))
            data_val = cts.get("data_value", "High")
            desc = cts.get("description", "")
            
            # Retrieve skill name
            skill_info = None
            for s in self.skills_list:
                if s["skill_id"] == sid:
                    skill_info = s
                    break
            s_name = skill_info["skill_name"] if skill_info else "Unknown Transferable Skill"
            
            total_importance += imp_score
            
            record = {
                "skill_id": sid,
                "skill_name": s_name,
                "importance_score": imp_score,
                "data_value": data_val,
                "description": desc
            }
            
            if sid in user_trans_ids:
                matched_importance += imp_score
                matched_list.append(record)
            else:
                missing_list.append(record)
                
        score = (matched_importance / total_importance) * 100.0 if total_importance > 0.0 else 100.0
        
        return {
            "score": round(score, 2),
            "matched_skills": matched_list,
            "missing_skills": missing_list
        }
