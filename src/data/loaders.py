import os
import pandas as pd

def load_raw_dataset(filename, raw_dir="data/raw"):
    """
    Safely load a raw dataset from the raw directory.
    Attempts encoding utf-8, fallback to latin-1.
    """
    filepath = os.path.join(raw_dir, filename)
    if not os.path.exists(filepath):
        # Case insensitive file system search if direct path fails
        files = os.listdir(raw_dir)
        matched = False
        for f in files:
            if f.lower().replace(" ", "").replace("-", "").replace("_", "") == filename.lower().replace(" ", "").replace("-", "").replace("_", ""):
                filepath = os.path.join(raw_dir, f)
                matched = True
                break
        if not matched:
            raise FileNotFoundError(f"Raw dataset file '{filename}' not found in '{raw_dir}'.")
            
    try:
        # Load with UTF-8
        df = pd.read_csv(filepath, encoding='utf-8')
        return df
    except UnicodeDecodeError:
        # Fallback to Latin-1
        df = pd.read_csv(filepath, encoding='latin-1')
        return df
    except Exception as e:
        raise IOError(f"Error loading CSV file '{filepath}': {str(e)}")
