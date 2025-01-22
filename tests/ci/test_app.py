import os

import pytest
from fastapi.testclient import TestClient
from openai import AuthenticationError, OpenAI

from app_fastapi import OPENAI_API_KEY, app

client = TestClient(app)


# Test environment variable setup
def test_openai_api_key_exists():
    """Ensure that the OpenAI API key is set."""
    assert OPENAI_API_KEY is not None, "OpenAI API key is not set."


# Test the `/search` endpoint with valid input
def test_search_endpoint_valid_query():
    """Test the /search endpoint with a valid query."""
    response = client.get("/search", params={"query": "climate change", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)


# Test the `/search` endpoint with missing query
def test_search_endpoint_missing_query():
    """Test the /search endpoint without providing a query."""
    response = client.get("/search", params={})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["query", "query"]
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["type"] == "missing"


# Test the `/search` endpoint with an empty query
def test_search_endpoint_empty_query():
    """Test the /search endpoint with an empty query."""
    response = client.get("/search", params={"query": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Query parameter is missing or empty."


# Test FAISS index and metadata loading
def test_faiss_index_metadata_loading():
    """Ensure that FAISS index and metadata are loaded correctly."""
    from app_fastapi import index, metadata

    assert index is not None, "FAISS index failed to load."
    assert metadata is not None, "Metadata failed to load."
