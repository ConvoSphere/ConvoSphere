"""
Backup manager for document processing operations.

This module provides automatic backup strategies for documents and their
processing states with configurable retention policies.
"""

import json
import os
import shutil
import tarfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.knowledge import Document, DocumentChunk, DocumentProcessingJob


class BackupType(Enum):
    """Types of backups."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    METADATA_ONLY = "metadata_only"


class BackupStatus(Enum):
    """Backup status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class BackupMetadata:
    """Metadata for a backup."""

    backup_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: datetime | None = None
    size_bytes: int = 0
    document_count: int = 0
    chunk_count: int = 0
    error_message: str | None = None
    retention_days: int = 30
    compression_ratio: float = 1.0


@dataclass
class DocumentBackup:
    """Backup data for a document."""

    document_id: str
    document_data: dict[str, Any]
    chunks_data: list[dict[str, Any]]
    backup_timestamp: datetime
    file_path: str | None = None


class DocumentBackupManager:
    """Manages automatic backups for documents and processing states."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.backup_dir = Path(self.settings.storage.backup_dir or "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup configuration
        self.auto_backup_enabled = getattr(self.settings, "auto_backup_enabled", True)
        self.backup_retention_days = getattr(self.settings, "backup_retention_days", 30)
        self.backup_compression = getattr(self.settings, "backup_compression", True)
        self.backup_schedule_hours = getattr(self.settings, "backup_schedule_hours", 24)

        # Metadata storage
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.backup_metadata: dict[str, BackupMetadata] = self._load_metadata()

    def _load_metadata(self) -> dict[str, BackupMetadata]:
        """Load backup metadata from file."""
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file) as f:
                data = json.load(f)
                return {
                    backup_id: BackupMetadata(**metadata_data)
                    for backup_id, metadata_data in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load backup metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save backup metadata to file."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(
                    {
                        backup_id: asdict(metadata)
                        for backup_id, metadata in self.backup_metadata.items()
                    },
                    f,
                    indent=2,
                    default=str,
                )
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        document_ids: list[str] | None = None,
        retention_days: int | None = None,
    ) -> str:
        """
        Create a backup of documents and their processing states.

        Args:
            backup_type: Type of backup to create
            document_ids: Specific documents to backup (None for all)
            retention_days: Retention period in days

        Returns:
            str: Backup ID
        """
        backup_id = f"backup_{int(datetime.utcnow().timestamp())}"

        # Create backup metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            retention_days=retention_days or self.backup_retention_days,
        )

        self.backup_metadata[backup_id] = metadata
        self._save_metadata()

        try:
            # Create backup directory
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)

            # Backup documents
            document_backups = await self._backup_documents(
                backup_path, document_ids, backup_type
            )

            # Backup processing jobs
            job_backups = await self._backup_processing_jobs(backup_path, document_ids)

            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "backup_type": backup_type.value,
                "created_at": datetime.utcnow().isoformat(),
                "document_count": len(document_backups),
                "job_count": len(job_backups),
                "documents": [doc.document_id for doc in document_backups],
                "compression": self.backup_compression,
            }

            # Save manifest
            manifest_path = backup_path / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            # Compress backup if enabled
            if self.backup_compression:
                await self._compress_backup(backup_path)

            # Update metadata
            metadata.status = BackupStatus.COMPLETED
            metadata.completed_at = datetime.utcnow()
            metadata.document_count = len(document_backups)
            metadata.size_bytes = self._get_backup_size(backup_path)

            self._save_metadata()

            logger.info(f"Backup {backup_id} completed successfully")
            return backup_id

        except Exception as e:
            metadata.status = BackupStatus.FAILED
            metadata.error_message = str(e)
            self._save_metadata()
            logger.error(f"Backup {backup_id} failed: {e}")
            raise

    async def _backup_documents(
        self, backup_path: Path, document_ids: list[str] | None, backup_type: BackupType
    ) -> list[DocumentBackup]:
        """Backup documents and their chunks."""
        document_backups = []

        # Query documents
        query = self.db.query(Document)
        if document_ids:
            query = query.filter(Document.id.in_(document_ids))

        documents = query.all()

        for document in documents:
            try:
                # Get document chunks
                chunks = (
                    self.db.query(DocumentChunk)
                    .filter(DocumentChunk.document_id == document.id)
                    .all()
                )

                # Prepare document data
                document_data = {
                    "id": str(document.id),
                    "title": document.title,
                    "description": document.description,
                    "file_name": document.file_name,
                    "file_path": document.file_path,
                    "file_type": document.file_type,
                    "file_size": document.file_size,
                    "mime_type": document.mime_type,
                    "status": document.status,
                    "author": document.author,
                    "source": document.source,
                    "language": document.language,
                    "year": document.year,
                    "version": document.version,
                    "keywords": document.keywords,
                    "document_type": document.document_type,
                    "processing_engine": document.processing_engine,
                    "processing_options": document.processing_options,
                    "page_count": document.page_count,
                    "word_count": document.word_count,
                    "character_count": document.character_count,
                    "error_message": document.error_message,
                    "user_id": str(document.user_id),
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat(),
                    "processed_at": (
                        document.processed_at.isoformat()
                        if document.processed_at
                        else None
                    ),
                }

                # Prepare chunks data
                chunks_data = []
                for chunk in chunks:
                    chunk_data = {
                        "id": str(chunk.id),
                        "document_id": str(chunk.document_id),
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "chunk_size": chunk.chunk_size,
                        "token_count": chunk.token_count,
                        "tokens": chunk.tokens,
                        "embedding": chunk.embedding,
                        "embedding_model": chunk.embedding_model,
                        "embedding_created_at": (
                            chunk.embedding_created_at.isoformat()
                            if chunk.embedding_created_at
                            else None
                        ),
                        "chunk_type": chunk.chunk_type,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title,
                        "table_id": chunk.table_id,
                        "figure_id": chunk.figure_id,
                        "chunk_metadata": chunk.chunk_metadata,
                        "created_at": chunk.created_at.isoformat(),
                        "updated_at": chunk.updated_at.isoformat(),
                    }
                    chunks_data.append(chunk_data)

                # Copy file if full backup
                file_path = None
                if backup_type == BackupType.FULL and document.file_path:
                    file_backup_path = (
                        backup_path / "files" / f"{document.id}_{document.file_name}"
                    )
                    file_backup_path.parent.mkdir(exist_ok=True)

                    if Path(document.file_path).exists():
                        shutil.copy2(document.file_path, file_backup_path)
                        file_path = str(file_backup_path)

                # Create document backup
                document_backup = DocumentBackup(
                    document_id=str(document.id),
                    document_data=document_data,
                    chunks_data=chunks_data,
                    file_path=file_path,
                    backup_timestamp=datetime.utcnow(),
                )

                # Save document backup
                doc_backup_path = backup_path / "documents" / f"{document.id}.json"
                doc_backup_path.parent.mkdir(exist_ok=True)

                with open(doc_backup_path, "w") as f:
                    json.dump(asdict(document_backup), f, indent=2, default=str)

                document_backups.append(document_backup)

            except Exception as e:
                logger.error(f"Failed to backup document {document.id}: {e}")
                continue

        return document_backups

    async def _backup_processing_jobs(
        self, backup_path: Path, document_ids: list[str] | None
    ) -> list[dict[str, Any]]:
        """Backup processing jobs."""
        job_backups = []

        # Query processing jobs
        query = self.db.query(DocumentProcessingJob)
        if document_ids:
            query = query.filter(DocumentProcessingJob.document_id.in_(document_ids))

        jobs = query.all()

        for job in jobs:
            try:
                job_data = {
                    "id": str(job.id),
                    "document_id": str(job.document_id),
                    "user_id": str(job.user_id),
                    "job_type": job.job_type,
                    "status": job.status,
                    "priority": job.priority,
                    "processing_engine": job.processing_engine,
                    "processing_options": job.processing_options,
                    "progress": job.progress,
                    "current_step": job.current_step,
                    "total_steps": job.total_steps,
                    "error_message": job.error_message,
                    "retry_count": job.retry_count,
                    "max_retries": job.max_retries,
                    "created_at": job.created_at.isoformat(),
                    "started_at": (
                        job.started_at.isoformat() if job.started_at else None
                    ),
                    "completed_at": (
                        job.completed_at.isoformat() if job.completed_at else None
                    ),
                }

                job_backups.append(job_data)

            except Exception as e:
                logger.error(f"Failed to backup job {job.id}: {e}")
                continue

        # Save jobs backup
        jobs_backup_path = backup_path / "jobs.json"
        with open(jobs_backup_path, "w") as f:
            json.dump(job_backups, f, indent=2, default=str)

        return job_backups

    async def _compress_backup(self, backup_path: Path):
        """Compress backup directory."""
        try:
            # Create compressed archive
            archive_path = backup_path.with_suffix(".tar.gz")

            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)

            # Remove uncompressed directory
            shutil.rmtree(backup_path)

            logger.info(f"Backup compressed: {archive_path}")

        except Exception as e:
            logger.error(f"Failed to compress backup: {e}")

    def _get_backup_size(self, backup_path: Path) -> int:
        """Get size of backup in bytes."""
        try:
            if backup_path.is_file():
                return backup_path.stat().st_size
            total_size = 0
            for file_path in backup_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0

    async def restore_backup(
        self,
        backup_id: str,
        restore_documents: bool = True,
        restore_jobs: bool = False,
        document_ids: list[str] | None = None,
    ) -> bool:
        """
        Restore documents from a backup.

        Args:
            backup_id: ID of the backup to restore
            restore_documents: Whether to restore documents
            restore_jobs: Whether to restore processing jobs
            document_ids: Specific documents to restore (None for all)

        Returns:
            bool: True if restore succeeded
        """
        if backup_id not in self.backup_metadata:
            raise ValueError(f"Backup {backup_id} not found")

        self.backup_metadata[backup_id]
        backup_path = self.backup_dir / backup_id

        # Check if backup is compressed
        compressed_path = backup_path.with_suffix(".tar.gz")
        if compressed_path.exists():
            await self._decompress_backup(compressed_path, backup_path)

        if not backup_path.exists():
            raise ValueError(f"Backup directory not found: {backup_path}")

        try:
            # Load manifest
            manifest_path = backup_path / "manifest.json"
            if not manifest_path.exists():
                raise ValueError("Backup manifest not found")

            with open(manifest_path) as f:
                json.load(f)

            # Restore documents
            if restore_documents:
                await self._restore_documents(backup_path, document_ids)

            # Restore jobs
            if restore_jobs:
                await self._restore_processing_jobs(backup_path, document_ids)

            logger.info(f"Backup {backup_id} restored successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}: {e}")
            raise

    async def _decompress_backup(self, compressed_path: Path, extract_path: Path):
        """Decompress backup archive."""
        try:
            with tarfile.open(compressed_path, "r:gz") as tar:
                # Security: Validate tar members before extraction
                for member in tar.getmembers():
                    # Check for path traversal attacks
                    if member.name.startswith(("/", "..", "~")):
                        raise ValueError(f"Dangerous path in archive: {member.name}")
                    # Check for absolute paths
                    if os.path.isabs(member.name):
                        raise ValueError(f"Absolute path in archive: {member.name}")
                    # Check for symlinks (potential security risk)
                    if member.issym() or member.islnk():
                        raise ValueError(f"Symlink in archive: {member.name}")

                # Extract to specific directory
                tar.extractall(extract_path.parent, members=tar.getmembers())
        except Exception as e:
            logger.error(f"Failed to decompress backup: {e}")
            raise

    async def _restore_documents(
        self, backup_path: Path, document_ids: list[str] | None
    ):
        """Restore documents from backup."""
        documents_path = backup_path / "documents"
        if not documents_path.exists():
            return

        for doc_file in documents_path.glob("*.json"):
            try:
                with open(doc_file) as f:
                    backup_data = json.load(f)

                document_backup = DocumentBackup(**backup_data)

                # Skip if not in document_ids filter
                if document_ids and document_backup.document_id not in document_ids:
                    continue

                # Check if document exists
                existing_doc = (
                    self.db.query(Document)
                    .filter(Document.id == document_backup.document_id)
                    .first()
                )

                if existing_doc:
                    # Update existing document
                    for key, value in document_backup.document_data.items():
                        if hasattr(existing_doc, key) and key not in [
                            "id",
                            "created_at",
                        ]:
                            setattr(existing_doc, key, value)
                    existing_doc.updated_at = datetime.utcnow()
                else:
                    # Create new document
                    doc_data = document_backup.document_data.copy()
                    doc_data["id"] = document_backup.document_id
                    doc_data["created_at"] = datetime.fromisoformat(
                        doc_data["created_at"]
                    )
                    doc_data["updated_at"] = datetime.fromisoformat(
                        doc_data["updated_at"]
                    )
                    if doc_data["processed_at"]:
                        doc_data["processed_at"] = datetime.fromisoformat(
                            doc_data["processed_at"]
                        )

                    new_doc = Document(**doc_data)
                    self.db.add(new_doc)

                # Restore chunks
                await self._restore_chunks(document_backup)

                # Restore file if it exists
                if (
                    document_backup.file_path
                    and Path(document_backup.file_path).exists()
                ):
                    original_path = document_backup.document_data["file_path"]
                    if original_path and not Path(original_path).exists():
                        Path(original_path).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(document_backup.file_path, original_path)

            except Exception as e:
                logger.error(f"Failed to restore document {doc_file}: {e}")
                continue

        self.db.commit()

    async def _restore_chunks(self, document_backup: DocumentBackup):
        """Restore document chunks."""
        try:
            # Delete existing chunks
            from backend.app.models.knowledge import DocumentChunk

            self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_backup.document_id
            ).delete()

            # Create new chunks
            for chunk_data in document_backup.chunks_data:
                chunk_data["id"] = chunk_data["id"]
                chunk_data["document_id"] = chunk_data["document_id"]
                chunk_data["created_at"] = datetime.fromisoformat(
                    chunk_data["created_at"]
                )
                chunk_data["updated_at"] = datetime.fromisoformat(
                    chunk_data["updated_at"]
                )
                if chunk_data["embedding_created_at"]:
                    chunk_data["embedding_created_at"] = datetime.fromisoformat(
                        chunk_data["embedding_created_at"]
                    )

                from backend.app.models.knowledge import DocumentChunk

                new_chunk = DocumentChunk(**chunk_data)
                self.db.add(new_chunk)

        except Exception as e:
            logger.error(
                f"Failed to restore chunks for document {document_backup.document_id}: {e}"
            )

    async def _restore_processing_jobs(
        self, backup_path: Path, document_ids: list[str] | None
    ):
        """Restore processing jobs from backup."""
        jobs_path = backup_path / "jobs.json"
        if not jobs_path.exists():
            return

        try:
            with open(jobs_path) as f:
                jobs_data = json.load(f)

            for job_data in jobs_data:
                # Skip if not in document_ids filter
                if document_ids and job_data["document_id"] not in document_ids:
                    continue

                # Check if job exists
                existing_job = (
                    self.db.query(DocumentProcessingJob)
                    .filter(DocumentProcessingJob.id == job_data["id"])
                    .first()
                )

                if existing_job:
                    # Update existing job
                    for key, value in job_data.items():
                        if hasattr(existing_job, key) and key not in [
                            "id",
                            "created_at",
                        ]:
                            setattr(existing_job, key, value)
                else:
                    # Create new job
                    job_data["id"] = job_data["id"]
                    job_data["created_at"] = datetime.fromisoformat(
                        job_data["created_at"]
                    )
                    if job_data["started_at"]:
                        job_data["started_at"] = datetime.fromisoformat(
                            job_data["started_at"]
                        )
                    if job_data["completed_at"]:
                        job_data["completed_at"] = datetime.fromisoformat(
                            job_data["completed_at"]
                        )

                    new_job = DocumentProcessingJob(**job_data)
                    self.db.add(new_job)

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to restore processing jobs: {e}")

    def cleanup_expired_backups(self) -> int:
        """Remove expired backups based on retention policy."""
        expired_count = 0
        current_time = datetime.utcnow()

        for backup_id, metadata in list(self.backup_metadata.items()):
            if metadata.status == BackupStatus.FAILED:
                # Remove failed backups immediately
                self._remove_backup(backup_id)
                expired_count += 1
                continue

            # Check retention period
            expiration_date = metadata.created_at + timedelta(
                days=metadata.retention_days
            )
            if current_time > expiration_date:
                self._remove_backup(backup_id)
                expired_count += 1

        return expired_count

    def _remove_backup(self, backup_id: str):
        """Remove a backup and its metadata."""
        try:
            # Remove backup files
            backup_path = self.backup_dir / backup_id
            compressed_path = backup_path.with_suffix(".tar.gz")

            if backup_path.exists():
                shutil.rmtree(backup_path)
            elif compressed_path.exists():
                compressed_path.unlink()

            # Remove metadata
            if backup_id in self.backup_metadata:
                del self.backup_metadata[backup_id]
                self._save_metadata()

            logger.info(f"Removed expired backup: {backup_id}")

        except Exception as e:
            logger.error(f"Failed to remove backup {backup_id}: {e}")

    def get_backup_statistics(self) -> dict[str, Any]:
        """Get backup statistics."""
        total_backups = len(self.backup_metadata)
        successful_backups = sum(
            1
            for m in self.backup_metadata.values()
            if m.status == BackupStatus.COMPLETED
        )
        failed_backups = sum(
            1 for m in self.backup_metadata.values() if m.status == BackupStatus.FAILED
        )

        total_size = sum(m.size_bytes for m in self.backup_metadata.values())
        total_documents = sum(m.document_count for m in self.backup_metadata.values())

        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": (
                successful_backups / total_backups if total_backups > 0 else 0
            ),
            "total_size_bytes": total_size,
            "total_documents": total_documents,
            "average_backup_size": (
                total_size / total_backups if total_backups > 0 else 0
            ),
        }


# Global backup manager instance
_backup_manager: DocumentBackupManager | None = None


def get_backup_manager(db: Session) -> DocumentBackupManager:
    """Get or create backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = DocumentBackupManager(db)
    return _backup_manager
