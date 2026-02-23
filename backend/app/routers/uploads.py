"""Upload history endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.services.upload_service import delete_upload, get_upload, get_uploads

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("")
def list_uploads(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """List upload history for current org."""
    org_id = current_user["org_id"]
    items = get_uploads(org_id)
    return {"data": items}


@router.get("/{upload_id}")
def get_upload_detail(
    upload_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get single upload record."""
    org_id = current_user["org_id"]
    doc = get_upload(org_id, upload_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return {"data": doc}


@router.delete("/{upload_id}")
def remove_upload(
    upload_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete an upload from history."""
    org_id = current_user["org_id"]
    if not delete_upload(org_id, upload_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return {"ok": True}
