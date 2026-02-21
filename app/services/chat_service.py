"""
Chat service for AI Tax Assistant integration.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.models.chat import TAX_ASSISTANT_SYSTEM_PROMPT, ChatMessage
from app.repositories.chat_repo import ChatRepository
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ClearChatResponse,
)


class ChatService:
    """AI Tax Assistant business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.settings = get_settings()

    async def send_message(
        self,
        user_id: uuid.UUID,
        message: str,
    ) -> ChatMessageResponse:
        """
        Send message to AI Tax Assistant and get response.

        Args:
            user_id: User's ID
            message: User's message

        Returns:
            ChatMessageResponse with assistant's reply
        """
        # Save user message
        user_message = ChatMessage(
            user_id=user_id,
            role="user",
            content=message,
        )
        user_message = await self.chat_repo.create(user_message)

        # Get recent context
        context_messages = await self.chat_repo.get_recent_context(user_id, limit=10)

        # Generate AI response
        assistant_response = await self._generate_response(message, context_messages)

        # Save assistant message
        assistant_message = ChatMessage(
            user_id=user_id,
            role="assistant",
            content=assistant_response,
        )
        assistant_message = await self.chat_repo.create(assistant_message)

        return ChatMessageResponse(
            id=str(assistant_message.id),
            role="assistant",
            content=assistant_response,
            created_at=assistant_message.created_at,
        )

    async def get_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> ChatHistoryResponse:
        """
        Get chat history.

        Args:
            user_id: User's ID
            limit: Max messages

        Returns:
            ChatHistoryResponse with message history
        """
        messages = await self.chat_repo.get_by_user(user_id, limit=limit)
        total = await self.chat_repo.count_by_user(user_id)

        return ChatHistoryResponse(
            messages=[
                ChatMessageResponse(
                    id=str(msg.id),
                    role=msg.role,  # type: ignore[arg-type]
                    content=msg.content,
                    created_at=msg.created_at,
                )
                for msg in messages
            ],
            total=total,
        )

    async def clear_history(
        self,
        user_id: uuid.UUID,
    ) -> ClearChatResponse:
        """
        Clear chat history.

        Args:
            user_id: User's ID

        Returns:
            ClearChatResponse with count of cleared messages
        """
        cleared_count = await self.chat_repo.clear_by_user(user_id)

        return ClearChatResponse(
            message="Chat history cleared",
            cleared_count=cleared_count,
        )

    async def _generate_response(
        self,
        message: str,
        context: list[ChatMessage],
    ) -> str:
        """
        Generate AI response using OpenAI.

        Args:
            message: Current user message
            context: Recent conversation context

        Returns:
            AI-generated response
        """
        import httpx

        # Use NexusBert API
        api_url = f"{self.settings.nexusbert_api_url.rstrip('/')}/ask"
        
        try:
            # Prepare multipart/form-data payload
            # NexusBert expects: question, session_id (optional), model (optional)
            form_data = {
                "question": message,
                "model": "gemini-2.5-flash",  # Default model in NexusBert
            }
            
            # If we had a session ID from the context, we could pass it, but
            # since we are managing history ourselves, we treat each request as
            # stateless or generate a temp session if needed.
            # Using a static or random session ID for now as we store history in our DB.
            form_data["session_id"] = str(uuid.uuid4())

            headers = {}
            if self.settings.nexusbert_api_key:
                 headers["X-API-Key"] = self.settings.nexusbert_api_key

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    data=form_data,
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    # NexusBert returns:
                    # {
                    #   "answer": "...",
                    #   "sources": [...],
                    #   "chunks_used": ...,
                    #   "session_id": "..."
                    # }
                    return data.get("answer", "I couldn't generate a response.")
                else:
                    # Fallback if API fails
                    return self._get_fallback_response(message)

        except Exception as e:
            # Return fallback on any error
            return self._get_fallback_response(message)

    def _get_fallback_response(self, message: str) -> str:
        """
        Generate fallback response when AI is unavailable.

        Args:
            message: User's message

        Returns:
            Fallback response
        """
        message_lower = message.lower()

        if "tax" in message_lower and "when" in message_lower:
            return (
                "Personal Income Tax (PIT) in Nigeria is due by March 31st each year "
                "for self-employed individuals and businesses. If you're employed, "
                "your employer handles PAYE monthly. For specific deadlines, I recommend "
                "checking with FIRS or a tax professional."
            )

        if "tin" in message_lower:
            return (
                "A Tax Identification Number (TIN) is required for all taxpayers in Nigeria. "
                "You can apply for a TIN through the Joint Tax Board (JTB) registration portal "
                "or through FIRS. You'll need your NIN and valid ID document. "
                "Use the TIN Application feature in this app to get started!"
            )

        if "vat" in message_lower:
            return (
                "VAT in Nigeria is currently 7.5%. It applies to the supply of goods and services, "
                "except those explicitly exempted (basic food items, medical services, etc.). "
                "VAT-registered businesses must remit VAT by the 21st of each month."
            )

        if "deduction" in message_lower or "relief" in message_lower:
            return (
                "Nigerian tax law provides several reliefs and deductions:\n"
                "• Consolidated Relief Allowance (CRA): ₦200,000 or 1% of gross income + 20% of gross income\n"
                "• Pension contributions (up to 20% of basic salary)\n"
                "• Life insurance premiums\n"
                "• National Housing Fund contributions (2.5% of basic)\n\n"
                "Check the Tax Optimization section for personalized suggestions!"
            )

        return (
            "I'm your Nigerian Tax Assistant, here to help with tax-related questions. "
            "I can help you understand:\n"
            "• Personal Income Tax (PIT) calculations\n"
            "• VAT requirements\n"
            "• Tax reliefs and deductions\n"
            "• TIN registration\n"
            "• Filing deadlines\n\n"
            "What would you like to know about Nigerian taxes?"
        )
