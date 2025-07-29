"""
Backup and recovery API endpoints.

This module provides endpoints for managing document backups and recovery operations.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.rate_limiting import rate_limit_auth
from backend.app.core.security import get_current_user
from backend.app.models.knowledge import Document
from backend.app.models.user import User
from backend.app.schemas.backup import (
    BackupCreate,
    BackupList,
    BackupResponse,
    BackupRestore,
    BackupStats,
    RecoveryStats,
)
from backend.app.services.document.backup_manager import BackupType, get_backup_manager
from backend.app.services.document.error_handler import get_document_error_handler
from backend.app.services.document.recovery_manager import (
    get_recovery_manager,
    get_state_manager,
)

router = APIRouter()


@router.post("/backups", response_model=BackupResponse)
@rate_limit_auth
async def create_backup(
    request: Request,
    backup_request: BackupCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new backup."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    try:
        backup_id = await backup_manager.create_backup(
            backup_type=BackupType(backup_request.backup_type),
            document_ids=backup_request.document_ids,
            retention_days=backup_request.retention_days,
        )

        # Get backup metadata
        metadata = backup_manager.backup_metadata.get(backup_id)

        return BackupResponse(
            backup_id=backup_id,
            status=metadata.status.value if metadata else "completed",
            message="Backup created successfully",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.get("/backups", response_model=BackupList)
@rate_limit_auth
async def list_backups(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    backup_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List available backups."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    # Filter backups
    backups = list(backup_manager.backup_metadata.values())

    if status:
        backups = [b for b in backups if b.status.value == status]

    if backup_type:
        backups = [b for b in backups if b.backup_type.value == backup_type]

    # Apply pagination
    total = len(backups)
    backups = backups[skip : skip + limit]

    return BackupList(
        backups=[
            {
                "backup_id": b.backup_id,
                "backup_type": b.backup_type.value,
                "status": b.status.value,
                "created_at": b.created_at,
                "completed_at": b.completed_at,
                "size_bytes": b.size_bytes,
                "document_count": b.document_count,
                "retention_days": b.retention_days,
                "error_message": b.error_message,
            }
            for b in backups
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/backups/{backup_id}", response_model=dict)
@rate_limit_auth
async def get_backup_details(
    request: Request,
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed information about a backup."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    if backup_id not in backup_manager.backup_metadata:
        raise HTTPException(status_code=404, detail="Backup not found")

    metadata = backup_manager.backup_metadata[backup_id]

    return {
        "backup_id": metadata.backup_id,
        "backup_type": metadata.backup_type.value,
        "status": metadata.status.value,
        "created_at": metadata.created_at,
        "completed_at": metadata.completed_at,
        "size_bytes": metadata.size_bytes,
        "document_count": metadata.document_count,
        "retention_days": metadata.retention_days,
        "error_message": metadata.error_message,
        "compression_ratio": metadata.compression_ratio,
    }


@router.post("/backups/{backup_id}/restore")
@rate_limit_auth
async def restore_backup(
    request: Request,
    backup_id: str,
    restore_request: BackupRestore,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restore documents from a backup."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    try:
        success = await backup_manager.restore_backup(
            backup_id=backup_id,
            restore_documents=restore_request.restore_documents,
            restore_jobs=restore_request.restore_jobs,
            document_ids=restore_request.document_ids,
        )

        if success:
            return {"message": "Backup restored successfully"}
        raise HTTPException(status_code=500, detail="Backup restore failed")

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.delete("/backups/{backup_id}")
@rate_limit_auth
async def delete_backup(
    request: Request,
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a backup."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    try:
        backup_manager._remove_backup(backup_id)
        return {"message": "Backup deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/backups/cleanup")
@rate_limit_auth
async def cleanup_expired_backups(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clean up expired backups."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    try:
        expired_count = backup_manager.cleanup_expired_backups()
        return {"message": f"Cleaned up {expired_count} expired backups"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/backups/stats", response_model=BackupStats)
@rate_limit_auth
async def get_backup_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get backup statistics."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    backup_manager = get_backup_manager(db)

    try:
        stats = backup_manager.get_backup_statistics()
        return BackupStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/recovery/stats", response_model=RecoveryStats)
@rate_limit_auth
async def get_recovery_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recovery statistics."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    error_handler = get_document_error_handler(db)
    recovery_manager = get_recovery_manager(db, error_handler)

    try:
        stats = recovery_manager.get_recovery_statistics()
        return RecoveryStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recovery statistics: {str(e)}"
        )


@router.post("/documents/{document_id}/rollback")
@rate_limit_auth
async def create_rollback_point(
    request: Request,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a rollback point for a document."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    state_manager = get_state_manager(db)

    try:
        rollback_id = state_manager.create_rollback_point(document_id)
        if rollback_id:
            return {"rollback_id": rollback_id, "message": "Rollback point created"}
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create rollback point: {str(e)}"
        )


@router.post("/documents/{document_id}/rollback/{rollback_id}")
@rate_limit_auth
async def rollback_document(
    request: Request,
    document_id: str,
    rollback_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rollback a document to a specific point."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    state_manager = get_state_manager(db)

    try:
        success = state_manager.rollback_to_point(document_id, rollback_id)
        if success:
            return {"message": "Document rolled back successfully"}
        raise HTTPException(status_code=404, detail="Rollback point not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


@router.get("/documents/{document_id}/rollback")
@rate_limit_auth
async def get_rollback_points(
    request: Request,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available rollback points for a document."""
    if current_user.role not in ["admin", "premium"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        rollback_points = document.processing_options.get("rollback_points", {})

        return {
            "document_id": document_id,
            "rollback_points": [
                {
                    "rollback_id": rollback_id,
                    "created_at": backup_data.get("updated_at"),
                    "status": backup_data.get("status"),
                }
                for rollback_id, backup_data in rollback_points.items()
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get rollback points: {str(e)}"
        )
