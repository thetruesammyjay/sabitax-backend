"""
Referral model for tracking user referrals and rewards.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


ReferralStatus = Literal["pending", "completed", "expired"]


class Referral(BaseModel):
    """Referral model for tracking referrals and rewards."""

    __tablename__ = "referrals"

    # Referrer (user who invited)
    referrer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Referred user (new user who joined)
    referred_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Reward
    reward_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("1000.00"),
    )
    reward_paid: Mapped[bool] = mapped_column(default=False)

    # Completion timestamp
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    referrer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referrer_id],
        back_populates="referrals_made",
    )
    referred: Mapped["User"] = relationship(
        "User",
        foreign_keys=[referred_id],
        back_populates="referrals_received",
    )

    def __repr__(self) -> str:
        return f"<Referral {self.referrer_id} -> {self.referred_id}: {self.status}>"


# Referral configuration
REFERRAL_REWARD_AMOUNT = Decimal("1000.00")  # ₦1,000 per referral
MONTHLY_REFERRAL_LIMIT = Decimal("50000.00")  # ₦50,000 monthly cap
