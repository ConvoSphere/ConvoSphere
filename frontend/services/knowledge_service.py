"""
Knowledge service for frontend.

This module provides a service layer for knowledge base operations
including document management, search, and RAG functionality.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.api import api_client


class KnowledgeService:
    """Service for knowledge base operations."""
    
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.is_loading = False
        self.search_results: List[Dict[str, Any]] = []
        self.is_searching = False
    
    async def load_documents(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Load documents from knowledge base.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        try:
            self.is_loading = True
            response = await api_client.get_documents(skip=skip, limit=limit)
            
            if response.success and response.data:
                self.documents = response.data
                return self.documents
            else:
                return []
                
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []
        finally:
            self.is_loading = False
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None
        """
        try:
            response = await api_client.get_document(document_id)
            
            if response.success and response.data:
                return response.data
            else:
                return None
                
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    async def upload_document(self, file_data: Dict[str, Any], metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Upload document to knowledge base.
        
        Args:
            file_data: File data
            metadata: Document metadata
            
        Returns:
            Uploaded document data or None
        """
        try:
            response = await api_client.upload_document(file_data, metadata)
            
            if response.success and response.data:
                # Add to local documents list
                self.documents.append(response.data)
                return response.data
            else:
                return None
                
        except Exception as e:
            print(f"Error uploading document: {e}")
            return None
    
    async def upload_document_advanced(
        self, 
        file_data: Dict[str, Any], 
        metadata: Dict[str, Any],
        engine: str = "auto",
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload document with advanced processing options.
        
        Args:
            file_data: File data
            metadata: Document metadata
            engine: Processing engine (auto, traditional, docling)
            processing_options: Engine-specific options
            
        Returns:
            Uploaded document data or None
        """
        try:
            # Add processing options to metadata
            if processing_options:
                metadata['processing_options'] = processing_options
            metadata['engine'] = engine
            
            response = await api_client._make_request(
                "POST",
                "/api/v1/knowledge/documents/upload-advanced",
                data={
                    "file": file_data,
                    "metadata": metadata,
                    "engine": engine,
                    "processing_options": processing_options
                }
            )
            
            if response.success and response.data:
                # Add to local documents list
                self.documents.append(response.data)
                return response.data
            else:
                return None
                
        except Exception as e:
            print(f"Error uploading document with advanced options: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from knowledge base.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_document(document_id)
            
            if response.success:
                # Remove from local documents list
                self.documents = [doc for doc in self.documents if doc.get("id") != document_id]
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def download_document(self, document_id: str) -> Optional[bytes]:
        """
        Download document content.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document content as bytes or None
        """
        try:
            response = await api_client.download_document(document_id)
            
            if response.success and response.data:
                return response.data
            else:
                return None
                
        except Exception as e:
            print(f"Error downloading document: {e}")
            return None
    
    async def process_document(self, document_id: str) -> bool:
        """
        Process document for embedding.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.process_document(document_id)
            
            if response.success:
                # Update document status in local list
                for doc in self.documents:
                    if doc.get("id") == document_id:
                        doc["status"] = "processed"
                        doc["updated_at"] = datetime.now().isoformat()
                        break
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error processing document: {e}")
            return False
    
    async def reprocess_document(
        self, 
        document_id: str, 
        engine: str = "auto",
        processing_options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Reprocess document with specific options.
        
        Args:
            document_id: Document ID
            engine: Processing engine
            processing_options: Engine-specific options
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client._make_request(
                "POST",
                f"/api/v1/knowledge/documents/{document_id}/reprocess",
                data={
                    "processing_options": {
                        "engine": engine,
                        "options": processing_options or {}
                    }
                }
            )
            
            if response.success:
                # Update document metadata in local list
                for doc in self.documents:
                    if doc.get("id") == document_id:
                        doc["metadata"].update(response.data.get("metadata", {}))
                        doc["updated_at"] = datetime.now().isoformat()
                        break
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error reprocessing document: {e}")
            return False
    
    async def get_processing_engines(self) -> Dict[str, Any]:
        """
        Get available processing engines.
        
        Returns:
            Dictionary of available engines
        """
        try:
            response = await api_client._make_request(
                "GET",
                "/api/v1/knowledge/processing/engines"
            )
            
            if response.success and response.data:
                return response.data
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting processing engines: {e}")
            return {}
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """
        Get supported document formats.
        
        Returns:
            Dictionary of supported formats
        """
        try:
            response = await api_client._make_request(
                "GET",
                "/api/v1/knowledge/processing/supported-formats"
            )
            
            if response.success and response.data:
                return response.data
            else:
                return {"all_formats": [], "by_engine": {}}
                
        except Exception as e:
            print(f"Error getting supported formats: {e}")
            return {"all_formats": [], "by_engine": {}}
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            self.is_searching = True
            response = await api_client.search_knowledge(query, limit=limit)
            
            if response.success and response.data:
                self.search_results = response.data
                return self.search_results
            else:
                return []
                
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
        finally:
            self.is_searching = False
    
    async def search_conversations(self, query: str, conversation_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversations semantically.
        
        Args:
            query: Search query
            conversation_id: Optional conversation ID to limit search
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            response = await api_client.search_conversations(query, conversation_id, limit)
            
            if response.success and response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document from local cache by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None
        """
        for doc in self.documents:
            if doc.get("id") == document_id:
                return doc
        return None
    
    def filter_documents(self, status: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Filter documents by status and tags.
        
        Args:
            status: Document status filter
            tags: List of tags to filter by
            
        Returns:
            Filtered list of documents
        """
        filtered = self.documents
        
        if status:
            filtered = [doc for doc in filtered if doc.get("status") == status]
        
        if tags:
            filtered = [doc for doc in filtered if any(tag in doc.get("tags", []) for tag in tags)]
        
        return filtered
    
    def get_documents_by_engine(self, engine: str) -> List[Dict[str, Any]]:
        """
        Get documents processed by specific engine.
        
        Args:
            engine: Processing engine name
            
        Returns:
            List of documents processed by the engine
        """
        return [
            doc for doc in self.documents 
            if doc.get("metadata", {}).get("processing_engine") == engine
        ]
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """
        Get document statistics.
        
        Returns:
            Dictionary with document statistics
        """
        if not self.documents:
            return {
                "total_documents": 0,
                "processed_documents": 0,
                "processing_documents": 0,
                "error_documents": 0,
                "processing_engines": {},
                "file_types": {}
            }
        
        stats = {
            "total_documents": len(self.documents),
            "processed_documents": len([d for d in self.documents if d.get("status") == "processed"]),
            "processing_documents": len([d for d in self.documents if d.get("status") == "processing"]),
            "error_documents": len([d for d in self.documents if d.get("status") == "error"]),
            "processing_engines": {},
            "file_types": {}
        }
        
        # Count by processing engine
        for doc in self.documents:
            engine = doc.get("metadata", {}).get("processing_engine", "unknown")
            stats["processing_engines"][engine] = stats["processing_engines"].get(engine, 0) + 1
            
            file_type = doc.get("file_type", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
        
        return stats
    
    def clear_search_results(self):
        """Clear search results."""
        self.search_results = []
        self.is_searching = False


# Global knowledge service instance
knowledge_service = KnowledgeService() 