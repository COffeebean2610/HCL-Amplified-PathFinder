import os
import json
import pandas as pd
import numpy as np

# Import our helper modules
from src.data.loaders import load_raw_dataset
from src.data.cleaners import (
    clean_career_interests,
    clean_career_transferable,
    clean_skill_dependencies,
    clean_engineering_projects,
    clean_coursera_courses
)
from src.data.normalizers import (
    clean_text,
    parse_skills,
    normalize_skill_name,
    normalize_difficulty
)
from src.data.validators import validate_processed_data

def run_pipeline(raw_dir="data/raw", processed_dir="data/processed", reports_dir="data/reports"):
    """Orchestrate the preparation, cleaning, normalization, and validation of the RouteMaster knowledge base."""
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    print("STARTING ROUTEMASTER KNOWLEDGE BASE PREPARATION PIPELINE...")
    
    # ── 1. LOAD RAW DATASETS ───────────────────────────────────────────────────
    print("Loading raw datasets...")
    ci_df = load_raw_dataset("Career–Interest Dataset.csv", raw_dir)
    ctech_df = load_raw_dataset("CAREER–TECHNICAL SKILLS DATASET.csv", raw_dir)
    ctrans_df = load_raw_dataset("CAREER–TRANSFERABLE SKILLS DATASET.csv", raw_dir)
    cc_df = load_raw_dataset("coursera_courses.csv", raw_dir)
    proj_df = load_raw_dataset("Engineering Projects Dataset.csv", raw_dir)
    sd_df = load_raw_dataset("Skill Dependency _ Prerequisite Dataset.csv", raw_dir)
    
    print(f"  Career-Interest rows: {len(ci_df)}")
    print(f"  Career-Technical rows: {len(ctech_df)}")
    print(f"  Career-Transferable rows: {len(ctrans_df)}")
    print(f"  Coursera Courses rows: {len(cc_df)}")
    print(f"  Engineering Projects rows: {len(proj_df)}")
    print(f"  Skill Dependency rows: {len(sd_df)}")
    
    # ── 2. RUN ROW-LEVEL DATA CLEANING ──────────────────────────────────────────
    print("Executing specific data-level cleanup...")
    ci_df = clean_career_interests(ci_df)
    ctrans_df = clean_career_transferable(ctrans_df)
    sd_df = clean_skill_dependencies(sd_df)
    proj_df = clean_engineering_projects(proj_df)
    cc_df = clean_coursera_courses(cc_df)
    
    # Clean career_technical column names just in case
    ctech_df.columns = [c.strip() for c in ctech_df.columns]
    
    # ── 3. BUILD CANONICAL CAREERS REGISTRY ──────────────────────────────────────
    print("Building Canonical Careers Registry...")
    # Gather all unique career titles across Interest, Tech, and Transferable sets
    all_raw_career_titles = set()
    all_raw_career_titles.update(ci_df['career_title'].dropna().unique())
    all_raw_career_titles.update(ctech_df['career_title'].dropna().unique())
    all_raw_career_titles.update(ctrans_df['career_title'].dropna().unique())
    
    # Normalize titles (lowercase strip) and select display capitalization
    careers_data = []
    career_title_mapping = {}  # lowercase title -> canonical_id
    
    # Sort for deterministic ID assignment
    sorted_career_titles = sorted(list(all_raw_career_titles))
    
    for idx, title in enumerate(sorted_career_titles, 1):
        canonical_id = f"CAR_{idx:03d}"
        
        # Determine domain and description from Career-Interest dataset if possible
        ci_matches = ci_df[ci_df['career_title'].str.lower() == title.lower()]
        if not ci_matches.empty:
            # Pick first available domain and description
            domain = str(ci_matches.iloc[0]['career_domain']).strip()
            description = str(ci_matches.iloc[0]['career_description']).strip()
            display_title = str(ci_matches.iloc[0]['career_title']).strip()
        else:
            # Fallback to Technical or Transferable display title
            ctech_matches = ctech_df[ctech_df['career_title'].str.lower() == title.lower()]
            if not ctech_matches.empty:
                display_title = str(ctech_matches.iloc[0]['career_title']).strip()
            else:
                ctrans_matches = ctrans_df[ctrans_df['career_title'].str.lower() == title.lower()]
                if not ctrans_matches.empty:
                    display_title = str(ctrans_matches.iloc[0]['career_title']).strip()
                else:
                    display_title = title
            domain = "Unknown"
            description = ""
            
        # Collect original IDs mapping for traceability
        original_mappings = []
        
        # Mappings from Interest set
        ci_map_matches = ci_df[ci_df['career_title'].str.lower() == title.lower()]['career_id'].unique()
        for oid in ci_map_matches:
            original_mappings.append({"source": "career_interests", "original_id": oid})
            
        # Mappings from Tech set
        ctech_map_matches = ctech_df[ctech_df['career_title'].str.lower() == title.lower()]['career_id'].unique()
        for oid in ctech_map_matches:
            original_mappings.append({"source": "career_technical_skills", "original_id": oid})
            
        # Mappings from Transferable set
        ctrans_map_matches = ctrans_df[ctrans_df['career_title'].str.lower() == title.lower()]['career_id'].unique()
        for oid in ctrans_map_matches:
            original_mappings.append({"source": "career_transferable_skills", "original_id": oid})
            
        career_record = {
            "career_id": canonical_id,
            "career_title": display_title,
            "career_domain": domain,
            "career_description": description,
            "original_mappings": original_mappings
        }
        
        careers_data.append(career_record)
        career_title_mapping[title.lower()] = canonical_id
        
    print(f"  Created {len(careers_data)} canonical careers.")
    
    # ── 4. BUILD CANONICAL SKILLS REGISTRY ───────────────────────────────────────
    print("Building Canonical Skills Registry...")
    # Gather all unique skills from core datasets
    core_skill_sources = []
    
    # 1. Tech skills
    for idx, row in ctech_df.iterrows():
        core_skill_sources.append({
            "name": str(row['skill_name']).strip(),
            "id": str(row['skill_id']).strip(),
            "category": str(row['skill_category']).strip(),
            "source": "career_technical_skills",
            "type": "technical"
        })
        
    # 2. Transferable skills
    for idx, row in ctrans_df.iterrows():
        core_skill_sources.append({
            "name": str(row['skill_name']).strip(),
            "id": str(row['skill_id']).strip(),
            "category": str(row['skill_category']).strip(),
            "source": "career_transferable_skills",
            "type": "transferable"
        })
        
    # 3. Dependency skills
    for idx, row in sd_df.iterrows():
        core_skill_sources.append({
            "name": str(row['source_skill']).strip(),
            "id": str(row['source_skill_id']).strip(),
            "category": str(row['domain']).strip(),
            "source": "skill_dependencies",
            "type": "technical"
        })
        core_skill_sources.append({
            "name": str(row['target_skill']).strip(),
            "id": str(row['target_skill_id']).strip(),
            "category": str(row['domain']).strip(),
            "source": "skill_dependencies",
            "type": "technical"
        })
        
    # 4. Project skills
    for idx, row in proj_df.iterrows():
        parsed = parse_skills(row['skills'])
        for s in parsed:
            core_skill_sources.append({
                "name": s,
                "id": None,
                "category": str(row['domain']).strip(),
                "source": "projects",
                "type": "technical"
            })
            
    # Process Coursera skills (which represents the largest group)
    print("  Parsing and checking Coursera course skills...")
    coursera_skills_set = set()
    for s in cc_df['Skills'].dropna():
        parsed = parse_skills(s, source="coursera")
        coursera_skills_set.update(parsed)
        
    # Build core map to prioritize display casing and categories
    core_skills_map = {}  # lowercase -> merged info
    for item in core_skill_sources:
        name_lower = item["name"].lower()
        if name_lower not in core_skills_map:
            core_skills_map[name_lower] = {
                "display_name": item["name"],
                "categories": set(),
                "types": set(),
                "mappings": []
            }
        # Keep longest/nicest casing
        if len(item["name"]) > len(core_skills_map[name_lower]["display_name"]):
            core_skills_map[name_lower]["display_name"] = item["name"]
            
        core_skills_map[name_lower]["categories"].add(item["category"])
        core_skills_map[name_lower]["types"].add(item["type"])
        if item["id"]:
            core_skills_map[name_lower]["mappings"].append({
                "source": item["source"],
                "original_id": item["id"],
                "original_name": item["name"]
            })
            
    # Assign canonical IDs
    skills_data = []
    skill_name_mapping = {}  # lowercase -> full canonical record
    skill_id_counter = 1
    
    # 1. First process core skills (sorted for determinism)
    for norm_key in sorted(core_skills_map.keys()):
        canonical_id = f"SK_{skill_id_counter:05d}"
        skill_id_counter += 1
        
        info = core_skills_map[norm_key]
        display_name, _ = normalize_skill_name(info["display_name"])
        
        # Categorization logic
        categories = list(info["categories"])
        primary_category = categories[0] if categories else "Other"
        
        types = list(info["types"])
        primary_type = "technical"
        if "transferable" in types and "technical" not in types:
            primary_type = "transferable"
            
        skill_record = {
            "skill_id": canonical_id,
            "skill_name": display_name,
            "normalized_name": norm_key,
            "skill_category": primary_category,
            "skill_type": primary_type,
            "original_mappings": info["mappings"]
        }
        skills_data.append(skill_record)
        skill_name_mapping[norm_key] = skill_record
        
    # 2. Add Coursera-only skills
    print("  Integrating Coursera course skills...")
    for s in sorted(list(coursera_skills_set)):
        norm_key = s.lower()
        if norm_key not in skill_name_mapping:
            # Coursera-only skill
            canonical_id = f"SK_{skill_id_counter:05d}"
            skill_id_counter += 1
            
            display_name, _ = normalize_skill_name(s, known_skills_map={k: v["skill_name"] for k, v in skill_name_mapping.items()})
            
            skill_record = {
                "skill_id": canonical_id,
                "skill_name": display_name,
                "normalized_name": norm_key,
                "skill_category": "Other",
                "skill_type": "other",
                "original_mappings": [{"source": "coursera_courses", "original_id": None, "original_name": s}]
            }
            skills_data.append(skill_record)
            skill_name_mapping[norm_key] = skill_record
            
    print(f"  Created {len(skills_data)} canonical skills ({len(core_skills_map)} core + {len(skills_data) - len(core_skills_map)} Coursera-only).")
    
    # Helper to resolve skill names to canonical IDs
    def get_canonical_skill_id(name_str):
        cleaned = clean_text(name_str).lower()
        # Direct check
        if cleaned in skill_name_mapping:
            return skill_name_mapping[cleaned]["skill_id"]
        # Fallback to normalized alias check
        _, norm_alias = normalize_skill_name(cleaned)
        if norm_alias in skill_name_mapping:
            return skill_name_mapping[norm_alias]["skill_id"]
        # If still not found, return None
        return None
        
    # ── 5. PROCESS RELATIONSHIPS AND LINK TABLES ────────────────────────────────
    print("Mapping relationships and constructing link collections...")
    
    # A. Career Interests
    career_interests = []
    for idx, row in ci_df.iterrows():
        title = str(row['career_title']).strip()
        cid = career_title_mapping[title.lower()]
        
        career_interests.append({
            "career_interest_id": f"CI_{idx+1:03d}",
            "career_id": cid,
            "interest_type": clean_text(row['interest_type']),
            "interest_score": float(row['interest_score']),
            "interest_description": clean_text(row['interest_description'])
        })
        
    # B. Career Technical Skills
    career_skills = []
    for idx, row in ctech_df.iterrows():
        title = str(row['career_title']).strip()
        cid = career_title_mapping[title.lower()]
        
        skill_name = str(row['skill_name']).strip()
        sid = get_canonical_skill_id(skill_name)
        
        career_skills.append({
            "career_skill_id": f"CS_{idx+1:04d}",
            "career_id": cid,
            "skill_id": sid,
            "importance": clean_text(row['importance']),
            "in_demand": clean_text(row['in_demand']),
            "hot_technology": clean_text(row['hot_technology']),
            "description": clean_text(row['description'])
        })
        
    # C. Career Transferable Skills
    career_transferable_skills = []
    for idx, row in ctrans_df.iterrows():
        title = str(row['career_title']).strip()
        cid = career_title_mapping[title.lower()]
        
        skill_name = str(row['skill_name']).strip()
        sid = get_canonical_skill_id(skill_name)
        
        career_transferable_skills.append({
            "career_trans_id": f"CTS_{idx+1:04d}",
            "career_id": cid,
            "skill_id": sid,
            "importance_score": float(row['importance_score']),
            "data_value": clean_text(row['data_value']),
            "description": clean_text(row['description'])
        })
        
    # D. Skill Dependencies / Prerequisites
    skill_dependencies = []
    for idx, row in sd_df.iterrows():
        src_name = str(row['source_skill']).strip()
        src_id = get_canonical_skill_id(src_name)
        
        tgt_name = str(row['target_skill']).strip()
        tgt_id = get_canonical_skill_id(tgt_name)
        
        skill_dependencies.append({
            "dependency_id": f"DEP_{idx+1:03d}",
            "source_skill_id": src_id,
            "source_skill_name": skill_name_mapping[src_name.lower()]["skill_name"],
            "target_skill_id": tgt_id,
            "target_skill_name": skill_name_mapping[tgt_name.lower()]["skill_name"],
            "relationship": clean_text(row['relationship']),
            "reason": clean_text(row['reason']),
            "difficulty": normalize_difficulty(row['difficulty']),
            "domain": clean_text(row['domain'])
        })
        
    # E. Courses (Coursera)
    courses = []
    for idx, row in cc_df.iterrows():
        raw_rating = row['Course Rating']
        try:
            rating = float(raw_rating)
            if np.isnan(rating):
                rating = None
        except (ValueError, TypeError):
            rating = None  # Non-numeric ratings mapped to None
            
        raw_skills = row['Skills']
        parsed_skills = parse_skills(raw_skills, source="coursera")
        canonical_sids = [get_canonical_skill_id(s) for s in parsed_skills]
        # Filter out None values just in case
        canonical_sids = [s for s in canonical_sids if s is not None]
        
        courses.append({
            "course_id": f"CRS_{idx+1:04d}",
            "course_name": clean_text(row['Course Name']),
            "organization": clean_text(row['University']),
            "difficulty": normalize_difficulty(row['Difficulty Level']),
            "original_difficulty": clean_text(row['Difficulty Level']),
            "rating": rating,
            "original_rating": clean_text(raw_rating),
            "url": clean_text(row['Course URL']),
            "description": clean_text(row['Course Description']),
            "skills": canonical_sids,
            "skills_raw": clean_text(raw_skills)
        })
        
    # F. Engineering Projects
    projects = []
    for idx, row in proj_df.iterrows():
        raw_skills = row['skills']
        parsed_skills = parse_skills(raw_skills)
        canonical_sids = [get_canonical_skill_id(s) for s in parsed_skills]
        canonical_sids = [s for s in canonical_sids if s is not None]
        
        tech_stack = parse_skills(row['tech_stack'])
        tags = parse_skills(row['tags'])
        
        # Clean github_url from Pandas float nan representation
        raw_github_url = row['github_url']
        if pd.isna(raw_github_url) or str(raw_github_url).strip().lower() in ["nan", "none", ""]:
            github_url = None
        else:
            github_url = str(raw_github_url).strip()
            
        projects.append({
            "project_id": f"PROJ_{idx+1:03d}",
            "project_name": clean_text(row['project_name']),
            "domain": clean_text(row['domain']),
            "difficulty": normalize_difficulty(row['difficulty']),
            "github_url": github_url,
            "description": clean_text(row['description']),
            "tech_stack": tech_stack,
            "tags": tags,
            "skills": canonical_sids,
            "skills_raw": clean_text(raw_skills)
        })
        
    # ── 6. SAVE PROCESSED DATASETS (JSON & CSV) ──────────────────────────────────
    print("Writing cleaned and structured knowledge base to disk...")
    
    # Define exports
    exports = {
        "careers": (careers_data, ["career_id", "career_title", "career_domain", "career_description"]),
        "skills": (skills_data, ["skill_id", "skill_name", "normalized_name", "skill_category", "skill_type"]),
        "courses": (courses, ["course_id", "course_name", "organization", "difficulty", "rating", "url", "description", "skills"]),
        "projects": (projects, ["project_id", "project_name", "domain", "difficulty", "github_url", "description", "tech_stack", "tags", "skills"]),
        "skill_dependencies": (skill_dependencies, ["dependency_id", "source_skill_id", "source_skill_name", "target_skill_id", "target_skill_name", "relationship", "reason", "difficulty", "domain"]),
        "career_interests": (career_interests, ["career_interest_id", "career_id", "interest_type", "interest_score", "interest_description"]),
        "career_skills": (career_skills, ["career_skill_id", "career_id", "skill_id", "importance", "in_demand", "hot_technology", "description"]),
        "career_transferable_skills": (career_transferable_skills, ["career_trans_id", "career_id", "skill_id", "importance_score", "data_value", "description"])
    }
    
    for coll_name, (data_list, columns) in exports.items():
        # Save JSON
        json_path = os.path.join(processed_dir, f"{coll_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=2, ensure_ascii=False)
            
        # Save CSV (converting lists to strings or handling special formats)
        csv_data = []
        for item in data_list:
            row_dict = {}
            for col in columns:
                val = item[col]
                # Convert list formats to comma-separated strings for CSV
                if isinstance(val, list):
                    # Special check: for skills lists, write comma-separated skill names instead of IDs
                    # to keep legacy recommender functional on the CSVs
                    if col == "skills" and coll_name in ["courses", "projects"]:
                        # Look up names for each skill ID
                        names = []
                        for sid in val:
                            # find skill
                            matching_skills = [sk for sk in skills_data if sk["skill_id"] == sid]
                            if matching_skills:
                                names.append(matching_skills[0]["skill_name"])
                        row_dict[col] = ", ".join(names)
                    else:
                        row_dict[col] = ", ".join([str(x) for x in val])
                else:
                    row_dict[col] = val
            csv_data.append(row_dict)
            
        csv_df = pd.DataFrame(csv_data)
        csv_path = os.path.join(processed_dir, f"{coll_name}.csv")
        csv_df.to_csv(csv_path, index=False, encoding="utf-8")
        
    # ALSO export legacy compatible `coursera_courses.csv` directly in data/processed/
    # to serve as an exact drop-in replacement for the recommender prototype
    print("Writing legacy compatible courses CSV...")
    legacy_courses = []
    for item in courses:
        # Convert skills list to comma-separated skill names
        skill_names = []
        for sid in item["skills"]:
            matching = [s for s in skills_data if s["skill_id"] == sid]
            if matching:
                skill_names.append(matching[0]["skill_name"])
                
        # Handle "Not Calibrated" ratings as empty/NaN in Pandas CSV
        rating_val = item["rating"] if item["rating"] is not None else np.nan
        
        legacy_courses.append({
            "Course Name": item["course_name"],
            "University": item["organization"],
            "Difficulty Level": item["difficulty"],
            "Course Rating": rating_val,
            "Course URL": item["url"],
            "Course Description": item["description"],
            "Skills": ", ".join(skill_names)
        })
        
    legacy_df = pd.DataFrame(legacy_courses)
    legacy_df.to_csv(os.path.join(processed_dir, "courses.csv"), index=False, encoding="utf-8")
    
    print(f"SUCCESS: Wrote all processed files to '{processed_dir}'")
    
    # ── 7. RUN AUTOMATED VALIDATION CHECKS ──────────────────────────────────────
    print("Executing data validation checks...")
    is_valid = validate_processed_data(processed_dir, reports_dir)
    if is_valid:
        print("PIPELINE COMPLETED SUCCESSFULLY: All validation checks passed.")
    else:
        print("PIPELINE COMPLETED WITH WARNINGS: Some validation errors were logged in 'data/reports/validation_report.md'.")

if __name__ == "__main__":
    run_pipeline()
