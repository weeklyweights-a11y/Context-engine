"""Customer profile service."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from app.es_client import get_es_client
from app.models.customer import CUSTOMERS_MAPPING, customers_index
from app.models.feedback import FEEDBACK_MAPPING, feedback_index
from app.services.es_service import (
    bulk_index_documents,
    ensure_index_exists,
    get_document,
    index_document,
    search_documents,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_customer(org_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Create single customer. Returns created document."""
    idx = customers_index(org_id)
    ensure_index_exists(idx, CUSTOMERS_MAPPING)

    customer_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    doc = {
        "id": customer_id,
        "org_id": org_id,
        "company_name": data.get("company_name", ""),
        "customer_id_external": data.get("customer_id_external"),
        "segment": data.get("segment"),
        "plan": data.get("plan"),
        "mrr": data.get("mrr"),
        "arr": data.get("arr"),
        "account_manager": data.get("account_manager"),
        "renewal_date": data.get("renewal_date"),
        "health_score": data.get("health_score"),
        "industry": data.get("industry"),
        "employee_count": data.get("employee_count"),
        "created_at": now,
        "updated_at": now,
        "metadata": data.get("metadata", {}),
    }
    doc = {k: v for k, v in doc.items() if v is not None}
    index_document(idx, customer_id, doc)
    logger.info("Created customer %s for org %s", customer_id[:8], org_id[:8])
    return doc


def create_customers_bulk(
    org_id: str,
    customers: list[dict[str, Any]],
) -> tuple[int, int, list[str]]:
    """Bulk create customers. Returns (imported_count, failed_count, created_ids)."""
    idx = customers_index(org_id)
    ensure_index_exists(idx, CUSTOMERS_MAPPING)

    now = datetime.utcnow().isoformat() + "Z"
    docs: list[dict[str, Any]] = []
    for c in customers:
        company_name = c.get("company_name") or c.get("company")
        if not company_name or not str(company_name).strip():
            continue
        customer_id = str(uuid.uuid4())
        doc = {
            "id": customer_id,
            "org_id": org_id,
            "company_name": str(company_name).strip(),
            "customer_id_external": c.get("customer_id_external") or c.get("customer_id"),
            "segment": c.get("segment"),
            "plan": c.get("plan"),
            "mrr": _to_float(c.get("mrr")),
            "arr": _to_float(c.get("arr")),
            "account_manager": c.get("account_manager"),
            "renewal_date": c.get("renewal_date"),
            "health_score": _to_int(c.get("health_score")),
            "industry": c.get("industry"),
            "employee_count": _to_int(c.get("employee_count")),
            "created_at": now,
            "updated_at": now,
            "metadata": {},
        }
        doc = {k: v for k, v in doc.items() if v is not None}
        docs.append(doc)

    if not docs:
        return (0, len(customers), [])

    success, failed = bulk_index_documents(idx, docs)
    created_ids = [d["id"] for d in docs]
    return (success, failed + (len(customers) - len(docs)), created_ids)


def _to_float(v: Any) -> float | None:
    """Convert to float or None."""
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _to_int(v: Any) -> int | None:
    """Convert to int or None."""
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def get_customer(org_id: str, customer_id: str) -> dict[str, Any] | None:
    """Get single customer. Returns None if not found or wrong org."""
    idx = customers_index(org_id)
    doc = get_document(idx, customer_id)
    if not doc or doc.get("org_id") != org_id:
        return None
    return doc


def get_customer_by_external_id(org_id: str, external_id: str) -> dict[str, Any] | None:
    """Find customer by customer_id_external."""
    idx = customers_index(org_id)
    hits = search_documents(
        idx,
        {"bool": {"must": [{"term": {"org_id": org_id}}, {"term": {"customer_id_external": external_id}}]}},
        size=1,
    )
    return hits[0] if hits else None


def get_customer_by_company_name(org_id: str, company_name: str) -> dict[str, Any] | None:
    """Find customer by company name (exact match on keyword field)."""
    if not company_name or not str(company_name).strip():
        return None
    idx = customers_index(org_id)
    name = str(company_name).strip()
    hits = search_documents(
        idx,
        {
            "bool": {
                "must": [
                    {"term": {"org_id": org_id}},
                    {"term": {"company_name.keyword": name}},
                ]
            }
        },
        size=1,
    )
    if hits:
        return hits[0]
    return None


