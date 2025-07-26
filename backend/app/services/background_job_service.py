"""
Background job service for asynchronous document processing.

This module provides services for managing background jobs for document processing,
including job queuing, execution, and monitoring.
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Empty, PriorityQueue
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.knowledge import Document, DocumentProcessingJob, DocumentStatus
from backend.app.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class BackgroundJobService:
    """Service for managing background document processing jobs."""

    def __init__(self):
        self.job_queue = PriorityQueue()
        self.running_jobs: dict[str, threading.Thread] = {}
        self.max_workers = 3
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.running = False
        self.worker_thread = None

    def start(self):
        """Start the background job processor."""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._process_jobs, daemon=True)
        self.worker_thread.start()
        logger.info("Background job service started")

    def stop(self):
        """Stop the background job processor."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.executor.shutdown(wait=True)
        logger.info("Background job service stopped")

    def _process_jobs(self):
        """Main job processing loop."""
        while self.running:
            try:
                # Get next job from queue
                try:
                    priority, job_id = self.job_queue.get(timeout=1)
                except Empty:
                    continue

                # Check if we can start a new job
                if len(self.running_jobs) >= self.max_workers:
                    # Put job back in queue
                    self.job_queue.put((priority, job_id))
                    time.sleep(1)
                    continue

                # Start job processing
                job_thread = threading.Thread(
                    target=self._execute_job,
                    args=(job_id,),
                    daemon=True,
                )
                job_thread.start()
                self.running_jobs[job_id] = job_thread

            except Exception as e:
                logger.exception(f"Error in job processing loop: {e}")
                time.sleep(1)

    def _execute_job(self, job_id: str):
        """Execute a single job."""
        db = next(get_db())
        try:
            # Get job from database
            job = (
                db.query(DocumentProcessingJob)
                .filter(DocumentProcessingJob.id == job_id)
                .first()
            )

            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # Update job status
            job.status = "running"
            job.started_at = datetime.utcnow()
            db.commit()

            # Execute job based on type
            if job.job_type == "process":
                self._process_document_job(job, db)
            elif job.job_type == "reprocess":
                self._reprocess_document_job(job, db)
            elif job.job_type == "bulk_import":
                self._bulk_import_job(job, db)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

            # Mark job as completed
            job.status = "completed"
            job.progress = 1.0
            job.completed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            logger.exception(f"Error executing job {job_id}: {e}")
            # Update job status to failed
            try:
                job.status = "failed"
                job.error_message = str(e)
                job.retry_count += 1
                db.commit()

                # Retry job if retry count is below max
                if job.retry_count < job.max_retries:
                    self.schedule_job(job_id, priority=job.priority + 1)

            except Exception as update_error:
                logger.exception(f"Error updating job status: {update_error}")
        finally:
            # Remove from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            db.close()

    def _process_document_job(self, job: DocumentProcessingJob, db: Session):
        """Process a document processing job."""
        try:
            # Get document
            document = db.query(Document).filter(Document.id == job.document_id).first()

            if not document:
                raise ValueError(f"Document {job.document_id} not found")

            # Update progress
            job.progress = 0.1
            job.current_step = "Starting document processing"
            db.commit()

            # Create knowledge service
            knowledge_service = KnowledgeService(db)

            # Process document
            job.progress = 0.3
            job.current_step = "Processing document"
            db.commit()

            # Note: This would need to be adapted for async processing
            # For now, we'll use a synchronous approach
            success = asyncio.run(knowledge_service.process_document(str(document.id)))

            if not success:
                raise Exception("Document processing failed")

            job.progress = 1.0
            job.current_step = "Completed"
            db.commit()

        except Exception as e:
            logger.exception(f"Error in document processing job: {e}")
            raise

    def _reprocess_document_job(self, job: DocumentProcessingJob, db: Session):
        """Reprocess a document job."""
        try:
            # Get document
            document = db.query(Document).filter(Document.id == job.document_id).first()

            if not document:
                raise ValueError(f"Document {job.document_id} not found")

            # Update progress
            job.progress = 0.1
            job.current_step = "Starting document reprocessing"
            db.commit()

            # Delete existing chunks
            job.progress = 0.2
            job.current_step = "Cleaning existing chunks"
            db.commit()

            # Delete chunks from database
            from backend.app.models.knowledge import DocumentChunk

            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id,
            ).delete()

            # Delete from Weaviate
            from backend.app.services.weaviate_service import WeaviateService

            weaviate_service = WeaviateService()
            weaviate_service.delete_document_chunks(str(document.id))

            # Update document status
            document.status = DocumentStatus.UPLOADED
            document.processed_at = None
            document.error_message = None
            db.commit()

            # Process document again
            job.progress = 0.5
            job.current_step = "Reprocessing document"
            db.commit()

            knowledge_service = KnowledgeService(db)
            success = asyncio.run(knowledge_service.process_document(str(document.id)))

            if not success:
                raise Exception("Document reprocessing failed")

            job.progress = 1.0
            job.current_step = "Completed"
            db.commit()

        except Exception as e:
            logger.exception(f"Error in document reprocessing job: {e}")
            raise

    def _bulk_import_job(self, job: DocumentProcessingJob, db: Session):
        """Bulk import job."""
        try:
            processing_options = job.processing_options
            files = processing_options.get("files", [])
            default_tags = processing_options.get("default_tags", [])
            processing_opts = processing_options.get("processing_options", {})

            total_files = len(files)
            job.total_steps = total_files
            job.progress = 0.0
            job.current_step = f"Processing {total_files} files"
            db.commit()

            knowledge_service = KnowledgeService(db)

            for i, file_info in enumerate(files):
                try:
                    # Update progress
                    job.progress = i / total_files
                    job.current_step = f"Processing file {i + 1}/{total_files}: {file_info.get('name', 'Unknown')}"
                    db.commit()

                    # Create document
                    document = knowledge_service.create_document(
                        user_id=str(job.user_id),
                        title=file_info.get("title", file_info.get("name", "Untitled")),
                        file_name=file_info.get("name", "unknown"),
                        file_content=file_info.get("content", b""),
                        description=file_info.get("description"),
                        tags=default_tags + file_info.get("tags", []),
                        metadata=processing_opts,
                    )

                    # Process document
                    success = asyncio.run(
                        knowledge_service.process_document(str(document.id)),
                    )
                    if not success:
                        logger.warning(
                            f"Failed to process file {file_info.get('name')}",
                        )

                except Exception as e:
                    logger.exception(
                        f"Error processing file {file_info.get('name')}: {e}",
                    )
                    # Continue with next file

            job.progress = 1.0
            job.current_step = "Bulk import completed"
            db.commit()

        except Exception as e:
            logger.exception(f"Error in bulk import job: {e}")
            raise

    def schedule_job(self, job_id: str, priority: int = 0) -> bool:
        """Schedule a job for processing."""
        try:
            self.job_queue.put((priority, job_id))
            logger.info(f"Job {job_id} scheduled with priority {priority}")
            return True
        except Exception as e:
            logger.exception(f"Error scheduling job {job_id}: {e}")
            return False

    def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        """Get the status of a job."""
        db = next(get_db())
        try:
            job = (
                db.query(DocumentProcessingJob)
                .filter(DocumentProcessingJob.id == job_id)
                .first()
            )

            if not job:
                return None

            return {
                "id": str(job.id),
                "status": job.status,
                "progress": job.progress,
                "current_step": job.current_step,
                "error_message": job.error_message,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": (
                    job.completed_at.isoformat() if job.completed_at else None
                ),
            }
        finally:
            db.close()

    def get_running_jobs(self) -> list[str]:
        """Get list of currently running job IDs."""
        return list(self.running_jobs.keys())

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self.running_jobs:
            # Note: In a real implementation, you'd need to implement proper job cancellation
            # For now, we'll just remove it from the running jobs
            del self.running_jobs[job_id]
            return True
        return False


# Global background job service instance
background_job_service = BackgroundJobService()


def start_background_job_service():
    """Start the background job service."""
    background_job_service.start()


def stop_background_job_service():
    """Stop the background job service."""
    background_job_service.stop()
