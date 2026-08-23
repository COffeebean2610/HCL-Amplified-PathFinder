# Phase 8 — Project Recommendation Engine

## 1. Objective
Personalized projects are essential for engineering education because they allow students to scaffold new, difficult concepts using their already-established skills. The RouteMaster Project Recommendation module ranks and recommends practical projects that cover critical career skill gaps, satisfy prerequisite constraints, and fit the student's difficulty level.

## 2. Dataset
We use the engineering projects registry containing **251 records** across technical domains (Data Science, Software Engineering, Artificial Intelligence, Mobile Dev). Key properties for each record:
- `project_id`: Canonical unique string identifier.
- `project_name`: Descriptive display name.
- `domain`: Subject category.
- `skills`: Mapped list of canonical skill IDs.
- `tech_stack`: List of technologies, languages, and frameworks.
- `description`: Text summarizing project goal.
- `difficulty`: beginner, intermediate, or advanced.
- `github_url`: Source code codebases.

## 3. Data Cleaning
During startup initialization of `ProjectRecommender`, the dataset is parsed and cleaned:
- **Difficulty Casing**: Difficulty strings are stripped and capitalized to match canonical keys (`Beginner`, `Intermediate`, `Advanced`). Unknown strings fallback to `Intermediate`.
- **URL Validation**: `github_url` values are verified to begin with `http://` or `https://`. Malformed or missing URLs fallback to `"#"` (indicating direct repository link is pending).
- **Duplicate Prevention**: Mapped into dictionaries keying off unique `project_id` values to prevent duplicate listing.

## 4. Skill Normalization & Processing
User current skills are normalized to canonical skill IDs using the Phase 1 skill taxonomy:
- Converts casing, handles delimiters (e.g. `'ML'` mapping to `'SK_00264'` for Machine Learning).
- Unknown input strings fallback to direct substring matching.

## 5. Skill Gap Integration
The engine integrates with the Phase 4 `SkillGapEngine` to extract `missing_technical_skills` and `prerequisite_gaps` for the resolved target career.

## 6. Candidate Retrieval
To run recommendations efficiently, candidate generation retrieves projects from two pipelines:
1. **Skills-based candidates**: Top 30 projects that contain at least one of the student's target career missing skills.
2. **Semantic candidates**: Top 30 projects returned via Phase 6 `RouteMasterVectorSearch` local cosine similarity.
These candidates are deduplicated by `project_id` to form the candidate pool.

## 7. Skill Match & Coverage Algorithm

### Weighted Skill-Gap Coverage
We weight missing skills based on their career priority mapping:
- `Critical`: 3.0
- `High`: 2.0
- `Medium` / `Low` / Other: 1.0

The coverage score is defined as:
$$\text{Skill Gap Coverage} = \frac{\sum_{s \in T_{proj} \cap M} \text{Weight}(s)}{\sum_{s \in M} \text{Weight}(s)}$$
*(If there are no missing career gaps, the score defaults to 1.0).*

### Project Skill Match Score
Evaluates the scaffolding alignment:
$$\text{Project Skill Match} = 0.50 \cdot \text{Gap Coverage} + 0.25 \cdot \text{Career Relevance} + 0.25 \cdot \text{Known Alignment}$$
Where:
- $\text{Career Relevance} = \frac{| T_{proj} \cap \text{Career Skills} |}{| T_{proj} |}$
- $\text{Known Alignment} = \frac{| T_{proj} \cap \text{Known Skills} |}{| T_{proj} |}$

## 8. Semantic Similarity
Formulates query text: `f"Practice project for target role: [Career Title]. Gaps: [Missing Skills]"` and computes dot product against BGE float32 project embeddings. Clamped to $[0, 1]$.

## 9. Prerequisite Readiness
Retrieves REQUIRED dependency closures from Phase 2 graph builder:
$$\text{Readiness} = \frac{| \text{Prerequisites of } T_{proj} \cap \text{Known Skills} |}{| \text{Prerequisites of } T_{proj} |}$$
- If $\text{Readiness} \ge 0.7$, status is `"Ready"`. Otherwise, it is marked as `"Locked"`.

## 10. Difficulty Compatibility
Aligns difficulty tiers:
- Exact match / User preference "Any Level" = 1.0.
- Off by 1 tier (e.g. Intermediate preference, Beginner project) = 0.5.
- Off by 2 tiers (e.g. Beginner preference, Advanced project) = 0.1.

## 11. Final Ranking Formula
The weighted composite ranking is:
$$\text{Final Score} = 0.45 \cdot S_{gap\_coverage} + 0.25 \cdot S_{semantic} + 0.20 \cdot S_{prerequisite} + 0.10 \cdot S_{difficulty}$$
Weights are configurable in `PROJECT_WEIGHTS` initialization to allow tuning.

## 12. Explainability
Deterministic reason strings are generated:
`f"This project is recommended because it helps you develop: [Skill Gap 1, 2], plus it practices your existing skills: [Known Skill 1], plus it perfectly fits your preferred Intermediate level."`

## 13. Greedy Diversification
To prevent recommendations from listing redundant projects (e.g. three React LMS clones), we apply a re-ranking loop. After selecting a project, we penalize the remaining candidates' final scores:
$$\text{Penalty} = 0.1 \cdot | T_{proj} \cap \text{Already Selected Skills} |$$
This promotes variety in the final portfolio recommendations.

## 14. API Contract (`POST /api/recommend-projects`)

### Request JSON:
```json
{
  "skills": ["Python", "SQL", "Git"],
  "interests": "Generative AI",
  "target_role": "AI Engineer",
  "difficulty": "Intermediate",
  "top_k": 3
}
```

### Response JSON:
```json
{
  "career": {
    "career_id": "CAR_003",
    "career_title": "AI Engineer"
  },
  "skill_gaps": ["Machine Learning", "Deep Learning", "Docker", "REST APIs", "PyTorch"],
  "projects": [
    {
      "project_id": "PROJ_022",
      "project_name": "Predictive Maintenance Pipeline",
      "domain": "Artificial Intelligence",
      "difficulty": "Intermediate",
      "github_url": "https://github.com/...",
      "final_score": 0.825,
      "skill_gap_coverage_score": 0.85,
      "semantic_score": 0.78,
      "prerequisite_score": 0.9,
      "difficulty_score": 1.0,
      "matched_existing_skills": ["Python"],
      "skills_to_develop": ["Machine Learning", "Pandas"],
      "prerequisite_status": "Ready",
      "reason": "..."
    }
  ]
}
```

## 15. Testing
The test suite in [`tests/test_project_recommender.py`](file:///d:/projects/HCL%20Amplified%20-%20Course%20Recommendation%20System/tests/test_project_recommender.py) checks:
- Project loader data cleaning and URL validation.
- Missing gap critical weighting.
- Prerequisite readiness scoring.
- Greedy diversification penalties.
- Empty profile edge cases.
- Flask API integration routing, JSON validation, and error fallback code.
- Mapped 100% of tests to success execution.
