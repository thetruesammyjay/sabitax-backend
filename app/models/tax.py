"""
Tax Filing model for tracking tax submissions.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


TaxType = Literal["PIT", "VAT", "CIT", "PAYE"]
FilingStatus = Literal["draft", "submitted", "processing", "completed", "rejected"]


class TaxFiling(BaseModel):
    """Tax filing submission model."""

    __tablename__ = "tax_filings"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tax details
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'PIT', 'VAT', etc.
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Filing status
    status: Mapped[str] = mapped_column(String(20), default="submitted")
    reference_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    # Declaration data (JSON)
    declaration_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    filed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Notes/comments
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tax_filings")

    def __repr__(self) -> str:
        return f"<TaxFiling {self.tax_type} {self.tax_year}: {self.status}>"


class TaxObligation(BaseModel):
    """Tax obligation tracking (calculated, not filed)."""

    __tablename__ = "tax_obligations"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Obligation details
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False)
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Calculation basis
    based_on: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    is_paid: Mapped[bool] = mapped_column(default=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<TaxObligation {self.tax_type} {self.tax_year}>"
