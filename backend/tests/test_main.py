"""Tests for main.py - FastAPI app root endpoint."""


def test_root_endpoint(client):
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to GLaDOS - FOD Detection API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_docs_endpoint_accessible(client):
    """Test that the OpenAPI docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_accessible(client):
    """Test that the OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "GLaDOS - FOD Detection API"
