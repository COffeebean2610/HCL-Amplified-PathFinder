import pandas as pd
import numpy as np
import re

def clean_career_interests(df):
    """Clean the Career-Interest dataset, handling column shifts and backslashes in headers."""
    # Rename columns to remove backslashes and strip whitespace
    df.columns = [c.replace('\\', '').strip() for c in df.columns]
    
    # Check for column shift due to unquoted commas in Generative AI career description
    if 'Unnamed: 7' in df.columns or 'Unnamed: 8' in df.columns:
        mask = df['Unnamed: 7'].notnull() | df['Unnamed: 8'].notnull()
        
        def merge_description(row):
            desc = str(row['career_description']).strip()
            u7 = str(row['Unnamed: 7']).strip() if pd.notnull(row['Unnamed: 7']) else ""
            u8 = str(row['Unnamed: 8']).strip() if pd.notnull(row['Unnamed: 8']) else ""
            
            parts = [desc]
            if u7:
                parts.append(u7)
            if u8:
                parts.append(u8)
            return ",".join(parts)
            
        df.loc[mask, 'career_description'] = df[mask].apply(merge_description, axis=1)
        
        # Drop unnamed columns
        df.drop(columns=['Unnamed: 7', 'Unnamed: 8'], inplace=True, errors='ignore')
        
    # Strip string fields
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

def clean_career_transferable(df):
    """Clean the Career-Transferable dataset, filtering duplicate header row."""
    df.columns = [c.strip() for c in df.columns]
    # Filter duplicate header row
    df = df[df['career_id'] != 'career_id'].reset_index(drop=True)
    
    # Strip string fields
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

def clean_skill_dependencies(df):
    """Clean the Skill Dependency dataset, filtering dummy row."""
    df.columns = [c.strip() for c in df.columns]
    # Filter dummy labels row
    df = df[df['source_skill_id'] != 'Column 1'].reset_index(drop=True)
    
    # Strip string fields
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df

def clean_engineering_projects(df):
    """Clean the Engineering Projects dataset."""
    df.columns = [c.strip() for c in df.columns]
    
    # Clean github_url: replace NaN or empty with None
    df['github_url'] = df['github_url'].apply(lambda x: str(x).strip() if pd.notnull(x) and str(x).strip() != "" and str(x).strip().lower() != "nan" else None)
    
    # Strip string fields
    for col in ['project_id', 'project_name', 'domain', 'skills', 'tech_stack', 'description', 'difficulty', 'tags']:
        df[col] = df[col].astype(str).str.strip()
        
    return df

def clean_coursera_courses(df):
    """Clean Coursera dataset, standardizing rating and difficulty."""
    df.columns = [c.strip() for c in df.columns]
    
    # Remove duplicate course names
    df.drop_duplicates(subset=['Course Name'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Strip string fields
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
        
    return df
