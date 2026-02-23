"""Common response schemas."""

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    elasticsearch: dict[str, Any]
    version: str


class ErrorResponse(BaseModel):
    """Error response shape."""

    detail: str
    status_code: int
