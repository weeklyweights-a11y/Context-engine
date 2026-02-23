"""Product service tests."""

from unittest.mock import patch

import pytest

from app.models.product import WIZARD_SECTIONS
from app.services.product_service import (
    delete_wizard_section,
    get_all_wizard_sections,
    get_onboarding_status,
    get_product_context,
    get_wizard_section,
    save_wizard_section,
)


def test_save_basics_stored():
    """Save basics section stores in ES."""
    with patch("app.services.product_service.ensure_index_exists") as mock_ensure:
        with patch(
            "app.services.product_service.get_document",
            return_value=None,
        ):
            with patch(
                "app.services.product_service.index_document"
            ) as mock_index:
                save_wizard_section(
                    "org-1",
                    "basics",
                    {"product_name": "Acme", "description": "B2B SaaS"},
                )
    mock_ensure.assert_called_once()
    mock_index.assert_called_once()
    call_args = mock_index.call_args
    assert call_args[0][0] == "org-1-product-context"
    assert call_args[0][1] == "basics"
    body = call_args[0][2]
    assert body["section"] == "basics"
    assert body["data"]["product_name"] == "Acme"


def test_save_areas_with_three_areas():
    """Save areas section with 3 areas stores all."""
    with patch("app.services.product_service.ensure_index_exists"):
        with patch("app.services.product_service.get_document", return_value=None):
                with patch(
                    "app.services.product_service.index_document"
                ) as mock_index:
                    save_wizard_section(
                        "org-1",
                        "areas",
                        {
                            "areas": [
                                {"name": "A1", "description": "D1"},
                                {"name": "A2", "description": "D2"},
                                {"name": "A3", "description": "D3"},
                            ]
                        },
                    )
    body = mock_index.call_args[0][2]
    areas = body["data"]["areas"]
    assert len(areas) == 3
    assert all("id" in a for a in areas)
    assert [a["name"] for a in areas] == ["A1", "A2", "A3"]


def test_get_wizard_section_returns_data():
    """Get wizard section returns correct data."""
    with patch("app.services.product_service.get_document") as mock_get:
        mock_get.return_value = {
            "section": "basics",
            "data": {"product_name": "Acme"},
            "updated_at": "2026-01-01T00:00:00Z",
        }
        result = get_wizard_section("org-1", "basics")
    assert result["section"] == "basics"
    assert result["data"]["product_name"] == "Acme"


def test_get_all_wizard_sections_returns_only_existing():
    """Get all wizard sections returns only sections that exist."""
    with patch("app.services.product_service.search_documents") as mock_search:
        mock_search.return_value = [
            {"section": "basics", "data": {"product_name": "Acme"}},
            {"section": "areas", "data": {"areas": []}},
        ]
        result = get_all_wizard_sections("org-1")
    assert set(result.keys()) == {"basics", "areas"}
    assert result["basics"]["data"]["product_name"] == "Acme"


def test_update_existing_section_upserts():
    """Update existing section updates, does not duplicate."""
    with patch("app.services.product_service.ensure_index_exists"):
        with patch("app.services.product_service.get_document") as mock_get:
            mock_get.return_value = {
                "section": "basics",
                "data": {"product_name": "Old"},
                "created_at": "2026-01-01T00:00:00Z",
            }
            with patch(
                "app.services.product_service.index_document"
            ) as mock_index:
                save_wizard_section(
                    "org-1",
                    "basics",
                    {"product_name": "Updated", "description": "New desc"},
                )
    call_args = mock_index.call_args
    assert call_args[0][1] == "basics"
    body = call_args[0][2]
    assert body["data"]["product_name"] == "Updated"
    assert body["data"]["description"] == "New desc"


def test_delete_section_removed():
    """Delete section removes it."""
    with patch("app.services.product_service.delete_document") as mock_del:
        mock_del.return_value = True
        result = delete_wizard_section("org-1", "basics")
    assert result is True


def test_get_product_context_flattens_all():
    """Get product context flattens all sections correctly."""
    with patch("app.services.product_service.get_all_wizard_sections") as mock_get:
        mock_get.return_value = {
            "basics": {
                "data": {
                    "product_name": "Acme",
                    "description": "B2B",
                    "industry": "SaaS",
                }
            },
            "areas": {"data": {"areas": [{"name": "Checkout", "id": "a1"}]}},
            "goals": {"data": {"goals": [{"title": "Reduce churn", "id": "g1"}]}},
        }
        ctx = get_product_context("org-1")
    assert ctx.product_name == "Acme"
    assert ctx.description == "B2B"
    assert ctx.industry == "SaaS"
    assert len(ctx.areas) == 1
    assert ctx.areas[0]["name"] == "Checkout"
    assert len(ctx.goals) == 1
    assert ctx.goals[0]["title"] == "Reduce churn"


def test_get_product_context_missing_sections_no_error():
    """Get product context with missing sections returns partial data (no error)."""
    with patch("app.services.product_service.get_all_wizard_sections") as mock_get:
        mock_get.return_value = {
            "basics": {"data": {"product_name": "Acme"}},
        }
        ctx = get_product_context("org-1")
    assert ctx.product_name == "Acme"
    assert ctx.areas == []
    assert ctx.goals == []


def test_product_context_org_isolation():
    """Product context only returns data for current org."""
    with patch("app.services.product_service.get_all_wizard_sections") as mock_get:
        mock_get.return_value = {
            "basics": {"data": {"product_name": "Org1 Product"}},
        }
        ctx = get_product_context("org-1")
    mock_get.assert_called_once_with("org-1")
    assert ctx.product_name == "Org1 Product"


def test_get_onboarding_status():
    """Get onboarding status returns completed flag and section count."""
    with patch("app.services.product_service.get_document") as mock_get_org:
        mock_get_org.return_value = {"onboarding_completed": False}
        with patch(
            "app.services.product_service.get_all_wizard_sections"
        ) as mock_sections:
            mock_sections.return_value = {"basics": {}, "areas": {}}
            status = get_onboarding_status("org-1")
    assert status["completed"] is False
    assert status["completed_sections"] == ["basics", "areas"]
    assert status["total_sections"] == 8
