"""Customer profile service tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.customer_service import (
    get_customer_feedback,
    get_customer_sentiment_trend,
)


def test_get_customer_feedback_returns_only_that_customer():
    """get_customer_feedback returns only that customer's items."""
    with patch("app.services.search_service.search_feedback") as mock_search:
        mock_search.return_value = (
            [{"id": "f1", "customer_id": "c1", "text": "Great"}],
            1,
        )
        items, total = get_customer_feedback("o1", "c1", page=1, page_size=20)
        assert len(items) == 1
        assert items[0]["customer_id"] == "c1"
        mock_search.assert_called_once()
        call_filters = mock_search.call_args[1]["filters"]
        assert call_filters["customer_id"] == "c1"


def test_get_customer_sentiment_trend_returns_aggregated_data():
    """get_customer_sentiment_trend returns periods and product_average."""
    with patch("app.services.customer_service.get_es_client") as mock_es_cls:
        mock_es = MagicMock()
        mock_es.search.side_effect = [
            {
                "aggregations": {
                    "by_period": {
                        "buckets": [
                            {
                                "key_as_string": "2026-01",
                                "avg_sentiment": {"value": -0.3},
                                "count": {"value": 4},
                            },
                        ],
                    },
                },
            },
            {
                "aggregations": {
                    "by_period": {
                        "buckets": [
                            {
                                "key_as_string": "2026-01",
                                "avg_sentiment": {"value": -0.1},
                            },
                        ],
                    },
                },
            },
        ]
        mock_es_cls.return_value = mock_es

        with patch("app.services.customer_service.ensure_index_exists"):
            data = get_customer_sentiment_trend("o1", "c1")

        assert "periods" in data
        assert "product_average" in data
        assert len(data["periods"]) == 1
        assert data["periods"][0]["date"] == "2026-01"
        assert data["periods"][0]["avg_sentiment"] == -0.3
        assert data["periods"][0]["count"] == 4


def test_get_customer_sentiment_trend_includes_product_average():
    """get_customer_sentiment_trend includes product average overlay."""
    with patch("app.services.customer_service.get_es_client") as mock_es_cls:
        mock_es = MagicMock()
        mock_es.search.side_effect = [
            {"aggregations": {"by_period": {"buckets": []}}},
            {
                "aggregations": {
                    "by_period": {
                        "buckets": [
                            {"key_as_string": "2026-01", "avg_sentiment": {"value": -0.15}},
                        ],
                    },
                },
            },
        ]
        mock_es_cls.return_value = mock_es

        with patch("app.services.customer_service.ensure_index_exists"):
            data = get_customer_sentiment_trend("o1", "c1")

        assert len(data["product_average"]) == 1
        assert data["product_average"][0]["date"] == "2026-01"
        assert data["product_average"][0]["avg_sentiment"] == -0.15


def test_get_customer_feedback_isolates_by_org():
    """get_customer_feedback passes org_id to search."""
    with patch("app.services.search_service.search_feedback") as mock_search:
        mock_search.return_value = ([], 0)
        get_customer_feedback("o1", "c1")
        mock_search.assert_called_once()
        assert mock_search.call_args.kwargs["org_id"] == "o1"
