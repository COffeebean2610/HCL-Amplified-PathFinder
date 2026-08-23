from model import load_model
from recommender import CourseRecommender

print("Loading canonical model from disk...")
vectorizer, tfidf_matrix, similarity_matrix, df = load_model('model/')
recommender = CourseRecommender(vectorizer, tfidf_matrix, similarity_matrix, df)

print("\nGenerating recommendations for query: 'machine learning python' with skills: ['Python', 'Machine Learning']...")
results = recommender.recommend(
    interests="machine learning python",
    user_skills=["Python", "Machine Learning"],
    completed_courses=[],
    difficulty="any",
    top_n=5
)

print("\n--- RECOMMENDATIONS ---")
for r in results:
    print(f"Rank {r['rank']}: {r['course_name']} ({r['course_difficulty']}, rating: {r['course_rating']})")
    print(f"  Skills matched/available: {r['skills']}")
    print(f"  Final Score: {r['final_score']} (Content: {r['content_score']}, Skills Overlap: {r['skills_score']})")
    print()

print("Verification complete.")
