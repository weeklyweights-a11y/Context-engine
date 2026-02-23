"""Agent chat endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas.agent import ChatRequest, ChatResponse
from app.services.agent_service import get_agent_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Send a message to the agent and get a response."""
    org_id = current_user["org_id"]
    user_id = current_user["user_id"]
    try:
        result = await get_agent_service().chat(
            org_id=org_id,
            user_id=user_id,
            message=body.message.strip(),
            conversation_id=body.conversation_id,
            context=body.context,
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.get("/conversations")
def list_conversations(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """List conversations for the current user."""
    org_id = current_user["org_id"]
    user_id = current_user["user_id"]
    items = get_agent_service().get_conversations(org_id=org_id, user_id=user_id)
    return {"data": items}


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get a single conversation by ID."""
    org_id = current_user["org_id"]
    doc = get_agent_service().get_conversation(org_id=org_id, conversation_id=conversation_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return doc
