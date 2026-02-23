"""Feedback item service."""

import uuid
from datetime import datetime
from typing import Any

from app.es_client import get_es_client
from app.models.feedback import (
    FEEDBACK_MAPPING,
    FEEDBACK_MAPPING_WITH_ELSER,
    feedback_index,
)
from app.services.customer_service import (
    get_customer_by_company_name,
    get_customer_by_external_id,
)
from app.services.elser_service import ensure_elser_deployed, is_elser_available
from app.services.es_service import (
    bulk_index_documents,
    ensure_index_exists,
    get_document,
    index_document,
)
from app.services.sentiment_service import analyze_sentiment
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _ensure_feedback_index(org_id: str) -> str:
    """Ensure feedback index exists. Returns index name."""
    idx = feedback_index(org_id)
    ensure_elser_deployed(get_es_client())
    mapping = FEEDBACK_MAPPING_WITH_ELSER if is_elser_available() else FEEDBACK_MAPPING
    ensure_index_exists(idx, mapping)
    return idx


def _resolve_customer(org_id: str, customer_id: str | None, customer_name: str | None) -> dict[str, Any]:
    """Resolve customer for denormalization. Returns {customer_id, customer_name, customer_segment}."""
    result = {"customer_id": None, "customer_name": customer_name, "customer_segment": None}
    if customer_id:
        from app.services.customer_service import get_customer

        cust = get_customer(org_id, customer_id)
        if cust:
            result["customer_id"] = cust.get("id")
            result["customer_name"] = cust.get("company_name") or customer_name
            result["customer_segment"] = cust.get("segment")
        return result
    if customer_name:
        cust = get_customer_by_company_name(org_id, customer_name)
        if cust:
            result["customer_id"] = cust.get("id")
            result["customer_name"] = cust.get("company_name")
            result["customer_segment"] = cust.get("segment")
    return result


def create_feedback_item(
    org_id: str,
    data: dict[str, Any],
    ingestion_method: str = "manual_entry",
    source_file: str | None = None,
) -> dict[str, Any]:
    """Create single feedback item. Auto-analyzes sentiment, resolves customer."""
    idx = _ensure_feedback_index(org_id)
    text = (data.get("text") or "").strip()
    if not text:
        raise ValueError("Feedback text is required")

    sentiment, score = analyze_sentiment(text) if not data.get("sentiment") else (
        data.get("sentiment", "neutral"),
        float(data.get("sentiment_score", 0)),
    )
    cust = _resolve_customer(
        org_id,
        data.get("customer_id"),
        data.get("customer_name"),
    )
    if data.get("customer_id") and not cust["customer_id"]:
        cust["customer_name"] = data.get("customer_name")

    feedback_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    created_at = data.get("created_at") or now

    doc = {
        "id": feedback_id,
        "org_id": org_id,
        "text": text,
        "source": data.get("source"),
        "sentiment": sentiment,
        "sentiment_score": score,
        "rating": data.get("rating"),
        "product_area": data.get("product_area"),
        "customer_id": cust["customer_id"],
        "customer_name": cust["customer_name"],
        "customer_segment": cust["customer_segment"],
        "author_name": data.get("author_name"),
        "author_email": data.get("author_email"),
        "tags": data.get("tags", []),
        "source_file": source_file,
        "ingestion_method": ingestion_method,
        "created_at": created_at,
        "ingested_at": now,
        "metadata": data.get("metadata", {}),
    }
    if is_elser_available():
        doc["text_semantic"] = text
    doc = {k: v for k, v in doc.items() if v is not None}
    if doc.get("tags") is not None and not isinstance(doc["tags"], list):
        doc["tags"] = [doc["tags"]]

    index_document(idx, feedback_id, doc)
    logger.info("Created feedback %s for org %s", feedback_id[:8], org_id[:8])
    return doc


