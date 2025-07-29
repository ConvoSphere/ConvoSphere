"""
Enhanced background job service with robust job management and monitoring.

This service provides advanced background job processing with job persistence,
retry mechanisms, monitoring, and comprehensive error handling.
"""

import asyncio
import signal
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from queue import Empty, PriorityQueue
from typing import Any

from loguru import logger

from backend.app.models.audit import AuditEventType, AuditSeverity
from backend.app.services.audit_service import audit_service


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(int, Enum):
    """Job priority levels."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class JobMetadata:
    """Job metadata for tracking and monitoring."""

    job_id: str
    job_type: str
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    progress: float = 0.0
    result: dict[str, Any] | None = None
    user_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None


class JobManager:
    """Enhanced job manager with persistence and monitoring."""

    def __init__(self, max_workers: int = 5, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.job_queue = PriorityQueue(maxsize=max_queue_size)
        self.running_jobs: dict[str, JobMetadata] = {}
        self.completed_jobs: dict[str, JobMetadata] = {}
        self.failed_jobs: dict[str, JobMetadata] = {}

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.worker_thread = None
        self.monitor_thread = None

        # Job handlers
        self.job_handlers: dict[str, Callable] = {}

        # Statistics
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "cancelled_jobs": 0,
            "avg_processing_time": 0.0,
        }

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down job manager...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def register_job_handler(self, job_type: str, handler: Callable):
        """Register a job handler for a specific job type."""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered job handler for type: {job_type}")

    def start(self):
        """Start the job manager."""
        if self.running:
            return

        self.running = True

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("Enhanced job manager started")

    def stop(self):
        """Stop the job manager gracefully."""
        if not self.running:
            return

        logger.info("Stopping job manager...")
        self.running = False

        # Cancel all running jobs
        for job_id in list(self.running_jobs.keys()):
            self.cancel_job(job_id)

        # Wait for threads to finish
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

        # Shutdown executor
        self.executor.shutdown(wait=True, timeout=30)

        logger.info("Job manager stopped")

    def _worker_loop(self):
        """Main worker loop for processing jobs."""
        while self.running:
            try:
                # Get next job from queue
                try:
                    priority, job_metadata = self.job_queue.get(timeout=1)
                except Empty:
                    continue

                # Check if we can start a new job
                if len(self.running_jobs) >= self.max_workers:
                    # Put job back in queue
                    self.job_queue.put((priority, job_metadata))
                    time.sleep(1)
                    continue

                # Start job processing
                self._start_job(job_metadata)

            except Exception as e:
                logger.exception(f"Error in worker loop: {e}")
                time.sleep(1)

    def _monitor_loop(self):
        """Monitor loop for job health checks and cleanup."""
        while self.running:
            try:
                # Clean up completed jobs
                self._cleanup_completed_jobs()

                # Check for stuck jobs
                self._check_stuck_jobs()

                # Update statistics
                self._update_statistics()

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Error in monitor loop: {e}")
                time.sleep(30)

    def _start_job(self, job_metadata: JobMetadata):
        """Start processing a job."""
        job_metadata.status = JobStatus.RUNNING
        job_metadata.started_at = datetime.now(UTC)
        self.running_jobs[job_metadata.job_id] = job_metadata

        # Submit to executor
        future = self.executor.submit(self._execute_job, job_metadata)
        future.add_done_callback(lambda f: self._job_completed(job_metadata.job_id, f))

        # Log job start
        asyncio.create_task(
            audit_service.log_event(
                event_type=AuditEventType.SYSTEM_MAINTENANCE,
                description=f"Background job started: {job_metadata.job_type}",
                user_id=job_metadata.user_id,
                details={
                    "job_id": job_metadata.job_id,
                    "job_type": job_metadata.job_type,
                    "priority": job_metadata.priority.value,
                },
                severity=AuditSeverity.INFO,
            )
        )

    def _execute_job(self, job_metadata: JobMetadata) -> dict[str, Any]:
        """Execute a job with error handling and retries."""
        job_id = job_metadata.job_id
        job_type = job_metadata.job_type

        try:
            # Get job handler
            handler = self.job_handlers.get(job_type)
            if not handler:
                raise ValueError(f"No handler registered for job type: {job_type}")

            # Execute job
            result = handler(job_metadata)

            # Update job metadata
            job_metadata.status = JobStatus.COMPLETED
            job_metadata.completed_at = datetime.now(UTC)
            job_metadata.progress = 100.0
            job_metadata.result = result

            logger.info(f"Job {job_id} completed successfully")
            return result

        except Exception as e:
            logger.exception(f"Job {job_id} failed: {e}")

            # Handle retries
            if job_metadata.retry_count < job_metadata.max_retries:
                job_metadata.retry_count += 1
                job_metadata.status = JobStatus.RETRYING
                job_metadata.error_message = str(e)

                # Schedule retry with exponential backoff
                retry_delay = min(300, 2**job_metadata.retry_count)  # Max 5 minutes
                threading.Timer(
                    retry_delay, lambda: self._retry_job(job_metadata)
                ).start()

                logger.info(
                    f"Job {job_id} scheduled for retry {job_metadata.retry_count}/{job_metadata.max_retries}"
                )
                return {"error": str(e), "retry_count": job_metadata.retry_count}
            # Job failed permanently
            job_metadata.status = JobStatus.FAILED
            job_metadata.completed_at = datetime.now(UTC)
            job_metadata.error_message = str(e)

            # Log failure
            asyncio.create_task(
                audit_service.log_event(
                    event_type=AuditEventType.SYSTEM_ERROR,
                    description=f"Background job failed permanently: {job_type}",
                    user_id=job_metadata.user_id,
                    details={
                        "job_id": job_metadata.job_id,
                        "job_type": job_metadata.job_type,
                        "error": str(e),
                        "retry_count": job_metadata.retry_count,
                    },
                    severity=AuditSeverity.ERROR,
                )
            )

            return {"error": str(e), "failed": True}

    def _retry_job(self, job_metadata: JobMetadata):
        """Retry a failed job."""
        job_metadata.status = JobStatus.PENDING
        job_metadata.started_at = None
        job_metadata.completed_at = None
        job_metadata.progress = 0.0

        # Re-queue with higher priority
        priority = job_metadata.priority.value + 1
        self.job_queue.put((priority, job_metadata))

    def _job_completed(self, job_id: str, future):
        """Handle job completion."""
        if job_id in self.running_jobs:
            job_metadata = self.running_jobs.pop(job_id)

            try:
                future.result()
                if job_metadata.status == JobStatus.COMPLETED:
                    self.completed_jobs[job_id] = job_metadata
                    self.stats["completed_jobs"] += 1
                else:
                    self.failed_jobs[job_id] = job_metadata
                    self.stats["failed_jobs"] += 1
            except Exception as e:
                logger.exception(f"Error getting job result for {job_id}: {e}")
                job_metadata.status = JobStatus.FAILED
                job_metadata.error_message = str(e)
                self.failed_jobs[job_id] = job_metadata
                self.stats["failed_jobs"] += 1

    def _cleanup_completed_jobs(self):
        """Clean up old completed jobs."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)

        # Clean completed jobs older than 24 hours
        old_completed = [
            job_id
            for job_id, job in self.completed_jobs.items()
            if job.completed_at and job.completed_at < cutoff_time
        ]
        for job_id in old_completed:
            del self.completed_jobs[job_id]

        # Clean failed jobs older than 7 days
        cutoff_time_failed = datetime.now(UTC) - timedelta(days=7)
        old_failed = [
            job_id
            for job_id, job in self.failed_jobs.items()
            if job.completed_at and job.completed_at < cutoff_time_failed
        ]
        for job_id in old_failed:
            del self.failed_jobs[job_id]

    def _check_stuck_jobs(self):
        """Check for stuck jobs and handle them."""
        current_time = datetime.now(UTC)
        stuck_timeout = timedelta(hours=2)  # 2 hours timeout

        stuck_jobs = []
        for job_id, job in self.running_jobs.items():
            if job.started_at and (current_time - job.started_at) > stuck_timeout:
                stuck_jobs.append(job_id)

        for job_id in stuck_jobs:
            logger.warning(f"Job {job_id} appears to be stuck, cancelling...")
            self.cancel_job(job_id)

    def _update_statistics(self):
        """Update job statistics."""
        total_completed = len(self.completed_jobs)
        if total_completed > 0:
            total_time = sum(
                (job.completed_at - job.started_at).total_seconds()
                for job in self.completed_jobs.values()
                if job.completed_at and job.started_at
            )
            self.stats["avg_processing_time"] = total_time / total_completed

    def submit_job(
        self,
        job_type: str,
        priority: JobPriority = JobPriority.NORMAL,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs,
    ) -> str:
        """Submit a new job to the queue."""
        if self.job_queue.qsize() >= self.max_queue_size:
            raise RuntimeError("Job queue is full")

        job_id = str(uuid.uuid4())
        job_metadata = JobMetadata(
            job_id=job_id,
            job_type=job_type,
            status=JobStatus.PENDING,
            priority=priority,
            created_at=datetime.now(UTC),
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )

        # Add job data to metadata
        job_metadata.result = kwargs

        # Add to queue
        self.job_queue.put((priority.value, job_metadata))
        self.stats["total_jobs"] += 1

        logger.info(f"Job {job_id} submitted: {job_type}")
        return job_id

    def get_job_status(self, job_id: str) -> JobMetadata | None:
        """Get job status and metadata."""
        # Check running jobs
        if job_id in self.running_jobs:
            return self.running_jobs[job_id]

        # Check completed jobs
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id]

        # Check failed jobs
        if job_id in self.failed_jobs:
            return self.failed_jobs[job_id]

        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self.running_jobs:
            job_metadata = self.running_jobs.pop(job_id)
            job_metadata.status = JobStatus.CANCELLED
            job_metadata.completed_at = datetime.now(UTC)
            self.stats["cancelled_jobs"] += 1

            logger.info(f"Job {job_id} cancelled")
            return True

        return False

    def get_job_statistics(self) -> dict[str, Any]:
        """Get job statistics."""
        return {
            **self.stats,
            "running_jobs": len(self.running_jobs),
            "completed_jobs": len(self.completed_jobs),
            "failed_jobs": len(self.failed_jobs),
            "queue_size": self.job_queue.qsize(),
            "max_workers": self.max_workers,
        }

    def get_recent_jobs(self, limit: int = 50) -> list[JobMetadata]:
        """Get recent jobs (running, completed, failed)."""
        all_jobs = []
        all_jobs.extend(self.running_jobs.values())
        all_jobs.extend(self.completed_jobs.values())
        all_jobs.extend(self.failed_jobs.values())

        # Sort by creation time (newest first)
        all_jobs.sort(key=lambda x: x.created_at, reverse=True)
        return all_jobs[:limit]


