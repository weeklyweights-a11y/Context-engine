"""Pydantic schemas for customers."""

from typing import Any

from pydantic import BaseModel, Field


class CustomerManualRequest(BaseModel):
    """Manual customer entry."""

    company_name: str = Field(..., min_length=1)
    customer_id_external: str | None = None
    segment: str | None = None
    plan: str | None = None
    mrr: float | None = None
    arr: float | None = None
    account_manager: str | None = None
    renewal_date: str | None = None
    health_score: int | None = None
    industry: str | None = None
    employee_count: int | None = None


class CustomerResponse(BaseModel):
    """Customer profile response."""

    id: str
    org_id: str
    company_name: str
    customer_id_external: str | None = None
    segment: str | None = None
    plan: str | None = None
    mrr: float | None = None
    arr: float | None = None
    account_manager: str | None = None
    renewal_date: str | None = None
    health_score: int | None = None
    industry: str | None = None
    employee_count: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    metadata: dict[str, Any] | None = None


class CustomerUploadInitResponse(BaseModel):
    """Response from initial customer CSV upload."""

    upload_id: str
    columns: list[str]
    suggested_mapping: dict[str, str | None]
    total_rows: int


class CustomerUploadConfirmRequest(BaseModel):
    """Column mapping confirmation for customers."""

    column_mapping: dict[str, str | None]


class CustomerUploadImportResponse(BaseModel):
    """Customer import result."""

    upload_id: str
    total_rows: int
    imported_rows: int
    failed_rows: int
