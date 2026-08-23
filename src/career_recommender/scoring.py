import numpy as np

# Configurable default scoring weights
DEFAULT_WEIGHTS = {
    "technical": 0.35,
    "interest": 0.25,
    "semantic": 0.20,
    "transferable": 0.15,
    "market": 0.05
}

class ScoringEngine:
    """
    Implements hybrid scoring calculations, market signal metrics,
    dynamic weight adjustment for cold start, and confidence estimation.
    """
    def __init__(self, custom_weights=None):
        self.weights = custom_weights if custom_weights else DEFAULT_WEIGHTS

    def calculate_market_signal(self, career_id, career_skills_list):
        """
        Calculate market demand signal (0-100 score) for a career based on
        density of in-demand and hot-technology required skills.
        """
        req_skills = [cs for cs in career_skills_list if cs["career_id"] == career_id]
        if not req_skills:
            return 50.0  # neutral default
            
        total_signals = len(req_skills) * 2.0
        active_signals = 0.0
        
        for cs in req_skills:
            if cs.get("in_demand", "").lower() == "yes":
                active_signals += 1.0
            if cs.get("hot_technology", "").lower() == "yes":
                active_signals += 1.0
                
        score = (active_signals / total_signals) * 100.0 if total_signals > 0 else 50.0
        return round(score, 2)

    def get_active_weights(self, has_skills, has_interests, has_transferable):
        """
        Dynamically redistributes weights if one or more signals are missing (cold-start).
        """
        active_flags = {
            "technical": has_skills,
            "interest": has_interests,
            "semantic": has_skills or has_interests,  # semantic requires either
            "transferable": has_transferable,
            "market": True  # market signal is static and always available
        }
        
        # 1. Filter weights by active flag
        weights = {}
        for key, val in self.weights.items():
            if active_flags.get(key, True):
                weights[key] = val
            else:
                weights[key] = 0.0
                
        # 2. Normalize weights to sum to 1.0
        total = sum(weights.values())
        if total > 0.0:
            for key in weights:
                weights[key] = weights[key] / total
        else:
            # Fallback equal weights if everything is missing
            active_count = sum(1 for v in active_flags.values() if v)
            val = 1.0 / active_count if active_count > 0 else 1.0
            for key in weights:
                weights[key] = val if active_flags.get(key, True) else 0.0
                
        return weights

    def calculate_confidence(self, user_skills, user_interests, user_trans):
        """
        Determine recommendation confidence level (High, Medium, Low)
        based on the volume and quality of input signals provided.
        """
        points = 0
        
        # Skills completeness points
        skills_count = len(user_skills)
        if skills_count >= 3:
            points += 2
        elif skills_count >= 1:
            points += 1
            
        # Interests completeness points
        if isinstance(user_interests, str):
            if len(user_interests.strip()) >= 30:
                points += 2
            elif len(user_interests.strip()) > 0:
                points += 1
        elif isinstance(user_interests, dict):
            active_count = sum(1 for v in user_interests.values() if v >= 3.0)
            if active_count >= 2:
                points += 2
            elif active_count >= 1:
                points += 1
                
        # Transferable completeness points
        trans_count = len(user_trans)
        if trans_count >= 2:
            points += 1
            
        # Classify by point boundaries (max = 5)
        if points >= 4:
            return "High"
        elif points >= 2:
            return "Medium"
        else:
            return "Low"

    def compute_hybrid_score(self, component_scores, active_weights):
        """
        Compute final hybrid match score using weighted active signals.
        """
        final_score = 0.0
        for key, score in component_scores.items():
            final_score += score * active_weights.get(key, 0.0)
        return min(100, max(0, int(round(final_score))))
