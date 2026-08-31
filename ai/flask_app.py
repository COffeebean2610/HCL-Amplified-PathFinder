import os
import json
from flask import Flask, render_template, request, jsonify, session
from model import load_model, build_tfidf_model, compute_similarity_matrix, save_model, evaluate_model
from recommender import CourseRecommender, _parse_user_input
from preprocessing import load_and_preprocess

app = Flask(__name__)
app.secret_key = 'course_recommender_secret_2024'

# ── Global model objects (loaded once at startup) ──────────────────────────────
recommender = None


def initialize_model():
    """Load or build the recommendation model."""
    global recommender
    model_dir = 'model/'

    if os.path.exists(os.path.join(model_dir, 'vectorizer.pkl')):
        print("INFO: Loading existing model from disk...")
        vectorizer, tfidf_matrix, similarity_matrix, df = load_model(model_dir)
    else:
        print("INFO: Building model from scratch...")
        df = load_and_preprocess('data/processed/courses.csv')
        vectorizer, tfidf_matrix = build_tfidf_model(df)
        similarity_matrix = compute_similarity_matrix(tfidf_matrix)
        save_model(vectorizer, tfidf_matrix, similarity_matrix, df, model_dir)

    recommender = CourseRecommender(vectorizer, tfidf_matrix, similarity_matrix, df)
    print(f"SUCCESS: Recommender ready with {len(df)} courses.")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Home page with input form."""
    all_skills       = recommender.get_all_skills()[:100]   # top 100 for autocomplete
    all_difficulties = recommender.get_all_difficulties()
    return render_template('index.html',
                           all_skills=all_skills,
                           all_difficulties=all_difficulties,
                           total_courses=len(recommender.df))


@app.route('/recommend', methods=['POST'])
def recommend():
    """Handle form submission and return recommendations."""
    interests         = request.form.get('interests', '').strip()
    skills_input      = request.form.get('skills', '').strip()
    completed_input   = request.form.get('completed_courses', '').strip()
    difficulty        = request.form.get('difficulty', 'any')
    top_n             = int(request.form.get('top_n', 10))

    # Parse comma-separated inputs
    user_skills       = _parse_user_input(skills_input)
    completed_courses = _parse_user_input(completed_input)

    if not interests and not user_skills:
        return render_template('index.html',
                               error="Please enter at least your interests or skills.",
                               all_skills=recommender.get_all_skills()[:100],
                               all_difficulties=recommender.get_all_difficulties(),
                               total_courses=len(recommender.df))

    results = recommender.recommend(
        interests=interests,
        user_skills=user_skills,
        completed_courses=completed_courses,
        difficulty=difficulty,
        top_n=top_n
    )

    return render_template('results.html',
                           results=results,
                           interests=interests,
                           user_skills=user_skills,
                           difficulty=difficulty,
                           total_found=len(results))


@app.route('/similar', methods=['GET'])
def similar():
    """Find courses similar to a given course."""
    course_name = request.args.get('course', '').strip()
    if not course_name:
        return jsonify({'error': 'No course name provided'}), 400

    similar_courses = recommender.similar_to_course(course_name, top_n=6)
    return jsonify({'similar_courses': similar_courses})


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """JSON API endpoint for recommendations."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400

    results = recommender.recommend(
        interests=data.get('interests', ''),
        user_skills=data.get('skills', []),
        completed_courses=data.get('completed_courses', []),
        difficulty=data.get('difficulty', 'any'),
        top_n=data.get('top_n', 10)
    )
    return jsonify({'recommendations': results, 'count': len(results)})


@app.route('/api/recommend-projects', methods=['POST'])
def api_recommend_projects():
    """JSON API endpoint for engineering project recommendations."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400

    target_role = data.get('target_role') or data.get('target_career')
    if not target_role:
        return jsonify({'error': 'Missing target_role or target_career parameter'}), 400

    payload = {
        "skills": data.get('skills', []),
        "interests": data.get('interests', ''),
        "target_role": target_role,
        "difficulty": data.get('difficulty', 'Any Level'),
        "top_k": int(data.get('top_k', 5))
    }

    try:
        from src.project_recommender.engine import recommend_projects_api
        res = recommend_projects_api(payload)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-roadmap', methods=['POST'])
def api_generate_roadmap():
    """JSON API endpoint for generating personalized learning roadmaps."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400

    target_role = data.get('target_role') or data.get('target_career')
    if not target_role:
        return jsonify({'error': 'Missing target_role or target_career parameter'}), 400

    payload = {
        "skills": data.get('skills', []),
        "interests": data.get('interests', ''),
        "target_role": target_role,
        "difficulty": data.get('difficulty', 'Any Level'),
        "completed_courses": data.get('completed_courses', []),
        "courses_per_skill": int(data.get('courses_per_skill', 3)),
        "projects_per_skill": int(data.get('projects_per_skill', 2))
    }

    try:
        from src.roadmap_generator.engine import generate_roadmap_api
        res = generate_roadmap_api(payload)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/evaluate')
def evaluate():
    """Show evaluation metrics."""
    from model import evaluate_model
    metrics = evaluate_model(recommender.df, recommender.similarity_matrix, sample_size=50)
    return render_template('evaluate.html', metrics=metrics)


@app.route('/about')
def about():
    return render_template('about.html')


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    initialize_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
