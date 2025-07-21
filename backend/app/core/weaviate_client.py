"""
Weaviate client for vector database operations.

This module provides Weaviate connection setup and utility functions
for the AI Assistant Platform.
"""

import weaviate
from typing import Optional, Dict, Any, List
from loguru import logger

from .config import settings

# Global Weaviate client instance
weaviate_client: Optional[weaviate.Client] = None


def init_weaviate() -> weaviate.Client:
    """
    Initialize Weaviate connection.
    
    Returns:
        weaviate.Client: Weaviate client instance
    """
    global weaviate_client
    
    try:
        # Create Weaviate client
        auth_config = None
        if settings.weaviate_api_key:
            auth_config = weaviate.Auth.api_key(settings.weaviate_api_key)
        
        weaviate_client = weaviate.Client(
            url=settings.weaviate_url,
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": settings.openai_api_key
            } if settings.openai_api_key else None,
            timeout_config=(5, 60),  # (connect_timeout, read_timeout)
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
        raise RuntimeError("Weaviate client not initialized. Call init_weaviate() first.")
    return weaviate_client


def close_weaviate() -> None:
    """Close Weaviate connection."""
    global weaviate_client
    
    if weaviate_client:
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


def get_weaviate_info() -> Dict[str, Any]:
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
        client = get_weaviate()
        
        # Define document schema
        document_schema = {
            "class": "Document",
            "description": "A document in the knowledge base",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "Document title"
                },
                {
                    "name": "file_type",
                    "dataType": ["string"],
                    "description": "File type (pdf, docx, etc.)"
                },
                {
                    "name": "user_id",
                    "dataType": ["string"],
                    "description": "User who uploaded the document"
                },
                {
                    "name": "upload_date",
                    "dataType": ["date"],
                    "description": "Upload date"
                },
                {
                    "name": "tags",
                    "dataType": ["text[]"],
                    "description": "Document tags"
                }
            ],
            "vectorizer": "text2vec-openai" if settings.openai_api_key else "none",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            } if settings.openai_api_key else {}
        }
        
        # Create schema if it doesn't exist
        try:
            client.schema.create_class(document_schema)
            logger.info("Weaviate Document schema created successfully")
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
    tags: Optional[List[str]] = None,
    document_id: Optional[str] = None
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
            "tags": tags or []
        }
        
        result = client.data_object.create(
            data_object=document_data,
            class_name="Document",
            uuid=document_id
        )
        
        logger.info(f"Document added to Weaviate with ID: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to add document to Weaviate: {e}")
        raise


def search_documents(
    query: str,
    limit: int = 10,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
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
            "limit": limit
        }
        
        # Add user filter if provided
        if user_id:
            search_query["where"] = {
                "path": ["user_id"],
                "operator": "Equal",
                "valueString": user_id
            }
        
        # Add vector search if OpenAI is configured
        if settings.openai_api_key:
            search_query["nearText"] = {
                "concepts": [query]
            }
        else:
            # Fallback to BM25 search
            search_query["bm25"] = {
                "query": query
            }
        
        result = client.query.get("Document", [
            "content", "title", "file_type", "user_id", "tags", "upload_date"
        ]).with_near_text({
            "concepts": [query]
        }).with_limit(limit).do()
        
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
        client.data_object.delete(document_id, class_name="Document")
        logger.info(f"Document deleted from Weaviate: {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document from Weaviate: {e}")
        return False 