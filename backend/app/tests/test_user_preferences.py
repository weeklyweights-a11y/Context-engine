"""User preferences tests."""

from unittest.mock import patch

import pytest

from app.services.auth_service import get_preferences, update_preferences


def test_get_preferences_returns_defaults_when_user_not_found():
    with patch("app.services.auth_service.get_user_by_id", return_value=None):
        result = get_preferences("unknown-user")
    assert "dashboard_preferences" in result
    assert "visible_widgets" in result["dashboard_preferences"]
    assert "default_period" in result["dashboard_preferences"]
    assert "summary" in result["dashboard_preferences"]["visible_widgets"]


def test_get_preferences_returns_stored():
    with patch("app.services.auth_service.get_user_by_id") as mock_get:
        mock_get.return_value = {
            "user_id": "u1",
            "dashboard_preferences": {
                "visible_widgets": ["summary", "volume"],
                "default_period": "7d",
            },
        }
        result = get_preferences("u1")
    assert result["dashboard_preferences"]["visible_widgets"] == ["summary", "volume"]
    assert result["dashboard_preferences"]["default_period"] == "7d"


def test_update_preferences_merges_and_returns():
    with patch("app.services.auth_service.get_preferences") as mock_get:
        mock_get.return_value = {
            "dashboard_preferences": {
                "visible_widgets": ["summary", "volume"],
                "default_period": "30d",
            }
        }
        with patch("app.services.auth_service.update_document"):
            result = update_preferences("u1", {
                "dashboard_preferences": {"default_period": "7d"}
            })
    assert result["dashboard_preferences"]["default_period"] == "7d"
    assert "visible_widgets" in result["dashboard_preferences"]
