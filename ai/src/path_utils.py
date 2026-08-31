"""
RouteMaster — Path Resolution Utility
Resolves relative data and model paths against the RouteMaster project root directory,
ensuring consistent file access regardless of current working directory.
"""
from pathlib import Path
from typing import Union

# Project Root is parent directory of src/
# E.g. <PROJECT_ROOT>/src/path_utils.py -> parents[1] is <PROJECT_ROOT>
PROJECT_ROOT = Path(__file__).resolve().parents[1]

def resolve_path(path_input: Union[str, Path]) -> Path:
    """
    Returns an absolute Path object.
    If path_input is relative, it is resolved against PROJECT_ROOT.
    """
    p = Path(path_input)
    if p.is_absolute():
        return p.resolve()
    return (PROJECT_ROOT / p).resolve()
