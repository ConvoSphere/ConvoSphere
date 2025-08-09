"""
Unit tests for AI Service Core Modules.

This module tests the new modular AI service components:
- ChatProcessor
- RequestBuilder  
- ResponseHandler
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.ai.core import ChatProcessor, RequestBuilder, ResponseHandler
from backend.app.services.ai.types.ai_types import (
    ChatConfig,
    ChatRequest,
    ChatResponse,
    ChatStreamResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderType,
)


class TestRequestBuilder:
    """Test class for RequestBuilder."""

    @pytest.fixture
    def request_builder(self):
        """Create a RequestBuilder instance."""
        return RequestBuilder()

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
        ]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_request_builder_initialization(self, request_builder):
        """Test RequestBuilder initialization."""
        assert request_builder._default_models is not None
        assert ProviderType.OPENAI in request_builder._default_models
        assert ProviderType.ANTHROPIC in request_builder._default_models

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_build_chat_request_valid(self, request_builder, sample_messages):
        """Test building a valid chat request."""
        request = request_builder.build_chat_request(
            messages=sample_messages,
            user_id="user123",
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=100,
        )

        assert isinstance(request, ChatRequest)
        assert request.messages == sample_messages
        assert request.user_id == "user123"
        assert request.provider == "openai"
        assert request.model == "gpt-4"
        assert request.config.temperature == 0.7
        assert request.config.max_tokens == 100

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_build_chat_request_default_model(self, request_builder, sample_messages):
        """Test building chat request with default model."""
        request = request_builder.build_chat_request(
            messages=sample_messages,
            user_id="user123",
            provider="openai",
        )

        assert request.model == "gpt-3.5-turbo"  # Default for OpenAI

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_build_embedding_request(self, request_builder):
        """Test building an embedding request."""
        texts = ["Hello world", "Test embedding"]
        request = request_builder.build_embedding_request(
            texts=texts,
            provider="openai",
            model="text-embedding-ada-002",
        )

        assert isinstance(request, EmbeddingRequest)
        assert request.texts == texts
        assert request.provider == "openai"
        assert request.model == "text-embedding-ada-002"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_messages_empty(self, request_builder):
        """Test validation with empty messages."""
        with pytest.raises(ValueError, match="Messages cannot be empty"):
            request_builder.build_chat_request(
                messages=[],
                user_id="user123",
                provider="openai",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_messages_invalid_role(self, request_builder):
        """Test validation with invalid message role."""
        invalid_messages = [{"role": "invalid", "content": "test"}]
        
        with pytest.raises(ValueError, match="Invalid role"):
            request_builder.build_chat_request(
                messages=invalid_messages,
                user_id="user123",
                provider="openai",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_messages_missing_fields(self, request_builder):
        """Test validation with missing message fields."""
        invalid_messages = [{"role": "user"}]  # Missing content
        
        with pytest.raises(ValueError, match="must have a 'content' field"):
            request_builder.build_chat_request(
                messages=invalid_messages,
                user_id="user123",
                provider="openai",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_user_id_empty(self, request_builder, sample_messages):
        """Test validation with empty user ID."""
        with pytest.raises(ValueError, match="User ID must be a non-empty string"):
            request_builder.build_chat_request(
                messages=sample_messages,
                user_id="",
                provider="openai",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_provider_unsupported(self, request_builder, sample_messages):
        """Test validation with unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            request_builder.build_chat_request(
                messages=sample_messages,
                user_id="user123",
                provider="unsupported",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_temperature_out_of_range(self, request_builder, sample_messages):
        """Test validation with temperature out of range."""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            request_builder.build_chat_request(
                messages=sample_messages,
                user_id="user123",
                provider="openai",
                temperature=3.0,
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_max_tokens_negative(self, request_builder, sample_messages):
        """Test validation with negative max tokens."""
        with pytest.raises(ValueError, match="Max tokens must be positive"):
            request_builder.build_chat_request(
                messages=sample_messages,
                user_id="user123",
                provider="openai",
                max_tokens=-1,
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_generate_request_id(self, request_builder):
        """Test request ID generation."""
        request_id = request_builder.generate_request_id()
        assert isinstance(request_id, str)
        assert len(request_id) > 0


class TestResponseHandler:
    """Test class for ResponseHandler."""

    @pytest.fixture
    def response_handler(self):
        """Create a ResponseHandler instance."""
        return ResponseHandler()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_response_handler_initialization(self, response_handler):
        """Test ResponseHandler initialization."""
        assert response_handler._request_id is None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_set_request_id(self, response_handler):
        """Test setting request ID."""
        request_id = "test-request-123"
        response_handler.set_request_id(request_id)
        assert response_handler._request_id == request_id

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_chat_response(self, response_handler):
        """Test creating a chat response."""
        response = response_handler.create_chat_response(
            content="Hello, world!",
            model="gpt-4",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="stop",
        )

        assert isinstance(response, ChatResponse)
        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.usage == {"input_tokens": 10, "output_tokens": 5}
        assert response.finish_reason == "stop"
        assert response.request_id is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_stream_response(self, response_handler):
        """Test creating a stream response."""
        response = response_handler.create_stream_response(
            content="Hello",
            model="gpt-4",
            finish_reason="stop",
        )

        assert isinstance(response, ChatStreamResponse)
        assert response.content == "Hello"
        assert response.model == "gpt-4"
        assert response.finish_reason == "stop"
        assert response.request_id is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_embedding_response(self, response_handler):
        """Test creating an embedding response."""
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        response = response_handler.create_embedding_response(
            embeddings=embeddings,
            model="text-embedding-ada-002",
            usage={"input_tokens": 10},
        )

        assert isinstance(response, EmbeddingResponse)
        assert response.embeddings == embeddings
        assert response.model == "text-embedding-ada-002"
        assert response.usage == {"input_tokens": 10}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_handle_provider_error_rate_limit(self, response_handler):
        """Test handling rate limit error."""
        error = Exception("rate limit exceeded")
        handled_error = response_handler.handle_provider_error(error, "openai")
        
        assert "Rate limit exceeded" in str(handled_error)
        assert "openai" in str(handled_error)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_handle_provider_error_quota(self, response_handler):
        """Test handling quota error."""
        error = Exception("quota exceeded")
        handled_error = response_handler.handle_provider_error(error, "anthropic")
        
        assert "Quota exceeded" in str(handled_error)
        assert "anthropic" in str(handled_error)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_handle_validation_error_messages(self, response_handler):
        """Test handling validation error for messages."""
        error = ValueError("messages cannot be empty")
        handled_error = response_handler.handle_validation_error(error)
        
        assert "Chat messages cannot be empty" in str(handled_error)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_handle_validation_error_temperature(self, response_handler):
        """Test handling validation error for temperature."""
        error = ValueError("temperature must be between 0 and 2")
        handled_error = response_handler.handle_validation_error(error)
        
        assert "Temperature must be between 0 and 2" in str(handled_error)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_response_content_valid(self, response_handler):
        """Test validating valid response content."""
        assert response_handler.validate_response_content("Valid content") is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_response_content_empty(self, response_handler):
        """Test validating empty response content."""
        assert response_handler.validate_response_content("") is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_response_content_too_long(self, response_handler):
        """Test validating response content that's too long."""
        long_content = "x" * 100001  # Over 100KB limit
        assert response_handler.validate_response_content(long_content) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_embeddings_valid(self, response_handler):
        """Test validating valid embeddings."""
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        assert response_handler.validate_embeddings(embeddings) is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_embeddings_empty(self, response_handler):
        """Test validating empty embeddings."""
        assert response_handler.validate_embeddings([]) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_validate_embeddings_invalid_type(self, response_handler):
        """Test validating embeddings with invalid type."""
        embeddings = [0.1, 0.2]  # Should be list of lists
        assert response_handler.validate_embeddings(embeddings) is False


class TestChatProcessor:
    """Test class for ChatProcessor."""

    @pytest.fixture
    def request_builder(self):
        """Create a RequestBuilder instance."""
        return RequestBuilder()

    @pytest.fixture
    def response_handler(self):
        """Create a ResponseHandler instance."""
        return ResponseHandler()

    @pytest.fixture
    def chat_processor(self, request_builder, response_handler):
        """Create a ChatProcessor instance."""
        return ChatProcessor(request_builder, response_handler)

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "Hello, how are you?"},
        ]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_chat_processor_initialization(self, chat_processor):
        """Test ChatProcessor initialization."""
        assert chat_processor.request_builder is not None
        assert chat_processor.response_handler is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_process_chat_completion_validation_error(self, chat_processor):
        """Test chat completion with validation error."""
        with pytest.raises(Exception, match="Chat messages cannot be empty"):
            await chat_processor.process_chat_completion(
                messages=[],
                user_id="user123",
                provider="openai",
            )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_providers(self, chat_processor):
        """Test getting available providers."""
        providers = chat_processor.get_available_providers()
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_provider_invalid(self, chat_processor):
        """Test getting invalid provider."""
        with pytest.raises(ValueError, match="not available"):
            chat_processor.get_provider("invalid_provider")

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_content_from_dict(self, chat_processor):
        """Test extracting content from dict response."""
        response = {"content": "Hello world"}
        content = chat_processor._extract_content(response)
        assert content == "Hello world"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_content_from_object(self, chat_processor):
        """Test extracting content from object response."""
        mock_response = MagicMock()
        mock_response.content = "Hello world"
        content = chat_processor._extract_content(mock_response)
        assert content == "Hello world"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_content_from_string(self, chat_processor):
        """Test extracting content from string response."""
        response = "Hello world"
        content = chat_processor._extract_content(response)
        assert content == "Hello world"