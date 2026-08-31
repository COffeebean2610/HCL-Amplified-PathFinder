import os
import pandas as pd
import numpy as np
import re

def profile_dataset(name, filepath):
    """Profile a single CSV dataset and return its statistics and anomalies."""
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
        
    try:
        # Load raw file
        df = pd.read_csv(filepath)
        
        # Basic stats
        rows, cols = df.shape
        duplicates = int(df.duplicated().sum())
        
        col_profiles = []
        anomalies = []
        
        # Check for column anomalies
        unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:")]
        if unnamed_cols:
            anomalies.append(f"Found unexpected columns: {unnamed_cols}")
            
        # Check if first row duplicates header
        first_row_matches_header = False
        if len(df) > 0:
            first_row_vals = [str(x).strip() for x in df.iloc[0].values]
            header_vals = [str(x).strip() for x in df.columns]
            if first_row_vals == header_vals:
                first_row_matches_header = True
                anomalies.append("First row contains duplicated header labels.")
                
        # Check column by column
        for col in df.columns:
            missing_count = int(df[col].isnull().sum())
            missing_pct = (missing_count / rows) * 100 if rows > 0 else 0
            unique_count = int(df[col].nunique())
            dtype = str(df[col].dtype)
            
            # Non-null examples
            non_null_samples = df[col].dropna().head(3).tolist()
            examples = [str(x) for x in non_null_samples]
            
            col_profiles.append({
                "column_name": col,
                "data_type": dtype,
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_count": unique_count,
                "examples": examples
            })
            
            # Anomaly checks on specific columns
            col_lower = col.lower().strip()
            
            # 1. Check for duplicate headers in rows
            row_header_matches = df[df[col] == col]
            if len(row_header_matches) > 0 and col != 'career_id' and not first_row_matches_header:
                anomalies.append(f"Column '{col}' has {len(row_header_matches)} rows containing header-like values (e.g. value is '{col}').")
            
            # 2. Difficulty column checks
            if 'difficulty' in col_lower or 'level' in col_lower:
                unique_diffs = df[col].dropna().unique().tolist()
                unusual_diffs = [d for d in unique_diffs if str(d).strip() not in ['Beginner', 'Intermediate', 'Advanced']]
                if unusual_diffs:
                    anomalies.append(f"Column '{col}' has unusual difficulty values: {unusual_diffs}")
            
            # 3. URL checks
            if 'url' in col_lower or 'link' in col_lower:
                bad_urls = df[df[col].notnull() & ~df[col].astype(str).str.startswith('http')][col].tolist()
                if bad_urls:
                    anomalies.append(f"Column '{col}' has {len(bad_urls)} malformed/missing HTTP scheme URLs. Examples: {bad_urls[:3]}")
                    
            # 4. Rating checks
            if 'rating' in col_lower or 'stars' in col_lower:
                non_numeric = df[pd.to_numeric(df[col], errors='coerce').isna()][col].dropna().unique().tolist()
                if non_numeric:
                    anomalies.append(f"Column '{col}' contains non-numeric ratings: {non_numeric}")
                    
            # 5. Check for separator anomalies (e.g. double spaces in skills list)
            if 'skill' in col_lower and 'id' not in col_lower and 'category' not in col_lower:
                # check if skills are separated by double spaces instead of commas
                double_spaces = df[df[col].astype(str).str.contains(r'\s{2,}')]
                commas = df[df[col].astype(str).str.contains(',')]
                if len(double_spaces) > 0 and len(commas) == 0:
                    anomalies.append(f"Column '{col}' uses double spaces (2+ spaces) as separators. No commas found.")
        
        return {
            "dataset_name": name,
            "filepath": filepath,
            "rows": rows,
            "columns": cols,
            "duplicates": duplicates,
            "col_profiles": col_profiles,
            "anomalies": anomalies
        }
    except Exception as e:
        return {"error": f"Failed to profile {name}: {str(e)}"}

def generate_report(raw_dir="data/raw", report_path="data/reports/data_profiling_report.md"):
    """Profile all raw datasets and generate a comprehensive markdown report."""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    datasets = {
        "Career-Interest Dataset": "Career–Interest Dataset.csv",
        "Career-Technical Skills Dataset": "CAREER–TECHNICAL SKILLS DATASET.csv",
        "Career-Transferable Skills Dataset": "CAREER–TRANSFERABLE SKILLS DATASET.csv",
        "Coursera Courses Dataset": "coursera_courses.csv",
        "Engineering Projects Dataset": "Engineering Projects Dataset.csv",
        "Skill Dependency / Prerequisite Dataset": "Skill Dependency _ Prerequisite Dataset.csv"
    }
    
    profiles = []
    for name, filename in datasets.items():
        filepath = os.path.join(raw_dir, filename)
        profile = profile_dataset(name, filepath)
        profiles.append(profile)
        
    # Write Markdown Report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RouteMaster - Data Profiling Report (Raw Datasets)\n\n")
        f.write(f"Generated dynamically. Local time: 2026-08-22\n\n")
        f.write("This profiling report analyzes the structure, metrics, columns, and quality anomalies of the raw datasets.\n\n")
        
        # Executive Summary Table
        f.write("## Executive Summary\n\n")
        f.write("| Dataset Name | Row Count | Column Count | Duplicate Rows | Anomalies Detected |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for p in profiles:
            if "error" in p:
                f.write(f"| {p.get('dataset_name', 'Unknown')} | ERROR | ERROR | ERROR | {p['error']} |\n")
            else:
                anom_count = len(p['anomalies'])
                f.write(f"| {p['dataset_name']} | {p['rows']} | {p['columns']} | {p['duplicates']} | {anom_count} |\n")
        f.write("\n---\n\n")
        
        # Detailed profile for each dataset
        for p in profiles:
            if "error" in p:
                continue
                
            f.write(f"## Dataset: {p['dataset_name']}\n\n")
            f.write(f"- **File Path**: `{p['filepath']}`\n")
            f.write(f"- **Rows**: {p['rows']}\n")
            f.write(f"- **Columns**: {p['columns']}\n")
            f.write(f"- **Duplicate Rows**: {p['duplicates']}\n\n")
            
            # Anomalies
            f.write("### Data Quality Anomalies\n\n")
            if p['anomalies']:
                for a in p['anomalies']:
                    f.write(f"- ⚠️ {a}\n")
            else:
                f.write("- ✅ No structural anomalies detected.\n")
            f.write("\n")
            
            # Column profiles
            f.write("### Column Details\n\n")
            f.write("| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |\n")
            f.write("| --- | --- | --- | --- | --- | --- |\n")
            for c in p['col_profiles']:
                samples = ", ".join([f"`{repr(x)}`" for x in c['examples']])
                f.write(f"| {c['column_name']} | {c['data_type']} | {c['missing_count']} | {c['missing_pct']:.1f}% | {c['unique_count']} | {samples} |\n")
            f.write("\n---\n\n")
            
    print(f"SUCCESS: Data profiling report successfully generated at '{report_path}'")

if __name__ == "__main__":
    generate_report()
