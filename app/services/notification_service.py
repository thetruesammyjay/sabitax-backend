"""
Notification service for user alerts and reminders.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.notification import Notification
from app.repositories.notification_repo import NotificationRepository
from app.schemas.notification import (
    MarkReadResponse,
    NotificationResponse,
    NotificationsResponse,
)


class NotificationService:
    """Notification business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    async def get_notifications(
        self,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationsResponse:
        """
        Get user notifications.

        Args:
            user_id: User's ID
            unread_only: Only return unread
            limit: Max results
            offset: Skip results

        Returns:
            NotificationsResponse with notifications
        """
        notifications = await self.notification_repo.get_by_user(
            user_id, unread_only=unread_only, limit=limit, offset=offset
        )

        unread_count = await self.notification_repo.count_unread(user_id)

        return NotificationsResponse(
            notifications=[
                NotificationResponse(
                    id=str(n.id),
                    type=n.type,
                    title=n.title,
                    message=n.message,
                    read=n.is_read,
                    action=n.action,
                    created_at=n.created_at,
                )
                for n in notifications
            ],
            unread_count=unread_count,
        )

    async def mark_as_read(
        self,
        user_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> MarkReadResponse:
        """
        Mark notification as read.

        Args:
            user_id: User's ID
            notification_id: Notification ID

        Returns:
            MarkReadResponse with status
        """
        notification = await self.notification_repo.mark_as_read(
            notification_id, user_id
        )

        if not notification:
            raise NotFoundError("Notification not found", resource="notification")

        return MarkReadResponse(
            id=str(notification.id),
            read=True,
        )

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """
        Mark all notifications as read.

        Args:
            user_id: User's ID

        Returns:
            Count of marked notifications
        """
        return await self.notification_repo.mark_all_as_read(user_id)

    async def create_notification(
        self,
        user_id: uuid.UUID,
        type: str,
        title: str,
        message: str | None = None,
        action: str | None = None,
    ) -> NotificationResponse:
        """
        Create a new notification.

        Args:
            user_id: User's ID
            type: Notification type
            title: Notification title
            message: Optional message body
            action: Optional action URL/identifier

        Returns:
            Created NotificationResponse
        """
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            action=action,
        )

        notification = await self.notification_repo.create(notification)

        return NotificationResponse(
            id=str(notification.id),
            type=notification.type,
            title=notification.title,
            message=notification.message,
            read=notification.is_read,
            action=notification.action,
            created_at=notification.created_at,
        )

    async def send_tax_reminder(
        self,
        user_id: uuid.UUID,
        due_date: str,
    ) -> NotificationResponse:
        """
        Send tax deadline reminder.

        Args:
            user_id: User's ID
            due_date: Tax due date string

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            type="tax_reminder",
            title="Tax Deadline Approaching",
            message=f"Your tax filing is due on {due_date}. File now to avoid penalties!",
            action="tax/file",
        )

    async def send_filing_complete(
        self,
        user_id: uuid.UUID,
        reference_number: str,
    ) -> NotificationResponse:
        """
        Send filing completion notification.

        Args:
            user_id: User's ID
            reference_number: Filing reference

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            type="filing_complete",
            title="Tax Filing Submitted",
            message=f"Your tax filing (Ref: {reference_number}) has been submitted successfully.",
            action=f"tax/filings",
        )

    async def send_tin_update(
        self,
        user_id: uuid.UUID,
        status: str,
        tin: str | None = None,
    ) -> NotificationResponse:
        """
        Send TIN application update.

        Args:
            user_id: User's ID
            status: Application status
            tin: Assigned TIN if approved

        Returns:
            Created notification
        """
        if status == "approved" and tin:
            title = "TIN Application Approved"
            message = f"Your TIN has been assigned: {tin}"
        elif status == "rejected":
            title = "TIN Application Update"
            message = "Your TIN application requires additional information."
        else:
            title = "TIN Application Processing"
            message = "Your TIN application is being processed."

        return await self.create_notification(
            user_id=user_id,
            type="tin_update",
            title=title,
            message=message,
            action="tin",
        )
