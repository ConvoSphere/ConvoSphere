"""
Knowledge base Pydantic schemas.

This module defines the Pydantic models for knowledge base API requests
and responses, including document management and search functionality.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document model."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    """Document creation model."""

    file_name: str = Field(..., min_length=1)
    file_content: bytes = Field(...)
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class DocumentResponse(DocumentBase):
    """Document response model."""

    id: str
    file_name: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int | None = None
    total_tokens: int | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Document list response model."""

    documents: list[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk response."""

    id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Chunk position in document")
    chunk_size: int = Field(..., description="Chunk size in characters")
    token_count: int = Field(..., description="Number of tokens in chunk")
    embedding_model: str | None = Field(None, description="Embedding model used")
    embedding_created_at: str | None = Field(
        None, description="Embedding creation timestamp",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    filters: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    """Search response model."""

    id: str
    content: str
    score: float
    document_id: str | None = None
    chunk_id: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentProcessRequest(BaseModel):
    """Document processing request model."""

    processing_options: dict[str, Any] | None = None


class ProcessingOptions(BaseModel):
    """Advanced processing options model."""

    engine: str = Field(
        "auto", description="Processing engine: auto, traditional, docling",
    )
    options: dict[str, Any] = Field(
        default_factory=dict, description="Engine-specific options",
    )


class ProcessingEngineInfo(BaseModel):
    """Processing engine information model."""

    name: str
    description: str
    supported_formats: list[str]
    features: list[str] | None = None


class SupportedFormats(BaseModel):
    """Supported formats response model."""

    all_formats: list[str]
    by_engine: dict[str, list[str]]


class DocumentReprocessRequest(BaseModel):
    """Document reprocessing request model."""

    processing_options: ProcessingOptions


class DocumentReprocessResponse(BaseModel):
    """Document reprocessing response model."""

    message: str
    metadata: dict[str, Any]


class DocumentUploadAdvanced(BaseModel):
    """Advanced document upload model."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    engine: str = Field(
        "auto", description="Processing engine: auto, traditional, docling",
    )
    processing_options: dict[str, Any] | None = Field(default_factory=dict)


class DocumentChunkInfo(BaseModel):
    """Document chunk information model."""

    id: str
    content: str
    chunk_type: str | None = None
    page_number: int | None = None
    table_id: str | None = None
    figure_id: str | None = None
    token_count: int
    start_word: int
    end_word: int
    embedding_model: str | None = None
    embedding_created_at: datetime | None = None


class DocumentProcessingResult(BaseModel):
    """Document processing result model."""

    success: bool
    text: str
    chunks: list[DocumentChunkInfo]
    tables: list[dict[str, Any]] = Field(default_factory=list)
    figures: list[dict[str, Any]] = Field(default_factory=list)
    formulas: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class DocumentStatistics(BaseModel):
    """Document statistics model."""

    total_documents: int
    processed_documents: int
    processing_documents: int
    error_documents: int
    total_chunks: int
    total_tokens: int
    processing_engines: dict[str, int] = Field(default_factory=dict)
    file_types: dict[str, int] = Field(default_factory=dict)


class SearchHistoryItem(BaseModel):
    """Schema for search history item."""

    id: str = Field(..., description="Search query ID")
    query: str = Field(..., description="Search query")
    query_type: str = Field(..., description="Type of search")
    result_count: int = Field(..., description="Number of results")
    execution_time: float | None = Field(None, description="Execution time in seconds")
    created_at: str = Field(..., description="Search timestamp")

    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    """Schema for search history response."""

    searches: list[SearchHistoryItem] = Field(..., description="List of search queries")
    total: int = Field(..., description="Total number of searches")
    skip: int = Field(..., description="Number of searches skipped")
    limit: int = Field(..., description="Maximum number of searches returned")


class KnowledgeBaseStats(BaseModel):
    """Schema for knowledge base statistics."""

    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_tokens: int = Field(..., description="Total number of tokens")
    documents_by_status: dict[str, int] = Field(
        ..., description="Documents count by status",
    )
    documents_by_type: dict[str, int] = Field(
        ..., description="Documents count by file type",
    )
    storage_used: int = Field(..., description="Storage used in bytes")
    last_processed: str | None = Field(
        None, description="Last document processing timestamp",
    )