# Global job manager instance
job_manager = JobManager()


# Convenience functions
def submit_background_job(
    job_type: str,
    priority: JobPriority = JobPriority.NORMAL,
    user_id: str | None = None,
    **kwargs,
) -> str:
    """Submit a background job."""
    return job_manager.submit_job(job_type, priority, user_id, **kwargs)


def get_job_status(job_id: str) -> JobMetadata | None:
    """Get job status."""
    return job_manager.get_job_status(job_id)


def cancel_background_job(job_id: str) -> bool:
    """Cancel a background job."""
    return job_manager.cancel_job(job_id)


def get_job_statistics() -> dict[str, Any]:
    """Get job statistics."""
    return job_manager.get_job_statistics()


# Example job handlers
def document_processing_handler(job_metadata: JobMetadata) -> dict[str, Any]:
    """Example handler for document processing jobs."""
    # Simulate document processing
    time.sleep(5)
    return {"processed": True, "document_id": job_metadata.resource_id}


def email_sending_handler(job_metadata: JobMetadata) -> dict[str, Any]:
    """Example handler for email sending jobs."""
    # Simulate email sending
    time.sleep(2)
    return {"sent": True, "recipient": job_metadata.result.get("recipient")}


# Register default handlers
job_manager.register_job_handler("document_processing", document_processing_handler)
job_manager.register_job_handler("email_sending", email_sending_handler)
