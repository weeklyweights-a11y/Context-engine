"""Analytics service for dashboard widgets — ES aggregations."""

from datetime import datetime, timedelta
from typing import Any

from app.es_client import get_es_client
from app.models.customer import CUSTOMERS_MAPPING, customers_index
from app.models.feedback import FEEDBACK_MAPPING, feedback_index
from app.services.es_service import ensure_index_exists
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _parse_period(period: str, from_date: str | None, to_date: str | None) -> tuple[str, str]:
    """Parse period into (from_iso, to_iso) date range. Returns (from_date, to_date)."""
    now = datetime.utcnow()
    to_dt = now
    if period == "custom" and from_date and to_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
            to_dt = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
            return (from_dt.strftime("%Y-%m-%d"), to_dt.strftime("%Y-%m-%d"))
        except (ValueError, TypeError):
            pass
    days = 30
    if period == "7d":
        days = 7
    elif period == "90d":
        days = 90
    from_dt = now - timedelta(days=days)
    return (from_dt.strftime("%Y-%m-%d"), to_dt.strftime("%Y-%m-%d"))


def _date_range_filter(from_date: str, to_date: str) -> dict[str, Any]:
    """Build ES range filter for created_at."""
    return {"range": {"created_at": {"gte": from_date, "lte": to_date + "T23:59:59.999Z"}}}


def _feedback_base_query(org_id: str, from_date: str, to_date: str) -> dict[str, Any]:
    """Base bool query for feedback index with org and date range."""
    return {
        "bool": {
            "filter": [
                {"term": {"org_id": org_id}},
                _date_range_filter(from_date, to_date),
            ]
        }
    }


def calculate_trend(current: float, previous: float) -> float | None:
    """Return % change: (current - previous) / previous * 100. None if previous is 0."""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


def get_summary(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Return 4 summary metrics with trends. At-risk = health_score < 50."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    prev_days = (
        (datetime.fromisoformat(to_dt) - datetime.fromisoformat(from_dt)).days or 1
    )
    prev_to = datetime.fromisoformat(from_dt) - timedelta(days=1)
    prev_from = prev_to - timedelta(days=prev_days)
    prev_from_str = prev_from.strftime("%Y-%m-%d")
    prev_to_str = prev_to.strftime("%Y-%m-%d")

    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)
    prev_base = {
        "bool": {
            "filter": [
                {"term": {"org_id": org_id}},
                _date_range_filter(prev_from_str, prev_to_str),
            ]
        }
    }

    # Current period aggregations
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={
            "total": {"value_count": {"field": "id"}},
            "avg_sentiment": {"avg": {"field": "sentiment_score"}},
            "active_issues": {
                "filter": {"range": {"sentiment_score": {"lt": -0.3}}},
                "aggs": {"areas": {"cardinality": {"field": "product_area"}}},
            },
        },
    )
    aggs = resp.get("aggregations", {})
    total = aggs.get("total", {}).get("value", 0) or 0
    avg_sent = aggs.get("avg_sentiment", {}).get("value")
    active_issues = (
        aggs.get("active_issues", {}).get("areas", {}).get("value", 0) or 0
    )

    # Previous period for trends
    prev_resp = es.search(
        index=idx,
        query=prev_base,
        size=0,
        aggs={
            "total": {"value_count": {"field": "id"}},
            "avg_sentiment": {"avg": {"field": "sentiment_score"}},
            "active_issues": {
                "filter": {"range": {"sentiment_score": {"lt": -0.3}}},
                "aggs": {"areas": {"cardinality": {"field": "product_area"}}},
            },
        },
    )
    prev_aggs = prev_resp.get("aggregations", {})
    prev_total = prev_aggs.get("total", {}).get("value", 0) or 0
    prev_avg_sent = prev_aggs.get("avg_sentiment", {}).get("value")
    prev_active = (
        prev_aggs.get("active_issues", {}).get("areas", {}).get("value", 0) or 0
    )

    # At-risk customers: health < 50
    cust_idx = customers_index(org_id)
    ensure_index_exists(cust_idx, CUSTOMERS_MAPPING)
    at_risk_resp = es.count(
        index=cust_idx,
        query={
            "bool": {
                "filter": [
                    {"term": {"org_id": org_id}},
                    {"range": {"health_score": {"lt": 50}}},
                ]
            }
        },
    )
    at_risk = at_risk_resp.get("count", 0) or 0

    return {
        "total_feedback": total,
        "total_feedback_trend": calculate_trend(float(total), float(prev_total)),
        "avg_sentiment": round(avg_sent, 2) if avg_sent is not None else 0.0,
        "avg_sentiment_trend": (
            calculate_trend(float(avg_sent or 0), float(prev_avg_sent or 0))
            if prev_avg_sent is not None or prev_total > 0
            else None
        ),
        "active_issues": active_issues,
        "active_issues_trend": calculate_trend(float(active_issues), float(prev_active)),
        "at_risk_customers": at_risk,
    }