def _get_customers_with_negative_feedback(org_id: str) -> list[str]:
    """Return list of customer_ids that have at least one negative feedback."""
    f_idx = feedback_index(org_id)
    ensure_index_exists(f_idx, FEEDBACK_MAPPING)
    es = get_es_client()
    resp = es.search(
        index=f_idx,
        query={
            "bool": {
                "filter": [
                    {"term": {"org_id": org_id}},
                    {"term": {"sentiment": "negative"}},
                    {"exists": {"field": "customer_id"}},
                ]
            }
        },
        size=0,
        aggs={
            "customers": {"terms": {"field": "customer_id", "size": 10000}},
        },
    )
    buckets = resp.get("aggregations", {}).get("customers", {}).get("buckets", [])
    return [b["key"] for b in buckets]


def _get_feedback_stats_by_customer(org_id: str) -> dict[str, dict[str, int]]:
    """Return {customer_id: {feedback_count, negative_feedback_count}}."""
    f_idx = feedback_index(org_id)
    ensure_index_exists(f_idx, FEEDBACK_MAPPING)
    es = get_es_client()
    resp = es.search(
        index=f_idx,
        query={
            "bool": {
                "filter": [
                    {"term": {"org_id": org_id}},
                    {"exists": {"field": "customer_id"}},
                ]
            }
        },
        size=0,
        aggs={
            "by_customer": {
                "terms": {"field": "customer_id", "size": 10000},
                "aggs": {
                    "negative_count": {
                        "filter": {"term": {"sentiment": "negative"}},
                    },
                },
            },
        },
    )
    buckets = resp.get("aggregations", {}).get("by_customer", {}).get("buckets", [])
    result: dict[str, dict[str, int]] = {}
    for b in buckets:
        cid = b["key"]
        result[cid] = {
            "feedback_count": b["doc_count"],
            "negative_feedback_count": b["negative_count"]["doc_count"],
        }
    return result


