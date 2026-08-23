"""
conftest.py for ai-service tests.
Sets up sys.path and creates a module-scoped TestClient that triggers lifespan.
"""
import sys
import os
import pytest

# Add repo root so src/ is importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_AISERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (_REPO_ROOT, _AISERVICE_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _start_service():
    """Start the service once for the whole test session (triggers lifespan)."""
    with TestClient(app) as c:
        pytest.shared_client = c
        yield
