import os
import re
import json
import pandas as pd
import networkx as nx

def validate_entity(entity, schema):
    """Validate a single dictionary object against a schema."""
    errors = []
    
    # Check required fields
    for field, rule in schema.items():
        is_required = rule.get("required", False)
        if is_required and field not in entity:
            errors.append(f"Missing required field: '{field}'")
            continue
            
        if field in entity:
            val = entity[field]
            expected_type = rule.get("type")
            
            # Check type
            if expected_type is not None:
                if not isinstance(val, expected_type):
                    # Handle float-int conversion allowance or None types
                    if expected_type == float and isinstance(val, int):
                        pass
                    elif isinstance(expected_type, tuple) and type(val) in expected_type:
                        pass
                    else:
                        errors.append(f"Field '{field}' has type {type(val).__name__}, expected {expected_type}")
                        
            # Check allowed values
            allowed_vals = rule.get("allowed")
            if allowed_vals and val not in allowed_vals:
                errors.append(f"Field '{field}' has invalid value '{val}', allowed: {allowed_vals}")
                
            # Check regex
            regex_pattern = rule.get("regex")
            if regex_pattern and isinstance(val, str):
                if not re.match(regex_pattern, val):
                    errors.append(f"Field '{field}' with value '{val}' does not match pattern '{regex_pattern}'")
                    
    return errors

