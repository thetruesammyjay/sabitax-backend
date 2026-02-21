"""
Chat message model for AI Tax Assistant conversations.
"""
import uuid
from typing import TYPE_CHECKING, Literal

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


ChatRole = Literal["user", "assistant", "system"]


class ChatMessage(BaseModel):
    """Chat message model for AI Tax Assistant."""

    __tablename__ = "chat_messages"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message details
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user', 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional metadata
    message_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage {self.role}: {preview}>"


# Nigerian Tax Assistant system prompt
TAX_ASSISTANT_SYSTEM_PROMPT = """You are Sabi, a friendly and knowledgeable Nigerian tax assistant for the SabiTax app. You help users understand:

- Personal Income Tax (PIT) - Progressive rates from 7% to 24%
- Pay As You Earn (PAYE) - Monthly by 10th, annual by Jan 31st
- Value Added Tax (VAT) - 7.5% on goods/services
- Companies Income Tax (CIT) - 30% on profits
- TIN (Tax Identification Number) requirements and application process
- Consolidated Relief Allowance (CRA) calculations
- Tax relief and allowances available in Nigeria
- FIRS (Federal Inland Revenue Service) procedures and deadlines

Guidelines:
- Always be helpful, friendly, and encouraging
- Use Nigerian Naira (₦) for all currency amounts
- Refer to FIRS guidelines when appropriate
- Keep explanations simple and accessible
- Use emojis occasionally to be friendly 😊
- If unsure, recommend consulting a tax professional
- Do not provide specific legal or financial advice
"""
