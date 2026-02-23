"""Customer endpoints."""

import csv
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, status, UploadFile

from app.dependencies import get_current_user
from app.schemas.customer import CustomerManualRequest, CustomerUploadConfirmRequest
from app.services.csv_service import (
    detect_customer_columns,
    parse_csv_file,
    validate_row,
)
from app.services.customer_service import (
    create_customer,
    create_customers_bulk,
    get_customer,
    get_customer_count,
    get_customer_feedback,
    get_customers,
    get_customer_sentiment_trend,
    search_customers,
)
from app.services.upload_service import (
    create_upload,
    get_upload,
    get_upload_temp_path,
    update_upload,
    save_uploaded_file,
    cleanup_upload_temp,
)

router = APIRouter(prefix="/customers", tags=["customers"])

MAX_CSV_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload-csv")
async def upload_customers_csv(
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

    suggested = detect_customer_columns(headers)
    upload_id = create_upload(
        org_id, "customers", file.filename or "upload.csv", len(rows), temp_path
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
def confirm_customer_mapping(
    upload_id: str,
    body: CustomerUploadConfirmRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Confirm column mapping for customer CSV import."""
    org_id = current_user["org_id"]
    upload = get_upload(org_id, upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    mapping = body.column_mapping
    if not mapping.get("company_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name column is required",
        )
    update_upload(upload_id, column_mapping=mapping)
    return {"data": {"upload_id": upload_id, "status": "confirmed"}}


@router.post("/upload-csv/{upload_id}/import")
def import_customers_csv(
    upload_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Run customer import from confirmed CSV."""
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
    if not mapping.get("company_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Column mapping not confirmed",
        )

    update_upload(upload_id, status="processing")
    rows = parse_csv_file(temp_path, mapping, required_fields=["company_name"])
    items = []
    failed = 0
    for row in rows:
        valid, _ = validate_row(row, ["company_name"])
        if not valid:
            failed += 1
            continue
        items.append(row)

    imported, bulk_failed, created_ids = create_customers_bulk(org_id, items)
    failed += bulk_failed

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
        }
    }


@router.post("/manual")
def create_customer_manual(
    body: CustomerManualRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Add single customer manually."""
    org_id = current_user["org_id"]
    doc = create_customer(org_id, body.model_dump(exclude_none=True))
    return {"data": doc}


@router.get("")
def list_customers(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    segment: str | None = Query(None),
    health_min: int | None = Query(None),
    health_max: int | None = Query(None),
    renewal_within: int | None = Query(None, description="Renewal within N days"),
    arr_min: float | None = Query(None),
    arr_max: float | None = Query(None),
    has_negative_feedback: bool | None = Query(None),
    include_feedback_stats: bool = Query(False),
    sort_by: str = Query("company_name"),
    sort_order: str = Query("asc"),
):
    """List customers with pagination and filters."""
    org_id = current_user["org_id"]
    filters = {
        "search": search,
        "segment": segment,
        "health_min": health_min,
        "health_max": health_max,
        "renewal_within_days": renewal_within,
        "arr_min": arr_min,
        "arr_max": arr_max,
        "has_negative_feedback": has_negative_feedback,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    if include_feedback_stats:
        filters["include_feedback_stats"] = True
    items, total = get_customers(org_id, page, page_size, filters)
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/search")
def customers_search(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    q: str = Query(""),
):
    """Search customers for autocomplete (e.g. Feedback page customer filter)."""
    org_id = current_user["org_id"]
    items = search_customers(org_id, q, size=20)
    return {"data": items}


@router.get("/count")
def customers_count(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get total customer count."""
    org_id = current_user["org_id"]
    count = get_customer_count(org_id)
    return {"data": {"count": count}}


@router.get("/{customer_id}/feedback")
def get_customer_feedback_endpoint(
    customer_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get feedback for a customer with pagination."""
    org_id = current_user["org_id"]
    doc = get_customer(org_id, customer_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    items, total = get_customer_feedback(org_id, customer_id, page, page_size)
    return {
        "data": items,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/{customer_id}/sentiment-trend")
def get_customer_sentiment_trend_endpoint(
    customer_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get sentiment trend over time for a customer."""
    org_id = current_user["org_id"]
    doc = get_customer(org_id, customer_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = get_customer_sentiment_trend(org_id, customer_id)
    return {"data": data}


@router.get("/{customer_id}")
def get_customer_detail(
    customer_id: str,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Get single customer."""
    org_id = current_user["org_id"]
    doc = get_customer(org_id, customer_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"data": doc}
