"""Auth route integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client with mocked ES."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"hits": []}}
    mock_es.get.return_value = {"_source": {"name": "Test Org"}}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            with patch("app.services.auth_service.index_document"):
                with patch("app.services.auth_service.search_documents") as mock_search:
                    mock_search.return_value = []
                    with patch("app.services.auth_service.get_document", return_value={"name": "Test Org"}):
                        from app.main import app
                        yield TestClient(app)


def test_post_signup_valid_returns_201(client: TestClient):
    """POST /auth/signup with valid data returns 201."""
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User",
            "org_name": "New Org",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "data" in data
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "new@example.com"


def test_post_signup_short_password_returns_422(client: TestClient):
    """POST /auth/signup with short password returns 422."""
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "t@x.com",
            "password": "short",
            "full_name": "T",
            "org_name": "O",
        },
    )
    assert resp.status_code == 422


def test_post_signup_bad_email_returns_422(client: TestClient):
    """POST /auth/signup with invalid email returns 422."""
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "T",
            "org_name": "O",
        },
    )
    assert resp.status_code == 422


def test_post_login_valid_returns_200(client: TestClient):
    """POST /auth/login with valid creds returns 200."""
    from app.utils.security import hash_password

    hashed = hash_password("secret123")
    with patch("app.services.auth_service.search_documents") as mock_search:
        mock_search.return_value = [
            {
                "user_id": "u1",
                "org_id": "o1",
                "email": "login@x.com",
                "hashed_password": hashed,
                "full_name": "L",
                "role": "pm",
            }
        ]
        with patch("app.services.auth_service.get_document", return_value={"name": "O"}):
            resp = client.post(
                "/api/v1/auth/login",
                json={"email": "login@x.com", "password": "secret123"},
            )
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


def test_post_login_wrong_password_returns_401(client: TestClient):
    """POST /auth/login with wrong password returns 401."""
    from app.utils.security import hash_password

    hashed = hash_password("correct")
    with patch("app.services.auth_service.search_documents", return_value=[{"hashed_password": hashed}]):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "x@x.com", "password": "wrong"},
        )
    assert resp.status_code == 401


def test_get_me_with_token_returns_200(client: TestClient):
    """GET /auth/me with valid token returns 200."""
    from app.utils.security import create_access_token

    token = create_access_token(sub="u1", org_id="o1", email="me@x.com")
    with patch("app.routers.auth.get_user_by_id") as mock_get:
        mock_get.return_value = {
            "user_id": "u1",
            "org_id": "o1",
            "email": "me@x.com",
            "full_name": "Me",
            "role": "pm",
        }
        with patch("app.routers.auth.get_document", return_value={"name": "Org"}):
            resp = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert resp.status_code == 200


def test_get_me_without_token_returns_401(client: TestClient):
    """GET /auth/me without token returns 401."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
