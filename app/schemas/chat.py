"""
Chat schemas for AI Tax Assistant.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ChatRole = Literal["user", "assistant"]


class ChatMessageRequest(BaseModel):
    """Send chat message request."""

    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Chat message response."""

    id: str
    role: ChatRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Chat history response."""

    messages: list[ChatMessageResponse]
    total: int


class ClearChatResponse(BaseModel):
    """Clear chat history response."""

    message: str
    cleared_count: int
