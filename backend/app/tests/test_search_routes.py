"""Search and related route integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user


def _mock_current_user():
    return {"user_id": "u1", "org_id": "o1", "email": "test@x.com"}


@pytest.fixture
def client():
    """Test client with mocked ES and auth."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    mock_es.count.return_value = {"count": 0}
    mock_es.get.side_effect = Exception("not found")
    mock_es.index.return_value = {"result": "created"}

    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.es_service.get_es_client", return_value=mock_es):
            with patch("app.services.elser_service.ensure_elser_deployed"):
                with patch("app.services.search_service.get_es_client", return_value=mock_es):
                    from app.main import app
                    app.dependency_overrides[get_current_user] = _mock_current_user
                    try:
                        yield TestClient(app)
                    finally:
                        app.dependency_overrides.pop(get_current_user, None)


def test_post_search_feedback_with_query_returns_200(client: TestClient):
    """POST /search/feedback with query returns 200 with results."""
    with patch("app.services.search_service.search_feedback") as mock_search:
        mock_search.return_value = (
            [{"id": "f1", "text": "payment problems", "sentiment": "negative"}],
            1,
        )
        resp = client.post(
            "/api/v1/search/feedback",
            json={"query": "payment problems", "page": 1, "page_size": 20},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data
    assert data["query"] == "payment problems"


def test_post_search_feedback_with_filters_returns_filtered(client: TestClient):
    """POST /search/feedback with filters returns filtered results."""
    with patch("app.routers.search.search_feedback") as mock_search:
        mock_search.return_value = ([], 0)
        resp = client.post(
            "/api/v1/search/feedback",
            json={
                "query": "",
                "filters": {"sentiment": ["negative"], "product_area": ["checkout"]},
                "page": 1,
                "page_size": 20,
            },
        )
    assert resp.status_code == 200
    mock_search.assert_called_once()
    call_filters = mock_search.call_args[1]["filters"]
    assert "sentiment" in call_filters
    assert "product_area" in call_filters


def test_post_search_feedback_without_auth_returns_401():
    """POST /search/feedback without auth returns 401."""
    mock_es = MagicMock()
    mock_es.info.return_value = {"cluster_name": "test", "version": {"number": "8.12"}}
    mock_es.indices.exists.return_value = True
    with patch("app.es_client.get_es_client", return_value=mock_es):
        with patch("app.services.elser_service.ensure_elser_deployed"):
            from app.main import app
            tc = TestClient(app)
            resp = tc.post(
                "/api/v1/search/feedback",
                json={"query": "test", "page": 1, "page_size": 20},
            )
    assert resp.status_code == 401


def test_get_feedback_similar_returns_similar_items(client: TestClient):
    """GET /feedback/{id}/similar returns similar items."""
    with patch("app.routers.feedback.get_feedback_item") as mock_get:
        mock_get.return_value = {"id": "f1", "text": "checkout broken"}
        with patch("app.routers.feedback.find_similar") as mock_similar:
            mock_similar.return_value = [
                {"id": "f2", "text": "payment failed"},
            ]
            resp = client.get("/api/v1/feedback/f1/similar")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["text"] == "payment failed"


def test_get_customers_id_feedback_returns_customer_feedback(client: TestClient):
    """GET /customers/{id}/feedback returns customer's feedback."""
    with patch("app.routers.customers.get_customer") as mock_get_cust:
        mock_get_cust.return_value = {"id": "c1", "company_name": "Acme"}
        with patch("app.routers.customers.get_customer_feedback") as mock_fb:
            mock_fb.return_value = ([{"id": "f1", "text": "Great"}], 1)
            resp = client.get("/api/v1/customers/c1/feedback")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data


def test_get_customers_id_sentiment_trend_returns_trend(client: TestClient):
    """GET /customers/{id}/sentiment-trend returns trend data."""
    with patch("app.routers.customers.get_customer") as mock_get_cust:
        mock_get_cust.return_value = {"id": "c1", "company_name": "Acme"}
        with patch("app.routers.customers.get_customer_sentiment_trend") as mock_trend:
            mock_trend.return_value = {
                "periods": [{"date": "2026-01", "avg_sentiment": -0.3, "count": 4}],
                "product_average": [{"date": "2026-01", "avg_sentiment": -0.1}],
            }
            resp = client.get("/api/v1/customers/c1/sentiment-trend")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "periods" in data["data"]
    assert "product_average" in data["data"]
