"""Spec generation service — gather data, call LLM, CRUD."""

import uuid
from datetime import datetime
from typing import Any

import httpx

from app.config import get_settings
from app.es_client import get_es_client
from app.models.feedback import FEEDBACK_MAPPING, feedback_index
from app.models.customer import CUSTOMERS_MAPPING, customers_index
from app.models.spec import SPECS_MAPPING, specs_index
from app.services.auth_service import get_user_by_id
from app.services.customer_service import get_customer
from app.services.es_service import (
    delete_document,
    ensure_index_exists,
    get_document,
    index_document,
    search_documents,
)
from app.services.product_service import get_all_wizard_sections, get_product_context
from app.utils.logging import get_logger

logger = get_logger(__name__)


def ensure_specs_index_exists(org_id: str) -> str:
    """Ensure specs index exists. Returns index name."""
    idx = specs_index(org_id)
    ensure_index_exists(idx, SPECS_MAPPING)
    return idx


def _llm_completion(prompt: str, system_prompt: str | None = None) -> str:
    """
    Call LLM for text completion.
    Preferred: ES Inference API. Fallback: Kibana converse (doc-only).
    """
    settings = get_settings()

    # Try ES Inference API first (completion task type)
    if settings.spec_inference_id:
        try:
            es = get_es_client()
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
            resp = es.inference.completion(
                inference_id=settings.spec_inference_id,
                input=full_prompt,
                timeout="300s",
            )
            # Handle ObjectApiResponse (dict-like)
            data = resp if isinstance(resp, dict) else getattr(resp, "body", resp) or {}
            text = None
            if isinstance(data, dict):
                # ES Inference completion API format: { "completion": [ { "result": "..." } ] }
                completion_arr = data.get("completion", [])
                if completion_arr and isinstance(completion_arr[0], dict):
                    text = completion_arr[0].get("result")
                if not text:
                    # Legacy inference_results format
                    results = data.get("inference_results", [])
                    if results:
                        outputs = results[0].get("output", [])
                        if outputs:
                            text = outputs[0].get("output_text")
                if not text:
                    text = data.get("result") or data.get("output")
            if isinstance(text, str) and text.strip():
                return text.strip()
        except Exception as e:
            logger.warning("ES Inference for spec failed, using Kibana fallback: %s", e)

    # Fallback: Kibana converse with strict doc-only prompt
    if settings.kibana_url and settings.kibana_api_key:
        try:
            url = f"{settings.kibana_url.rstrip('/')}/api/agent_builder/converse"
            headers = {
                "Authorization": f"ApiKey {settings.kibana_api_key}",
                "kbn-xsrf": "true",
                "Content-Type": "application/json",
            }
            full_input = prompt
            if system_prompt:
                full_input = f"{system_prompt}\n\n---\n\n{prompt}"
            payload = {
                "input": full_input,
                "agent_id": settings.agent_id,
            }
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            # Extract text from converse response
            for key in ("response", "output", "content", "text"):
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            steps = data.get("steps", [])
            if isinstance(steps, list) and steps:
                last = steps[-1]
                if isinstance(last, dict):
                    for k in ("content", "message", "output", "text"):
                        v = last.get(k)
                        if isinstance(v, str) and v.strip():
                            return v.strip()
        except Exception as e:
            logger.error("Kibana converse for spec failed: %s", e)
            raise ValueError("Spec generation temporarily unavailable. Please try again.")

    raise ValueError(
        "Spec generation requires SPEC_INFERENCE_ID or KIBANA_URL + KIBANA_API_KEY."
    )


def _build_data_brief(
    org_id: str,
    topic: str,
    product_area: str | None,
    feedback_hits: list[dict],
    customer_ids: list[str],
    total_arr: float,
    data_freshness_date: str | None,
) -> dict[str, Any]:
    """Build data_brief for LLM prompts and regeneration."""
    feedback_quotes = []
    feedback_ids = []
    for h in feedback_hits[:20]:
        fid = h.get("id")
        if fid:
            feedback_ids.append(fid)
        text = (h.get("text") or "").strip()
        if not text:
            continue
        cust = h.get("customer_name") or "Unknown"
        sentiment = h.get("sentiment") or "neutral"
        feedback_quotes.append({
            "id": fid,
            "customer_id": h.get("customer_id"),
            "text": text[:500] + ("..." if len(text) > 500 else ""),
            "customer_name": cust,
            "sentiment": sentiment,
        })

    product_context = get_all_wizard_sections(org_id)
    goals = (product_context.get("goals", {}).get("data", {}).get("goals", [])) or []
    roadmap = product_context.get("roadmap", {}).get("data", {}) or {}
    teams = (product_context.get("teams", {}).get("data", {}).get("teams", [])) or []
    tech = product_context.get("tech_stack", {}).get("data", {}).get("technologies", []) or []

    return {
        "topic": topic,
        "product_area": product_area,
        "feedback_count": len(feedback_hits),
        "customer_count": len(customer_ids),
        "total_arr": total_arr,
        "data_freshness_date": data_freshness_date,
        "feedback_quotes": feedback_quotes,
        "feedback_ids": feedback_ids,
        "customer_ids": list(customer_ids),
        "goals": goals,
        "roadmap": roadmap,
        "teams": teams,
        "tech_stack": tech,
    }