def get_customers(
    org_id: str,
    page: int = 1,
    page_size: int = 20,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated customers. Returns (items, total_count).
    Extended filters: search, renewal_within_days, arr_min, arr_max,
    has_negative_feedback, include_feedback_stats.
    """
    idx = customers_index(org_id)
    ensure_index_exists(idx, CUSTOMERS_MAPPING)
    filters = filters or {}

    must: list[dict[str, Any]] = [{"term": {"org_id": org_id}}]

    if filters.get("search"):
        q = str(filters["search"]).strip()
        if q:
            must.append({
                "multi_match": {
                    "query": q,
                    "fields": ["company_name", "account_manager", "industry"],
                    "type": "best_fields",
                    "operator": "or",
                },
            })

    if filters.get("segment"):
        seg = filters["segment"]
        terms = [seg] if isinstance(seg, str) else seg
        if terms:
            must.append({"terms": {"segment": terms}})
    if filters.get("health_min") is not None:
        must.append({"range": {"health_score": {"gte": filters["health_min"]}}})
    if filters.get("health_max") is not None:
        must.append({"range": {"health_score": {"lte": filters["health_max"]}}})

    if filters.get("renewal_within_days") is not None:
        days = int(filters["renewal_within_days"])
        now = datetime.utcnow().date().isoformat()
        end = (datetime.utcnow() + timedelta(days=days)).date().isoformat()
        must.append({"range": {"renewal_date": {"gte": now, "lte": end}}})

    if filters.get("arr_min") is not None or filters.get("arr_max") is not None:
        r: dict[str, Any] = {}
        if filters.get("arr_min") is not None:
            r["gte"] = float(filters["arr_min"])
        if filters.get("arr_max") is not None:
            r["lte"] = float(filters["arr_max"])
        if r:
            must.append({"range": {"arr": r}})

    has_neg = filters.get("has_negative_feedback")
    if has_neg is True:
        neg_customer_ids = _get_customers_with_negative_feedback(org_id)
        if neg_customer_ids:
            must.append({"terms": {"id": neg_customer_ids}})
        else:
            must.append({"terms": {"id": ["__none__"]}})
    elif has_neg is False:
        neg_customer_ids = _get_customers_with_negative_feedback(org_id)
        if neg_customer_ids:
            must.append({"bool": {"must_not": [{"terms": {"id": neg_customer_ids}}]}})

    query = {"bool": {"must": must}}
    sort_field = filters.get("sort_by", "company_name")
    if sort_field == "company_name":
        sort_field = "company_name.keyword"
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
    total_val = total.get("value", 0) if isinstance(total, dict) else total
    items = [h["_source"] for h in hits.get("hits", [])]

    if filters.get("include_feedback_stats") and items:
        stats = _get_feedback_stats_by_customer(org_id)
        for c in items:
            cid = c.get("id")
            s = stats.get(cid, {}) if cid else {}
            c["feedback_count"] = s.get("feedback_count", 0)
            c["negative_feedback_count"] = s.get("negative_feedback_count", 0)

    return (items, total_val)


def get_customer_feedback(
    org_id: str,
    customer_id: str,
    page: int = 1,
    page_size: int = 20,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated feedback for a customer. Reuses search logic with customer_id filter."""
    from app.services.search_service import search_feedback

    filters = dict(filters or {})
    filters["customer_id"] = customer_id
    return search_feedback(
        org_id=org_id,
        query="",
        filters=filters,
        sort_by="date",
        page=page,
        page_size=page_size,
    )


def get_customer_sentiment_trend(
    org_id: str,
    customer_id: str,
) -> dict[str, Any]:
    """
    Date histogram of avg sentiment_score for customer and product-wide.
    Returns { periods: [...], product_average: [...] }.
    """
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()

    # Customer sentiment over time (use week for finer granularity)
    cust_resp = es.search(
        index=idx,
        query={
            "bool": {
                "filter": [
                    {"term": {"org_id": org_id}},
                    {"term": {"customer_id": customer_id}},
                ]
            }
        },
        size=0,
        aggs={
            "by_period": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "week",
                    "format": "yyyy-MM-dd",
                },
                "aggs": {
                    "avg_sentiment": {"avg": {"field": "sentiment_score"}},
                    "count": {"value_count": {"field": "sentiment_score"}},
                },
            }
        },
    )
    cust_agg = cust_resp.get("aggregations", {}).get("by_period", {}).get("buckets", [])

    # Product-wide average for same buckets
    prod_resp = es.search(
        index=idx,
        query={"bool": {"filter": [{"term": {"org_id": org_id}}]}},
        size=0,
        aggs={
            "by_period": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "week",
                    "format": "yyyy-MM-dd",
                },
                "aggs": {"avg_sentiment": {"avg": {"field": "sentiment_score"}}},
            }
        },
    )
    prod_agg = prod_resp.get("aggregations", {}).get("by_period", {}).get("buckets", [])

    periods = [
        {
            "date": b.get("key_as_string", str(b.get("key", ""))),
            "avg_sentiment": round((b.get("avg_sentiment") or {}).get("value") or 0, 2),
            "count": (b.get("count") or {}).get("value", 0),
        }
        for b in cust_agg
    ]
    product_average = [
        {
            "date": b.get("key_as_string", str(b.get("key", ""))),
            "avg_sentiment": round((b.get("avg_sentiment") or {}).get("value") or 0, 2),
        }
        for b in prod_agg
    ]
    return {"periods": periods, "product_average": product_average}


def search_customers(
    org_id: str,
    q: str,
    size: int = 20,
) -> list[dict[str, Any]]:
    """Search customers by company name, account manager, industry. For autocomplete."""
    if not q or not str(q).strip():
        return []
    idx = customers_index(org_id)
    ensure_index_exists(idx, CUSTOMERS_MAPPING)
    es = get_es_client()
    resp = es.search(
        index=idx,
        query={
            "bool": {
                "must": [
                    {"term": {"org_id": org_id}},
                    {
                        "multi_match": {
                            "query": str(q).strip(),
                            "fields": ["company_name", "account_manager", "industry"],
                            "type": "best_fields",
                            "operator": "or",
                        },
                    },
                ]
            }
        },
        size=size,
        _source=["id", "company_name", "segment"],
    )
    hits = resp.get("hits", {}).get("hits", [])
    return [h["_source"] for h in hits]


def get_customer_count(org_id: str) -> int:
    """Get total customer count for org."""
    idx = customers_index(org_id)
    try:
        es = get_es_client()
        resp = es.count(index=idx, query={"term": {"org_id": org_id}})
        return resp.get("count", 0)
    except Exception:
        return 0
