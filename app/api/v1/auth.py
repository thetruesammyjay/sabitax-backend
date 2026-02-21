"""
Authentication endpoints.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SocialLoginRequest,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new user account.

    - **name**: User's full name (2-255 characters)
    - **email**: Valid email address
    - **password**: Password (8+ characters, must contain uppercase, lowercase, digit)

    Returns access token and user info.
    """
    service = AuthService(db)
    return await service.register(
        name=data.name,
        email=data.email,
        password=data.password,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Login with email and password.

    Returns access token and user info.
    """
    service = AuthService(db)
    return await service.login(
        email=data.email,
        password=data.password,
    )


@router.post("/social", response_model=AuthResponse)
async def social_login(
    data: SocialLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Social login (Google/Apple).

    - **provider**: 'google' or 'apple'
    - **token**: OAuth token from provider

    Returns access token and user info.
    """
    service = AuthService(db)
    return await service.social_login(
        provider=data.provider,
        token=data.token,
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Request password reset.

    Sends password reset email if account exists.
    """
    service = AuthService(db)
    await service.forgot_password(data.email)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Reset password with token.

    - **token**: Password reset token from email
    - **new_password**: New password (8+ characters)
    """
    service = AuthService(db)
    await service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
    return MessageResponse(message="Password reset successfully")
