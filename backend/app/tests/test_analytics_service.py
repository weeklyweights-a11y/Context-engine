"""Analytics service tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.analytics_service import (
    calculate_trend,
    get_area_breakdown,
    get_at_risk_customers,
    get_segment_breakdown,
    get_sentiment_breakdown,
    get_source_distribution,
    get_summary,
    get_top_issues,
    get_volume,
)


def test_calculate_trend_positive():
    assert calculate_trend(120, 100) == 20.0


def test_calculate_trend_negative():
    assert calculate_trend(80, 100) == -20.0


def test_calculate_trend_zero_previous_returns_none():
    assert calculate_trend(100, 0) is None


def test_get_summary_returns_four_metrics():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "total": {"value": 100},
            "avg_sentiment": {"value": -0.2},
            "active_issues": {"areas": {"value": 4}},
        }
    }
    mock_es.count.return_value = {"count": 3}
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_summary("o1", "30d")
    assert "total_feedback" in result
    assert "avg_sentiment" in result
    assert "active_issues" in result
    assert "at_risk_customers" in result


def test_get_volume_returns_periods():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "volume": {
                "buckets": [
                    {"key_as_string": "2026-01-01", "count": {"value": 10}},
                    {"key_as_string": "2026-01-02", "count": {"value": 15}},
                ]
            }
        }
    }
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_volume("o1", "30d")
    assert "periods" in result
    assert len(result["periods"]) == 2


def test_get_sentiment_breakdown_sums_to_100():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "sentiment": {
                "buckets": [
                    {"key": "positive", "doc_count": 40},
                    {"key": "negative", "doc_count": 30},
                    {"key": "neutral", "doc_count": 30},
                ]
            }
        }
    }
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_sentiment_breakdown("o1", "30d")
    assert result["total"] == 100
    breakdown = {b["sentiment"]: b["percentage"] for b in result["breakdown"]}
    assert abs(sum(breakdown.values()) - 100) < 1


def test_get_top_issues_returns_ranked_list():
    mock_es = MagicMock()
    mock_es.search.side_effect = [
        {
            "aggregations": {
                "by_area": {
                    "buckets": [
                        {
                            "key": "checkout",
                            "doc_count": 50,
                            "avg_sentiment": {"value": -0.6},
                            "unique_customers": {"value": 12},
                        }
                    ]
                }
            }
        },
        {"aggregations": {"by_area": {"buckets": [{"key": "checkout", "doc_count": 40}]}}},
    ]
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_top_issues("o1", "30d", limit=5)
    assert "issues" in result


def test_get_area_breakdown_returns_areas():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "by_area": {
                "buckets": [
                    {"key": "checkout", "doc_count": 100, "avg_sentiment": {"value": -0.3}},
                ]
            }
        }
    }
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_area_breakdown("o1", "30d")
    assert "areas" in result


def test_get_at_risk_returns_customers():
    mock_es = MagicMock()
    mock_es.search.side_effect = [
        {"aggregations": {"by_customer": {"buckets": []}}},
        {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": "c1",
                            "company_name": "Acme",
                            "arr": 50000,
                            "renewal_date": "2026-06-01",
                            "health_score": 35,
                        }
                    }
                ]
            }
        },
    ]
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_at_risk_customers("o1", "30d", limit=5)
    assert "customers" in result


def test_get_source_distribution():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "by_source": {
                "buckets": [{"key": "support_ticket", "doc_count": 50}]
            }
        }
    }
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_source_distribution("o1", "30d")
    assert "breakdown" in result
    assert "total" in result


def test_get_segment_breakdown():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "by_segment": {
                "buckets": [
                    {"key": "enterprise", "doc_count": 30, "by_area": {"buckets": []}},
                ]
            }
        }
    }
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_segment_breakdown("o1", "30d")
    assert "segments" in result


def test_get_summary_empty_data_returns_zeros():
    mock_es = MagicMock()
    mock_es.search.return_value = {
        "aggregations": {
            "total": {"value": 0},
            "avg_sentiment": {"value": None},
            "active_issues": {"areas": {"value": 0}},
        }
    }
    mock_es.count.return_value = {"count": 0}
    with patch("app.services.analytics_service.get_es_client", return_value=mock_es):
        with patch("app.services.analytics_service.ensure_index_exists"):
            result = get_summary("o1", "30d")
    assert result["total_feedback"] == 0
    assert result["at_risk_customers"] == 0
