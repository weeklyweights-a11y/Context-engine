"""Spec endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user
from app.schemas.spec import GenerateSpecRequest, UpdateSpecRequest
from app.services.spec_service import (
    delete_spec,
    generate_specs,
    get_spec,
    get_specs,
    regenerate_spec,
    update_spec,
)

router = APIRouter(prefix="/specs", tags=["specs"])


@router.post("/generate")
def create_spec_generate(
    body: GenerateSpecRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Generate specs for a topic. Returns spec summary for redirect."""
    org_id = current_user["org_id"]
    user_id = current_user["user_id"]
    try:
        doc = generate_specs(
            org_id,
            user_id,
            body.topic,
            body.product_area,
        )
        return {
            "data": {
                "id": doc["id"],
                "title": doc["title"],
                "status": doc["status"],
                "feedback_count": doc["feedback_count"],
                "customer_count": doc["customer_count"],
                "total_arr": doc.get("total_arr", 0),
                "created_at": doc["created_at"],
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
def list_specs(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_area: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    customer_id: str | None = Query(None),
):
    """List specs with pagination and filters."""
    org_id = current_user["org_id"]
    filters = {
        "product_area": product_area,
        "status": status_filter,
        "date_from": date_from,
        "date_to": date_to,
        "customer_id": customer_id,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    items, total = get_specs(org_id, page, page_size, filters)
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("/{spec_id}/regenerate")
def regenerate_spec_endpoint(
    spec_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Regenerate 4 docs from saved data_brief."""
    org_id = current_user["org_id"]
    user_id = current_user["user_id"]
    try:
        doc = regenerate_spec(org_id, spec_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": doc}


@router.get("/{spec_id}")
def get_spec_detail(
    spec_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get full spec with 4 documents."""
    org_id = current_user["org_id"]
    doc = get_spec(org_id, spec_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": doc}


@router.put("/{spec_id}")
def update_spec_endpoint(
    spec_id: str,
    body: UpdateSpecRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Update spec status or content."""
    org_id = current_user["org_id"]
    updates = body.model_dump(exclude_none=True)
    doc = update_spec(org_id, spec_id, updates)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": doc}


@router.delete("/{spec_id}")
def delete_spec_endpoint(
    spec_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete spec."""
    org_id = current_user["org_id"]
    ok = delete_spec(org_id, spec_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": {"deleted": True}}