def validate_processed_data(processed_dir="data/processed", report_dir="data/reports"):
    """Validate all processed datasets and generate a markdown report."""
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "validation_report.md")
    
    from .schemas import (
        CAREER_SCHEMA, SKILL_SCHEMA, COURSE_SCHEMA, PROJECT_SCHEMA,
        DEPENDENCY_SCHEMA, CAREER_INTEREST_SCHEMA, CAREER_SKILL_SCHEMA,
        CAREER_TRANSFERABLE_SKILL_SCHEMA
    )
    
    files_to_validate = {
        "careers.json": CAREER_SCHEMA,
        "skills.json": SKILL_SCHEMA,
        "courses.json": COURSE_SCHEMA,
        "projects.json": PROJECT_SCHEMA,
        "skill_dependencies.json": DEPENDENCY_SCHEMA,
        "career_interests.json": CAREER_INTEREST_SCHEMA,
        "career_skills.json": CAREER_SKILL_SCHEMA,
        "career_transferable_skills.json": CAREER_TRANSFERABLE_SKILL_SCHEMA
    }
    
    validation_results = {}
    total_errors = 0
    
    # 1. Structural Validation
    for filename, schema in files_to_validate.items():
        filepath = os.path.join(processed_dir, filename)
        if not os.path.exists(filepath):
            validation_results[filename] = {
                "status": "MISSING",
                "record_count": 0,
                "schema_errors": [f"File {filename} is missing."],
                "relational_errors": []
            }
            total_errors += 1
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            schema_errors = []
            for idx, item in enumerate(data):
                errs = validate_entity(item, schema)
                for e in errs:
                    schema_errors.append(f"Row {idx}: {e}")
                    
            validation_results[filename] = {
                "status": "VALIDATED" if not schema_errors else "FAILED_SCHEMA",
                "record_count": len(data),
                "schema_errors": schema_errors[:20],  # cap at 20 examples
                "schema_error_count": len(schema_errors),
                "relational_errors": []
            }
            total_errors += len(schema_errors)
        except Exception as e:
            validation_results[filename] = {
                "status": "ERROR",
                "record_count": 0,
                "schema_errors": [f"Failed to load or parse JSON: {str(e)}"],
                "relational_errors": []
            }
            total_errors += 1
            
    # 2. Relational Integrity Checks (only if base files exist and loaded successfully)
    # Load careers and skills to check IDs
    careers_set = set()
    skills_set = set()
    
    careers_file = os.path.join(processed_dir, "careers.json")
    if os.path.exists(careers_file):
        try:
            with open(careers_file, "r") as f:
                careers_set = {item["career_id"] for item in json.load(f)}
        except:
            pass
            
    skills_file = os.path.join(processed_dir, "skills.json")
    if os.path.exists(skills_file):
        try:
            with open(skills_file, "r") as f:
                skills_set = {item["skill_id"] for item in json.load(f)}
        except:
            pass
            
    # Now run foreign key checks
    for filename in files_to_validate.keys():
        if filename not in validation_results or validation_results[filename]["status"] in ["MISSING", "ERROR"]:
            continue
            
        filepath = os.path.join(processed_dir, filename)
        rel_errors = []
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                
            for idx, item in enumerate(data):
                # Check career_id reference
                if "career_id" in item:
                    cid = item["career_id"]
                    if cid not in careers_set:
                        rel_errors.append(f"Row {idx}: Referencing unknown career ID '{cid}'")
                        
                # Check skill_id reference
                if "skill_id" in item:
                    sid = item["skill_id"]
                    if sid not in skills_set:
                        rel_errors.append(f"Row {idx}: Referencing unknown skill ID '{sid}'")
                        
                # Check source_skill_id and target_skill_id
                if "source_skill_id" in item:
                    sid = item["source_skill_id"]
                    if sid not in skills_set:
                        rel_errors.append(f"Row {idx}: Unknown source skill ID '{sid}'")
                if "target_skill_id" in item:
                    sid = item["target_skill_id"]
                    if sid not in skills_set:
                        rel_errors.append(f"Row {idx}: Unknown target skill ID '{sid}'")
                        
                # Check lists of skills (courses and projects)
                if "skills" in item and isinstance(item["skills"], list) and filename in ["courses.json", "projects.json"]:
                    for sid in item["skills"]:
                        if sid not in skills_set:
                            rel_errors.append(f"Row {idx}: List contains unknown skill ID '{sid}'")
                            
                # Check URLs for basic validity
                if "url" in item:
                    url = item["url"]
                    if not str(url).startswith("http"):
                        rel_errors.append(f"Row {idx}: Malformed course URL: '{url}'")
                if "github_url" in item and item["github_url"] is not None:
                    url = item["github_url"]
                    if not str(url).startswith("http"):
                        rel_errors.append(f"Row {idx}: Malformed GitHub URL: '{url}'")
                        
            validation_results[filename]["relational_errors"] = rel_errors[:20]
            validation_results[filename]["relational_error_count"] = len(rel_errors)
            total_errors += len(rel_errors)
            if len(rel_errors) > 0 and validation_results[filename]["status"] == "VALIDATED":
                validation_results[filename]["status"] = "FAILED_RELATIONAL"
                
        except Exception as e:
            validation_results[filename]["relational_errors"] = [f"FK Check failed: {str(e)}"]
            total_errors += 1
            
    # 3. Check for cycles in prerequisites
    cycle_errors = []
    dep_file = os.path.join(processed_dir, "skill_dependencies.json")
    if os.path.exists(dep_file):
        try:
            with open(dep_file, "r") as f:
                deps = json.load(f)
            G = nx.DiGraph()
            for d in deps:
                G.add_edge(d["source_skill_id"], d["target_skill_id"])
            cycles = list(nx.simple_cycles(G))
            if cycles:
                for cycle in cycles:
                    cycle_names = []
                    for sid in cycle:
                        cycle_names.append(sid)
                    cycle_errors.append(f"Cycle detected in prerequisites: {' -> '.join(cycle_names)}")
                total_errors += len(cycle_errors)
        except Exception as e:
            cycle_errors.append(f"Could not construct skill graph for cycle check: {str(e)}")
            total_errors += 1
            
    # Write Validation Report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RouteMaster - Knowledge Base Validation Report\n\n")
        f.write(f"Generated dynamically. Local time: 2026-08-22\n\n")
        f.write(f"**Overall Validation Status**: {'FAILED ❌' if total_errors > 0 else 'PASSED ✅'}\n")
        f.write(f"**Total Errors Found**: {total_errors}\n\n")
        
        # Summary Table
        f.write("## Dataset Validation Status Summary\n\n")
        f.write("| Collection / File | Records | Status | Schema Errors | Relational Errors |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for filename, res in validation_results.items():
            sch_errs = res.get("schema_error_count", len(res["schema_errors"]))
            rel_errs = res.get("relational_error_count", len(res["relational_errors"]))
            status_emoji = "✅" if res["status"] == "VALIDATED" else "❌"
            f.write(f"| `{filename}` | {res['record_count']} | {status_emoji} {res['status']} | {sch_errs} | {rel_errs} |\n")
            
        if cycle_errors:
            f.write("\n## Graph Cycles / Toplogical Errors\n\n")
            for c in cycle_errors:
                f.write(f"- ❌ {c}\n")
        else:
            f.write("\n## Graph Integrity\n\n- ✅ Prerequisite skill dependency graph is a valid Directed Acyclic Graph (no cycles detected).\n")
            
        # Detailed errors by file
        f.write("\n## Detailed Error Logs\n\n")
        has_details = False
        for filename, res in validation_results.items():
            sch_errs = res.get("schema_error_count", len(res["schema_errors"]))
            rel_errs = res.get("relational_error_count", len(res["relational_errors"]))
            
            if sch_errs > 0 or rel_errs > 0:
                has_details = True
                f.write(f"### File: `{filename}`\n\n")
                if sch_errs > 0:
                    f.write(f"#### Schema Errors ({sch_errs} total, showing first 20):\n")
                    for e in res["schema_errors"]:
                        f.write(f"- `{e}`\n")
                    f.write("\n")
                if rel_errs > 0:
                    f.write(f"#### Relational Errors ({rel_errs} total, showing first 20):\n")
                    for e in res["relational_errors"]:
                        f.write(f"- `{e}`\n")
                    f.write("\n")
                    
        if not has_details and not cycle_errors:
            f.write("All datasets passed all validations cleanly! No errors found.\n")
            
    print(f"SUCCESS: Validation report generated at '{report_path}'. Overall status: {'FAILED' if total_errors > 0 else 'PASSED'}")
    return total_errors == 0
