"""Spec route integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user


def _mock_current_user():
    return {"user_id": "u1", "org_id": "o1", "email": "test@x.com"}


@pytest.fixture
def client():
    """Test client with mocked ES and auth."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    mock_es.get.return_value = None
    mock_es.index.return_value = {"result": "created"}
    mock_es.delete.return_value = {"result": "deleted"}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            app.dependency_overrides[get_current_user] = _mock_current_user
            try:
                yield TestClient(app)
            finally:
                app.dependency_overrides.pop(get_current_user, None)


def test_post_specs_generate_returns_200(client: TestClient):
    """POST /specs/generate returns 200 and spec summary."""
    with patch("app.routers.specs.generate_specs") as mock_gen:
        mock_gen.return_value = {
            "id": "spec-1",
            "title": "Checkout Issues",
            "status": "draft",
            "feedback_count": 10,
            "customer_count": 5,
            "total_arr": 100000,
            "created_at": "2026-02-20T12:00:00Z",
        }
        resp = client.post(
            "/api/v1/specs/generate",
            json={"topic": "checkout form state loss", "product_area": "checkout"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == "spec-1"
    assert data["title"] == "Checkout Issues"
    assert data["feedback_count"] == 10


def test_post_specs_generate_empty_topic_returns_422(client: TestClient):
    """POST /specs/generate with empty topic returns 422."""
    resp = client.post("/api/v1/specs/generate", json={"topic": ""})
    assert resp.status_code == 422


def test_post_specs_generate_value_error_returns_400(client: TestClient):
    """POST /specs/generate with ValueError (e.g. no feedback) returns 400."""
    with patch("app.routers.specs.generate_specs") as mock_gen:
        mock_gen.side_effect = ValueError("Not enough feedback")
        resp = client.post(
            "/api/v1/specs/generate",
            json={"topic": "obscure topic"},
        )
    assert resp.status_code == 400
    assert "Not enough feedback" in resp.json()["detail"]


def test_get_specs_list(client: TestClient):
    """GET /specs returns paginated list."""
    with patch("app.routers.specs.get_specs") as mock_get:
        mock_get.return_value = ([], 0)
        resp = client.get("/api/v1/specs")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["total"] == 0


def test_get_specs_with_filters(client: TestClient):
    """GET /specs with product_area and status filters."""
    with patch("app.routers.specs.get_specs") as mock_get:
        mock_get.return_value = ([], 0)
        resp = client.get("/api/v1/specs?product_area=checkout&status=draft")
    assert resp.status_code == 200
    mock_get.assert_called_once()
    call_filters = mock_get.call_args[0][3]
    assert call_filters.get("product_area") == "checkout"
    assert call_filters.get("status") == "draft"


def test_get_spec_detail(client: TestClient):
    """GET /specs/{id} returns full spec."""
    spec_doc = {
        "id": "spec-1",
        "org_id": "o1",
        "title": "Test",
        "prd": "# PRD",
        "architecture": "# Arch",
        "rules": "# Rules",
        "plan": "# Plan",
    }
    with patch("app.routers.specs.get_spec", return_value=spec_doc):
        resp = client.get("/api/v1/specs/spec-1")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == "spec-1"
    assert "prd" in resp.json()["data"]


def test_get_spec_not_found_returns_404(client: TestClient):
    """GET /specs/{id} returns 404 when not found."""
    with patch("app.routers.specs.get_spec", return_value=None):
        resp = client.get("/api/v1/specs/unknown-id")
    assert resp.status_code == 404


def test_put_spec(client: TestClient):
    """PUT /specs/{id} updates spec."""
    updated = {"id": "s1", "status": "final", "org_id": "o1"}
    with patch("app.routers.specs.update_spec", return_value=updated):
        resp = client.put("/api/v1/specs/s1", json={"status": "final"})
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "final"


def test_put_spec_not_found_returns_404(client: TestClient):
    """PUT /specs/{id} returns 404 when not found."""
    with patch("app.routers.specs.update_spec", return_value=None):
        resp = client.put("/api/v1/specs/unknown", json={"status": "final"})
    assert resp.status_code == 404


def test_delete_spec(client: TestClient):
    """DELETE /specs/{id} returns 200 when deleted."""
    with patch("app.routers.specs.delete_spec", return_value=True):
        resp = client.delete("/api/v1/specs/spec-1")
    assert resp.status_code == 200
    assert resp.json()["data"]["deleted"] is True


def test_delete_spec_not_found_returns_404(client: TestClient):
    """DELETE /specs/{id} returns 404 when not found."""
    with patch("app.routers.specs.delete_spec", return_value=False):
        resp = client.delete("/api/v1/specs/unknown")
    assert resp.status_code == 404


def test_post_specs_regenerate(client: TestClient):
    """POST /specs/{id}/regenerate returns updated spec."""
    updated = {"id": "s1", "prd": "# New PRD", "status": "draft"}
    with patch("app.routers.specs.regenerate_spec", return_value=updated):
        resp = client.post("/api/v1/specs/s1/regenerate")
    assert resp.status_code == 200
    assert resp.json()["data"]["prd"] == "# New PRD"


def test_post_specs_regenerate_not_found_returns_404(client: TestClient):
    """POST /specs/{id}/regenerate returns 404 when not found."""
    with patch("app.routers.specs.regenerate_spec", return_value=None):
        resp = client.post("/api/v1/specs/unknown/regenerate")
    assert resp.status_code == 404


def test_specs_endpoints_reject_without_auth():
    """Spec endpoints reject requests without JWT."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            c = TestClient(app)
            resp = c.get("/api/v1/specs")
    assert resp.status_code == 401
