"""
Knowledge base Pydantic schemas.

This module defines the Pydantic models for knowledge base API requests
and responses, including document management and search functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Schema for creating a new document."""
    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    tags: Optional[List[str]] = Field(default_factory=list, description="Document tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    description: str = Field(..., description="Document description")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File type (pdf, txt, doc, docx, md)")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    status: str = Field(..., description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    chunk_count: int = Field(..., description="Number of chunks")
    total_tokens: int = Field(..., description="Total number of tokens")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    processed_at: Optional[str] = Field(None, description="Processing completion timestamp")
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    documents: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    skip: int = Field(..., description="Number of documents skipped")
    limit: int = Field(..., description="Maximum number of documents returned")


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
    """Schema for search request."""
    query: str = Field(..., min_length=1, description="Search query")
    search_type: str = Field(..., description="Type of search (knowledge, conversation, hybrid)")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Search filters")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for conversation search")


class SearchResult(BaseModel):
    """Schema for search result."""
    id: str = Field(..., description="Result ID")
    content: str = Field(..., description="Result content")
    score: float = Field(..., description="Relevance score")
    source_type: str = Field(..., description="Source type (document, conversation)")
    source_id: str = Field(..., description="Source ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str = Field(..., description="Original search query")
    search_type: str = Field(..., description="Type of search performed")
    results: List[SearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    execution_time: Optional[float] = Field(None, description="Search execution time in seconds")


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


class DocumentProcessRequest(BaseModel):
    """Schema for document processing request."""
    chunk_size: Optional[int] = Field(500, ge=100, le=2000, description="Chunk size in characters")
    overlap: Optional[int] = Field(50, ge=0, le=500, description="Chunk overlap in characters")
    embedding_model: Optional[str] = Field(None, description="Embedding model to use")


class KnowledgeBaseStats(BaseModel):
    """Schema for knowledge base statistics."""
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_tokens: int = Field(..., description="Total number of tokens")
    documents_by_status: Dict[str, int] = Field(..., description="Documents count by status")
    documents_by_type: Dict[str, int] = Field(..., description="Documents count by file type")
    storage_used: int = Field(..., description="Storage used in bytes")
    last_processed: Optional[str] = Field(None, description="Last document processing timestamp") 