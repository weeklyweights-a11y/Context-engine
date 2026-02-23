"""Feedback endpoints."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, status, UploadFile

from app.dependencies import get_current_user
from app.schemas.feedback import (
    FeedbackManualRequest,
    FeedbackUploadConfirmRequest,
)
from app.services.area_detection_service import detect_areas
from app.services.csv_service import (
    detect_feedback_columns,
    parse_csv_file,
    validate_row,
)
from app.services.feedback_service import (
    create_feedback_item,
    create_feedback_items_bulk,
    get_feedback_count,
    get_feedback_item,
    get_feedback_items,
)
from app.services.search_service import find_similar
from app.services.upload_service import (
    create_upload,
    get_upload,
    get_upload_temp_path,
    update_upload,
    save_uploaded_file,
    cleanup_upload_temp,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])

MAX_CSV_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload-csv")
async def upload_feedback_csv(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Upload CSV file, get column mapping and total rows."""
    org_id = current_user["org_id"]
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large (max 50MB)",
        )

    temp_path = save_uploaded_file(content, file.filename)
    try:
        with open(temp_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            rows = list(reader)
    except Exception as e:
        Path(temp_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV: {str(e)}",
        ) from e

    suggested = detect_feedback_columns(headers)
    upload_id = create_upload(
        org_id, "feedback", file.filename or "upload.csv", len(rows), temp_path
    )
    # Build preview: first 5 rows mapped to our fields
    preview_sample: list[dict] = []
    if rows and headers:
        our_to_csv = {k: v for k, v in suggested.items() if v}
        csv_to_our = {v: k for k, v in our_to_csv.items()}
        for row in rows[:5]:
            out: dict = {}
            for i, cell in enumerate(row):
                h = headers[i].strip() if i < len(headers) else ""
                if h and h in csv_to_our:
                    out[csv_to_our[h]] = (cell.strip() if cell else "")
            preview_sample.append(out)
    return {
        "data": {
            "upload_id": upload_id,
            "columns": headers,
            "suggested_mapping": suggested,
            "total_rows": len(rows),
            "preview_sample": preview_sample,
        }
    }


@router.post("/upload-csv/{upload_id}/confirm")
def confirm_feedback_mapping(
    upload_id: str,
    body: FeedbackUploadConfirmRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Confirm column mapping for feedback CSV import."""
    org_id = current_user["org_id"]
    upload = get_upload(org_id, upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    if not body.column_mapping.get("text"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text column is required",
        )
    update_upload(
        upload_id,
        column_mapping=body.column_mapping,
        default_source=body.default_source,
        use_today_for_date=body.use_today_for_date,
        auto_detect_areas=body.auto_detect_areas,
        auto_analyze_sentiment=body.auto_analyze_sentiment,
    )
    return {"data": {"upload_id": upload_id, "status": "confirmed"}}


@router.post("/upload-csv/{upload_id}/import")
def import_feedback_csv(
    upload_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Run feedback import from confirmed CSV."""
    org_id = current_user["org_id"]
    upload = get_upload(org_id, upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    temp_path = get_upload_temp_path(upload_id)
    if not temp_path or not Path(temp_path).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file no longer available",
        )

    mapping = upload.get("column_mapping") or {}
    if not mapping.get("text"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column mapping not confirmed",
        )

    update_upload(upload_id, status="processing")
    rows = parse_csv_file(temp_path, mapping, required_fields=["text"])
    use_today = upload.get("use_today_for_date", False)
    today_iso = datetime.utcnow().isoformat() + "Z" if use_today else None
    items = []
    failed = 0
    for row in rows:
        valid, _ = validate_row(row, ["text"])
        if not valid:
            failed += 1
            continue
        if row.get("date"):
            row["created_at"] = row["date"]
        elif use_today and today_iso:
            row["created_at"] = today_iso
        items.append(row)

    imported, bulk_failed, created_ids = create_feedback_items_bulk(
        org_id,
        items,
        ingestion_method="csv_upload",
        source_file=upload.get("filename"),
        default_source=upload.get("default_source"),
        auto_analyze_sentiment=upload.get("auto_analyze_sentiment", True),
    )
    failed += bulk_failed

    detected = []
    if items and upload.get("auto_detect_areas", True):
        texts = [r.get("text", "") for r in items if r.get("text")]
        detected = detect_areas(org_id, texts)

    update_upload(
        upload_id,
        status="completed",
        imported_rows=imported,
        failed_rows=failed,
        imported_ids=created_ids,
    )
    cleanup_upload_temp(upload_id)

    return {
        "data": {
            "upload_id": upload_id,
            "total_rows": upload.get("total_rows", 0),
            "imported_rows": imported,
            "failed_rows": failed,
            "detected_areas": detected,
        }
    }


@router.post("/manual")
def create_feedback_manual(
    body: FeedbackManualRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Add single feedback item manually."""
    org_id = current_user["org_id"]
    try:
        doc = create_feedback_item(org_id, body.model_dump(exclude_none=True))
        return {"data": doc}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("")
def list_feedback(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_type: str | None = Query(None),
    product_area: str | None = Query(None),
    sentiment: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    """List feedback with pagination and filters."""
    org_id = current_user["org_id"]
    filters = {
        "source_type": source_type,
        "product_area": product_area,
        "sentiment": sentiment,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
    items, total = get_feedback_items(org_id, page, page_size, filters)
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/count")
def feedback_count(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get total feedback count."""
    org_id = current_user["org_id"]
    count = get_feedback_count(org_id)
    return {"data": {"count": count}}


@router.get("/{item_id}/similar")
def get_similar_feedback(
    item_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Find feedback items similar to the given item."""
    org_id = current_user["org_id"]
    doc = get_feedback_item(org_id, item_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    items = find_similar(org_id, item_id, size=5)
    return {"data": items}


@router.get("/{item_id}")
def get_feedback(
    item_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get single feedback item."""
    org_id = current_user["org_id"]
    doc = get_feedback_item(org_id, item_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": doc}
