"""
Unit tests for AI Service (Current Modular Implementation).

This module tests the current AI service functionality using the new modular architecture.
The old legacy tests have been moved to tests/legacy/ for reference.

Tested functionality:
- Chat completion and streaming
- Embedding generation
- Cost tracking
- RAG functionality
- Tool execution
- Model management
- Backward compatibility
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from backend.app.services.ai_service import AIService, get_ai_service
from backend.app.services.ai.types.ai_types import (
    ChatResponse,
    ChatStreamResponse,
    EmbeddingResponse,
    CostInfo,
)


class TestAIServiceCurrent:
    """Test class for current modular AI service implementation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def ai_service(self, mock_db):
        """Create an AIService instance."""
        return AIService(mock_db)

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "Hello, how are you?"},
        ]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_ai_service_initialization(self, ai_service):
        """Test AIService initialization with modular components."""
        assert ai_service.db is not None
        assert ai_service.request_builder is not None
        assert ai_service.response_handler is not None
        assert ai_service.chat_processor is not None
        assert ai_service.rag_middleware is not None
        assert ai_service.tool_middleware is not None
        assert ai_service.cost_middleware is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_basic(self, ai_service, sample_messages):
        """Test basic chat completion functionality."""
        # Mock the chat processor
        mock_response = ChatResponse(
            content="Hello! I'm doing well, thank you for asking.",
            model="gpt-3.5-turbo",
            usage={"input_tokens": 10, "output_tokens": 15},
            finish_reason="stop",
        )
        
        with patch.object(ai_service.chat_processor, 'process_chat_completion', 
                         new_callable=AsyncMock, return_value=mock_response):
            response = await ai_service.chat_completion(
                messages=sample_messages,
                user_id="user123",
                provider="openai",
                model="gpt-3.5-turbo",
            )
            
            assert isinstance(response, ChatResponse)
            assert response.content == "Hello! I'm doing well, thank you for asking."
            assert response.model == "gpt-3.5-turbo"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_stream(self, ai_service, sample_messages):
        """Test streaming chat completion."""
        # Mock the chat processor
        mock_responses = [
            ChatStreamResponse(content="Hello", model="gpt-3.5-turbo", finish_reason=None),
            ChatStreamResponse(content=" world", model="gpt-3.5-turbo", finish_reason=None),
            ChatStreamResponse(content="!", model="gpt-3.5-turbo", finish_reason="stop"),
        ]
        
        with patch.object(ai_service.chat_processor, 'process_chat_completion_stream', 
                         new_callable=AsyncMock) as mock_stream:
            mock_stream.return_value = mock_responses
            
            responses = []
            async for response in ai_service.chat_completion_stream(
                messages=sample_messages,
                user_id="user123",
                provider="openai",
                model="gpt-3.5-turbo",
            ):
                responses.append(response)
            
            assert len(responses) == 3
            assert all(isinstance(r, ChatStreamResponse) for r in responses)

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_embeddings(self, ai_service):
        """Test embedding generation."""
        texts = ["Hello world", "Test embedding"]
        mock_response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            model="text-embedding-ada-002",
            usage={"input_tokens": 10},
        )
        
        with patch.object(ai_service.chat_processor, 'process_embeddings', 
                         new_callable=AsyncMock, return_value=mock_response):
            response = await ai_service.get_embeddings(
                texts=texts,
                provider="openai",
                model="text-embedding-ada-002",
            )
            
            assert isinstance(response, EmbeddingResponse)
            assert len(response.embeddings) == 2
            assert response.model == "text-embedding-ada-002"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_execute_tools(self, ai_service):
        """Test tool execution."""
        ai_response = """
        I'll help you calculate that.
        
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>
        {"expression": "2 + 2"}
        </parameters>
        </tool_call>
        """
        
        mock_results = [{"tool": "calculator", "result": "4"}]
        
        with patch.object(ai_service.tool_middleware, 'execute_tools_from_response', 
                         new_callable=AsyncMock, return_value=mock_results):
            results = await ai_service.execute_tools(ai_response, "user123")
            
            assert results == mock_results
            assert len(results) == 1
            assert results[0]["tool"] == "calculator"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_providers(self, ai_service):
        """Test getting available providers."""
        with patch.object(ai_service.chat_processor, 'get_available_providers', 
                         return_value=["openai", "anthropic"]):
            providers = ai_service.get_available_providers()
            
            assert providers == ["openai", "anthropic"]
            assert "openai" in providers
            assert "anthropic" in providers

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_models(self, ai_service):
        """Test getting available models for a provider."""
        models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        
        with patch.object(ai_service.chat_processor, 'get_available_models', 
                         return_value=models):
            available_models = ai_service.get_available_models("openai")
            
            assert available_models == models
            assert "gpt-4" in available_models
            assert "gpt-3.5-turbo" in available_models

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_info(self, ai_service):
        """Test getting model information."""
        model_info = {
            "name": "gpt-4",
            "provider": "openai",
            "max_tokens": 8192,
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06,
        }
        
        with patch.object(ai_service.chat_processor, 'get_model_info', 
                         return_value=model_info):
            info = ai_service.get_model_info("openai", "gpt-4")
            
            assert info == model_info
            assert info["name"] == "gpt-4"
            assert info["provider"] == "openai"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_summary(self, ai_service):
        """Test getting cost summary."""
        cost_summary = {
            "total_cost": 0.15,
            "total_tokens": 500,
            "daily_cost": 0.05,
            "monthly_cost": 0.15,
        }
        
        with patch.object(ai_service.cost_middleware, 'get_cost_summary', 
                         return_value=cost_summary):
            summary = ai_service.get_cost_summary("user123", 30)
            
            assert summary == cost_summary
            assert summary["total_cost"] == 0.15
            assert summary["total_tokens"] == 500

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_daily_costs(self, ai_service):
        """Test getting daily costs."""
        daily_costs = [
            {"date": "2024-01-01", "cost": 0.02, "tokens": 100},
            {"date": "2024-01-02", "cost": 0.03, "tokens": 150},
        ]
        
        with patch.object(ai_service.cost_middleware, 'get_daily_costs', 
                         return_value=daily_costs):
            costs = ai_service.get_daily_costs("user123", 7)
            
            assert costs == daily_costs
            assert len(costs) == 2
            assert costs[0]["date"] == "2024-01-01"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_usage_stats(self, ai_service):
        """Test getting model usage statistics."""
        usage_stats = {
            "gpt-4": {
                "total_requests": 50,
                "total_tokens": 2500,
                "total_cost": 0.075,
            },
            "gpt-3.5-turbo": {
                "total_requests": 100,
                "total_tokens": 3000,
                "total_cost": 0.045,
            },
        }
        
        with patch.object(ai_service.cost_middleware, 'get_model_usage_stats', 
                         return_value=usage_stats):
            stats = ai_service.get_model_usage_stats("user123", 30)
            
            assert stats == usage_stats
            assert "gpt-4" in stats
            assert "gpt-3.5-turbo" in stats
            assert stats["gpt-4"]["total_requests"] == 50

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_with_rag(self, ai_service, sample_messages):
        """Test chat completion with RAG enabled."""
        # Mock the middleware
        with patch.object(ai_service.rag_middleware, 'should_apply_rag', return_value=True):
            with patch.object(ai_service.rag_middleware, 'process', 
                             new_callable=AsyncMock, return_value=sample_messages):
                with patch.object(ai_service.chat_processor, 'process_chat_completion', 
                                 new_callable=AsyncMock) as mock_process:
                    mock_response = ChatResponse(
                        content="Response with RAG context",
                        model="gpt-4",
                        usage={"input_tokens": 20, "output_tokens": 10},
                        finish_reason="stop",
                    )
                    mock_process.return_value = mock_response
                    
                    response = await ai_service.chat_completion(
                        messages=sample_messages,
                        user_id="user123",
                        provider="openai",
                        model="gpt-4",
                        use_knowledge_base=True,
                    )
                    
                    assert isinstance(response, ChatResponse)
                    assert response.content == "Response with RAG context"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_with_tools(self, ai_service, sample_messages):
        """Test chat completion with tools enabled."""
        # Mock the middleware
        with patch.object(ai_service.tool_middleware, 'should_apply_tools', return_value=True):
            with patch.object(ai_service.tool_middleware, 'process', 
                             new_callable=AsyncMock, return_value=sample_messages):
                with patch.object(ai_service.chat_processor, 'process_chat_completion', 
                                 new_callable=AsyncMock) as mock_process:
                    mock_response = ChatResponse(
                        content="Response with tools",
                        model="gpt-4",
                        usage={"input_tokens": 15, "output_tokens": 8},
                        finish_reason="stop",
                    )
                    mock_process.return_value = mock_response
                    
                    response = await ai_service.chat_completion(
                        messages=sample_messages,
                        user_id="user123",
                        provider="openai",
                        model="gpt-4",
                        use_tools=True,
                    )
                    
                    assert isinstance(response, ChatResponse)
                    assert response.content == "Response with tools"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_error_handling_chat_completion(self, ai_service, sample_messages):
        """Test error handling in chat completion."""
        with patch.object(ai_service.chat_processor, 'process_chat_completion', 
                         new_callable=AsyncMock, side_effect=Exception("Provider error")):
            with pytest.raises(Exception, match="Chat completion failed"):
                await ai_service.chat_completion(
                    messages=sample_messages,
                    user_id="user123",
                    provider="openai",
                )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_error_handling_embeddings(self, ai_service):
        """Test error handling in embeddings generation."""
        texts = ["Hello world"]
        
        with patch.object(ai_service.chat_processor, 'process_embeddings', 
                         new_callable=AsyncMock, side_effect=Exception("Embedding error")):
            with pytest.raises(Exception, match="Embeddings generation failed"):
                await ai_service.get_embeddings(
                    texts=texts,
                    provider="openai",
                )

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_backward_compatibility_api(self, ai_service):
        """Test backward compatibility of API methods."""
        # All original methods should be available
        assert hasattr(ai_service, 'chat_completion')
        assert hasattr(ai_service, 'chat_completion_stream')
        assert hasattr(ai_service, 'get_embeddings')
        assert hasattr(ai_service, 'execute_tools')
        assert hasattr(ai_service, 'get_available_providers')
        assert hasattr(ai_service, 'get_provider')
        assert hasattr(ai_service, 'get_available_models')
        assert hasattr(ai_service, 'get_model_info')
        assert hasattr(ai_service, 'get_cost_summary')
        assert hasattr(ai_service, 'get_daily_costs')
        assert hasattr(ai_service, 'get_model_usage_stats')


class TestAIServiceSingleton:
    """Test class for AI service singleton functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_ai_service_creation(self, mock_db):
        """Test AI service singleton creation."""
        # Clear any existing singleton
        import backend.app.services.ai_service as ai_service_module
        ai_service_module.ai_service = None
        
        # Create new service
        service = get_ai_service(mock_db)
        
        assert service is not None
        assert isinstance(service, AIService)
        assert service.db == mock_db

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_ai_service_singleton(self, mock_db):
        """Test AI service singleton behavior."""
        # Clear any existing singleton
        import backend.app.services.ai_service as ai_service_module
        ai_service_module.ai_service = None
        
        # Create first service
        service1 = get_ai_service(mock_db)
        
        # Create second service (should return same instance)
        service2 = get_ai_service(mock_db)
        
        assert service1 is service2
        assert service1.db == service2.db

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_ai_service_no_db(self):
        """Test AI service creation without database."""
        # Clear any existing singleton
        import backend.app.services.ai_service as ai_service_module
        ai_service_module.ai_service = None
        
        with pytest.raises(ValueError, match="Database session is required"):
            get_ai_service(None)