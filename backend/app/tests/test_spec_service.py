"""Spec service unit tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.spec_service import (
    delete_spec,
    gather_spec_data,
    get_spec,
    get_specs,
    regenerate_spec,
    save_spec,
    update_spec,
)


@pytest.fixture
def mock_es():
    """Mock ES client and services."""
    mock = MagicMock()
    mock.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}
    mock.get.return_value = None
    mock.index.return_value = {"result": "created"}
    mock.delete.return_value = {"result": "deleted"}
    return mock


@pytest.fixture
def mock_feedback_hits():
    """Sample feedback hits for gather_spec_data."""
    return [
        {
            "_source": {
                "id": "fb1",
                "text": "Checkout form loses state when navigating back",
                "customer_id": "c1",
                "customer_name": "Acme Inc",
                "sentiment": "negative",
                "created_at": "2026-01-15T12:00:00Z",
            }
        },
    ]


def test_gather_spec_data_empty_feedback_raises(mock_es):
    """gather_spec_data raises when no feedback matches topic."""
    with patch("app.services.spec_service.get_es_client", return_value=mock_es):
        with patch("app.services.spec_service.ensure_index_exists"):
            with patch("app.services.spec_service.get_customer", return_value={"arr": 1000}):
                mock_es.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}
                with pytest.raises(ValueError, match="Not enough feedback"):
                    gather_spec_data("org1", "checkout issues", None)


def test_gather_spec_data_returns_data_brief(mock_es, mock_feedback_hits):
    """gather_spec_data returns data_brief with feedback, customers, ARR."""
    mock_es.search.side_effect = [
        {"hits": {"hits": mock_feedback_hits, "total": {"value": 1}}},
    ]
    with patch("app.services.spec_service.get_es_client", return_value=mock_es):
        with patch("app.services.spec_service.ensure_index_exists"):
            with patch("app.services.spec_service.get_customer", return_value={"arr": 5000}):
                result = gather_spec_data("org1", "checkout", "checkout")
    assert result["topic"] == "checkout"
    assert result["product_area"] == "checkout"
    assert result["feedback_count"] >= 1
    assert "feedback_quotes" in result
    assert "feedback_ids" in result
    assert "customer_ids" in result
    assert "data_freshness_date" in result


def test_save_spec_and_get_spec(mock_es):
    """save_spec stores doc; get_spec retrieves it."""
    doc = {
        "id": "spec-1",
        "org_id": "org1",
        "title": "Test Spec",
        "status": "draft",
        "prd": "# PRD",
        "architecture": "# Arch",
        "rules": "# Rules",
        "plan": "# Plan",
    }
    with patch("app.services.spec_service.ensure_index_exists"):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            save_spec("org1", doc)
    mock_es.index.assert_called_once()

    mock_es.get.return_value = {"_source": doc}
    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        result = get_spec("org1", "spec-1")
    assert result is not None
    assert result["id"] == "spec-1"
    assert result["org_id"] == "org1"


def test_get_spec_wrong_org_returns_none(mock_es):
    """get_spec returns None when org_id doesn't match."""
    mock_es.get.return_value = {"_source": {"id": "s1", "org_id": "org-other"}}
    with patch("app.services.spec_service.get_es_client", return_value=mock_es):
        result = get_spec("org1", "s1")
    assert result is None


def test_get_specs_paginated(mock_es):
    """get_specs returns paginated list."""
    mock_es.search.return_value = {
        "hits": {
            "hits": [{"_source": {"id": "s1", "org_id": "o1", "title": "T1"}}],
            "total": {"value": 1},
        }
    }
    with patch("app.services.spec_service.get_es_client", return_value=mock_es):
        with patch("app.services.spec_service.ensure_specs_index_exists", return_value="o1-specs"):
            items, total = get_specs("org1", page=1, page_size=20)
    assert len(items) == 1
    assert total == 1


def test_update_spec(mock_es):
    """update_spec updates allowed fields."""
    existing = {
        "id": "s1",
        "org_id": "org1",
        "status": "draft",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    mock_es.get.return_value = {"_source": existing}
    with patch("app.services.es_service.get_es_client", return_value=mock_es):
        with patch("app.services.spec_service.specs_index", return_value="org1-specs"):
            result = update_spec("org1", "s1", {"status": "final"})
    assert result is not None
    assert result["status"] == "final"
    mock_es.index.assert_called()


def test_update_spec_not_found_returns_none(mock_es):
    """update_spec returns None when spec not found."""
    with patch("app.services.spec_service.get_spec", return_value=None):
        result = update_spec("org1", "missing", {"status": "final"})
    assert result is None


def test_delete_spec(mock_es):
    """delete_spec removes doc and returns True."""
    with patch("app.services.spec_service.get_spec", return_value={"id": "s1", "org_id": "org1"}):
        with patch("app.services.spec_service.specs_index", return_value="org1-specs"):
            with patch("app.services.spec_service.delete_document", return_value=True):
                result = delete_spec("org1", "s1")
    assert result is True


def test_delete_spec_not_found_returns_false():
    """delete_spec returns False when spec not found."""
    with patch("app.services.spec_service.get_spec", return_value=None):
        result = delete_spec("org1", "missing")
    assert result is False


def test_regenerate_spec(mock_es):
    """regenerate_spec calls LLM 4x and updates doc."""
    existing = {
        "id": "s1",
        "org_id": "org1",
        "data_brief": {"topic": "x", "feedback_quotes": []},
        "prd": "old",
    }
    with patch("app.services.spec_service.get_spec", return_value=existing):
        with patch("app.services.spec_service.get_product_context", return_value=MagicMock(product_name="P")):
            with patch("app.services.spec_service.generate_prd", return_value="# New PRD"):
                with patch("app.services.spec_service.generate_architecture", return_value="# New Arch"):
                    with patch("app.services.spec_service.generate_rules", return_value="# New Rules"):
                        with patch("app.services.spec_service.generate_plan", return_value="# New Plan"):
                            with patch("app.services.spec_service.index_document"):
                                result = regenerate_spec("org1", "s1", "user1")
    assert result is not None
    assert result["prd"] == "# New PRD"
    assert result["status"] == "draft"


def test_regenerate_spec_no_data_brief_raises():
    """regenerate_spec raises when data_brief missing."""
    with patch("app.services.spec_service.get_spec", return_value={"id": "s1", "org_id": "org1"}):
        with pytest.raises(ValueError, match="no data_brief"):
            regenerate_spec("org1", "s1", "user1")
