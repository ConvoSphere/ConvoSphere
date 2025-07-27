"""
Comprehensive tests for Chat API endpoints.

This module tests all chat-related endpoints including:
- Conversation creation
- Message sending
- Conversation listing
- Message retrieval
- Conversation deletion
- Mode status checking
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation, Message
from backend.app.models.user import User
from backend.app.models.assistant import Assistant


class TestChatEndpoints:
    """Test suite for chat API endpoints."""

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_success(self, client: TestClient, test_user_headers: dict):
        """Test successful conversation creation."""
        request_data = {
            "title": "Test Conversation",
            "assistant_id": "test-assistant-id",
            "description": "A test conversation"
        }
        
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.create_conversation.return_value = {
                "id": "conv-123",
                "title": "Test Conversation",
                "assistant_id": "test-assistant-id",
                "user_id": "user-123",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            response = client.post(
                "/api/v1/chat/conversations",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "conv-123"
            assert data["title"] == "Test Conversation"
            mock_service.create_conversation.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_invalid_title(self, client: TestClient, test_user_headers: dict):
        """Test conversation creation with invalid title."""
        request_data = {
            "title": "",  # Empty title
            "assistant_id": "test-assistant-id"
        }
        
        response = client.post(
            "/api/v1/chat/conversations",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_title_too_long(self, client: TestClient, test_user_headers: dict):
        """Test conversation creation with title too long."""
        request_data = {
            "title": "A" * 501,  # Exceeds 500 character limit
            "assistant_id": "test-assistant-id"
        }
        
        response = client.post(
            "/api/v1/chat/conversations",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_service_error(self, client: TestClient, test_user_headers: dict):
        """Test conversation creation when service raises an error."""
        request_data = {
            "title": "Test Conversation",
            "assistant_id": "test-assistant-id"
        }
        
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.create_conversation.side_effect = Exception("Service error")
            
            response = client.post(
                "/api/v1/chat/conversations",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 500

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_success(self, client: TestClient, test_user_headers: dict):
        """Test successful conversation listing."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversations.return_value = {
                "conversations": [
                    {
                        "id": "conv-1",
                        "title": "Conversation 1",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    {
                        "id": "conv-2", 
                        "title": "Conversation 2",
                        "created_at": "2024-01-02T00:00:00Z"
                    }
                ],
                "total": 2,
                "page": 1,
                "per_page": 20
            }
            
            response = client.get(
                "/api/v1/chat/conversations?page=1&per_page=20",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["conversations"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 20

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_invalid_pagination(self, client: TestClient, test_user_headers: dict):
        """Test conversation listing with invalid pagination parameters."""
        # Test invalid page number
        response = client.get(
            "/api/v1/chat/conversations?page=0",
            headers=test_user_headers
        )
        assert response.status_code == 422
        
        # Test invalid per_page
        response = client.get(
            "/api/v1/chat/conversations?per_page=0",
            headers=test_user_headers
        )
        assert response.status_code == 422
        
        # Test per_page too large
        response = client.get(
            "/api/v1/chat/conversations?per_page=101",
            headers=test_user_headers
        )
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_empty_result(self, client: TestClient, test_user_headers: dict):
        """Test conversation listing with empty result."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversations.return_value = {
                "conversations": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            }
            
            response = client.get(
                "/api/v1/chat/conversations",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["conversations"]) == 0
            assert data["total"] == 0

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_success(self, client: TestClient, test_user_headers: dict):
        """Test successful message sending."""
        request_data = {
            "message": "Hello, this is a test message",
            "assistant_id": "test-assistant-id",
            "use_knowledge_base": True,
            "use_tools": True,
            "max_context_chunks": 5,
            "temperature": 0.7
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.return_value = {
                "success": True,
                "content": "Hello! I'm here to help.",
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "model_used": "gpt-4",
                "tokens_used": 150,
                "processing_time": 1.5,
                "tool_calls": [],
                "mode_decision": None,
                "reasoning_process": None
            }
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["content"] == "Hello! I'm here to help."
            assert data["conversation_id"] == "conv-123"
            assert data["message_id"] == "msg-456"

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_invalid_message(self, client: TestClient, test_user_headers: dict):
        """Test message sending with invalid message."""
        # Empty message
        request_data = {
            "message": "",
            "assistant_id": "test-assistant-id"
        }
        
        response = client.post(
            "/api/v1/chat/conversations/conv-123/messages",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 422
        
        # Message too long
        request_data = {
            "message": "A" * 10001,  # Exceeds 10000 character limit
            "assistant_id": "test-assistant-id"
        }
        
        response = client.post(
            "/api/v1/chat/conversations/conv-123/messages",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_invalid_parameters(self, client: TestClient, test_user_headers: dict):
        """Test message sending with invalid parameters."""
        request_data = {
            "message": "Test message",
            "max_context_chunks": 0,  # Invalid: must be >= 1
            "temperature": 3.0  # Invalid: must be <= 2.0
        }
        
        response = client.post(
            "/api/v1/chat/conversations/conv-123/messages",
            json=request_data,
            headers=test_user_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_engine_error(self, client: TestClient, test_user_headers: dict):
        """Test message sending when assistant engine fails."""
        request_data = {
            "message": "Test message",
            "assistant_id": "test-assistant-id"
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.side_effect = Exception("Engine error")
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 500

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_success(self, client: TestClient, test_user_headers: dict):
        """Test successful message retrieval."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_messages.return_value = {
                "messages": [
                    {
                        "id": "msg-1",
                        "content": "Hello",
                        "role": "user",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    {
                        "id": "msg-2",
                        "content": "Hi there!",
                        "role": "assistant",
                        "created_at": "2024-01-01T00:01:00Z"
                    }
                ],
                "total": 2,
                "page": 1,
                "per_page": 50
            }
            
            response = client.get(
                "/api/v1/chat/conversations/conv-123/messages?page=1&per_page=50",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["messages"]) == 2
            assert data["total"] == 2

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_invalid_pagination(self, client: TestClient, test_user_headers: dict):
        """Test message retrieval with invalid pagination."""
        # Test invalid page number
        response = client.get(
            "/api/v1/chat/conversations/conv-123/messages?page=0",
            headers=test_user_headers
        )
        assert response.status_code == 422
        
        # Test per_page too large
        response = client.get(
            "/api/v1/chat/conversations/conv-123/messages?per_page=201",
            headers=test_user_headers
        )
        assert response.status_code == 422

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_not_found(self, client: TestClient, test_user_headers: dict):
        """Test message retrieval for non-existent conversation."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_messages.side_effect = ValueError("Conversation not found")
            
            response = client.get(
                "/api/v1/chat/conversations/nonexistent/messages",
                headers=test_user_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_success(self, client: TestClient, test_user_headers: dict):
        """Test successful conversation deletion."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.return_value = True
            
            response = client.delete(
                "/api/v1/chat/conversations/conv-123",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_service.delete_conversation.assert_called_once_with("conv-123", "user-123")

    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_not_found(self, client: TestClient, test_user_headers: dict):
        """Test conversation deletion for non-existent conversation."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.side_effect = ValueError("Conversation not found")
            
            response = client.delete(
                "/api/v1/chat/conversations/nonexistent",
                headers=test_user_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_unauthorized(self, client: TestClient, test_user_headers: dict):
        """Test conversation deletion without authorization."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.side_effect = PermissionError("Not authorized")
            
            response = client.delete(
                "/api/v1/chat/conversations/conv-123",
                headers=test_user_headers
            )
            
            assert response.status_code == 403

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_mode_status_success(self, client: TestClient, test_user_headers: dict):
        """Test successful mode status retrieval."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_mode_status.return_value = {
                "mode": "hybrid",
                "status": "active",
                "last_updated": "2024-01-01T00:00:00Z",
                "config": {
                    "use_knowledge_base": True,
                    "use_tools": True
                }
            }
            
            response = client.get(
                "/api/v1/chat/conversations/conv-123/mode/status",
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "hybrid"
            assert data["status"] == "active"

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_mode_status_not_found(self, client: TestClient, test_user_headers: dict):
        """Test mode status retrieval for non-existent conversation."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_mode_status.side_effect = ValueError("Conversation not found")
            
            response = client.get(
                "/api/v1/chat/conversations/nonexistent/mode/status",
                headers=test_user_headers
            )
            
            assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_tool_calls(self, client: TestClient, test_user_headers: dict):
        """Test message sending with tool calls."""
        request_data = {
            "message": "Search for information about AI",
            "use_tools": True,
            "assistant_id": "test-assistant-id"
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.return_value = {
                "success": True,
                "content": "I found some information about AI.",
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "model_used": "gpt-4",
                "tokens_used": 200,
                "processing_time": 2.0,
                "tool_calls": [
                    {
                        "tool": "search",
                        "parameters": {"query": "AI information"},
                        "result": "Found AI information"
                    }
                ],
                "mode_decision": {
                    "mode": "tool_usage",
                    "reasoning": "User requested search"
                },
                "reasoning_process": [
                    {"step": "analyze", "reasoning": "User wants information about AI"}
                ]
            }
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["tool_calls"]) == 1
            assert data["tool_calls"][0]["tool"] == "search"
            assert data["mode_decision"]["mode"] == "tool_usage"

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_metadata(self, client: TestClient, test_user_headers: dict):
        """Test message sending with additional metadata."""
        request_data = {
            "message": "Test message with metadata",
            "assistant_id": "test-assistant-id",
            "metadata": {
                "source": "web_client",
                "session_id": "session-123",
                "user_agent": "test-browser"
            }
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.return_value = {
                "success": True,
                "content": "Response with metadata",
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "model_used": "gpt-4",
                "tokens_used": 100,
                "processing_time": 1.0,
                "tool_calls": [],
                "mode_decision": None,
                "reasoning_process": None
            }
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_force_mode(self, client: TestClient, test_user_headers: dict):
        """Test message sending with forced conversation mode."""
        request_data = {
            "message": "Force specific mode",
            "assistant_id": "test-assistant-id",
            "force_mode": "structured"
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.return_value = {
                "success": True,
                "content": "Structured response",
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "model_used": "gpt-4",
                "tokens_used": 150,
                "processing_time": 1.5,
                "tool_calls": [],
                "mode_decision": {
                    "mode": "structured",
                    "reasoning": "Forced by user"
                },
                "reasoning_process": None
            }
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mode_decision"]["mode"] == "structured"

    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_custom_model(self, client: TestClient, test_user_headers: dict):
        """Test message sending with custom AI model."""
        request_data = {
            "message": "Test with custom model",
            "assistant_id": "test-assistant-id",
            "model": "gpt-4-turbo",
            "temperature": 0.5,
            "max_tokens": 500
        }
        
        with patch('backend.app.api.v1.endpoints.chat.assistant_engine') as mock_engine:
            mock_engine.process_message.return_value = {
                "success": True,
                "content": "Response from custom model",
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "model_used": "gpt-4-turbo",
                "tokens_used": 300,
                "processing_time": 2.0,
                "tool_calls": [],
                "mode_decision": None,
                "reasoning_process": None
            }
            
            response = client.post(
                "/api/v1/chat/conversations/conv-123/messages",
                json=request_data,
                headers=test_user_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["model_used"] == "gpt-4-turbo"
            assert data["tokens_used"] == 300