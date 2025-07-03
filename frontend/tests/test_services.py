"""
Unit tests for frontend services.

This module provides comprehensive testing for all frontend services
including API client, authentication, and other service layers.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from frontend.services.api import APIClient
from frontend.services.auth_service import AuthService
from frontend.services.websocket_service import WebSocketService
from frontend.services.assistant_service import AssistantService
from frontend.services.conversation_service import ConversationService
from frontend.services.message_service import MessageService
from frontend.services.tool_service import ToolService
from frontend.services.knowledge_service import KnowledgeService
from frontend.services.user_service import UserService
from frontend.services.error_handler import ErrorHandler


class TestAPIClient:
    """Test cases for APIClient."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client instance."""
        return APIClient(base_url="http://localhost:8000")
    
    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {"success": True, "data": {"test": "value"}}
        mock.text = '{"success": true, "data": {"test": "value"}}'
        return mock
    
    @pytest.mark.asyncio
    async def test_get_request_success(self, api_client, mock_response):
        """Test successful GET request."""
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await api_client.get("/test")
            assert result["success"] is True
            assert result["data"]["test"] == "value"
    
    @pytest.mark.asyncio
    async def test_post_request_success(self, api_client, mock_response):
        """Test successful POST request."""
        with patch('httpx.AsyncClient.post', return_value=mock_response):
            result = await api_client.post("/test", {"key": "value"})
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_put_request_success(self, api_client, mock_response):
        """Test successful PUT request."""
        with patch('httpx.AsyncClient.put', return_value=mock_response):
            result = await api_client.put("/test/1", {"key": "value"})
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_delete_request_success(self, api_client, mock_response):
        """Test successful DELETE request."""
        with patch('httpx.AsyncClient.delete', return_value=mock_response):
            result = await api_client.delete("/test/1")
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_request_with_headers(self, api_client, mock_response):
        """Test request with custom headers."""
        with patch('httpx.AsyncClient.get', return_value=mock_response) as mock_get:
            await api_client.get("/test", headers={"Authorization": "Bearer token"})
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer token"
    
    @pytest.mark.asyncio
    async def test_request_error_handling(self, api_client):
        """Test error handling in requests."""
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Not found"}
        error_response.text = '{"error": "Not found"}'
        
        with patch('httpx.AsyncClient.get', return_value=error_response):
            with pytest.raises(Exception):
                await api_client.get("/test")


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        return AuthService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_login_success(self, auth_service, mock_api_client):
        """Test successful login."""
        auth_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {
                "access_token": "test_token",
                "user": {"id": 1, "email": "test@example.com"}
            }
        }
        
        result = auth_service.login("test@example.com", "password")
        assert result["success"] is True
        assert auth_service.is_authenticated() is True
    
    def test_login_failure(self, auth_service, mock_api_client):
        """Test failed login."""
        auth_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": False,
            "error": "Invalid credentials"
        }
        
        result = auth_service.login("test@example.com", "wrong_password")
        assert result["success"] is False
        assert auth_service.is_authenticated() is False
    
    def test_register_success(self, auth_service, mock_api_client):
        """Test successful registration."""
        auth_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"message": "User created successfully"}
        }
        
        result = auth_service.register("test@example.com", "password", "Test User")
        assert result["success"] is True
    
    def test_logout(self, auth_service):
        """Test logout functionality."""
        auth_service.token = "test_token"
        auth_service.user = {"id": 1}
        
        auth_service.logout()
        assert auth_service.token is None
        assert auth_service.user is None
        assert auth_service.is_authenticated() is False
    
    def test_token_validation(self, auth_service, mock_api_client):
        """Test token validation."""
        auth_service.api_client = mock_api_client
        auth_service.token = "test_token"
        
        mock_api_client.get.return_value = {
            "success": True,
            "data": {"user": {"id": 1}}
        }
        
        result = auth_service.validate_token()
        assert result["success"] is True
    
    def test_password_change(self, auth_service, mock_api_client):
        """Test password change."""
        auth_service.api_client = mock_api_client
        auth_service.token = "test_token"
        
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"message": "Password changed successfully"}
        }
        
        result = auth_service.change_password("old_password", "new_password")
        assert result["success"] is True


