"""Customer route integration tests."""

from io import BytesIO
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
    mock_es.count.return_value = {"count": 0}
    mock_es.get.side_effect = Exception("not found")
    mock_es.index.return_value = {"result": "created"}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            from app.main import app
            app.dependency_overrides[get_current_user] = _mock_current_user
            try:
                yield TestClient(app)
            finally:
                app.dependency_overrides.pop(get_current_user, None)


def test_post_customer_manual_valid(client: TestClient):
    """POST /customers/manual with valid data returns 200."""
    with patch("app.routers.customers.create_customer") as mock_create:
        mock_create.return_value = {"id": "c1", "company_name": "Acme"}
        resp = client.post(
            "/api/v1/customers/manual",
            json={"company_name": "Acme", "segment": "Enterprise"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["company_name"] == "Acme"


def test_get_customers_list(client: TestClient):
    """GET /customers returns paginated list."""
    with patch("app.routers.customers.get_customers") as mock_get:
        mock_get.return_value = ([], 0)
        resp = client.get("/api/v1/customers")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data


def test_get_customers_count(client: TestClient):
    """GET /customers/count returns count."""
    with patch("app.routers.customers.get_customer_count", return_value=10):
        resp = client.get("/api/v1/customers/count")
    assert resp.status_code == 200
    assert resp.json()["data"]["count"] == 10


def test_get_customer_item_not_found(client: TestClient):
    """GET /customers/{id} returns 404 when not found."""
    with patch("app.routers.customers.get_customer", return_value=None):
        resp = client.get("/api/v1/customers/unknown-id")
    assert resp.status_code == 404


def test_upload_customers_csv(client: TestClient, tmp_path):
    """POST /customers/upload-csv returns upload_id and suggested mapping."""
    csv_content = b"company_name,segment\nAcme,Enterprise\n"
    csv_path = tmp_path / "customers.csv"
    csv_path.write_bytes(csv_content)

    def fake_save(content: bytes, _filename: str) -> str:
        csv_path.write_bytes(content)
        return str(csv_path)

    with patch("app.routers.customers.save_uploaded_file", side_effect=fake_save):
        with patch("app.routers.customers.create_upload", return_value="up-1"):
            resp = client.post(
                "/api/v1/customers/upload-csv",
                files={"file": ("customers.csv", BytesIO(csv_content), "text/csv")},
            )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "upload_id" in data
    assert "columns" in data


def test_customer_endpoints_reject_without_jwt():
    """Customer endpoints reject requests without JWT."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    with patch("app.es_client.get_es_client", return_value=mock_es):
        from app.main import app
        tc = TestClient(app)
        endpoints = [
            ("get", "/api/v1/customers", {}),
            ("get", "/api/v1/customers/count", {}),
            ("post", "/api/v1/customers/manual", {"json": {"company_name": "Acme"}}),
        ]
        for method, path, kwargs in endpoints:
            fn = getattr(tc, method)
            resp = fn(path, **kwargs)
            assert resp.status_code == 401, f"{method} {path} should reject without token"
