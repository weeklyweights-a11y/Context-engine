"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.es_client import get_es_client
from app.services.auth_service import get_user_by_id
from app.services.es_service import get_document
from app.utils.security import decode_token

security = HTTPBearer(auto_error=False)

# For typing: CurrentUser-like object
# We use a simple dict with user_id, org_id, email


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ] = None,
) -> dict:
    """
    Extract and validate JWT, return current user info.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    org_id = payload.get("org_id")
    email = payload.get("email")

    if not user_id or not org_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return {"user_id": user_id, "org_id": org_id, "email": email}


def get_es_client_dep():
    """Dependency that returns ES client."""
    return get_es_client()
