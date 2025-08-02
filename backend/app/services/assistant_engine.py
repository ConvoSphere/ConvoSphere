"""
Assistant Engine for processing user messages with hybrid mode support.

This module provides the main assistant engine with hybrid chat/agent mode
capabilities, structured output, and integration with the HybridModeManager.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from backend.app.core.config import get_settings
from backend.app.schemas.hybrid_mode import ConversationMode, StructuredResponse
from backend.app.services.assistants import assistant_engine as modular_assistant_engine


class ProcessingRequest:
    """Request for message processing."""

    def __init__(
        self,
        request_id: str,
        user_id: str,
        conversation_id: str,
        message: str,
        assistant_id: str | None = None,
        use_knowledge_base: bool = True,
        use_tools: bool = True,
        max_context_chunks: int = 5,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
        force_mode: ConversationMode | None = None,
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.message = message
        self.assistant_id = assistant_id
        self.use_knowledge_base = use_knowledge_base
        self.use_tools = use_tools
        self.max_context_chunks = max_context_chunks
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.metadata = metadata or {}
        self.force_mode = force_mode


class ProcessingResult:
    """Result of message processing."""

    def __init__(
        self,
        request_id: str,
        success: bool,
        content: str,
        tool_calls: list[dict[str, Any]],
        metadata: dict[str, Any],
        model_used: str,
        tokens_used: int,
        processing_time: float,
        error_message: str | None = None,
        structured_response: StructuredResponse | None = None,
    ):
        self.request_id = request_id
        self.success = success
        self.content = content
        self.tool_calls = tool_calls
        self.metadata = metadata
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.processing_time = processing_time
        self.error_message = error_message
        self.structured_response = structured_response


class AIResponse:
    """AI response with structured output."""

    def __init__(
        self,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        message_type: str = "text",
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.metadata = metadata or {}
        self.message_type = message_type


class AssistantEngine:
    """
    Main assistant engine for processing user messages with hybrid mode support.
    
    This is a facade that delegates to the modular assistant engine implementation.
    """

    def __init__(self):
        """Initialize the assistant engine."""
        self.engine = modular_assistant_engine
        self.default_model = get_settings().default_ai_model
        self.default_max_tokens = 2048

    async def process_message(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        assistant_id: str | None = None,
        use_knowledge_base: bool = True,
        use_tools: bool = True,
        max_context_chunks: int = 5,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
        force_mode: ConversationMode | None = None,
    ) -> ProcessingResult:
        """
        Process a user message and generate a response with hybrid mode support.

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            message: User message
            assistant_id: Assistant ID (optional)
            use_knowledge_base: Whether to use knowledge base
            use_tools: Whether to use tools
            max_context_chunks: Maximum knowledge chunks to include
            temperature: AI model temperature
            max_tokens: Maximum tokens for response
            model: AI model to use
            metadata: Additional metadata
            force_mode: Force specific conversation mode

        Returns:
            Processing result with structured response
        """
        try:
            # Delegate to modular engine
            result = await self.engine.process_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message,
                assistant_id=assistant_id,
                use_knowledge_base=use_knowledge_base,
                use_tools=use_tools,
                max_context_chunks=max_context_chunks,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
                metadata=metadata,
                force_mode=force_mode,
            )

            # Convert to legacy format for backward compatibility
            return ProcessingResult(
                request_id=result.request_id,
                success=result.success,
                content=result.content,
                tool_calls=result.tool_calls,
                metadata=result.metadata,
                model_used=result.model_used,
                tokens_used=result.tokens_used,
                processing_time=result.processing_time,
                error_message=result.error_message,
                structured_response=result.structured_response,
            )

        except Exception as e:
            logger.error(f"Error in assistant engine: {e}")
            return ProcessingResult(
                request_id=f"error_{datetime.now(UTC).timestamp()}",
                success=False,
                content=f"Entschuldigung, es gab einen Fehler bei der Verarbeitung: {str(e)}",
                tool_calls=[],
                metadata={},
                model_used=self.default_model,
                tokens_used=0,
                processing_time=0.0,
                error_message=str(e),
            )

    def get_processing_status(self, request_id: str) -> dict[str, Any] | None:
        """
        Get processing status for a request.

        Args:
            request_id: Request ID

        Returns:
            dict: Processing status or None if not found
        """
        return self.engine.get_processing_status(request_id)

    def get_stats(self) -> dict[str, Any]:
        """
        Get assistant engine statistics.

        Returns:
            dict: Engine statistics
        """
        return self.engine.get_stats()


# Global assistant engine instance for backward compatibility
assistant_engine = AssistantEngine()
