"""
Notification repository for database operations.
"""
import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Notification database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        """Create a new notification."""
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Notification | None:
        """Get notification by ID."""
        query = select(Notification).where(Notification.id == notification_id)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """Get notifications for a user."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )

        if unread_only:
            query = query.where(Notification.is_read == False)  # noqa: E712

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_unread(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Count unread notifications for a user."""
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)  # noqa: E712
        )
        return result.scalar() or 0

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification | None:
        """Mark notification as read."""
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )
        return await self.get_by_id(notification_id, user_id)

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Mark all notifications as read for a user."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        return result.rowcount  # type: ignore