class TestWebSocketService:
    """Test cases for WebSocketService."""
    
    @pytest.fixture
    def websocket_service(self):
        """Create WebSocket service instance."""
        return WebSocketService()
    
    def test_connection_initialization(self, websocket_service):
        """Test WebSocket connection initialization."""
        assert websocket_service.is_connected() is False
        assert websocket_service.connection is None
    
    @pytest.mark.asyncio
    async def test_connect_success(self, websocket_service):
        """Test successful WebSocket connection."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await websocket_service.connect("ws://localhost:8000/ws")
            
            assert websocket_service.is_connected() is True
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message(self, websocket_service):
        """Test sending message through WebSocket."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await websocket_service.connect("ws://localhost:8000/ws")
            await websocket_service.send_message({"type": "test", "data": "value"})
            
            mock_websocket.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, websocket_service):
        """Test WebSocket disconnection."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await websocket_service.connect("ws://localhost:8000/ws")
            await websocket_service.disconnect()
            
            assert websocket_service.is_connected() is False
            mock_websocket.close.assert_called_once()


class TestAssistantService:
    """Test cases for AssistantService."""
    
    @pytest.fixture
    def assistant_service(self):
        """Create assistant service instance."""
        return AssistantService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_get_assistants(self, assistant_service, mock_api_client):
        """Test getting assistants list."""
        assistant_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "Assistant 1"},
                {"id": 2, "name": "Assistant 2"}
            ]
        }
        
        result = assistant_service.get_assistants()
        assert result["success"] is True
        assert len(result["data"]) == 2
    
    def test_create_assistant(self, assistant_service, mock_api_client):
        """Test creating assistant."""
        assistant_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"id": 1, "name": "New Assistant"}
        }
        
        result = assistant_service.create_assistant({
            "name": "New Assistant",
            "description": "Test assistant"
        })
        assert result["success"] is True
        assert result["data"]["name"] == "New Assistant"
    
    def test_update_assistant(self, assistant_service, mock_api_client):
        """Test updating assistant."""
        assistant_service.api_client = mock_api_client
        mock_api_client.put.return_value = {
            "success": True,
            "data": {"id": 1, "name": "Updated Assistant"}
        }
        
        result = assistant_service.update_assistant(1, {
            "name": "Updated Assistant"
        })
        assert result["success"] is True
    
    def test_delete_assistant(self, assistant_service, mock_api_client):
        """Test deleting assistant."""
        assistant_service.api_client = mock_api_client
        mock_api_client.delete.return_value = {
            "success": True,
            "data": {"message": "Assistant deleted"}
        }
        
        result = assistant_service.delete_assistant(1)
        assert result["success"] is True


class TestConversationService:
    """Test cases for ConversationService."""
    
    @pytest.fixture
    def conversation_service(self):
        """Create conversation service instance."""
        return ConversationService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_get_conversations(self, conversation_service, mock_api_client):
        """Test getting conversations list."""
        conversation_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Conversation 1"},
                {"id": 2, "title": "Conversation 2"}
            ]
        }
        
        result = conversation_service.get_conversations()
        assert result["success"] is True
        assert len(result["data"]) == 2
    
    def test_create_conversation(self, conversation_service, mock_api_client):
        """Test creating conversation."""
        conversation_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"id": 1, "title": "New Conversation"}
        }
        
        result = conversation_service.create_conversation({
            "title": "New Conversation",
            "assistant_id": 1
        })
        assert result["success"] is True
    
    def test_get_conversation_messages(self, conversation_service, mock_api_client):
        """Test getting conversation messages."""
        conversation_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "content": "Hello"},
                {"id": 2, "content": "Hi there"}
            ]
        }
        
        result = conversation_service.get_conversation_messages(1)
        assert result["success"] is True
        assert len(result["data"]) == 2


class TestMessageService:
    """Test cases for MessageService."""
    
    @pytest.fixture
    def message_service(self):
        """Create message service instance."""
        return MessageService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_send_message(self, message_service, mock_api_client):
        """Test sending message."""
        message_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"id": 1, "content": "Test message"}
        }
        
        result = message_service.send_message(1, "Test message")
        assert result["success"] is True
    
    def test_get_message_history(self, message_service, mock_api_client):
        """Test getting message history."""
        message_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "content": "Message 1"},
                {"id": 2, "content": "Message 2"}
            ]
        }
        
        result = message_service.get_message_history(1)
        assert result["success"] is True
        assert len(result["data"]) == 2


class TestToolService:
    """Test cases for ToolService."""
    
    @pytest.fixture
    def tool_service(self):
        """Create tool service instance."""
        return ToolService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_get_tools(self, tool_service, mock_api_client):
        """Test getting tools list."""
        tool_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "name": "Tool 1"},
                {"id": 2, "name": "Tool 2"}
            ]
        }
        
        result = tool_service.get_tools()
        assert result["success"] is True
        assert len(result["data"]) == 2
    
    def test_execute_tool(self, tool_service, mock_api_client):
        """Test executing tool."""
        tool_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"result": "Tool execution result"}
        }
        
        result = tool_service.execute_tool(1, {"param": "value"})
        assert result["success"] is True


class TestKnowledgeService:
    """Test cases for KnowledgeService."""
    
    @pytest.fixture
    def knowledge_service(self):
        """Create knowledge service instance."""
        return KnowledgeService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_get_documents(self, knowledge_service, mock_api_client):
        """Test getting documents list."""
        knowledge_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Document 1"},
                {"id": 2, "title": "Document 2"}
            ]
        }
        
        result = knowledge_service.get_documents()
        assert result["success"] is True
        assert len(result["data"]) == 2
    
    def test_upload_document(self, knowledge_service, mock_api_client):
        """Test uploading document."""
        knowledge_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": {"id": 1, "title": "Uploaded Document"}
        }
        
        result = knowledge_service.upload_document("test.pdf", b"file_content")
        assert result["success"] is True
    
    def test_search_documents(self, knowledge_service, mock_api_client):
        """Test searching documents."""
        knowledge_service.api_client = mock_api_client
        mock_api_client.post.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Search Result 1"}
            ]
        }
        
        result = knowledge_service.search_documents("test query")
        assert result["success"] is True


class TestUserService:
    """Test cases for UserService."""
    
    @pytest.fixture
    def user_service(self):
        """Create user service instance."""
        return UserService()
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return Mock()
    
    def test_get_user_profile(self, user_service, mock_api_client):
        """Test getting user profile."""
        user_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": {"id": 1, "email": "test@example.com"}
        }
        
        result = user_service.get_user_profile()
        assert result["success"] is True
        assert result["data"]["email"] == "test@example.com"
    
    def test_update_user_profile(self, user_service, mock_api_client):
        """Test updating user profile."""
        user_service.api_client = mock_api_client
        mock_api_client.put.return_value = {
            "success": True,
            "data": {"id": 1, "name": "Updated Name"}
        }
        
        result = user_service.update_user_profile({"name": "Updated Name"})
        assert result["success"] is True
    
    def test_get_user_statistics(self, user_service, mock_api_client):
        """Test getting user statistics."""
        user_service.api_client = mock_api_client
        mock_api_client.get.return_value = {
            "success": True,
            "data": {
                "total_conversations": 10,
                "total_messages": 100
            }
        }
        
        result = user_service.get_user_statistics()
        assert result["success"] is True
        assert result["data"]["total_conversations"] == 10


class TestErrorHandler:
    """Test cases for ErrorHandler."""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler instance."""
        return ErrorHandler()
    
    def test_handle_api_error(self, error_handler):
        """Test handling API errors."""
        error = Exception("API Error")
        result = error_handler.handle_error(error)
        assert result["success"] is False
        assert "error" in result
    
    def test_handle_network_error(self, error_handler):
        """Test handling network errors."""
        error = ConnectionError("Network Error")
        result = error_handler.handle_error(error)
        assert result["success"] is False
        assert "error" in result
    
    def test_handle_validation_error(self, error_handler):
        """Test handling validation errors."""
        error = ValueError("Validation Error")
        result = error_handler.handle_error(error)
        assert result["success"] is False
        assert "error" in result


