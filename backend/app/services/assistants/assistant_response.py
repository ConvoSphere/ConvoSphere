"""
Assistant Response Generator Service.

This module provides response generation functionality for assistant processing,
including AI model integration, structured output generation, and response formatting.
"""

from typing import Any

from loguru import logger

from backend.app.schemas.hybrid_mode import StructuredResponse
from backend.app.services.ai_service import ai_service
from backend.app.services.hybrid_mode_manager import hybrid_mode_manager


class ProcessingRequest:
    """Request for message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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


class AssistantResponseGenerator:
    """Generator for assistant responses with AI integration."""

    def __init__(self):
        """Initialize the response generator."""
        self.ai_service = ai_service
        self.hybrid_mode_manager = hybrid_mode_manager

    async def generate_response(
        self,
        request: ProcessingRequest,
        context: dict[str, Any],
        knowledge_context: str,
        tools: list[dict[str, Any]],
    ) -> AIResponse:
        """
        Generate AI response for the request.

        Args:
            request: Processing request
            context: Conversation context
            knowledge_context: Knowledge base context
            tools: Available tools

        Returns:
            AIResponse: Generated AI response
        """
        try:
            # Decide conversation mode
            mode_decision = await self.hybrid_mode_manager.decide_mode(
                conversation_id=request.conversation_id,
                user_message=request.message,
                context=context,
                force_mode=request.force_mode,
            )

            # Prepare messages for AI
            messages = self._prepare_messages_for_ai(
                request, context, knowledge_context, mode_decision
            )

            # Create system message
            system_message = self._create_system_message(
                mode_decision, knowledge_context
            )

            # Generate AI response
            ai_response = await self.ai_service.generate_response(
                messages=messages,
                system_message=system_message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=tools if tools else None,
            )

            # Create AI response object
            response = AIResponse(
                content=ai_response.get("content", ""),
                tool_calls=ai_response.get("tool_calls", []),
                metadata={
                    "model_used": ai_response.get("model_used", request.model),
                    "tokens_used": ai_response.get("tokens_used", 0),
                    "processing_time": ai_response.get("processing_time", 0.0),
                    "mode_decision": mode_decision.dict() if mode_decision else None,
                    "knowledge_context_used": bool(knowledge_context),
                    "tools_available": len(tools) if tools else 0,
                },
            )

            logger.debug(
                f"Generated response for conversation {request.conversation_id}"
            )
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return AIResponse(
                content=f"Entschuldigung, es gab einen Fehler bei der Antwortgenerierung: {str(e)}",
                metadata={"error": str(e)},
            )

    def _prepare_messages_for_ai(
        self,
        request: ProcessingRequest,
        context: dict[str, Any],
        knowledge_context: str,
        mode_decision,
    ) -> list[dict[str, str]]:
        """
        Prepare messages for AI processing.

        Args:
            request: Processing request
            context: Conversation context
            knowledge_context: Knowledge base context
            mode_decision: Mode decision

        Returns:
            List[dict]: Messages for AI
        """
        messages = []

        # Add conversation history
        conversation_messages = context.get("messages", [])
        for msg in conversation_messages[-10:]:  # Last 10 messages
            if msg.get("role") in ["user", "assistant"]:
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )

        # Add current user message
        messages.append(
            {
                "role": "user",
                "content": request.message,
            }
        )

        return messages

    def _create_system_message(self, mode_decision, knowledge_context: str) -> str:
        """
        Create system message for AI.

        Args:
            mode_decision: Mode decision
            knowledge_context: Knowledge base context

        Returns:
            str: System message
        """
        system_message = "Du bist ein hilfreicher KI-Assistent."

        # Add mode-specific instructions
        if mode_decision and mode_decision.recommended_mode:
            mode = mode_decision.recommended_mode
            if mode == "agent":
                system_message += (
                    " Du arbeitest im Agent-Modus und kannst Tools verwenden."
                )
            elif mode == "chat":
                system_message += (
                    " Du arbeitest im Chat-Modus für natürliche Konversation."
                )
            else:
                system_message += (
                    " Du arbeitest im Hybrid-Modus und passt dich automatisch an."
                )

        # Add knowledge context if available
        if knowledge_context:
            system_message += f"\n\n{knowledge_context}"

        # Add general instructions
        system_message += """

        Wichtige Hinweise:
        - Antworte in der Sprache der Benutzerfrage
        - Sei hilfreich und präzise
        - Verwende Tools wenn nötig
        - Gib strukturierte Antworten wenn möglich
        """

        return system_message

    async def create_structured_response(
        self, request: ProcessingRequest, ai_response: AIResponse
    ) -> StructuredResponse:
        """
        Create structured response from AI response.

        Args:
            request: Processing request
            ai_response: AI response

        Returns:
            StructuredResponse: Structured response
        """
        try:
            # Create structured response
            structured_response = StructuredResponse(
                content=ai_response.content,
                metadata=ai_response.metadata,
                tool_calls=ai_response.tool_calls,
                message_type=ai_response.message_type,
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                assistant_id=request.assistant_id,
            )

            logger.debug(f"Created structured response for {request.conversation_id}")
            return structured_response

        except Exception as e:
            logger.error(f"Error creating structured response: {e}")
            # Return fallback structured response
            return StructuredResponse(
                content=f"Fehler bei der Erstellung der strukturierten Antwort: {str(e)}",
                metadata={"error": str(e)},
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                assistant_id=request.assistant_id,
            )

    async def format_response_for_user(
        self, ai_response: AIResponse, include_metadata: bool = False
    ) -> dict[str, Any]:
        """
        Format response for user consumption.

        Args:
            ai_response: AI response
            include_metadata: Whether to include metadata

        Returns:
            dict: Formatted response
        """
        formatted_response = {
            "content": ai_response.content,
            "message_type": ai_response.message_type,
        }

        if ai_response.tool_calls:
            formatted_response["tool_calls"] = ai_response.tool_calls

        if include_metadata:
            formatted_response["metadata"] = ai_response.metadata

        return formatted_response

    async def validate_response(
        self, ai_response: AIResponse
    ) -> tuple[bool, str | None]:
        """
        Validate AI response.

        Args:
            ai_response: AI response to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check if response has content
            if not ai_response.content or not ai_response.content.strip():
                return False, "Response content is empty"

            # Check content length
            if len(ai_response.content) > 10000:
                return False, "Response content too long"

            # Check for inappropriate content (basic check)
            inappropriate_words = ["error", "exception", "traceback"]
            content_lower = ai_response.content.lower()
            for word in inappropriate_words:
                if word in content_lower:
                    return False, f"Response contains inappropriate content: {word}"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_response_stats(self) -> dict[str, Any]:
        """
        Get response generator statistics.

        Returns:
            dict: Response generator statistics
        """
        try:
            ai_stats = self.ai_service.get_stats()

            return {
                "ai_service": ai_stats,
                "total_responses_generated": ai_stats.get("total_requests", 0),
                "average_response_time": ai_stats.get("average_response_time", 0.0),
                "success_rate": ai_stats.get("success_rate", 0.0),
            }

        except Exception as e:
            logger.error(f"Error getting response stats: {e}")
            return {"error": str(e)}


# Global response generator instance
assistant_response_generator = AssistantResponseGenerator()
