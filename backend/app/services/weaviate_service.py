"""
Weaviate service for semantic search and RAG.

This module provides integration with Weaviate for:
- Semantic search in chat conversations
- Retrieval-Augmented Generation (RAG) for external knowledge
"""

import os
from typing import Any

import weaviate
from loguru import logger


class WeaviateService:
    """Service for Weaviate semantic search and RAG."""

    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8081")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        self.client = self._init_client()

    def _init_client(self):
        try:
            auth = weaviate.AuthApiKey(api_key=self.api_key) if self.api_key else None
            client = weaviate.Client(self.url, auth_client_secret=auth) if auth else weaviate.Client(self.url)
            logger.info(f"Connected to Weaviate at {self.url}")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            return None

    def health(self) -> bool:
        """Check Weaviate health."""
        try:
            return self.client.is_ready() if self.client else False
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            return False

    def index_message(
        self,
        conversation_id: str,
        message_id: str,
        content: str,
        role: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Index a chat message in Weaviate."""
        try:
            obj = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "content": content,
                "role": role,
                "metadata": metadata or {},
            }
            self.client.data_object.create(obj, class_name="ChatMessage")
            logger.info(f"Indexed message {message_id} in Weaviate")
        except Exception as e:
            logger.error(f"Failed to index message: {e}")

    def semantic_search_messages(
        self, query: str, conversation_id: str | None = None, limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in chat messages."""
        try:
            filters = None
            if conversation_id:
                filters = {
                    "path": ["conversation_id"],
                    "operator": "Equal",
                    "valueString": conversation_id,
                }
            result = (
                self.client.query.get(
                    "ChatMessage",
                    ["message_id", "content", "role", "conversation_id", "metadata"],
                )
                .with_near_text({"concepts": [query]})
                .with_where(filters)
                .with_limit(limit)
                .do()
            )
            return result["data"]["Get"]["ChatMessage"]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def index_knowledge(
        self,
        doc_id: str,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Index a knowledge document in Weaviate."""
        try:
            obj = {
                "doc_id": doc_id,
                "content": content,
                "source": source,
                "metadata": metadata or {},
            }
            self.client.data_object.create(obj, class_name="Knowledge")
            logger.info(f"Indexed knowledge doc {doc_id} in Weaviate")
        except Exception as e:
            logger.error(f"Failed to index knowledge: {e}")

    def semantic_search_knowledge(
        self, query: str, limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in knowledge base."""
        try:
            result = (
                self.client.query.get(
                    "Knowledge",
                    ["doc_id", "content", "source", "metadata"],
                )
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .do()
            )
            return result["data"]["Get"]["Knowledge"]
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []


# Global Weaviate service instance
weaviate_service = WeaviateService()
