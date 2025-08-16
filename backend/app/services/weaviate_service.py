"""
Weaviate service for semantic search and RAG.

This module provides integration with Weaviate for:
- Semantic search in chat conversations
- Retrieval-Augmented Generation (RAG) for external knowledge
"""

import logging
import os
from typing import Any

from loguru import logger
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for Weaviate semantic search and RAG."""

    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        self.client = self._init_client()

    def _parse_host_port(self) -> tuple[str, int]:
        url = self.url
        host_port = url.replace("http://", "").replace("https://", "")
        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                port = 8080
        else:
            host, port = host_port, 8080
        return host, port

    def _init_client(self) -> weaviate.Client | None:
        """Initialize Weaviate v4 client."""
        try:
            # Avoid network initialization in tests
            if os.getenv("TESTING") == "1":
                logger.info("TESTING=1: Skipping Weaviate client initialization")
                return None

            host, port = self._parse_host_port()
            if self.api_key:
                client = weaviate.connect_to_local(
                    host=host,
                    port=port,
                    auth_credentials=Auth.api_key(self.api_key),
                )
            else:
                client = weaviate.connect_to_local(host=host, port=port)

            # Probe readiness
            client.is_ready()
            logger.info(f"Connected to Weaviate at {self.url}")
            return client
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Failed to connect to Weaviate (connection error): {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to connect to Weaviate (invalid configuration): {e}")
            return None
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to connect to Weaviate (unexpected error): {e}")
            return None

    def health(self) -> bool:
        """Check Weaviate health."""
        try:
            return self.client.is_ready() if self.client else False
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Weaviate health check failed (connection error): {e}")
            return False
        except Exception as e:  # noqa: BLE001
            logger.error(f"Weaviate health check failed (unexpected error): {e}")
            return False

    def index_message(
        self,
        conversation_id: str,
        message_id: str,
        content: str,
        role: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Index a chat message in Weaviate (v4)."""
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

            self.client.collections.get("ChatMessage").data.insert(
                properties=obj,
                uuid=message_id,
            )
            logger.info(f"Indexed message {message_id} in Weaviate")
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Failed to index message (connection error): {e}")
        except ValueError as e:
            logger.error(f"Failed to index message (invalid data): {e}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to index message (unexpected error): {e}")

    def semantic_search_messages(
        self,
        query: str,
        conversation_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in chat messages (v4)."""
        try:
            if not self.client:
                logger.warning("Weaviate client not available")
                return []

            coll = self.client.collections.get("ChatMessage")
            weaviate_filter = (
                Filter.by_property("conversation_id").equal(conversation_id)
                if conversation_id
                else None
            )
            result = coll.query.near_text(
                query=query,
                limit=limit,
                filters=weaviate_filter,
            )

            items: list[dict[str, Any]] = []
            for o in getattr(result, "objects", []) or []:
                props = getattr(o, "properties", {}) or {}
                items.append(
                    {
                        "message_id": props.get("message_id"),
                        "content": props.get("content"),
                        "role": props.get("role"),
                        "conversation_id": props.get("conversation_id"),
                        "metadata": props.get("metadata", {}),
                        "score": getattr(o, "metadata", {}).get("score")
                        if getattr(o, "metadata", None)
                        else None,
                    }
                )
            return items
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Semantic search failed (connection error): {e}")
            return []
        except ValueError as e:
            logger.error(f"Semantic search failed (invalid query): {e}")
            return []
        except Exception as e:  # noqa: BLE001
            logger.error(f"Semantic search failed (unexpected error): {e}")
            return []

    def index_knowledge(
        self,
        doc_id: str,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Index a knowledge document in Weaviate (v4)."""
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

            self.client.collections.get("Knowledge").data.insert(
                properties=obj,
                uuid=doc_id,
            )
            logger.info(f"Indexed knowledge doc {doc_id} in Weaviate")
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Failed to index knowledge (connection error): {e}")
        except ValueError as e:
            logger.error(f"Failed to index knowledge (invalid data): {e}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to index knowledge (unexpected error): {e}")

    def semantic_search_knowledge(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in knowledge documents (v4)."""
        try:
            if not self.client:
                logger.warning("Weaviate client not available")
                return []

            coll = self.client.collections.get("Knowledge")
            result = coll.query.near_text(query=query, limit=limit)

            items: list[dict[str, Any]] = []
            for o in getattr(result, "objects", []) or []:
                props = getattr(o, "properties", {}) or {}
                items.append(
                    {
                        "doc_id": props.get("doc_id"),
                        "content": props.get("content"),
                        "source": props.get("source"),
                        "metadata": props.get("metadata", {}),
                        "score": getattr(o, "metadata", {}).get("score")
                        if getattr(o, "metadata", None)
                        else None,
                    }
                )
            return items
        except (ConnectionError, TimeoutError) as e:  # noqa: PT011
            logger.error(f"Knowledge search failed (connection error): {e}")
            return []
        except ValueError as e:
            logger.error(f"Knowledge search failed (invalid query): {e}")
            return []
        except Exception as e:  # noqa: BLE001
            logger.error(f"Knowledge search failed (unexpected error): {e}")
            return []


# Global Weaviate service instance (safe for tests due to TESTING guard)
weaviate_service = WeaviateService()
