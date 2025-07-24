"""
Knowledge base API endpoints.

This module provides REST API endpoints for managing documents,
searching the knowledge base, and RAG functionality.
"""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.knowledge import (
    DocumentList,
    DocumentResponse,
    ProcessingOptions,
    SearchRequest,
    SearchResponse,
    TagList,
    TagResponse,
    DocumentUpdate,
    DocumentProcessingJobResponse,
    DocumentProcessingJobList,
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    BulkImportRequest,
    BulkImportResponse,
    KnowledgeBaseStats,
)
from app.services.docling_processor import docling_processor
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    tags: str | None = Form(None),  # Comma-separated tags
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document to the knowledge base."""
    try:
        # Validate file type
        allowed_types = [".pdf", ".txt", ".doc", ".docx", ".md"]
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {allowed_types}",
            )

        # Read file content
        file_content = await file.read()

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Parse processing options
        processing_opts = {}
        if processing_options:
            try:
                import json

                processing_opts = json.loads(processing_options)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid processing options JSON",
                )

        # Create document
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.create_document(
            user_id=str(current_user.id),
            title=title,
            file_name=file.filename,
            file_content=file_content,
            description=description,
            tags=tag_list,
            metadata=processing_opts,
        )

        return DocumentResponse.from_orm(document)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}",
        )


@router.get("/documents", response_model=DocumentList)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    document_type: str | None = Query(None),
    author: str | None = Query(None),
    year: int | None = Query(None),
    language: str | None = Query(None),
    tag_names: str | None = Query(None),  # Comma-separated tag names
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get documents for the current user with advanced filtering."""
    try:
        # Parse tag names
        tag_list = None
        if tag_names:
            tag_list = [tag.strip() for tag in tag_names.split(",") if tag.strip()]

        knowledge_service = KnowledgeService(db)
        documents, total = knowledge_service.get_documents(
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
            status=status,
            document_type=document_type,
            author=author,
            year=year,
            language=language,
            tag_names=tag_list,
        )

        return DocumentList(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving documents: {str(e)}",
        )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document by ID."""
    try:
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.get_document(document_id, str(current_user.id))

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse.from_orm(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving document: {str(e)}",
        )


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update document metadata."""
    try:
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.update_document_metadata(
            document_id=document_id,
            user_id=str(current_user.id),
            title=document_update.title,
            description=document_update.description,
            author=document_update.author,
            source=document_update.source,
            year=document_update.year,
            language=document_update.language,
            keywords=document_update.keywords,
            tags=document_update.tags,
        )

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse.from_orm(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating document: {str(e)}",
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document."""
    try:
        knowledge_service = KnowledgeService(db)
        success = knowledge_service.delete_document(document_id, str(current_user.id))

        if not success:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}",
        )


@router.post("/documents/{document_id}/process")
async def process_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process a document to extract text and create embeddings."""
    try:
        knowledge_service = KnowledgeService(db)

        # Check if document exists and belongs to user
        document = knowledge_service.get_document(document_id, str(current_user.id))
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Process document
        success = await knowledge_service.process_document(document_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to process document")

        return {"message": "Document processing started successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}",
        )


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a document file."""
    try:
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.get_document(document_id, str(current_user.id))

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="Document file not found")

        return FileResponse(
            path=document.file_path,
            filename=document.file_name,
            media_type=document.mime_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error downloading document: {str(e)}",
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search documents using semantic search."""
    try:
        knowledge_service = KnowledgeService(db)

        if request.search_type == "knowledge":
            results = await knowledge_service.search_documents(
                query=request.query,
                user_id=str(current_user.id),
                limit=request.limit,
                filters=request.filters,
            )
        elif request.search_type == "conversation":
            results = await knowledge_service.search_conversations(
                query=request.query,
                user_id=str(current_user.id),
                conversation_id=request.conversation_id,
                limit=request.limit,
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")

        return SearchResponse(
            query=request.query,
            search_type=request.search_type,
            results=results,
            total=len(results),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching documents: {str(e)}",
        )


@router.post("/search/advanced", response_model=AdvancedSearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Advanced search with complex filtering and sorting."""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Convert filters to Weaviate format
        filters = {}
        if request.filters:
            if request.filters.document_type:
                filters["document_type"] = request.filters.document_type
            if request.filters.author:
                filters["author"] = request.filters.author
            if request.filters.language:
                filters["language"] = request.filters.language
            if request.filters.year:
                filters["year"] = request.filters.year

        results = await knowledge_service.search_documents(
            query=request.query,
            user_id=str(current_user.id),
            limit=request.limit,
            filters=filters,
        )

        return AdvancedSearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            offset=request.offset,
            limit=request.limit,
            filters_applied=request.filters,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error performing advanced search: {str(e)}",
        )


@router.get("/search/history")
async def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get search history for the current user."""
    try:
        knowledge_service = KnowledgeService(db)
        search_history = knowledge_service.get_search_history(
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
        )

        return {
            "searches": search_history,
            "total": len(search_history),
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving search history: {str(e)}",
        )


@router.get("/tags", response_model=TagList)
async def get_tags(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tags for the current user's documents."""
    try:
        knowledge_service = KnowledgeService(db)
        tags = knowledge_service.get_tags(str(current_user.id), limit)

        return TagList(
            tags=[TagResponse.from_orm(tag) for tag in tags],
            total=len(tags),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving tags: {str(e)}",
        )


@router.get("/tags/search", response_model=TagList)
async def search_tags(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search tags by name."""
    try:
        knowledge_service = KnowledgeService(db)
        tags = knowledge_service.search_tags(query, str(current_user.id), limit)

        return TagList(
            tags=[TagResponse.from_orm(tag) for tag in tags],
            total=len(tags),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching tags: {str(e)}",
        )


@router.get("/processing/jobs", response_model=DocumentProcessingJobList)
async def get_processing_jobs(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document processing jobs for the current user."""
    try:
        knowledge_service = KnowledgeService(db)
        jobs = knowledge_service.get_processing_jobs(
            user_id=str(current_user.id),
            status=status,
            limit=limit,
        )

        return DocumentProcessingJobList(
            jobs=[DocumentProcessingJobResponse.from_orm(job) for job in jobs],
            total=len(jobs),
            skip=0,
            limit=limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving processing jobs: {str(e)}",
        )


@router.post("/processing/jobs")
async def create_processing_job(
    document_id: str,
    job_type: str = Form("process"),
    priority: int = Form(0, ge=0, le=10),
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document processing job."""
    try:
        # Parse processing options
        options = {}
        if processing_options:
            try:
                import json
                options = json.loads(processing_options)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid processing options JSON",
                )

        knowledge_service = KnowledgeService(db)
        job = knowledge_service.create_processing_job(
            document_id=document_id,
            user_id=str(current_user.id),
            job_type=job_type,
            priority=priority,
            processing_options=options,
        )

        return DocumentProcessingJobResponse.from_orm(job)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating processing job: {str(e)}",
        )


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_documents(
    request: BulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk import multiple documents."""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Create a bulk import job
        job = knowledge_service.create_processing_job(
            document_id="",  # Will be set for each document
            user_id=str(current_user.id),
            job_type="bulk_import",
            priority=5,
            processing_options={
                "files": request.files,
                "default_tags": request.tags,
                "processing_options": request.processing_options.dict() if request.processing_options else {},
            },
        )

        return BulkImportResponse(
            job_id=str(job.id),
            total_files=len(request.files),
            message="Bulk import job created successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating bulk import job: {str(e)}",
        )


@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get knowledge base statistics for the current user."""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Get documents with different statuses
        documents, total = knowledge_service.get_documents(str(current_user.id), limit=10000)
        
        # Calculate statistics
        processed_count = sum(1 for doc in documents if doc.status == "processed")
        processing_count = sum(1 for doc in documents if doc.status == "processing")
        error_count = sum(1 for doc in documents if doc.status == "error")
        
        # Calculate total chunks and tokens
        total_chunks = sum(doc.chunk_count or 0 for doc in documents)
        total_tokens = sum(doc.total_tokens or 0 for doc in documents)
        
        # Calculate storage used
        storage_used = sum(doc.file_size for doc in documents)
        
        # Get documents by type
        documents_by_type = {}
        for doc in documents:
            doc_type = doc.document_type or "unknown"
            documents_by_type[doc_type] = documents_by_type.get(doc_type, 0) + 1
        
        # Get documents by status
        documents_by_status = {
            "uploaded": sum(1 for doc in documents if doc.status == "uploaded"),
            "processing": processing_count,
            "processed": processed_count,
            "error": error_count,
        }
        
        # Get last processed document
        last_processed = None
        processed_docs = [doc for doc in documents if doc.processed_at]
        if processed_docs:
            last_processed = max(processed_docs, key=lambda x: x.processed_at).processed_at.isoformat()

        return KnowledgeBaseStats(
            total_documents=total,
            total_chunks=total_chunks,
            total_tokens=total_tokens,
            documents_by_status=documents_by_status,
            documents_by_type=documents_by_type,
            storage_used=storage_used,
            last_processed=last_processed,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving statistics: {str(e)}",
        )


@router.get("/processing/engines")
async def get_processing_engines():
    """Get available document processing engines."""
    engines = {
        "traditional": {
            "name": "Traditional Processing",
            "description": "Basic text extraction using standard libraries",
            "supported_formats": ["pdf", "docx", "txt", "md", "html"],
        },
    }

    # Add Docling if available
    if docling_processor.is_available():
        engines["docling"] = {
            "name": "Docling Advanced Processing",
            "description": "Advanced document processing with OCR, ASR, and vision models",
            "supported_formats": docling_processor.get_supported_formats(),
            "features": [
                "OCR for scanned documents",
                "Audio transcription (ASR)",
                "Image analysis with vision models",
                "Table and figure extraction",
                "Formula recognition",
                "Page layout understanding",
            ],
        }

    return engines


@router.get("/processing/supported-formats")
async def get_supported_formats():
    """Get supported document formats."""
    formats = {
        "traditional": ["pdf", "docx", "txt", "md", "html"],
        "docling": docling_processor.get_supported_formats()
        if docling_processor.is_available()
        else [],
    }

    # Combine all formats
    all_formats = set()
    for format_list in formats.values():
        all_formats.update(format_list)

    return {
        "all_formats": sorted(all_formats),
        "by_engine": formats,
    }


@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    processing_options: ProcessingOptions,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reprocess a document with specific options."""
    try:
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.get_document(document_id, str(current_user.id))

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Read file content
        with open(document.file_path, "rb") as f:
            file_content = f.read()

        # Process with specific options
        if processing_options.engine == "docling" and docling_processor.is_available():
            result = docling_processor.process_document(
                file_content,
                document.file_name,
                options=processing_options.options,
            )
        else:
            # Use traditional processing
            from app.services.document_processor import document_processor

            result = document_processor.process_document(
                file_content, document.file_name,
            )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=f"Reprocessing failed: {result.get('error')}",
            )

        # Update document metadata
        document.metadata.update(result["metadata"])
        db.commit()

        return {
            "message": "Document reprocessed successfully",
            "metadata": result["metadata"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")


@router.post("/documents/upload-advanced", response_model=DocumentResponse)
async def upload_document_advanced(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    engine: str = Form("auto"),  # auto, traditional, docling
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document with advanced processing options."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read file content
        file_content = await file.read()

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Parse processing options
        processing_opts = {}
        if processing_options:
            try:
                import json

                processing_opts = json.loads(processing_options)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid processing options JSON",
                )

        # Determine processing engine
        if engine == "auto":
            file_type = Path(file.filename).suffix.lower().lstrip(".")
            if (
                docling_processor.is_available()
                and file_type in docling_processor.get_supported_formats()
            ):
                engine = "docling"
            else:
                engine = "traditional"

        # Validate engine
        if engine == "docling" and not docling_processor.is_available():
            raise HTTPException(status_code=400, detail="Docling engine not available")

        # Add engine to metadata
        processing_opts["engine"] = engine

        # Create document
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.create_document(
            user_id=str(current_user.id),
            title=title,
            file_name=file.filename,
            file_content=file_content,
            description=description,
            tags=tag_list,
            metadata=processing_opts,
        )

        return DocumentResponse.from_orm(document)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
