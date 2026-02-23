"""Feedback service tests."""

from unittest.mock import patch

import pytest

from app.services.feedback_service import (
    create_feedback_item,
    create_feedback_items_bulk,
    get_feedback_item,
    get_feedback_items,
    get_feedback_count,
)


def test_create_feedback_item():
    """create_feedback_item stores feedback with sentiment and customer resolution."""
    with patch("app.services.feedback_service._ensure_feedback_index", return_value="o1-feedback"):
        with patch("app.services.feedback_service.index_document") as mock_idx:
            with patch("app.services.feedback_service.analyze_sentiment", return_value=("positive", 0.8)):
                with patch("app.services.feedback_service._resolve_customer", return_value={
                    "customer_id": None, "customer_name": "Acme", "customer_segment": None,
                }):
                    doc = create_feedback_item("o1", {"text": "Great product!"})
                    assert doc["text"] == "Great product!"
                    assert doc["sentiment"] == "positive"
                    mock_idx.assert_called_once()


def test_create_feedback_item_requires_text():
    """create_feedback_item raises ValueError if text is empty."""
    with patch("app.services.feedback_service._ensure_feedback_index", return_value="o1-feedback"):
        with pytest.raises(ValueError, match="Feedback text is required"):
            create_feedback_item("o1", {"text": ""})
        with pytest.raises(ValueError, match="Feedback text is required"):
            create_feedback_item("o1", {})


def test_create_feedback_items_bulk():
    """create_feedback_items_bulk returns (imported, failed)."""
    with patch("app.services.feedback_service._ensure_feedback_index", return_value="o1-feedback"):
        with patch("app.services.feedback_service.analyze_sentiment", return_value=("neutral", 0)):
            with patch("app.services.feedback_service._resolve_customer", return_value={
                "customer_id": None, "customer_name": None, "customer_segment": None,
            }):
                with patch("app.services.feedback_service.bulk_index_documents", return_value=(3, 0)):
                    imported, failed, created_ids = create_feedback_items_bulk(
                        "o1",
                        [
                            {"text": "A"},
                            {"text": "B"},
                            {"text": "C"},
                        ],
                    )
                    assert imported == 3
                    assert failed == 0
                    assert len(created_ids) == 3


def test_get_feedback_item():
    """get_feedback_item returns doc when found and org matches."""
    with patch("app.services.feedback_service.get_document") as mock_get:
        mock_get.return_value = {"id": "f1", "org_id": "o1", "text": "Hello"}
        doc = get_feedback_item("o1", "f1")
        assert doc is not None
        assert doc["text"] == "Hello"


def test_get_feedback_item_returns_none_wrong_org():
    """get_feedback_item returns None when org does not match."""
    with patch("app.services.feedback_service.get_document") as mock_get:
        mock_get.return_value = {"id": "f1", "org_id": "o2"}
        doc = get_feedback_item("o1", "f1")
        assert doc is None


def test_get_feedback_count():
    """get_feedback_count returns count from ES."""
    with patch("app.services.feedback_service.get_es_client") as mock_es:
        mock_es.return_value.count.return_value = {"count": 42}
        count = get_feedback_count("o1")
        assert count == 42
