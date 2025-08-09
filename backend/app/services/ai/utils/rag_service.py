"""RAG (Retrieval-Augmented Generation) service utility."""

import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_service import KnowledgeService
from app.services.ai.providers.base import ChatMessage


class RAGService:
    """RAG service for knowledge base integration."""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
        self.knowledge_service = KnowledgeService(db)
    
    async def get_relevant_context(
        self,
        query: str,
        user_id: str,
        max_chunks: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get relevant context from knowledge base."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embeddings([query])
            if not query_embedding:
                return []
            
            # Search for similar documents
            similar_chunks = await self.knowledge_service.search_similar_chunks(
                query_embedding[0],
                user_id=user_id,
                limit=max_chunks,
                similarity_threshold=similarity_threshold
            )
            
            return similar_chunks
            
        except Exception as e:
            raise Exception(f"Failed to get relevant context: {str(e)}")
    
    def format_context_for_prompt(
        self,
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """Format context chunks for inclusion in prompt."""
        if not context_chunks:
            return ""
        
        formatted_context = "Relevant information from knowledge base:\n\n"
        
        for i, chunk in enumerate(context_chunks, 1):
            formatted_context += f"{i}. {chunk.get('content', '')}\n"
            if chunk.get('source'):
                formatted_context += f"   Source: {chunk['source']}\n"
            formatted_context += "\n"
        
        return formatted_context
    
    async def create_rag_prompt(
        self,
        user_message: str,
        user_id: str,
        max_context_chunks: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[ChatMessage]:
        """Create a RAG-enhanced prompt."""
        try:
            # Get relevant context
            context_chunks = await self.get_relevant_context(
                user_message,
                user_id,
                max_chunks=max_context_chunks,
                similarity_threshold=similarity_threshold
            )
            
            # Format context
            context_text = self.format_context_for_prompt(context_chunks)
            
            # Create system message with context
            system_message = """You are a helpful AI assistant. Use the provided context to answer questions accurately and comprehensively. If the context doesn't contain relevant information, say so and provide a general helpful response.

When using information from the context, cite the source if available."""
            
            if context_text:
                system_message += f"\n\n{context_text}"
            
            # Create messages
            messages = [
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=user_message)
            ]
            
            return messages
            
        except Exception as e:
            raise Exception(f"Failed to create RAG prompt: {str(e)}")
    
    async def process_rag_response(
        self,
        response: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process RAG response and add metadata."""
        return {
            "response": response,
            "context_used": len(context_chunks),
            "sources": [chunk.get("source") for chunk in context_chunks if chunk.get("source")],
            "confidence_score": self._calculate_confidence_score(context_chunks)
        }
    
    def _calculate_confidence_score(
        self,
        context_chunks: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score based on context relevance."""
        if not context_chunks:
            return 0.0
        
        # Calculate average similarity score
        total_score = sum(chunk.get("similarity", 0.0) for chunk in context_chunks)
        avg_score = total_score / len(context_chunks)
        
        # Normalize to 0-1 range
        return min(avg_score, 1.0)
    
    async def update_knowledge_base(
        self,
        user_id: str,
        content: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update knowledge base with new content."""
        try:
            # Add document to knowledge base
            document = await self.knowledge_service.add_document(
                content=content,
                user_id=user_id,
                source=source,
                metadata=metadata
            )
            
            return {
                "success": True,
                "document_id": document.id,
                "chunks_created": len(document.chunks) if document.chunks else 0
            }
            
        except Exception as e:
            raise Exception(f"Failed to update knowledge base: {str(e)}")
    
    async def get_knowledge_stats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            stats = await self.knowledge_service.get_user_stats(user_id)
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to get knowledge stats: {str(e)}")