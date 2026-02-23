"""Feedback route integration tests."""

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
            with patch("app.services.elser_service.ensure_elser_deployed"):
                from app.main import app
                app.dependency_overrides[get_current_user] = _mock_current_user
                try:
                    yield TestClient(app)
                finally:
                    app.dependency_overrides.pop(get_current_user, None)


def test_post_feedback_manual_valid(client: TestClient):
    """POST /feedback/manual with valid data returns 200."""
    with patch("app.routers.feedback.create_feedback_item") as mock_create:
        mock_create.return_value = {"id": "f1", "text": "Great!", "sentiment": "positive"}
        resp = client.post(
            "/api/v1/feedback/manual",
            json={"text": "Great product!"},
        )
    assert resp.status_code == 200
    assert resp.json()["data"]["text"] == "Great!"


def test_post_feedback_manual_empty_text_returns_422(client: TestClient):
    """POST /feedback/manual with empty text returns 422 (validation error)."""
    resp = client.post(
        "/api/v1/feedback/manual",
        json={"text": ""},
    )
    assert resp.status_code == 422


def test_get_feedback_list(client: TestClient):
    """GET /feedback returns paginated list."""
    with patch("app.routers.feedback.get_feedback_items") as mock_get:
        mock_get.return_value = ([], 0)
        resp = client.get("/api/v1/feedback")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data


def test_get_feedback_count(client: TestClient):
    """GET /feedback/count returns count."""
    with patch("app.routers.feedback.get_feedback_count", return_value=42):
        resp = client.get("/api/v1/feedback/count")
    assert resp.status_code == 200
    assert resp.json()["data"]["count"] == 42


def test_get_feedback_item_not_found(client: TestClient):
    """GET /feedback/{id} returns 404 when not found."""
    with patch("app.routers.feedback.get_feedback_item", return_value=None):
        resp = client.get("/api/v1/feedback/unknown-id")
    assert resp.status_code == 404


def test_upload_csv_returns_mapping(client: TestClient, tmp_path):
    """POST /feedback/upload-csv returns upload_id and suggested mapping."""
    csv_content = b"feedback,source\nGreat,support\n"
    csv_path = tmp_path / "test.csv"
    csv_path.write_bytes(csv_content)

    def fake_save(content: bytes, _filename: str) -> str:
        csv_path.write_bytes(content)
        return str(csv_path)

    with patch("app.routers.feedback.save_uploaded_file", side_effect=fake_save):
        with patch("app.routers.feedback.create_upload", return_value="up-1"):
            resp = client.post(
                "/api/v1/feedback/upload-csv",
                files={"file": ("test.csv", BytesIO(csv_content), "text/csv")},
            )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "upload_id" in data
    assert "columns" in data
    assert "suggested_mapping" in data


def test_upload_csv_non_csv_returns_400(client: TestClient):
    """POST /feedback/upload-csv with non-CSV returns 400."""
    resp = client.post(
        "/api/v1/feedback/upload-csv",
        files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400


def test_feedback_endpoints_reject_without_jwt():
    """Feedback endpoints reject requests without JWT."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.elser_service.ensure_elser_deployed"):
            from app.main import app
            tc = TestClient(app)
            endpoints = [
                ("get", "/api/v1/feedback", {}),
                ("get", "/api/v1/feedback/count", {}),
                ("post", "/api/v1/feedback/manual", {"json": {"text": "x"}}),
            ]
            for method, path, kwargs in endpoints:
                fn = getattr(tc, method)
                resp = fn(path, **kwargs)
                assert resp.status_code == 401
