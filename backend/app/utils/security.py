"""JWT and password utilities."""

import hashlib
from datetime import datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings


def _preprocess(password: str) -> bytes:
    """SHA256 hash to stay under bcrypt's 72-byte limit."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (SHA256 pre-hash for long passwords)."""
    return bcrypt.hashpw(_preprocess(password), bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(_preprocess(plain_password), hashed_password.encode("ascii"))


def create_access_token(
    sub: str, org_id: str, email: str
) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": sub,
        "org_id": org_id,
        "email": email,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate JWT. Returns payload or None if invalid."""
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None
