"""RAG Middleware for AI Service."""

from typing import Any, Dict, List, Optional

from ..types.ai_types import ChatRequest, RAGContext


class RAGMiddleware:
    """RAG (Retrieval-Augmented Generation) middleware."""

    def __init__(self, rag_service=None):
        self.rag_service = rag_service

    async def process(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        max_context_chunks: int = 5,
    ) -> List[Dict[str, str]]:
        """Process messages with RAG enhancement."""
        if not messages:
            return messages

        # Extract the last user message for RAG processing
        last_user_message = self._extract_last_user_message(messages)
        if not last_user_message:
            return messages

        try:
            # Get RAG context
            rag_context = await self._get_rag_context(
                last_user_message, user_id, max_context_chunks
            )

            if not rag_context or not rag_context.chunks:
                return messages

            # Enhance messages with RAG context
            enhanced_messages = self._enhance_messages_with_rag(messages, rag_context)
            return enhanced_messages

        except Exception as e:
            # Log error but continue without RAG enhancement
            print(f"RAG processing failed: {str(e)}")
            return messages

    def _extract_last_user_message(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Extract the last user message from the conversation."""
        for message in reversed(messages):
            if message.get("role") == "user":
                return message.get("content", "")
        return None

    async def _get_rag_context(
        self, query: str, user_id: str, max_context_chunks: int
    ) -> Optional[RAGContext]:
        """Get RAG context for the query."""
        if not self.rag_service:
            return None

        try:
            # Use existing RAG service to get relevant chunks
            rag_messages = await self.rag_service.create_rag_prompt(
                query, user_id, max_context_chunks=max_context_chunks
            )

            # Extract context from RAG messages
            context = self._extract_context_from_rag_messages(rag_messages)
            return context

        except Exception as e:
            print(f"Failed to get RAG context: {str(e)}")
            return None

    def _extract_context_from_rag_messages(
        self, rag_messages: List[Dict[str, str]]
    ) -> Optional[RAGContext]:
        """Extract RAG context from processed messages."""
        if not rag_messages:
            return None

        # Find system message with RAG context
        for message in rag_messages:
            if message.get("role") == "system":
                content = message.get("content", "")
                if "context:" in content.lower() or "relevant information:" in content.lower():
                    # Extract chunks and sources from system message
                    chunks = self._parse_rag_chunks(content)
                    sources = self._extract_sources(content)
                    
                    return RAGContext(
                        query="",  # Will be filled by caller
                        chunks=chunks,
                        relevance_scores=[1.0] * len(chunks),  # Default scores
                        sources=sources,
                    )

        return None

    def _parse_rag_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Parse RAG chunks from system message content."""
        chunks = []
        
        # Simple parsing - look for document chunks
        lines = content.split("\n")
        current_chunk = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith("Document:") or line.startswith("Chunk:"):
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = {"content": line}
            elif line and current_chunk:
                current_chunk["content"] = current_chunk.get("content", "") + "\n" + line
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def _extract_sources(self, content: str) -> List[str]:
        """Extract source information from RAG content."""
        sources = []
        
        # Look for source patterns
        lines = content.split("\n")
        for line in lines:
            if "source:" in line.lower() or "file:" in line.lower():
                # Extract filename or source
                parts = line.split(":")
                if len(parts) > 1:
                    source = parts[1].strip()
                    if source:
                        sources.append(source)
        
        return sources

    def _enhance_messages_with_rag(
        self, messages: List[Dict[str, str]], rag_context: RAGContext
    ) -> List[Dict[str, str]]:
        """Enhance messages with RAG context."""
        if not rag_context.chunks:
            return messages

        # Create context summary
        context_summary = self._create_context_summary(rag_context)

        # Add context to system message or create new one
        enhanced_messages = []
        context_added = False

        for message in messages:
            if message.get("role") == "system" and not context_added:
                # Enhance existing system message
                enhanced_content = message.get("content", "") + "\n\n" + context_summary
                enhanced_messages.append({
                    "role": "system",
                    "content": enhanced_content
                })
                context_added = True
            else:
                enhanced_messages.append(message)

        # If no system message found, add one at the beginning
        if not context_added:
            enhanced_messages.insert(0, {
                "role": "system",
                "content": context_summary
            })

        return enhanced_messages

    def _create_context_summary(self, rag_context: RAGContext) -> str:
        """Create a summary of RAG context for the AI."""
        summary = "You have access to the following relevant information:\n\n"
        
        for i, chunk in enumerate(rag_context.chunks):
            content = chunk.get("content", "")
            if content:
                summary += f"Context {i+1}:\n{content}\n\n"
        
        if rag_context.sources:
            summary += f"Sources: {', '.join(rag_context.sources)}\n\n"
        
        summary += "Please use this information to provide accurate and helpful responses."
        
        return summary

    def should_apply_rag(self, messages: List[Dict[str, str]], use_knowledge_base: bool) -> bool:
        """Determine if RAG should be applied."""
        if not use_knowledge_base:
            return False
        
        if not messages:
            return False
        
        # Check if there's a user message that might benefit from RAG
        has_user_message = any(
            message.get("role") == "user" for message in messages
        )
        
        return has_user_message

    def get_rag_metrics(self, rag_context: Optional[RAGContext]) -> Dict[str, Any]:
        """Get metrics about RAG processing."""
        if not rag_context:
            return {
                "chunks_retrieved": 0,
                "sources_used": 0,
                "context_length": 0,
            }
        
        total_context_length = sum(
            len(chunk.get("content", "")) for chunk in rag_context.chunks
        )
        
        return {
            "chunks_retrieved": len(rag_context.chunks),
            "sources_used": len(rag_context.sources),
            "context_length": total_context_length,
            "avg_relevance_score": sum(rag_context.relevance_scores) / len(rag_context.relevance_scores) if rag_context.relevance_scores else 0,
        }