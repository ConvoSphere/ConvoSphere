"""
Unified tests for Chat API endpoints.

This module provides comprehensive testing of chat-related endpoints including:
- Conversation creation
- Message sending
- Conversation listing
- Message retrieval
- Conversation deletion
- Mode status checking

Tests are categorized by complexity and execution speed using pytest marks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation, Message
from backend.app.models.user import User
from backend.app.models.assistant import Assistant


class TestChatEndpoints:
    """Unified test suite for chat API endpoints."""

    # =============================================================================
    # FAST TESTS - Basic functionality with minimal mocking
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_success_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for successful conversation creation."""
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

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_validation_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for conversation creation validation."""
        # Empty title
        request_data = {"title": "", "assistant_id": "test-assistant-id"}
        response = client.post("/api/v1/chat/conversations", json=request_data, headers=test_user_headers)
        assert response.status_code == 422
        
        # Title too long
        request_data = {"title": "A" * 501, "assistant_id": "test-assistant-id"}
        response = client.post("/api/v1/chat/conversations", json=request_data, headers=test_user_headers)
        assert response.status_code == 422

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for conversation listing."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversations.return_value = {
                "conversations": [
                    {"id": "conv-1", "title": "Conversation 1", "created_at": "2024-01-01T00:00:00Z"},
                    {"id": "conv-2", "title": "Conversation 2", "created_at": "2024-01-02T00:00:00Z"}
                ],
                "total": 2,
                "page": 1,
                "per_page": 20
            }
            
            response = client.get("/api/v1/chat/conversations", headers=test_user_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data["conversations"]) == 2
            assert data["total"] == 2

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for conversation deletion."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.return_value = True
            
            response = client.delete("/api/v1/chat/conversations/conv-123", headers=test_user_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    # =============================================================================
    # COMPREHENSIVE TESTS - Full functionality with edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_create_conversation_service_error(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for service error handling."""
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

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_pagination_validation(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for pagination validation."""
        # Invalid page number
        response = client.get("/api/v1/chat/conversations?page=0", headers=test_user_headers)
        assert response.status_code == 422
        
        # Invalid per_page
        response = client.get("/api/v1/chat/conversations?per_page=0", headers=test_user_headers)
        assert response.status_code == 422
        
        # Per_page too large
        response = client.get("/api/v1/chat/conversations?per_page=101", headers=test_user_headers)
        assert response.status_code == 422

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversations_empty_result(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for empty conversation list."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversations.return_value = {
                "conversations": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            }
            
            response = client.get("/api/v1/chat/conversations", headers=test_user_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data["conversations"]) == 0
            assert data["total"] == 0

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_not_found(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for deleting non-existent conversation."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.side_effect = ValueError("Conversation not found")
            
            response = client.delete("/api/v1/chat/conversations/nonexistent", headers=test_user_headers)
            assert response.status_code == 404

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_delete_conversation_unauthorized(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for unauthorized conversation deletion."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.delete_conversation.side_effect = PermissionError("Not authorized")
            
            response = client.delete("/api/v1/chat/conversations/conv-123", headers=test_user_headers)
            assert response.status_code == 403

    # =============================================================================
    # MESSAGE TESTS - Message sending and retrieval
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_success_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for successful message sending."""
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

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_validation_comprehensive(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for message validation."""
        # Empty message
        request_data = {"message": "", "assistant_id": "test-assistant-id"}
        response = client.post("/api/v1/chat/conversations/conv-123/messages", json=request_data, headers=test_user_headers)
        assert response.status_code == 422
        
        # Message too long
        request_data = {"message": "A" * 10001, "assistant_id": "test-assistant-id"}
        response = client.post("/api/v1/chat/conversations/conv-123/messages", json=request_data, headers=test_user_headers)
        assert response.status_code == 422
        
        # Invalid parameters
        request_data = {
            "message": "Test message",
            "max_context_chunks": 0,  # Invalid: must be >= 1
            "temperature": 3.0  # Invalid: must be <= 2.0
        }
        response = client.post("/api/v1/chat/conversations/conv-123/messages", json=request_data, headers=test_user_headers)
        assert response.status_code == 422

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_send_message_engine_error(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for engine error handling."""
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

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for message retrieval."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_messages.return_value = {
                "messages": [
                    {"id": "msg-1", "content": "Hello", "role": "user", "created_at": "2024-01-01T00:00:00Z"},
                    {"id": "msg-2", "content": "Hi there!", "role": "assistant", "created_at": "2024-01-01T00:01:00Z"}
                ],
                "total": 2,
                "page": 1,
                "per_page": 50
            }
            
            response = client.get("/api/v1/chat/conversations/conv-123/messages", headers=test_user_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data["messages"]) == 2
            assert data["total"] == 2

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_validation(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for message retrieval validation."""
        # Invalid page number
        response = client.get("/api/v1/chat/conversations/conv-123/messages?page=0", headers=test_user_headers)
        assert response.status_code == 422
        
        # Per_page too large
        response = client.get("/api/v1/chat/conversations/conv-123/messages?per_page=201", headers=test_user_headers)
        assert response.status_code == 422

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_messages_not_found(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for non-existent conversation messages."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_messages.side_effect = ValueError("Conversation not found")
            
            response = client.get("/api/v1/chat/conversations/nonexistent/messages", headers=test_user_headers)
            assert response.status_code == 404

    # =============================================================================
    # ADVANCED FEATURE TESTS - Tool calls, metadata, custom models
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_tool_calls(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for message sending with tool calls."""
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

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_metadata(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for message sending with metadata."""
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

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_force_mode(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for forced conversation mode."""
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

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_send_message_with_custom_model(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for custom AI model usage."""
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

    # =============================================================================
    # MODE STATUS TESTS - Conversation mode management
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_mode_status_fast(self, client: TestClient, test_user_headers: dict):
        """Fast test for mode status retrieval."""
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
            
            response = client.get("/api/v1/chat/conversations/conv-123/mode/status", headers=test_user_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "hybrid"
            assert data["status"] == "active"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_conversation_mode_status_not_found(self, client: TestClient, test_user_headers: dict):
        """Comprehensive test for non-existent conversation mode status."""
        with patch('backend.app.api.v1.endpoints.chat.conversation_service') as mock_service:
            mock_service.get_conversation_mode_status.side_effect = ValueError("Conversation not found")
            
            response = client.get("/api/v1/chat/conversations/nonexistent/mode/status", headers=test_user_headers)
            assert response.status_code == 404

    # =============================================================================
    # SCHEMA VALIDATION TESTS - Request/Response structure validation
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_chat_message_request_validation(self):
        """Fast test for ChatMessageRequest validation."""
        from backend.app.api.v1.endpoints.chat import ChatMessageRequest
        
        # Test valid request
        valid_request = ChatMessageRequest(
            message="Valid message",
            assistant_id="test-assistant-id",
            use_knowledge_base=True,
            use_tools=True,
            max_context_chunks=5,
            temperature=0.7
        )
        assert valid_request.message == "Valid message"
        assert valid_request.assistant_id == "test-assistant-id"
        
        # Test invalid temperature
        with pytest.raises(ValueError):
            ChatMessageRequest(
                message="Test message",
                temperature=3.0  # Invalid: must be <= 2.0
            )
        
        # Test invalid max_context_chunks
        with pytest.raises(ValueError):
            ChatMessageRequest(
                message="Test message",
                max_context_chunks=0  # Invalid: must be >= 1
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_conversation_create_request_validation(self):
        """Fast test for ConversationCreateRequest validation."""
        from backend.app.api.v1.endpoints.chat import ConversationCreateRequest
        
        # Test valid request
        valid_request = ConversationCreateRequest(
            title="Valid Title",
            assistant_id="test-assistant-id",
            description="Valid description"
        )
        assert valid_request.title == "Valid Title"
        assert valid_request.assistant_id == "test-assistant-id"
        
        # Test empty title
        with pytest.raises(ValueError):
            ConversationCreateRequest(title="")
        
        # Test title too long
        with pytest.raises(ValueError):
            ConversationCreateRequest(title="A" * 501)  # Exceeds 500 character limit

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_chat_message_response_structure(self):
        """Fast test for ChatMessageResponse structure."""
        from backend.app.api.v1.endpoints.chat import ChatMessageResponse
        
        # Test response creation
        response = ChatMessageResponse(
            success=True,
            content="AI response",
            conversation_id="conv-123",
            message_id="msg-456",
            model_used="gpt-4",
            tokens_used=150,
            processing_time=1.5,
            tool_calls=[],
            mode_decision=None,
            reasoning_process=None
        )
        
        assert response.success is True
        assert response.content == "AI response"
        assert response.conversation_id == "conv-123"
        assert response.message_id == "msg-456"
        assert response.model_used == "gpt-4"
        assert response.tokens_used == 150
        assert response.processing_time == 1.5

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_conversation_list_response_structure(self):
        """Fast test for ConversationListResponse structure."""
        from backend.app.api.v1.endpoints.chat import ConversationListResponse
        
        # Test response creation
        response = ConversationListResponse(
            conversations=[
                {"id": "conv-1", "title": "Conversation 1"},
                {"id": "conv-2", "title": "Conversation 2"}
            ],
            total=2,
            page=1,
            per_page=20
        )
        
        assert len(response.conversations) == 2
        assert response.total == 2
        assert response.page == 1
        assert response.per_page == 20