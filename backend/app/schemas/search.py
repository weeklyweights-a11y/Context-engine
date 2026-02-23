"""Pydantic schemas for search."""

from pydantic import BaseModel, Field


class SearchFeedbackFilters(BaseModel):
    """Filters for feedback search (all optional)."""

    product_area: list[str] | None = None
    source: list[str] | None = None
    sentiment: list[str] | None = None
    customer_segment: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None
    customer_id: str | None = None
    has_customer: bool | None = None


class SearchFeedbackRequest(BaseModel):
    """Request body for POST /search/feedback."""

    query: str = ""
    filters: SearchFeedbackFilters | None = None
    sort_by: str = "relevance"
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
