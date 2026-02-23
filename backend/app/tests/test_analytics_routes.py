"""Analytics route integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user


def _mock_current_user():
    return {"user_id": "u1", "org_id": "o1", "email": "test@x.com"}


@pytest.fixture
def client():
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    mock_es.count.return_value = {"count": 0}
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            with patch("app.services.elser_service.ensure_elser_deployed"):
                from app.main import app
                app.dependency_overrides[get_current_user] = _mock_current_user
                try:
                    yield TestClient(app)
                finally:
                    app.dependency_overrides.pop(get_current_user, None)


def test_get_analytics_summary_returns_200(client: TestClient):
    with patch("app.routers.analytics.get_summary") as mock_get:
        mock_get.return_value = {
            "total_feedback": 100,
            "avg_sentiment": -0.2,
            "active_issues": 4,
            "at_risk_customers": 3,
        }
        resp = client.get("/api/v1/analytics/summary?period=30d")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_feedback"] == 100


def test_get_analytics_volume_returns_200(client: TestClient):
    with patch("app.routers.analytics.get_volume") as mock_get:
        mock_get.return_value = {"periods": []}
        resp = client.get("/api/v1/analytics/volume?period=30d")
    assert resp.status_code == 200


def test_get_analytics_sentiment_returns_200(client: TestClient):
    with patch("app.routers.analytics.get_sentiment_breakdown") as mock_get:
        mock_get.return_value = {"breakdown": [], "total": 0}
        resp = client.get("/api/v1/analytics/sentiment?period=30d")
    assert resp.status_code == 200


def test_analytics_endpoints_require_auth():
    with patch("app.es_client.get_es_client") as mock_es:
        mock_es.return_value.info.return_value = {"cluster_name": "test"}
        from app.main import app
        c = TestClient(app)
    resp = c.get("/api/v1/analytics/summary")
    assert resp.status_code == 401


def test_get_config_returns_kibana_url(client: TestClient):
    resp = client.get("/api/v1/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "kibana_url" in data


def test_get_user_preferences_returns_200(client: TestClient):
    with patch("app.routers.user.get_preferences") as mock_get:
        mock_get.return_value = {
            "dashboard_preferences": {
                "visible_widgets": ["summary", "volume"],
                "default_period": "30d",
            }
        }
        resp = client.get("/api/v1/user/preferences")
    assert resp.status_code == 200
    assert "dashboard_preferences" in resp.json()


def test_put_user_preferences_saved(client: TestClient):
    with patch("app.routers.user.update_preferences") as mock_put:
        mock_put.return_value = {
            "dashboard_preferences": {
                "visible_widgets": ["summary"],
                "default_period": "7d",
            }
        }
        resp = client.put(
            "/api/v1/user/preferences",
            json={"dashboard_preferences": {"default_period": "7d"}},
        )
    assert resp.status_code == 200
    assert resp.json()["dashboard_preferences"]["default_period"] == "7d"
