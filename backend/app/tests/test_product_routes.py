"""Product route integration tests."""

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
    mock_es.search.return_value = {"hits": {"hits": []}}
    mock_es.get.side_effect = Exception("not found")
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


def test_put_wizard_basics_valid_returns_200(client: TestClient):
    """PUT /product/wizard/basics with valid data returns 200."""
    with patch("app.routers.product.save_wizard_section") as mock_save:
        mock_save.return_value = {"section": "basics", "data": {"product_name": "Acme"}}
        resp = client.put(
            "/api/v1/product/wizard/basics",
            json={"product_name": "Acme", "description": "B2B"},
        )
    assert resp.status_code == 200
    assert "data" in resp.json()


def test_put_wizard_basics_missing_product_name_returns_422(client: TestClient):
    """PUT /product/wizard/basics with missing product_name returns 422."""
    resp = client.put(
        "/api/v1/product/wizard/basics",
        json={"description": "B2B"},
    )
    assert resp.status_code == 422


def test_put_wizard_areas_empty_list_returns_200(client: TestClient):
    """PUT /product/wizard/areas with empty list is valid."""
    with patch("app.routers.product.save_wizard_section") as mock_save:
        mock_save.return_value = {"section": "areas", "data": {"areas": []}}
        resp = client.put(
            "/api/v1/product/wizard/areas",
            json={"areas": []},
        )
    assert resp.status_code == 200


def test_get_wizard_returns_all_sections(client: TestClient):
    """GET /product/wizard returns all saved sections."""
    with patch("app.routers.product.get_all_wizard_sections") as mock_get:
        mock_get.return_value = {
            "basics": {"data": {"product_name": "Acme"}},
            "areas": {"data": {"areas": []}},
        }
        resp = client.get("/api/v1/product/wizard")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "basics" in data["data"]
    assert "completed_sections" in data


def test_get_wizard_section_returns_section(client: TestClient):
    """GET /product/wizard/{section} returns that section."""
    with patch("app.routers.product.get_wizard_section") as mock_get:
        mock_get.return_value = {"section": "basics", "data": {"product_name": "Acme"}}
        resp = client.get("/api/v1/product/wizard/basics")
    assert resp.status_code == 200
    assert resp.json()["data"]["data"]["product_name"] == "Acme"


def test_get_wizard_section_nonexistent_returns_404(client: TestClient):
    """GET /product/wizard/{section} for non-existent section returns 404."""
    with patch("app.routers.product.get_wizard_section", return_value=None):
        resp = client.get("/api/v1/product/wizard/basics")
    assert resp.status_code == 404


def test_delete_wizard_section_returns_200(client: TestClient):
    """DELETE /product/wizard/{section} returns 200."""
    with patch("app.routers.product.delete_wizard_section", return_value=True):
        resp = client.delete("/api/v1/product/wizard/basics")
    assert resp.status_code == 200


def test_get_context_returns_flattened(client: TestClient):
    """GET /product/context returns flattened data."""
    from app.schemas.product import ProductContextResponse
    with patch("app.routers.product.get_product_context") as mock_get:
        mock_get.return_value = ProductContextResponse(
            product_name="Acme",
            areas=[],
            goals=[],
        )
        resp = client.get("/api/v1/product/context")
    assert resp.status_code == 200
    assert resp.json()["data"]["product_name"] == "Acme"


def test_get_onboarding_status_new_user_completed_false(client: TestClient):
    """GET /product/onboarding-status for new user returns completed: false."""
    with patch("app.routers.product.get_onboarding_status") as mock_get:
        mock_get.return_value = {"completed": False, "completed_sections": [], "total_sections": 8}
        resp = client.get("/api/v1/product/onboarding-status")
    assert resp.status_code == 200
    assert resp.json()["data"]["completed"] is False


def test_post_onboarding_complete_returns_completed_true(client: TestClient):
    """POST /product/onboarding-complete returns completed: true."""
    with patch("app.routers.product.mark_onboarding_complete"):
        resp = client.post("/api/v1/product/onboarding-complete")
    assert resp.status_code == 200
    assert resp.json()["data"]["completed"] is True


def test_get_onboarding_status_after_complete_returns_true(client: TestClient):
    """GET /product/onboarding-status after complete returns completed: true."""
    with patch("app.routers.product.get_onboarding_status") as mock_get:
        mock_get.return_value = {"completed": True, "completed_sections": ["basics"], "total_sections": 8}
        resp = client.get("/api/v1/product/onboarding-status")
    assert resp.status_code == 200
    assert resp.json()["data"]["completed"] is True


def test_product_endpoints_reject_without_jwt():
    """All product endpoints reject requests without JWT (401 from HTTPBearer)."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"hits": []}}
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            test_client = TestClient(app)
            endpoints = [
                ("put", "/api/v1/product/wizard/basics", {"json": {"product_name": "Acme"}}),
                ("get", "/api/v1/product/wizard", {}),
                ("get", "/api/v1/product/wizard/basics", {}),
                ("delete", "/api/v1/product/wizard/basics", {}),
                ("get", "/api/v1/product/context", {}),
                ("get", "/api/v1/product/onboarding-status", {}),
                ("post", "/api/v1/product/onboarding-complete", {}),
            ]
            for method, path, kwargs in endpoints:
                fn = getattr(test_client, method)
                resp = fn(path, **kwargs)
                assert resp.status_code == 401, f"{method} {path} should reject without token"
