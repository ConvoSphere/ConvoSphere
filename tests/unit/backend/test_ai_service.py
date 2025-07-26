"""
Unit tests for AI Service.

This module tests the AI service functionality including:
- Chat completion and streaming
- Embedding generation
- Cost tracking
- RAG functionality
- Tool execution
- Model management
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.services.ai_service import AIResponse, AIService, CostInfo, CostTracker


class TestCostTracker:
    """Test class for CostTracker."""

    def test_cost_tracker_initialization(self):
        """Test CostTracker initialization."""
        tracker = CostTracker()

        assert tracker.costs == []
        assert tracker.total_cost == 0.0
        assert tracker.total_tokens == 0

    def test_add_cost(self):
        """Test adding cost information."""
        tracker = CostTracker()
        cost_info = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(),
            user_id="user123",
            conversation_id="conv123",
        )

        tracker.add_cost(cost_info)

        assert len(tracker.costs) == 1
        assert tracker.total_cost == 0.03
        assert tracker.total_tokens == 100
        assert tracker.costs[0] == cost_info

    def test_get_total_cost(self):
        """Test getting total cost."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4", tokens_used=100, cost_usd=0.03, timestamp=datetime.now()
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(),
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        assert tracker.get_total_cost() == 0.04

    def test_get_total_tokens(self):
        """Test getting total tokens."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4", tokens_used=100, cost_usd=0.03, timestamp=datetime.now()
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(),
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        assert tracker.get_total_tokens() == 150

    def test_get_costs_by_user(self):
        """Test getting costs for specific user."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(),
            user_id="user123",
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(),
            user_id="user456",
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        user_costs = tracker.get_costs_by_user("user123")
        assert len(user_costs) == 1
        assert user_costs[0].user_id == "user123"

    def test_get_costs_by_conversation(self):
        """Test getting costs for specific conversation."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(),
            conversation_id="conv123",
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(),
            conversation_id="conv456",
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        conv_costs = tracker.get_costs_by_conversation("conv123")
        assert len(conv_costs) == 1
        assert conv_costs[0].conversation_id == "conv123"


class TestAIService:
    """Test class for AIService."""

    @pytest.fixture
    def ai_service(self):
        """Create AIService instance for testing."""
        with patch("backend.app.services.ai_service.LITELLM_AVAILABLE", True):
            service = AIService()
            service.cost_tracker = CostTracker()
            return service

    @pytest.fixture
    def mock_litellm(self):
        """Mock LiteLLM functions."""
        with patch("backend.app.services.ai_service.litellm") as mock_litellm:
            mock_litellm.completion = AsyncMock()
            mock_litellm.acompletion = AsyncMock()
            yield mock_litellm

    @pytest.fixture
    def sample_messages(self):
        """Sample messages for testing."""
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
        ]

    @pytest.fixture
    def mock_completion_response(self):
        """Mock completion response."""
        return {
            "choices": [
                {
                    "message": {
                        "content": "I'm doing well, thank you for asking!",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50, "prompt_tokens": 20, "completion_tokens": 30},
            "model": "gpt-4",
        }

    def test_ai_service_initialization_with_litellm(self):
        """Test AIService initialization when LiteLLM is available."""
        with patch("backend.app.services.ai_service.LITELLM_AVAILABLE", True):
            service = AIService()
            assert service.enabled is True

    def test_ai_service_initialization_without_litellm(self):
        """Test AIService initialization when LiteLLM is not available."""
        with patch("backend.app.services.ai_service.LITELLM_AVAILABLE", False):
            service = AIService()
            assert service.enabled is False

    @pytest.mark.asyncio
    async def test_chat_completion(
        self, ai_service, mock_litellm, sample_messages, mock_completion_response
    ):
        """Test chat completion functionality."""
        # Mock the acompletion function directly
        with patch(
            "backend.app.services.ai_service.acompletion",
            return_value=mock_completion_response,
        ):
            result = await ai_service.chat_completion(
                messages=sample_messages,
                model="gpt-4",
                temperature=0.7,
                user_id="user123",
                conversation_id="conv123",
            )

        assert result == mock_completion_response

        # Verify cost tracking
        assert len(ai_service.cost_tracker.costs) == 1
        cost_info = ai_service.cost_tracker.costs[0]
        assert cost_info.model == "gpt-4"
        assert cost_info.tokens_used == 50
        assert cost_info.user_id == "user123"
        assert cost_info.conversation_id == "conv123"

    @pytest.mark.asyncio
    async def test_chat_completion_with_tools(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Test chat completion with tools."""
        tools = [{"name": "test_tool", "description": "A test tool"}]
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "I'll use the test tool",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {"name": "test_tool", "arguments": "{}"},
                            }
                        ],
                    }
                }
            ],
            "usage": {"total_tokens": 100},
            "model": "gpt-4",
        }

        with patch(
            "backend.app.services.ai_service.acompletion", return_value=mock_response
        ):
            result = await ai_service.chat_completion(
                messages=sample_messages, tools=tools, tool_choice="auto"
            )

        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_embeddings(self, ai_service, mock_litellm):
        """Test embedding generation."""
        mock_embeddings = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_response = {
            "choices": [{"message": {"content": "test"}}],
            "usage": {"total_tokens": 10},
            "embeddings": mock_embeddings,
        }

        with patch(
            "backend.app.services.ai_service.acompletion", return_value=mock_response
        ):
            result = await ai_service.get_embeddings("test text")

            assert result == mock_embeddings

    @pytest.mark.asyncio
    async def test_get_embeddings_batch(self, ai_service, mock_litellm):
        """Test batch embedding generation."""
        texts = ["text1", "text2", "text3"]
        mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        with patch("backend.app.services.ai_service.acompletion") as mock_acompletion:
            mock_acompletion.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 10},
                "embeddings": mock_embeddings[
                    0
                ],  # Return first embedding for each call
            }

            result = await ai_service.get_embeddings_batch(texts)

            # Since the current implementation doesn't actually batch, we expect individual calls
            assert len(result) == len(texts)

    def test_get_available_models(self, ai_service):
        """Test getting available models."""
        ai_service.models = {
            "gpt-4": {"provider": "openai", "max_tokens": 8192},
            "gpt-3.5-turbo": {"provider": "openai", "max_tokens": 4096},
        }

        result = ai_service.get_available_models()

        assert result == ai_service.models

    def test_get_available_providers(self, ai_service):
        """Test getting available providers."""
        ai_service.providers = {
            "openai": {"api_key": "sk-..."},
            "anthropic": {"api_key": "sk-ant-..."},
        }

        result = ai_service.get_available_providers()

        assert result == ai_service.providers

    def test_get_cost_summary(self, ai_service):
        """Test getting cost summary."""
        cost_info = CostInfo(
            model="gpt-4", tokens_used=100, cost_usd=0.03, timestamp=datetime.now()
        )
        ai_service.cost_tracker.add_cost(cost_info)

        summary = ai_service.get_cost_summary()

        assert summary["total_cost"] == 0.03
        assert summary["total_tokens"] == 100
        assert len(summary["costs"]) == 1

    def test_is_enabled(self, ai_service):
        """Test checking if AI service is enabled."""
        ai_service.enabled = True
        assert ai_service.is_enabled() is True

        ai_service.enabled = False
        assert ai_service.is_enabled() is False

    def test_health_check(self, ai_service):
        """Test health check functionality."""
        ai_service.enabled = True
        ai_service.models = {"gpt-4": {}}
        ai_service.providers = {"openai": {}}

        health = ai_service.health_check()

        assert health["status"] == "healthy"
        assert health["enabled"] is True
        assert "models_count" in health
        assert "providers_count" in health

    @pytest.mark.asyncio
    async def test_chat_completion_with_rag(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Test chat completion with RAG functionality."""
        # Mock knowledge search
        with patch.object(ai_service, "_search_knowledge_for_context") as mock_search:
            mock_search.return_value = [{"content": "Relevant context", "score": 0.9}]

            # Mock tool preparation
            with patch.object(
                ai_service, "_prepare_tools_for_completion"
            ) as mock_tools:
                mock_tools.return_value = []

                mock_response = {
                    "choices": [
                        {
                            "message": {
                                "content": "Response with context",
                                "role": "assistant",
                            }
                        }
                    ],
                    "usage": {"total_tokens": 100},
                    "model": "gpt-4",
                }
                with patch(
                    "backend.app.services.ai_service.acompletion",
                    return_value=mock_response,
                ):
                    result = await ai_service.chat_completion_with_rag(
                        messages=sample_messages,
                        user_id="user123",
                        use_knowledge_base=True,
                        use_tools=True,
                    )

                assert result == mock_response
                mock_search.assert_called_once()
                mock_tools.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tool_call(self, ai_service):
        """Test tool execution."""
        tool_call = {
            "id": "call_123",
            "function": {"name": "test_tool", "arguments": '{"param": "value"}'},
        }

        # Mock tool service
        with patch("backend.app.services.ai_service.tool_service") as mock_tool_service:
            mock_tool_service.execute_tool.return_value = {"result": "success"}

            result = await ai_service.execute_tool_call(tool_call, "user123")

            assert result["result"] == "success"
            mock_tool_service.execute_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response(self, ai_service, mock_litellm, sample_messages):
        """Test generate_response method."""
        mock_response = {
            "choices": [
                {"message": {"content": "Generated response", "role": "assistant"}}
            ],
            "usage": {"total_tokens": 50},
            "model": "gpt-4",
        }
        with patch(
            "backend.app.services.ai_service.acompletion", return_value=mock_response
        ):
            result = await ai_service.generate_response(sample_messages, "gpt-4")

        assert isinstance(result, AIResponse)
        assert result.content == "Generated response"
        assert result.message_type == "text"

    @pytest.mark.asyncio
    async def test_generate_response_with_tools(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Test generate_response_with_tools method."""
        tools = [{"name": "test_tool"}]
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Response with tools",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "function": {"name": "test_tool", "arguments": "{}"},
                            }
                        ],
                    }
                }
            ],
            "usage": {"total_tokens": 100},
            "model": "gpt-4",
        }
        with patch(
            "backend.app.services.ai_service.acompletion", return_value=mock_response
        ):
            result = await ai_service.generate_response_with_tools(
                sample_messages, tools, "gpt-4"
            )

        assert isinstance(result, AIResponse)
        assert result.content == "Response with tools"
        assert result.tool_calls is not None
        assert len(result.tool_calls) == 1

    @pytest.mark.asyncio
    async def test_embed_text(self, ai_service, mock_litellm):
        """Test embed_text method."""
        mock_embeddings = [0.1, 0.2, 0.3]
        mock_litellm.embedding.return_value = {"data": [{"embedding": mock_embeddings}]}

        result = await ai_service.embed_text("test text")

        assert result == mock_embeddings

    @pytest.mark.asyncio
    async def test_get_response(self, ai_service, mock_litellm, sample_messages):
        """Test get_response method."""
        # Mock RAG functionality
        with patch.object(ai_service, "chat_completion_with_rag") as mock_rag:
            mock_rag.return_value = {
                "choices": [
                    {"message": {"content": "Final response", "role": "assistant"}}
                ]
            }

            result = await ai_service.get_response(
                conversation_id="conv123",
                user_message="Hello",
                user_id="user123",
                use_rag=True,
                use_tools=True,
            )

            assert isinstance(result, AIResponse)
            assert result.content == "Final response"

    def test_track_cost(self, ai_service):
        """Test cost tracking functionality."""
        response = {
            "usage": {
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50,
            },
            "model": "gpt-4",
        }

        ai_service._track_cost(response, "gpt-4", "user123", "conv123")

        assert len(ai_service.cost_tracker.costs) == 1
        cost_info = ai_service.cost_tracker.costs[0]
        assert cost_info.model == "gpt-4"
        assert cost_info.tokens_used == 100
        assert cost_info.user_id == "user123"
        assert cost_info.conversation_id == "conv123"

    @pytest.mark.asyncio
    async def test_error_handling_chat_completion(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Test error handling in chat completion."""
        mock_litellm.acompletion.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            await ai_service.chat_completion(sample_messages)

    @pytest.mark.asyncio
    async def test_error_handling_embeddings(self, ai_service, mock_litellm):
        """Test error handling in embedding generation."""
        mock_litellm.embedding.side_effect = Exception("Embedding Error")

        with pytest.raises(Exception):
            await ai_service.get_embeddings("test text")

    def test_cost_tracking_accuracy(self, ai_service):
        """Test cost tracking accuracy with multiple calls."""
        responses = [
            {"usage": {"total_tokens": 100}, "model": "gpt-4"},
            {"usage": {"total_tokens": 200}, "model": "gpt-3.5-turbo"},
        ]

        for response in responses:
            ai_service._track_cost(response, response["model"])

        assert ai_service.cost_tracker.get_total_tokens() == 300
        assert len(ai_service.cost_tracker.costs) == 2

    @pytest.mark.asyncio
    async def test_model_selection(self, ai_service, mock_litellm, sample_messages):
        """Test model selection functionality."""
        mock_response = {
            "choices": [{"message": {"content": "Response", "role": "assistant"}}],
            "usage": {"total_tokens": 50},
            "model": "gpt-3.5-turbo",
        }
        mock_litellm.acompletion.return_value = mock_response

        # Test with specific model
        await ai_service.chat_completion(sample_messages, model="gpt-3.5-turbo")

        call_args = mock_litellm.acompletion.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_temperature_control(self, ai_service, mock_litellm, sample_messages):
        """Test temperature parameter control."""
        mock_response = {
            "choices": [{"message": {"content": "Response", "role": "assistant"}}],
            "usage": {"total_tokens": 50},
            "model": "gpt-4",
        }
        mock_litellm.acompletion.return_value = mock_response

        await ai_service.chat_completion(sample_messages, temperature=0.1)

        call_args = mock_litellm.acompletion.call_args
        assert call_args[1]["temperature"] == 0.1

    @pytest.mark.asyncio
    async def test_max_tokens_control(self, ai_service, mock_litellm, sample_messages):
        """Test max_tokens parameter control."""
        mock_response = {
            "choices": [{"message": {"content": "Response", "role": "assistant"}}],
            "usage": {"total_tokens": 50},
            "model": "gpt-4",
        }
        mock_litellm.acompletion.return_value = mock_response

        await ai_service.chat_completion(sample_messages, max_tokens=1000)

        call_args = mock_litellm.acompletion.call_args
        assert call_args[1]["max_tokens"] == 1000