def gather_spec_data(
    org_id: str,
    topic: str,
    product_area: str | None = None,
) -> dict[str, Any]:
    """
    Gather feedback, customers, ARR, product context for spec generation.
    Returns data_brief dict. Raises ValueError if feedback_count == 0.
    """
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()

    must = [{"term": {"org_id": org_id}}, {"match": {"text": topic}}]
    if product_area:
        must.append({"term": {"product_area": product_area}})

    resp = es.search(
        index=idx,
        query={"bool": {"must": must}},
        size=100,
        sort=[{"created_at": {"order": "desc"}}],
        _source=["id", "text", "customer_id", "customer_name", "sentiment", "product_area", "created_at"],
    )
    hits = resp.get("hits", {}).get("hits", [])
    feedback_hits = [h["_source"] for h in hits]

    if not feedback_hits:
        raise ValueError("Not enough feedback to generate specs for this topic.")

    customer_ids = list({h.get("customer_id") for h in feedback_hits if h.get("customer_id")})
    total_arr = 0.0
    cust_idx = customers_index(org_id)
    ensure_index_exists(cust_idx, CUSTOMERS_MAPPING)
    for cid in customer_ids:
        cust = get_customer(org_id, cid) if cid else None
        if cust and cust.get("arr") is not None:
            total_arr += float(cust["arr"])

    max_created = max(
        (h.get("created_at") for h in feedback_hits if h.get("created_at")),
        default=None,
    )
    data_freshness_date = max_created

    return _build_data_brief(
        org_id,
        topic,
        product_area,
        feedback_hits,
        customer_ids,
        total_arr,
        data_freshness_date,
    )


def _format_product_context(pc: Any) -> str:
    """Format product context for LLM prompts."""
    parts = []
    if pc.product_name:
        parts.append(f"Product: {pc.product_name}")
    if pc.description:
        parts.append(f"Description: {pc.description}")
    if pc.areas:
        parts.append("\n## Product Areas")
        for a in pc.areas:
            name = a.get("name", a) if isinstance(a, dict) else str(a)
            parts.append(f"- {name}")
    if pc.goals:
        parts.append("\n## Business Goals")
        for g in pc.goals:
            title = g.get("title", g) if isinstance(g, dict) else str(g)
            parts.append(f"- {title}")
    if pc.segments:
        parts.append("\n## Customer Segments")
        for s in pc.segments:
            name = s.get("name", s) if isinstance(s, dict) else str(s)
            parts.append(f"- {name}")
    if pc.competitors:
        parts.append("\n## Competitors")
        for c in pc.competitors:
            name = c.get("name", c) if isinstance(c, dict) else str(c)
            parts.append(f"- {name}")
    if pc.teams:
        parts.append("\n## Teams")
        for t in pc.teams:
            name = t.get("name", t) if isinstance(t, dict) else str(t)
            parts.append(f"- {name}")
    if pc.technologies:
        parts.append("\n## Tech Stack")
        for t in pc.technologies:
            name = t.get("name", t) if isinstance(t, dict) else str(t)
            parts.append(f"- {name}")
    if pc.existing_features or pc.planned_features:
        parts.append("\n## Roadmap")
        if pc.existing_features:
            parts.append("Existing features:")
            for f in pc.existing_features[:10]:
                parts.append(f"  - {f.get('name', f) if isinstance(f, dict) else f}")
        if pc.planned_features:
            parts.append("Planned features:")
            for f in pc.planned_features[:10]:
                parts.append(f"  - {f.get('name', f) if isinstance(f, dict) else f}")
    return "\n".join(parts) if parts else "No product context available."


