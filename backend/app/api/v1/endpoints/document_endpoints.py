"""
Document-related API endpoints (upload, download, get, update, delete, process).
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
    DocumentResponse,
    DocumentList,
    DocumentUpdate,
    ProcessingOptions,
)
from app.services.docling_processor import docling_processor
from app.services.knowledge_service import KnowledgeService

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
    # ... existing code ...

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
    # ... existing code ...

# Get document by ID
@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Update document
@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Delete document
@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Process document
@router.post("/documents/{document_id}/process")
async def process_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Download document
@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

# Reprocess document
@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    processing_options: ProcessingOptions,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... existing code ...

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
    # ... existing code ...