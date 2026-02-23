"""Config endpoint for frontend (e.g. Kibana URL)."""

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(tags=["config"])


@router.get("/config")
def get_config(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Return client config (e.g. kibana_url). Auth required."""
    settings = get_settings()
    return {"kibana_url": settings.kibana_url or ""}
