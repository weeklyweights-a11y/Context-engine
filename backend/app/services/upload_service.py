"""Upload history and temporary file management."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.upload import (
    UPLOAD_HISTORY_INDEX,
    UPLOAD_HISTORY_MAPPING,
)
from app.services.es_service import (
    delete_document,
    ensure_index_exists,
    get_document,
    index_document,
    search_document_ids,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

TEMP_UPLOAD_DIR = Path("/tmp/ce_uploads")


def _ensure_temp_dir() -> Path:
    """Ensure temp upload directory exists."""
    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_UPLOAD_DIR


def create_upload(
    org_id: str,
    upload_type: str,
    filename: str,
    total_rows: int,
    temp_file_path: str,
) -> str:
    """
    Create upload history record.

    Returns:
        upload_id (document id).
    """
    ensure_index_exists(UPLOAD_HISTORY_INDEX, UPLOAD_HISTORY_MAPPING)
    upload_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    body = {
        "id": upload_id,
        "org_id": org_id,
        "upload_type": upload_type,
        "filename": filename,
        "total_rows": total_rows,
        "imported_rows": 0,
        "failed_rows": 0,
        "status": "pending",
        "column_mapping": {},
        "error_message": None,
        "temp_file_path": temp_file_path,
        "created_at": now,
        "completed_at": None,
    }
    index_document(UPLOAD_HISTORY_INDEX, upload_id, body)
    logger.info("Created upload %s for org %s", upload_id[:8], org_id[:8])
    return upload_id


def update_upload(
    upload_id: str,
    *,
    status: str | None = None,
    imported_rows: int | None = None,
    failed_rows: int | None = None,
    column_mapping: dict[str, Any] | None = None,
    error_message: str | None = None,
    default_source: str | None = None,
    use_today_for_date: bool | None = None,
    auto_detect_areas: bool | None = None,
    auto_analyze_sentiment: bool | None = None,
    imported_ids: list[str] | None = None,
) -> None:
    """Update upload record. Only provided fields are updated."""
    doc = get_document(UPLOAD_HISTORY_INDEX, upload_id)
    if not doc:
        return

    now = datetime.utcnow().isoformat() + "Z"
    if status is not None:
        doc["status"] = status
    if imported_rows is not None:
        doc["imported_rows"] = imported_rows
    if failed_rows is not None:
        doc["failed_rows"] = failed_rows
    if column_mapping is not None:
        doc["column_mapping"] = column_mapping
    if error_message is not None:
        doc["error_message"] = error_message
    if default_source is not None:
        doc["default_source"] = default_source
    if use_today_for_date is not None:
        doc["use_today_for_date"] = use_today_for_date
    if auto_detect_areas is not None:
        doc["auto_detect_areas"] = auto_detect_areas
    if auto_analyze_sentiment is not None:
        doc["auto_analyze_sentiment"] = auto_analyze_sentiment
    if imported_ids is not None:
        doc["imported_ids"] = imported_ids
    if status in ("completed", "failed"):
        doc["completed_at"] = now

    index_document(UPLOAD_HISTORY_INDEX, upload_id, doc)


def get_upload(org_id: str, upload_id: str) -> dict[str, Any] | None:
    """Get single upload. Returns None if not found or wrong org."""
    doc = get_document(UPLOAD_HISTORY_INDEX, upload_id)
    if not doc or doc.get("org_id") != org_id:
        return None
    return doc


def get_uploads(org_id: str) -> list[dict[str, Any]]:
    """List uploads for org, newest first."""
    from app.services.es_service import search_documents

    ensure_index_exists(UPLOAD_HISTORY_INDEX, UPLOAD_HISTORY_MAPPING)
    hits = search_documents(
        UPLOAD_HISTORY_INDEX,
        {"term": {"org_id": org_id}},
        size=100,
    )
    sorted_hits = sorted(
        hits,
        key=lambda d: d.get("created_at", "") or "",
        reverse=True,
    )
    return sorted_hits


def get_upload_temp_path(upload_id: str) -> str | None:
    """Return temp file path for upload, or None if not found."""
    doc = get_document(UPLOAD_HISTORY_INDEX, upload_id)
    if not doc:
        return None
    return doc.get("temp_file_path")


def cleanup_upload_temp(upload_id: str) -> None:
    """Delete temp file for upload."""
    path = get_upload_temp_path(upload_id)
    if path:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning("Failed to cleanup temp file %s: %s", path, str(e))


def delete_upload(org_id: str, upload_id: str) -> bool:
    """
    Delete upload record and all imported data. Verifies org ownership.
    Deletes feedback or customer documents created by this upload.
    Falls back to deleting by source_file for feedback if imported_ids not stored.
    Returns True if deleted.
    """
    doc = get_upload(org_id, upload_id)
    if not doc:
        return False

    imported_ids: list[str] = doc.get("imported_ids") or []
    upload_type = doc.get("upload_type", "")
    filename = doc.get("filename") or ""

    if not imported_ids and upload_type == "feedback" and filename:
        from app.models.feedback import feedback_index as _feedback_idx
        idx = _feedback_idx(org_id)
        try:
            imported_ids = search_document_ids(
                idx,
                {
                    "bool": {
                        "must": [
                            {"term": {"org_id": org_id}},
                            {"term": {"source_file": filename}},
                            {"term": {"ingestion_method": "csv_upload"}},
                        ]
                    }
                },
                size=10000,
            )
        except Exception:
            pass

    if imported_ids:
        if upload_type == "feedback":
            from app.models.feedback import feedback_index
            idx = feedback_index(org_id)
            for doc_id in imported_ids:
                try:
                    delete_document(idx, doc_id)
                except Exception:
                    pass
        elif upload_type == "customers":
            from app.models.customer import customers_index
            idx = customers_index(org_id)
            for doc_id in imported_ids:
                try:
                    delete_document(idx, doc_id)
                except Exception:
                    pass

    cleanup_upload_temp(upload_id)
    return delete_document(UPLOAD_HISTORY_INDEX, upload_id)


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to temp directory. Returns path to saved file.
    """
    _ensure_temp_dir()
    ext = Path(filename).suffix or ".csv"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = TEMP_UPLOAD_DIR / unique_name
    path.write_bytes(file_content)
    return str(path)
