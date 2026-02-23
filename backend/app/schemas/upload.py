"""Pydantic schemas for upload history."""

from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Single upload record."""

    id: str
    org_id: str
    upload_type: str
    filename: str
    total_rows: int
    imported_rows: int
    failed_rows: int
    status: str
    column_mapping: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: str
    completed_at: str | None = None


class UploadListResponse(BaseModel):
    """List of uploads."""

    data: list[dict[str, Any]]
    pagination: dict[str, int] | None = None
