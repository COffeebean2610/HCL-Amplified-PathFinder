import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class InterestMatcher:
    """
    Matches user interests (structured dict or natural language text)
    against the RIASEC interest types database using TF-IDF semantic profiles.
    """
    def __init__(self, career_interests_list, vectorizer):
        self.career_interests = career_interests_list
        self.vectorizer = vectorizer
        self.riasec_types = ["Investigative", "Realistic", "Conventional", "Enterprising", "Artistic", "Social"]
        self._build_riasec_profiles()

    def _build_riasec_profiles(self):
        """Aggregate descriptions for each RIASEC type to form reference text profiles."""
        self.profiles = {}
        for r_type in self.riasec_types:
            # Gather descriptions for this interest type
            descs = []
            for item in self.career_interests:
                if item["interest_type"].lower().strip() == r_type.lower():
                    descs.append(item["interest_description"])
            
            # Form unified profile text
            self.profiles[r_type] = " ".join(set(descs))

        # Pre-vectorize RIASEC profiles
        self.profile_vectors = {}
        for r_type, text in self.profiles.items():
            if text.strip() and self.vectorizer:
                try:
                    self.profile_vectors[r_type] = self.vectorizer.transform([text])
                except Exception:
                    self.profile_vectors[r_type] = None
            else:
                self.profile_vectors[r_type] = None

    def match_interests(self, interests_input):
        """
        Processes interest inputs and returns a dict mapping RIASEC interest types
        to scores (0.0 to 5.0 scale).
        """
        # Case 1: Already structured dictionary of scores
        if isinstance(interests_input, dict):
            result = {}
            for r_type in self.riasec_types:
                val = interests_input.get(r_type, 0.0)
                # Bound between 0.0 and 5.0
                result[r_type] = max(0.0, min(5.0, float(val)))
            return result

        # Case 2: Natural Language String
        result = {r_type: 0.0 for r_type in self.riasec_types}
        if not isinstance(interests_input, str) or not interests_input.strip():
            return result

        # Vectorize user input text
        try:
            user_vec = self.vectorizer.transform([interests_input])
        except Exception:
            return result

        similarities = {}
        for r_type, vec in self.profile_vectors.items():
            if vec is not None:
                sim = cosine_similarity(user_vec, vec)[0][0]
                similarities[r_type] = float(sim)
            else:
                similarities[r_type] = 0.0

        # Relative scaling so maximum matching interest gets 5.0, others scale proportionally
        max_sim = max(similarities.values()) if similarities else 0.0
        if max_sim > 0.0:
            for r_type, sim in similarities.items():
                result[r_type] = round((sim / max_sim) * 5.0, 2)
        
        return result
