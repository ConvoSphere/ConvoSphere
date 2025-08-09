"""
Unit tests for AI Service Types Module.

This module tests the new AI service type definitions:
- ProviderType
- ModelType
- ProviderConfig
- ChatConfig
- ChatRequest
- ChatResponse
- ChatStreamResponse
- EmbeddingRequest
- EmbeddingResponse
- ModelInfo
- CostInfo
- RAGContext
- ToolInfo
- ToolCall
"""

import pytest
from datetime import datetime, UTC
from dataclasses import asdict

from backend.app.services.ai.types.ai_types import (
    ProviderType,
    ModelType,
    ProviderConfig,
    ChatConfig,
    ChatRequest,
    ChatResponse,
    ChatStreamResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelInfo,
    CostInfo,
    RAGContext,
    ToolInfo,
    ToolCall,
)


class TestProviderType:
    """Test class for ProviderType enum."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_type_values(self):
        """Test ProviderType enum values."""
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.ANTHROPIC == "anthropic"
        assert ProviderType.GOOGLE == "google"
        assert ProviderType.AZURE == "azure"
        assert ProviderType.CUSTOM == "custom"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_type_list(self):
        """Test ProviderType list method."""
        providers = list(ProviderType)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
        assert "azure" in providers
        assert "custom" in providers


class TestModelType:
    """Test class for ModelType enum."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_model_type_values(self):
        """Test ModelType enum values."""
        assert ModelType.CHAT == "chat"
        assert ModelType.EMBEDDING == "embedding"
        assert ModelType.IMAGE == "image"
        assert ModelType.AUDIO == "audio"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_model_type_list(self):
        """Test ModelType list method."""
        model_types = list(ModelType)
        assert "chat" in model_types
        assert "embedding" in model_types
        assert "image" in model_types
        assert "audio" in model_types


