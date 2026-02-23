"""Authentication service."""

import uuid
from datetime import datetime
from typing import Any

from app.models.user import ORGANIZATIONS_INDEX, USERS_INDEX
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse
from app.services.es_service import get_document, index_document, search_documents, update_document
from app.utils.logging import get_logger
from app.utils.security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)


def signup(req: SignupRequest) -> AuthResponse:
    """
    Create org and user, return token.

    Raises:
        ValueError: If email already exists (caller maps to 409).
    """
    existing = search_documents(
        USERS_INDEX,
        {"term": {"email": req.email}},
        size=1,
    )
    if existing:
        logger.info("Signup rejected: email already exists")
        raise ValueError("A user with this email already exists")

    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    index_document(
        ORGANIZATIONS_INDEX,
        org_id,
        {
            "org_id": org_id,
            "name": req.org_name,
            "onboarding_completed": False,
            "created_at": now,
            "updated_at": now,
        },
    )

    index_document(
        USERS_INDEX,
        user_id,
        {
            "user_id": user_id,
            "org_id": org_id,
            "email": req.email,
            "hashed_password": hash_password(req.password),
            "full_name": req.full_name,
            "role": "pm",
            "created_at": now,
            "updated_at": now,
        },
    )

    logger.info("User signed up: %s", req.email[:3] + "***@" + req.email.split("@")[-1])

    token = create_access_token(sub=user_id, org_id=org_id, email=req.email)
    return AuthResponse(
        user=UserResponse(
            user_id=user_id,
            email=req.email,
            full_name=req.full_name,
            org_id=org_id,
            org_name=req.org_name,
            role="pm",
        ),
        access_token=token,
    )


def login(req: LoginRequest) -> AuthResponse:
    """
    Verify credentials and return token.

    Raises:
        ValueError: If email not found or password wrong (caller maps to 401).
    """
    hits = search_documents(
        USERS_INDEX,
        {"term": {"email": req.email}},
        size=1,
    )
    if not hits:
        logger.info("Login failed: email not found")
        raise ValueError("Invalid email or password")

    user = hits[0]
    if not verify_password(req.password, user["hashed_password"]):
        logger.info("Login failed: wrong password")
        raise ValueError("Invalid email or password")

    org = get_document(ORGANIZATIONS_INDEX, user["org_id"])
    org_name = org["name"] if org else ""

    token = create_access_token(
        sub=user["user_id"],
        org_id=user["org_id"],
        email=user["email"],
    )

    logger.info("User logged in: %s", req.email[:3] + "***@" + req.email.split("@")[-1])

    return AuthResponse(
        user=UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user["full_name"],
            org_id=user["org_id"],
            org_name=org_name,
            role=user.get("role", "pm"),
        ),
        access_token=token,
    )


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Get user document by user_id (not doc _id)."""
    hits = search_documents(
        USERS_INDEX,
        {"term": {"user_id": user_id}},
        size=1,
    )
    return hits[0] if hits else None


def get_preferences(user_id: str) -> dict[str, Any]:
    """Get dashboard preferences for user. Returns defaults if none set."""
    user = get_user_by_id(user_id)
    if not user:
        return {
            "dashboard_preferences": {
                "visible_widgets": [
                    "summary", "volume", "sentiment", "top_issues",
                    "areas", "at_risk", "recent", "sources", "segments",
                ],
                "default_period": "30d",
            }
        }
    prefs = user.get("dashboard_preferences") or {}
    return {
        "dashboard_preferences": {
            "visible_widgets": prefs.get("visible_widgets") or [
                "summary", "volume", "sentiment", "top_issues",
                "areas", "at_risk", "recent", "sources", "segments",
            ],
            "default_period": prefs.get("default_period") or "30d",
        }
    }


def update_preferences(user_id: str, preferences: dict[str, Any]) -> dict[str, Any]:
    """Update dashboard preferences. Returns updated preferences."""
    current = get_preferences(user_id)
    existing = current.get("dashboard_preferences") or {}
    prefs = preferences.get("dashboard_preferences") or {}
    merged = {
        "visible_widgets": prefs.get("visible_widgets") if "visible_widgets" in prefs else existing.get("visible_widgets"),
        "default_period": prefs.get("default_period") if "default_period" in prefs else existing.get("default_period"),
    }
    if merged["visible_widgets"] is None:
        merged["visible_widgets"] = [
            "summary", "volume", "sentiment", "top_issues",
            "areas", "at_risk", "recent", "sources", "segments",
        ]
    if merged["default_period"] is None:
        merged["default_period"] = "30d"
    now = datetime.utcnow().isoformat() + "Z"
    update_document(
        USERS_INDEX,
        user_id,
        {"dashboard_preferences": merged, "updated_at": now},
    )
    return {"dashboard_preferences": merged}
