"""Similar feedback endpoint tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.search_service import find_similar


def test_find_similar_returns_items_excluding_source():
    """find_similar returns similar items and excludes source."""
    with patch("app.services.search_service.get_feedback_item") as mock_get:
        mock_get.return_value = {"id": "f1", "text": "checkout is broken"}
        with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
            with patch("app.services.search_service.is_elser_available", return_value=False):
                with patch("app.services.search_service.get_es_client") as mock_es_cls:
                    mock_es = MagicMock()
                    mock_es.search.return_value = {
                        "hits": {
                            "hits": [
                                {"_source": {"id": "f2", "text": "payment failed"}},
                                {"_source": {"id": "f3", "text": "billing issue"}},
                            ],
                        }
                    }
                    mock_es_cls.return_value = mock_es

                    items = find_similar("o1", "f1", size=5)
                    assert len(items) == 2
                    assert all(i["id"] != "f1" for i in items)


def test_find_similar_excludes_source_from_results():
    """find_similar explicitly excludes source item from results."""
    with patch("app.services.search_service.get_feedback_item") as mock_get:
        mock_get.return_value = {"id": "f1", "text": "checkout broken"}
        with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
            with patch("app.services.search_service.is_elser_available", return_value=False):
                with patch("app.services.search_service.get_es_client") as mock_es_cls:
                    mock_es = MagicMock()
                    # ES could return source in hits; find_similar filters it out
                    mock_es.search.return_value = {
                        "hits": {
                            "hits": [
                                {"_source": {"id": "f1", "text": "checkout broken"}},
                                {"_source": {"id": "f2", "text": "other"}},
                            ],
                        }
                    }
                    mock_es_cls.return_value = mock_es

                    items = find_similar("o1", "f1", size=5)
                    assert len(items) == 1
                    assert items[0]["id"] == "f2"


def test_find_similar_returns_max_size():
    """find_similar returns at most size items."""
    with patch("app.services.search_service.get_feedback_item") as mock_get:
        mock_get.return_value = {"id": "f1", "text": "x"}
        with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
            with patch("app.services.search_service.is_elser_available", return_value=False):
                with patch("app.services.search_service.get_es_client") as mock_es_cls:
                    mock_es = MagicMock()
                    hits = [{"_source": {"id": f"f{i}", "text": f"text{i}"}} for i in range(10)]
                    mock_es.search.return_value = {"hits": {"hits": hits}}
                    mock_es_cls.return_value = mock_es

                    items = find_similar("o1", "f1", size=5)
                    assert len(items) <= 5


def test_find_similar_isolates_by_org():
    """find_similar filters by org_id."""
    with patch("app.services.search_service.get_feedback_item") as mock_get:
        mock_get.return_value = {"id": "f1", "text": "x"}
        with patch("app.services.search_service._ensure_feedback_index", return_value="o1-feedback"):
            with patch("app.services.search_service.is_elser_available", return_value=False):
                with patch("app.services.search_service.get_es_client") as mock_es_cls:
                    mock_es = MagicMock()
                    mock_es.search.return_value = {"hits": {"hits": []}}
                    mock_es_cls.return_value = mock_es

                    find_similar("o1", "f1", size=5)
                    call_query = mock_es.search.call_args[1]["query"]
                    assert "o1" in str(call_query)


def test_find_similar_returns_empty_when_source_not_found():
    """find_similar returns [] when source feedback not found."""
    with patch("app.services.search_service.get_feedback_item", return_value=None):
        items = find_similar("o1", "unknown", size=5)
        assert items == []
