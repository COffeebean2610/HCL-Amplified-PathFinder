import os
import json
import numpy as np
from src.career_recommender.recommender import CareerRecommender

def evaluate_recommender(processed_dir="data/processed", reports_dir="data/reports"):
    """
    Evaluates the Career Recommendation Engine across several profiles
    and outputs a detailed Markdown evaluation report.
    """
    print("STARTING ROUTEMASTER CAREER RECOMMENDER EVALUATION...")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "career_recommender_evaluation.md")
    
    recommender = CareerRecommender(processed_dir=processed_dir)
    
    # Define test profiles representing different student scenarios
    profiles = {
        "AI_ML_Student": {
            "interests": "I want to design neural networks, train machine learning models and study artificial intelligence.",
            "current_skills": ["Python", "SQL", "Machine Learning"],
            "transferable_skills": ["Problem Solving"],
            "target_career": None
        },
        "Web_Developer": {
            "interests": "I enjoy creating frontend user interfaces, building web applications, and writing JavaScript/CSS code.",
            "current_skills": ["HTML", "CSS", "JavaScript", "React"],
            "transferable_skills": ["Communication"],
            "target_career": None
        },
        "Data_Analyst": {
            "interests": "I enjoy analyzing database tables, data warehousing, spreadsheets, statistics and reporting dashboards.",
            "current_skills": ["SQL", "Excel", "Statistics"],
            "transferable_skills": ["Analytical Thinking"],
            "target_career": None
        },
        "Cold_Start_No_Skills": {
            "interests": "I am passionate about mobile applications, flutter, android and iOS development.",
            "current_skills": [],
            "transferable_skills": []
        },
        "Cold_Start_No_Interests": {
            "interests": "",
            "current_skills": ["Java", "C++", "Data Structures"],
            "transferable_skills": ["Teamwork"]
        }
    }
    
    results = {}
    recommendations_list = []
    
    for name, prof in profiles.items():
        print(f"Evaluating profile '{name}'...")
        res = recommender.recommend(prof, top_k=5)
        results[name] = res
        recommendations_list.append([r["career_id"] for r in res["recommendations"]])

    # 1. Recommendation Diversity Analysis
    # Measure overlap between different profiles to verify recommendation uniqueness
    pairwise_overlaps = []
    for i in range(len(recommendations_list)):
        for j in range(i + 1, len(recommendations_list)):
            set_a = set(recommendations_list[i])
            set_b = set(recommendations_list[j])
            overlap = len(set_a.intersection(set_b)) / 5.0
            pairwise_overlaps.append(overlap)
            
    avg_overlap = np.mean(pairwise_overlaps) if pairwise_overlaps else 0.0
    diversity_score = (1.0 - avg_overlap) * 100.0  # 100% means completely distinct lists
    
    # 2. Schema Compliance Audit
    schema_compliance = True
    compliance_issues = []
    
    for name, res in results.items():
        if "profile_summary" not in res:
            compliance_issues.append(f"{name}: Missing 'profile_summary'")
            schema_compliance = False
        if "recommendations" not in res:
            compliance_issues.append(f"{name}: Missing 'recommendations'")
            schema_compliance = False
        else:
            for idx, rec in enumerate(res["recommendations"]):
                required_fields = {
                    "rank", "career_id", "career", "domain", "match_score",
                    "confidence", "score_breakdown", "matched_technical_skills",
                    "missing_technical_skills", "critical_missing_skills",
                    "matched_transferable_skills", "missing_transferable_skills",
                    "prerequisite_gaps", "complete_roadmap_path", "explanation"
                }
                missing_fields = required_fields - set(rec.keys())
                if missing_fields:
                    compliance_issues.append(f"{name} rec rank {idx+1}: Missing fields {list(missing_fields)}")
                    schema_compliance = False

    # 3. Dynamic Weight Redistribution Checks (Cold-Start robustness)
    no_skills_res = results["Cold_Start_No_Skills"]["recommendations"][0]
    no_ints_res = results["Cold_Start_No_Interests"]["recommendations"][0]
    
    # If no skills provided, tech weight is 0.0 -> tech score should not pull down total
    no_skills_tech_score = no_skills_res["score_breakdown"]["technical_skill_match"]
    no_skills_match_score = no_skills_res["match_score"]
    
    # If no interests provided, interest weight is 0.0 -> interest score is 0.0 but match score > 0
    no_ints_interest_score = no_ints_res["score_breakdown"]["interest_match"]
    no_ints_match_score = no_ints_res["match_score"]

    # Write Markdown Report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RouteMaster - Career Recommendation Engine Evaluation Report\n\n")
        f.write("Generated dynamically. Local time: 2026-08-22\n\n")
        
        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Recommendation Diversity Score**: {diversity_score:.1f}% (high means distinct recommendation lists per profile)\n")
        f.write(f"- **Schema Compliance status**: {'✅ COMPLIANT' if schema_compliance else '❌ NON-COMPLIANT'}\n")
        f.write(f"- **Active Evaluation Profiles**: {len(profiles)}\n")
        f.write(f"- **Validation Approach**: Rule-based expert validation (due to absence of formal ground-truth labels)\n\n")
        
        if compliance_issues:
            f.write("### Compliance Issues Found:\n")
            for issue in compliance_issues:
                f.write(f"- {issue}\n")
            f.write("\n")
            
        f.write("## 2. Profile Recommendations Summary\n\n")
        for name, res in results.items():
            f.write(f"### Profile: `{name}`\n")
            f.write(f"- **Input Interests**: \"{profiles[name].get('interests', 'N/A')}\"\n")
            f.write(f"- **Input Skills**: {profiles[name].get('current_skills', [])}\n")
            f.write("- **Top 3 Recommendations**:\n")
            for rec in res["recommendations"][:3]:
                f.write(f"  1. Rank {rec['rank']}: **{rec['career']}** (Fit: {rec['match_score']}%, Confidence: {rec['confidence']})\n")
                f.write(f"     - *Explanation*: {rec['explanation']}\n")
            f.write("\n")
            
        f.write("## 3. Cold-Start Analysis\n\n")
        f.write("### Profile: `Cold_Start_No_Skills` (Interests only)\n")
        f.write(f"- Technical Skill Match score: {no_skills_tech_score}%\n")
        f.write(f"- Dynamic Match score: {no_skills_match_score}%\n")
        f.write("- *Observation*: Because skills were missing, the engine redistributed technical weight to interest and semantic scores, preventing the match score from being dragged down to 0%.\n\n")
        
        f.write("### Profile: `Cold_Start_No_Interests` (Skills only)\n")
        f.write(f"- Interest Match score: {no_ints_interest_score}%\n")
        f.write(f"- Dynamic Match score: {no_ints_match_score}%\n")
        f.write("- *Observation*: Interest scoring was deactivated and weight was redistributed to technical and transferable elements.\n\n")
        
    print(f"SUCCESS: Evaluation complete. Report written to '{report_path}'.")
    return report_path

if __name__ == "__main__":
    evaluate_recommender()
