"""RAG Middleware for AI Service."""

from typing import Any, Dict, List, Optional

from ..utils.rag_service import RAGService
from ..types.ai_types import ChatRequest, RAGContext


class RAGMiddleware:
    """RAG (Retrieval-Augmented Generation) middleware."""

    def __init__(self, rag_service=None):
        """Initialize RAG middleware with optional RAG service."""
        self.rag_service = rag_service or RAGService()

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
            # Get RAG context using existing RAG service
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
        """Get RAG context for the query using existing RAG service."""
        try:
            # Use existing RAG service to get relevant chunks
            rag_messages = await self.rag_service.create_rag_prompt(
                query, user_id, max_context_chunks=max_context_chunks
            )

            # Extract context from RAG messages
            context = self._extract_context_from_rag_messages(rag_messages, query)
            return context

        except Exception as e:
            print(f"Failed to get RAG context: {str(e)}")
            return None

    def _extract_context_from_rag_messages(
        self, rag_messages: List[Dict[str, str]], query: str
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
                        query=query,
                        chunks=chunks,
                        relevance_scores=[1.0] * len(chunks),  # Default scores
                        sources=sources,
                    )

        return None

    def _parse_rag_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Parse RAG chunks from content."""
        chunks = []
        
        # Simple parsing - look for content between markers
        lines = content.split('\n')
        current_chunk = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for chunk markers
            if line.startswith('---') or line.startswith('###') or line.startswith('**'):
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = {"content": "", "metadata": {}}
            elif current_chunk is not None:
                current_chunk["content"] += line + "\n"
        
        # Add last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def _extract_sources(self, content: str) -> List[str]:
        """Extract sources from RAG content."""
        sources = []
        
        # Look for source markers
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Source:') or line.startswith('Reference:'):
                source = line.split(':', 1)[1].strip()
                if source:
                    sources.append(source)
        
        return sources

    def _enhance_messages_with_rag(
        self, messages: List[Dict[str, str]], rag_context: RAGContext
    ) -> List[Dict[str, str]]:
        """Enhance messages with RAG context."""
        enhanced_messages = messages.copy()
        
        # Create context summary
        context_summary = self._create_context_summary(rag_context)
        
        # Add system message with RAG context
        rag_system_message = {
            "role": "system",
            "content": f"""You have access to the following relevant information to help answer the user's question:

{context_summary}

Please use this information to provide accurate and helpful responses. If the information is relevant to the user's question, incorporate it into your answer. If the information is not relevant, you can ignore it and provide a general response.

Sources: {', '.join(rag_context.sources) if rag_context.sources else 'No specific sources available'}"""
        }
        
        # Insert RAG system message after the first system message (if any)
        insert_index = 0
        for i, message in enumerate(enhanced_messages):
            if message.get("role") == "system":
                insert_index = i + 1
                break
        
        enhanced_messages.insert(insert_index, rag_system_message)
        
        return enhanced_messages

    def _create_context_summary(self, rag_context: RAGContext) -> str:
        """Create a summary of the RAG context."""
        if not rag_context.chunks:
            return "No relevant information available."
        
        summary = "Relevant Information:\n\n"
        
        for i, chunk in enumerate(rag_context.chunks, 1):
            content = chunk.get("content", "").strip()
            if content:
                summary += f"{i}. {content}\n\n"
        
        return summary.strip()

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
                "sources_count": 0,
                "context_length": 0,
                "relevance_scores": [],
            }
        
        total_context_length = sum(
            len(chunk.get("content", "")) for chunk in rag_context.chunks
        )
        
        return {
            "chunks_retrieved": len(rag_context.chunks),
            "sources_count": len(rag_context.sources),
            "context_length": total_context_length,
            "relevance_scores": rag_context.relevance_scores,
        }