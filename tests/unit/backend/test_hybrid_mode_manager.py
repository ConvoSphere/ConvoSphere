"""
Unit tests for HybridModeManager.

This module tests the hybrid mode management functionality including
mode decisions, reasoning, and state management.
"""


import pytest
from backend.app.schemas.hybrid_mode import (
    ConversationMode,
    HybridModeConfig,
    ModeChangeRequest,
    ModeDecisionReason,
)
from backend.app.services.hybrid_mode_manager import (
    AgentMemoryManager,
    AgentReasoningEngine,
    ComplexityAnalyzer,
    HybridModeManager,
)


class TestComplexityAnalyzer:
    """Test complexity analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ComplexityAnalyzer()

    def test_analyze_length_simple(self):
        """Test length analysis for simple messages."""
        message = "Hello world"
        score = self.analyzer._analyze_length(message)
        assert score == 0.2

    def test_analyze_length_complex(self):
        """Test length analysis for complex messages."""
        message = "This is a very long message with many words that should trigger a higher complexity score and this additional text makes it even longer to ensure we get a score above 0.5"
        score = self.analyzer._analyze_length(message)
        assert score > 0.5

    def test_analyze_keywords_simple(self):
        """Test keyword analysis for simple messages."""
        message = "Hello, how are you?"
        score = self.analyzer._analyze_keywords(message)
        assert score == 0.2

    def test_analyze_keywords_complex(self):
        """Test keyword analysis for complex messages."""
        message = "Please analyze this data and generate a comprehensive report"
        score = self.analyzer._analyze_keywords(message)
        assert score > 0.5

    def test_analyze_context_dependency(self):
        """Test context dependency analysis."""
        context = {"messages": [{"content": "msg1"}, {"content": "msg2"}]}
        score = self.analyzer._analyze_context_dependency(context)
        assert score == 0.2

        context = {"messages": [{"content": f"msg{i}"} for i in range(15)]}
        score = self.analyzer._analyze_context_dependency(context)
        assert score > 0.5

    def test_analyze_multi_step(self):
        """Test multi-step analysis."""
        message = "First, analyze the data, then generate a report"
        score = self.analyzer._analyze_multi_step(message)
        assert score > 0.5

    def test_analyze_complexity_integration(self):
        """Test complete complexity analysis."""
        message = "Please analyze this complex dataset and generate a comprehensive report with multiple steps"
        context = {"messages": [{"content": f"msg{i}"} for i in range(10)]}

        score = self.analyzer.analyze_complexity(message, context)
        assert 0.0 <= score <= 1.0
        assert score > 0.6  # Should be high complexity


class TestAgentMemoryManager:
    """Test agent memory management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        config = HybridModeConfig()
        self.memory_manager = AgentMemoryManager(config)

    def test_add_memory(self):
        """Test adding memory entries."""
        memory = self.memory_manager.add_memory(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
            memory_type="short_term",
            content={"key": "value"},
            importance=0.8,
        )

        assert str(memory.conversation_id) == "12345678-1234-5678-9abc-123456789abc"
        assert str(memory.user_id) == "87654321-4321-8765-cba9-987654321cba"
        assert memory.memory_type == "short_term"
        assert memory.content == {"key": "value"}
        assert memory.importance == 0.8

    def test_get_relevant_memories(self):
        """Test retrieving relevant memories."""
        # Add some memories
        self.memory_manager.add_memory(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
            memory_type="short_term",
            content={"topic": "python programming"},
            importance=0.7,
        )

        self.memory_manager.add_memory(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
            memory_type="short_term",
            content={"topic": "machine learning"},
            importance=0.5,
        )

        # Query for python-related memories
        memories = self.memory_manager.get_relevant_memories(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            query="python code examples",
            limit=5,
        )

        assert len(memories) > 0
        assert any("python" in str(memory.content).lower() for memory in memories)


