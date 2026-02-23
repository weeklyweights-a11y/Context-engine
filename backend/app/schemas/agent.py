"""Pydantic schemas for agent chat."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for agent chat."""

    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    """Response from agent chat."""

    conversation_id: str
    response: str
    tools_used: list[Any] = Field(default_factory=list)
    citations: list[dict[str, Any]] = Field(default_factory=list)
