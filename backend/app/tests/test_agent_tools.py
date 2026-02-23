"""Tests for agent tool registration and tool-related behavior."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.agent_service import (
    TOOL_IDS,
    AgentService,
    _tool_id,
    _extract_response_text,
)


def test_tool_ids_count():
    assert len(TOOL_IDS) == 7
    assert "search_feedback" in TOOL_IDS
    assert "trend_analysis" in TOOL_IDS
    assert "top_issues" in TOOL_IDS
    assert "find_similar" in TOOL_IDS
    assert "customer_lookup" in TOOL_IDS
    assert "compare_segments" in TOOL_IDS
    assert "generate_spec_prep" in TOOL_IDS


def test_tool_id_format_short_org():
    assert _tool_id("abc123", "search_feedback") == "ce_abc123_search_feedback"


def test_tool_id_format_long_org_truncated():
    long_org = "a" * 20
    tid = _tool_id(long_org, "search_feedback")
    assert tid.startswith("ce_")
    assert "search_feedback" in tid
    assert len(tid) <= 64


def test_extract_response_from_message_content():
    data = {"message": {"content": "The answer is 42"}}
    assert _extract_response_text(data) == "The answer is 42"


def test_extract_response_from_response_string():
    data = {"response": "Direct response text"}
    assert _extract_response_text(data) == "Direct response text"


def test_extract_response_from_steps():
    data = {
        "steps": [
            {"type": "tool", "content": "tool output"},
            {"type": "message", "content": "Final answer from assistant"},
        ],
    }
    assert _extract_response_text(data) == "Final answer from assistant"


def test_extract_response_fallback_when_empty():
    data = {"conversation_id": "x", "status": "complete", "response": {}}
    result = _extract_response_text(data)
    assert "unexpected" in result.lower() or "try again" in result.lower()


@pytest.fixture
def mock_settings():
    with patch("app.services.agent_service.get_settings") as m:
        s = MagicMock()
        s.kibana_url = "https://kibana.example.com"
        s.kibana_api_key = "test-key"
        m.return_value = s
        yield s


def test_chat_includes_tools_used_in_response(mock_settings):
    """Chat response includes tools_used and citations from Kibana."""
    svc = AgentService()
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
                            "message": {"content": "Found 5 feedback items"},
                            "tools_used": [{"tool_id": "ce_org1_search_feedback"}],
                            "citations": [{"id": "fb1", "text": "checkout is broken"}],
                        }
                        mock_resp.raise_for_status = MagicMock()
                        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                            return_value=mock_resp
                        )
                        with patch.object(svc, "register_tools", new_callable=AsyncMock):
                            with patch.object(svc, "register_agent", new_callable=AsyncMock):
                                import asyncio
                                result = asyncio.get_event_loop().run_until_complete(
                                    svc.chat(org_id="org1", user_id="u1", message="Show checkout feedback")
                                )
    assert result["response"] == "Found 5 feedback items"
    assert result["tools_used"] == [{"tool_id": "ce_org1_search_feedback"}]
    assert result["citations"] == [{"id": "fb1", "text": "checkout is broken"}]
