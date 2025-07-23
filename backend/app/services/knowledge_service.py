"""
Knowledge base service for document management and RAG functionality.

This module provides services for uploading, processing, and searching documents
in the knowledge base for retrieval-augmented generation.
"""

import logging
import mimetypes
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.knowledge import Document, DocumentChunk, SearchQuery

from .ai_service import AIService
from .document_processor import document_processor
from .embedding_service import embedding_service
from .weaviate_service import WeaviateService

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Service for managing knowledge base documents and search."""

    def __init__(self, db: Session):
        self.db = db
        self.weaviate_service = WeaviateService()
        self.ai_service = AIService()

        # Ensure upload directory exists
        self.upload_dir = Path(get_settings().UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def create_document(
        self,
        user_id: str,
        title: str,
        file_name: str,
        file_content: bytes,
        description: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Create a new document and save it to storage."""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file_name).suffix
            file_type = file_extension.lower().lstrip(".")

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_name)

            # Save file to storage
            file_path = self.upload_dir / f"{file_id}{file_extension}"
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Create document record
            document = Document(
                id=uuid.UUID(file_id),
                user_id=uuid.UUID(user_id),
                title=title,
                description=description or "",
                file_name=file_name,
                file_path=str(file_path),
                file_type=file_type,
                file_size=len(file_content),
                mime_type=mime_type,
                tags=tags or [],
                metadata=metadata or {},
                status="uploaded",
            )

            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            logger.info(f"Created document {document.id} for user {user_id}")
            return document

        except Exception as e:
            logger.error(f"Error creating document: {e}")
            self.db.rollback()
            raise

    async def process_document(self, document_id: str) -> bool:
        """Process a document by extracting text and creating chunks."""
        try:
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if not document:
                raise ValueError(f"Document {document_id} not found")

            # Update status to processing
            document.status = "processing"
            self.db.commit()

            # Read file content
            with open(document.file_path, "rb") as f:
                file_content = f.read()

            # Process document using document processor (with Docling integration)
            result = document_processor.process_document(
                file_content, document.file_name,
            )

            if not result["success"]:
                raise ValueError(
                    f"Document processing failed: {result.get('error', 'Unknown error')}",
                )

            # Create document chunks from processed chunks
            processed_chunks = result["chunks"]
            chunks = []

            for i, processed_chunk in enumerate(processed_chunks):
                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    chunk_index=i,
                    content=processed_chunk["content"],
                    token_count=processed_chunk["token_count"],
                    start_word=processed_chunk["start_word"],
                    end_word=processed_chunk["end_word"],
                )

                # Add Docling-specific metadata if available
                if "chunk_type" in processed_chunk:
                    chunk.metadata = {
                        "chunk_type": processed_chunk["chunk_type"],
                        "page_number": processed_chunk.get("page_number"),
                        "table_id": processed_chunk.get("table_id"),
                        "figure_id": processed_chunk.get("figure_id"),
                    }

                chunks.append(chunk)

            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await embedding_service.generate_embeddings(chunk_texts)

            # Add embeddings to chunks and store in Weaviate
            for i, chunk in enumerate(chunks):
                if i < len(embeddings) and embeddings[i]:
                    chunk.embedding = embeddings[i]
                    chunk.embedding_model = get_settings().default_embedding_model
                    chunk.embedding_created_at = datetime.utcnow()

                    # Enhanced metadata for Weaviate
                    weaviate_metadata = {
                        "title": document.title,
                        "file_type": document.file_type,
                        "chunk_index": chunk.chunk_index,
                        "user_id": str(document.user_id),
                        "processing_engine": result["metadata"].get(
                            "processing_engine", "traditional",
                        ),
                    }

                    # Add Docling-specific metadata
                    if hasattr(chunk, "metadata") and chunk.metadata:
                        weaviate_metadata.update(chunk.metadata)

                    # Store in Weaviate
                    self.weaviate_service.add_document_chunk(
                        chunk_id=str(chunk.id),
                        document_id=str(document.id),
                        content=chunk.content,
                        embedding=embeddings[i],
                        metadata=weaviate_metadata,
                    )

            # Save chunks to database
            self.db.add_all(chunks)

            # Update document metadata with Docling information
            document.metadata.update(result["metadata"])

            # Add Docling-specific information
            if "tables" in result:
                document.metadata["table_count"] = len(result["tables"])
            if "figures" in result:
                document.metadata["figure_count"] = len(result["figures"])
            if "formulas" in result:
                document.metadata["formula_count"] = len(result["formulas"])

            document.status = "processed"
            document.processed_at = datetime.utcnow()
            document.chunk_count = len(chunks)

            self.db.commit()

            logger.info(
                f"Successfully processed document {document_id} with {len(chunks)} chunks using {result['metadata'].get('processing_engine', 'traditional')} engine",
            )
            return True

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            # Update document status to error
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if document:
                document.status = "error"
                document.error_message = str(e)
                self.db.commit()
            return False

    def get_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[list[Document], int]:
        """Get documents for a user with optional filtering."""
        query = self.db.query(Document).filter(Document.user_id == user_id)

        if status:
            query = query.filter(Document.status == status)

        total = query.count()
        documents = query.offset(skip).limit(limit).all()

        return documents, total

    def get_document(self, document_id: str, user_id: str) -> Document | None:
        """Get a specific document by ID."""
        return (
            self.db.query(Document)
            .filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id,
                ),
            )
            .first()
        )

    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and its chunks."""
        try:
            document = self.get_document(document_id, user_id)
            if not document:
                return False

            # Delete from Weaviate
            self.weaviate_service.delete_document_chunks(str(document.id))

            # Delete file from storage
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            # Delete from database (cascade will delete chunks)
            self.db.delete(document)
            self.db.commit()

            logger.info(f"Deleted document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            self.db.rollback()
            return False

    async def search_documents(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search documents using semantic search."""
        try:
            # Generate query embedding using embedding service
            query_embedding = await embedding_service.generate_single_embedding(query)
            if not query_embedding:
                return []

            # Search in Weaviate
            search_results = self.weaviate_service.search_documents(
                query_embedding=query_embedding,
                user_id=user_id,
                limit=limit,
                filters=filters,
            )

            # Log search query
            search_query = SearchQuery(
                user_id=uuid.UUID(user_id),
                query=query,
                query_type="knowledge",
                filters=filters or {},
                result_count=len(search_results),
            )
            self.db.add(search_query)
            self.db.commit()

            return search_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def search_conversations(
        self,
        query: str,
        user_id: str,
        conversation_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search conversations using semantic search."""
        try:
            # Generate query embedding using embedding service
            query_embedding = await embedding_service.generate_single_embedding(query)
            if not query_embedding:
                return []

            # Search in Weaviate
            search_results = self.weaviate_service.search_conversations(
                query_embedding=query_embedding,
                user_id=user_id,
                conversation_id=conversation_id,
                limit=limit,
            )

            # Log search query
            search_query = SearchQuery(
                user_id=uuid.UUID(user_id),
                query=query,
                query_type="conversation",
                filters={"conversation_id": conversation_id} if conversation_id else {},
                result_count=len(search_results),
            )
            self.db.add(search_query)
            self.db.commit()

            return search_results

        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []

    def _extract_text_from_file(self, file_path: str, file_type: str) -> str | None:
        """Extract text content from various file types."""
        try:
            if file_type in ("txt", "md"):
                with open(file_path, encoding="utf-8") as f:
                    return f.read()

            elif file_type == "pdf":
                # Implement PDF text extraction
                try:
                    import io

                    import PyPDF2

                    with open(file_path, "rb") as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        return text.strip()
                except ImportError:
                    logger.error(
                        "PyPDF2 not installed. Install with: pip install PyPDF2",
                    )
                    return None
                except Exception as e:
                    logger.error(f"PDF extraction error: {e}")
                    return None

            elif file_type in ["doc", "docx"]:
                # Implement Word document text extraction
                try:
                    import docx
                    from docx import Document

                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"

                    # Also extract text from tables
                    for table in doc.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                text += cell.text + " "
                            text += "\n"

                    return text.strip()
                except ImportError:
                    logger.error(
                        "python-docx not installed. Install with: pip install python-docx",
                    )
                    return None
                except Exception as e:
                    logger.error(f"Word document extraction error: {e}")
                    return None

            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return None

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None

    def _create_chunks(
        self,
        text: str,
        document_id: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[DocumentChunk]:
        """Create text chunks from document content."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in ".!?":
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                # Count tokens (rough estimation)
                token_count = len(chunk_text.split())

                chunk = DocumentChunk(
                    document_id=uuid.UUID(document_id),
                    content=chunk_text,
                    chunk_index=len(chunks),
                    chunk_size=len(chunk_text),
                    token_count=token_count,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                    },
                )

                self.db.add(chunk)
                chunks.append(chunk)

            start = end - overlap
            if start >= len(text):
                break

        self.db.commit()
        return chunks

    def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding for text using AI service."""
        try:
            # Use AI service to generate embedding
            return self.ai_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
