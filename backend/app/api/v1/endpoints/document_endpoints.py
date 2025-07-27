"""
Document-related API endpoints (upload, download, get, update, delete, process).
"""

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.knowledge import (
    DocumentList,
    DocumentResponse,
    DocumentUpdate,
    ProcessingOptions,
)
from backend.app.services.knowledge_service import KnowledgeService
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


# Upload document
@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a new document."""
    service = KnowledgeService(db)
    return await service.upload_document(
        file,
        title,
        description,
        tags,
        processing_options,
        current_user,
    )


# Get documents
@router.get("/documents", response_model=DocumentList)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    document_type: str | None = Query(None),
    author: str | None = Query(None),
    year: int | None = Query(None),
    language: str | None = Query(None),
    tag_names: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get documents with filtering."""
    service = KnowledgeService(db)
    return await service.get_documents(
        current_user,
        skip,
        limit,
        status,
        document_type,
        author,
        year,
        language,
        tag_names,
    )


# Get document by ID
@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document by ID."""
    service = KnowledgeService(db)
    return await service.get_document(document_id, current_user)


# Update document
@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a document."""
    service = KnowledgeService(db)
    return await service.update_document(document_id, document_update, current_user)


# Delete document
@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document."""
    service = KnowledgeService(db)
    await service.delete_document(document_id, current_user)
    return {"message": "Document deleted successfully"}


# Process document
@router.post("/documents/{document_id}/process")
async def process_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process a document."""
    service = KnowledgeService(db)
    return await service.process_document(document_id, current_user)


# Download document
@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a document."""
    service = KnowledgeService(db)
    return await service.download_document(document_id, current_user)


# Reprocess document
@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    processing_options: ProcessingOptions,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reprocess a document with new options."""
    service = KnowledgeService(db)
    return await service.reprocess_document(
        document_id,
        processing_options,
        current_user,
    )


# Advanced upload
@router.post("/documents/upload-advanced", response_model=DocumentResponse)
async def upload_document_advanced(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    engine: str = Form("auto"),
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document with advanced options."""
    service = KnowledgeService(db)
    return await service.upload_document_advanced(
        file,
        title,
        description,
        tags,
        engine,
        processing_options,
        current_user,
    )
