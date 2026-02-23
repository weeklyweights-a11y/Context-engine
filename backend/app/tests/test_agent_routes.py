"""Tests for agent routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user


def _mock_current_user():
    return {"user_id": "u1", "org_id": "o1", "email": "test@x.com"}


@pytest.fixture
def client():
    """Test client with mocked ES, auth, and agent service."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    mock_es.get.return_value = {"_source": {}}
    mock_es.index.return_value = {"result": "created"}

    async def mock_chat(org_id, user_id, message, conversation_id=None, context=None):
        return {
            "conversation_id": "conv-1",
            "response": "Hello from agent",
            "tools_used": [],
            "citations": [],
        }

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            with patch("app.services.elser_service.ensure_elser_deployed"):
                with patch(
                    "app.routers.agent.get_agent_service"
                ) as mock_get_svc:
                    mock_svc = MagicMock()
                    mock_svc.chat = AsyncMock(side_effect=mock_chat)
                    mock_svc.get_conversations.return_value = []
                    mock_svc.get_conversation.return_value = None
                    mock_get_svc.return_value = mock_svc
                    from app.main import app

                    app.dependency_overrides[get_current_user] = _mock_current_user
                    try:
                        yield TestClient(app)
                    finally:
                        app.dependency_overrides.pop(get_current_user, None)




def test_post_chat_returns_200(client: TestClient):
    """POST /agent/chat returns 200 with response."""
    resp = client.post(
        "/api/v1/agent/chat",
        json={"message": "What are top issues?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    assert "response" in data
    assert data["response"] == "Hello from agent"


def test_post_chat_with_conversation_id_continues(client: TestClient):
    """POST /agent/chat with conversation_id continues conversation."""
    with patch("app.services.agent_service.get_document") as mock_get:
        mock_get.return_value = {"org_id": "o1", "kibana_conversation_id": "kibana-old"}
        resp = client.post(
            "/api/v1/agent/chat",
            json={"message": "Follow up", "conversation_id": "our-conv-1"},
        )
    assert resp.status_code == 200


def test_get_conversations_returns_200(client: TestClient):
    """GET /agent/conversations returns 200."""
    with patch(
        "app.routers.agent.get_agent_service"
    ) as mock_get:
        mock_svc = MagicMock()
        mock_svc.get_conversations.return_value = []
        mock_get.return_value = mock_svc
        resp = client.get("/api/v1/agent/conversations")
    assert resp.status_code == 200
    assert "data" in resp.json()


def test_get_conversation_returns_200(client: TestClient):
    """GET /agent/conversations/{id} returns 200 when found."""
    with patch("app.routers.agent.get_agent_service") as mock_get:
        mock_svc = MagicMock()
        mock_svc.get_conversation.return_value = {"id": "c1", "title": "Test"}
        mock_get.return_value = mock_svc
        resp = client.get("/api/v1/agent/conversations/c1")
    assert resp.status_code == 200
    assert resp.json()["id"] == "c1"


def test_get_conversation_returns_404_when_not_found(client: TestClient):
    """GET /agent/conversations/{id} returns 404 when not found."""
    with patch("app.routers.agent.get_agent_service") as mock_get:
        mock_svc = MagicMock()
        mock_svc.get_conversation.return_value = None
        mock_get.return_value = mock_svc
        resp = client.get("/api/v1/agent/conversations/nonexistent")
    assert resp.status_code == 404


def test_post_chat_without_auth_returns_401():
    """POST /agent/chat without auth returns 401."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"hits": []}}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            with patch("app.services.elser_service.ensure_elser_deployed"):
                from app.main import app

                if get_current_user in app.dependency_overrides:
                    app.dependency_overrides.pop(get_current_user)
                client = TestClient(app)
                resp = client.post("/api/v1/agent/chat", json={"message": "hi"})
    assert resp.status_code == 401
