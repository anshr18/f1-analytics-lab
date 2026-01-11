"""
Pytest Configuration and Fixtures

Shared fixtures for all tests.
"""

import pytest
from fastapi.testclient import TestClient

from f1hub.main import app


@pytest.fixture
def client():
    """
    FastAPI test client.

    Returns:
        TestClient: FastAPI test client
    """
    return TestClient(app)


@pytest.fixture
def test_settings():
    """
    Test settings override.

    Returns:
        dict: Test configuration
    """
    return {
        "ENVIRONMENT": "testing",
        "DEBUG": True,
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_f1hub",
    }


# Database fixtures will be added in Week 2
# @pytest.fixture
# def db():
#     """Test database session"""
#     pass
