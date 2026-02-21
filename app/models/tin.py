"""
TIN (Tax Identification Number) Application model.
"""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


TINStatus = Literal["processing", "approved", "rejected", "pending_documents"]


class TINApplication(BaseModel):
    """TIN application model for tracking new TIN requests."""

    __tablename__ = "tin_applications"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Application details
    nin: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    # Document upload
    id_document_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    utility_bill_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="processing")

    # Result
    assigned_tin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reference
    reference_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    # Timestamps
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tin_applications")

    def __repr__(self) -> str:
        return f"<TINApplication {self.reference_number}: {self.status}>"
