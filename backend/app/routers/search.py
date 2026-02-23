"""Search endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.search import SearchFeedbackRequest
from app.services.search_service import search_feedback

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/feedback")
def search_feedback_endpoint(
    body: SearchFeedbackRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Hybrid semantic + keyword search on feedback."""
    org_id = current_user["org_id"]
    filters_dict = body.filters.model_dump(exclude_none=True) if body.filters else None
    items, total = search_feedback(
        org_id=org_id,
        query=body.query,
        filters=filters_dict,
        sort_by=body.sort_by,
        page=body.page,
        page_size=body.page_size,
    )
    return {
        "data": items,
        "pagination": {"page": body.page, "page_size": body.page_size, "total": total},
        "query": body.query,
    }
