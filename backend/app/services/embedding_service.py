"""
Embedding service for generating vector embeddings.

This module provides functionality for generating embeddings from text chunks
using various embedding models and managing embedding operations.
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio

from litellm import completion
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings."""
    
    def __init__(self):
        self.model = settings.default_embedding_model
        self.batch_size = 10  # Process embeddings in batches
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                # Generate embeddings for batch
                batch_embeddings = await self._generate_batch_embeddings(batch)
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Use LiteLLM for embedding generation
            response = await completion(
                model=self.model,
                messages=[{"role": "user", "content": text} for text in texts],
                temperature=0,
                max_tokens=1,  # We only need embeddings, not completions
                embedding=True
            )
            
            if hasattr(response, 'embeddings') and response.embeddings:
                return response.embeddings
            else:
                logger.warning("No embeddings returned from model")
                return []
                
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return []
    
    async def generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector or None
        """
        try:
            embeddings = await self.generate_embeddings([text])
            return embeddings[0] if embeddings else None
            
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar embeddings to query embedding.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
            
        Returns:
            List of results with index and similarity score
        """
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append({
                    'index': i,
                    'similarity': similarity
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top_k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding most similar embeddings: {e}")
            return []
    
    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of text chunks with content
            
        Returns:
            List of chunks with embeddings added
        """
        try:
            if not chunks:
                return []
            
            # Extract text content
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = await self.generate_embeddings(texts)
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                if i < len(embeddings):
                    chunk['embedding'] = embeddings[i]
                else:
                    chunk['embedding'] = None
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            return chunks
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate embedding vector.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not embedding:
                return False
            
            # Check if it's a list of numbers
            if not all(isinstance(x, (int, float)) for x in embedding):
                return False
            
            # Check if it's not all zeros
            if all(x == 0 for x in embedding):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating embedding: {e}")
            return False
    
    def get_embedding_dimension(self, embedding: List[float]) -> int:
        """
        Get dimension of embedding vector.
        
        Args:
            embedding: Embedding vector
            
        Returns:
            Dimension of the embedding
        """
        try:
            return len(embedding) if embedding else 0
        except Exception as e:
            logger.error(f"Error getting embedding dimension: {e}")
            return 0


# Global embedding service instance
embedding_service = EmbeddingService() 