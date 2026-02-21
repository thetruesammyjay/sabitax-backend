"""
Security utilities for authentication and authorization.
Password hashing, JWT token handling.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Custom expiration time
        extra_claims: Additional claims to include

    Returns:
        Encoded JWT token string
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
    }

    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str | Any) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        subject: Token subject (usually user ID)

    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload dict or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


def get_token_subject(token: str) -> str | None:
    """
    Extract subject from a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token subject (user ID) or None if invalid
    """
    payload = decode_token(token)
    if payload is None:
        return None
    return payload.get("sub")


def create_password_reset_token(email: str) -> str:
    """
    Create a short-lived token for password reset.

    Args:
        email: User email address

    Returns:
        Password reset token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=1)

    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": now,
        "type": "password_reset",
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token and extract email.

    Args:
        token: Password reset token

    Returns:
        Email address or None if invalid
    """
    payload = decode_token(token)
    if payload is None:
        return None

    if payload.get("type") != "password_reset":
        return None

    return payload.get("sub")
