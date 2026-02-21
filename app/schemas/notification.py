"""
Notification schemas for request/response validation.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


NotificationType = Literal[
    "tax_reminder",
    "filing_complete",
    "tin_update",
    "subscription",
    "referral",
    "system",
    "tip",
]


class NotificationResponse(BaseModel):
    """Notification response."""

    id: str
    type: str
    title: str
    message: str | None
    read: bool
    action: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationsResponse(BaseModel):
    """Notifications list response."""

    notifications: list[NotificationResponse]
    unread_count: int


class MarkReadResponse(BaseModel):
    """Mark notification as read response."""

    id: str
    read: bool


class NotificationSettingsRequest(BaseModel):
    """Notification settings update request."""

    tax_reminders: bool = True
    filing_updates: bool = True
    tips: bool = True
    marketing: bool = False


class NotificationSettingsResponse(BaseModel):
    """Notification settings response."""

    tax_reminders: bool
    filing_updates: bool
    tips: bool
    marketing: bool
