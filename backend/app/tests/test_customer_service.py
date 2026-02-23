"""Customer service tests."""

from unittest.mock import patch

import pytest

from app.services.customer_service import (
    create_customer,
    create_customers_bulk,
    get_customer,
    get_customer_count,
)


def test_create_customer():
    """create_customer stores customer and returns doc."""
    with patch("app.services.customer_service.ensure_index_exists"):
        with patch("app.services.customer_service.index_document") as mock_idx:
            doc = create_customer("o1", {"company_name": "Acme", "segment": "Enterprise"})
            assert doc["company_name"] == "Acme"
            mock_idx.assert_called_once()


def test_create_customers_bulk():
    """create_customers_bulk returns (imported, failed, created_ids)."""
    with patch("app.services.customer_service.ensure_index_exists"):
        with patch("app.services.customer_service.bulk_index_documents", return_value=(2, 0)):
            imported, failed, created_ids = create_customers_bulk(
                "o1",
                [
                    {"company_name": "Acme"},
                    {"company_name": "Beta"},
                ],
            )
            assert imported == 2
            assert failed == 0
            assert len(created_ids) == 2


def test_create_customers_bulk_skips_empty_company():
    """create_customers_bulk skips rows without company_name."""
    with patch("app.services.customer_service.ensure_index_exists"):
        with patch("app.services.customer_service.bulk_index_documents", return_value=(1, 0)) as mock_bulk:
            imported, failed, _ = create_customers_bulk(
                "o1",
                [{"company_name": "Acme"}, {"company_name": ""}, {"company_name": "  "}],
            )
            assert imported == 1
            assert failed == 2


def test_get_customer():
    """get_customer returns doc when found."""
    with patch("app.services.customer_service.get_document") as mock_get:
        mock_get.return_value = {"id": "c1", "org_id": "o1", "company_name": "Acme"}
        doc = get_customer("o1", "c1")
        assert doc is not None
        assert doc["company_name"] == "Acme"


def test_get_customer_returns_none_wrong_org():
    """get_customer returns None when org does not match."""
    with patch("app.services.customer_service.get_document") as mock_get:
        mock_get.return_value = {"id": "c1", "org_id": "o2"}
        doc = get_customer("o1", "c1")
        assert doc is None


def test_get_customer_count():
    """get_customer_count returns count from ES."""
    with patch("app.services.customer_service.get_es_client") as mock_es:
        mock_es.return_value.count.return_value = {"count": 10}
        count = get_customer_count("o1")
        assert count == 10