def get_volume(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
    areas: list[str] | None = None,
) -> dict[str, Any]:
    """Return date histogram of feedback count. Optional terms sub-agg on product_area."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)

    date_histogram: dict[str, Any] = {
        "date_histogram": {
            "field": "created_at",
            "calendar_interval": "day",
            "min_doc_count": 0,
            "extended_bounds": {"min": from_dt, "max": to_dt},
        }
    }
    if areas:
        date_histogram["aggs"] = {
            "by_area": {
                "terms": {"field": "product_area", "include": areas},
                "aggs": {"count": {"value_count": {"field": "id"}}},
            }
        }
    else:
        date_histogram["aggs"] = {"count": {"value_count": {"field": "id"}}}

    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={"volume": date_histogram},
    )
    buckets = (
        resp.get("aggregations", {})
        .get("volume", {})
        .get("buckets", [])
    )
    result = []
    for b in buckets:
        key = b.get("key_as_string", b.get("key", ""))[:10]
        if areas:
            by_area = {
                sb["key"]: sb.get("count", {}).get("value", 0)
                for sb in b.get("by_area", {}).get("buckets", [])
            }
            total = sum(by_area.values())
            result.append({"date": key, "count": total, "by_area": by_area})
        else:
            result.append({"date": key, "count": b.get("count", {}).get("value", 0)})
    return {"periods": result}


def get_sentiment_breakdown(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Return sentiment breakdown: positive, negative, neutral counts and percentages."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={"sentiment": {"terms": {"field": "sentiment", "size": 10}}},
    )
    buckets = (
        resp.get("aggregations", {})
        .get("sentiment", {})
        .get("buckets", [])
    )
    total = sum(b["doc_count"] for b in buckets)
    result = []
    for b in buckets:
        count = b["doc_count"]
        pct = round(count / total * 100, 1) if total > 0 else 0
        result.append({"sentiment": b["key"], "count": count, "percentage": pct})
    return {"breakdown": result, "total": total}


def get_top_issues(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Return top issues by product_area with severity and growth. Reuses agent logic."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    prev_days = (
        (datetime.fromisoformat(to_dt) - datetime.fromisoformat(from_dt)).days or 1
    )
    prev_to = datetime.fromisoformat(from_dt) - timedelta(days=1)
    prev_from = prev_to - timedelta(days=prev_days)
    prev_from_str = prev_from.strftime("%Y-%m-%d")
    prev_to_str = prev_to.strftime("%Y-%m-%d")

    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = {
        "bool": {
            "filter": [
                {"term": {"org_id": org_id}},
                {"term": {"sentiment": "negative"}},
                _date_range_filter(from_dt, to_dt),
            ]
        }
    }
    prev_base = {
        "bool": {
            "filter": [
                {"term": {"org_id": org_id}},
                {"term": {"sentiment": "negative"}},
                _date_range_filter(prev_from_str, prev_to_str),
            ]
        }
    }
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={
            "by_area": {
                "terms": {"field": "product_area", "size": limit * 2},
                "aggs": {
                    "unique_customers": {"cardinality": {"field": "customer_id"}},
                    "avg_sentiment": {"avg": {"field": "sentiment_score"}},
                },
            }
        },
    )
    prev_resp = es.search(
        index=idx,
        query=prev_base,
        size=0,
        aggs={"by_area": {"terms": {"field": "product_area", "size": limit * 2}}},
    )
    prev_counts = {
        b["key"]: b["doc_count"]
        for b in prev_resp.get("aggregations", {})
        .get("by_area", {})
        .get("buckets", [])
    }
    buckets = (
        resp.get("aggregations", {})
        .get("by_area", {})
        .get("buckets", [])
    )
    issues = []
    for b in buckets[:limit]:
        area = b["key"] or "Unknown"
        count = b["doc_count"]
        prev_count = prev_counts.get(area, 0)
        growth = calculate_trend(float(count), float(prev_count)) if prev_count else None
        avg_sent = b.get("avg_sentiment", {}).get("value") or -0.5
        unique_customers = b.get("unique_customers", {}).get("value", 0)

        severity = "Stable"
        if avg_sent < -0.5 and count >= 10:
            severity = "Critical"
        elif growth is not None and growth > 15:
            severity = "Emerging"
        elif growth is not None and growth < -5:
            severity = "Improving"

        issues.append({
            "product_area": area,
            "issue_name": area,
            "feedback_count": count,
            "growth_rate": growth,
            "severity": severity,
            "affected_customers": unique_customers,
            "avg_sentiment": round(avg_sent, 2),
        })
    return {"issues": issues}


def get_area_breakdown(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Return product_area terms with count and avg sentiment."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={
            "by_area": {
                "terms": {"field": "product_area", "size": 50},
                "aggs": {"avg_sentiment": {"avg": {"field": "sentiment_score"}}},
            }
        },
    )
    buckets = (
        resp.get("aggregations", {})
        .get("by_area", {})
        .get("buckets", [])
    )
    result = []
    for b in buckets:
        avg_sent = b.get("avg_sentiment", {}).get("value")
        result.append({
            "product_area": b["key"] or "Unknown",
            "count": b["doc_count"],
            "avg_sentiment": round(avg_sent, 2) if avg_sent is not None else 0.0,
        })
    return {"areas": result}


def get_at_risk_customers(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Return customers with health < 50 OR significant negative feedback. Include negative_feedback_count."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    fb_idx = feedback_index(org_id)
    cust_idx = customers_index(org_id)
    ensure_index_exists(fb_idx, FEEDBACK_MAPPING)
    ensure_index_exists(cust_idx, CUSTOMERS_MAPPING)
    es = get_es_client()

    date_filter = _date_range_filter(from_dt, to_dt)
    neg_agg_resp = es.search(
        index=fb_idx,
        query={
            "bool": {
                "filter": [
                    {"term": {"org_id": org_id}},
                    {"term": {"sentiment": "negative"}},
                    {"exists": {"field": "customer_id"}},
                    date_filter,
                ]
            }
        },
        size=0,
        aggs={
            "by_customer": {
                "terms": {"field": "customer_id", "size": 10000},
            }
        },
    )
    neg_by_customer = {
        b["key"]: b["doc_count"]
        for b in neg_agg_resp.get("aggregations", {})
        .get("by_customer", {})
        .get("buckets", [])
    }

    should_clauses: list[dict[str, Any]] = [{"range": {"health_score": {"lt": 50}}}]
    neg_ids = [k for k in neg_by_customer.keys()][:500]
    if neg_ids:
        should_clauses.append({"terms": {"id": neg_ids}})
    resp = es.search(
        index=cust_idx,
        query={
            "bool": {
                "filter": [{"term": {"org_id": org_id}}],
                "should": should_clauses,
                "minimum_should_match": 1,
            }
        },
        size=limit,
        sort=[{"health_score": {"order": "asc", "missing": "_last"}}],
        _source=["id", "company_name", "arr", "renewal_date", "health_score"],
    )
    hits = resp.get("hits", {}).get("hits", [])
    customers = []
    for h in hits:
        src = h.get("_source", {})
        cid = src.get("id")
        neg_count = neg_by_customer.get(cid, 0)
        customers.append({
            "id": cid,
            "company_name": src.get("company_name", ""),
            "arr": src.get("arr"),
            "renewal_date": src.get("renewal_date"),
            "health_score": src.get("health_score"),
            "negative_feedback_count": neg_count,
        })
    return {"customers": customers}


def get_source_distribution(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Return terms aggregation on source field."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={"by_source": {"terms": {"field": "source", "size": 50}}},
    )
    buckets = (
        resp.get("aggregations", {})
        .get("by_source", {})
        .get("buckets", [])
    )
    total = sum(b["doc_count"] for b in buckets)
    result = []
    for b in buckets:
        count = b["doc_count"]
        pct = round(count / total * 100, 1) if total > 0 else 0
        result.append({"source": b["key"] or "unknown", "count": count, "percentage": pct})
    return {"breakdown": result, "total": total}


def get_segment_breakdown(
    org_id: str,
    period: str = "30d",
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Return terms aggregation on customer_segment, optionally by product_area."""
    from_dt, to_dt = _parse_period(period, from_date, to_date)
    idx = feedback_index(org_id)
    ensure_index_exists(idx, FEEDBACK_MAPPING)
    es = get_es_client()
    base = _feedback_base_query(org_id, from_dt, to_dt)
    resp = es.search(
        index=idx,
        query=base,
        size=0,
        aggs={
            "by_segment": {
                "terms": {"field": "customer_segment", "size": 20},
                "aggs": {
                    "by_area": {"terms": {"field": "product_area", "size": 20}},
                },
            }
        },
    )
    buckets = (
        resp.get("aggregations", {})
        .get("by_segment", {})
        .get("buckets", [])
    )
    result = []
    for b in buckets:
        by_area = [{"product_area": sb["key"], "count": sb["doc_count"]} for sb in b.get("by_area", {}).get("buckets", [])]
        result.append({
            "segment": b["key"] or "Unknown",
            "count": b["doc_count"],
            "by_area": by_area,
        })
    return {"segments": result}
