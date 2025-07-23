"""
Tests for Pydantic v2 schemas and validation.

This module tests the new conversation and agent schemas with
comprehensive validation and error handling.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from pydantic import ValidationError

from app.schemas.conversation import (
    MessageCreate,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationSearchParams,
)
from app.schemas.agent import (
    ToolCall,
    AgentConfig,
    AgentResponse as AgentResponseSchema,
    AgentCreate,
    AgentUpdate,
)
from app.models.conversation import MessageRole, MessageType


class TestMessageSchemas:
    """Test message-related schemas."""

    def test_message_create_valid(self):
        """Test valid message creation."""
        message_data = {
            "content": "Hello, world!",
            "role": MessageRole.USER,
            "message_type": MessageType.TEXT,
            "conversation_id": str(uuid4()),
        }
        
        message = MessageCreate(**message_data)
        assert message.content == "Hello, world!"
        assert message.role == MessageRole.USER
        assert message.message_type == MessageType.TEXT

    def test_message_create_empty_content(self):
        """Test message creation with empty content."""
        message_data = {
            "content": "",
            "role": MessageRole.USER,
            "conversation_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "Message content cannot be empty" in str(exc_info.value)

    def test_message_create_whitespace_content(self):
        """Test message creation with whitespace content."""
        message_data = {
            "content": "   ",
            "role": MessageRole.USER,
            "conversation_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "Message content cannot be empty" in str(exc_info.value)

    def test_message_create_content_too_long(self):
        """Test message creation with content too long."""
        long_content = "x" * 50001
        message_data = {
            "content": long_content,
            "role": MessageRole.USER,
            "conversation_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "String should have at most 50000 characters" in str(exc_info.value)

    def test_message_create_with_tool_data(self):
        """Test message creation with tool data."""
        message_data = {
            "content": "Tool execution result",
            "role": MessageRole.TOOL,
            "tool_name": "test_tool",
            "tool_input": {"param": "value"},
            "tool_output": {"result": "success"},
            "conversation_id": str(uuid4()),
        }
        
        message = MessageCreate(**message_data)
        assert message.tool_name == "test_tool"
        assert message.tool_input == {"param": "value"}
        assert message.tool_output == {"result": "success"}

    def test_message_create_tool_name_empty(self):
        """Test message creation with empty tool name."""
        message_data = {
            "content": "Tool result",
            "role": MessageRole.TOOL,
            "tool_name": "",
            "conversation_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "Tool name cannot be empty when provided" in str(exc_info.value)

    def test_message_create_negative_tokens(self):
        """Test message creation with negative tokens."""
        message_data = {
            "content": "Test message",
            "role": MessageRole.USER,
            "tokens_used": -1,
            "conversation_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "Token usage cannot be negative" in str(exc_info.value)


class TestConversationSchemas:
    """Test conversation-related schemas."""

    def test_conversation_create_valid(self):
        """Test valid conversation creation."""
        conversation_data = {
            "title": "Test Conversation",
            "description": "A test conversation",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
            "tags": ["test", "demo"],
            "access": "private",
        }
        
        conversation = ConversationCreate(**conversation_data)
        assert conversation.title == "Test Conversation"
        assert conversation.description == "A test conversation"
        assert conversation.tags == ["test", "demo"]
        assert conversation.access == "private"

    def test_conversation_create_empty_title(self):
        """Test conversation creation with empty title."""
        conversation_data = {
            "title": "",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(**conversation_data)
        
        assert "Conversation title cannot be empty" in str(exc_info.value)

    def test_conversation_create_title_too_long(self):
        """Test conversation creation with title too long."""
        long_title = "x" * 501
        conversation_data = {
            "title": long_title,
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(**conversation_data)
        
        assert "String should have at most 500 characters" in str(exc_info.value)

    def test_conversation_create_invalid_access(self):
        """Test conversation creation with invalid access level."""
        conversation_data = {
            "title": "Test Conversation",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
            "access": "invalid",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(**conversation_data)
        
        assert "String should match pattern" in str(exc_info.value)

    def test_conversation_create_too_many_tags(self):
        """Test conversation creation with too many tags."""
        many_tags = [f"tag_{i}" for i in range(21)]
        conversation_data = {
            "title": "Test Conversation",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
            "tags": many_tags,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate(**conversation_data)
        
        assert "Maximum 20 tags allowed" in str(exc_info.value)

    def test_conversation_create_duplicate_tags(self):
        """Test conversation creation with duplicate tags."""
        conversation_data = {
            "title": "Test Conversation",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
            "tags": ["test", "test", "demo"],
        }
        
        conversation = ConversationCreate(**conversation_data)
        assert conversation.tags == ["test", "demo"]  # Duplicates removed

    def test_conversation_search_params_valid(self):
        """Test valid conversation search parameters."""
        search_params = {
            "query": "test query",
            "page": 1,
            "size": 20,
            "access": "private",
            "is_active": True,
        }
        
        params = ConversationSearchParams(**search_params)
        assert params.query == "test query"
        assert params.page == 1
        assert params.size == 20
        assert params.access == "private"
        assert params.is_active is True

    def test_conversation_search_params_invalid_page(self):
        """Test conversation search with invalid page."""
        search_params = {
            "query": "test",
            "page": 0,  # Invalid: must be >= 1
            "size": 20,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationSearchParams(**search_params)
        
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_conversation_search_params_invalid_size(self):
        """Test conversation search with invalid size."""
        search_params = {
            "query": "test",
            "page": 1,
            "size": 101,  # Invalid: must be <= 100
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationSearchParams(**search_params)
        
        assert "Input should be less than or equal to 100" in str(exc_info.value)

    def test_conversation_search_params_future_date(self):
        """Test conversation search with future date."""
        future_date = datetime(2025, 1, 1)
        search_params = {
            "query": "test",
            "created_after": future_date,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationSearchParams(**search_params)
        
        assert "Date cannot be in the future" in str(exc_info.value)

    def test_conversation_search_params_date_order(self):
        """Test conversation search with invalid date order."""
        search_params = {
            "query": "test",
            "created_after": datetime(2023, 12, 1),
            "created_before": datetime(2023, 11, 1),  # Before created_after
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConversationSearchParams(**search_params)
        
        assert "created_before must be after created_after" in str(exc_info.value)


class TestAgentSchemas:
    """Test agent-related schemas."""

    def test_tool_call_valid(self):
        """Test valid tool call."""
        tool_call_data = {
            "id": "call_123",
            "name": "test_tool",
            "arguments": {"param": "value"},
            "status": "pending",
        }
        
        tool_call = ToolCall(**tool_call_data)
        assert tool_call.id == "call_123"
        assert tool_call.name == "test_tool"
        assert tool_call.arguments == {"param": "value"}
        assert tool_call.status == "pending"

    def test_tool_call_empty_name(self):
        """Test tool call with empty name."""
        tool_call_data = {
            "id": "call_123",
            "name": "",
            "arguments": {},
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ToolCall(**tool_call_data)
        
        assert "Tool name cannot be empty" in str(exc_info.value)

    def test_tool_call_invalid_status(self):
        """Test tool call with invalid status."""
        tool_call_data = {
            "id": "call_123",
            "name": "test_tool",
            "arguments": {},
            "status": "invalid_status",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ToolCall(**tool_call_data)
        
        assert "String should match pattern" in str(exc_info.value)

    def test_agent_config_valid(self):
        """Test valid agent configuration."""
        agent_config_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "system_prompt": "You are a helpful assistant.",
            "tools": ["tool1", "tool2"],
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        
        config = AgentConfig(**agent_config_data)
        assert config.name == "Test Agent"
        assert config.description == "A test agent"
        assert config.system_prompt == "You are a helpful assistant."
        assert config.tools == ["tool1", "tool2"]
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_agent_config_empty_name(self):
        """Test agent config with empty name."""
        agent_config_data = {
            "name": "",
            "description": "A test agent",
            "system_prompt": "You are a helpful assistant.",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(**agent_config_data)
        
        assert "Agent name cannot be empty" in str(exc_info.value)

    def test_agent_config_invalid_temperature(self):
        """Test agent config with invalid temperature."""
        agent_config_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 3.0,  # Invalid: must be <= 2.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(**agent_config_data)
        
        assert "Input should be less than or equal to 2" in str(exc_info.value)

    def test_agent_config_too_many_tools(self):
        """Test agent config with too many tools."""
        many_tools = [f"tool_{i}" for i in range(51)]
        agent_config_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "system_prompt": "You are a helpful assistant.",
            "tools": many_tools,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(**agent_config_data)
        
        assert "Maximum 50 tools allowed" in str(exc_info.value)

    def test_agent_config_duplicate_tools(self):
        """Test agent config with duplicate tools."""
        agent_config_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "system_prompt": "You are a helpful assistant.",
            "tools": ["tool1", "tool1", "tool2"],
        }
        
        config = AgentConfig(**agent_config_data)
        assert config.tools == ["tool1", "tool2"]  # Duplicates removed

    def test_agent_response_valid(self):
        """Test valid agent response."""
        response_data = {
            "content": "Hello, I can help you!",
            "model_used": "gpt-4",
            "tokens_used": 100,
            "processing_time": 1.5,
            "confidence": 0.9,
        }
        
        response = AgentResponseSchema(**response_data)
        assert response.content == "Hello, I can help you!"
        assert response.model_used == "gpt-4"
        assert response.tokens_used == 100
        assert response.processing_time == 1.5
        assert response.confidence == 0.9

    def test_agent_response_invalid_confidence(self):
        """Test agent response with invalid confidence."""
        response_data = {
            "content": "Hello!",
            "model_used": "gpt-4",
            "tokens_used": 100,
            "processing_time": 1.5,
            "confidence": 1.5,  # Invalid: must be <= 1.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AgentResponseSchema(**response_data)
        
        assert "Input should be less than or equal to 1" in str(exc_info.value)

    def test_agent_response_negative_tokens(self):
        """Test agent response with negative tokens."""
        response_data = {
            "content": "Hello!",
            "model_used": "gpt-4",
            "tokens_used": -1,  # Invalid: must be >= 0
            "processing_time": 1.5,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AgentResponseSchema(**response_data)
        
        assert "Input should be greater than or equal to 0" in str(exc_info.value)


class TestSchemaIntegration:
    """Test schema integration and edge cases."""

    def test_message_response_from_model(self):
        """Test creating MessageResponse from model data."""
        # Simulate model data
        model_data = {
            "id": str(uuid4()),
            "content": "Test message",
            "role": MessageRole.USER,
            "message_type": MessageType.TEXT,
            "conversation_id": str(uuid4()),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        response = MessageResponse(**model_data)
        assert response.content == "Test message"
        assert response.role == MessageRole.USER

    def test_conversation_response_from_model(self):
        """Test creating ConversationResponse from model data."""
        # Simulate model data
        model_data = {
            "id": str(uuid4()),
            "title": "Test Conversation",
            "description": "Test description",
            "user_id": str(uuid4()),
            "assistant_id": str(uuid4()),
            "is_active": True,
            "is_archived": False,
            "message_count": 5,
            "total_tokens": 1000,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": [],
        }
        
        response = ConversationResponse(**model_data)
        assert response.title == "Test Conversation"
        assert response.message_count == 5
        assert response.total_tokens == 1000

    def test_schema_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        message_data = {
            "content": "Test message",
            "role": MessageRole.USER,
            "conversation_id": str(uuid4()),
            "extra_field": "should_fail",  # Extra field
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MessageCreate(**message_data)
        
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_schema_validation_assignment(self):
        """Test that validation works on assignment."""
        message = MessageCreate(
            content="Test message",
            role=MessageRole.USER,
            conversation_id=str(uuid4()),
        )
        
        # This should raise an error due to validate_assignment=True
        with pytest.raises(ValidationError):
            message.content = ""  # Invalid assignment