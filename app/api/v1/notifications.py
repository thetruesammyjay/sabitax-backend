"""
Notification endpoints.
"""
import uuid

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import MessageResponse
from app.schemas.notification import (
    MarkReadResponse,
    NotificationsResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=NotificationsResponse)
async def get_notifications(
    current_user: CurrentUser,
    db: DbSession,
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get user notifications.

    Returns notifications with unread count.
    """
    service = NotificationService(db)
    return await service.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.post("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Mark notification as read.
    """
    service = NotificationService(db)
    return await service.mark_as_read(
        user_id=current_user.id,
        notification_id=notification_id,
    )


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_notifications_read(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Mark all notifications as read.
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return MessageResponse(message=f"Marked {count} notifications as read")
