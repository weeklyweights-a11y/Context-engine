"""Pytest fixtures for backend tests."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set minimal env before importing app (needed for ES client init)
os.environ.setdefault("ELASTICSEARCH_CLOUD_ID", "test:base64")
os.environ.setdefault("ELASTICSEARCH_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-min-32-chars-long")


@pytest.fixture
def mock_es_client():
    """Mock Elasticsearch client for tests that don't need real ES."""
    mock = MagicMock()
    mock.info.return_value = {
        "cluster_name": "test-cluster",
        "version": {"number": "8.12.0"},
    }
    mock.indices.exists.return_value = True
    mock.index.return_value = {"result": "created"}
    mock.get.return_value = {"_source": {}}
    mock.search.return_value = {"hits": {"hits": []}}
    mock.delete.return_value = {"result": "deleted"}
    return mock


@pytest.fixture
def client(mock_es_client):
    """Test client with mocked ES."""
    with patch("app.es_client.get_es_client", return_value=mock_es_client):
        with patch("app.services.es_service.get_es_client", return_value=mock_es_client):
            from app.main import app
            yield TestClient(app)
