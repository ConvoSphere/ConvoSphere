"""
Integration tests for AI Service Middleware Pipeline.

This module tests the integration between different middleware components:
- RAGMiddleware + ToolMiddleware + CostMiddleware
- Complete request processing pipeline
- Error handling across middleware
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from backend.app.services.ai.middleware import RAGMiddleware, ToolMiddleware, CostMiddleware
from backend.app.services.ai.types.ai_types import (
    ChatRequest,
    ChatResponse,
    RAGContext,
    ToolInfo,
    ToolCall,
)


class TestMiddlewarePipelineIntegration:
    """Test class for middleware pipeline integration."""

    @pytest.fixture
    def rag_middleware(self):
        """Create a RAGMiddleware instance."""
        return RAGMiddleware()

    @pytest.fixture
    def tool_middleware(self):
        """Create a ToolMiddleware instance."""
        return ToolMiddleware()

    @pytest.fixture
    def cost_middleware(self):
        """Create a CostMiddleware instance."""
        return CostMiddleware()

    @pytest.fixture
    def sample_messages(self):
        """Sample chat messages for testing."""
        return [
            {"role": "user", "content": "What is the weather in Berlin and calculate 2+2?"},
        ]

    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        mock_service = MagicMock()
        mock_service.search.return_value = [
            {"content": "Berlin weather: Sunny, 22°C", "metadata": {"source": "weather_api"}},
        ]
        return mock_service

    @pytest.fixture
    def mock_tool_manager(self):
        """Mock tool manager."""
        mock_manager = MagicMock()
        mock_manager.get_available_tools.return_value = [
            ToolInfo(
                name="calculator",
                description="Performs mathematical calculations",
                parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
                is_available=True,
            ),
            ToolInfo(
                name="weather",
                description="Gets weather information",
                parameters={"type": "object", "properties": {"location": {"type": "string"}}},
                is_available=True,
            ),
        ]
        mock_manager.execute_tool.return_value = {"result": "4"}
        return mock_manager

    @pytest.fixture
    def mock_cost_tracker(self):
        """Mock cost tracker."""
        mock_tracker = MagicMock()
        mock_tracker.add_cost.return_value = True
        mock_tracker.get_total_cost.return_value = 0.05
        return mock_tracker

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_complete_pipeline_with_all_middleware(
        self, rag_middleware, tool_middleware, cost_middleware, 
        sample_messages, mock_rag_service, mock_tool_manager, mock_cost_tracker
    ):
        """Test complete pipeline with all middleware components."""
        # Setup middleware with mocked services
        rag_middleware.rag_service = mock_rag_service
        tool_middleware.tool_manager = mock_tool_manager
        cost_middleware.cost_tracker = mock_cost_tracker

        # Process with RAG middleware
        rag_processed = await rag_middleware.process(sample_messages, "user123", 5)
        assert len(rag_processed) > len(sample_messages)
        assert any("Berlin weather" in msg.get("content", "") for msg in rag_processed)

        # Process with Tool middleware
        tool_processed = await tool_middleware.process(rag_processed, True)
        assert len(tool_processed) > len(rag_processed)
        assert any("calculator" in msg.get("content", "") for msg in tool_processed)

        # Track cost
        cost_info = {
            "model": "gpt-4",
            "tokens_used": 150,
            "cost_usd": 0.03,
            "timestamp": datetime.now(UTC),
            "user_id": "user123",
            "conversation_id": "conv123",
        }
        cost_result = cost_middleware.track_cost(cost_info)
        assert cost_result is True

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_rag_only(
        self, rag_middleware, tool_middleware, cost_middleware, 
        sample_messages, mock_rag_service
    ):
        """Test pipeline with RAG middleware only."""
        # Setup RAG middleware only
        rag_middleware.rag_service = mock_rag_service

        # Process with RAG middleware
        rag_processed = await rag_middleware.process(sample_messages, "user123", 5)
        assert len(rag_processed) > len(sample_messages)

        # Process with Tool middleware (should not add tools)
        tool_processed = await tool_middleware.process(rag_processed, False)
        assert tool_processed == rag_processed

        # Process with Cost middleware (should not fail)
        cost_info = {
            "model": "gpt-4",
            "tokens_used": 100,
            "cost_usd": 0.02,
            "timestamp": datetime.now(UTC),
            "user_id": "user123",
            "conversation_id": "conv123",
        }
        cost_result = cost_middleware.track_cost(cost_info)
        assert cost_result is True

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_tools_only(
        self, rag_middleware, tool_middleware, cost_middleware, 
        sample_messages, mock_tool_manager
    ):
        """Test pipeline with Tool middleware only."""
        # Setup Tool middleware only
        tool_middleware.tool_manager = mock_tool_manager

        # Process with RAG middleware (should not add context)
        rag_processed = await rag_middleware.process(sample_messages, "user123", 5)
        assert rag_processed == sample_messages

        # Process with Tool middleware
        tool_processed = await tool_middleware.process(rag_processed, True)
        assert len(tool_processed) > len(rag_processed)
        assert any("calculator" in msg.get("content", "") for msg in tool_processed)

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(
        self, rag_middleware, tool_middleware, cost_middleware, sample_messages
    ):
        """Test pipeline error handling."""
        # Test with no services configured (should not fail)
        rag_processed = await rag_middleware.process(sample_messages, "user123", 5)
        assert rag_processed == sample_messages

        tool_processed = await tool_middleware.process(rag_processed, True)
        assert tool_processed == rag_processed

        cost_result = cost_middleware.track_cost({})
        assert cost_result is True

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_cost_limits(
        self, rag_middleware, tool_middleware, cost_middleware, 
        sample_messages, mock_cost_tracker
    ):
        """Test pipeline with cost limits."""
        # Setup cost middleware
        cost_middleware.cost_tracker = mock_cost_tracker
        cost_middleware.set_cost_limits(daily_limit=0.01, monthly_limit=0.10)

        # Test under limit
        under_limit = cost_middleware.check_cost_limit("user123", 0.005, "daily")
        assert under_limit is True

        # Test over limit
        over_limit = cost_middleware.check_cost_limit("user123", 0.02, "daily")
        assert over_limit is False

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_tool_execution(
        self, tool_middleware, mock_tool_manager
    ):
        """Test pipeline with tool execution."""
        tool_middleware.tool_manager = mock_tool_manager

        # Test tool execution from response
        ai_response = """
        I'll help you calculate that.
        
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>
        {"expression": "2 + 2"}
        </parameters>
        </tool_call>
        """
        
        results = await tool_middleware.execute_tools_from_response(ai_response, "user123")
        assert len(results) == 1
        assert results[0]["result"] == "4"

    @pytest.mark.integration
    @pytest.mark.service
    def test_pipeline_cost_estimation(
        self, cost_middleware
    ):
        """Test pipeline cost estimation."""
        # Test cost estimation for different models
        gpt4_cost = cost_middleware.estimate_cost("gpt-4", 100, 50)
        gpt35_cost = cost_middleware.estimate_cost("gpt-3.5-turbo", 100, 50)
        
        assert gpt4_cost > 0
        assert gpt35_cost > 0
        assert gpt4_cost > gpt35_cost  # GPT-4 should be more expensive

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_large_context(
        self, rag_middleware, sample_messages, mock_rag_service
    ):
        """Test pipeline with large context."""
        # Mock large RAG response
        large_chunks = [
            {"content": f"Large chunk {i}", "metadata": {"source": f"doc{i}"}}
            for i in range(20)
        ]
        mock_rag_service.search.return_value = large_chunks
        
        rag_middleware.rag_service = mock_rag_service

        # Process with limited chunks
        processed = await rag_middleware.process(sample_messages, "user123", max_context_chunks=5)
        
        # Should limit to 5 chunks
        context_messages = [msg for msg in processed if "Context:" in msg.get("content", "")]
        assert len(context_messages) == 1
        
        context_content = context_messages[0]["content"]
        chunk_count = context_content.count("Large chunk")
        assert chunk_count <= 5

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_multiple_tool_calls(
        self, tool_middleware, mock_tool_manager
    ):
        """Test pipeline with multiple tool calls."""
        tool_middleware.tool_manager = mock_tool_manager

        # Test multiple tool calls
        ai_response = """
        I'll help you with both calculations.
        
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>{"expression": "2 + 2"}</parameters>
        </tool_call>
        
        <tool_call>
        <tool_name>calculator</tool_name>
        <parameters>{"expression": "5 * 3"}</parameters>
        </tool_call>
        """
        
        results = await tool_middleware.execute_tools_from_response(ai_response, "user123")
        assert len(results) == 2
        assert all("result" in result for result in results)

    @pytest.mark.integration
    @pytest.mark.service
    def test_pipeline_cost_summary(
        self, cost_middleware, mock_cost_tracker
    ):
        """Test pipeline cost summary."""
        cost_middleware.cost_tracker = mock_cost_tracker
        
        # Mock cost summary
        mock_cost_tracker.get_cost_summary.return_value = {
            "total_cost": 0.15,
            "total_tokens": 500,
            "daily_cost": 0.05,
            "monthly_cost": 0.15,
        }
        
        summary = cost_middleware.get_cost_summary("user123", 30)
        assert summary["total_cost"] == 0.15
        assert summary["total_tokens"] == 500

    @pytest.mark.integration
    @pytest.mark.service
    @pytest.mark.asyncio
    async def test_pipeline_with_streaming_cost(
        self, cost_middleware, mock_cost_tracker
    ):
        """Test pipeline with streaming cost tracking."""
        cost_middleware.cost_tracker = mock_cost_tracker
        
        # Test streaming cost tracking
        cost_info = {
            "model": "gpt-4",
            "tokens_used": 200,
            "cost_usd": 0.06,
            "timestamp": datetime.now(UTC),
            "user_id": "user123",
            "conversation_id": "conv123",
        }
        
        result = cost_middleware.track_streaming_cost(cost_info)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.service
    def test_pipeline_model_usage_stats(
        self, cost_middleware, mock_cost_tracker
    ):
        """Test pipeline model usage statistics."""
        cost_middleware.cost_tracker = mock_cost_tracker
        
        # Mock usage stats
        mock_cost_tracker.get_model_usage_stats.return_value = {
            "gpt-4": {
                "total_requests": 50,
                "total_tokens": 2500,
                "total_cost": 0.075,
                "avg_tokens_per_request": 50,
            },
            "gpt-3.5-turbo": {
                "total_requests": 100,
                "total_tokens": 3000,
                "total_cost": 0.045,
                "avg_tokens_per_request": 30,
            },
        }
        
        stats = cost_middleware.get_model_usage_stats("user123", 30)
        assert "gpt-4" in stats
        assert "gpt-3.5-turbo" in stats
        assert stats["gpt-4"]["total_requests"] == 50
        assert stats["gpt-3.5-turbo"]["total_requests"] == 100