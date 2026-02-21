"""
User repository for database operations.
"""
import uuid
from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """User database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, referral_code: str) -> User | None:
        """Get user by referral code."""
        result = await self.db.execute(
            select(User).where(User.referral_code == referral_code)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        """Get user by Google ID."""
        result = await self.db.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def get_by_apple_id(self, apple_id: str) -> User | None:
        """Get user by Apple ID."""
        result = await self.db.execute(
            select(User).where(User.apple_id == apple_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user_id: uuid.UUID, **kwargs) -> User | None:
        """Update user by ID."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(**kwargs)
        )
        return await self.get_by_id(user_id)

    async def update_password(self, user_id: uuid.UUID, password_hash: str) -> bool:
        """Update user password."""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
        )
        return result.rowcount > 0  # type: ignore

    async def update_streak(
        self,
        user_id: uuid.UUID,
        streak_days: int,
        last_active_date: date,
    ) -> User | None:
        """Update user streak."""
        return await self.update(
            user_id,
            streak_days=streak_days,
            last_active_date=last_active_date,
        )

    async def set_tin(
        self,
        user_id: uuid.UUID,
        tin: str,
        verified: bool = False,
    ) -> User | None:
        """Set user TIN."""
        return await self.update(user_id, tin=tin, tin_verified=verified)

    async def update_subscription_plan(
        self,
        user_id: uuid.UUID,
        plan: str,
    ) -> User | None:
        """Update user subscription plan."""
        return await self.update(user_id, subscription_plan=plan)

    async def set_referral_code(
        self,
        user_id: uuid.UUID,
        referral_code: str,
    ) -> User | None:
        """Set user referral code."""
        return await self.update(user_id, referral_code=referral_code)

    async def set_referred_by(
        self,
        user_id: uuid.UUID,
        referrer_id: uuid.UUID,
    ) -> User | None:
        """Set who referred this user."""
        return await self.update(user_id, referred_by=referrer_id)

    async def verify_email(self, user_id: uuid.UUID) -> User | None:
        """Mark user email as verified."""
        return await self.update(user_id, is_verified=True)

    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user by ID."""
        user = await self.get_by_id(user_id)
        if user:
            await self.db.delete(user)
            return True
        return False
