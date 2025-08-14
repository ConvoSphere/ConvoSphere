"""
Agent runner interfaces and adapters.

Provides a unified interface for agent/assistant processing and an adapter
that runs the modular assistant engine as an agent.
"""

from typing import Any


class AgentRunner:
    """Interface for agents to process messages uniformly."""

    async def process_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        message: str,
        model: str | None = None,
        temperature: float | None = None,
        use_tools: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class AssistantAgentAdapter(AgentRunner):
    """Adapter to run the modular assistant engine as an agent."""

    def __init__(self):
        from backend.app.services.assistants.assistant_engine import assistant_engine

        self.engine = assistant_engine

    async def process_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        message: str,
        model: str | None = None,
        temperature: float | None = None,
        use_tools: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = await self.engine.process_message(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            use_tools=use_tools,
            model=model,
            temperature=temperature or 0.7,
            metadata=metadata,
        )
        return {
            "success": result.success,
            "content": result.content,
            "tool_calls": result.tool_calls,
            "metadata": result.metadata,
            "model_used": result.model_used,
            "tokens_used": result.tokens_used,
            "processing_time": result.processing_time,
            "structured_response": getattr(result, "structured_response", None),
        }