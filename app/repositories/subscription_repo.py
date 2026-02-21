"""
Subscription repository for database operations.
"""
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription


class SubscriptionRepository:
    """Subscription database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        self.db.add(subscription)
        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription

    async def get_by_id(
        self,
        subscription_id: uuid.UUID,
    ) -> Subscription | None:
        """Get subscription by ID."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(
        self,
        user_id: uuid.UUID,
    ) -> Subscription | None:
        """Get active subscription for a user."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
            .order_by(Subscription.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> list[Subscription]:
        """Get subscription history for a user."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        subscription_id: uuid.UUID,
        **kwargs,
    ) -> Subscription | None:
        """Update subscription."""
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**kwargs)
        )
        return await self.get_by_id(subscription_id)

    async def cancel(
        self,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Subscription | None:
        """Cancel a subscription."""
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .where(Subscription.user_id == user_id)
            .values(
                status="cancelled",
                cancelled_at=datetime.utcnow(),
            )
        )
        return await self.get_by_id(subscription_id)

    async def expire_subscription(
        self,
        subscription_id: uuid.UUID,
    ) -> bool:
        """Mark subscription as expired."""
        result = await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(status="expired")
        )
        return result.rowcount > 0  # type: ignore
