import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import clean_text, clean_skills


# ── Helper ─────────────────────────────────────────────────────────────────────

def _skills_overlap_score(user_skills: list, course_skills: list) -> float:
    """Jaccard-style overlap between user skills and course skills."""
    if not user_skills or not course_skills:
        return 0.0
    u = set(s.lower().strip() for s in user_skills)
    c = set(s.lower().strip() for s in course_skills)
    intersection = u & c
    union = u | c
    return len(intersection) / len(union) if union else 0.0


def _parse_user_input(text: str) -> list:
    """Convert comma/space-separated user input string into a clean list."""
    if not text:
        return []
    items = re.split(r'[,;|\n]+', text)
    return [i.strip().lower() for i in items if i.strip()]


# ── Core Recommender ───────────────────────────────────────────────────────────

class CourseRecommender:
    def __init__(self, vectorizer, tfidf_matrix, similarity_matrix, df):
        self.vectorizer        = vectorizer
        self.tfidf_matrix      = tfidf_matrix
        self.similarity_matrix = similarity_matrix
        self.df                = df.reset_index(drop=True)

    # ── 1. Content-Based Query Score ──────────────────────────────────────────
    def _content_score_from_query(self, query: str) -> np.ndarray:
        """Transform a free-text query to TF-IDF and compute cosine similarity."""
        if not query.strip():
            return np.zeros(len(self.df))
        query_vec = self.vectorizer.transform([clean_text(query)])
        scores    = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        return scores

    # ── 2. Skills Overlap Score ────────────────────────────────────────────────
    def _skills_score(self, user_skills: list) -> np.ndarray:
        scores = np.array([
            _skills_overlap_score(user_skills, course_skills)
            for course_skills in self.df['skills_list']
        ])
        return scores

    # ── 3. Completed Courses Penalty ──────────────────────────────────────────
    def _completed_mask(self, completed_courses: list) -> np.ndarray:
        """Return a boolean mask: True = not completed (keep), False = completed (exclude)."""
        completed_lower = [c.lower().strip() for c in completed_courses]
        mask = np.array([
            not any(comp in name.lower() for comp in completed_lower)
            for name in self.df['course_name']
        ])
        return mask

    # ── 4. Difficulty Filter ──────────────────────────────────────────────────
    def _difficulty_mask(self, difficulty: str) -> np.ndarray:
        if not difficulty or difficulty == 'any':
            return np.ones(len(self.df), dtype=bool)
        diff_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        target   = diff_map.get(difficulty.lower(), None)
        if target is None:
            return np.ones(len(self.df), dtype=bool)
        return self.df['difficulty_encoded'].values == target

    # ── 5. Main Recommend Method ──────────────────────────────────────────────
    def recommend(
        self,
        interests: str = '',
        user_skills: list = None,
        completed_courses: list = None,
        difficulty: str = 'any',
        top_n: int = 10,
        content_weight: float = 0.6,
        skills_weight: float = 0.4
    ) -> list:
        """
        Returns a list of dicts (top_n recommended courses).

        Parameters
        ----------
        interests        : free-text interest description
        user_skills      : list of skill strings the user has
        completed_courses: list of course names already done (excluded)
        difficulty       : 'any' | 'beginner' | 'intermediate' | 'advanced'
        top_n            : number of results
        content_weight   : weight for TF-IDF content score  (default 0.6)
        skills_weight    : weight for skills overlap score   (default 0.4)
        """
        if user_skills      is None: user_skills       = []
        if completed_courses is None: completed_courses = []

        # Build query string = interests + skills
        user_skills_parsed = [_parse_user_input(s) for s in user_skills]
        user_skills_flat   = [item for sublist in user_skills_parsed for item in sublist]
        if isinstance(user_skills, str):
            user_skills_flat = _parse_user_input(user_skills)

        query = interests + ' ' + ' '.join(user_skills_flat)

        # Compute component scores
        content_scores = self._content_score_from_query(query)
        skills_scores  = self._skills_score(user_skills_flat)

        # Weighted final score
        final_scores = content_weight * content_scores + skills_weight * skills_scores

        # Apply filters
        completed_mask = self._completed_mask(completed_courses)
        difficulty_mask = self._difficulty_mask(difficulty)
        combined_mask = completed_mask & difficulty_mask
        final_scores[~combined_mask] = -1  # push filtered items to bottom

        # Boost by rating (small bonus: up to +0.05)
        max_rating = self.df['course_rating'].max()
        if max_rating > 0:
            rating_bonus = (self.df['course_rating'].values / max_rating) * 0.05
            final_scores += rating_bonus

        # Rank
        top_indices = np.argsort(final_scores)[::-1][:top_n]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df.iloc[idx]
            results.append({
                'rank'                   : rank,
                'course_name'            : row['course_name'],
                'organization'           : row.get('organization', ''),
                'course_difficulty'      : row['course_difficulty'],
                'course_rating'          : round(float(row['course_rating']), 1),
                'course_certificate_type': row.get('course_certificate_type', ''),
                'skills'                 : row['skills_list'][:8],   # show top 8
                'course_url'             : row.get('course_url', '#'),
                'content_score'          : round(float(content_scores[idx]), 4),
                'skills_score'           : round(float(skills_scores[idx]), 4),
                'final_score'            : round(float(final_scores[idx]), 4),
            })

        return results

    # ── 6. Similar Courses (course-to-course) ─────────────────────────────────
    def similar_to_course(self, course_name: str, top_n: int = 6) -> list:
        """Find courses similar to a given course name."""
        matches = self.df[self.df['course_name'].str.lower() == course_name.lower()]
        if matches.empty:
            # fuzzy fallback
            mask = self.df['course_name'].str.lower().str.contains(course_name.lower(), na=False)
            matches = self.df[mask]
        if matches.empty:
            return []

        idx    = matches.index[0]
        scores = list(enumerate(self.similarity_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

        results = []
        for rank, (i, score) in enumerate(scores, 1):
            row = self.df.iloc[i]
            results.append({
                'rank'             : rank,
                'course_name'      : row['course_name'],
                'organization'     : row.get('organization', ''),
                'course_difficulty': row['course_difficulty'],
                'course_rating'    : round(float(row['course_rating']), 1),
                'skills'           : row['skills_list'][:6],
                'similarity_score' : round(float(score), 4),
            })
        return results

    # ── 7. All unique skills in dataset ───────────────────────────────────────
    def get_all_skills(self) -> list:
        all_skills = set()
        for skills in self.df['skills_list']:
            all_skills.update(skills)
        return sorted(all_skills)

    def get_all_difficulties(self) -> list:
        return sorted(self.df['course_difficulty'].dropna().unique().tolist())
