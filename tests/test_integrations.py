import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chat_service import ChatService
from app.services.bank_service import BankService
from app.schemas.chat import ChatMessageResponse
from app.schemas.bank import LinkBankResponse

@pytest.mark.asyncio
async def test_chat_service_nexusbert(db_session):
    service = ChatService(db_session)
    user_id = uuid.uuid4()
    message = "What are the tax brackets?"

    # Mock the settings to have a URL and key
    with patch("app.services.chat_service.get_settings") as mock_settings:
        mock_settings.return_value.nexusbert_api_url = "https://mock-sabitax-ai.com"
        mock_settings.return_value.nexusbert_api_key = "test-key"

        # Re-initialize to pick up mocked settings if they are cached in __init__
        service = ChatService(db_session)
        service.settings = mock_settings.return_value

        # Mock httpx.AsyncClient as an async context manager
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "Tax brackets are 7%, 11%, etc.",
            "sources": [],
            "session_id": "123"
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
            mock_client_cls.return_value.__aexit__.return_value = False

            response = await service.send_message(user_id, message)

            assert isinstance(response, ChatMessageResponse)
            assert response.content == "Tax brackets are 7%, 11%, etc."
            assert response.role == "assistant"

            # Verify the API was called correctly
            args, kwargs = mock_client_instance.post.call_args
            assert args[0] == "https://mock-sabitax-ai.com/ask"
            assert kwargs["data"]["question"] == message
            assert "X-API-Key" in kwargs["headers"]

@pytest.mark.asyncio
async def test_bank_service_initiate_link_mono(db_session):
    service = BankService(db_session)
    user_id = uuid.uuid4()
    
    # Mock UserRepository to return a user
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    
    with patch("app.services.bank_service.get_settings") as mock_settings:
        mock_settings.return_value.mono_secret_key = "test-mono-key"
        service = BankService(db_session)
        service.settings = mock_settings.return_value
        
        # Mock the user repository lookup
        with patch("app.repositories.user_repo.UserRepository.get_by_id", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user
            
            # Mock httpx.AsyncClient as an async context manager
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "session_123"}

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
                mock_client_cls.return_value.__aexit__.return_value = False

                response = await service.initiate_link(user_id, "mono")
                
                assert isinstance(response, LinkBankResponse)
                assert response.session_id == "session_123"
                assert "connect.withmono.com" in response.widget_url
                
                # Verify API call
                args, kwargs = mock_client_instance.post.call_args
                assert args[0] == "https://api.withmono.com/v2/connect/session"
                assert kwargs["json"]["customer"]["id"] == str(user_id)