def generate_prd(data_brief: dict[str, Any], product_context: Any) -> str:
    """Generate PRD markdown via LLM."""
    quotes_text = "\n".join(
        f"- feedback_id={q.get('id', '')} customer_id={q.get('customer_id', '') or ''} [{q.get('customer_name', 'Unknown')}] {q.get('text', '')[:200]}... (sentiment: {q.get('sentiment', 'neutral')})"
        for q in data_brief.get("feedback_quotes", [])[:15]
    )
    pc_text = _format_product_context(product_context)
    arr = data_brief.get("total_arr") or 0
    prompt = f"""Generate a PRD for: {data_brief.get('topic', 'unknown topic')}

Based on {data_brief.get('feedback_count', 0)} customer feedback items affecting {data_brief.get('customer_count', 0)} customers (${arr:,.0f} ARR).

## Data Available
{quotes_text}

## Product Context
{pc_text}

## PRD Structure
1. Problem Statement — What's broken, who's affected, business impact
2. User Stories — Derived from real feedback, cite specific customers
3. Requirements — Functional requirements with priority (P0-P3)
4. Success Metrics — Measurable outcomes linked to business goals
5. Out of Scope — What this spec intentionally excludes
6. Open Questions — Unresolved items needing team input

## Rules
- Every requirement must trace to real feedback
- Include exact customer quotes (with attribution)
- Mention specific customer names and ARR when citing impact
- Reference business goals where relevant
- Be specific and actionable, not generic
- For customer citations use markdown links: [Company Name](/customers/CUSTOMER_ID)
- For feedback quotes use markdown links: [quote text](/feedback?id=FEEDBACK_ID)
- Use the feedback_id and customer_id from the Data Available section when creating links
"""
    return _llm_completion(
        prompt,
        system_prompt="You are a senior product/engineering writer. Output only valid markdown. No preamble.",
    )


def generate_architecture(data_brief: dict[str, Any], product_context: Any) -> str:
    """Generate Architecture markdown via LLM."""
    pc_text = _format_product_context(product_context)
    prompt = f"""Generate an Architecture doc for: {data_brief.get('topic', 'unknown topic')}

## Structure
1. System Overview — How this fits into existing architecture
2. Technical Approach — Recommended implementation strategy
3. Data Model Changes — New/modified schemas
4. API Changes — New/modified endpoints
5. Dependencies — External services, libraries
6. Migration Strategy — How to roll out safely
7. Performance Considerations — Scale, latency, caching
8. Security Considerations

## Context
Current tech stack and architecture: {pc_text}
"""
    return _llm_completion(
        prompt,
        system_prompt="You are a senior engineer. Output only valid markdown. No preamble.",
    )


def generate_rules(data_brief: dict[str, Any], product_context: Any) -> str:
    """Generate Engineering Rules markdown via LLM."""
    prompt = f"""Generate Engineering Rules for: {data_brief.get('topic', 'unknown topic')}

## Structure
1. Coding Standards — Specific to this feature
2. Error Handling — What can go wrong, how to handle
3. Testing Requirements — Unit, integration, e2e test cases
4. Logging & Monitoring — What to log, alerts to set
5. Rollback Plan — How to undo if things break
6. Edge Cases — From real feedback
7. Accessibility Requirements
8. Documentation Requirements
"""
    return _llm_completion(
        prompt,
        system_prompt="You are a senior engineer. Output only valid markdown. No preamble.",
    )


def generate_plan(data_brief: dict[str, Any], product_context: Any) -> str:
    """Generate Implementation Plan markdown via LLM."""
    pc_text = _format_product_context(product_context)
    prompt = f"""Generate an Implementation Plan for: {data_brief.get('topic', 'unknown topic')}

## Structure
1. Phase Breakdown — Split into shippable increments
2. Task List — Specific tasks with time estimates
3. Dependencies — What blocks what
4. Team Assignments — Who does what (use teams from product context)
5. Timeline — Realistic schedule
6. Risk Register — What could go wrong
7. Definition of Done — Per phase and overall
8. Launch Checklist — Pre-launch verification steps

## Product Context
{pc_text}
"""
    return _llm_completion(
        prompt,
        system_prompt="You are a senior engineering lead. Output only valid markdown. No preamble.",
    )


def generate_specs(
    org_id: str,
    user_id: str,
    topic: str,
    product_area: str | None = None,
) -> dict[str, Any]:
    """
    Full pipeline: gather data → 4 LLM calls → save.
    Returns saved spec document.
    """
    data_brief = gather_spec_data(org_id, topic, product_area)
    product_context = get_product_context(org_id)

    prd = generate_prd(data_brief, product_context)
    architecture = generate_architecture(data_brief, product_context)
    rules = generate_rules(data_brief, product_context)
    plan = generate_plan(data_brief, product_context)

    user = get_user_by_id(user_id)
    generated_by_name = (user.get("full_name") or user.get("email") or "Unknown") if user else "Unknown"

    title = (topic[:80] + "..." if len(topic) > 80 else topic).title()
    spec_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    doc = {
        "id": spec_id,
        "org_id": org_id,
        "title": title,
        "topic": topic,
        "product_area": product_area,
        "status": "draft",
        "prd": prd,
        "architecture": architecture,
        "rules": rules,
        "plan": plan,
        "feedback_count": data_brief.get("feedback_count", 0),
        "customer_count": data_brief.get("customer_count", 0),
        "total_arr": data_brief.get("total_arr", 0),
        "feedback_ids": data_brief.get("feedback_ids", []),
        "customer_ids": data_brief.get("customer_ids", []),
        "linked_goal_id": None,
        "generated_by": user_id,
        "generated_by_name": generated_by_name,
        "data_brief": data_brief,
        "data_freshness_date": data_brief.get("data_freshness_date"),
        "created_at": now,
        "updated_at": now,
    }
    idx = ensure_specs_index_exists(org_id)
    index_document(idx, spec_id, doc)
    logger.info("Generated spec %s for org %s", spec_id[:8], org_id[:8])
    return doc


