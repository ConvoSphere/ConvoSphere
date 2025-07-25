"""
Knowledge base models for document management and RAG functionality.

This module defines the database models for storing documents, chunks,
and metadata for the retrieval-augmented generation system.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


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
    DOCUMENT = "document"  # Word, OpenOffice
    TEXT = "text"  # txt, md
    SPREADSHEET = "spreadsheet"  # Excel, CSV
    PRESENTATION = "presentation"  # PowerPoint
    IMAGE = "image"  # Images with OCR
    AUDIO = "audio"  # Audio files with transcription
    VIDEO = "video"  # Video files with transcription
    CODE = "code"  # Source code files
    OTHER = "other"


# Association table for document tags
document_tag_association = Table(
    "document_tag_association",
    Base.metadata,
    Column(
        "document_id", UUID(as_uuid=True), ForeignKey("documents.id"), primary_key=True,
    ),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    """Tag model for document categorization."""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    is_system = Column(
        Boolean, default=False, nullable=False,
    )  # System tags cannot be deleted

    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship(
        "Document", secondary=document_tag_association, back_populates="tag_objects",
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Document(Base):
    """Document model for storing uploaded files and metadata."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, doc, docx, md
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=True)

    # Processing status
    status = Column(String(50), default=DocumentStatus.UPLOADED, nullable=False)
    error_message = Column(Text, nullable=True)

    # Structured metadata
    author = Column(String(255), nullable=True, index=True)
    source = Column(String(500), nullable=True)
    language = Column(String(10), nullable=True, index=True)  # ISO language code
    year = Column(Integer, nullable=True, index=True)
    version = Column(String(50), nullable=True)
    keywords = Column(JSON, default=list)  # List of keywords

    # Document type categorization
    document_type = Column(
        String(50), nullable=True, index=True,
    )  # From DocumentType enum

    # Processing metadata
    processing_engine = Column(String(100), nullable=True)  # traditional, docling, etc.
    processing_options = Column(JSON, default=dict)

    # Content statistics
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)

    # Legacy fields (for backward compatibility)
    tags = Column(JSON, default=list)  # List of tags (deprecated, use Tag model)
    knowledge_metadata = Column(JSON, default=dict)  # Additional metadata

    # User and timestamps
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    tag_objects = relationship(
        "Tag", secondary=document_tag_association, back_populates="documents",
    )

    # Indexes for better query performance
    __table_args__ = (
        Index("idx_documents_user_status", "user_id", "status"),
        Index("idx_documents_type_year", "document_type", "year"),
        Index("idx_documents_author_year", "author", "year"),
        Index("idx_documents_language", "language"),
    )

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

    @property
    def tag_names(self) -> list[str]:
        """Get list of tag names."""
        return [tag.name for tag in self.tags]

    def add_tag(self, tag_name: str, db_session) -> bool:
        """Add a tag to the document."""
        try:
            # Normalize tag name
            tag_name = tag_name.lower().strip()

            # Find or create tag
            tag = db_session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db_session.add(tag)
                db_session.flush()  # Get the ID

            if tag not in self.tags:
                self.tags.append(tag)
                tag.usage_count += 1
                db_session.commit()
                return True
            return False
        except Exception:
            db_session.rollback()
            raise

    def remove_tag(self, tag_name: str, db_session) -> bool:
        """Remove a tag from the document."""
        try:
            tag_name = tag_name.lower().strip()
            tag = db_session.query(Tag).filter(Tag.name == tag_name).first()
            if tag and tag in self.tags:
                self.tags.remove(tag)
                tag.usage_count = max(0, tag.usage_count - 1)
                db_session.commit()
                return True
            return False
        except Exception:
            db_session.rollback()
            raise


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

    # Enhanced metadata
    chunk_type = Column(String(50), nullable=True)  # text, table, figure, formula, etc.
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    table_id = Column(String(100), nullable=True)
    figure_id = Column(String(100), nullable=True)

    # Legacy field
    chunk_metadata = Column(JSON, default=dict)  # Additional chunk metadata

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    # Indexes for better query performance
    __table_args__ = (
        Index("idx_chunks_document_index", "document_id", "chunk_index"),
        Index("idx_chunks_type", "chunk_type"),
        Index("idx_chunks_page", "page_number"),
    )

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


class DocumentProcessingJob(Base):
    """Model for tracking document processing jobs."""

    __tablename__ = "document_processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Job information
    job_type = Column(String(50), nullable=False)  # process, reprocess, bulk_import
    status = Column(
        String(50), default="pending", nullable=False,
    )  # pending, running, completed, failed
    priority = Column(
        Integer, default=0, nullable=False,
    )  # Higher number = higher priority

    # Processing details
    processing_engine = Column(String(100), nullable=True)
    processing_options = Column(JSON, default=dict)

    # Progress tracking
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    current_step = Column(String(100), nullable=True)
    total_steps = Column(Integer, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("Document")
    user = relationship("User")

    def __repr__(self):
        return f"<DocumentProcessingJob(id={self.id}, document_id={self.document_id}, status='{self.status}')>"
