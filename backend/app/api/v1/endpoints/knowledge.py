"""
Knowledge base API endpoints.

This module provides REST API endpoints for managing documents,
searching the knowledge base, and RAG functionality.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....services.knowledge_service import KnowledgeService
from ....schemas.knowledge import (
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    SearchRequest,
    SearchResponse,
    DocumentProcessRequest
)

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
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
        
        # Create document
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.create_document(
            user_id=str(current_user.id),
            title=title,
            file_name=file.filename,
            file_content=file_content,
            description=description,
            tags=tag_list
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


@router.get("/documents", response_model=DocumentListResponse)
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
        
        document_responses = []
        for doc in documents:
            document_responses.append(DocumentResponse(
                id=str(doc.id),
                title=doc.title,
                description=doc.description,
                file_name=doc.file_name,
                file_type=doc.file_type,
                file_size=doc.file_size,
                status=doc.status,
                tags=doc.tags,
                chunk_count=doc.chunk_count,
                total_tokens=doc.total_tokens,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
                processed_at=doc.processed_at.isoformat() if doc.processed_at else None
            ))
        
        return DocumentListResponse(
            documents=document_responses,
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.delete("/documents/{document_id}")
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
        success = knowledge_service.process_document(document_id)
        
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