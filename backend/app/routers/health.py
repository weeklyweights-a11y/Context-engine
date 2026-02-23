"""Health check endpoints."""

from fastapi import APIRouter

from app.es_client import check_es_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Return application and Elasticsearch health status."""
    return check_es_health()
