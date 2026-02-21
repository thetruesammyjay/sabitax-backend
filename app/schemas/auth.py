"""
Authentication schemas for request/response validation.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """User registration request."""

    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class SocialLoginRequest(BaseModel):
    """Social login request (Google/Apple)."""

    provider: str = Field(..., pattern="^(google|apple)$")
    token: str


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset with token."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class AuthResponse(BaseModel):
    """Authentication response with user data."""

    access_token: str
    token_type: str = "bearer"
    user: "UserBasic"


class UserBasic(BaseModel):
    """Basic user info for auth responses."""

    id: str
    name: str | None
    email: str

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


# Update forward reference
AuthResponse.model_rebuild()
