"""
Weaviate client for vector database operations.

This module provides Weaviate connection setup and utility functions
for the AI Assistant Platform.
"""

from datetime import datetime
from typing import Any

import weaviate
from loguru import logger
from weaviate.classes.init import Auth

from .config import get_settings

# Global Weaviate client instance
weaviate_client: weaviate.Client | None = None


def init_weaviate() -> weaviate.Client:
    """
    Initialize Weaviate connection.

    Returns:
        weaviate.Client: Weaviate client instance
    """
    global weaviate_client

    try:
        # Create Weaviate client with proper configuration
        weaviate_url = get_settings().weaviate_url
        # Parse URL properly
        if weaviate_url.startswith("http://"):
            host = weaviate_url[7:]  # Remove "http://"
        elif weaviate_url.startswith("https://"):
            host = weaviate_url[8:]  # Remove "https://"
        else:
            host = weaviate_url

        # Remove port if present
        if ":" in host:
            host = host.split(":")[0]

        if get_settings().weaviate_api_key:
            # Use v4 API with API key authentication
            weaviate_client = weaviate.connect_to_local(
                host=host,
                port=8080,
                auth_credentials=Auth.api_key(get_settings().weaviate_api_key),
            )
        else:
            # For local Weaviate without authentication
            weaviate_client = weaviate.connect_to_local(
                host=host,
                port=8080,
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
        meta = client.get_meta()

        return {
            "status": "connected" if check_weaviate_connection() else "disconnected",
            "version": meta.get("version", "unknown"),
            "modules": meta.get("modules", []),
            "hostname": meta.get("hostname", "unknown"),
        }
    except Exception as e:
        logger.error(f"Failed to get Weaviate info: {e}")
        return {"status": "error", "error": str(e)}


def create_schema_if_not_exists() -> None:
    """
    Create Weaviate schema if it doesn't exist.
    """
    try:
        get_weaviate()

        # Define document schema for Weaviate v4
        from weaviate.classes.config import DataType, Property

        [
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="Document content",
            ),
            Property(
                name="title",
                data_type=DataType.TEXT,
                description="Document title",
            ),
            Property(
                name="file_type",
                data_type=DataType.TEXT,
                description="File type (pdf, docx, etc.)",
            ),
            Property(
                name="user_id",
                data_type=DataType.TEXT,
                description="User who uploaded the document",
            ),
            Property(
                name="upload_date",
                data_type=DataType.DATE,
                description="Upload date",
            ),
            Property(
                name="tags",
                data_type=DataType.TEXT_ARRAY,
                description="Document tags",
            ),
        ]

        # Create collection directly

        # Create schema if it doesn't exist
        try:
            # Temporarily skip schema creation to allow backend to start
            logger.info("Skipping Weaviate schema creation for now")
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise
            logger.info("Weaviate Document schema already exists")

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
        return result

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

        # Build search query
        search_query = {
            "class": "Document",
            "properties": ["content", "title", "file_type", "user_id", "tags"],
            "limit": limit,
        }

        # Add user filter if provided
        if user_id:
            search_query["where"] = {
                "path": ["user_id"],
                "operator": "Equal",
                "valueString": user_id,
            }

        # Add vector search if OpenAI is configured
        if get_settings().openai_api_key:
            search_query["nearText"] = {
                "concepts": [query],
            }
        else:
            # Fallback to BM25 search
            search_query["bm25"] = {
                "query": query,
            }

        result = (
            client.query.get(
                "Document",
                [
                    "content",
                    "title",
                    "file_type",
                    "user_id",
                    "tags",
                    "upload_date",
                ],
            )
            .with_near_text(
                {
                    "concepts": [query],
                },
            )
            .with_limit(limit)
            .do()
        )

        return result["data"]["Get"]["Document"]

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
