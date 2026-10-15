import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the backend package is importable from a plain `pytest` invocation.
PYTHON_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
if PYTHON_ROOT not in sys.path:
    sys.path.insert(0, PYTHON_ROOT)

from app import main as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)
