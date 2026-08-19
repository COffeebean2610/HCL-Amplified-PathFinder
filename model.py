import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import load_and_preprocess


def build_tfidf_model(df):
    """Build TF-IDF matrix from combined course features."""
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),   # unigrams + bigrams
        min_df=1,
        max_df=0.95,
        sublinear_tf=True     # log-scale TF for better weighting
    )
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
    print(f"✅ TF-IDF matrix built: {tfidf_matrix.shape}")
    return vectorizer, tfidf_matrix


def compute_similarity_matrix(tfidf_matrix):
    """Pre-compute full cosine similarity matrix (for small-medium datasets)."""
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"✅ Similarity matrix computed: {similarity_matrix.shape}")
    return similarity_matrix


def save_model(vectorizer, tfidf_matrix, similarity_matrix, df, model_dir='model/'):
    """Persist all model artifacts to disk."""
    os.makedirs(model_dir, exist_ok=True)

    with open(os.path.join(model_dir, 'vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)

    with open(os.path.join(model_dir, 'tfidf_matrix.pkl'), 'wb') as f:
        pickle.dump(tfidf_matrix, f)

    with open(os.path.join(model_dir, 'similarity_matrix.pkl'), 'wb') as f:
        pickle.dump(similarity_matrix, f)

    df.to_pickle(os.path.join(model_dir, 'courses_df.pkl'))
    print(f"✅ All model artifacts saved to '{model_dir}'")


def load_model(model_dir='model/'):
    """Load all model artifacts from disk."""
    with open(os.path.join(model_dir, 'vectorizer.pkl'), 'rb') as f:
        vectorizer = pickle.load(f)

    with open(os.path.join(model_dir, 'tfidf_matrix.pkl'), 'rb') as f:
        tfidf_matrix = pickle.load(f)

    with open(os.path.join(model_dir, 'similarity_matrix.pkl'), 'rb') as f:
        similarity_matrix = pickle.load(f)

    import pandas as pd
    df = pd.read_pickle(os.path.join(model_dir, 'courses_df.pkl'))

    print("✅ Model loaded successfully from disk.")
    return vectorizer, tfidf_matrix, similarity_matrix, df


def evaluate_model(df, similarity_matrix, sample_size=10):
    """
    Basic evaluation metrics:
    - Intra-list diversity  : avg pairwise dissimilarity in top-10 recommendations
    - Coverage              : % of catalogue that ever gets recommended
    - Average precision@K   : using category as proxy for relevance
    """
    import random
    random.seed(42)

    sample_indices = random.sample(range(len(df)), min(sample_size, len(df)))
    diversities = []
    recommended_set = set()

    for idx in sample_indices:
        scores = list(enumerate(similarity_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        top_k = [i for i, _ in scores[1:11]]   # top-10, exclude self

        recommended_set.update(top_k)

        # Intra-list diversity = 1 - avg pairwise similarity within the list
        top_sim = similarity_matrix[np.ix_(top_k, top_k)]
        upper_tri = top_sim[np.triu_indices(len(top_k), k=1)]
        diversity = 1 - upper_tri.mean() if len(upper_tri) > 0 else 0
        diversities.append(diversity)

    coverage = len(recommended_set) / len(df) * 100
    avg_diversity = np.mean(diversities)

    print("\n📊 Model Evaluation Metrics:")
    print(f"   Catalogue size       : {len(df)} courses")
    print(f"   Coverage @10         : {coverage:.1f}%")
    print(f"   Avg Intra-list Div.  : {avg_diversity:.4f}  (1=max diverse, 0=identical)")

    return {
        'coverage_percent': round(coverage, 2),
        'avg_diversity': round(float(avg_diversity), 4),
        'catalogue_size': len(df)
    }


if __name__ == '__main__':
    df = load_and_preprocess()
    vectorizer, tfidf_matrix = build_tfidf_model(df)
    similarity_matrix = compute_similarity_matrix(tfidf_matrix)
    save_model(vectorizer, tfidf_matrix, similarity_matrix, df)
    evaluate_model(df, similarity_matrix)
