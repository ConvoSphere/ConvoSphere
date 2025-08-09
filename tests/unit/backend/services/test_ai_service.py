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

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

# Legacy tests for old AI service - these will be deprecated
# New tests are in test_ai_core.py, test_ai_middleware.py, test_ai_types.py, and test_ai_service_refactored.py
from backend.app.services.ai_service import AIService
from backend.app.services.ai.types.ai_types import CostInfo
from backend.app.services.ai.utils.cost_tracker import CostTracker


class TestCostTracker:
    """Test class for CostTracker."""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_cost_tracker_initialization(self):
        """Fast test for CostTracker initialization."""
        tracker = CostTracker()

        assert tracker.costs == []
        assert tracker.total_cost == 0.0
        assert tracker.total_tokens == 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_add_cost(self):
        """Fast test for adding cost information."""
        tracker = CostTracker()
        cost_info = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(UTC),
            user_id="user123",
            conversation_id="conv123",
        )

        tracker.add_cost(cost_info)

        assert len(tracker.costs) == 1
        assert tracker.total_cost == 0.03
        assert tracker.total_tokens == 100
        assert tracker.costs[0] == cost_info

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_total_cost(self):
        """Fast test for getting total cost."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4", tokens_used=100, cost_usd=0.03, timestamp=datetime.now(UTC)
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(UTC),
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        assert tracker.get_total_cost() == 0.04

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_total_tokens(self):
        """Fast test for getting total tokens."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4", tokens_used=100, cost_usd=0.03, timestamp=datetime.now(UTC)
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(UTC),
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        assert tracker.get_total_tokens() == 150

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_costs_by_user(self):
        """Comprehensive test for getting costs for specific user."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(UTC),
            user_id="user123",
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(UTC),
            user_id="user456",
        )

        tracker.add_cost(cost_info1)
        tracker.add_cost(cost_info2)

        user_costs = tracker.get_costs_by_user("user123")
        assert len(user_costs) == 1
        assert user_costs[0].user_id == "user123"

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_costs_by_conversation(self):
        """Comprehensive test for getting costs for specific conversation."""
        tracker = CostTracker()
        cost_info1 = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(UTC),
            conversation_id="conv123",
        )
        cost_info2 = CostInfo(
            model="gpt-3.5-turbo",
            tokens_used=50,
            cost_usd=0.01,
            timestamp=datetime.now(UTC),
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
        """Create AIService instance."""
        return AIService()

    @pytest.fixture
    def mock_litellm(self):
        """Mock LiteLLM client."""
        with patch("backend.app.services.ai_service.litellm") as mock:
            yield mock

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
            "usage": {"total_tokens": 50, "prompt_tokens": 30, "completion_tokens": 20},
        }

    # =============================================================================
    # FAST TESTS - Basic functionality
    # =============================================================================

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_ai_service_initialization_with_litellm(self):
        """Fast test for AIService initialization with LiteLLM."""
        with patch("backend.app.services.ai_service.litellm"):
            service = AIService()
            assert service is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_ai_service_initialization_without_litellm(self):
        """Fast test for AIService initialization without LiteLLM."""
        with patch("backend.app.services.ai_service.litellm", None):
            service = AIService()
            assert service is not None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion(
        self, ai_service, mock_litellm, sample_messages, mock_completion_response
    ):
        """Fast test for chat completion."""
        mock_litellm.completion.return_value = mock_completion_response

        response = await ai_service.chat_completion(
            messages=sample_messages,
            model="gpt-4",
            temperature=0.7,
            max_tokens=100,
        )

        assert response is not None
        assert "choices" in response
        assert len(response["choices"]) > 0
        mock_litellm.completion.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_embeddings(self, ai_service, mock_litellm):
        """Fast test for getting embeddings."""
        mock_embeddings = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
        mock_litellm.embedding.return_value = mock_embeddings

        embeddings = await ai_service.get_embeddings(
            texts=["Hello world"], model="text-embedding-ada-002"
        )

        assert embeddings is not None
        assert len(embeddings) > 0
        mock_litellm.embedding.assert_called_once()

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_models(self, ai_service):
        """Fast test for getting available models."""
        models = ai_service.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_available_providers(self, ai_service):
        """Fast test for getting available providers."""
        providers = ai_service.get_available_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_is_enabled(self, ai_service):
        """Fast test for checking if AI service is enabled."""
        enabled = ai_service.is_enabled()
        assert isinstance(enabled, bool)

    # =============================================================================
    # COMPREHENSIVE TESTS - Advanced functionality and edge cases
    # =============================================================================

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_with_tools(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Comprehensive test for chat completion with tools."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                },
            }
        ]

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "I'll get the weather for you.",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "New York"}',
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"total_tokens": 100},
        }
        mock_litellm.completion.return_value = mock_response

        response = await ai_service.chat_completion(
            messages=sample_messages,
            model="gpt-4",
            tools=tools,
        )

        assert response is not None
        assert "choices" in response
        assert "tool_calls" in response["choices"][0]["message"]

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_embeddings_batch(self, ai_service, mock_litellm):
        """Comprehensive test for getting embeddings in batch."""
        mock_embeddings = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }
        mock_litellm.embedding.return_value = mock_embeddings

        embeddings = await ai_service.get_embeddings(
            texts=["Hello", "World"], model="text-embedding-ada-002"
        )

        assert embeddings is not None
        assert len(embeddings) == 2

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_summary(self, ai_service):
        """Comprehensive test for getting cost summary."""
        summary = ai_service.get_cost_summary()
        assert isinstance(summary, dict)
        assert "total_cost" in summary
        assert "total_tokens" in summary
        assert "costs_by_model" in summary

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_health_check(self, ai_service):
        """Comprehensive test for health check."""
        health = ai_service.health_check()
        assert isinstance(health, dict)
        assert "status" in health
        assert "message" in health

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_chat_completion_with_rag(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Comprehensive test for chat completion with RAG."""
        # Mock RAG context
        rag_context = "Based on the knowledge base: The weather is sunny."
        enhanced_messages = sample_messages + [
            {"role": "system", "content": f"Context: {rag_context}"}
        ]

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Based on the context, the weather is sunny.",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 80},
        }
        mock_litellm.completion.return_value = mock_response

        response = await ai_service.chat_completion(
            messages=enhanced_messages,
            model="gpt-4",
            rag_context=rag_context,
        )

        assert response is not None
        assert "choices" in response

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_execute_tool_call(self, ai_service):
        """Comprehensive test for executing tool calls."""
        tool_call = {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "New York"}',
            },
        }

        with patch.object(ai_service, "_execute_function") as mock_execute:
            mock_execute.return_value = {"temperature": 72, "condition": "sunny"}
            result = await ai_service.execute_tool_call(tool_call)

            assert result is not None
            mock_execute.assert_called_once()

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_generate_response(self, ai_service, mock_litellm, sample_messages):
        """Comprehensive test for generating response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Generated response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }
        mock_litellm.completion.return_value = mock_response

        response = await ai_service.generate_response(
            messages=sample_messages,
            model="gpt-4",
        )

        assert response is not None
        assert isinstance(response, AIResponse)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_generate_response_with_tools(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Comprehensive test for generating response with tools."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Perform calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"},
                        },
                        "required": ["expression"],
                    },
                },
            }
        ]

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "I'll calculate that for you.",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call_456",
                                "type": "function",
                                "function": {
                                    "name": "calculator",
                                    "arguments": '{"expression": "2+2"}',
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"total_tokens": 100},
        }
        mock_litellm.completion.return_value = mock_response

        response = await ai_service.generate_response(
            messages=sample_messages,
            model="gpt-4",
            tools=tools,
        )

        assert response is not None
        assert isinstance(response, AIResponse)

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_embed_text(self, ai_service, mock_litellm):
        """Comprehensive test for embedding text."""
        mock_embeddings = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
        mock_litellm.embedding.return_value = mock_embeddings

        embedding = await ai_service.embed_text("Hello world")
        assert embedding is not None
        assert len(embedding) > 0

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_get_response(self, ai_service, mock_litellm, sample_messages):
        """Comprehensive test for getting response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Response content",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }
        mock_litellm.completion.return_value = mock_response

        response = await ai_service.get_response(
            messages=sample_messages,
            model="gpt-4",
        )

        assert response is not None
        assert "content" in response

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_track_cost(self, ai_service):
        """Comprehensive test for cost tracking."""
        cost_info = CostInfo(
            model="gpt-4",
            tokens_used=100,
            cost_usd=0.03,
            timestamp=datetime.now(UTC),
            user_id="user123",
            conversation_id="conv123",
        )

        ai_service.track_cost(cost_info)
        summary = ai_service.get_cost_summary()

        assert summary["total_cost"] == 0.03
        assert summary["total_tokens"] == 100

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_error_handling_chat_completion(
        self, ai_service, mock_litellm, sample_messages
    ):
        """Comprehensive test for error handling in chat completion."""
        mock_litellm.completion.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            await ai_service.chat_completion(
                messages=sample_messages,
                model="gpt-4",
            )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_error_handling_embeddings(self, ai_service, mock_litellm):
        """Comprehensive test for error handling in embeddings."""
        mock_litellm.embedding.side_effect = Exception("Embedding Error")

        with pytest.raises(Exception):
            await ai_service.get_embeddings(
                texts=["Hello world"], model="text-embedding-ada-002"
            )

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    def test_cost_tracking_accuracy(self, ai_service):
        """Comprehensive test for cost tracking accuracy."""
        # Add multiple costs
        costs = [
            CostInfo(
                model="gpt-4",
                tokens_used=100,
                cost_usd=0.03,
                timestamp=datetime.now(UTC),
            ),
            CostInfo(
                model="gpt-3.5-turbo",
                tokens_used=50,
                cost_usd=0.01,
                timestamp=datetime.now(UTC),
            ),
        ]

        for cost in costs:
            ai_service.track_cost(cost)

        summary = ai_service.get_cost_summary()
        assert summary["total_cost"] == 0.04
        assert summary["total_tokens"] == 150

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_model_selection(self, ai_service, mock_litellm, sample_messages):
        """Comprehensive test for model selection."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Model specific response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }
        mock_litellm.completion.return_value = mock_response

        # Test different models
        models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
        for model in models:
            response = await ai_service.chat_completion(
                messages=sample_messages,
                model=model,
            )
            assert response is not None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_temperature_control(self, ai_service, mock_litellm, sample_messages):
        """Comprehensive test for temperature control."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Temperature controlled response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }
        mock_litellm.completion.return_value = mock_response

        # Test different temperature values
        temperatures = [0.0, 0.5, 1.0]
        for temp in temperatures:
            response = await ai_service.chat_completion(
                messages=sample_messages,
                model="gpt-4",
                temperature=temp,
            )
            assert response is not None

    @pytest.mark.comprehensive
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_max_tokens_control(self, ai_service, mock_litellm, sample_messages):
        """Comprehensive test for max tokens control."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Token limited response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }
        mock_litellm.completion.return_value = mock_response

        # Test different max token values
        max_tokens_list = [10, 50, 100]
        for max_tokens in max_tokens_list:
            response = await ai_service.chat_completion(
                messages=sample_messages,
                model="gpt-4",
                max_tokens=max_tokens,
            )
            assert response is not None