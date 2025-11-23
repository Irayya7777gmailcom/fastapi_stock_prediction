"""
API Endpoint Tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_get_all_stocks():
    """Test getting all stocks list"""
    response = client.get("/api/v1/stocks/")
    assert response.status_code == 200
    data = response.json()
    assert "all_stocks" in data
    assert isinstance(data["all_stocks"], list)


def test_get_stock_summary_valid():
    """Test getting summary for a valid stock"""
    response = client.get("/api/v1/stocks/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert "historical" in data
    assert "live" in data
    assert isinstance(data["historical"], list)
    assert isinstance(data["live"], list)


def test_get_stock_summary_case_insensitive():
    """Test stock lookup is case insensitive"""
    response1 = client.get("/api/v1/stocks/RELIANCE")
    response2 = client.get("/api/v1/stocks/reliance")
    assert response1.status_code == response2.status_code


def test_get_favorites():
    """Test getting favorite stocks"""
    response = client.get("/api/v1/stocks/favorites/list")
    assert response.status_code == 200
    data = response.json()
    assert "favorites" in data
    assert isinstance(data["favorites"], list)


def test_api_docs_available():
    """Test API documentation is accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema is available"""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
