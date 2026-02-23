"""Auth endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth_service import get_user_by_id, login, signup
from app.services.es_service import get_document
from app.models.user import ORGANIZATIONS_INDEX

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=dict, status_code=201)
def signup_endpoint(req: SignupRequest) -> dict:
    """Create account and org, return user and token."""
    try:
        result = signup(req)
        return {"data": result.model_dump()}
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=dict)
def login_endpoint(req: LoginRequest) -> dict:
    """Login and return user and token."""
    try:
        result = login(req)
        return {"data": result.model_dump()}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


@router.get("/me", response_model=dict)
def me_endpoint(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Return current user info (no token)."""
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    org = get_document(ORGANIZATIONS_INDEX, user["org_id"])
    org_name = org["name"] if org else ""

    return {
        "data": {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "org_id": user["org_id"],
            "org_name": org_name,
            "role": user.get("role", "pm"),
        }
    }
