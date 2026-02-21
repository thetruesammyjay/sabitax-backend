"""
AI Chat endpoints.
"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ClearChatResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("", response_model=ChatMessageResponse)
async def send_chat_message(
    data: ChatMessageRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Send message to AI Tax Assistant.

    Returns AI response with Nigerian tax expertise.
    """
    service = ChatService(db)
    return await service.send_message(
        user_id=current_user.id,
        message=data.message,
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100, description="Max messages to return"),
):
    """
    Get chat history.

    Returns conversation history with AI Tax Assistant.
    """
    service = ChatService(db)
    return await service.get_history(
        user_id=current_user.id,
        limit=limit,
    )


@router.delete("/history", response_model=ClearChatResponse)
async def clear_chat_history(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Clear chat history.

    Deletes all messages with AI Tax Assistant.
    """
    service = ChatService(db)
    return await service.clear_history(current_user.id)