def create_feedback_items_bulk(
    org_id: str,
    items: list[dict[str, Any]],
    ingestion_method: str = "csv_upload",
    source_file: str | None = None,
    default_source: str | None = None,
    auto_analyze_sentiment: bool = True,
) -> tuple[int, int, list[str]]:
    """
    Bulk create feedback items. Returns (imported_count, failed_count, created_ids).

    Each item can have customer_id or customer_name for resolution.
    """
    idx = _ensure_feedback_index(org_id)
    now = datetime.utcnow().isoformat() + "Z"
    docs: list[dict[str, Any]] = []
    failed = 0
    include_semantic = is_elser_available()

    for item in items:
        text = (item.get("text") or "").strip()
        if not text:
            failed += 1
            continue

        if auto_analyze_sentiment and not item.get("sentiment"):
            sentiment, score = analyze_sentiment(text)
        else:
            sentiment = item.get("sentiment", "neutral")
            score = float(item.get("sentiment_score", 0))

        cust = _resolve_customer(
            org_id,
            item.get("customer_id"),
            item.get("customer_name"),
        )

        feedback_id = str(uuid.uuid4())
        created_at = item.get("created_at") or now

        doc = {
            "id": feedback_id,
            "org_id": org_id,
            "text": text,
            "source": item.get("source") or default_source,
            "sentiment": sentiment,
            "sentiment_score": score,
            "rating": item.get("rating"),
            "product_area": item.get("product_area"),
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "customer_segment": cust["customer_segment"],
            "author_name": item.get("author_name"),
            "author_email": item.get("author_email"),
            "tags": item.get("tags", []),
            "source_file": source_file,
            "ingestion_method": ingestion_method,
            "created_at": created_at,
            "ingested_at": now,
            "metadata": {},
        }
        if include_semantic:
            doc["text_semantic"] = text
        doc = {k: v for k, v in doc.items() if v is not None}
        if doc.get("tags") is not None and not isinstance(doc["tags"], list):
            doc["tags"] = [doc["tags"]]
        docs.append(doc)

    if not docs:
        return (0, failed, [])

    success, bulk_failed = bulk_index_documents(idx, docs)
    created_ids = [d["id"] for d in docs]
    return (success, failed + bulk_failed, created_ids)


def get_feedback_item(org_id: str, item_id: str) -> dict[str, Any] | None:
    """Get single feedback item. Returns None if not found or wrong org."""
    idx = feedback_index(org_id)
    doc = get_document(idx, item_id)
    if not doc or doc.get("org_id") != org_id:
        return None
    return doc


def get_feedback_items(
    org_id: str,
    page: int = 1,
    page_size: int = 20,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated feedback. Returns (items, total_count)."""
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)

    must = [{"term": {"org_id": org_id}}]
    filters = filters or {}
    if filters.get("source_type"):
        must.append({"term": {"source": filters["source_type"]}})
    if filters.get("product_area"):
        must.append({"term": {"product_area": filters["product_area"]}})
    if filters.get("sentiment"):
        must.append({"term": {"sentiment": filters["sentiment"]}})

    query = {"bool": {"must": must}}
    sort_field = filters.get("sort_by", "created_at")
    sort_order = "desc" if filters.get("sort_order", "desc") == "desc" else "asc"

    es = get_es_client()
    resp = es.search(
        index=idx,
        query=query,
        from_=(page - 1) * page_size,
        size=page_size,
        sort=[{sort_field: {"order": sort_order}}],
    )
    hits = resp.get("hits", {})
    total = hits.get("total", {})
    if isinstance(total, dict):
        total_val = total.get("value", 0)
    else:
        total_val = total
    items = [h["_source"] for h in hits.get("hits", [])]
    return (items, total_val)


def get_feedback_count(org_id: str) -> int:
    """Get total feedback count for org."""
    idx = feedback_index(org_id)
    try:
        es = get_es_client()
        resp = es.count(index=idx, query={"term": {"org_id": org_id}})
        return resp.get("count", 0)
    except Exception:
        return 0
