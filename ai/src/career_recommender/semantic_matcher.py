import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.data.normalizers import clean_text

class SemanticMatcher:
    """
    Compiles text profiles for careers and learners, and calculates
    cosine similarity using the pre-built Phase 1 TF-IDF vectorizer.
    """
    def __init__(self, careers_list, skills_list, career_skills_list,
                 career_trans_skills_list, career_interests_list, vectorizer):
        self.careers = careers_list
        self.skills = {s["skill_id"]: s["skill_name"] for s in skills_list}
        self.career_skills = career_skills_list
        self.career_trans = career_trans_skills_list
        self.career_interests = career_interests_list
        self.vectorizer = vectorizer
        
        self.career_vectors = {}
        self._precompute_career_profiles()

    def _precompute_career_profiles(self):
        """Construct unified text representations for all careers and pre-vectorize them."""
        for c in self.careers:
            cid = c["career_id"]
            title = c["career_title"]
            domain = c["career_domain"]
            desc = c["career_description"]
            
            # Match technical skills
            tech_names = []
            for cs in self.career_skills:
                if cs["career_id"] == cid:
                    s_name = self.skills.get(cs["skill_id"], "")
                    if s_name:
                        tech_names.append(s_name)
            
            # Match transferable skills
            trans_names = []
            for cts in self.career_trans:
                if cts["career_id"] == cid:
                    s_name = self.skills.get(cts["skill_id"], "")
                    if s_name:
                        trans_names.append(s_name)
                        
            # Match interest descriptions
            interest_descs = []
            for ci in self.career_interests:
                if ci["career_id"] == cid:
                    interest_descs.append(ci["interest_description"])

            # Form complete career profile text
            profile_parts = [
                title,
                domain,
                desc,
                ", ".join(tech_names),
                ", ".join(trans_names),
                " ".join(set(interest_descs))
            ]
            
            profile_text = clean_text(" | ".join([p for p in profile_parts if p.strip()]))
            
            if profile_text.strip() and self.vectorizer is not None:
                try:
                    self.career_vectors[cid] = self.vectorizer.transform([profile_text])
                except Exception:
                    self.career_vectors[cid] = None
            else:
                self.career_vectors[cid] = None

    def match_profile(self, user_interests, user_skills, user_trans):
        """
        Build learner representation string and calculate cosine similarity
        against all precomputed career vectors.
        """
        # Form learner representation
        interest_str = ""
        if isinstance(user_interests, str):
            interest_str = user_interests
        elif isinstance(user_interests, dict):
            active_interests = [k for k, v in user_interests.items() if v >= 3.0]
            if active_interests:
                interest_str = f"I am interested in {', '.join(active_interests)}."
                
        profile_parts = [
            interest_str,
            " ".join(user_skills),
            " ".join(user_trans)
        ]
        
        learner_text = clean_text(" ".join([p for p in profile_parts if p.strip()]))
        
        scores = {}
        if not learner_text.strip() or self.vectorizer is None:
            return {c["career_id"]: 0.0 for c in self.careers}

        try:
            learner_vec = self.vectorizer.transform([learner_text])
        except Exception:
            return {c["career_id"]: 0.0 for c in self.careers}

        for cid, car_vec in self.career_vectors.items():
            if car_vec is not None:
                sim = cosine_similarity(learner_vec, car_vec)[0][0]
                # Scale similarity to 0-100 scale
                scores[cid] = round(float(sim) * 100.0, 2)
            else:
                scores[cid] = 0.0
                
        return scores
