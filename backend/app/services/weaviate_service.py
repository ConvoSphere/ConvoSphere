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
from weaviate.classes.init import Auth


class WeaviateService:
    """Service for Weaviate semantic search and RAG."""

    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        self.client = self._init_client()

    def _init_client(self):
        try:
            # Parse URL to extract host and port
            if self.url.startswith("http://"):
                host = self.url[7:]  # Remove "http://"
            elif self.url.startswith("https://"):
                host = self.url[8:]  # Remove "https://"
            else:
                host = self.url

            # Extract host and port
            if ":" in host:
                host, port_str = host.split(":", 1)
                port = int(port_str)
            else:
                port = 8080

            # Create auth credentials if API key is provided
            auth_credentials = None
            if self.api_key:
                auth_credentials = Auth.api_key(self.api_key)

            # Use v4 API to connect to Weaviate
            client = weaviate.connect_to_custom(
                http_host=host,
                http_port=port,
                http_secure=False,
                grpc_host=host,
                grpc_port=50051,
                grpc_secure=False,
                auth_credentials=auth_credentials,
            )

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
            if not self.client:
                logger.warning("Weaviate client not available")
                return

            obj = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "content": content,
                "role": role,
                "metadata": metadata or {},
            }

            # Use v4 API for data insertion
            self.client.data.insert(obj, collection_name="ChatMessage")
            logger.info(f"Indexed message {message_id} in Weaviate")
        except Exception as e:
            logger.error(f"Failed to index message: {e}")

    def semantic_search_messages(
        self,
        query: str,
        conversation_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in chat messages."""
        try:
            if not self.client:
                logger.warning("Weaviate client not available")
                return []

            # Build query using v4 API
            query_builder = (
                self.client.query.get(
                    "ChatMessage",
                    ["message_id", "content", "role", "conversation_id", "metadata"],
                )
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
            )

            # Add filter if conversation_id is provided
            if conversation_id:
                query_builder = query_builder.with_where(
                    {
                        "path": ["conversation_id"],
                        "operator": "Equal",
                        "valueString": conversation_id,
                    },
                )

            result = query_builder.do()
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
            if not self.client:
                logger.warning("Weaviate client not available")
                return

            obj = {
                "doc_id": doc_id,
                "content": content,
                "source": source,
                "metadata": metadata or {},
            }

            # Use v4 API for data insertion
            self.client.data.insert(obj, collection_name="Knowledge")
            logger.info(f"Indexed knowledge doc {doc_id} in Weaviate")
        except Exception as e:
            logger.error(f"Failed to index knowledge: {e}")

    def semantic_search_knowledge(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in knowledge base."""
        try:
            if not self.client:
                logger.warning("Weaviate client not available")
                return []

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
