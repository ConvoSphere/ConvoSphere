"""
Knowledge service for the AI Assistant Platform.

This module provides comprehensive knowledge base functionality including
document management, search, processing, and embedding integration.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from utils.helpers import format_file_size, generate_id
from utils.validators import validate_document_data

from .api import api_client
from .error_handler import handle_api_error, handle_network_error


class DocumentStatus(Enum):
    """Document processing status enumeration."""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentType(Enum):
    """Document type enumeration."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class DocumentChunk:
    """Document chunk data model."""

    id: str
    document_id: str
    content: str
    chunk_index: int
    start_position: int
    end_position: int
    embedding_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class Document:
    """Document data model."""

    id: str
    name: str
    filename: str
    file_type: DocumentType
    file_size: int
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: datetime | None = None
    chunks: list[DocumentChunk] | None = None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None
    category: str | None = None
    description: str | None = None
    version: str = "1.0.0"


@dataclass
class SearchResult:
    """Search result data model."""

    document_id: str
    document_name: str
    chunk_id: str
    content: str
    score: float
    chunk_index: int
    start_position: int
    end_position: int
    metadata: dict[str, Any] | None = None


class KnowledgeService:
    """Service for knowledge base management and search."""

    def __init__(self):
        """Initialize the knowledge service."""
        self.documents: list[Document] = []
        self.search_results: list[SearchResult] = []
        self.is_loading = False
        self.upload_progress: dict[str, float] = {}

    async def get_documents(self, force_refresh: bool = False) -> list[Document]:
        """
        Get all documents.

        Args:
            force_refresh: Force refresh from API

        Returns:
            List of documents
        """
        if not force_refresh and self.documents:
            return self.documents

        self.is_loading = True

        try:
            response = await api_client.get_documents()

            if response.success and response.data:
                self.documents = [
                    self._create_document_from_data(doc_data)
                    for doc_data in response.data
                ]
            else:
                handle_api_error(response, "Laden der Dokumente")
                return []

            return self.documents

        except Exception as e:
            handle_network_error(e, "Laden der Dokumente")
            return []
        finally:
            self.is_loading = False

    async def get_document(self, document_id: str) -> Document | None:
        """
        Get specific document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document or None if not found
        """
        try:
            response = await api_client.get_document(document_id)

            if response.success and response.data:
                return self._create_document_from_data(response.data)
            handle_api_error(response, f"Laden des Dokuments {document_id}")
            return None

        except Exception as e:
            handle_network_error(e, f"Laden des Dokuments {document_id}")
            return None

    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        file_type: str,
        category: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
        on_progress: callable | None = None,
    ) -> Document | None:
        """
        Upload a document.

        Args:
            file_data: File content as bytes
            filename: Name of the file
            file_type: MIME type of the file
            category: Document category
            tags: Document tags
            description: Document description
            on_progress: Progress callback function

        Returns:
            Uploaded document or None if failed
        """
        try:
            # Create document data
            document_data = {
                "filename": filename,
                "file_type": file_type,
                "file_size": len(file_data),
                "category": category,
                "tags": tags or [],
                "description": description,
            }

            # Validate document data
            validation = validate_document_data(document_data)
            if not validation["valid"]:
                raise ValueError(f"Document validation failed: {validation['errors']}")

            # Upload document
            response = await api_client.upload_document(
                file_data,
                filename,
                file_type,
                document_data,
                on_progress=on_progress,
            )

            if response.success and response.data:
                document = self._create_document_from_data(response.data)
                self.documents.append(document)
                return document
            handle_api_error(response, "Hochladen des Dokuments")
            return None

        except Exception as e:
            handle_network_error(e, "Hochladen des Dokuments")
            return None

    async def update_document(
        self, document_id: str, document_data: dict[str, Any],
    ) -> Document | None:
        """
        Update document metadata.

        Args:
            document_id: Document ID
            document_data: Updated document data

        Returns:
            Updated document or None if failed
        """
        try:
            response = await api_client.update_document(document_id, document_data)

            if response.success and response.data:
                document = self._create_document_from_data(response.data)

                # Update in local list
                for i, existing_doc in enumerate(self.documents):
                    if existing_doc.id == document_id:
                        self.documents[i] = document
                        break

                return document
            handle_api_error(response, f"Aktualisieren des Dokuments {document_id}")
            return None

        except Exception as e:
            handle_network_error(e, f"Aktualisieren des Dokuments {document_id}")
            return None

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.

        Args:
            document_id: Document ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_document(document_id)

            if response.success:
                # Remove from local list
                self.documents = [d for d in self.documents if d.id != document_id]
                return True
            handle_api_error(response, f"Löschen des Dokuments {document_id}")
            return False

        except Exception as e:
            handle_network_error(e, f"Löschen des Dokuments {document_id}")
            return False

    async def search_documents(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> list[SearchResult]:
        """
        Search documents.

        Args:
            query: Search query
            filters: Search filters
            limit: Maximum number of results

        Returns:
            List of search results
        """
        try:
            search_data = {
                "query": query,
                "filters": filters or {},
                "limit": limit,
            }

            response = await api_client.search_documents(search_data)

            if response.success and response.data:
                self.search_results = [
                    self._create_search_result_from_data(result_data)
                    for result_data in response.data
                ]
                return self.search_results
            handle_api_error(response, "Dokumentensuche")
            return []

        except Exception as e:
            handle_network_error(e, "Dokumentensuche")
            return []

    async def get_document_chunks(self, document_id: str) -> list[DocumentChunk]:
        """
        Get document chunks.

        Args:
            document_id: Document ID

        Returns:
            List of document chunks
        """
        try:
            response = await api_client.get_document_chunks(document_id)

            if response.success and response.data:
                return [
                    self._create_chunk_from_data(chunk_data)
                    for chunk_data in response.data
                ]
            handle_api_error(response, f"Laden der Dokument-Chunks {document_id}")
            return []

        except Exception as e:
            handle_network_error(e, f"Laden der Dokument-Chunks {document_id}")
            return []

    async def reprocess_document(self, document_id: str) -> bool:
        """
        Reprocess a document.

        Args:
            document_id: Document ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.reprocess_document(document_id)

            if response.success:
                # Update document status
                for doc in self.documents:
                    if doc.id == document_id:
                        doc.status = DocumentStatus.PROCESSING
                        doc.processed_at = None
                        break

                return True
            handle_api_error(response, f"Neuverarbeitung des Dokuments {document_id}")
            return False

        except Exception as e:
            handle_network_error(e, f"Neuverarbeitung des Dokuments {document_id}")
            return False

    def get_documents_by_category(self, category: str) -> list[Document]:
        """
        Get documents by category.

        Args:
            category: Category to filter by

        Returns:
            List of documents in category
        """
        return [d for d in self.documents if d.category == category]

    def get_documents_by_status(self, status: DocumentStatus) -> list[Document]:
        """
        Get documents by status.

        Args:
            status: Status to filter by

        Returns:
            List of documents with specified status
        """
        return [d for d in self.documents if d.status == status]

    def get_documents_by_type(self, doc_type: DocumentType) -> list[Document]:
        """
        Get documents by type.

        Args:
            doc_type: Document type to filter by

        Returns:
            List of documents of specified type
        """
        return [d for d in self.documents if d.file_type == doc_type]

    def search_documents_local(self, query: str) -> list[Document]:
        """
        Search documents locally by name and description.

        Args:
            query: Search query

        Returns:
            List of matching documents
        """
        query_lower = query.lower()
        return [
            d
            for d in self.documents
            if query_lower in d.name.lower()
            or (d.description and query_lower in d.description.lower())
        ]

    def get_document_categories(self) -> list[str]:
        """
        Get all document categories.

        Returns:
            List of unique categories
        """
        return list(set(d.category for d in self.documents if d.category))

    def get_document_stats(self) -> dict[str, Any]:
        """
        Get document statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self.documents)
        completed = len(self.get_documents_by_status(DocumentStatus.COMPLETED))
        processing = len(self.get_documents_by_status(DocumentStatus.PROCESSING))
        failed = len(self.get_documents_by_status(DocumentStatus.FAILED))

        categories = self.get_document_categories()
        type_counts = {}
        for doc_type in DocumentType:
            type_counts[doc_type.value] = len(self.get_documents_by_type(doc_type))

        total_size = sum(d.file_size for d in self.documents)

        return {
            "total_documents": total,
            "completed_documents": completed,
            "processing_documents": processing,
            "failed_documents": failed,
            "categories": categories,
            "category_count": len(categories),
            "type_counts": type_counts,
            "total_size": total_size,
            "total_size_formatted": format_file_size(total_size),
        }

    def get_upload_progress(self, document_id: str) -> float:
        """
        Get upload progress for a document.

        Args:
            document_id: Document ID

        Returns:
            Upload progress (0.0 to 1.0)
        """
        return self.upload_progress.get(document_id, 0.0)

    def set_upload_progress(self, document_id: str, progress: float):
        """
        Set upload progress for a document.

        Args:
            document_id: Document ID
            progress: Upload progress (0.0 to 1.0)
        """
        self.upload_progress[document_id] = max(0.0, min(1.0, progress))

    def clear_upload_progress(self, document_id: str):
        """
        Clear upload progress for a document.

        Args:
            document_id: Document ID
        """
        if document_id in self.upload_progress:
            del self.upload_progress[document_id]

    def _create_document_from_data(self, data: dict[str, Any]) -> Document:
        """
        Create Document object from API data.

        Args:
            data: API response data

        Returns:
            Document object
        """
        # Parse chunks if available
        chunks = None
        if data.get("chunks"):
            chunks = [
                self._create_chunk_from_data(chunk_data)
                for chunk_data in data["chunks"]
            ]

        return Document(
            id=data.get("id", generate_id("doc_")),
            name=data.get("name", ""),
            filename=data.get("filename", ""),
            file_type=DocumentType(data.get("file_type", "unknown")),
            file_size=data.get("file_size", 0),
            status=DocumentStatus(data.get("status", "uploading")),
            uploaded_at=datetime.fromisoformat(data["uploaded_at"])
            if data.get("uploaded_at")
            else datetime.now(),
            processed_at=datetime.fromisoformat(data["processed_at"])
            if data.get("processed_at")
            else None,
            chunks=chunks,
            metadata=data.get("metadata"),
            tags=data.get("tags", []),
            category=data.get("category"),
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
        )

    def _create_chunk_from_data(self, data: dict[str, Any]) -> DocumentChunk:
        """
        Create DocumentChunk object from API data.

        Args:
            data: API response data

        Returns:
            DocumentChunk object
        """
        return DocumentChunk(
            id=data.get("id", generate_id("chunk_")),
            document_id=data.get("document_id", ""),
            content=data.get("content", ""),
            chunk_index=data.get("chunk_index", 0),
            start_position=data.get("start_position", 0),
            end_position=data.get("end_position", 0),
            embedding_id=data.get("embedding_id"),
            metadata=data.get("metadata"),
        )

    def _create_search_result_from_data(self, data: dict[str, Any]) -> SearchResult:
        """
        Create SearchResult object from API data.

        Args:
            data: API response data

        Returns:
            SearchResult object
        """
        return SearchResult(
            document_id=data.get("document_id", ""),
            document_name=data.get("document_name", ""),
            chunk_id=data.get("chunk_id", ""),
            content=data.get("content", ""),
            score=data.get("score", 0.0),
            chunk_index=data.get("chunk_index", 0),
            start_position=data.get("start_position", 0),
            end_position=data.get("end_position", 0),
            metadata=data.get("metadata"),
        )


# Global knowledge service instance
knowledge_service = KnowledgeService()
