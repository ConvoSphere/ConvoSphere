"""
Unit tests for AI Service Middleware Modules.

This module tests the new modular AI service middleware components:
- RAGMiddleware
- ToolMiddleware
- CostMiddleware
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from backend.app.services.ai.middleware import RAGMiddleware, ToolMiddleware, CostMiddleware
from backend.app.services.ai.types.ai_types import RAGContext, ToolInfo, ToolCall


class TestRAGMiddleware:
    """Test class for RAGMiddleware."""

    @pytest.fixture
    def rag_middleware(self):
        """Create a RAGMiddleware instance."""
        return RAGMiddleware()

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "What is the capital of France?"},
        ]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_rag_middleware_initialization(self, rag_middleware):
        """Test RAGMiddleware initialization."""
        assert rag_middleware.rag_service is None
        assert rag_middleware._max_context_chunks == 5

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_should_apply_rag_enabled(self, rag_middleware, sample_messages):
        """Test should_apply_rag when RAG is enabled."""
        assert rag_middleware.should_apply_rag(sample_messages, True) is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_should_apply_rag_disabled(self, rag_middleware, sample_messages):
        """Test should_apply_rag when RAG is disabled."""
        assert rag_middleware.should_apply_rag(sample_messages, False) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_should_apply_rag_no_user_messages(self, rag_middleware):
        """Test should_apply_rag when no user messages."""
        messages = [{"role": "assistant", "content": "Hello"}]
        assert rag_middleware.should_apply_rag(messages, True) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_process_no_rag_service(self, rag_middleware, sample_messages):
        """Test process when no RAG service is available."""
        processed_messages = await rag_middleware.process(
            sample_messages, "user123", 5
        )
        assert processed_messages == sample_messages

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_user_messages(self, rag_middleware):
        """Test extracting user messages."""
        messages = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
        ]
        user_messages = rag_middleware._extract_user_messages(messages)
        assert len(user_messages) == 2
        assert user_messages[0] == "Question 1"
        assert user_messages[1] == "Question 2"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_parse_rag_chunks(self, rag_middleware):
        """Test parsing RAG chunks."""
        chunks = [
            {"content": "Chunk 1", "metadata": {"source": "doc1"}},
            {"content": "Chunk 2", "metadata": {"source": "doc2"}},
        ]
        parsed_chunks = rag_middleware._parse_rag_chunks(chunks)
        assert len(parsed_chunks) == 2
        assert parsed_chunks[0]["content"] == "Chunk 1"
        assert parsed_chunks[0]["source"] == "doc1"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_sources(self, rag_middleware):
        """Test extracting sources from chunks."""
        chunks = [
            {"content": "Chunk 1", "source": "doc1"},
            {"content": "Chunk 2", "source": "doc2"},
            {"content": "Chunk 3", "source": "doc1"},  # Duplicate
        ]
        sources = rag_middleware._extract_sources(chunks)
        assert len(sources) == 2
        assert "doc1" in sources
        assert "doc2" in sources

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_context_summary(self, rag_middleware):
        """Test creating context summary."""
        chunks = [
            {"content": "First chunk content"},
            {"content": "Second chunk content"},
        ]
        summary = rag_middleware._create_context_summary(chunks)
        assert "First chunk content" in summary
        assert "Second chunk content" in summary
        assert "Context:" in summary

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_context_summary_empty(self, rag_middleware):
        """Test creating context summary with empty chunks."""
        summary = rag_middleware._create_context_summary([])
        assert summary == ""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_create_context_summary_too_many_chunks(self, rag_middleware):
        """Test creating context summary with too many chunks."""
        chunks = [{"content": f"Chunk {i}"} for i in range(10)]
        summary = rag_middleware._create_context_summary(chunks, max_chunks=3)
        assert "Chunk 0" in summary
        assert "Chunk 1" in summary
        assert "Chunk 2" in summary
        assert "Chunk 3" not in summary


class TestToolMiddleware:
    """Test class for ToolMiddleware."""

    @pytest.fixture
    def tool_middleware(self):
        """Create a ToolMiddleware instance."""
        return ToolMiddleware()

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "Calculate 2 + 2"},
        ]

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_tool_middleware_initialization(self, tool_middleware):
        """Test ToolMiddleware initialization."""
        assert tool_middleware.tool_manager is None

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_should_apply_tools_enabled(self, tool_middleware, sample_messages):
        """Test should_apply_tools when tools are enabled."""
        assert tool_middleware.should_apply_tools(sample_messages, True) is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_should_apply_tools_disabled(self, tool_middleware, sample_messages):
        """Test should_apply_tools when tools are disabled."""
        assert tool_middleware.should_apply_tools(sample_messages, False) is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_process_no_tool_manager(self, tool_middleware, sample_messages):
        """Test process when no tool manager is available."""
        processed_messages = await tool_middleware.process(sample_messages, True)
        assert processed_messages == sample_messages

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_format_tool_prompt(self, tool_middleware):
        """Test formatting tool prompt."""
        tools = [
            ToolInfo(
                name="calculator",
                description="Performs mathematical calculations",
                parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
            ),
            ToolInfo(
                name="weather",
                description="Gets weather information",
                parameters={"type": "object", "properties": {"location": {"type": "string"}}},
            ),
        ]
        prompt = tool_middleware._format_tool_prompt(tools)
        assert "calculator" in prompt
        assert "weather" in prompt
        assert "mathematical calculations" in prompt
        assert "weather information" in prompt

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_format_tool_prompt_empty(self, tool_middleware):
        """Test formatting tool prompt with empty tools."""
        prompt = tool_middleware._format_tool_prompt([])
        assert prompt == ""

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_execute_tools_from_response_no_tool_manager(self, tool_middleware):
        """Test execute_tools_from_response when no tool manager."""
        results = await tool_middleware.execute_tools_from_response(
            "Use calculator to compute 2+2", "user123"
        )
        assert results == []

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_tool_calls_valid(self, tool_middleware):
        """Test extracting valid tool calls."""
        response = """
        I'll help you calculate that.
        
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>
        {"expression": "2 + 2"}
        </parameters>
        </tool_call>
        """
        tool_calls = tool_middleware._extract_tool_calls(response)
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "calculator"
        assert tool_calls[0].parameters == {"expression": "2 + 2"}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_tool_calls_invalid_format(self, tool_middleware):
        """Test extracting tool calls with invalid format."""
        response = "Invalid tool call format"
        tool_calls = tool_middleware._extract_tool_calls(response)
        assert tool_calls == []

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_tool_calls_multiple(self, tool_middleware):
        """Test extracting multiple tool calls."""
        response = """
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>{"expression": "2 + 2"}</parameters>
        </tool_call>
        
        <tool_call>
        <tool_name>weather</tool_name>
        <parameters>{"location": "Berlin"}</parameters>
        </tool_call>
        """
        tool_calls = tool_middleware._extract_tool_calls(response)
        assert len(tool_calls) == 2
        assert tool_calls[0].name == "calculator"
        assert tool_calls[1].name == "weather"

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_extract_tool_calls_missing_parameters(self, tool_middleware):
        """Test extracting tool calls with missing parameters."""
        response = """
        <tool_call>
        <tool_name>calculator</tool_name>
        </tool_call>
        """
        tool_calls = tool_middleware._extract_tool_calls(response)
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "calculator"
        assert tool_calls[0].parameters == {}


class TestCostMiddleware:
    """Test class for CostMiddleware."""

    @pytest.fixture
    def cost_middleware(self):
        """Create a CostMiddleware instance."""
        return CostMiddleware()

    @pytest.fixture
    def sample_cost_info(self):
        """Sample cost information for testing."""
        return {
            "model": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost_usd": 0.03,
            "timestamp": datetime.now(UTC),
            "user_id": "user123",
            "conversation_id": "conv123",
        }

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_cost_middleware_initialization(self, cost_middleware):
        """Test CostMiddleware initialization."""
        assert cost_middleware.cost_tracker is None
        assert cost_middleware._daily_limit == 10.0
        assert cost_middleware._monthly_limit == 100.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_track_cost_no_tracker(self, cost_middleware, sample_cost_info):
        """Test track_cost when no cost tracker is available."""
        result = cost_middleware.track_cost(sample_cost_info)
        assert result is True  # Should not fail when no tracker

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_track_streaming_cost_no_tracker(self, cost_middleware, sample_cost_info):
        """Test track_streaming_cost when no cost tracker is available."""
        result = cost_middleware.track_streaming_cost(sample_cost_info)
        assert result is True  # Should not fail when no tracker

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_estimate_cost_gpt4(self, cost_middleware):
        """Test cost estimation for GPT-4."""
        estimated_cost = cost_middleware.estimate_cost("gpt-4", 100, 50)
        assert isinstance(estimated_cost, float)
        assert estimated_cost > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_estimate_cost_gpt35(self, cost_middleware):
        """Test cost estimation for GPT-3.5."""
        estimated_cost = cost_middleware.estimate_cost("gpt-3.5-turbo", 100, 50)
        assert isinstance(estimated_cost, float)
        assert estimated_cost > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_estimate_cost_unknown_model(self, cost_middleware):
        """Test cost estimation for unknown model."""
        estimated_cost = cost_middleware.estimate_cost("unknown-model", 100, 50)
        assert estimated_cost == 0.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_calculate_token_count(self, cost_middleware):
        """Test token count calculation."""
        text = "Hello world, this is a test message."
        token_count = cost_middleware._calculate_token_count(text)
        assert isinstance(token_count, int)
        assert token_count > 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_calculate_token_count_empty(self, cost_middleware):
        """Test token count calculation for empty text."""
        token_count = cost_middleware._calculate_token_count("")
        assert token_count == 0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_check_cost_limit_daily_under(self, cost_middleware):
        """Test daily cost limit check when under limit."""
        result = cost_middleware.check_cost_limit("user123", 5.0, "daily")
        assert result is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_check_cost_limit_daily_over(self, cost_middleware):
        """Test daily cost limit check when over limit."""
        result = cost_middleware.check_cost_limit("user123", 15.0, "daily")
        assert result is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_check_cost_limit_monthly_under(self, cost_middleware):
        """Test monthly cost limit check when under limit."""
        result = cost_middleware.check_cost_limit("user123", 50.0, "monthly")
        assert result is True

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_check_cost_limit_monthly_over(self, cost_middleware):
        """Test monthly cost limit check when over limit."""
        result = cost_middleware.check_cost_limit("user123", 150.0, "monthly")
        assert result is False

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_summary_no_tracker(self, cost_middleware):
        """Test get_cost_summary when no cost tracker."""
        summary = cost_middleware.get_cost_summary("user123", 30)
        assert summary == {"total_cost": 0.0, "total_tokens": 0}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_daily_costs_no_tracker(self, cost_middleware):
        """Test get_daily_costs when no cost tracker."""
        daily_costs = cost_middleware.get_daily_costs("user123", 7)
        assert daily_costs == []

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_model_usage_stats_no_tracker(self, cost_middleware):
        """Test get_model_usage_stats when no cost tracker."""
        stats = cost_middleware.get_model_usage_stats("user123", 30)
        assert stats == {}

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_get_cost_limits(self, cost_middleware):
        """Test getting cost limits."""
        limits = cost_middleware.get_cost_limits()
        assert "daily_limit" in limits
        assert "monthly_limit" in limits
        assert limits["daily_limit"] == 10.0
        assert limits["monthly_limit"] == 100.0

    @pytest.mark.fast
    @pytest.mark.unit
    @pytest.mark.service
    def test_set_cost_limits(self, cost_middleware):
        """Test setting cost limits."""
        cost_middleware.set_cost_limits(daily_limit=5.0, monthly_limit=50.0)
        limits = cost_middleware.get_cost_limits()
        assert limits["daily_limit"] == 5.0
        assert limits["monthly_limit"] == 50.0