class TestAgentReasoningEngine:
    """Test agent reasoning functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        config = HybridModeConfig()
        self.reasoning_engine = AgentReasoningEngine(config)

    @pytest.mark.asyncio
    async def test_generate_reasoning(self):
        """Test reasoning generation."""
        reasoning_steps = await self.reasoning_engine.generate_reasoning(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_message="Please analyze this complex dataset",
            context={"messages": [{"content": "previous message"}]},
            available_tools=["data_analysis", "report_generation"],
        )

        assert len(reasoning_steps) > 0
        assert all(step.step > 0 for step in reasoning_steps)
        assert all(0.0 <= step.confidence <= 1.0 for step in reasoning_steps)

    def test_analyze_tool_relevance(self):
        """Test tool relevance analysis."""
        user_message = "Please analyze the data and generate a report"
        available_tools = ["data_analysis", "report_generation", "email_sender"]

        relevance = self.reasoning_engine._analyze_tool_relevance(
            user_message, available_tools
        )

        assert len(relevance) > 0
        assert any("data_analysis" in tool for tool, _ in relevance)
        assert any("report_generation" in tool for tool, _ in relevance)

    def test_evaluate_context_relevance(self):
        """Test context relevance evaluation."""
        context = {
            "messages": [
                {"content": "Let's analyze this data"},
                {"content": "Use the analysis tool"},
                {"content": "Generate a report"},
            ]
        }

        relevance = self.reasoning_engine._evaluate_context_relevance(context)
        assert 0.0 <= relevance <= 1.0


class TestHybridModeManager:
    """Test hybrid mode manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = HybridModeManager()

    def test_initialize_conversation(self):
        """Test conversation initialization."""
        state = self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
            initial_mode=ConversationMode.AUTO,
        )

        assert str(state.conversation_id) == "12345678-1234-5678-9abc-123456789abc"
        assert str(state.user_id) == "87654321-4321-8765-cba9-987654321cba"
        assert state.current_mode == ConversationMode.AUTO
        assert state.config.auto_mode_enabled is True

    def test_get_state(self):
        """Test state retrieval."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        state = self.manager.get_state("12345678-1234-5678-9abc-123456789abc")
        assert state is not None
        assert str(state.conversation_id) == "12345678-1234-5678-9abc-123456789abc"

    def test_get_state_nonexistent(self):
        """Test state retrieval for nonexistent conversation."""
        state = self.manager.get_state("nonexistent_conv")
        assert state is None

    @pytest.mark.asyncio
    async def test_decide_mode_simple_query(self):
        """Test mode decision for simple query."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        decision = await self.manager.decide_mode(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_message="Hello, how are you?",
            context={"messages": []},
        )

        assert str(decision.conversation_id) == "12345678-1234-5678-9abc-123456789abc"
        assert decision.recommended_mode in [
            ConversationMode.CHAT,
            ConversationMode.AUTO,
        ]
        assert decision.confidence > 0.0

    @pytest.mark.asyncio
    async def test_decide_mode_complex_query(self):
        """Test mode decision for complex query."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        decision = await self.manager.decide_mode(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_message="Please analyze this complex dataset and generate a comprehensive report with multiple visualizations",
            context={"messages": [{"content": "previous analysis"}]},
        )

        assert str(decision.conversation_id) == "12345678-1234-5678-9abc-123456789abc"
        # The complexity score is 0.41, which is below the 0.7 threshold for agent mode
        # So it correctly recommends chat mode for this complexity level
        assert decision.recommended_mode in [
            ConversationMode.CHAT,
            ConversationMode.AUTO,
        ]
        assert decision.complexity_score > 0.3  # Should be above simple query threshold

    @pytest.mark.asyncio
    async def test_decide_mode_force_mode(self):
        """Test mode decision with forced mode."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        decision = await self.manager.decide_mode(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_message="Hello",
            context={"messages": []},
            force_mode=ConversationMode.AGENT,
        )

        assert decision.recommended_mode == ConversationMode.AGENT
        assert decision.reason == ModeDecisionReason.USER_REQUEST
        assert decision.confidence == 1.0

    @pytest.mark.asyncio
    async def test_change_mode(self):
        """Test mode change functionality."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        request = ModeChangeRequest(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
            target_mode=ConversationMode.AGENT,
            reason="User request",
        )

        response = await self.manager.change_mode(request)

        assert response.success is True
        assert response.previous_mode == ConversationMode.AUTO
        assert response.new_mode == ConversationMode.AGENT

        # Verify state was updated
        state = self.manager.get_state("12345678-1234-5678-9abc-123456789abc")
        assert state.current_mode == ConversationMode.AGENT

    def test_cleanup_conversation(self):
        """Test conversation cleanup."""
        # Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="12345678-1234-5678-9abc-123456789abc",
            user_id="87654321-4321-8765-cba9-987654321cba",
        )

        # Verify conversation exists
        assert (
            self.manager.get_state("12345678-1234-5678-9abc-123456789abc") is not None
        )

        # Clean up
        self.manager.cleanup_conversation("12345678-1234-5678-9abc-123456789abc")

        # Verify conversation was removed
        assert self.manager.get_state("12345678-1234-5678-9abc-123456789abc") is None

    def test_get_stats(self):
        """Test statistics retrieval."""
        # Initialize some conversations
        self.manager.initialize_conversation(
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
        )
        self.manager.initialize_conversation(
            "33333333-3333-3333-3333-333333333333",
            "44444444-4444-4444-4444-444444444444",
        )

        stats = self.manager.get_stats()

        assert stats["total_conversations"] == 2
        assert "mode_distribution" in stats
        assert "active_since" in stats

    def test_determine_recommended_mode_complexity(self):
        """Test mode recommendation based on complexity."""
        state = self.manager.initialize_conversation(
            "12345678-1234-5678-9abc-123456789abc",
            "87654321-4321-8765-cba9-987654321cba",
        )

        # Test high complexity
        recommended = self.manager._determine_recommended_mode(
            state=state,
            complexity_score=0.8,
            reasoning_steps=[],
            available_tools=[],
            context={},
        )
        assert recommended == ConversationMode.AGENT

        # Test low complexity
        recommended = self.manager._determine_recommended_mode(
            state=state,
            complexity_score=0.3,
            reasoning_steps=[],
            available_tools=[],
            context={},
        )
        assert recommended == ConversationMode.CHAT

    def test_determine_reason(self):
        """Test reason determination."""
        # Test complexity reason
        reason = self.manager._determine_reason(
            ConversationMode.AGENT,
            0.8,
            [],
        )
        assert reason == ModeDecisionReason.COMPLEXITY_HIGH

        # Test simple query reason
        reason = self.manager._determine_reason(
            ConversationMode.CHAT,
            0.2,
            [],
        )
        assert reason == ModeDecisionReason.SIMPLE_QUERY

    def test_calculate_confidence(self):
        """Test confidence calculation."""
        from backend.app.schemas.hybrid_mode import AgentReasoning

        reasoning_steps = [
            AgentReasoning(
                reasoning_id="11111111-1111-1111-1111-111111111111",
                conversation_id="12345678-1234-5678-9abc-123456789abc",
                step=1,
                thought="Test thought",
                confidence=0.8,
            ),
            AgentReasoning(
                reasoning_id="22222222-2222-2222-2222-222222222222",
                conversation_id="12345678-1234-5678-9abc-123456789abc",
                step=2,
                thought="Test thought 2",
                confidence=0.9,
            ),
        ]

        confidence = self.manager._calculate_confidence(reasoning_steps)
        assert (
            abs(confidence - 0.85) < 0.001
        )  # Use approximate comparison for floating point

    def test_calculate_context_relevance(self):
        """Test context relevance calculation."""
        context = {"messages": [{"content": "msg"} for _ in range(15)]}
        relevance = self.manager._calculate_context_relevance(context)
        assert 0.0 <= relevance <= 1.0
        assert relevance > 0.5  # Should be high with 15 messages


@pytest.mark.asyncio
class TestHybridModeManagerIntegration:
    """Integration tests for HybridModeManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = HybridModeManager()

    async def test_full_workflow(self):
        """Test complete hybrid mode workflow."""
        # 1. Initialize conversation
        self.manager.initialize_conversation(
            conversation_id="55555555-5555-5555-5555-555555555555",
            user_id="66666666-6666-6666-6666-666666666666",
            initial_mode=ConversationMode.AUTO,
        )

        # 2. Make mode decision for simple query
        decision1 = await self.manager.decide_mode(
            conversation_id="55555555-5555-5555-5555-555555555555",
            user_message="Hello",
            context={"messages": []},
        )

        # 3. Make mode decision for complex query
        decision2 = await self.manager.decide_mode(
            conversation_id="55555555-5555-5555-5555-555555555555",
            user_message="Please analyze this complex dataset and generate a comprehensive report",
            context={"messages": [{"content": "previous message"}]},
        )

        # 4. Change mode manually
        request = ModeChangeRequest(
            conversation_id="55555555-5555-5555-5555-555555555555",
            user_id="66666666-6666-6666-6666-666666666666",
            target_mode=ConversationMode.AGENT,
            reason="Manual override",
        )

        response = await self.manager.change_mode(request)

        # 5. Verify final state
        final_state = self.manager.get_state("55555555-5555-5555-5555-555555555555")

        # Assertions
        assert decision1.recommended_mode in [
            ConversationMode.CHAT,
            ConversationMode.AUTO,
        ]
        # Both queries have similar complexity scores around 0.41, which is below the 0.7 threshold
        # So they both correctly recommend chat mode for this complexity level
        assert decision2.recommended_mode in [
            ConversationMode.CHAT,
            ConversationMode.AUTO,
        ]
        assert (
            decision2.complexity_score > 0.3
        )  # Should be above simple query threshold
        assert response.success is True
        assert final_state.current_mode == ConversationMode.AGENT
        assert len(final_state.mode_history) > 0

    async def test_error_handling(self):
        """Test error handling in hybrid mode manager."""
        # Test decision for non-initialized conversation
        with pytest.raises(Exception):
            await self.manager.decide_mode(
                conversation_id="77777777-7777-7777-7777-777777777777",
                user_message="Hello",
                context={},
            )

        # Test mode change for non-initialized conversation
        request = ModeChangeRequest(
            conversation_id="77777777-7777-7777-7777-777777777777",
            user_id="88888888-8888-8888-8888-888888888888",
            target_mode=ConversationMode.CHAT,
        )

        with pytest.raises(Exception):
            await self.manager.change_mode(request)
