"""
Assistant Engine for processing user messages and generating responses.

This module provides the main engine that integrates AI service, context manager,
and tool executor to process user messages and generate intelligent responses.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger

from app.core.config import get_settings
from app.services.ai_service import AIResponse, ai_service
from app.services.context_manager import context_manager
from app.services.knowledge_service import knowledge_service
from app.services.tool_executor import ToolExecution, tool_executor


class ProcessingStatus(Enum):
    """Processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingRequest:
    """Processing request data."""

    id: str
    user_id: str
    conversation_id: str
    assistant_id: str | None
    message: str
    use_knowledge_base: bool = True
    use_tools: bool = True
    max_context_chunks: int = 5
    temperature: float = 0.7
    max_tokens: int | None = None
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Processing result data."""

    request_id: str
    status: ProcessingStatus
    response: AIResponse | None = None
    tool_executions: list[ToolExecution] = field(default_factory=list)
    knowledge_used: list[dict[str, Any]] = field(default_factory=list)
    processing_time: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AssistantEngine:
    """Main assistant engine for processing user messages."""

    def __init__(self):
        """Initialize the assistant engine."""
        self.processing_requests: dict[str, ProcessingRequest] = {}
        self.processing_results: dict[str, ProcessingResult] = {}
        self.max_concurrent_requests = 5
        self.default_model = get_settings().default_ai_model
        self.default_max_tokens = 2048

        # Processing semaphore to limit concurrent requests
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent_requests)

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
    ) -> ProcessingResult:
        """
        Process a user message and generate a response.

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

        Returns:
            Processing result
        """
        # Create processing request
        request_id = f"req_{len(self.processing_requests)}_{datetime.now().timestamp()}"
        request = ProcessingRequest(
            id=request_id,
            user_id=user_id,
            conversation_id=conversation_id,
            assistant_id=assistant_id,
            message=message,
            use_knowledge_base=use_knowledge_base,
            use_tools=use_tools,
            max_context_chunks=max_context_chunks,
            temperature=temperature,
            max_tokens=max_tokens or self.default_max_tokens,
            model=model or self.default_model,
            metadata=metadata or {},
        )

        self.processing_requests[request_id] = request

        # Create processing result
        result = ProcessingResult(
            request_id=request_id,
            status=ProcessingStatus.PENDING,
        )
        self.processing_results[request_id] = result

        # Process with semaphore to limit concurrency
        async with self.processing_semaphore:
            return await self._process_request(request, result)

    async def _process_request(
        self,
        request: ProcessingRequest,
        result: ProcessingResult,
    ) -> ProcessingResult:
        """Process a single request."""
        start_time = datetime.now()
        result.status = ProcessingStatus.PROCESSING

        try:
            # Step 1: Add user message to context
            await context_manager.add_message(
                request.conversation_id,
                request.user_id,
                request.message,
                role="user",
            )

            # Step 2: Get knowledge base context if enabled
            knowledge_chunks = []
            if request.use_knowledge_base:
                knowledge_chunks = await self._get_knowledge_context(
                    request.user_id,
                    request.message,
                    request.max_context_chunks,
                )

                if knowledge_chunks:
                    await context_manager.add_knowledge_context(
                        request.conversation_id,
                        request.user_id,
                        knowledge_chunks,
                    )
                    result.knowledge_used = knowledge_chunks

            # Step 3: Get conversation context
            messages = await context_manager.get_messages_for_completion(
                request.conversation_id,
                request.user_id,
            )

            # Step 4: Prepare tools if enabled
            tools = []
            if request.use_tools:
                tools = await self._prepare_tools(request.message)

            # Step 5: Generate AI response
            ai_response = await self._generate_response(
                messages,
                tools,
                request.temperature,
                request.max_tokens,
                request.model,
            )

            # Step 6: Handle tool calls if any
            if ai_response.tool_calls:
                tool_results = await self._execute_tool_calls(
                    ai_response.tool_calls,
                    request.user_id,
                    request.conversation_id,
                )
                result.tool_executions = tool_results

                # Add tool results to context
                for tool_exec in tool_results:
                    if tool_exec.status.value == "completed":
                        await context_manager.add_tool_result(
                            request.conversation_id,
                            request.user_id,
                            tool_exec.tool_id,
                            tool_exec.result,
                        )

                # Generate follow-up response if needed
                if tool_results:
                    follow_up_messages = (
                        await context_manager.get_messages_for_completion(
                            request.conversation_id,
                            request.user_id,
                        )
                    )

                    follow_up_response = await self._generate_response(
                        follow_up_messages,
                        [],  # No tools for follow-up
                        request.temperature,
                        request.max_tokens,
                        request.model,
                    )

                    ai_response = follow_up_response

            # Step 7: Add assistant response to context
            if ai_response.content:
                await context_manager.add_message(
                    request.conversation_id,
                    request.user_id,
                    ai_response.content,
                    role="assistant",
                )

            # Step 8: Complete processing
            result.response = ai_response
            result.status = ProcessingStatus.COMPLETED

        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.error = str(e)
            logger.error(f"Error processing request {request.id}: {e}")

        finally:
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()

            # Clean up request
            if request.id in self.processing_requests:
                del self.processing_requests[request.id]

        return result

    async def _get_knowledge_context(
        self,
        user_id: str,
        query: str,
        max_chunks: int,
    ) -> list[dict[str, Any]]:
        """Get relevant knowledge base context."""
        try:
            search_results = await knowledge_service.search_documents(
                query=query,
                limit=max_chunks,
            )

            # Convert search results to knowledge chunks
            knowledge_chunks = []
            for result in search_results:
                chunk = {
                    "id": result.chunk_id,
                    "content": result.content,
                    "source": result.document_name,
                    "score": result.score,
                    "metadata": result.metadata or {},
                }
                knowledge_chunks.append(chunk)

            return knowledge_chunks

        except Exception as e:
            logger.error(f"Error getting knowledge context: {e}")
            return []

    async def _prepare_tools(self, user_message: str) -> list[dict[str, Any]]:
        """Prepare tools for AI completion."""
        try:
            available_tools = tool_executor.get_available_tools()
            tools = []

            for tool_def in available_tools:
                if tool_def.enabled:
                    schema = tool_executor.get_tool_schema(tool_def.id)
                    if schema:
                        tools.append(schema)

            return tools

        except Exception as e:
            logger.error(f"Error preparing tools: {e}")
            return []

    async def _generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> AIResponse:
        """Generate AI response."""
        try:
            # Prepare completion parameters
            completion_params = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": model,
            }

            # Add tools if available
            if tools:
                completion_params["tools"] = tools
                completion_params["tool_choice"] = "auto"

            # Generate completion
            response = await ai_service.chat_completion(**completion_params)

            # Parse response
            content = (
                response.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            tool_calls = (
                response.get("choices", [{}])[0].get("message", {}).get("tool_calls")
            )

            return AIResponse(
                content=content,
                tool_calls=tool_calls,
                metadata=response.get("usage", {}),
            )

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return AIResponse(
                content=f"Entschuldigung, es gab einen Fehler bei der Verarbeitung: {str(e)}",
                message_type="error",
            )

    async def _execute_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        user_id: str,
        conversation_id: str,
    ) -> list[ToolExecution]:
        """Execute tool calls from AI response."""
        tool_executions = []

        for tool_call in tool_calls:
            try:
                tool_id = tool_call.get("function", {}).get("name")
                arguments = tool_call.get("function", {}).get("arguments", "{}")

                # Parse arguments
                try:
                    params = json.loads(arguments)
                except json.JSONDecodeError:
                    params = {}

                # Execute tool
                execution = await tool_executor.execute_tool(
                    tool_id=tool_id,
                    parameters=params,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )

                tool_executions.append(execution)

            except Exception as e:
                logger.error(f"Error executing tool call: {e}")
                # Create failed execution record
                failed_execution = ToolExecution(
                    id=f"failed_{len(tool_executions)}",
                    tool_id=tool_call.get("function", {}).get("name", "unknown"),
                    user_id=user_id,
                    conversation_id=conversation_id,
                    parameters={},
                    status="failed",
                    error=str(e),
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                )
                tool_executions.append(failed_execution)

        return tool_executions

    async def get_processing_status(self, request_id: str) -> ProcessingResult | None:
        """Get processing status for a request."""
        return self.processing_results.get(request_id)

    async def cancel_processing(self, request_id: str) -> bool:
        """Cancel a processing request."""
        if request_id in self.processing_requests:
            # Mark as cancelled
            if request_id in self.processing_results:
                self.processing_results[request_id].status = ProcessingStatus.CANCELLED

            # Remove from active requests
            del self.processing_requests[request_id]
            return True

        return False

    async def get_processing_stats(self) -> dict[str, Any]:
        """Get processing statistics."""
        total_requests = len(self.processing_results)
        completed = len(
            [
                r
                for r in self.processing_results.values()
                if r.status == ProcessingStatus.COMPLETED
            ],
        )
        failed = len(
            [
                r
                for r in self.processing_results.values()
                if r.status == ProcessingStatus.FAILED
            ],
        )
        pending = len(
            [
                r
                for r in self.processing_results.values()
                if r.status == ProcessingStatus.PENDING
            ],
        )
        processing = len(
            [
                r
                for r in self.processing_results.values()
                if r.status == ProcessingStatus.PROCESSING
            ],
        )

        avg_processing_time = 0
        if completed > 0:
            processing_times = [
                r.processing_time
                for r in self.processing_results.values()
                if r.processing_time
            ]
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)

        return {
            "total_requests": total_requests,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "processing": processing,
            "success_rate": (completed / total_requests * 100)
            if total_requests > 0
            else 0,
            "average_processing_time": avg_processing_time,
            "active_requests": len(self.processing_requests),
            "max_concurrent_requests": self.max_concurrent_requests,
        }

    async def clear_old_results(self, max_age_hours: int = 24):
        """Clear old processing results."""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        results_to_remove = []
        for request_id, result in self.processing_results.items():
            # Extract timestamp from request_id
            try:
                timestamp_str = request_id.split("_")[-1]
                timestamp = float(timestamp_str)
                if timestamp < cutoff_time:
                    results_to_remove.append(request_id)
            except (ValueError, IndexError):
                # If we can't parse the timestamp, keep the result
                continue

        for request_id in results_to_remove:
            del self.processing_results[request_id]

        logger.info(f"Cleared {len(results_to_remove)} old processing results")


# Global assistant engine instance
assistant_engine = AssistantEngine()
