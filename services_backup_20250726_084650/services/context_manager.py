"""
Context Manager for conversation context management.

This module provides conversation context management with token limits,
message history, and context optimization for AI assistants.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger


class ContextType(Enum):
    """Context type enumeration."""

    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    USER_PROFILE = "user_profile"


@dataclass
class ContextItem:
    """Individual context item."""

    id: str
    type: ContextType
    content: str
    metadata: dict[str, Any]
    timestamp: datetime
    token_count: int
    importance_score: float = 1.0
    expires_at: datetime | None = None


@dataclass
class ConversationContext:
    """Conversation context container."""

    conversation_id: str
    user_id: str
    assistant_id: str | None
    items: list[ContextItem] = field(default_factory=list)
    max_tokens: int = 8000
    current_tokens: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    settings: dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Manages conversation context with token limits and optimization."""

    def __init__(self):
        """Initialize the context manager."""
        self.contexts: dict[str, ConversationContext] = {}
        self.max_context_age = timedelta(hours=24)  # Context expires after 24 hours
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.token_buffer = 500  # Buffer for token estimation

        # Start cleanup task
        asyncio.create_task(self._cleanup_old_contexts())

    async def get_context(
        self,
        conversation_id: str,
        user_id: str,
    ) -> ConversationContext:
        """
        Get or create conversation context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Conversation context
        """
        if conversation_id not in self.contexts:
            self.contexts[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
            )

        return self.contexts[conversation_id]

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        role: str = "user",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Add a message to the conversation context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            role: Message role (user, assistant, system)
            metadata: Additional metadata

        Returns:
            True if added successfully
        """
        context = await self.get_context(conversation_id, user_id)

        # Determine context type based on role
        if role == "system":
            context_type = ContextType.SYSTEM
        elif role == "assistant":
            context_type = ContextType.CONVERSATION
        else:
            context_type = ContextType.CONVERSATION

        # Estimate token count
        token_count = await self._estimate_tokens(content)

        # Create context item
        item = ContextItem(
            id=f"msg_{len(context.items)}",
            type=context_type,
            content=content,
            metadata={
                "role": role,
                "user_id": user_id,
                **(metadata or {}),
            },
            timestamp=datetime.now(),
            token_count=token_count,
        )

        # Check if adding this item would exceed token limit
        if context.current_tokens + token_count > context.max_tokens:
            # Optimize context to make room
            await self._optimize_context(context)

            # Check again after optimization
            if context.current_tokens + token_count > context.max_tokens:
                logger.warning(f"Context full for conversation {conversation_id}")
                return False

        # Add item to context
        context.items.append(item)
        context.current_tokens += token_count
        context.updated_at = datetime.now()

        return True

    async def add_knowledge_context(
        self,
        conversation_id: str,
        user_id: str,
        knowledge_chunks: list[dict[str, Any]],
    ) -> bool:
        """
        Add knowledge base context to conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            knowledge_chunks: List of knowledge chunks

        Returns:
            True if added successfully
        """
        context = await self.get_context(conversation_id, user_id)

        for chunk in knowledge_chunks:
            content = chunk.get("content", "")
            token_count = await self._estimate_tokens(content)

            item = ContextItem(
                id=f"knowledge_{len(context.items)}",
                type=ContextType.KNOWLEDGE,
                content=content,
                metadata={
                    "source": chunk.get("source"),
                    "score": chunk.get("score", 0.0),
                    "chunk_id": chunk.get("id"),
                    **(chunk.get("metadata", {})),
                },
                timestamp=datetime.now(),
                token_count=token_count,
                importance_score=chunk.get("score", 0.5),
            )

            # Check token limit
            if context.current_tokens + token_count > context.max_tokens:
                await self._optimize_context(context)

                if context.current_tokens + token_count > context.max_tokens:
                    logger.warning("Cannot add knowledge context - limit exceeded")
                    return False

            context.items.append(item)
            context.current_tokens += token_count

        context.updated_at = datetime.now()
        return True

    async def add_tool_result(
        self,
        conversation_id: str,
        user_id: str,
        tool_name: str,
        result: Any,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Add tool execution result to context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            tool_name: Name of the tool
            result: Tool execution result
            metadata: Additional metadata

        Returns:
            True if added successfully
        """
        context = await self.get_context(conversation_id, user_id)

        # Convert result to string
        if isinstance(result, dict):
            content = json.dumps(result, indent=2)
        else:
            content = str(result)

        token_count = await self._estimate_tokens(content)

        item = ContextItem(
            id=f"tool_{len(context.items)}",
            type=ContextType.TOOL_RESULT,
            content=content,
            metadata={
                "tool_name": tool_name,
                "result_type": type(result).__name__,
                **(metadata or {}),
            },
            timestamp=datetime.now(),
            token_count=token_count,
            importance_score=0.8,  # Tool results are moderately important
        )

        # Check token limit
        if context.current_tokens + token_count > context.max_tokens:
            await self._optimize_context(context)

            if context.current_tokens + token_count > context.max_tokens:
                logger.warning("Cannot add tool result - limit exceeded")
                return False

        context.items.append(item)
        context.current_tokens += token_count
        context.updated_at = datetime.now()

        return True

    async def get_messages_for_completion(
        self,
        conversation_id: str,
        user_id: str,
        max_tokens: int | None = None,
    ) -> list[dict[str, str]]:
        """
        Get messages formatted for AI completion.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            max_tokens: Maximum tokens to include

        Returns:
            List of messages in OpenAI format
        """
        context = await self.get_context(conversation_id, user_id)

        if max_tokens is None:
            max_tokens = context.max_tokens - self.token_buffer

        messages = []
        current_tokens = 0

        # Add items in chronological order, respecting token limit
        for item in context.items:
            if current_tokens + item.token_count > max_tokens:
                break

            # Format based on context type
            if item.type == ContextType.CONVERSATION:
                role = item.metadata.get("role", "user")
                messages.append(
                    {
                        "role": role,
                        "content": item.content,
                    },
                )
            elif item.type == ContextType.KNOWLEDGE:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Relevant information: {item.content}",
                    },
                )
            elif item.type == ContextType.TOOL_RESULT:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Tool result ({item.metadata.get('tool_name', 'unknown')}): {item.content}",
                    },
                )
            elif item.type == ContextType.SYSTEM:
                messages.append(
                    {
                        "role": "system",
                        "content": item.content,
                    },
                )

            current_tokens += item.token_count

        return messages

    async def get_context_summary(
        self,
        conversation_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Get context summary and statistics.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Context summary
        """
        context = await self.get_context(conversation_id, user_id)

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "total_items": len(context.items),
            "current_tokens": context.current_tokens,
            "max_tokens": context.max_tokens,
            "token_usage_percent": (context.current_tokens / context.max_tokens) * 100,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "items_by_type": {
                item_type.value: len(
                    [item for item in context.items if item.type == item_type],
                )
                for item_type in ContextType
            },
        }

    async def clear_context(self, conversation_id: str, user_id: str):
        """Clear conversation context."""
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]
            logger.info(f"Cleared context for conversation {conversation_id}")

    async def set_context_settings(
        self,
        conversation_id: str,
        user_id: str,
        settings: dict[str, Any],
    ):
        """Set context settings."""
        context = await self.get_context(conversation_id, user_id)
        context.settings.update(settings)

        # Update max tokens if specified
        if "max_tokens" in settings:
            context.max_tokens = settings["max_tokens"]

    async def _optimize_context(self, context: ConversationContext):
        """
        Optimize context by removing less important items.

        Args:
            context: Conversation context to optimize
        """
        if context.current_tokens <= context.max_tokens:
            return

        # Sort items by importance and recency
        def sort_key(item: ContextItem) -> tuple[float, datetime]:
            # Higher importance score = higher priority
            # More recent = higher priority
            recency_score = (
                datetime.now() - item.timestamp
            ).total_seconds() / 3600  # Hours ago
            return (item.importance_score, -recency_score)

        # Sort items (least important first)
        sorted_items = sorted(context.items, key=sort_key)

        # Remove items until we're under the limit
        tokens_to_remove = (
            context.current_tokens - context.max_tokens + self.token_buffer
        )

        removed_tokens = 0
        items_to_remove = []

        for item in sorted_items:
            if removed_tokens >= tokens_to_remove:
                break

            # Don't remove system messages unless absolutely necessary
            if (
                item.type == ContextType.SYSTEM
                and removed_tokens < tokens_to_remove * 0.8
            ):
                continue

            items_to_remove.append(item)
            removed_tokens += item.token_count

        # Remove items
        for item in items_to_remove:
            context.items.remove(item)
            context.current_tokens -= item.token_count

        logger.info(
            f"Optimized context: removed {len(items_to_remove)} items, "
            f"freed {removed_tokens} tokens",
        )

    async def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        # In a production system, you'd use a proper tokenizer
        return len(text) // 4 + 1

    async def _cleanup_old_contexts(self):
        """Clean up old contexts periodically."""
        while True:
            try:
                current_time = datetime.now()
                contexts_to_remove = []

                for conversation_id, context in self.contexts.items():
                    if current_time - context.updated_at > self.max_context_age:
                        contexts_to_remove.append(conversation_id)

                for conversation_id in contexts_to_remove:
                    del self.contexts[conversation_id]
                    logger.info(f"Cleaned up old context: {conversation_id}")

                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"Error in context cleanup: {e}")
                await asyncio.sleep(self.cleanup_interval)


# Global context manager instance
context_manager = ContextManager()
