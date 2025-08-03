"""
Assistant Engine Service.

This module provides the main assistant engine for processing user messages
with hybrid mode support, extracted from the original AssistantEngine for better modularity.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from backend.app.core.config import get_settings
from backend.app.schemas.hybrid_mode import (
    ConversationMode,
    StructuredResponse,
)

from .assistant_context import AssistantContextManager
from .assistant_memory import AssistantMemoryManager
from .assistant_processor import AssistantProcessor
from .assistant_response import AssistantResponseGenerator
from .assistant_tools import AssistantToolsManager


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


class AssistantEngine:
    """Main assistant engine for processing user messages with hybrid mode support."""

    def __init__(self):
        """Initialize the assistant engine."""
        self.processing_requests: dict[str, ProcessingRequest] = {}
        self.processing_results: dict[str, ProcessingResult] = {}
        self.max_concurrent_requests = 5
        self.default_model = get_settings().default_ai_model
        self.default_max_tokens = 2048

        # Processing semaphore to limit concurrent requests
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        # Initialize modular services
        self.processor = AssistantProcessor()
        self.context_manager = AssistantContextManager()
        self.response_generator = AssistantResponseGenerator()
        self.tools_manager = AssistantToolsManager()
        self.memory_manager = AssistantMemoryManager()

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
        # Create processing request
        request_id = (
            f"req_{len(self.processing_requests)}_{datetime.now(UTC).timestamp()}"
        )

        request = ProcessingRequest(
            request_id=request_id,
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

        self.processing_requests[request_id] = request

        try:
            async with self.processing_semaphore:
                return await self._process_request(request)
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            return ProcessingResult(
                request_id=request_id,
                success=False,
                content=f"Entschuldigung, es gab einen Fehler bei der Verarbeitung: {str(e)}",
                tool_calls=[],
                metadata={},
                model_used="",
                tokens_used=0,
                processing_time=0.0,
                error_message=str(e),
            )
        finally:
            # Clean up request
            if request_id in self.processing_requests:
                del self.processing_requests[request_id]

    async def _process_request(self, request: ProcessingRequest) -> ProcessingResult:
        """Process a single request with hybrid mode support."""
        start_time = datetime.now(UTC)

        try:
            # Get conversation context
            context = await self.context_manager.get_conversation_context(request)

            # Prepare knowledge context
            knowledge_context = ""
            if request.use_knowledge_base:
                knowledge_context = (
                    await self.context_manager.prepare_knowledge_context(request)
                )

            # Prepare tools
            tools = []
            if request.use_tools:
                tools = await self.tools_manager.prepare_tools(request.message)

            # Generate response
            ai_response = await self.response_generator.generate_response(
                request, context, knowledge_context, tools
            )

            # Execute tools if needed
            if ai_response.tool_calls:
                tool_results = await self.tools_manager.execute_tools(
                    ai_response.tool_calls
                )
                # Update response with tool results
                ai_response.metadata = ai_response.metadata or {}
                ai_response.metadata["tool_results"] = tool_results

            # Update memory
            await self.memory_manager.update_memory(request, ai_response)

            # Save response to conversation
            structured_response = (
                await self.response_generator.create_structured_response(
                    request, ai_response
                )
            )
            await self.context_manager.save_response_to_conversation(
                request, structured_response
            )

            end_time = datetime.now(UTC)
            processing_time = (end_time - start_time).total_seconds()

            # Create processing result
            result = ProcessingResult(
                request_id=request.request_id,
                success=True,
                content=ai_response.content,
                tool_calls=ai_response.tool_calls or [],
                metadata=ai_response.metadata or {},
                model_used=ai_response.metadata.get("model_used", self.default_model),
                tokens_used=ai_response.metadata.get("tokens_used", 0),
                processing_time=processing_time,
                structured_response=structured_response,
            )

            self.processing_results[request.request_id] = result
            return result

        except Exception as e:
            logger.error(f"Error in request processing: {e}")
            end_time = datetime.now(UTC)
            processing_time = (end_time - start_time).total_seconds()

            return ProcessingResult(
                request_id=request.request_id,
                success=False,
                content=f"Fehler bei der Verarbeitung: {str(e)}",
                tool_calls=[],
                metadata={},
                model_used=self.default_model,
                tokens_used=0,
                processing_time=processing_time,
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
        request = self.processing_requests.get(request_id)
        result = self.processing_results.get(request_id)

        if not request:
            return None

        return {
            "request_id": request_id,
            "status": "completed" if result else "processing",
            "request": {
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "message": request.message[:100] + "..."
                if len(request.message) > 100
                else request.message,
                "assistant_id": request.assistant_id,
            },
            "result": {
                "success": result.success if result else None,
                "processing_time": result.processing_time if result else None,
                "error_message": result.error_message if result else None,
            }
            if result
            else None,
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Get assistant engine statistics.

        Returns:
            dict: Engine statistics
        """
        total_requests = len(self.processing_requests)
        total_results = len(self.processing_results)
        successful_results = len(
            [r for r in self.processing_results.values() if r.success]
        )
        failed_results = total_results - successful_results

        avg_processing_time = 0.0
        if total_results > 0:
            avg_processing_time = (
                sum(r.processing_time for r in self.processing_results.values())
                / total_results
            )

        return {
            "active_requests": total_requests,
            "total_processed": total_results,
            "successful_requests": successful_results,
            "failed_requests": failed_results,
            "success_rate": (successful_results / total_results * 100)
            if total_results > 0
            else 0,
            "average_processing_time": round(avg_processing_time, 3),
            "max_concurrent_requests": self.max_concurrent_requests,
            "default_model": self.default_model,
        }


# Global assistant engine instance
assistant_engine = AssistantEngine()
