"""
Bank Account model for linked bank accounts.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


BankProvider = Literal["mono", "okra"]
BankStatus = Literal["active", "inactive", "pending", "error"]


class BankAccount(BaseModel):
    """Linked bank account model."""

    __tablename__ = "bank_accounts"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider details
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # 'mono', 'okra'
    provider_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Bank details
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")

    # Sync info
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Link timestamp
    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="bank_accounts")

    @property
    def masked_account_number(self) -> str:
        """Return masked account number."""
        from app.core.utils import mask_account_number

        return mask_account_number(self.account_number) if self.account_number else ""

    def __repr__(self) -> str:
        return f"<BankAccount {self.bank_name}: {self.masked_account_number}>"
