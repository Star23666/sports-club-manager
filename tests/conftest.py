import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure project `python` package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import main as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)
