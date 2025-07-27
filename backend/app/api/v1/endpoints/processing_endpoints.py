"""
Processing-related API endpoints (jobs, engines, supported formats, bulk import).
"""

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.knowledge import (
    BulkImportRequest,
    BulkImportResponse,
    DocumentProcessingJobList,
)
from backend.app.services.docling_processor import docling_processor
from backend.app.services.knowledge_service import KnowledgeService
from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.orm import Session

router = APIRouter()


# Get processing jobs
@router.get("/processing/jobs", response_model=DocumentProcessingJobList)
async def get_processing_jobs(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get processing jobs for the current user."""
    service = KnowledgeService(db)
    return await service.get_processing_jobs(current_user, status, limit)


# Create processing job
@router.post("/processing/jobs")
async def create_processing_job(
    document_id: str,
    job_type: str = Form("process"),
    priority: int = Form(0, ge=0, le=10),
    processing_options: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new processing job."""
    service = KnowledgeService(db)
    return await service.create_processing_job(
        document_id,
        job_type,
        priority,
        processing_options,
        current_user,
    )


# Bulk import
@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_documents(
    request: BulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk import documents."""
    service = KnowledgeService(db)
    return await service.bulk_import_documents(request, current_user)


# Get processing engines
@router.get("/processing/engines")
async def get_processing_engines():
    """Get available processing engines."""
    return docling_processor.get_engines()


# Get supported formats
@router.get("/processing/supported-formats")
async def get_supported_formats():
    """Get supported file formats."""
    return docling_processor.get_supported_formats()
