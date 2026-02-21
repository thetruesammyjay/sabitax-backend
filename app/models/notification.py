"""
Notification model for user notifications.
"""
import uuid
from typing import TYPE_CHECKING, Literal

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


NotificationType = Literal[
    "tax_reminder",
    "filing_complete",
    "tin_update",
    "subscription",
    "referral",
    "system",
    "tip",
]


class Notification(BaseModel):
    """Notification model for user alerts."""

    __tablename__ = "notifications"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Notification details
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    # Action (optional deep link or action identifier)
    action: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        read_status = "read" if self.is_read else "unread"
        return f"<Notification {self.type}: {self.title} ({read_status})>"
