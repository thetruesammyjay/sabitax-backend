"""
Chat message repository for database operations.
"""
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage


class ChatRepository:
    """Chat message database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message."""
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def create_batch(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Create multiple chat messages."""
        self.db.add_all(messages)
        await self.db.flush()
        for message in messages:
            await self.db.refresh(message)
        return messages

    async def get_by_id(
        self,
        message_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> ChatMessage | None:
        """Get chat message by ID."""
        query = select(ChatMessage).where(ChatMessage.id == message_id)
        if user_id:
            query = query.where(ChatMessage.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        before_id: uuid.UUID | None = None,
    ) -> list[ChatMessage]:
        """Get chat messages for a user, ordered by creation time."""
        query = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
        )

        if before_id:
            # Get messages older than the specified message
            subquery = select(ChatMessage.created_at).where(ChatMessage.id == before_id)
            query = query.where(ChatMessage.created_at < subquery.scalar_subquery())

        query = query.limit(limit)
        result = await self.db.execute(query)
        # Reverse to get chronological order
        return list(reversed(result.scalars().all()))

    async def get_recent_context(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> list[ChatMessage]:
        """Get recent messages for context (ordered chronologically)."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def count_by_user(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Count messages for a user."""
        result = await self.db.execute(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.user_id == user_id)
        )
        return result.scalar() or 0

    async def clear_by_user(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Delete all messages for a user."""
        result = await self.db.execute(
            delete(ChatMessage).where(ChatMessage.user_id == user_id)
        )
        return result.rowcount  # type: ignore
