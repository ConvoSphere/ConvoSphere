"""
Pydantic schemas for backup and recovery operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BackupCreate(BaseModel):
    """Schema for creating a backup."""
    backup_type: str = Field(..., description="Type of backup (full, incremental, differential, metadata_only)")
    document_ids: Optional[List[str]] = Field(None, description="Specific documents to backup")
    retention_days: Optional[int] = Field(30, description="Retention period in days")


class BackupResponse(BaseModel):
    """Schema for backup creation response."""
    backup_id: str
    status: str
    message: str


class BackupInfo(BaseModel):
    """Schema for backup information."""
    backup_id: str
    backup_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    size_bytes: int
    document_count: int
    retention_days: int
    error_message: Optional[str] = None


class BackupList(BaseModel):
    """Schema for list of backups."""
    backups: List[BackupInfo]
    total: int
    skip: int
    limit: int


class BackupRestore(BaseModel):
    """Schema for backup restore request."""
    restore_documents: bool = Field(True, description="Whether to restore documents")
    restore_jobs: bool = Field(False, description="Whether to restore processing jobs")
    document_ids: Optional[List[str]] = Field(None, description="Specific documents to restore")


class RecoveryStats(BaseModel):
    """Schema for recovery statistics."""
    total_attempts: int
    successful_recoveries: int
    overall_success_rate: float
    strategy_statistics: Dict[str, Dict[str, Any]]


class BackupStats(BaseModel):
    """Schema for backup statistics."""
    total_backups: int
    successful_backups: int
    failed_backups: int
    success_rate: float
    total_size_bytes: int
    total_documents: int
    average_backup_size: float


class RollbackPoint(BaseModel):
    """Schema for rollback point information."""
    rollback_id: str
    created_at: Optional[datetime] = None
    status: Optional[str] = None


class RollbackPoints(BaseModel):
    """Schema for list of rollback points."""
    document_id: str
    rollback_points: List[RollbackPoint]


class OperationHistory(BaseModel):
    """Schema for operation history."""
    operation_id: str
    checkpoint: Optional[Dict[str, Any]] = None
    recovery_attempts: List[Dict[str, Any]]
    total_attempts: int
    successful_recovery: bool