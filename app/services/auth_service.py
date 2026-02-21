"""
Authentication service for user registration and login.
"""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
)
from app.core.utils import generate_referral_code
from app.models.referral import Referral
from app.models.user import User
from app.repositories.referral_repo import ReferralRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import AuthResponse, UserBasic


class AuthService:
    """Authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.referral_repo = ReferralRepository(db)

    async def register(
        self,
        name: str,
        email: str,
        password: str,
        referral_code: str | None = None,
    ) -> AuthResponse:
        """
        Register a new user.

        Args:
            name: User's full name
            email: User's email address
            password: Plain text password
            referral_code: Optional referral code

        Returns:
            AuthResponse with token and user data

        Raises:
            ConflictError: If email already exists
        """
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ConflictError("An account with this email already exists")

        # Handle referral
        referrer_id = None
        if referral_code:
            referrer = await self.user_repo.get_by_referral_code(referral_code)
            if referrer:
                referrer_id = referrer.id

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            referral_code=generate_referral_code(name),
            referred_by=referrer_id,
            streak_days=1,
            last_active_date=date.today(),
        )
        user = await self.user_repo.create(user)

        # Create referral record if referred
        if referrer_id:
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=user.id,
                status="pending",
            )
            await self.referral_repo.create(referral)

        # Generate token
        access_token = create_access_token(str(user.id))

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserBasic(
                id=str(user.id),
                name=user.name,
                email=user.email,
            ),
        )

    async def login(
        self,
        email: str,
        password: str,
    ) -> AuthResponse:
        """
        Login with email and password.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            AuthResponse with token and user data

        Raises:
            UnauthorizedError: If credentials are invalid
        """
        user = await self.user_repo.get_by_email(email)

        if not user or not user.password_hash:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Update streak
        await self._update_streak(user)

        # Generate token
        access_token = create_access_token(str(user.id))

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserBasic(
                id=str(user.id),
                name=user.name,
                email=user.email,
            ),
        )

    async def social_login(
        self,
        provider: str,
        token: str,
    ) -> AuthResponse:
        """
        Handle social login (Google/Apple).

        Args:
            provider: 'google' or 'apple'
            token: OAuth token from provider

        Returns:
            AuthResponse with token and user data
        """
        # Verify token with provider (placeholder - integrate actual OAuth)
        user_info = await self._verify_social_token(provider, token)

        if not user_info:
            raise UnauthorizedError("Invalid social login token")

        # Look up user by provider ID
        user = None
        if provider == "google":
            user = await self.user_repo.get_by_google_id(user_info["id"])
        elif provider == "apple":
            user = await self.user_repo.get_by_apple_id(user_info["id"])

        # If not found, check by email
        if not user and user_info.get("email"):
            user = await self.user_repo.get_by_email(user_info["email"])
            if user:
                # Link social account
                if provider == "google":
                    await self.user_repo.update(user.id, google_id=user_info["id"])
                elif provider == "apple":
                    await self.user_repo.update(user.id, apple_id=user_info["id"])

        # Create new user if not found
        if not user:
            user = User(
                name=user_info.get("name", ""),
                email=user_info.get("email", f"{user_info['id']}@{provider}.local"),
                google_id=user_info["id"] if provider == "google" else None,
                apple_id=user_info["id"] if provider == "apple" else None,
                is_verified=True,
                referral_code=generate_referral_code(user_info.get("name", "User")),
                streak_days=1,
                last_active_date=date.today(),
            )
            user = await self.user_repo.create(user)

        # Update streak
        await self._update_streak(user)

        # Generate token
        access_token = create_access_token(str(user.id))

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserBasic(
                id=str(user.id),
                name=user.name,
                email=user.email,
            ),
        )

    async def forgot_password(self, email: str) -> str:
        """
        Request password reset.

        Args:
            email: User's email

        Returns:
            Reset token (in production, send via email)
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            # Don't reveal if email exists
            return "If the email exists, a reset link has been sent"

        # Generate reset token
        reset_token = create_password_reset_token(email)

        # In production, send email with reset link
        # await send_reset_email(email, reset_token)

        return reset_token  # Return for development; in prod, just confirm

    async def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> bool:
        """
        Reset password with token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            True if successful

        Raises:
            BadRequestError: If token is invalid
        """
        email = verify_password_reset_token(token)

        if not email:
            raise BadRequestError("Invalid or expired reset token")

        user = await self.user_repo.get_by_email(email)

        if not user:
            raise BadRequestError("Invalid or expired reset token")

        # Update password
        await self.user_repo.update_password(user.id, hash_password(new_password))

        return True

    async def _update_streak(self, user: User) -> None:
        """Update user's activity streak."""
        today = date.today()

        if user.last_active_date:
            days_since = (today - user.last_active_date).days

            if days_since == 1:
                # Consecutive day, increment streak
                await self.user_repo.update_streak(
                    user.id,
                    streak_days=user.streak_days + 1,
                    last_active_date=today,
                )
            elif days_since > 1:
                # Streak broken, reset to 1
                await self.user_repo.update_streak(
                    user.id,
                    streak_days=1,
                    last_active_date=today,
                )
            # If same day, no update needed
        else:
            # First activity
            await self.user_repo.update_streak(
                user.id,
                streak_days=1,
                last_active_date=today,
            )

    async def _verify_social_token(
        self,
        provider: str,
        token: str,
    ) -> dict | None:
        """
        Verify social OAuth token.

        This is a placeholder - integrate actual OAuth verification.
        """
        # Placeholder implementation
        # In production, verify with Google/Apple APIs
        import httpx

        if provider == "google":
            # Verify Google token
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "id": data.get("sub"),
                            "email": data.get("email"),
                            "name": data.get("name"),
                        }
            except Exception:
                pass

        elif provider == "apple":
            # Apple Sign In verification requires more complex JWT verification
            # Placeholder - implement proper Apple ID verification
            pass

        return None
