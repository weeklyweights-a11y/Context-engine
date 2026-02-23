"""Pydantic schemas for feedback."""

from typing import Any

from pydantic import BaseModel, Field


class FeedbackManualRequest(BaseModel):
    """Manual feedback entry."""

    text: str = Field(..., min_length=1)
    source: str | None = None
    product_area: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    author_name: str | None = None
    author_email: str | None = None
    rating: int | None = None
    created_at: str | None = None


class FeedbackResponse(BaseModel):
    """Feedback item response."""

    id: str
    org_id: str
    text: str
    source: str | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    rating: int | None = None
    product_area: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    customer_segment: str | None = None
    author_name: str | None = None
    author_email: str | None = None
    tags: list[str] | None = None
    source_file: str | None = None
    ingestion_method: str | None = None
    created_at: str | None = None
    ingested_at: str | None = None
    metadata: dict[str, Any] | None = None


class DetectedArea(BaseModel):
    """Detected product area from feedback."""

    name: str
    count: int
    is_new: bool


class FeedbackUploadInitResponse(BaseModel):
    """Response from initial CSV upload."""

    upload_id: str
    columns: list[str]
    suggested_mapping: dict[str, str | None]
    total_rows: int


class FeedbackUploadConfirmRequest(BaseModel):
    """Column mapping confirmation."""

    column_mapping: dict[str, str | None]
    default_source: str | None = None
    use_today_for_date: bool = False
    auto_detect_areas: bool = True
    auto_analyze_sentiment: bool = True


class FeedbackUploadImportResponse(BaseModel):
    """Import result."""

    upload_id: str
    total_rows: int
    imported_rows: int
    failed_rows: int
    detected_areas: list[dict[str, Any]] = Field(default_factory=list)
