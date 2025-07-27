"""
Comprehensive tests for WebSocket API endpoints.

This module tests all WebSocket functionality including:
- Connection management
- Message handling
- Real-time chat features
- Knowledge base integration
- Typing indicators
- Processing job updates
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.conversation import Conversation, Message


class TestWebSocketEndpoints:
    """Test suite for WebSocket API endpoints."""

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_general_connection_success(self, client: TestClient):
        """Test successful general WebSocket connection."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth.return_value = mock_user
            
            with client.websocket_connect("/api/v1/websocket/?token=valid-token") as websocket:
                # Test connection establishment
                data = websocket.receive_text()
                message = json.loads(data)
                
                assert message["type"] == "connection_established"
                assert message["data"]["user_id"] == "user-123"
                assert message["data"]["message"] == "Connected to general WebSocket"
                
                # Test ping/pong
                websocket.send_text(json.dumps({"type": "ping"}))
                pong_data = websocket.receive_text()
                pong_message = json.loads(pong_data)
                
                assert pong_message["type"] == "pong"
                assert "timestamp" in pong_message["data"]

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_general_authentication_failure(self, client: TestClient):
        """Test general WebSocket connection with invalid token."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            mock_auth.return_value = None
            
            with pytest.raises(Exception):  # WebSocket connection should fail
                with client.websocket_connect("/api/v1/websocket/?token=invalid-token") as websocket:
                    pass

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_conversation_connection_success(self, client: TestClient):
        """Test successful conversation WebSocket connection."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_conv = MagicMock()
                mock_conv.id = "conv-123"
                mock_conv.user_id = "user-123"
                mock_conversation.query.filter.return_value.first.return_value = mock_conv
                
                with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                    # Test connection establishment
                    data = websocket.receive_text()
                    message = json.loads(data)
                    
                    assert message["type"] == "connection_established"
                    assert message["data"]["user_id"] == "user-123"
                    assert message["data"]["conversation_id"] == "conv-123"
                    assert message["data"]["message"] == "Connected to chat"

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_conversation_access_denied(self, client: TestClient):
        """Test conversation WebSocket connection with access denied."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                # Conversation not found or access denied
                mock_conversation.query.filter.return_value.first.return_value = None
                
                with pytest.raises(Exception):  # WebSocket connection should fail
                    with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                        pass

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, client: TestClient):
        """Test WebSocket message handling in conversation."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                with patch('backend.app.api.v1.endpoints.websocket.ConversationService') as mock_conv_service:
                    with patch('backend.app.api.v1.endpoints.websocket.AIService') as mock_ai_service:
                        with patch('backend.app.api.v1.endpoints.websocket.KnowledgeService') as mock_knowledge_service:
                            mock_user = MagicMock()
                            mock_user.id = "user-123"
                            mock_auth.return_value = mock_user
                            
                            mock_conv = MagicMock()
                            mock_conv.id = "conv-123"
                            mock_conv.user_id = "user-123"
                            mock_conversation.query.filter.return_value.first.return_value = mock_conv
                            
                            # Mock services
                            mock_conv_service_instance = MagicMock()
                            mock_conv_service.return_value = mock_conv_service_instance
                            mock_conv_service_instance.add_message.return_value = "msg-456"
                            
                            mock_ai_service_instance = MagicMock()
                            mock_ai_service.return_value = mock_ai_service_instance
                            mock_ai_service_instance.process_message.return_value = {
                                "content": "AI response",
                                "model_used": "gpt-4",
                                "tokens_used": 100
                            }
                            
                            mock_knowledge_service_instance = MagicMock()
                            mock_knowledge_service.return_value = mock_knowledge_service_instance
                            mock_knowledge_service_instance.search_documents.return_value = []
                            
                            with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                                # Send a message
                                message_data = {
                                    "type": "message",
                                    "data": {
                                        "content": "Hello, AI!",
                                        "knowledgeContext": True
                                    }
                                }
                                websocket.send_text(json.dumps(message_data))
                                
                                # Should receive AI response
                                response_data = websocket.receive_text()
                                response_message = json.loads(response_data)
                                
                                assert response_message["type"] == "ai_response"
                                assert "content" in response_message["data"]

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_typing_indicator(self, client: TestClient):
        """Test WebSocket typing indicator functionality."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_conv = MagicMock()
                mock_conv.id = "conv-123"
                mock_conv.user_id = "user-123"
                mock_conversation.query.filter.return_value.first.return_value = mock_conv
                
                with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                    # Send typing indicator
                    typing_data = {
                        "type": "typing",
                        "data": {
                            "is_typing": True,
                            "user_id": "user-123"
                        }
                    }
                    websocket.send_text(json.dumps(typing_data))
                    
                    # Should receive typing indicator broadcast
                    response_data = websocket.receive_text()
                    response_message = json.loads(response_data)
                    
                    assert response_message["type"] == "typing_indicator"
                    assert response_message["data"]["is_typing"] is True
                    assert response_message["data"]["user_id"] == "user-123"

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_knowledge_search(self, client: TestClient):
        """Test WebSocket knowledge search functionality."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                with patch('backend.app.api.v1.endpoints.websocket.KnowledgeService') as mock_knowledge_service:
                    mock_user = MagicMock()
                    mock_user.id = "user-123"
                    mock_auth.return_value = mock_user
                    
                    mock_conv = MagicMock()
                    mock_conv.id = "conv-123"
                    mock_conv.user_id = "user-123"
                    mock_conversation.query.filter.return_value.first.return_value = mock_conv
                    
                    mock_knowledge_service_instance = MagicMock()
                    mock_knowledge_service.return_value = mock_knowledge_service_instance
                    mock_knowledge_service_instance.search_documents.return_value = [
                        {"id": "doc-1", "title": "Test Document", "content": "Test content"}
                    ]
                    
                    with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                        # Send knowledge search request
                        search_data = {
                            "type": "knowledge_search",
                            "data": {
                                "query": "test query",
                                "max_results": 5
                            }
                        }
                        websocket.send_text(json.dumps(search_data))
                        
                        # Should receive knowledge update
                        response_data = websocket.receive_text()
                        response_message = json.loads(response_data)
                        
                        assert response_message["type"] == "knowledge_update"
                        assert "documents" in response_message["data"]
                        assert "search_query" in response_message["data"]

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_processing_job_update(self, client: TestClient):
        """Test WebSocket processing job update functionality."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_conv = MagicMock()
                mock_conv.id = "conv-123"
                mock_conv.user_id = "user-123"
                mock_conversation.query.filter.return_value.first.return_value = mock_conv
                
                with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                    # Send processing job update
                    job_data = {
                        "type": "processing_job_update",
                        "data": {
                            "job_id": "job-123",
                            "status": "processing",
                            "progress": 50
                        }
                    }
                    websocket.send_text(json.dumps(job_data))
                    
                    # Should receive job update confirmation
                    response_data = websocket.receive_text()
                    response_message = json.loads(response_data)
                    
                    assert response_message["type"] == "job_update_received"
                    assert response_message["data"]["job_id"] == "job-123"

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_invalid_message_type(self, client: TestClient):
        """Test WebSocket handling of invalid message types."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_conv = MagicMock()
                mock_conv.id = "conv-123"
                mock_conv.user_id = "user-123"
                mock_conversation.query.filter.return_value.first.return_value = mock_conv
                
                with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                    # Send invalid message type
                    invalid_data = {
                        "type": "invalid_type",
                        "data": {}
                    }
                    websocket.send_text(json.dumps(invalid_data))
                    
                    # Should receive error response
                    response_data = websocket.receive_text()
                    response_message = json.loads(response_data)
                    
                    assert response_message["type"] == "error"
                    assert "Unknown message type" in response_message["data"]["message"]

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_connection_manager(self):
        """Test ConnectionManager functionality."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        # Test connection tracking
        mock_websocket = MagicMock()
        user_id = "user-123"
        conversation_id = "conv-123"
        
        # Test connect
        await manager.connect(mock_websocket, user_id, conversation_id)
        
        connection_id = f"{user_id}_{conversation_id}"
        assert connection_id in manager.active_connections
        assert conversation_id in manager.conversation_connections
        assert user_id in manager.user_connections
        
        # Test send personal message
        await manager.send_personal_message("test message", user_id, conversation_id)
        mock_websocket.send_text.assert_called_with("test message")
        
        # Test disconnect
        manager.disconnect(user_id, conversation_id)
        assert connection_id not in manager.active_connections
        assert conversation_id not in manager.conversation_connections
        assert user_id not in manager.user_connections

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_broadcast_to_conversation(self):
        """Test broadcast functionality to conversation."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        # Create multiple connections to same conversation
        mock_websocket1 = MagicMock()
        mock_websocket2 = MagicMock()
        
        await manager.connect(mock_websocket1, "user-1", "conv-123")
        await manager.connect(mock_websocket2, "user-2", "conv-123")
        
        # Test broadcast
        await manager.broadcast_to_conversation("broadcast message", "conv-123")
        
        mock_websocket1.send_text.assert_called_with("broadcast message")
        mock_websocket2.send_text.assert_called_with("broadcast message")
        
        # Test broadcast with exclude
        await manager.broadcast_to_conversation("exclude message", "conv-123", exclude_user="user-1")
        
        # user-1 should not receive the message
        assert mock_websocket1.send_text.call_count == 1
        # user-2 should receive the message
        assert mock_websocket2.send_text.call_count == 2

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_typing_indicator_broadcast(self):
        """Test typing indicator broadcast functionality."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        mock_websocket = MagicMock()
        await manager.connect(mock_websocket, "user-123", "conv-123")
        
        # Test typing indicator
        await manager.send_typing_indicator("conv-123", "user-123", True)
        
        expected_message = json.dumps({
            "type": "typing_indicator",
            "data": {
                "user_id": "user-123",
                "is_typing": True,
                "conversation_id": "conv-123"
            }
        })
        
        mock_websocket.send_text.assert_called_with(expected_message)

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_knowledge_update_send(self):
        """Test knowledge update sending functionality."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        mock_websocket = MagicMock()
        await manager.connect(mock_websocket, "user-123", "conv-123")
        
        documents = [{"id": "doc-1", "title": "Test Doc"}]
        search_query = "test query"
        
        # Test knowledge update
        await manager.send_knowledge_update("user-123", "conv-123", documents, search_query)
        
        expected_message = json.dumps({
            "type": "knowledge_update",
            "data": {
                "documents": documents,
                "search_query": search_query,
                "timestamp": pytest.approx(asyncio.get_event_loop().time(), rel=1.0)
            }
        })
        
        mock_websocket.send_text.assert_called_with(expected_message)

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_processing_job_update_send(self):
        """Test processing job update sending functionality."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        mock_websocket = MagicMock()
        await manager.connect(mock_websocket, "user-123", "conv-123")
        
        # Test processing job update
        await manager.send_processing_job_update("user-123", "conv-123", "job-123", "processing", 75)
        
        expected_message = json.dumps({
            "type": "processing_job_update",
            "data": {
                "job_id": "job-123",
                "status": "processing",
                "progress": 75,
                "timestamp": pytest.approx(asyncio.get_event_loop().time(), rel=1.0)
            }
        })
        
        mock_websocket.send_text.assert_called_with(expected_message)

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_connection_cleanup(self):
        """Test WebSocket connection cleanup on disconnect."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        mock_websocket = MagicMock()
        user_id = "user-123"
        conversation_id = "conv-123"
        
        # Connect
        await manager.connect(mock_websocket, user_id, conversation_id)
        
        # Verify connection is tracked
        connection_id = f"{user_id}_{conversation_id}"
        assert connection_id in manager.active_connections
        assert conversation_id in manager.conversation_connections
        assert user_id in manager.user_connections
        
        # Disconnect
        manager.disconnect(user_id, conversation_id)
        
        # Verify cleanup
        assert connection_id not in manager.active_connections
        assert conversation_id not in manager.conversation_connections
        assert user_id not in manager.user_connections

    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_multiple_conversations(self):
        """Test WebSocket handling of multiple conversations."""
        from backend.app.api.v1.endpoints.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        mock_websocket1 = MagicMock()
        mock_websocket2 = MagicMock()
        
        # Connect to different conversations
        await manager.connect(mock_websocket1, "user-1", "conv-1")
        await manager.connect(mock_websocket2, "user-1", "conv-2")
        
        # Verify both connections are tracked
        assert "user-1_conv-1" in manager.active_connections
        assert "user-1_conv-2" in manager.active_connections
        assert "conv-1" in manager.conversation_connections
        assert "conv-2" in manager.conversation_connections
        assert "user-1" in manager.user_connections
        assert len(manager.user_connections["user-1"]) == 2
        
        # Test broadcast to specific conversation
        await manager.broadcast_to_conversation("conv-1 message", "conv-1")
        mock_websocket1.send_text.assert_called_with("conv-1 message")
        mock_websocket2.send_text.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_current_user_ws_success(self):
        """Test successful WebSocket user authentication."""
        from backend.app.api.v1.endpoints.websocket import get_current_user_ws
        
        with patch('backend.app.api.v1.endpoints.websocket.decode_access_token') as mock_decode:
            with patch('backend.app.api.v1.endpoints.websocket.User') as mock_user:
                mock_decode.return_value = {"sub": "user-123"}
                
                mock_user_obj = MagicMock()
                mock_user_obj.id = "user-123"
                mock_user.query.filter.return_value.first.return_value = mock_user_obj
                
                mock_db = MagicMock()
                
                result = asyncio.run(get_current_user_ws("valid-token", mock_db))
                
                assert result == mock_user_obj
                mock_decode.assert_called_once_with("valid-token")

    @pytest.mark.unit
    @pytest.mark.api
    def test_get_current_user_ws_invalid_token(self):
        """Test WebSocket user authentication with invalid token."""
        from backend.app.api.v1.endpoints.websocket import get_current_user_ws
        
        with patch('backend.app.api.v1.endpoints.websocket.decode_access_token') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")
            
            mock_db = MagicMock()
            
            result = asyncio.run(get_current_user_ws("invalid-token", mock_db))
            
            assert result is None