# Integration tests
class TestServiceIntegration:
    """Integration tests for services."""
    
    @pytest.fixture
    def auth_service(self):
        """Create authenticated auth service."""
        service = AuthService()
        service.token = "test_token"
        service.user = {"id": 1, "email": "test@example.com"}
        return service
    
    @pytest.fixture
    def assistant_service(self, auth_service):
        """Create assistant service with authentication."""
        service = AssistantService()
        service.auth_service = auth_service
        return service
    
    def test_authenticated_request(self, assistant_service, mock_api_client):
        """Test that authenticated requests include token."""
        assistant_service.api_client = mock_api_client
        mock_api_client.get.return_value = {"success": True, "data": []}
        
        assistant_service.get_assistants()
        
        # Verify that the request included the authorization header
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert "headers" in call_args[1]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"


# Performance tests
class TestServicePerformance:
    """Performance tests for services."""
    
    @pytest.mark.asyncio
    async def test_api_client_performance(self):
        """Test API client performance."""
        client = APIClient(base_url="http://localhost:8000")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_get.return_value = mock_response
            
            # Test multiple concurrent requests
            tasks = [client.get("/test") for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 10
            assert all(result["success"] for result in results)
    
    @pytest.mark.asyncio
    async def test_websocket_performance(self):
        """Test WebSocket service performance."""
        service = WebSocketService()
        
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await service.connect("ws://localhost:8000/ws")
            
            # Test multiple message sends
            tasks = [
                service.send_message({"type": "test", "data": f"message_{i}"})
                for i in range(10)
            ]
            await asyncio.gather(*tasks)
            
            assert mock_websocket.send.call_count == 10


if __name__ == "__main__":
    pytest.main([__file__]) 