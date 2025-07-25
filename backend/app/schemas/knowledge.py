"""
Knowledge base Pydantic schemas.

This module defines the Pydantic models for knowledge base API requests
and responses, including document management and search functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(str, Enum):
    """Document processing status."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    REPROCESSING = "reprocessing"


class DocumentType(str, Enum):
    """Document types for categorization."""

    PDF = "pdf"
    DOCUMENT = "document"
    TEXT = "text"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    OTHER = "other"


class TagBase(BaseModel):
    """Base tag model."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """Tag creation model."""


class TagResponse(TagBase):
    """Tag response model."""

    id: str
    usage_count: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagList(BaseModel):
    """Tag list response model."""

    tags: list[TagResponse]
    total: int


class DocumentBase(BaseModel):
    """Base document model."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    author: str | None = Field(None, max_length=255)
    source: str | None = Field(None, max_length=500)
    language: str | None = Field(None, max_length=10)
    year: int | None = Field(None, ge=1900, le=2100)
    keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    """Document creation model."""

    file_name: str = Field(..., min_length=1)
    file_content: bytes = Field(...)
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    """Document update model."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    author: str | None = Field(None, max_length=255)
    source: str | None = Field(None, max_length=500)
    language: str | None = Field(None, max_length=10)
    year: int | None = Field(None, ge=1900, le=2100)
    keywords: list[str] | None = None
    tags: list[str] | None = None


class DocumentResponse(DocumentBase):
    """Document response model."""

    id: str
    file_name: str
    file_type: str
    file_size: int
    status: DocumentStatus
    document_type: DocumentType | None = None
    processing_engine: str | None = None
    page_count: int | None = None
    word_count: int | None = None
    character_count: int | None = None
    chunk_count: int | None = None
    total_tokens: int | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
    error_message: str | None = None
    tag_names: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


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
    chunk_type: str | None = Field(
        None,
        description="Type of chunk (text, table, figure, etc.)",
    )
    page_number: int | None = Field(None, description="Page number")
    section_title: str | None = Field(None, description="Section title")
    table_id: str | None = Field(None, description="Table ID if chunk is a table")
    figure_id: str | None = Field(None, description="Figure ID if chunk is a figure")
    embedding_model: str | None = Field(None, description="Embedding model used")
    embedding_created_at: str | None = Field(
        None,
        description="Embedding creation timestamp",
    )
    chunk_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata",
    )
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., min_length=1)
    search_type: str = Field(
        "knowledge",
        description="Type of search: knowledge, conversation, hybrid",
    )
    limit: int = Field(10, ge=1, le=100)
    filters: dict[str, Any] | None = None
    conversation_id: str | None = None


class SearchResponse(BaseModel):
    """Search response model."""

    query: str
    search_type: str
    results: list[dict[str, Any]]
    total: int


class SearchResult(BaseModel):
    """Individual search result model."""

    id: str
    content: str
    score: float
    document_id: str | None = None
    chunk_id: str | None = None
    document_title: str | None = None
    document_type: str | None = None
    author: str | None = None
    language: str | None = None
    year: int | None = None
    chunk_type: str | None = None
    page_number: int | None = None
    section_title: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentProcessRequest(BaseModel):
    """Document processing request model."""

    processing_options: dict[str, Any] | None = None


class ProcessingOptions(BaseModel):
    """Advanced processing options model."""

    engine: str = Field(
        "auto",
        description="Processing engine: auto, traditional, docling",
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Engine-specific options",
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
        "auto",
        description="Processing engine: auto, traditional, docling",
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

    model_config = ConfigDict(from_attributes=True)


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
        ...,
        description="Documents count by status",
    )
    documents_by_type: dict[str, int] = Field(
        ...,
        description="Documents count by file type",
    )
    storage_used: int = Field(..., description="Storage used in bytes")
    last_processed: str | None = Field(
        None,
        description="Last document processing timestamp",
    )


class DocumentProcessingJobBase(BaseModel):
    """Base document processing job model."""

    job_type: str = Field(
        ...,
        description="Type of job: process, reprocess, bulk_import",
    )
    priority: int = Field(0, ge=0, le=10, description="Job priority (0-10)")
    processing_engine: str | None = Field(None, description="Processing engine to use")
    processing_options: dict[str, Any] = Field(
        default_factory=dict,
        description="Processing options",
    )


class DocumentProcessingJobCreate(DocumentProcessingJobBase):
    """Document processing job creation model."""


class DocumentProcessingJobResponse(DocumentProcessingJobBase):
    """Document processing job response model."""

    id: str
    document_id: str
    user_id: str
    status: str
    progress: float
    current_step: str | None = None
    total_steps: int | None = None
    error_message: str | None = None
    retry_count: int
    max_retries: int
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessingJobList(BaseModel):
    """Document processing job list response model."""

    jobs: list[DocumentProcessingJobResponse]
    total: int
    skip: int
    limit: int


class BulkImportRequest(BaseModel):
    """Bulk import request model."""

    files: list[dict[str, Any]] = Field(..., description="List of file information")
    processing_options: ProcessingOptions | None = None
    tags: list[str] = Field(
        default_factory=list,
        description="Default tags for all documents",
    )


class BulkImportResponse(BaseModel):
    """Bulk import response model."""

    job_id: str
    total_files: int
    message: str


class DocumentFilter(BaseModel):
    """Document filter model for advanced search."""

    status: DocumentStatus | None = None
    document_type: DocumentType | None = None
    author: str | None = None
    year: int | None = None
    language: str | None = None
    tag_names: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_file_size: int | None = None
    max_file_size: int | None = None


class AdvancedSearchRequest(BaseModel):
    """Advanced search request model."""

    query: str = Field(..., min_length=1)
    filters: DocumentFilter | None = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sort_by: str = Field(
        "relevance",
        description="Sort by: relevance, date, title, author",
    )
    sort_order: str = Field("desc", description="Sort order: asc, desc")


class AdvancedSearchResponse(BaseModel):
    """Advanced search response model."""

    query: str
    results: list[SearchResult]
    total: int
    offset: int
    limit: int
    filters_applied: DocumentFilter | None = None
    execution_time: float | None = None
