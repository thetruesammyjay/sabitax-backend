"""
User model for authentication and profile management.
"""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.bank_account import BankAccount
    from app.models.chat import ChatMessage
    from app.models.notification import Notification
    from app.models.referral import Referral
    from app.models.subscription import Subscription
    from app.models.tax import TaxFiling
    from app.models.tin import TINApplication
    from app.models.transaction import Transaction


class User(BaseModel):
    """User model for SabiTax platform."""

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Social login
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    apple_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    # TIN (Tax Identification Number)
    tin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tin_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Subscription
    subscription_plan: Mapped[str] = mapped_column(String(20), default="free")

    # Referral
    referral_code: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )
    referred_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Activity tracking
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tax_filings: Mapped[list["TaxFiling"]] = relationship(
        "TaxFiling",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tin_applications: Mapped[list["TINApplication"]] = relationship(
        "TINApplication",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Self-referential relationship for referrals
    referrer: Mapped["User | None"] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[referred_by],
    )

    # People this user has referred
    referrals_made: Mapped[list["Referral"]] = relationship(
        "Referral",
        foreign_keys="[Referral.referrer_id]",
        back_populates="referrer",
    )

    # Referrals received (when this user was referred)
    referrals_received: Mapped[list["Referral"]] = relationship(
        "Referral",
        foreign_keys="[Referral.referred_id]",
        back_populates="referred",
    )

    @property
    def avatar_initials(self) -> str:
        """Generate avatar initials from name."""
        if not self.name:
            return self.email[0].upper()
        parts = self.name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.name[0].upper()

    def __repr__(self) -> str:
        return f"<User {self.email}>"
