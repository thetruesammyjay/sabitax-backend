import asyncio
import uuid
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.chat_service import ChatService
from app.services.bank_service import BankService
from app.schemas.chat import ChatMessageResponse
from app.schemas.bank import LinkBankResponse

# Mock DB Session
mock_db_session = MagicMock()

async def test_chat_service_nexusbert():
    print("Testing NexusBert Integration...", end=" ")
    service = ChatService(mock_db_session)
    user_id = uuid.uuid4()
    message = "What are the tax brackets?"

    with patch("app.services.chat_service.get_settings") as mock_settings:
        mock_settings.return_value.nexusbert_api_url = "https://mock-nexusbert.com"
        mock_settings.return_value.nexusbert_api_key = "test-key"
        
        service = ChatService(mock_db_session)
        service.settings = mock_settings.return_value
        # Mock chat repo
        service.chat_repo = AsyncMock()
        service.chat_repo.create.return_value = MagicMock(id=uuid.uuid4(), created_at="now")

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "answer": "Tax brackets are 7%, 11%, etc.",
                "sources": [],
                "session_id": "123"
            }

            response = await service.send_message(user_id, message)
            
            assert isinstance(response, ChatMessageResponse)
            assert response.content == "Tax brackets are 7%, 11%, etc."
            assert response.role == "assistant"
            print("PASSED")

async def test_bank_service_initiate_link_mono():
    print("Testing Mono Initiate Link...", end=" ")
    service = BankService(mock_db_session)
    user_id = uuid.uuid4()
    
    mock_user = AsyncMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    
    with patch("app.repositories.user_repo.UserRepository.get_by_id", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = mock_user
        
        with patch("app.services.bank_service.get_settings") as mock_settings:
            mock_settings.return_value.mono_secret_key = "test-mono-key"
            service = BankService(mock_db_session)
            service.settings = mock_settings.return_value
            
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {"id": "session_123"}
                
                response = await service.initiate_link(user_id, "mono")
                
                assert isinstance(response, LinkBankResponse)
                assert response.session_id == "session_123"
                assert "connect.withmono.com" in response.widget_url
                print("PASSED")

async def main():
    try:
        await test_chat_service_nexusbert()
        await test_bank_service_initiate_link_mono()
        print("\nAll integration verification tests PASSED.")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
