"""User endpoints (preferences, etc.)."""

from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.services.auth_service import get_preferences, update_preferences

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/preferences")
def get_user_preferences(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """Return dashboard preferences for current user."""
    return get_preferences(current_user["user_id"])


@router.put("/preferences")
def put_user_preferences(
    current_user: Annotated[dict, Depends(get_current_user)],
    body: Annotated[dict[str, Any], Body()],
) -> dict[str, Any]:
    """Update dashboard preferences. Body: { dashboard_preferences: { visible_widgets?, default_period? } }."""
    try:
        return update_preferences(current_user["user_id"], body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
