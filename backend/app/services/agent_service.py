"""Agent service — proxies to Kibana Agent Builder converse API."""

import json
import uuid
from datetime import datetime
from typing import Any

import httpx

from app.config import get_settings
from app.models.conversation import (
    CONVERSATIONS_MAPPING,
    conversations_index,
)
from app.services.es_service import (
    ensure_index_exists,
    get_document,
    index_document,
    search_documents,
)
from app.services.product_service import get_product_context
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _extract_response_text(data: dict[str, Any]) -> str:
    """
    Extract assistant response text from Kibana converse API response.
    Handles various response structures across ES/Kibana versions.
    Kibana 8.x returns: conversation_id, round_id, status, steps, response, ...
    """
    # Top-level string fields
    for key in ("output", "response", "answer", "content", "text"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val

    # response (Kibana 8.x: can be string, dict, or array of blocks)
    resp_val = data.get("response")
    if isinstance(resp_val, str) and resp_val.strip():
        return resp_val
    if isinstance(resp_val, dict):
        for key in ("content", "text", "message"):
            val = resp_val.get(key)
            if isinstance(val, str) and val.strip():
                return val
        content = resp_val.get("content")
        if isinstance(content, list):
            parts = [b.get("text") or b.get("content") for b in content if isinstance(b, dict)]
            text = "\n".join(p for p in parts if isinstance(p, str) and p.strip())
            if text:
                return text
    if isinstance(resp_val, list):
        parts = []
        for b in resp_val:
            if isinstance(b, dict):
                t = b.get("text") or b.get("content") or b.get("message")
                if isinstance(t, str) and t.strip():
                    parts.append(t)
        if parts:
            return "\n".join(parts)

    # steps array — last message step often has the final reply (Kibana 8.x)
    steps = data.get("steps") or []
    if isinstance(steps, list):

        def _text_from(val: Any) -> str | None:
            if isinstance(val, str) and val.strip():
                return val
            if isinstance(val, dict):
                for k in ("content", "text", "message"):
                    t = val.get(k)
                    if isinstance(t, str) and t.strip():
                        return t
                arr = val.get("content")
                if isinstance(arr, list):
                    parts = [b.get("text") or b.get("content") for b in arr if isinstance(b, dict)]
                    out = "\n".join(p for p in parts if isinstance(p, str) and p.strip())
                    if out:
                        return out
            if isinstance(val, list):
                parts = [b.get("text") or b.get("content") for b in val if isinstance(b, dict)]
                out = "\n".join(p for p in parts if isinstance(p, str) and p.strip())
                if out:
                    return out
            return None

        for step in reversed(steps):
            if not isinstance(step, dict):
                continue
            for key in ("content", "message", "output", "text", "response"):
                t = _text_from(step.get(key))
                if t:
                    return t

    # message or output object
    msg_obj = data.get("message") or data.get("output") or {}
    if isinstance(msg_obj, str) and msg_obj.strip():
        return msg_obj
    if isinstance(msg_obj, dict):
        for key in ("content", "text", "message"):
            val = msg_obj.get(key)
            if isinstance(val, str) and val.strip():
                return val
        # content can be array of content blocks: [{ type: "text", text: "..." }]
        content = msg_obj.get("content")
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    t = block.get("text") or block.get("content") or block.get("message")
                    if isinstance(t, str) and t.strip():
                        parts.append(t)
            if parts:
                return "\n".join(parts)

    # conversation.messages — last assistant message
    conv = data.get("conversation") or {}
    messages = conv.get("messages") or conv.get("message") or data.get("messages") or []
    if isinstance(messages, list):
        for m in reversed(messages):
            if isinstance(m, dict) and m.get("role") in ("assistant", "AI"):
                content = m.get("content") or m.get("message") or m.get("text")
                if isinstance(content, str) and content.strip():
                    return content
                if isinstance(content, list):
                    parts = [b.get("text") or b.get("content") for b in content if isinstance(b, dict)]
                    text = "\n".join(p for p in parts if isinstance(p, str) and p.strip())
                    if text:
                        return text

    # Log structure when extraction fails (debug Kibana schema)
    _steps = data.get("steps") or []
    try:
        steps_preview = []
        for i, s in enumerate((_steps[:3] if isinstance(_steps, list) else [])):
            if isinstance(s, dict):
                steps_preview.append({"i": i, "keys": list(s.keys()), "content_preview": str(s.get("content"))[:300]})
        debug = {
            "keys": list(data.keys()),
            "response_type": type(data.get("response")).__name__,
            "response_preview": str(data.get("response"))[:800] if data.get("response") else None,
            "steps_count": len(_steps) if isinstance(_steps, list) else 0,
            "steps_preview": steps_preview,
        }
        logger.warning("Could not extract response text from Kibana. Debug: %s", json.dumps(debug, default=str))
    except Exception as e:
        logger.warning("Could not extract response text. Keys: %s. Log error: %s", list(data.keys()), e)
    return "The agent responded but the format was unexpected. Please try again."
TOOL_IDS = [
    "search_feedback",
    "trend_analysis",
    "top_issues",
    "find_similar",
    "customer_lookup",
    "compare_segments",
    "generate_spec_prep",
]


def _tool_id(org_id: str, base: str) -> str:
    """Return org-scoped tool ID (max 64 chars)."""
    short_org = org_id[:12] if len(org_id) > 12 else org_id
    return f"ce_{short_org}_{base}"


def _build_instructions(product_context: Any) -> str:
    """Build agent instructions from product context."""
    parts = [
        "You are the Context Engine Agent — an AI assistant for Product Managers.",
        "",
        "You help PMs understand their customer feedback, identify trends, prioritize issues, and generate engineering specs.",
        "",
        "## Product Context",
        "",
    ]
    if product_context.product_name:
        parts.append(f"Product: {product_context.product_name}")
    if product_context.description:
        parts.append(f"Description: {product_context.description}")
    if product_context.industry:
        parts.append(f"Industry: {product_context.industry}")
    if product_context.stage:
        parts.append(f"Stage: {product_context.stage}")
    if product_context.areas:
        areas_list = "\n".join(
            f"- {a.get('name', a) if isinstance(a, dict) else a}"
            for a in product_context.areas
        )
        parts.extend(["", "## Product Areas", "", areas_list])
    if product_context.goals:
        goals_list = "\n".join(
            f"- {g.get('title', g) if isinstance(g, dict) else g}"
            for g in product_context.goals
        )
        parts.extend(["", "## Business Goals", "", goals_list])
    if product_context.segments:
        seg_list = "\n".join(
            f"- {s.get('name', s) if isinstance(s, dict) else s}"
            for s in product_context.segments
        )
        parts.extend(["", "## Customer Segments", "", seg_list])
    if product_context.competitors:
        comp_list = "\n".join(
            f"- {c.get('name', c) if isinstance(c, dict) else c}"
            for c in product_context.competitors
        )
        parts.extend(["", "## Competitors", "", comp_list])
    if product_context.teams:
        team_list = "\n".join(
            f"- {t.get('name', t) if isinstance(t, dict) else t}"
            for t in product_context.teams
        )
        parts.extend(["", "## Teams", "", team_list])
    parts.extend([
        "",
        "## Rules",
        "- Always cite specific numbers (feedback count, sentiment scores, ARR)",
        "- When mentioning customers, include segment and ARR",
        "- Connect issues to business goals and product areas",
        "- When asked to generate specs, gather all relevant data first",
    ])
    return "\n".join(parts)


def _esql_tool_config(org_id: str, tool_base: str) -> dict[str, Any]:
    """Return ES|QL tool configuration for a given org and tool."""
    fb_idx = f"{org_id}-feedback"
    cust_idx = f"{org_id}-customers"
    configs: dict[str, dict[str, Any]] = {
        "search_feedback": {
            "description": "Search customer feedback by topic, product area, source, sentiment, segment, or date range.",
            "query": f"FROM {fb_idx} | WHERE MATCH(text, ?search_query) | STATS count = COUNT(*), avg_sentiment = AVG(sentiment_score) BY product_area | SORT count DESC | LIMIT 10",
            "params": {"search_query": {"type": "string", "description": "What to search for in feedback text"}},
        },
        "trend_analysis": {
            "description": "Analyze feedback trends over time. Compare current period volume and sentiment.",
            "query": f"FROM {fb_idx} | WHERE created_at >= NOW() - ?period | STATS feedback_count = COUNT(*), avg_sentiment = AVG(sentiment_score), negative_count = COUNT_IF(sentiment == \"negative\") BY product_area | SORT feedback_count DESC | LIMIT 20",
            "params": {"period": {"type": "string", "description": "Time period: 7 days, 30 days, or 90 days"}},
        },
        "top_issues": {
            "description": "Find the most impactful issues from customer feedback.",
            "query": f"FROM {fb_idx} | WHERE sentiment == \"negative\" AND created_at >= NOW() - ?period | STATS issue_count = COUNT(*), avg_sentiment = AVG(sentiment_score), unique_customers = COUNT_DISTINCT(customer_name) BY product_area | SORT issue_count DESC | LIMIT 5",
            "params": {"period": {"type": "string", "description": "Time period: 7 days, 30 days, or 90 days"}},
        },
        "find_similar": {
            "description": "Find feedback items similar to a given text.",
            "query": f"FROM {fb_idx} METADATA _score | WHERE MATCH(text, ?search_text) | KEEP text, sentiment, sentiment_score, product_area, customer_name, created_at, _score | SORT _score DESC | LIMIT 5",
            "params": {"search_text": {"type": "string", "description": "Text to find similar feedback for"}},
        },
        "customer_lookup": {
            "description": "Look up a customer profile and their feedback summary.",
            "query": f"FROM {cust_idx} | WHERE company_name LIKE ?customer_name | KEEP company_name, segment, plan, mrr, arr, health_score, account_manager, renewal_date, industry, employee_count | LIMIT 5",
            "params": {"customer_name": {"type": "string", "description": "Customer/company name to look up"}},
        },
        "compare_segments": {
            "description": "Compare feedback metrics between customer segments.",
            "query": f"FROM {fb_idx} | WHERE created_at >= NOW() - ?period | STATS feedback_count = COUNT(*), avg_sentiment = AVG(sentiment_score), negative_pct = COUNT_IF(sentiment == \"negative\") * 100.0 / COUNT(*) BY customer_segment | SORT feedback_count DESC",
            "params": {"period": {"type": "string", "description": "Time period: 7 days, 30 days, or 90 days"}},
        },
        "generate_spec_prep": {
            "description": "Gather data needed to generate engineering specs for a topic.",
            "query": f"FROM {fb_idx} | WHERE MATCH(text, ?topic) | STATS total_feedback = COUNT(*), avg_sentiment = AVG(sentiment_score), unique_customers = COUNT_DISTINCT(customer_name), sources = VALUES(source) BY product_area | SORT total_feedback DESC | LIMIT 10",
            "params": {"topic": {"type": "string", "description": "The topic/issue to gather spec data for"}},
        },
    }
    cfg = configs.get(tool_base, {})
    config: dict[str, Any] = {"query": cfg.get("query", "")}
    params = cfg.get("params", {})
    if params:
        config["params"] = params
    return {
        "id": _tool_id(org_id, tool_base),
        "type": "esql",
        "description": cfg.get("description", ""),
        "configuration": config,
    }


class AgentService:
    """Service for Kibana Agent Builder proxy and conversation storage."""

    def __init__(self) -> None:
        settings = get_settings()
        self.kibana_url = (settings.kibana_url or "").rstrip("/")
        self.api_key = settings.kibana_api_key or ""
        self.agent_id_base = settings.agent_id or "context-engine-agent"

    def _agent_id(self, org_id: str) -> str:
        short_org = org_id[:12] if len(org_id) > 12 else org_id
        return f"ce-{short_org}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"ApiKey {self.api_key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
        }

    def _enabled(self) -> bool:
        return bool(self.kibana_url and self.api_key)

    async def register_tools(self, org_id: str) -> None:
        """Register org-specific ES|QL tools in Agent Builder."""
        if not self._enabled():
            raise ValueError("Kibana URL and API key are required")
        url = f"{self.kibana_url}/api/agent_builder/tools"
        for tool_base in TOOL_IDS:
            body = _esql_tool_config(org_id, tool_base)
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=body, headers=self._headers())
                    if resp.status_code in (200, 201):
                        logger.info("Registered tool %s for org %s", body["id"], org_id[:8])
                    else:
                        logger.warning("Tool registration %s: %s", body["id"], resp.text)
            except Exception as e:
                logger.error("Failed to register tool %s: %s", body["id"], str(e))
                raise

    async def register_agent(self, org_id: str) -> None:
        """Register/update custom agent with product context in instructions."""
        if not self._enabled():
            raise ValueError("Kibana URL and API key are required")
        product_context = get_product_context(org_id)
        instructions = _build_instructions(product_context)
        tool_ids = [_tool_id(org_id, t) for t in TOOL_IDS]
        tools_config = [{"tool_ids": [tid]} for tid in tool_ids]
        body = {
            "id": self._agent_id(org_id),
            "name": "Context Engine Agent",
            "description": "AI assistant for Product Managers. Analyzes customer feedback, identifies trends, and helps generate engineering specs.",
            "configuration": {
                "instructions": instructions,
                "tools": tools_config,
            },
        }
        url = f"{self.kibana_url}/api/agent_builder/agents"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=body, headers=self._headers())
                if resp.status_code in (200, 201):
                    logger.info("Registered agent for org %s", org_id[:8])
                else:
                    logger.warning("Agent registration: %s", resp.text)
                    resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to register agent: %s", str(e))
            raise

    async def chat(
        self,
        org_id: str,
        user_id: str,
        message: str,
        conversation_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send message to Agent Builder, store conversation, return response.

        Returns: { conversation_id, response, tools_used, citations }
        """
        if not self._enabled():
            raise ValueError("Agent temporarily unavailable. Configure KIBANA_URL and KIBANA_API_KEY.")
        try:
            await self.register_tools(org_id)
        except Exception:
            pass  # May already exist
        try:
            await self.register_agent(org_id)
        except Exception:
            pass  # May already exist

        # Use Kibana's conversation_id for context; our ID for storage
        kibana_conv_id: str | None = None
        if conversation_id:
            existing = get_document(conversations_index(org_id), conversation_id)
            if existing and existing.get("org_id") == org_id:
                kibana_conv_id = existing.get("kibana_conversation_id") or None

        payload: dict[str, Any] = {
            "input": message,
            "agent_id": self._agent_id(org_id),
        }
        if kibana_conv_id:
            payload["conversation_id"] = kibana_conv_id

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.kibana_url}/api/agent_builder/converse",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error("Kibana converse error: %s", e.response.text)
            raise ValueError("Agent temporarily unavailable. Please try again later.")
        except Exception as e:
            logger.error("Kibana converse failed: %s", str(e))
            raise ValueError("Agent temporarily unavailable. Please try again later.")

        # Map Kibana response to our format (structure may vary by ES version)
        logger.debug("Kibana converse raw response keys: %s", list(data.keys()) if isinstance(data, dict) else type(data))

        kibana_conv_id = (
            data.get("conversation_id")
            or data.get("conversationId")
            or data.get("id")
        )
        if not kibana_conv_id and isinstance(data.get("conversation"), dict):
            kibana_conv_id = data["conversation"].get("id") or data["conversation"].get("conversation_id")

        response_text = _extract_response_text(data)
        tools_used = data.get("tools_used") or data.get("tool_calls") or []
        citations = data.get("citations") or []

        idx = conversations_index(org_id)
        ensure_index_exists(idx, CONVERSATIONS_MAPPING)
        now = datetime.utcnow().isoformat() + "Z"
        our_conv_id = conversation_id or str(uuid.uuid4())

        # Load existing or create new
        existing = get_document(idx, our_conv_id)
        messages = list(existing.get("messages", [])) if existing else []
        messages.append({"role": "user", "content": message, "timestamp": now})
        messages.append({"role": "assistant", "content": response_text, "timestamp": now})
        title = (existing or {}).get("title") or (message[:50] + "..." if len(message) > 50 else message)

        doc = {
            "id": our_conv_id,
            "org_id": org_id,
            "user_id": user_id,
            "kibana_conversation_id": kibana_conv_id or "",
            "title": title,
            "messages": messages,
            "created_at": (existing or {}).get("created_at") or now,
            "updated_at": now,
        }
        index_document(idx, our_conv_id, doc)

        return {
            "conversation_id": our_conv_id,
            "response": response_text,
            "tools_used": tools_used,
            "citations": citations,
        }

    def get_conversations(self, org_id: str, user_id: str) -> list[dict[str, Any]]:
        """List conversations for user (UI dropdown)."""
        idx = conversations_index(org_id)
        ensure_index_exists(idx, CONVERSATIONS_MAPPING)
        hits = search_documents(
            idx,
            {"bool": {"must": [{"term": {"org_id": org_id}}, {"term": {"user_id": user_id}}]}},
            size=50,
        )
        # Sort by updated_at desc
        hits.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
        return hits

    def get_conversation(self, org_id: str, conversation_id: str) -> dict[str, Any] | None:
        """Get single conversation for UI display and continuation."""
        idx = conversations_index(org_id)
        doc = get_document(idx, conversation_id)
        if not doc or doc.get("org_id") != org_id:
            return None
        return doc


def get_agent_service() -> AgentService:
    """Return agent service singleton."""
    return AgentService()
