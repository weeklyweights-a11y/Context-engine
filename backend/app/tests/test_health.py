"""Health endpoint tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_connected():
    """Client with working ES mock."""
    mock_es = MagicMock()
    mock_es.info.return_value = {
        "cluster_name": "test-cluster",
        "version": {"number": "8.12.0"},
    }
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            yield TestClient(app)


@pytest.fixture
def client_degraded():
    """Client where ES raises on info()."""
    mock_es = MagicMock()
    mock_es.info.side_effect = Exception("Connection refused")
    mock_es.indices.exists.return_value = True
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            yield TestClient(app)


def test_health_returns_200_with_es_info(client_connected: TestClient):
    """GET /health returns 200 with ES cluster info."""
    resp = client_connected.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "elasticsearch" in data
    assert data["elasticsearch"]["status"] == "connected"
    assert data["elasticsearch"]["cluster_name"] == "test-cluster"
    assert "version" in data


def test_health_returns_degraded_when_es_unreachable(client_degraded: TestClient):
    """GET /health returns degraded when ES unreachable."""
    resp = client_degraded.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["elasticsearch"]["status"] == "disconnected"
    assert "error" in data["elasticsearch"]
