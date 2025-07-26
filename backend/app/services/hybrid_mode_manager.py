"""
Hybrid Mode Manager Service.

This module provides hybrid chat/agent mode management with structured output,
agent memory, and reasoning capabilities using Pydantic AI framework.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from backend.app.core.exceptions import ConversationError
from backend.app.schemas.hybrid_mode import (
    AgentMemory,
    AgentReasoning,
    ConversationMode,
    HybridModeConfig,
    HybridModeState,
    ModeChangeRequest,
    ModeChangeResponse,
    ModeDecision,
    ModeDecisionReason,
)
from backend.app.services.tool_executor_v2 import enhanced_tool_executor as tool_executor
from loguru import logger
from pydantic import BaseModel


class ComplexityAnalyzer(BaseModel):
    """Analyzes query complexity for mode decisions."""

    def analyze_complexity(self, user_message: str, context: dict[str, Any]) -> float:
        """
        Analyze query complexity and return a score between 0.0 and 1.0.

        Args:
            user_message: User's message
            context: Conversation context

        Returns:
            float: Complexity score (0.0 = simple, 1.0 = complex)
        """
        complexity_factors = {
            "length": self._analyze_length(user_message),
            "keywords": self._analyze_keywords(user_message),
            "context_dependency": self._analyze_context_dependency(context),
            "multi_step": self._analyze_multi_step(user_message),
        }

        # Weighted average of complexity factors
        weights = {
            "length": 0.2,
            "keywords": 0.3,
            "context_dependency": 0.3,
            "multi_step": 0.2,
        }
        complexity_score = sum(
            score * weights[factor] for factor, score in complexity_factors.items()
        )

        return min(1.0, max(0.0, complexity_score))

    def _analyze_length(self, message: str) -> float:
        """Analyze message length complexity."""
        words = len(message.split())
        if words < 10:
            return 0.2
        if words < 30:
            return 0.5
        if words < 60:
            return 0.7
        return 0.9

    def _analyze_keywords(self, message: str) -> float:
        """Analyze keyword complexity."""
        complex_keywords = [
            "analyze",
            "compare",
            "research",
            "investigate",
            "calculate",
            "compute",
            "generate",
            "create",
            "build",
            "develop",
            "implement",
            "optimize",
            "debug",
            "test",
            "validate",
            "verify",
            "synthesize",
            "integrate",
        ]

        message_lower = message.lower()
        complex_count = sum(
            1 for keyword in complex_keywords if keyword in message_lower
        )

        if complex_count == 0:
            return 0.2
        if complex_count == 1:
            return 0.5
        if complex_count == 2:
            return 0.7
        return 0.9

    def _analyze_context_dependency(self, context: dict[str, Any]) -> float:
        """Analyze context dependency complexity."""
        context_size = len(context.get("messages", []))
        if context_size < 3:
            return 0.2
        if context_size < 10:
            return 0.5
        if context_size < 20:
            return 0.7
        return 0.9

    def _analyze_multi_step(self, message: str) -> float:
        """Analyze multi-step task complexity."""
        step_indicators = [
            "first",
            "then",
            "next",
            "finally",
            "after",
            "before",
            "step",
            "phase",
        ]
        message_lower = message.lower()
        step_count = sum(
            1 for indicator in step_indicators if indicator in message_lower
        )

        if step_count == 0:
            return 0.2
        if step_count == 1:
            return 0.5
        if step_count == 2:
            return 0.7
        return 0.9


class AgentMemoryManager(BaseModel):
    """Manages agent memory for context retention."""

    config: HybridModeConfig
    memories: dict[str, list[AgentMemory]] = {}

    def __init__(self, config: HybridModeConfig):
        super().__init__(config=config)
        self.memories = {}

    def add_memory(
        self,
        conversation_id: str,
        user_id: str,
        memory_type: str,
        content: dict[str, Any],
        importance: float = 0.5,
    ) -> AgentMemory:
        """Add a new memory entry."""
        memory = AgentMemory(
            conversation_id=uuid.UUID(conversation_id),
            user_id=uuid.UUID(user_id),
            memory_type=memory_type,
            content=content,
            importance=importance,
            expires_at=datetime.now()
            + timedelta(hours=self.config.memory_retention_hours),
        )

        if conversation_id not in self.memories:
            self.memories[conversation_id] = []

        self.memories[conversation_id].append(memory)

        # Clean up expired memories
        self._cleanup_expired_memories(conversation_id)

        return memory

    def get_relevant_memories(
        self,
        conversation_id: str,
        query: str,
        limit: int = 5,
    ) -> list[AgentMemory]:
        """Get relevant memories for a query."""
        if conversation_id not in self.memories:
            return []

        memories = self.memories[conversation_id]

        # Simple relevance scoring based on keyword matching
        scored_memories = []
        query_words = set(query.lower().split())

        for memory in memories:
            if memory.expires_at and memory.expires_at < datetime.now():
                continue

            memory_text = str(memory.content).lower()
            memory_words = set(memory_text.split())

            # Calculate relevance score
            common_words = query_words.intersection(memory_words)
            relevance_score = (
                len(common_words) / max(len(query_words), 1) * memory.importance
            )

            scored_memories.append((memory, relevance_score))

        # Sort by relevance and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]

    def _cleanup_expired_memories(self, conversation_id: str):
        """Remove expired memories."""
        if conversation_id in self.memories:
            current_time = datetime.now()
            self.memories[conversation_id] = [
                memory
                for memory in self.memories[conversation_id]
                if not memory.expires_at or memory.expires_at > current_time
            ]


class AgentReasoningEngine(BaseModel):
    """Handles agent reasoning and decision making."""

    config: HybridModeConfig

    def __init__(self, config: HybridModeConfig):
        super().__init__(config=config)

    async def generate_reasoning(
        self,
        conversation_id: str,
        user_message: str,
        context: dict[str, Any],
        available_tools: list[str],
    ) -> list[AgentReasoning]:
        """Generate reasoning steps for mode decision."""
        reasoning_steps = []

        # Step 1: Analyze query complexity
        complexity_analyzer = ComplexityAnalyzer()
        complexity_score = complexity_analyzer.analyze_complexity(user_message, context)

        reasoning_steps.append(
            AgentReasoning(
                reasoning_id=uuid.uuid4(),
                conversation_id=uuid.UUID(conversation_id),
                step=1,
                thought=f"Analyzing query complexity. Score: {complexity_score:.2f}",
                confidence=0.8,
                evidence=[f"Message length: {len(user_message.split())} words"],
                conclusion=f"Query complexity is {'high' if complexity_score > 0.7 else 'medium' if complexity_score > 0.4 else 'low'}",
            )
        )

        # Step 2: Check tool availability
        tool_relevance = self._analyze_tool_relevance(user_message, available_tools)

        reasoning_steps.append(
            AgentReasoning(
                reasoning_id=uuid.uuid4(),
                conversation_id=uuid.UUID(conversation_id),
                step=2,
                thought=f"Checking tool relevance. Available tools: {len(available_tools)}",
                confidence=0.9,
                evidence=(
                    [
                        f"Relevant tools: {[tool for tool, score in tool_relevance if score > 0.5]}"
                    ]
                    if tool_relevance
                    else ["No relevant tools found"]
                ),
                conclusion=f"Tool relevance: {'high' if any(score > 0.5 for _, score in tool_relevance) else 'low'}",
            )
        )

        # Step 3: Evaluate context requirements
        context_relevance = self._evaluate_context_relevance(context)

        reasoning_steps.append(
            AgentReasoning(
                reasoning_id=uuid.uuid4(),
                conversation_id=uuid.UUID(conversation_id),
                step=3,
                thought=f"Evaluating context requirements. Context size: {len(context.get('messages', []))}",
                confidence=0.7,
                evidence=[f"Context relevance score: {context_relevance:.2f}"],
                conclusion=f"Context requires agent mode: {'yes' if context_relevance > 0.6 else 'no'}",
            )
        )

        return reasoning_steps[: self.config.reasoning_steps_max]

    def _analyze_tool_relevance(
        self, user_message: str, available_tools: list[str]
    ) -> list[tuple[str, float]]:
        """Analyze which tools are relevant to the user message."""
        tool_relevance = []
        message_lower = user_message.lower()

        for tool in available_tools:
            relevance_score = 0.0

            # Simple keyword matching (in a real implementation, this would use embeddings)
            tool_keywords = tool.lower().split("_")
            for keyword in tool_keywords:
                if keyword in message_lower:
                    relevance_score += 0.3

            if relevance_score > 0:
                tool_relevance.append((tool, min(1.0, relevance_score)))

        return sorted(tool_relevance, key=lambda x: x[1], reverse=True)

    def _evaluate_context_relevance(self, context: dict[str, Any]) -> float:
        """Evaluate how much the context requires agent mode."""
        messages = context.get("messages", [])
        if not messages:
            return 0.0

        # Check for agent-related patterns in recent messages
        recent_messages = messages[-5:]  # Last 5 messages
        agent_indicators = 0

        for message in recent_messages:
            content = message.get("content", "").lower()
            if any(
                indicator in content
                for indicator in ["tool", "execute", "analyze", "research", "calculate"]
            ):
                agent_indicators += 1

        return min(1.0, agent_indicators / len(recent_messages))


class HybridModeManager:
    """Manages hybrid chat/agent mode switching with structured output and reasoning."""

    def __init__(self):
        self.active_states: dict[str, HybridModeState] = {}
        self.complexity_analyzer = ComplexityAnalyzer()
        self.default_config = HybridModeConfig()

    def initialize_conversation(
        self,
        conversation_id: str,
        user_id: str,
        initial_mode: ConversationMode = ConversationMode.AUTO,
        config: HybridModeConfig | None = None,
    ) -> HybridModeState:
        """Initialize hybrid mode for a conversation."""
        if config is None:
            config = self.default_config

        state = HybridModeState(
            conversation_id=uuid.UUID(conversation_id),
            user_id=uuid.UUID(user_id),
            current_mode=initial_mode,
            last_mode_change=datetime.now(),
            config=config,
        )

        self.active_states[conversation_id] = state
        logger.info(
            f"Initialized hybrid mode for conversation {conversation_id} with mode {initial_mode}"
        )

        return state

    async def decide_mode(
        self,
        conversation_id: str,
        user_message: str,
        context: dict[str, Any],
        force_mode: ConversationMode | None = None,
    ) -> ModeDecision:
        """Decide the appropriate mode for the next response."""
        state = self.active_states.get(conversation_id)
        if not state:
            raise ConversationError(
                f"Conversation {conversation_id} not initialized for hybrid mode"
            )

        # If force mode is specified, use it
        if force_mode:
            return ModeDecision(
                conversation_id=state.conversation_id,
                user_message=user_message,
                current_mode=state.current_mode,
                recommended_mode=force_mode,
                reason=ModeDecisionReason.USER_REQUEST,
                confidence=1.0,
                complexity_score=0.0,
                available_tools=[],
                context_relevance=0.0,
            )

        # Get available tools
        available_tools = tool_executor.get_available_tools()
        tool_names = [tool.get("name", "") for tool in available_tools]

        # Analyze complexity
        complexity_score = self.complexity_analyzer.analyze_complexity(
            user_message, context
        )

        # Generate reasoning
        reasoning_engine = AgentReasoningEngine(state.config)
        reasoning_steps = await reasoning_engine.generate_reasoning(
            conversation_id, user_message, context, tool_names
        )

        # Determine recommended mode
        recommended_mode = self._determine_recommended_mode(
            state, complexity_score, reasoning_steps, tool_names, context
        )

        # Create mode decision
        return ModeDecision(
            conversation_id=state.conversation_id,
            user_message=user_message,
            current_mode=state.current_mode,
            recommended_mode=recommended_mode,
            reason=self._determine_reason(
                recommended_mode, complexity_score, reasoning_steps
            ),
            confidence=self._calculate_confidence(reasoning_steps),
            complexity_score=complexity_score,
            available_tools=tool_names,
            context_relevance=self._calculate_context_relevance(context),
            reasoning_steps=reasoning_steps,
        )


    def _determine_recommended_mode(
        self,
        state: HybridModeState,
        complexity_score: float,
        reasoning_steps: list[AgentReasoning],
        available_tools: list[str],
        context: dict[str, Any],
    ) -> ConversationMode:
        """Determine the recommended mode based on analysis."""
        config = state.config

        # If auto mode is disabled, stay in current mode
        if not config.auto_mode_enabled:
            return state.current_mode

        # Check if complexity requires agent mode
        if complexity_score > config.complexity_threshold:
            return ConversationMode.AGENT

        # Check if tools are available and relevant
        if available_tools and any(
            "tool" in step.conclusion.lower() for step in reasoning_steps
        ):
            return ConversationMode.AGENT

        # Check context requirements
        if self._calculate_context_relevance(context) > 0.6:
            return ConversationMode.AGENT

        # Default to chat mode for simple queries
        return ConversationMode.CHAT

    def _determine_reason(
        self,
        recommended_mode: ConversationMode,
        complexity_score: float,
        reasoning_steps: list[AgentReasoning],
    ) -> ModeDecisionReason:
        """Determine the reason for the mode decision."""
        if recommended_mode == ConversationMode.AGENT:
            if complexity_score > 0.7:
                return ModeDecisionReason.COMPLEXITY_HIGH
            if any("tool" in step.conclusion.lower() for step in reasoning_steps):
                return ModeDecisionReason.TOOLS_AVAILABLE
            return ModeDecisionReason.CONTEXT_REQUIRES_AGENT
        if complexity_score < 0.3:
            return ModeDecisionReason.SIMPLE_QUERY
        return ModeDecisionReason.CONTINUATION

    def _calculate_confidence(self, reasoning_steps: list[AgentReasoning]) -> float:
        """Calculate confidence in the mode decision."""
        if not reasoning_steps:
            return 0.5

        # Average confidence of reasoning steps
        total_confidence = sum(step.confidence for step in reasoning_steps)
        return total_confidence / len(reasoning_steps)

    def _calculate_context_relevance(self, context: dict[str, Any]) -> float:
        """Calculate context relevance score."""
        messages = context.get("messages", [])
        if not messages:
            return 0.0

        # Simple heuristic: more messages = higher context relevance
        return min(1.0, len(messages) / 20.0)

    async def change_mode(
        self,
        request: ModeChangeRequest,
    ) -> ModeChangeResponse:
        """Change the mode for a conversation."""
        state = self.active_states.get(str(request.conversation_id))
        if not state:
            raise ConversationError(f"Conversation {request.conversation_id} not found")

        previous_mode = state.current_mode
        new_mode = request.target_mode

        # Update state
        state.current_mode = new_mode
        state.last_mode_change = datetime.now()
        state.updated_at = datetime.now()

        # Add to history
        history_entry = {
            "from_mode": previous_mode.value,
            "to_mode": new_mode.value,
            "reason": request.reason or "User request",
            "timestamp": datetime.now().isoformat(),
        }
        state.mode_history.append(history_entry)

        logger.info(
            f"Changed mode for conversation {request.conversation_id}: {previous_mode} -> {new_mode}"
        )

        return ModeChangeResponse(
            success=True,
            previous_mode=previous_mode,
            new_mode=new_mode,
            reason=request.reason or "Mode changed by user",
        )

    def get_state(self, conversation_id: str) -> HybridModeState | None:
        """Get the current state for a conversation."""
        return self.active_states.get(conversation_id)

    def cleanup_conversation(self, conversation_id: str):
        """Clean up state for a conversation."""
        if conversation_id in self.active_states:
            del self.active_states[conversation_id]
            logger.info(
                f"Cleaned up hybrid mode state for conversation {conversation_id}"
            )

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about hybrid mode usage."""
        total_conversations = len(self.active_states)
        mode_counts = {}

        for state in self.active_states.values():
            mode = state.current_mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        return {
            "total_conversations": total_conversations,
            "mode_distribution": mode_counts,
            "active_since": (
                min(state.created_at for state in self.active_states.values())
                if self.active_states
                else None
            ),
        }


# Global hybrid mode manager instance
hybrid_mode_manager = HybridModeManager()
