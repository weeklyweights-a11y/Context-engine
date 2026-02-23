"""Search service for hybrid semantic + keyword feedback search."""

from typing import Any

from app.es_client import get_es_client
from app.models.feedback import (
    FEEDBACK_MAPPING,
    FEEDBACK_MAPPING_WITH_ELSER,
    feedback_index,
)
from app.services.es_service import ensure_index_exists
from app.services.feedback_service import get_feedback_item
from app.services.elser_service import ensure_elser_deployed, is_elser_available
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _ensure_feedback_index(org_id: str) -> str:
    """Ensure feedback index exists. Returns index name."""
    idx = feedback_index(org_id)
    ensure_elser_deployed(get_es_client())
    mapping = FEEDBACK_MAPPING_WITH_ELSER if is_elser_available() else FEEDBACK_MAPPING
    ensure_index_exists(idx, mapping)
    return idx


def build_filter_clauses(filters: dict[str, Any] | None) -> list[dict[str, Any]]:
    """
    Convert filter dict to ES bool filter array.
    Filters: product_area, source, sentiment, customer_segment (terms),
    date_from/date_to (range), customer_id (term), has_customer (exists).
    """
    clauses: list[dict[str, Any]] = []
    filters = filters or {}

    if filters.get("product_area"):
        val = filters["product_area"]
        terms = [val] if isinstance(val, str) else val
        if terms:
            clauses.append({"terms": {"product_area": terms}})

    if filters.get("source"):
        val = filters["source"]
        terms = [val] if isinstance(val, str) else val
        if terms:
            clauses.append({"terms": {"source": terms}})

    if filters.get("sentiment"):
        val = filters["sentiment"]
        terms = [val] if isinstance(val, str) else val
        if terms:
            clauses.append({"terms": {"sentiment": terms}})

    if filters.get("customer_segment"):
        val = filters["customer_segment"]
        terms = [val] if isinstance(val, str) else val
        if terms:
            clauses.append({"terms": {"customer_segment": terms}})

    date_range: dict[str, Any] = {}
    if filters.get("date_from"):
        date_range["gte"] = filters["date_from"]
    if filters.get("date_to"):
        date_range["lte"] = filters["date_to"]
    if date_range:
        clauses.append({"range": {"created_at": date_range}})

    if filters.get("customer_id"):
        clauses.append({"term": {"customer_id": filters["customer_id"]}})

    if filters.get("has_customer") is True:
        clauses.append({"exists": {"field": "customer_id"}})
    elif filters.get("has_customer") is False:
        clauses.append({"bool": {"must_not": [{"exists": {"field": "customer_id"}}]}})

    return clauses


def search_feedback(
    org_id: str,
    query: str,
    filters: dict[str, Any] | None,
    sort_by: str,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int]:
    """
    Hybrid search on feedback.
    Query non-empty: ELSER semantic + BM25 keyword (bool.should), sort by _score.
    Query empty: match_all + filters, sort by created_at desc.
    When ELSER unavailable: keyword-only fallback.
    """
    idx = _ensure_feedback_index(org_id)
    es = get_es_client()
    filter_clauses = build_filter_clauses(filters)
    base_filter = [{"term": {"org_id": org_id}}] + filter_clauses

    query_str = (query or "").strip()
    has_query = bool(query_str)

    if has_query and is_elser_available():
        # Hybrid: semantic + keyword
        should_clauses: list[dict[str, Any]] = [
            {"match": {"text": {"query": query_str, "boost": 1}}},
            {
                "semantic": {
                    "field": "text_semantic",
                    "query": query_str,
                    "boost": 2,
                },
            },
        ]
        main_query: dict[str, Any] = {
            "bool": {
                "must": [{"bool": {"should": should_clauses, "minimum_should_match": 1}}],
                "filter": base_filter,
            },
        }
        sort_clause: list[dict[str, Any]] = [{"_score": {"order": "desc"}}]
    elif has_query:
        # Keyword-only fallback when ELSER unavailable
        main_query = {
            "bool": {
                "must": [{"match": {"text": query_str}}],
                "filter": base_filter,
            },
        }
        sort_clause = [{"_score": {"order": "desc"}}]
    else:
        # Empty query: match_all + filters
        main_query = {"bool": {"must": [{"match_all": {}}], "filter": base_filter}}
        sort_clause = [{"created_at": {"order": "desc"}}]

    # Override sort when explicitly requested
    if not has_query:
        sort_clause = [{"created_at": {"order": "desc"}}]
    elif sort_by == "date":
        sort_clause = [{"created_at": {"order": "desc"}}]
    elif sort_by == "sentiment":
        sort_clause = [{"sentiment_score": {"order": "asc"}}]  # Most negative first

    from_ = (page - 1) * page_size
    resp = es.search(
        index=idx,
        query=main_query,
        from_=from_,
        size=page_size,
        sort=sort_clause,
    )
    hits = resp.get("hits", {})
    total = hits.get("total", {})
    total_val = total.get("value", 0) if isinstance(total, dict) else total
    items = [h["_source"] for h in hits.get("hits", [])]
    return (items, total_val)


def find_similar(
    org_id: str,
    feedback_id: str,
    size: int = 5,
) -> list[dict[str, Any]]:
    """
    Find feedback items similar to the given item.
    Uses semantic search with source text as query when ELSER available;
    fallback to more_like_this when ELSER unavailable.
    Excludes the source item. Returns up to size items.
    """
    source = get_feedback_item(org_id, feedback_id)
    if not source:
        return []

    idx = _ensure_feedback_index(org_id)
    es = get_es_client()
    text = (source.get("text") or "").strip()
    if not text:
        return []

    if is_elser_available():
        try:
            main_query: dict[str, Any] = {
                "bool": {
                    "must": [
                        {
                            "semantic": {
                                "field": "text_semantic",
                                "query": text,
                            },
                        },
                    ],
                    "filter": [
                        {"term": {"org_id": org_id}},
                        {"bool": {"must_not": [{"term": {"id": feedback_id}}]}},
                    ],
                },
            }
            resp = es.search(
                index=idx,
                query=main_query,
                size=size,
                sort=[{"_score": {"order": "desc"}}],
            )
        except Exception as e:
            logger.warning("Semantic similar search failed, using more_like_this: %s", e)
            main_query = {
                "bool": {
                    "must": [
                        {
                            "more_like_this": {
                                "fields": ["text"],
                                "like": [{"_index": idx, "_id": feedback_id}],
                                "min_term_freq": 1,
                                "max_query_terms": 12,
                            },
                        },
                    ],
                    "filter": [{"term": {"org_id": org_id}}],
                },
            }
            resp = es.search(index=idx, query=main_query, size=size + 1)
    else:
        main_query = {
            "bool": {
                "must": [
                    {
                        "more_like_this": {
                            "fields": ["text"],
                            "like": [{"_index": idx, "_id": feedback_id}],
                            "min_term_freq": 1,
                            "max_query_terms": 12,
                        },
                    },
                ],
                "filter": [{"term": {"org_id": org_id}}],
            },
        }
        resp = es.search(index=idx, query=main_query, size=size + 1)

    hits = resp.get("hits", {}).get("hits", [])
    items = []
    for h in hits:
        doc = h.get("_source", {})
        if doc.get("id") != feedback_id:
            items.append(doc)
        if len(items) >= size:
            break
    return items
