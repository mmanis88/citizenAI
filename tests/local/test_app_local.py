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


def test_openai_api_key_is_valid():
    """Check if the OpenAI API key is valid."""
    try:
        # Instantiate the OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Make a simple request to validate the API key
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "This is a test."}],
            max_tokens=5,
        )

        # Validate the response
        assert (
            response.choices[0].message.content.strip() != ""
        ), "Response is empty, API key might be invalid."
    except AuthenticationError:
        pytest.fail(
            "OpenAI API key is invalid. Ensure a valid API key is set correctly."
        )
    except Exception as e:
        pytest.fail(f"Unexpected error while validating OpenAI API key: {e}")


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
