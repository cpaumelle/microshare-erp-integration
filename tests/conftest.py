# pytest configuration for Microshare ERP Integration tests
import pytest
import asyncio
from fastapi.testclient import TestClient
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def client():
    """FastAPI test client"""
    from services.integration_api.main import app
    return TestClient(app)

@pytest.fixture 
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    test_vars = {
        "MICROSHARE_AUTH_URL": "https://dauth.microshare.io",
        "MICROSHARE_API_URL": "https://dapi.microshare.io", 
        "MICROSHARE_USERNAME": "test_user",
        "MICROSHARE_PASSWORD": "test_pass",
        "MICROSHARE_API_KEY": "test_key",
        "CACHE_TTL": "60"
    }
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

