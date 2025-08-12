"""
Assistant Context Manager Service.

This module provides context management functionality for assistant processing,
including conversation context, knowledge base integration, and response saving.
"""

from typing import Any

from loguru import logger

from backend.app.schemas.hybrid_mode import StructuredResponse
from backend.app.services.conversation_service import conversation_service
from backend.app.services.hybrid_mode_manager import hybrid_mode_manager
from backend.app.services.knowledge_service import knowledge_service


class ProcessingRequest:
    """Request for message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AssistantContextManager:
    """Manager for assistant context and conversation handling."""

    def __init__(self):
        """Initialize the context manager."""
        self.hybrid_mode_manager = hybrid_mode_manager
        self.conversation_service = conversation_service
        self.knowledge_service = knowledge_service

    async def get_conversation_context(
        self, request: ProcessingRequest
    ) -> dict[str, Any]:
        """
        Get conversation context for processing.

        Args:
            request: Processing request

        Returns:
            dict: Conversation context
        """
        try:
            # Get conversation messages
            conversation = await self.conversation_service.get_conversation(
                request.conversation_id
            )

            if not conversation:
                return {
                    "messages": [],
                    "conversation_id": request.conversation_id,
                    "user_id": request.user_id,
                    "assistant_id": request.assistant_id,
                }

            # Get recent messages
            messages = await self.conversation_service.get_conversation_messages(
                request.conversation_id, limit=10
            )

            # Get hybrid mode state
            mode_state = self.hybrid_mode_manager.get_state(request.conversation_id)
            if not mode_state:
                # Initialize hybrid mode if not exists
                mode_state = self.hybrid_mode_manager.initialize_conversation(
                    request.conversation_id,
                    request.user_id,
                )

            context = {
                "messages": [msg.dict() for msg in messages],
                "conversation_id": request.conversation_id,
                "user_id": request.user_id,
                "assistant_id": request.assistant_id,
                "hybrid_mode_state": mode_state.dict() if mode_state else None,
                "conversation_metadata": (
                    conversation.conversation_metadata if conversation else {}
                ),
            }

            logger.debug(
                f"Retrieved context for conversation {request.conversation_id}"
            )
            return context

        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {
                "messages": [],
                "conversation_id": request.conversation_id,
                "user_id": request.user_id,
                "assistant_id": request.assistant_id,
                "error": str(e),
            }

    async def prepare_knowledge_context(self, request: ProcessingRequest) -> str:
        """
        Prepare knowledge base context for the request.

        Args:
            request: Processing request

        Returns:
            str: Knowledge context string
        """
        try:
            if not request.use_knowledge_base:
                return ""

            # Search knowledge base for relevant content
            search_results = await self.knowledge_service.search_knowledge(
                query=request.message,
                user_id=request.user_id,
                limit=request.max_context_chunks,
            )

            if not search_results:
                return ""

            # Format knowledge context
            knowledge_context = "Relevante Informationen aus der Wissensdatenbank:\n\n"

            for i, result in enumerate(search_results, 1):
                knowledge_context += f"{i}. {result.get('title', 'Unbekannt')}\n"
                knowledge_context += f"   {result.get('content', '')[:200]}...\n\n"

            logger.debug(
                f"Prepared knowledge context with {len(search_results)} chunks"
            )
            return knowledge_context

        except Exception as e:
            logger.error(f"Error preparing knowledge context: {e}")
            return ""

    async def update_conversation_mode(
        self, request: ProcessingRequest, new_mode: str
    ) -> bool:
        """
        Update conversation mode.

        Args:
            request: Processing request
            new_mode: New conversation mode

        Returns:
            bool: True if updated successfully
        """
        try:
            # Update hybrid mode state
            mode_request = {
                "conversation_id": request.conversation_id,
                "user_id": request.user_id,
                "new_mode": new_mode,
                "reason": "Automatic mode change based on request",
            }

            await self.hybrid_mode_manager.change_mode(mode_request)

            logger.info(
                f"Updated conversation mode to {new_mode} for {request.conversation_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error updating conversation mode: {e}")
            return False

    async def save_response_to_conversation(
        self, request: ProcessingRequest, structured_response: StructuredResponse
    ) -> bool:
        """
        Save response to conversation.

        Args:
            request: Processing request
            structured_response: Structured response to save

        Returns:
            bool: True if saved successfully
        """
        try:
            # Save user message
            await self.conversation_service.add_message(
                conversation_id=request.conversation_id,
                content=request.message,
                role="user",
                metadata=request.metadata,
            )

            # Save assistant response
            await self.conversation_service.add_message(
                conversation_id=request.conversation_id,
                content=structured_response.content,
                role="assistant",
                metadata={
                    "model_used": structured_response.metadata.get("model_used"),
                    "tokens_used": structured_response.metadata.get("tokens_used"),
                    "processing_time": structured_response.metadata.get(
                        "processing_time"
                    ),
                    "tool_calls": structured_response.metadata.get("tool_calls", []),
                    "structured_response": structured_response.dict(),
                },
            )

            logger.debug(f"Saved response to conversation {request.conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving response to conversation: {e}")
            return False

    async def get_conversation_summary(
        self, conversation_id: str
    ) -> dict[str, Any] | None:
        """
        Get conversation summary.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Conversation summary or None if not found
        """
        try:
            conversation = await self.conversation_service.get_conversation(
                conversation_id
            )
            if not conversation:
                return None

            messages = await self.conversation_service.get_conversation_messages(
                conversation_id, limit=50
            )

            return {
                "conversation_id": conversation_id,
                "title": conversation.title,
                "message_count": len(messages),
                "total_tokens": conversation.total_tokens,
                "created_at": (
                    conversation.created_at.isoformat()
                    if conversation.created_at
                    else None
                ),
                "last_message": messages[-1].dict() if messages else None,
                "metadata": conversation.conversation_metadata,
            }

        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return None

    async def cleanup_conversation_context(self, conversation_id: str) -> bool:
        """
        Clean up conversation context.

        Args:
            conversation_id: Conversation ID

        Returns:
            bool: True if cleaned up successfully
        """
        try:
            # Clean up hybrid mode state
            self.hybrid_mode_manager.cleanup_conversation(conversation_id)

            logger.info(f"Cleaned up context for conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error cleaning up conversation context: {e}")
            return False

    def get_context_stats(self) -> dict[str, Any]:
        """
        Get context manager statistics.

        Returns:
            dict: Context manager statistics
        """
        try:
            hybrid_stats = self.hybrid_mode_manager.get_stats()

            return {
                "hybrid_mode_manager": hybrid_stats,
                "active_conversations": hybrid_stats.get("active_conversations", 0),
                "mode_changes": hybrid_stats.get("mode_changes", 0),
            }

        except Exception as e:
            logger.error(f"Error getting context stats: {e}")
            return {"error": str(e)}


# Global context manager instance
assistant_context_manager = AssistantContextManager()
