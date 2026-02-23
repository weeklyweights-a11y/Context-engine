"""Pydantic schemas for specs."""

from typing import Any

from pydantic import BaseModel, Field


class GenerateSpecRequest(BaseModel):
    """Request body for POST /specs/generate."""

    topic: str = Field(..., min_length=1)
    product_area: str | None = None


class GenerateSpecResponse(BaseModel):
    """Response from generate - subset of spec for redirect."""

    id: str
    title: str
    status: str
    feedback_count: int
    customer_count: int
    total_arr: float
    created_at: str


class UpdateSpecRequest(BaseModel):
    """Request body for PUT /specs/{id}."""

    status: str | None = None
    prd: str | None = None
    architecture: str | None = None
    rules: str | None = None
    plan: str | None = None
    title: str | None = None


class SpecDetail(BaseModel):
    """Full spec document."""

    id: str
    org_id: str
    title: str
    topic: str
    product_area: str | None
    status: str
    prd: str
    architecture: str
    rules: str
    plan: str
    feedback_count: int
    customer_count: int
    total_arr: float
    feedback_ids: list[str] = Field(default_factory=list)
    customer_ids: list[str] = Field(default_factory=list)
    linked_goal_id: str | None = None
    generated_by: str | None = None
    generated_by_name: str | None = None
    data_freshness_date: str | None = None
    created_at: str
    updated_at: str

    model_config = {"extra": "ignore"}


class SpecListItem(BaseModel):
    """Spec list item (card)."""

    id: str
    title: str
    topic: str
    product_area: str | None
    status: str
    feedback_count: int
    customer_count: int
    total_arr: float
    prd: str | None = None
    created_at: str

    model_config = {"extra": "ignore"}


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total: int


class SpecListResponse(BaseModel):
    """Paginated list response."""

    data: list[dict[str, Any]]
    pagination: PaginationInfo
