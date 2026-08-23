import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
    return ' '.join(tokens)


def clean_skills(skills_text):
    """Parse and normalize the skills column."""
    if pd.isna(skills_text) or skills_text is None:
        return []
    skills_text = str(skills_text)
    # Handle list-like strings
    skills_text = re.sub(r"[\[\]'\"{}]", '', skills_text)
    skills = [s.strip().lower() for s in re.split(r'[,;|]', skills_text) if s.strip()]
    return skills


def load_and_preprocess(filepath='data/processed/courses.csv'):
    """Load dataset and apply full preprocessing pipeline."""
    df = pd.read_csv(filepath)

    print(f"OK: Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns found: {list(df.columns)}")

    # ── Column name normalization ──────────────────────────────────────────────
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Flexible column mapping (handles common Kaggle Coursera dataset variants)
    rename_map = {}
    col_list = df.columns.tolist()

    def find_col(candidates):
        for c in candidates:
            for col in col_list:
                if c in col:
                    return col
        return None

    name_col  = find_col(['course_name', 'name', 'title', 'course_title'])
    desc_col  = find_col(['course_description', 'description', 'about', 'summary'])
    skill_col = find_col(['skills', 'skill', 'tag', 'topic'])
    diff_col  = find_col(['difficulty', 'level', 'course_difficulty'])
    rate_col  = find_col(['rating', 'course_rating', 'stars'])
    cert_col  = find_col(['certificate', 'cert', 'course_certificate_type'])
    org_col   = find_col(['organization', 'university', 'institution', 'provider'])
    url_col   = find_col(['url', 'link', 'course_url'])

    if name_col:  rename_map[name_col]  = 'course_name'
    if desc_col:  rename_map[desc_col]  = 'course_description'
    if skill_col: rename_map[skill_col] = 'skills'
    if diff_col:  rename_map[diff_col]  = 'course_difficulty'
    if rate_col:  rename_map[rate_col]  = 'course_rating'
    if cert_col:  rename_map[cert_col]  = 'course_certificate_type'
    if org_col:   rename_map[org_col]   = 'organization'
    if url_col:   rename_map[url_col]   = 'course_url'

    df.rename(columns=rename_map, inplace=True)

    # Ensure all expected columns exist (fill missing ones with defaults)
    defaults = {
        'course_name': 'Unknown Course',
        'course_description': '',
        'skills': '',
        'course_difficulty': 'Beginner',
        'course_rating': 0.0,
        'course_certificate_type': 'Certificate',
        'organization': '',
        'course_url': '#',
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    # ── Data Cleaning ──────────────────────────────────────────────────────────
    df.drop_duplicates(subset=['course_name'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Clean rating
    df['course_rating'] = pd.to_numeric(df['course_rating'], errors='coerce').fillna(0.0)

    # Parse skills into a list
    df['skills_list'] = df['skills'].apply(clean_skills)

    # Clean text fields for TF-IDF
    df['clean_description'] = df['course_description'].apply(clean_text)
    df['clean_name']        = df['course_name'].apply(clean_text)
    df['clean_skills']      = df['skills_list'].apply(lambda lst: ' '.join(lst))

    # ── Feature Engineering ────────────────────────────────────────────────────
    # Combined feature: name (weighted x2) + description + skills (weighted x2)
    df['combined_features'] = (
        df['clean_name'] + ' ' + df['clean_name'] + ' ' +
        df['clean_description'] + ' ' +
        df['clean_skills'] + ' ' + df['clean_skills']
    )

    # Difficulty encoding
    difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'mixed': 2}
    df['difficulty_encoded'] = (
        df['course_difficulty'].str.lower()
        .map(difficulty_map)
        .fillna(1)
        .astype(int)
    )

    print(f"SUCCESS: Preprocessing complete. {len(df)} courses ready.")
    return df


if __name__ == '__main__':
    df = load_and_preprocess()
    print(df[['course_name', 'skills_list', 'difficulty_encoded']].head())
