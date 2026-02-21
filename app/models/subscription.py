"""
Subscription model for plan management.
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


SubscriptionStatus = Literal["active", "cancelled", "expired", "trial"]
PlanId = Literal["free", "plus"]


class Subscription(BaseModel):
    """Subscription model for tracking user plans."""

    __tablename__ = "subscriptions"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Plan details
    plan_id: Mapped[str] = mapped_column(String(20), nullable=False)  # 'free', 'plus'
    status: Mapped[str] = mapped_column(String(20), default="active")

    # Payment info (optional)
    payment_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount_paid: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != "active":
            return False
        if self.expires_at and datetime.now(self.expires_at.tzinfo) > self.expires_at:
            return False
        return True

    def __repr__(self) -> str:
        return f"<Subscription {self.plan_id}: {self.status}>"


# Subscription plan definitions
SUBSCRIPTION_PLANS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": 0,
        "currency": "NGN",
        "billing_period": None,
        "features": [
            "Track Expenses",
            "Basic Reports",
            "Manual Transaction Entry",
            "Tax Estimates",
        ],
    },
    "plus": {
        "id": "plus",
        "name": "SabiTax Plus",
        "price": 5000,
        "currency": "NGN",
        "billing_period": "yearly",
        "features": [
            "Auto-Filing (PIT & VAT)",
            "Audit Defense",
            "Priority Support",
            "Bank Linking",
            "Receipt Scanning",
            "Unlimited Transactions",
            "Tax Optimization Tips",
        ],
    },
}
