"""
Document-related API endpoints (upload, download, get, update, delete, process).
"""

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.rate_limiting import rate_limit_upload, rate_limit_search
from backend.app.core.caching import cache
from backend.app.core.pagination import PaginationParams, PaginationOptimizer
from backend.app.monitoring.performance_monitor import monitor_performance
from backend.app.models.user import User
from backend.app.schemas.knowledge import (
    DocumentList,
    DocumentResponse,
    DocumentUpdate,
    ProcessingOptions,
)
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.services.search.advanced_search import get_advanced_search_service, SearchType, SearchFilter
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, Request
from sqlalchemy.orm import Session

router = APIRouter()


# Upload document
@router.post("/documents", response_model=DocumentResponse)
@rate_limit_upload
async def upload_document(
    request: Request,
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
@rate_limit_search
@cache(ttl=300, key_prefix="documents")
@monitor_performance
async def get_documents(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    document_type: str | None = Query(None),
    author: str | None = Query(None),
    year: int | None = Query(None),
    language: str | None = Query(None),
    tag_names: str | None = Query(None),
    search_type: str = Query("hybrid"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get documents with filtering and advanced search."""
    service = KnowledgeService(db)
    
    # Use advanced search if search parameters are provided
    if any([status, document_type, author, year, language, tag_names]):
        search_service = get_advanced_search_service(db)
        
        # Build search filters
        filters = []
        if status:
            filters.append(SearchFilter("status", "equals", status))
        if document_type:
            filters.append(SearchFilter("document_type", "equals", document_type))
        if author:
            filters.append(SearchFilter("author", "equals", author))
        if year:
            filters.append(SearchFilter("year", "equals", year))
        if language:
            filters.append(SearchFilter("language", "equals", language))
        if tag_names:
            filters.append(SearchFilter("tags", "in", tag_names.split(",")))
        
        # Perform advanced search
        search_result = await search_service.search(
            query="",  # Empty query for filtering only
            user_id=str(current_user.id),
            search_type=SearchType(search_type),
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=(skip // limit) + 1,
            page_size=limit
        )
        
        return DocumentList(
            documents=search_result["results"],
            total=search_result["total"],
            page=search_result["page"],
            page_size=search_result["page_size"]
        )
    
    # Fallback to regular service method
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
