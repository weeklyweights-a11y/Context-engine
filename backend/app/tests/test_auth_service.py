"""Auth service tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.schemas.auth import LoginRequest, SignupRequest
from app.services.auth_service import login, signup
from app.utils.security import decode_token, verify_password


@pytest.fixture
def mock_es():
    """Mock ES for auth service tests."""
    mock = MagicMock()
    mock.indices.exists.return_value = True
    return mock


def test_signup_creates_user_and_returns_token(mock_es):
    """Signup creates user + org and returns token."""
    with patch("app.services.auth_service.index_document"):
        with patch("app.services.auth_service.search_documents", return_value=[]):
            with patch("app.services.auth_service.get_document", return_value={"name": "Test Org"}):
                result = signup(
                    SignupRequest(
                        email="test@example.com",
                        password="password123",
                        full_name="Test User",
                        org_name="Test Org",
                    )
                )

    assert result.access_token
    assert result.user.email == "test@example.com"
    assert result.user.full_name == "Test User"
    assert result.user.org_name == "Test Org"
    assert result.token_type == "bearer"

    payload = decode_token(result.access_token)
    assert payload["email"] == "test@example.com"
    assert "sub" in payload
    assert "org_id" in payload


def test_signup_duplicate_email_raises(mock_es):
    """Signup with duplicate email raises ValueError."""
    with patch("app.services.auth_service.search_documents") as mock_search:
        mock_search.return_value = [{"email": "existing@example.com"}]

        with pytest.raises(ValueError, match="already exists"):
            signup(
                SignupRequest(
                    email="existing@example.com",
                    password="password123",
                    full_name="Test",
                    org_name="Org",
                )
            )


def test_login_correct_returns_token(mock_es):
    """Login with correct credentials returns token."""
    from app.utils.security import hash_password

    hashed = hash_password("password123")
    user_doc = {
        "user_id": "u1",
        "org_id": "o1",
        "email": "test@example.com",
        "hashed_password": hashed,
        "full_name": "Test",
        "role": "pm",
    }
    with patch("app.services.auth_service.search_documents", return_value=[user_doc]):
        with patch("app.services.auth_service.get_document", return_value={"name": "Test Org"}):
            result = login(LoginRequest(email="test@example.com", password="password123"))

    assert result.access_token
    assert result.user.email == "test@example.com"


def test_login_wrong_password_raises(mock_es):
    """Login with wrong password raises ValueError."""
    from app.utils.security import hash_password

    hashed = hash_password("correctpassword")
    with patch("app.services.auth_service.search_documents") as mock_search:
        mock_search.return_value = [
            {"user_id": "u1", "org_id": "o1", "email": "t@x.com", "hashed_password": hashed},
        ]
        with pytest.raises(ValueError, match="Invalid email or password"):
            login(LoginRequest(email="t@x.com", password="wrongpassword"))


def test_login_nonexistent_email_raises(mock_es):
    """Login with nonexistent email raises ValueError."""
    with patch("app.services.auth_service.search_documents", return_value=[]):
        with pytest.raises(ValueError, match="Invalid email or password"):
            login(LoginRequest(email="nonexistent@x.com", password="any"))


def test_password_is_hashed():
    """Password is hashed, not stored plain."""
    from app.utils.security import hash_password

    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)
