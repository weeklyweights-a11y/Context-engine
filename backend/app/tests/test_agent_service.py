"""Tests for agent_service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.agent_service import AgentService


@pytest.fixture
def mock_settings():
    with patch("app.services.agent_service.get_settings") as m:
        s = MagicMock()
        s.kibana_url = "https://kibana.example.com"
        s.kibana_api_key = "test-key"
        s.agent_id = "context-engine-agent"
        m.return_value = s
        yield s


@pytest.fixture
def agent_service(mock_settings):
    return AgentService()


def test_agent_service_enabled_when_config_set(agent_service):
    assert agent_service._enabled() is True


def test_agent_service_disabled_when_no_url():
    with patch("app.services.agent_service.get_settings") as m:
        m.return_value.kibana_url = ""
        m.return_value.kibana_api_key = "key"
        svc = AgentService()
    assert svc._enabled() is False


def test_agent_id_per_org(agent_service):
    assert agent_service._agent_id("org123") == "ce-org123"


@pytest.mark.asyncio
async def test_chat_proxies_to_kibana(agent_service):
    with patch("app.services.agent_service.get_document", return_value=None):
        with patch("app.services.agent_service.ensure_index_exists"):
            with patch("app.services.agent_service.index_document"):
                with patch("app.services.agent_service.get_product_context") as mock_ctx:
                    mock_ctx.return_value = MagicMock(
                        product_name="Test",
                        areas=[],
                        goals=[],
                        segments=[],
                        competitors=[],
                        teams=[],
                    )
                    with patch("app.services.agent_service.httpx.AsyncClient") as mock_client:
                        mock_resp = MagicMock()
                        mock_resp.status_code = 200
                        mock_resp.json.return_value = {
                            "conversation_id": "kibana-conv-1",
                            "message": {"content": "Here is the response"},
                        }
                        mock_resp.raise_for_status = MagicMock()
                        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                            return_value=mock_resp
                        )
                        with patch.object(
                            agent_service, "register_tools", new_callable=AsyncMock
                        ):
                            with patch.object(
                                agent_service, "register_agent", new_callable=AsyncMock
                            ):
                                result = await agent_service.chat(
                                    org_id="o1",
                                    user_id="u1",
                                    message="What are top issues?",
                                )
    assert result["conversation_id"]
    assert result["response"] == "Here is the response"
    assert "tools_used" in result
    assert "citations" in result


@pytest.mark.asyncio
async def test_chat_raises_when_kibana_not_configured():
    with patch("app.services.agent_service.get_settings") as m:
        m.return_value.kibana_url = ""
        m.return_value.kibana_api_key = ""
        m.return_value.agent_id = "agent"
        svc = AgentService()
    with pytest.raises(ValueError, match="temporarily unavailable"):
        await svc.chat(org_id="o1", user_id="u1", message="hi")


def test_get_conversations_returns_list(agent_service):
    with patch("app.services.agent_service.ensure_index_exists"):
        with patch("app.services.agent_service.search_documents", return_value=[]):
            items = agent_service.get_conversations(org_id="o1", user_id="u1")
    assert items == []


def test_get_conversation_returns_none_when_not_found(agent_service):
    with patch("app.services.agent_service.get_document", return_value=None):
        result = agent_service.get_conversation(org_id="o1", conversation_id="c1")
    assert result is None


def test_get_conversation_returns_none_when_org_mismatch(agent_service):
    with patch("app.services.agent_service.get_document", return_value={"org_id": "o2"}):
        result = agent_service.get_conversation(org_id="o1", conversation_id="c1")
    assert result is None