def save_spec(org_id: str, spec_data: dict[str, Any]) -> dict[str, Any]:
    """Save spec document. Returns saved doc."""
    idx = ensure_specs_index_exists(org_id)
    spec_id = spec_data.get("id") or str(uuid.uuid4())
    index_document(idx, spec_id, spec_data)
    return spec_data


def get_spec(org_id: str, spec_id: str) -> dict[str, Any] | None:
    """Get single spec. Returns None if not found or wrong org."""
    idx = specs_index(org_id)
    doc = get_document(idx, spec_id)
    if not doc or doc.get("org_id") != org_id:
        return None
    return doc


def get_specs(
    org_id: str,
    page: int = 1,
    page_size: int = 20,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated specs. Returns (items, total_count)."""
    idx = ensure_specs_index_exists(org_id)
    filters = filters or {}

    must = [{"term": {"org_id": org_id}}]
    if filters.get("product_area"):
        must.append({"term": {"product_area": filters["product_area"]}})
    if filters.get("status"):
        must.append({"term": {"status": filters["status"]}})
    if filters.get("customer_id"):
        must.append({"term": {"customer_ids": filters["customer_id"]}})
    if filters.get("date_from") or filters.get("date_to"):
        r: dict[str, Any] = {}
        if filters.get("date_from"):
            r["gte"] = filters["date_from"]
        if filters.get("date_to"):
            r["lte"] = filters["date_to"]
        must.append({"range": {"created_at": r}})

    es = get_es_client()
    resp = es.search(
        index=idx,
        query={"bool": {"must": must}},
        from_=(page - 1) * page_size,
        size=page_size,
        sort=[{"created_at": {"order": "desc"}}],
    )
    hits = resp.get("hits", {})
    total = hits.get("total", {})
    total_val = total.get("value", 0) if isinstance(total, dict) else total
    items = [h["_source"] for h in hits.get("hits", [])]
    return (items, total_val)


def update_spec(org_id: str, spec_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    """Update spec fields. Returns updated doc or None."""
    doc = get_spec(org_id, spec_id)
    if not doc:
        return None
    now = datetime.utcnow().isoformat() + "Z"
    allowed = {"status", "prd", "architecture", "rules", "plan", "title"}
    for k, v in updates.items():
        if k in allowed and v is not None:
            doc[k] = v
    doc["updated_at"] = now
    idx = specs_index(org_id)
    index_document(idx, spec_id, doc)
    return doc


def delete_spec(org_id: str, spec_id: str) -> bool:
    """Delete spec. Returns True if deleted."""
    doc = get_spec(org_id, spec_id)
    if not doc:
        return False
    idx = specs_index(org_id)
    return delete_document(idx, spec_id)


def regenerate_spec(org_id: str, spec_id: str, user_id: str) -> dict[str, Any] | None:
    """Regenerate 4 docs from saved data_brief. Sets status=draft. Returns updated spec."""
    doc = get_spec(org_id, spec_id)
    if not doc:
        return None
    data_brief = doc.get("data_brief")
    if not data_brief:
        raise ValueError("Spec has no data_brief; cannot regenerate.")

    product_context = get_product_context(org_id)
    prd = generate_prd(data_brief, product_context)
    architecture = generate_architecture(data_brief, product_context)
    rules = generate_rules(data_brief, product_context)
    plan = generate_plan(data_brief, product_context)

    now = datetime.utcnow().isoformat() + "Z"
    doc["prd"] = prd
    doc["architecture"] = architecture
    doc["rules"] = rules
    doc["plan"] = plan
    doc["status"] = "draft"
    doc["updated_at"] = now

    idx = specs_index(org_id)
    index_document(idx, spec_id, doc)
    logger.info("Regenerated spec %s for org %s", spec_id[:8], org_id[:8])
    return doc
