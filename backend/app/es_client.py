"""Elasticsearch singleton client."""

from typing import Any

from elasticsearch import Elasticsearch

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_client: Elasticsearch | None = None


def get_es_client() -> Elasticsearch:
    """Return singleton Elasticsearch client."""
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.elasticsearch_api_key:
            raise ValueError("ELASTICSEARCH_API_KEY must be set in .env")
        if settings.elasticsearch_url:
            _client = Elasticsearch(
                hosts=[settings.elasticsearch_url],
                api_key=settings.elasticsearch_api_key,
                request_timeout=300,
            )
        elif settings.elasticsearch_cloud_id:
            _client = Elasticsearch(
                cloud_id=settings.elasticsearch_cloud_id,
                api_key=settings.elasticsearch_api_key,
                request_timeout=300,
            )
        else:
            raise ValueError(
                "Set ELASTICSEARCH_URL (or ELASTICSEARCH_CLOUD_ID) and ELASTICSEARCH_API_KEY in .env"
            )
        logger.info("Elasticsearch client initialized")
    return _client


def check_es_health() -> dict[str, Any]:
    """
    Check Elasticsearch cluster health.

    Returns status, cluster name, version. Returns degraded status if ES unreachable.
    """
    try:
        client = get_es_client()
        info = client.info()
        cluster_name = info.get("cluster_name", "unknown")
        version = info.get("version", {}).get("number", "unknown")
        logger.info("ES health check OK: cluster=%s version=%s", cluster_name, version)
        return {
            "status": "healthy",
            "elasticsearch": {
                "status": "connected",
                "cluster_name": cluster_name,
                "version": version,
            },
            "version": "0.1.0",
        }
    except Exception as e:
        logger.error("ES health check failed: %s", str(e))
        return {
            "status": "degraded",
            "elasticsearch": {
                "status": "disconnected",
                "error": str(e),
            },
            "version": "0.1.0",
        }
