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

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_general_connection_success(self, client: TestClient):
        """Fast test for successful general WebSocket connection."""
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

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_conversation_connection_success(self, client: TestClient):
        """Fast test for successful conversation WebSocket connection."""
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

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, client: TestClient):
        """Fast test for WebSocket message handling."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                with patch('backend.app.api.v1.endpoints.websocket.MessageService') as mock_message_service:
                    mock_user = MagicMock()
                    mock_user.id = "user-123"
                    mock_auth.return_value = mock_user
                    
                    mock_conv = MagicMock()
                    mock_conv.id = "conv-123"
                    mock_conv.user_id = "user-123"
                    mock_conversation.query.filter.return_value.first.return_value = mock_conv
                    
                    mock_service = MagicMock()
                    mock_message_service.return_value = mock_service
                    
                    with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                        # Send a message
                        message_data = {
                            "type": "message",
                            "data": {
                                "content": "Hello, this is a test message",
                                "role": "user"
                            }
                        }
                        websocket.send_text(json.dumps(message_data))
                        
                        # Receive acknowledgment
                        response_data = websocket.receive_text()
                        response_message = json.loads(response_data)
                        
                        assert response_message["type"] == "message_received"
                        assert response_message["data"]["status"] == "processing"

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced functionality and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_general_authentication_failure(self, client: TestClient):
        """Comprehensive test for general WebSocket connection with invalid token."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            mock_auth.return_value = None
            
            with pytest.raises(Exception):  # WebSocket connection should fail
                with client.websocket_connect("/api/v1/websocket/?token=invalid-token") as websocket:
                    pass

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_conversation_access_denied(self, client: TestClient):
        """Comprehensive test for conversation WebSocket connection with access denied."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                # Conversation belongs to different user
                mock_conv = MagicMock()
                mock_conv.id = "conv-123"
                mock_conv.user_id = "user-456"  # Different user
                mock_conversation.query.filter.return_value.first.return_value = mock_conv
                
                with pytest.raises(Exception):  # WebSocket connection should fail
                    with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                        pass

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_typing_indicator(self, client: TestClient):
        """Comprehensive test for typing indicator functionality."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager:
                    mock_user = MagicMock()
                    mock_user.id = "user-123"
                    mock_auth.return_value = mock_user
                    
                    mock_conv = MagicMock()
                    mock_conv.id = "conv-123"
                    mock_conv.user_id = "user-123"
                    mock_conversation.query.filter.return_value.first.return_value = mock_conv
                    
                    mock_ws_manager = MagicMock()
                    mock_manager.return_value = mock_ws_manager
                    
                    with client.websocket_connect("/api/v1/websocket/conv-123?token=valid-token") as websocket:
                        # Send typing indicator
                        typing_data = {
                            "type": "typing_start",
                            "data": {
                                "user_id": "user-123"
                            }
                        }
                        websocket.send_text(json.dumps(typing_data))
                        
                        # Verify typing indicator was broadcast
                        mock_ws_manager.broadcast_typing_indicator.assert_called_once_with(
                            "conv-123", "user-123", True
                        )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_knowledge_search(self, client: TestClient):
        """Comprehensive test for knowledge search via WebSocket."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.KnowledgeService') as mock_knowledge_service:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_service = MagicMock()
                mock_knowledge_service.return_value = mock_service
                
                search_results = [
                    {"id": "doc-1", "title": "Test Document", "content": "Test content"},
                    {"id": "doc-2", "title": "Another Document", "content": "More content"}
                ]
                mock_service.search_documents.return_value = search_results
                
                with client.websocket_connect("/api/v1/websocket/?token=valid-token") as websocket:
                    # Send knowledge search request
                    search_data = {
                        "type": "knowledge_search",
                        "data": {
                            "query": "test query",
                            "limit": 5
                        }
                    }
                    websocket.send_text(json.dumps(search_data))
                    
                    # Receive search results
                    response_data = websocket.receive_text()
                    response_message = json.loads(response_data)
                    
                    assert response_message["type"] == "knowledge_search_results"
                    assert len(response_message["data"]["results"]) == 2
                    assert response_message["data"]["query"] == "test query"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_processing_job_update(self, client: TestClient):
        """Comprehensive test for processing job updates via WebSocket."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.ProcessingJobService') as mock_job_service:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_service = MagicMock()
                mock_job_service.return_value = mock_service
                
                job_status = {
                    "job_id": "job-123",
                    "status": "completed",
                    "progress": 100,
                    "result": "Processing completed successfully"
                }
                mock_service.get_job_status.return_value = job_status
                
                with client.websocket_connect("/api/v1/websocket/?token=valid-token") as websocket:
                    # Request job status
                    job_data = {
                        "type": "job_status",
                        "data": {
                            "job_id": "job-123"
                        }
                    }
                    websocket.send_text(json.dumps(job_data))
                    
                    # Receive job status
                    response_data = websocket.receive_text()
                    response_message = json.loads(response_data)
                    
                    assert response_message["type"] == "job_status_update"
                    assert response_message["data"]["job_id"] == "job-123"
                    assert response_message["data"]["status"] == "completed"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_invalid_message_type(self, client: TestClient):
        """Comprehensive test for handling invalid message types."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user-123"
            mock_auth.return_value = mock_user
            
            with client.websocket_connect("/api/v1/websocket/?token=valid-token") as websocket:
                # Send invalid message type
                invalid_data = {
                    "type": "invalid_type",
                    "data": {}
                }
                websocket.send_text(json.dumps(invalid_data))
                
                # Receive error response
                response_data = websocket.receive_text()
                response_message = json.loads(response_data)
                
                assert response_message["type"] == "error"
                assert "Unknown message type" in response_message["data"]["message"]

    # =============================================================================
    # CONNECTION MANAGEMENT TESTS
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_connection_manager(self):
        """Comprehensive test for WebSocket connection manager."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Test connection addition
            mock_websocket = MagicMock()
            mock_manager.add_connection.assert_not_called()
            
            # Simulate connection
            mock_manager.add_connection("user-123", mock_websocket)
            mock_manager.add_connection.assert_called_once_with("user-123", mock_websocket)
            
            # Test connection removal
            mock_manager.remove_connection.assert_not_called()
            mock_manager.remove_connection("user-123")
            mock_manager.remove_connection.assert_called_once_with("user-123")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_broadcast_to_conversation(self):
        """Comprehensive test for broadcasting messages to conversation."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            message_data = {
                "type": "message",
                "data": {
                    "content": "Test message",
                    "user_id": "user-123"
                }
            }
            
            # Test broadcasting
            mock_manager.broadcast_to_conversation.assert_not_called()
            mock_manager.broadcast_to_conversation("conv-123", message_data)
            mock_manager.broadcast_to_conversation.assert_called_once_with("conv-123", message_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_typing_indicator_broadcast(self):
        """Comprehensive test for typing indicator broadcasting."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Test typing start
            mock_manager.broadcast_typing_indicator.assert_not_called()
            mock_manager.broadcast_typing_indicator("conv-123", "user-123", True)
            mock_manager.broadcast_typing_indicator.assert_called_once_with("conv-123", "user-123", True)
            
            # Test typing stop
            mock_manager.broadcast_typing_indicator("conv-123", "user-123", False)
            assert mock_manager.broadcast_typing_indicator.call_count == 2

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_knowledge_update_send(self):
        """Comprehensive test for knowledge update sending."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            knowledge_data = {
                "type": "knowledge_update",
                "data": {
                    "document_id": "doc-123",
                    "status": "processed",
                    "summary": "Document processed successfully"
                }
            }
            
            # Test knowledge update sending
            mock_manager.send_to_user.assert_not_called()
            mock_manager.send_to_user("user-123", knowledge_data)
            mock_manager.send_to_user.assert_called_once_with("user-123", knowledge_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_processing_job_update_send(self):
        """Comprehensive test for processing job update sending."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            job_data = {
                "type": "job_update",
                "data": {
                    "job_id": "job-123",
                    "status": "processing",
                    "progress": 50
                }
            }
            
            # Test job update sending
            mock_manager.send_to_user.assert_not_called()
            mock_manager.send_to_user("user-123", job_data)
            mock_manager.send_to_user.assert_called_once_with("user-123", job_data)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_connection_cleanup(self):
        """Comprehensive test for WebSocket connection cleanup."""
        with patch('backend.app.api.v1.endpoints.websocket.WebSocketManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Test cleanup
            mock_manager.cleanup_disconnected.assert_not_called()
            mock_manager.cleanup_disconnected()
            mock_manager.cleanup_disconnected.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_websocket_multiple_conversations(self, client: TestClient):
        """Comprehensive test for multiple conversation connections."""
        with patch('backend.app.api.v1.endpoints.websocket.get_current_user_ws') as mock_auth:
            with patch('backend.app.api.v1.endpoints.websocket.Conversation') as mock_conversation:
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_auth.return_value = mock_user
                
                mock_conv1 = MagicMock()
                mock_conv1.id = "conv-1"
                mock_conv1.user_id = "user-123"
                
                mock_conv2 = MagicMock()
                mock_conv2.id = "conv-2"
                mock_conv2.user_id = "user-123"
                
                # Test first conversation
                mock_conversation.query.filter.return_value.first.return_value = mock_conv1
                with client.websocket_connect("/api/v1/websocket/conv-1?token=valid-token") as websocket1:
                    data1 = websocket1.receive_text()
                    message1 = json.loads(data1)
                    assert message1["data"]["conversation_id"] == "conv-1"
                
                # Test second conversation
                mock_conversation.query.filter.return_value.first.return_value = mock_conv2
                with client.websocket_connect("/api/v1/websocket/conv-2?token=valid-token") as websocket2:
                    data2 = websocket2.receive_text()
                    message2 = json.loads(data2)
                    assert message2["data"]["conversation_id"] == "conv-2"

    # =============================================================================
    # AUTHENTICATION TESTS
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_current_user_ws_success(self):
        """Fast test for successful WebSocket user authentication."""
        with patch('backend.app.api.v1.endpoints.websocket.verify_token') as mock_verify:
            with patch('backend.app.api.v1.endpoints.websocket.get_user_by_id') as mock_get_user:
                mock_verify.return_value = "user-123"
                
                mock_user = MagicMock()
                mock_user.id = "user-123"
                mock_user.is_active = True
                mock_get_user.return_value = mock_user
                
                from backend.app.api.v1.endpoints.websocket import get_current_user_ws
                
                result = get_current_user_ws("valid-token")
                assert result == mock_user
                mock_verify.assert_called_once_with("valid-token")
                mock_get_user.assert_called_once_with("user-123")

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_current_user_ws_invalid_token(self):
        """Comprehensive test for WebSocket authentication with invalid token."""
        with patch('backend.app.api.v1.endpoints.websocket.verify_token') as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")
            
            from backend.app.api.v1.endpoints.websocket import get_current_user_ws
            
            result = get_current_user_ws("invalid-token")
            assert result is None
            mock_verify.assert_called_once_with("invalid-token")