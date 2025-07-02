"""
Knowledge base Pydantic schemas.

This module defines the Pydantic models for knowledge base API requests
and responses, including document management and search functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document model."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)


class DocumentCreate(DocumentBase):
    """Document creation model."""
    file_name: str = Field(..., min_length=1)
    file_content: bytes = Field(...)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentResponse(DocumentBase):
    """Document response model."""
    id: str
    file_name: str
    file_type: str
    file_size: int
    status: str
    chunk_count: Optional[int] = None
    total_tokens: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Document list response model."""
    documents: List[DocumentResponse]
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
    embedding_model: Optional[str] = Field(None, description="Embedding model used")
    embedding_created_at: Optional[str] = Field(None, description="Embedding creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Search response model."""
    id: str
    content: str
    score: float
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentProcessRequest(BaseModel):
    """Document processing request model."""
    processing_options: Optional[Dict[str, Any]] = None


class ProcessingOptions(BaseModel):
    """Advanced processing options model."""
    engine: str = Field("auto", description="Processing engine: auto, traditional, docling")
    options: Dict[str, Any] = Field(default_factory=dict, description="Engine-specific options")


class ProcessingEngineInfo(BaseModel):
    """Processing engine information model."""
    name: str
    description: str
    supported_formats: List[str]
    features: Optional[List[str]] = None


class SupportedFormats(BaseModel):
    """Supported formats response model."""
    all_formats: List[str]
    by_engine: Dict[str, List[str]]


class DocumentReprocessRequest(BaseModel):
    """Document reprocessing request model."""
    processing_options: ProcessingOptions


class DocumentReprocessResponse(BaseModel):
    """Document reprocessing response model."""
    message: str
    metadata: Dict[str, Any]


class DocumentUploadAdvanced(BaseModel):
    """Advanced document upload model."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    engine: str = Field("auto", description="Processing engine: auto, traditional, docling")
    processing_options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentChunkInfo(BaseModel):
    """Document chunk information model."""
    id: str
    content: str
    chunk_type: Optional[str] = None
    page_number: Optional[int] = None
    table_id: Optional[str] = None
    figure_id: Optional[str] = None
    token_count: int
    start_word: int
    end_word: int
    embedding_model: Optional[str] = None
    embedding_created_at: Optional[datetime] = None


class DocumentProcessingResult(BaseModel):
    """Document processing result model."""
    success: bool
    text: str
    chunks: List[DocumentChunkInfo]
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    figures: List[Dict[str, Any]] = Field(default_factory=list)
    formulas: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class DocumentStatistics(BaseModel):
    """Document statistics model."""
    total_documents: int
    processed_documents: int
    processing_documents: int
    error_documents: int
    total_chunks: int
    total_tokens: int
    processing_engines: Dict[str, int] = Field(default_factory=dict)
    file_types: Dict[str, int] = Field(default_factory=dict)


class SearchHistoryItem(BaseModel):
    """Schema for search history item."""
    id: str = Field(..., description="Search query ID")
    query: str = Field(..., description="Search query")
    query_type: str = Field(..., description="Type of search")
    result_count: int = Field(..., description="Number of results")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    created_at: str = Field(..., description="Search timestamp")
    
    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    """Schema for search history response."""
    searches: List[SearchHistoryItem] = Field(..., description="List of search queries")
    total: int = Field(..., description="Total number of searches")
    skip: int = Field(..., description="Number of searches skipped")
    limit: int = Field(..., description="Maximum number of searches returned")


class KnowledgeBaseStats(BaseModel):
    """Schema for knowledge base statistics."""
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_tokens: int = Field(..., description="Total number of tokens")
    documents_by_status: Dict[str, int] = Field(..., description="Documents count by status")
    documents_by_type: Dict[str, int] = Field(..., description="Documents count by file type")
    storage_used: int = Field(..., description="Storage used in bytes")
    last_processed: Optional[str] = Field(None, description="Last document processing timestamp") 