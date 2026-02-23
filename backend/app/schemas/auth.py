"""Auth request and response schemas."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request body."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    org_name: str


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User info in API responses."""

    user_id: str
    email: str
    full_name: str
    org_id: str
    org_name: str
    role: str


class AuthResponse(BaseModel):
    """Auth response with user and token."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
