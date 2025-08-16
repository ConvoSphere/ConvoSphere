"""
Weaviate client for vector database operations.

This module provides Weaviate connection setup and utility functions
for the AI Assistant Platform.
"""

from datetime import datetime
from typing import Any

import os
import weaviate
from loguru import logger
from weaviate.classes.init import Auth

from .config import get_settings

# Global Weaviate client instance
weaviate_client: weaviate.Client | None = None


def init_weaviate() -> weaviate.Client:
    """
    Initialize Weaviate connection (v4).

    Returns:
        weaviate.Client: Weaviate client instance
    """
    global weaviate_client

    if os.getenv("TESTING") == "1":
        logger.info("TESTING=1: Skipping Weaviate initialization")
        # Create a lightweight stub object that has minimal methods used in code paths
        class _Stub:
            def is_ready(self) -> bool:  # type: ignore[override]
                return True

            def close(self) -> None:
                pass

            @property
            def collections(self):  # type: ignore[no-redef]
                class _Colls:
                    def get(self, _name):
                        class _Data:
                            def insert(self, **_kwargs):
                                return "stub-id"

                            def delete_by_id(self, _id):  # noqa: ARG002
                                return True

                        class _C:
                            data = _Data()

                            class query:  # noqa: N801
                                @staticmethod
                                def near_text(**_kwargs):
                                    class _R:
                                        objects = []

                                    return _R()

                        return _C()

                return _Colls()

        weaviate_client = _Stub()  # type: ignore[assignment]
        return weaviate_client  # type: ignore[return-value]

    try:
        # Create Weaviate client with proper configuration
        weaviate_url = get_settings().weaviate.weaviate_url
        # Parse URL properly
        host_port = weaviate_url.replace("http://", "").replace("https://", "")
        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                port = 8080
        else:
            host, port = host_port, 8080

        if get_settings().weaviate.weaviate_api_key:
            # Use v4 API with API key authentication
            weaviate_client = weaviate.connect_to_local(
                host=host,
                port=port,
                auth_credentials=Auth.api_key(get_settings().weaviate.weaviate_api_key),
            )
        else:
            # For local Weaviate without authentication
            weaviate_client = weaviate.connect_to_local(
                host=host,
                port=port,
            )

        # Test connection
        weaviate_client.is_ready()
        logger.info("Weaviate connection established successfully")

        return weaviate_client

    except Exception as e:
        logger.error(f"Failed to initialize Weaviate connection: {e}")
        raise


def get_weaviate() -> weaviate.Client:
    """
    Get Weaviate client instance.

    Returns:
        weaviate.Client: Weaviate client instance

    Raises:
        RuntimeError: If Weaviate is not initialized
    """
    if weaviate_client is None:
        raise RuntimeError(
            "Weaviate client not initialized. Call init_weaviate() first.",
        )
    return weaviate_client


def close_weaviate() -> None:
    """Close Weaviate connection."""
    global weaviate_client

    if weaviate_client:
        try:
            # Properly close the client connection
            weaviate_client.close()
        except Exception as e:
            logger.warning(f"Error closing Weaviate connection: {e}")
        finally:
            weaviate_client = None
            logger.info("Weaviate connection closed")


def check_weaviate_connection() -> bool:
    """
    Check Weaviate connection status.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_weaviate()
        return client.is_ready()
    except Exception as e:
        logger.error(f"Weaviate connection check failed: {e}")
        return False


def get_weaviate_info() -> dict[str, Any]:
    """
    Get Weaviate server information.

    Returns:
        dict: Weaviate server information
    """
    try:
        client = get_weaviate()
        # v4 meta retrieval can vary by client; provide a minimal stub
        return {"status": "connected" if check_weaviate_connection() else "disconnected"}
    except Exception as e:
        logger.error(f"Failed to get Weaviate info: {e}")
        return {"status": "error", "error": str(e)}


def create_schema_if_not_exists() -> None:
    """
    Create Weaviate schema if it doesn't exist.
    """
    try:
        get_weaviate()
        # Intentionally skip schema management here; assume collections managed elsewhere
        logger.info("Skipping Weaviate schema creation (managed externally)")
    except Exception as e:
        logger.error(f"Failed to create Weaviate schema: {e}")
        raise


def add_document(
    content: str,
    title: str,
    file_type: str,
    user_id: str,
    tags: list[str] | None = None,
    document_id: str | None = None,
) -> str:
    """
    Add document to Weaviate.

    Args:
        content: Document content
        title: Document title
        file_type: File type
        user_id: User ID
        tags: Document tags
        document_id: Optional document ID

    Returns:
        str: Document ID in Weaviate
    """
    try:
        client = get_weaviate()

        document_data = {
            "content": content,
            "title": title,
            "file_type": file_type,
            "user_id": user_id,
            "upload_date": datetime.utcnow().isoformat(),
            "tags": tags or [],
        }

        result = client.collections.get("Document").data.insert(
            properties=document_data,
            uuid=document_id,
        )

        logger.info(f"Document added to Weaviate with ID: {result}")
        return str(result)

    except Exception as e:
        logger.error(f"Failed to add document to Weaviate: {e}")
        raise


def search_documents(
    query: str,
    limit: int = 10,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search documents in Weaviate.

    Args:
        query: Search query
        limit: Maximum number of results
        user_id: Optional user ID filter

    Returns:
        List[Dict[str, Any]]: Search results
    """
    try:
        client = get_weaviate()
        coll = client.collections.get("Document")
        # For simplicity, perform near_text; Filter by user if provided
        filters = None
        if user_id:
            from weaviate.classes.query import Filter

            filters = Filter.by_property("user_id").equal(user_id)
        result = coll.query.near_text(query=query, limit=limit, filters=filters)

        items: list[dict[str, Any]] = []
        for o in getattr(result, "objects", []) or []:
            props = getattr(o, "properties", {}) or {}
            items.append(
                {
                    "content": props.get("content"),
                    "title": props.get("title"),
                    "file_type": props.get("file_type"),
                    "user_id": props.get("user_id"),
                    "tags": props.get("tags", []),
                    "upload_date": props.get("upload_date"),
                    "score": getattr(o, "metadata", {}).get("score")
                    if getattr(o, "metadata", None)
                    else None,
                }
            )
        return items

    except Exception as e:
        logger.error(f"Failed to search documents in Weaviate: {e}")
        return []


def delete_document(document_id: str) -> bool:
    """
    Delete document from Weaviate.

    Args:
        document_id: Document ID to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_weaviate()
        client.collections.get("Document").data.delete_by_id(document_id)
        logger.info(f"Document deleted from Weaviate: {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document from Weaviate: {e}")
        return False
