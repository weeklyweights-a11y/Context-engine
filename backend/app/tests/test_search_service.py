"""Search service tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.search_service import (
    build_filter_clauses,
    search_feedback,
    find_similar,
)


def test_build_filter_clauses_empty():
    """build_filter_clauses with no filters returns only org filter context (caller adds org)."""
    clauses = build_filter_clauses(None)
    assert clauses == []


def test_build_filter_clauses_product_area():
    """build_filter_clauses with product_area adds terms clause."""
    clauses = build_filter_clauses({"product_area": ["checkout", "billing"]})
    assert len(clauses) == 1
    assert clauses[0] == {"terms": {"product_area": ["checkout", "billing"]}}


def test_build_filter_clauses_sentiment():
    """build_filter_clauses with sentiment adds terms clause."""
    clauses = build_filter_clauses({"sentiment": ["negative"]})
    assert clauses[0] == {"terms": {"sentiment": ["negative"]}}


def test_build_filter_clauses_date_range():
    """build_filter_clauses with date_from/date_to adds range clause."""
    clauses = build_filter_clauses({
        "date_from": "2026-01-01",
        "date_to": "2026-02-20",
    })
    assert len(clauses) == 1
    assert clauses[0]["range"]["created_at"]["gte"] == "2026-01-01"
    assert clauses[0]["range"]["created_at"]["lte"] == "2026-02-20"


def test_build_filter_clauses_has_customer():
    """build_filter_clauses with has_customer adds exists clause."""
    clauses = build_filter_clauses({"has_customer": True})
    assert clauses[0] == {"exists": {"field": "customer_id"}}


def test_build_filter_clauses_customer_id():
    """build_filter_clauses with customer_id adds term clause."""
    clauses = build_filter_clauses({"customer_id": "c1"})
    assert clauses[0] == {"term": {"customer_id": "c1"}}


def test_search_feedback_empty_query_returns_match_all():
    """search_feedback with empty query uses match_all and sort by created_at."""
    with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
        with patch("app.services.search_service.get_es_client") as mock_es_cls:
            mock_es = MagicMock()
            mock_es.search.return_value = {"hits": {"total": {"value": 10}, "hits": []}}
            mock_es_cls.return_value = mock_es

            items, total = search_feedback("o1", "", None, "relevance", 1, 20)
            assert items == []
            assert total == 10
            call_query = mock_es.search.call_args[1]["query"]
            assert "match_all" in str(call_query)


def test_search_feedback_with_query_calls_es():
    """search_feedback with query executes search and returns results."""
    with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
        with patch("app.services.search_service.is_elser_available", return_value=False):
            with patch("app.services.search_service.get_es_client") as mock_es_cls:
                mock_es = MagicMock()
                mock_es.search.return_value = {
                    "hits": {
                        "total": {"value": 2},
                        "hits": [
                            {"_source": {"id": "f1", "text": "checkout broken"}},
                            {"_source": {"id": "f2", "text": "payment failed"}},
                        ],
                    }
                }
                mock_es_cls.return_value = mock_es

                items, total = search_feedback("o1", "payment", None, "relevance", 1, 20)
                assert len(items) == 2
                assert total == 2
                assert items[0]["text"] == "checkout broken"


def test_search_feedback_isolates_by_org():
    """search_feedback filter includes org_id."""
    with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
        with patch("app.services.search_service.is_elser_available", return_value=False):
            with patch("app.services.search_service.get_es_client") as mock_es_cls:
                mock_es = MagicMock()
                mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
                mock_es_cls.return_value = mock_es

                search_feedback("o1", "test", None, "relevance", 1, 20)
                call_query = mock_es.search.call_args[1]["query"]
                assert "o1" in str(call_query)
