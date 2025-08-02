"""
Assistant Memory Manager Service.

This module provides memory management functionality for assistant processing,
including agent memory updates, retrieval, and context management.
"""

from typing import Any

from loguru import logger

from backend.app.schemas.hybrid_mode import AgentMemory
from backend.app.services.hybrid_mode_manager import hybrid_mode_manager


class ProcessingRequest:
    """Request for message processing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AIResponse:
    """AI response with structured output."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class AssistantMemoryManager:
    """Manager for assistant memory and context retention."""

    def __init__(self):
        """Initialize the memory manager."""
        self.hybrid_mode_manager = hybrid_mode_manager

    async def update_memory(
        self, request: ProcessingRequest, ai_response: AIResponse
    ) -> list[AgentMemory]:
        """
        Update agent memory with new information.

        Args:
            request: Processing request
            ai_response: AI response

        Returns:
            List[AgentMemory]: Updated memory entries
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            # Create memory entries based on response
            memory_entries = []

            # Memory for user interaction
            user_memory = AgentMemory(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                memory_type="user_interaction",
                content={
                    "user_message": request.message,
                    "assistant_response": ai_response.content,
                    "tools_used": ai_response.tool_calls if ai_response.tool_calls else [],
                    "model_used": ai_response.metadata.get("model_used"),
                    "processing_time": ai_response.metadata.get("processing_time"),
                },
                importance=0.7,
            )
            memory_entries.append(user_memory)

            # Memory for tool usage if tools were used
            if ai_response.tool_calls:
                tool_memory = AgentMemory(
                    conversation_id=request.conversation_id,
                    user_id=request.user_id,
                    memory_type="tool_usage",
                    content={
                        "tools_used": ai_response.tool_calls,
                        "user_message": request.message,
                        "success": True,
                    },
                    importance=0.8,
                )
                memory_entries.append(tool_memory)

            # Memory for knowledge context if used
            if ai_response.metadata.get("knowledge_context_used"):
                knowledge_memory = AgentMemory(
                    conversation_id=request.conversation_id,
                    user_id=request.user_id,
                    memory_type="knowledge_usage",
                    content={
                        "user_query": request.message,
                        "knowledge_accessed": True,
                        "context_chunks": ai_response.metadata.get("context_chunks", 0),
                    },
                    importance=0.6,
                )
                memory_entries.append(knowledge_memory)

            # Add memories to memory manager
            for memory in memory_entries:
                memory_manager.add_memory(
                    conversation_id=request.conversation_id,
                    user_id=request.user_id,
                    memory_type=memory.memory_type,
                    content=memory.content,
                    importance=memory.importance,
                )

            logger.debug(f"Updated memory with {len(memory_entries)} entries for conversation {request.conversation_id}")
            return memory_entries

        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            return []

    async def get_memory_context(
        self, request: ProcessingRequest, user_message: str
    ) -> list[AgentMemory]:
        """
        Get relevant memory context for the request.

        Args:
            request: Processing request
            user_message: User message

        Returns:
            List[AgentMemory]: Relevant memory entries
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            # Get relevant memories
            relevant_memories = memory_manager.get_relevant_memories(
                conversation_id=request.conversation_id,
                query=user_message,
                limit=5,
            )

            logger.debug(f"Retrieved {len(relevant_memories)} relevant memories for conversation {request.conversation_id}")
            return relevant_memories

        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return []

    async def get_conversation_memory_summary(
        self, conversation_id: str
    ) -> dict[str, Any]:
        """
        Get memory summary for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            dict: Memory summary
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            # Get all memories for conversation
            all_memories = memory_manager.memories.get(conversation_id, [])

            if not all_memories:
                return {
                    "conversation_id": conversation_id,
                    "total_memories": 0,
                    "memory_types": {},
                    "average_importance": 0.0,
                    "recent_memories": [],
                }

            # Analyze memories
            memory_types = {}
            total_importance = 0.0

            for memory in all_memories:
                memory_type = memory.memory_type
                memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
                total_importance += memory.importance

            # Get recent memories (last 10)
            recent_memories = sorted(
                all_memories,
                key=lambda x: x.created_at,
                reverse=True
            )[:10]

            return {
                "conversation_id": conversation_id,
                "total_memories": len(all_memories),
                "memory_types": memory_types,
                "average_importance": total_importance / len(all_memories) if all_memories else 0.0,
                "recent_memories": [
                    {
                        "type": memory.memory_type,
                        "importance": memory.importance,
                        "created_at": memory.created_at.isoformat(),
                        "content_summary": str(memory.content)[:100] + "...",
                    }
                    for memory in recent_memories
                ],
            }

        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {"error": str(e)}

    async def cleanup_old_memories(self, conversation_id: str) -> int:
        """
        Clean up old memories for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            int: Number of memories cleaned up
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            # Get current memories
            current_memories = memory_manager.memories.get(conversation_id, [])
            
            if not current_memories:
                return 0

            # Clean up expired memories
            memory_manager._cleanup_expired_memories(conversation_id)

            # Get remaining memories
            remaining_memories = memory_manager.memories.get(conversation_id, [])
            cleaned_count = len(current_memories) - len(remaining_memories)

            logger.info(f"Cleaned up {cleaned_count} old memories for conversation {conversation_id}")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up memories: {e}")
            return 0

    async def get_user_memory_patterns(
        self, user_id: str, time_period_hours: int = 24
    ) -> dict[str, Any]:
        """
        Get memory patterns for a user.

        Args:
            user_id: User ID
            time_period_hours: Time period for analysis

        Returns:
            dict: Memory patterns
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            # Get all memories for user
            user_memories = []
            for conversation_memories in memory_manager.memories.values():
                for memory in conversation_memories:
                    if memory.user_id == user_id:
                        user_memories.append(memory)

            if not user_memories:
                return {
                    "user_id": user_id,
                    "total_memories": 0,
                    "memory_patterns": {},
                    "frequent_topics": [],
                }

            # Analyze patterns
            memory_types = {}
            topics = {}

            for memory in user_memories:
                # Count memory types
                memory_type = memory.memory_type
                memory_types[memory_type] = memory_types.get(memory_type, 0) + 1

                # Extract topics from content
                content = memory.content
                if isinstance(content, dict):
                    user_message = content.get("user_message", "")
                    if user_message:
                        # Simple topic extraction (first few words)
                        words = user_message.split()[:5]
                        topic = " ".join(words).lower()
                        topics[topic] = topics.get(topic, 0) + 1

            # Get frequent topics
            frequent_topics = sorted(
                topics.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            return {
                "user_id": user_id,
                "total_memories": len(user_memories),
                "memory_patterns": memory_types,
                "frequent_topics": [
                    {"topic": topic, "count": count}
                    for topic, count in frequent_topics
                ],
                "average_importance": sum(m.importance for m in user_memories) / len(user_memories),
            }

        except Exception as e:
            logger.error(f"Error getting user memory patterns: {e}")
            return {"error": str(e)}

    def get_memory_stats(self) -> dict[str, Any]:
        """
        Get memory manager statistics.

        Returns:
            dict: Memory manager statistics
        """
        try:
            # Get memory manager from hybrid mode manager
            memory_manager = self.hybrid_mode_manager.memory_manager

            total_memories = sum(len(memories) for memories in memory_manager.memories.values())
            total_conversations = len(memory_manager.memories)

            # Calculate average memories per conversation
            avg_memories_per_conversation = (
                total_memories / total_conversations if total_conversations > 0 else 0
            )

            return {
                "total_memories": total_memories,
                "total_conversations": total_conversations,
                "average_memories_per_conversation": round(avg_memories_per_conversation, 2),
                "memory_retention_hours": memory_manager.config.memory_retention_hours,
            }

        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}


# Global memory manager instance
assistant_memory_manager = AssistantMemoryManager()