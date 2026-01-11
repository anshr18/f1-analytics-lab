"""
Tests for main application endpoints.
"""

from fastapi import status


def test_health_check(client):
    """Test health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "environment" in data


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/docs"


def test_swagger_ui_enabled(client):
    """Test that Swagger UI is accessible."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK


def test_redoc_enabled(client):
    """Test that ReDoc is accessible."""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK
