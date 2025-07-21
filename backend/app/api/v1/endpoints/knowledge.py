"""
Knowledge base API endpoints.

This module provides REST API endpoints for managing documents,
searching the knowledge base, and RAG functionality.
"""

import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from ....core.database import get_db
from ....core.security import get_current_user, require_permission
from ....models.user import User
from ....services.knowledge_service import KnowledgeService
from ....services.docling_processor import docling_processor
from ....schemas.knowledge import (
    DocumentResponse,
    DocumentList,
    SearchRequest,
    SearchResponse,
    ProcessingOptions
)

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    processing_options: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document to the knowledge base."""
    try:
        # Validate file type
        allowed_types = [".pdf", ".txt", ".doc", ".docx", ".md"]
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {allowed_types}"
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
                raise HTTPException(status_code=400, detail="Invalid processing options JSON")
        
        # Create document
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.create_document(
            user_id=str(current_user.id),
            title=title,
            file_name=file.filename,
            file_content=file_content,
            description=description,
            tags=tag_list,
            metadata=processing_opts
        )
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            status=document.status,
            tags=document.tags,
            chunk_count=document.chunk_count,
            total_tokens=document.total_tokens,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat(),
            processed_at=document.processed_at.isoformat() if document.processed_at else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/documents", response_model=DocumentList)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents for the current user."""
    try:
        knowledge_service = KnowledgeService(db)
        documents, total = knowledge_service.get_documents(
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
            status=status
        )
        
        return DocumentList(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.delete("/documents/{document_id}")
@require_permission("knowledge:delete")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.post("/documents/{document_id}/process")
@require_permission("knowledge:write")
async def process_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            media_type=document.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search documents using semantic search."""
    try:
        knowledge_service = KnowledgeService(db)
        
        if request.search_type == "knowledge":
            results = knowledge_service.search_documents(
                query=request.query,
                user_id=str(current_user.id),
                limit=request.limit,
                filters=request.filters
            )
        elif request.search_type == "conversation":
            results = knowledge_service.search_conversations(
                query=request.query,
                user_id=str(current_user.id),
                conversation_id=request.conversation_id,
                limit=request.limit
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        return SearchResponse(
            query=request.query,
            search_type=request.search_type,
            results=results,
            total=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.get("/search/history")
async def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search history for the current user."""
    try:
        # TODO: Implement search history retrieval
        return {
            "searches": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search history: {str(e)}")


@router.get("/processing/engines")
async def get_processing_engines():
    """Get available document processing engines."""
    engines = {
        "traditional": {
            "name": "Traditional Processing",
            "description": "Basic text extraction using standard libraries",
            "supported_formats": ["pdf", "docx", "txt", "md", "html"]
        }
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
                "Page layout understanding"
            ]
        }
    
    return engines


@router.get("/processing/supported-formats")
async def get_supported_formats():
    """Get supported document formats."""
    formats = {
        "traditional": ["pdf", "docx", "txt", "md", "html"],
        "docling": docling_processor.get_supported_formats() if docling_processor.is_available() else []
    }
    
    # Combine all formats
    all_formats = set()
    for format_list in formats.values():
        all_formats.update(format_list)
    
    return {
        "all_formats": sorted(list(all_formats)),
        "by_engine": formats
    }


@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    processing_options: ProcessingOptions,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprocess a document with specific options."""
    try:
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.get_document(document_id, str(current_user.id))
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Read file content
        with open(document.file_path, 'rb') as f:
            file_content = f.read()
        
        # Process with specific options
        if processing_options.engine == "docling" and docling_processor.is_available():
            result = docling_processor.process_document(
                file_content, 
                document.file_name,
                options=processing_options.options
            )
        else:
            # Use traditional processing
            from ....services.document_processor import document_processor
            result = document_processor.process_document(file_content, document.file_name)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=f"Reprocessing failed: {result.get('error')}")
        
        # Update document metadata
        document.metadata.update(result['metadata'])
        db.commit()
        
        return {"message": "Document reprocessed successfully", "metadata": result['metadata']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")


@router.post("/documents/upload-advanced", response_model=DocumentResponse)
async def upload_document_advanced(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    engine: str = Form("auto"),  # auto, traditional, docling
    processing_options: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Parse processing options
        processing_opts = {}
        if processing_options:
            try:
                import json
                processing_opts = json.loads(processing_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid processing options JSON")
        
        # Determine processing engine
        if engine == "auto":
            file_type = Path(file.filename).suffix.lower().lstrip('.')
            if docling_processor.is_available() and file_type in docling_processor.get_supported_formats():
                engine = "docling"
            else:
                engine = "traditional"
        
        # Validate engine
        if engine == "docling" and not docling_processor.is_available():
            raise HTTPException(status_code=400, detail="Docling engine not available")
        
        # Add engine to metadata
        processing_opts['engine'] = engine
        
        # Create document
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.create_document(
            user_id=str(current_user.id),
            title=title,
            file_name=file.filename,
            file_content=file_content,
            description=description,
            tags=tag_list,
            metadata=processing_opts
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}") 