class TestProviderConfig:
    """Test class for ProviderConfig dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_config_creation(self):
        """Test ProviderConfig creation."""
        config = ProviderConfig(
            api_key="test-key",
            base_url="https://api.openai.com",
            timeout=30,
            max_retries=3,
        )
        
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.openai.com"
        assert config.timeout == 30
        assert config.max_retries == 3

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_config_defaults(self):
        """Test ProviderConfig default values."""
        config = ProviderConfig(api_key="test-key")
        
        assert config.api_key == "test-key"
        assert config.base_url is None
        assert config.timeout == 60
        assert config.max_retries == 5

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_provider_config_to_dict(self):
        """Test ProviderConfig to dict conversion."""
        config = ProviderConfig(
            api_key="test-key",
            base_url="https://api.openai.com",
            timeout=30,
            max_retries=3,
        )
        
        config_dict = asdict(config)
        assert config_dict["api_key"] == "test-key"
        assert config_dict["base_url"] == "https://api.openai.com"
        assert config_dict["timeout"] == 30
        assert config_dict["max_retries"] == 3


class TestChatConfig:
    """Test class for ChatConfig dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_config_creation(self):
        """Test ChatConfig creation."""
        config = ChatConfig(
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_config_defaults(self):
        """Test ChatConfig default values."""
        config = ChatConfig()
        
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_config_to_dict(self):
        """Test ChatConfig to dict conversion."""
        config = ChatConfig(
            temperature=0.8,
            max_tokens=500,
            top_p=0.95,
        )
        
        config_dict = asdict(config)
        assert config_dict["temperature"] == 0.8
        assert config_dict["max_tokens"] == 500
        assert config_dict["top_p"] == 0.95


class TestChatRequest:
    """Test class for ChatRequest dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_request_creation(self):
        """Test ChatRequest creation."""
        messages = [{"role": "user", "content": "Hello"}]
        config = ChatConfig(temperature=0.7)
        
        request = ChatRequest(
            messages=messages,
            user_id="user123",
            provider="openai",
            model="gpt-4",
            config=config,
            request_id="req-123",
        )
        
        assert request.messages == messages
        assert request.user_id == "user123"
        assert request.provider == "openai"
        assert request.model == "gpt-4"
        assert request.config == config
        assert request.request_id == "req-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_request_to_dict(self):
        """Test ChatRequest to dict conversion."""
        messages = [{"role": "user", "content": "Hello"}]
        config = ChatConfig(temperature=0.7)
        
        request = ChatRequest(
            messages=messages,
            user_id="user123",
            provider="openai",
            model="gpt-4",
            config=config,
        )
        
        request_dict = asdict(request)
        assert request_dict["messages"] == messages
        assert request_dict["user_id"] == "user123"
        assert request_dict["provider"] == "openai"
        assert request_dict["model"] == "gpt-4"
        assert "config" in request_dict


class TestChatResponse:
    """Test class for ChatResponse dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_response_creation(self):
        """Test ChatResponse creation."""
        response = ChatResponse(
            content="Hello, world!",
            model="gpt-4",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="stop",
            request_id="req-123",
        )
        
        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.usage == {"input_tokens": 10, "output_tokens": 5}
        assert response.finish_reason == "stop"
        assert response.request_id == "req-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_response_to_dict(self):
        """Test ChatResponse to dict conversion."""
        response = ChatResponse(
            content="Hello, world!",
            model="gpt-4",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="stop",
        )
        
        response_dict = asdict(response)
        assert response_dict["content"] == "Hello, world!"
        assert response_dict["model"] == "gpt-4"
        assert response_dict["usage"] == {"input_tokens": 10, "output_tokens": 5}
        assert response_dict["finish_reason"] == "stop"


class TestChatStreamResponse:
    """Test class for ChatStreamResponse dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_stream_response_creation(self):
        """Test ChatStreamResponse creation."""
        response = ChatStreamResponse(
            content="Hello",
            model="gpt-4",
            finish_reason="stop",
            request_id="req-123",
        )
        
        assert response.content == "Hello"
        assert response.model == "gpt-4"
        assert response.finish_reason == "stop"
        assert response.request_id == "req-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_stream_response_to_dict(self):
        """Test ChatStreamResponse to dict conversion."""
        response = ChatStreamResponse(
            content="Hello",
            model="gpt-4",
            finish_reason="stop",
        )
        
        response_dict = asdict(response)
        assert response_dict["content"] == "Hello"
        assert response_dict["model"] == "gpt-4"
        assert response_dict["finish_reason"] == "stop"


class TestEmbeddingRequest:
    """Test class for EmbeddingRequest dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_embedding_request_creation(self):
        """Test EmbeddingRequest creation."""
        request = EmbeddingRequest(
            texts=["Hello", "World"],
            provider="openai",
            model="text-embedding-ada-002",
            request_id="req-123",
        )
        
        assert request.texts == ["Hello", "World"]
        assert request.provider == "openai"
        assert request.model == "text-embedding-ada-002"
        assert request.request_id == "req-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_embedding_request_to_dict(self):
        """Test EmbeddingRequest to dict conversion."""
        request = EmbeddingRequest(
            texts=["Hello", "World"],
            provider="openai",
            model="text-embedding-ada-002",
        )
        
        request_dict = asdict(request)
        assert request_dict["texts"] == ["Hello", "World"]
        assert request_dict["provider"] == "openai"
        assert request_dict["model"] == "text-embedding-ada-002"


class TestEmbeddingResponse:
    """Test class for EmbeddingResponse dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_embedding_response_creation(self):
        """Test EmbeddingResponse creation."""
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        response = EmbeddingResponse(
            embeddings=embeddings,
            model="text-embedding-ada-002",
            usage={"input_tokens": 10},
            request_id="req-123",
        )
        
        assert response.embeddings == embeddings
        assert response.model == "text-embedding-ada-002"
        assert response.usage == {"input_tokens": 10}
        assert response.request_id == "req-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_embedding_response_to_dict(self):
        """Test EmbeddingResponse to dict conversion."""
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        response = EmbeddingResponse(
            embeddings=embeddings,
            model="text-embedding-ada-002",
            usage={"input_tokens": 10},
        )
        
        response_dict = asdict(response)
        assert response_dict["embeddings"] == embeddings
        assert response_dict["model"] == "text-embedding-ada-002"
        assert response_dict["usage"] == {"input_tokens": 10}


class TestModelInfo:
    """Test class for ModelInfo dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_model_info_creation(self):
        """Test ModelInfo creation."""
        info = ModelInfo(
            name="gpt-4",
            provider="openai",
            model_type=ModelType.CHAT,
            max_tokens=8192,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06,
            is_available=True,
        )
        
        assert info.name == "gpt-4"
        assert info.provider == "openai"
        assert info.model_type == ModelType.CHAT
        assert info.max_tokens == 8192
        assert info.cost_per_1k_input == 0.03
        assert info.cost_per_1k_output == 0.06
        assert info.is_available is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_model_info_to_dict(self):
        """Test ModelInfo to dict conversion."""
        info = ModelInfo(
            name="gpt-4",
            provider="openai",
            model_type=ModelType.CHAT,
            max_tokens=8192,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06,
            is_available=True,
        )
        
        info_dict = asdict(info)
        assert info_dict["name"] == "gpt-4"
        assert info_dict["provider"] == "openai"
        assert info_dict["model_type"] == ModelType.CHAT
        assert info_dict["max_tokens"] == 8192


class TestCostInfo:
    """Test class for CostInfo dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_cost_info_creation(self):
        """Test CostInfo creation."""
        timestamp = datetime.now(UTC)
        info = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=timestamp,
            user_id="user123",
            conversation_id="conv123",
        )
        
        assert info.model == "gpt-4"
        assert info.tokens_used == 100
        assert info.cost_usd == 0.03
        assert info.timestamp == timestamp
        assert info.user_id == "user123"
        assert info.conversation_id == "conv123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_cost_info_to_dict(self):
        """Test CostInfo to dict conversion."""
        timestamp = datetime.now(UTC)
        info = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=timestamp,
            user_id="user123",
            conversation_id="conv123",
        )
        
        info_dict = asdict(info)
        assert info_dict["model"] == "gpt-4"
        assert info_dict["tokens_used"] == 100
        assert info_dict["cost_usd"] == 0.03
        assert info_dict["user_id"] == "user123"
        assert info_dict["conversation_id"] == "conv123"


class TestRAGContext:
    """Test class for RAGContext dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_rag_context_creation(self):
        """Test RAGContext creation."""
        context = RAGContext(
            chunks=[{"content": "Chunk 1", "source": "doc1"}],
            sources=["doc1"],
            summary="Context summary",
            relevance_score=0.85,
        )
        
        assert context.chunks == [{"content": "Chunk 1", "source": "doc1"}]
        assert context.sources == ["doc1"]
        assert context.summary == "Context summary"
        assert context.relevance_score == 0.85

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_rag_context_to_dict(self):
        """Test RAGContext to dict conversion."""
        context = RAGContext(
            chunks=[{"content": "Chunk 1", "source": "doc1"}],
            sources=["doc1"],
            summary="Context summary",
            relevance_score=0.85,
        )
        
        context_dict = asdict(context)
        assert context_dict["chunks"] == [{"content": "Chunk 1", "source": "doc1"}]
        assert context_dict["sources"] == ["doc1"]
        assert context_dict["summary"] == "Context summary"
        assert context_dict["relevance_score"] == 0.85


class TestToolInfo:
    """Test class for ToolInfo dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_tool_info_creation(self):
        """Test ToolInfo creation."""
        tool = ToolInfo(
            name="calculator",
            description="Performs mathematical calculations",
            parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
            is_available=True,
        )
        
        assert tool.name == "calculator"
        assert tool.description == "Performs mathematical calculations"
        assert tool.parameters == {"type": "object", "properties": {"expression": {"type": "string"}}}
        assert tool.is_available is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_tool_info_to_dict(self):
        """Test ToolInfo to dict conversion."""
        tool = ToolInfo(
            name="calculator",
            description="Performs mathematical calculations",
            parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
            is_available=True,
        )
        
        tool_dict = asdict(tool)
        assert tool_dict["name"] == "calculator"
        assert tool_dict["description"] == "Performs mathematical calculations"
        assert tool_dict["is_available"] is True


class TestToolCall:
    """Test class for ToolCall dataclass."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_tool_call_creation(self):
        """Test ToolCall creation."""
        tool_call = ToolCall(
            name="calculator",
            parameters={"expression": "2 + 2"},
            call_id="call-123",
        )
        
        assert tool_call.name == "calculator"
        assert tool_call.parameters == {"expression": "2 + 2"}
        assert tool_call.call_id == "call-123"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_tool_call_to_dict(self):
        """Test ToolCall to dict conversion."""
        tool_call = ToolCall(
            name="calculator",
            parameters={"expression": "2 + 2"},
            call_id="call-123",
        )
        
        tool_call_dict = asdict(tool_call)
        assert tool_call_dict["name"] == "calculator"
        assert tool_call_dict["parameters"] == {"expression": "2 + 2"}
        assert tool_call_dict["call_id"] == "call-123"