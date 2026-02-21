"""
Transaction model for income and expense tracking.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


TransactionType = Literal["income", "expense"]


class Transaction(BaseModel):
    """Transaction model for tracking income and expenses."""

    __tablename__ = "transactions"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'income' or 'expense'
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Receipt handling
    receipt_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Date of transaction
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Description/notes
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="transactions")

    @property
    def formatted_amount(self) -> str:
        """Return formatted amount with sign and currency."""
        from app.core.utils import format_naira

        if self.type == "income":
            return format_naira(self.amount, show_sign=True)
        return format_naira(-self.amount, show_sign=True)

    def __repr__(self) -> str:
        return f"<Transaction {self.title}: {self.formatted_amount}>"


# Common transaction categories
INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Business",
    "Investment",
    "Gift",
    "Other Income",
]

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Rent",
    "Utilities",
    "Other Expense",
]
