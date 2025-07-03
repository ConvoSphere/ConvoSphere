"""
Knowledge base models for document management and RAG functionality.

This module defines the database models for storing documents, chunks,
and metadata for the retrieval-augmented generation system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class Document(Base):
    """Document model for storing uploaded files and metadata."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, doc, docx, md
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, error
    error_message = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)  # List of tags
    knowledge_metadata = Column(JSON, default=dict)  # Additional metadata
    
    # User and timestamps
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def chunk_count(self) -> int:
        """Get the number of chunks for this document."""
        return len(self.chunks)
    
    @property
    def total_tokens(self) -> int:
        """Get the total number of tokens across all chunks."""
        return sum(chunk.token_count for chunk in self.chunks)


class DocumentChunk(Base):
    """Document chunk model for storing text chunks with embeddings."""
    
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in document
    chunk_size = Column(Integer, nullable=False)  # Number of characters
    
    # Token information
    token_count = Column(Integer, nullable=False, default=0)
    tokens = Column(JSON, nullable=True)  # Tokenized content
    
    # Embedding information
    embedding = Column(JSON, nullable=True)  # Vector embedding
    embedding_model = Column(String(100), nullable=True)  # Model used for embedding
    embedding_created_at = Column(DateTime, nullable=True)
    
    # Metadata
    chunk_metadata = Column(JSON, default=dict)  # Additional chunk metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
    
    @property
    def content_preview(self) -> str:
        """Get a preview of the chunk content."""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content


class SearchQuery(Base):
    """Search query model for tracking search history."""
    
    __tablename__ = "search_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Query information
    query = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # conversation, knowledge, hybrid
    filters = Column(JSON, default=dict)  # Search filters
    
    # Results
    result_count = Column(Integer, default=0)
    execution_time = Column(Float, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="search_queries")
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query[:50]}...', type='{self.query_type}')>" 