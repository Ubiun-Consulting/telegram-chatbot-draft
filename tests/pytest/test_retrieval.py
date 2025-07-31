import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "retrieval-service"

def test_search_endpoint():
    """Test the search endpoint"""
    search_data = {
        "query": "resilience building",
        "k": 3
    }
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    assert "documents" in response.json()

def test_embed_endpoint():
    """Test the embed endpoint"""
    embed_data = {
        "texts": ["This is a test document.", "Another test document."]
    }
    response = client.post("/embed", json=embed_data)
    assert response.status_code == 200
    assert "embeddings" in response.json()

def test_add_documents():
    """Test adding documents to the store"""
    add_data = {
        "texts": ["Test document 1", "Test document 2"],
        "metadata": [
            {"source": "test1.txt"},
            {"source": "test2.txt"}
        ]
    }
    response = client.post("/add", json=add_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_search_with_invalid_query():
    """Test search with invalid query"""
    search_data = {
        "query": "",
        "k": 5
    }
    response = client.post("/search", json=search_data)
    # Should handle empty query gracefully
    assert response.status_code == 200 