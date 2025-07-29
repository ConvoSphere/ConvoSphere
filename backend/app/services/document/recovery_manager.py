"""
Recovery manager for document processing operations.

This module provides advanced recovery mechanisms including automatic retries,
rollback functionality, and state management for document processing operations.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.models.knowledge import Document, DocumentStatus
from backend.app.services.document.error_handler import (
    DocumentErrorHandler,
)


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""

    RETRY = "retry"
    ROLLBACK = "rollback"
    FALLBACK = "fallback"
    SKIP = "skip"
    MANUAL = "manual"


class OperationState(Enum):
    """States of document processing operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    RECOVERED = "recovered"


@dataclass
class OperationCheckpoint:
    """Checkpoint for operation state."""

    operation_id: str
    document_id: str
    state: OperationState
    timestamp: datetime
    data: dict[str, Any]
    error: str | None = None


@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt."""

    attempt_id: str
    operation_id: str
    strategy: RecoveryStrategy
    timestamp: datetime
    success: bool
    error_message: str | None = None
    duration: float = 0.0


class DocumentRecoveryManager:
    """Manages recovery operations for document processing."""

    def __init__(self, db: Session, error_handler: DocumentErrorHandler):
        self.db = db
        self.error_handler = error_handler
        self.checkpoints: dict[str, OperationCheckpoint] = {}
        self.recovery_attempts: list[RecoveryAttempt] = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.max_retry_delay = 300  # 5 minutes

    async def execute_with_recovery(
        self,
        operation_id: str,
        document_id: str,
        operation: Callable,
        rollback_operation: Callable | None = None,
        max_retries: int = None,
        recovery_strategies: list[RecoveryStrategy] = None,
    ) -> bool:
        """
        Execute an operation with automatic recovery mechanisms.

        Args:
            operation_id: Unique identifier for the operation
            document_id: ID of the document being processed
            operation: The operation to execute
            rollback_operation: Optional rollback operation
            max_retries: Maximum number of retry attempts
            recovery_strategies: List of recovery strategies to try

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        if max_retries is None:
            max_retries = self.max_retries
        if recovery_strategies is None:
            recovery_strategies = [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.ROLLBACK,
                RecoveryStrategy.SKIP,
            ]

        # Create initial checkpoint
        checkpoint = OperationCheckpoint(
            operation_id=operation_id,
            document_id=document_id,
            state=OperationState.PENDING,
            timestamp=datetime.utcnow(),
            data={},
        )
        self.checkpoints[operation_id] = checkpoint

        # Update document status
        await self._update_document_status(document_id, DocumentStatus.PROCESSING)

        for attempt in range(max_retries + 1):
            try:
                # Execute operation
                checkpoint.state = OperationState.IN_PROGRESS
                checkpoint.timestamp = datetime.utcnow()

                result = await operation()

                # Operation succeeded
                checkpoint.state = OperationState.COMPLETED
                checkpoint.timestamp = datetime.utcnow()
                checkpoint.data["result"] = result

                await self._update_document_status(
                    document_id, DocumentStatus.PROCESSED
                )
                logger.info(f"Operation {operation_id} completed successfully")
                return True

            except Exception as e:
                # Operation failed
                checkpoint.state = OperationState.FAILED
                checkpoint.timestamp = datetime.utcnow()
                checkpoint.error = str(e)

                logger.warning(
                    f"Operation {operation_id} failed (attempt {attempt + 1}): {e}"
                )

                # Try recovery strategies
                if attempt < max_retries:
                    recovery_success = await self._attempt_recovery(
                        operation_id,
                        document_id,
                        operation,
                        rollback_operation,
                        recovery_strategies,
                        e,
                    )
                    if recovery_success:
                        checkpoint.state = OperationState.RECOVERED
                        checkpoint.timestamp = datetime.utcnow()
                        await self._update_document_status(
                            document_id, DocumentStatus.PROCESSED
                        )
                        logger.info(f"Operation {operation_id} recovered successfully")
                        return True

                    # Wait before retry
                    delay = min(self.retry_delay * (2**attempt), self.max_retry_delay)
                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted
                    await self._update_document_status(
                        document_id, DocumentStatus.ERROR, str(e)
                    )
                    logger.error(
                        f"Operation {operation_id} failed after {max_retries} retries"
                    )
                    return False

        return False

    async def _attempt_recovery(
        self,
        operation_id: str,
        document_id: str,
        operation: Callable,
        rollback_operation: Callable | None,
        strategies: list[RecoveryStrategy],
        error: Exception,
    ) -> bool:
        """Attempt recovery using specified strategies."""

        for strategy in strategies:
            recovery_attempt = RecoveryAttempt(
                attempt_id=f"{operation_id}_recovery_{len(self.recovery_attempts)}",
                operation_id=operation_id,
                strategy=strategy,
                timestamp=datetime.utcnow(),
                success=False,
            )

            start_time = time.time()

            try:
                if strategy == RecoveryStrategy.RETRY:
                    success = await self._retry_operation(operation)
                elif strategy == RecoveryStrategy.ROLLBACK:
                    success = await self._rollback_operation(
                        rollback_operation, document_id
                    )
                elif strategy == RecoveryStrategy.FALLBACK:
                    success = await self._fallback_operation(document_id)
                elif strategy == RecoveryStrategy.SKIP:
                    success = await self._skip_operation(document_id)
                else:
                    success = False

                recovery_attempt.success = success
                recovery_attempt.duration = time.time() - start_time

                if success:
                    logger.info(f"Recovery successful using strategy: {strategy.value}")
                    self.recovery_attempts.append(recovery_attempt)
                    return True
                recovery_attempt.error_message = (
                    f"Recovery strategy {strategy.value} failed"
                )

            except Exception as recovery_error:
                recovery_attempt.error_message = str(recovery_error)
                recovery_attempt.duration = time.time() - start_time
                logger.error(
                    f"Recovery strategy {strategy.value} failed: {recovery_error}"
                )

            self.recovery_attempts.append(recovery_attempt)

        return False

    async def _retry_operation(self, operation: Callable) -> bool:
        """Retry the operation."""
        try:
            await operation()
            return True
        except Exception as e:
            logger.warning(f"Retry operation failed: {e}")
            return False

    async def _rollback_operation(
        self, rollback_operation: Callable | None, document_id: str
    ) -> bool:
        """Rollback the operation."""
        if not rollback_operation:
            logger.warning("No rollback operation provided")
            return False

        try:
            await rollback_operation()

            # Update document status to indicate rollback
            await self._update_document_status(document_id, DocumentStatus.UPLOADED)

            logger.info(f"Rollback completed for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    async def _fallback_operation(self, document_id: str) -> bool:
        """Use fallback processing method."""
        try:
            # Get document
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if not document:
                return False

            # Use basic text extraction as fallback
            from backend.app.services.document.processors.text_processor import (
                TextProcessor,
            )

            text_processor = TextProcessor()
            content = text_processor.process(document.file_path)

            if content and content.strip():
                # Create basic chunks
                chunks = self._create_basic_chunks(content, document_id)

                # Save chunks to database
                for chunk in chunks:
                    self.db.add(chunk)
                self.db.commit()

                logger.info(f"Fallback processing completed for document {document_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Fallback operation failed: {e}")
            return False

    async def _skip_operation(self, document_id: str) -> bool:
        """Skip the operation and mark as completed."""
        try:
            # Mark document as processed but with warning
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if document:
                document.status = DocumentStatus.PROCESSED
                document.error_message = "Processing skipped due to errors"
                document.updated_at = datetime.utcnow()
                self.db.commit()

            logger.info(f"Operation skipped for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Skip operation failed: {e}")
            return False

    def _create_basic_chunks(self, content: str, document_id: str) -> list[Any]:
        """Create basic text chunks for fallback processing."""
        import uuid

        from backend.app.models.knowledge import DocumentChunk

        chunks = []
        chunk_size = 500
        overlap = 50

        for i in range(0, len(content), chunk_size - overlap):
            chunk_content = content[i : i + chunk_size]
            if chunk_content.strip():
                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=chunk_content,
                    chunk_size=len(chunk_content),
                    token_count=len(chunk_content.split()),
                    chunk_type="text",
                )
                chunks.append(chunk)

        return chunks

    async def _update_document_status(
        self, document_id: str, status: DocumentStatus, error_message: str | None = None
    ):
        """Update document status in database."""
        try:
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if document:
                document.status = status
                if error_message:
                    document.error_message = error_message
                document.updated_at = datetime.utcnow()

                if status == DocumentStatus.PROCESSED:
                    document.processed_at = datetime.utcnow()

                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")

    def get_operation_history(self, operation_id: str) -> dict[str, Any]:
        """Get operation history including checkpoints and recovery attempts."""
        checkpoint = self.checkpoints.get(operation_id)
        attempts = [a for a in self.recovery_attempts if a.operation_id == operation_id]

        return {
            "operation_id": operation_id,
            "checkpoint": checkpoint.__dict__ if checkpoint else None,
            "recovery_attempts": [a.__dict__ for a in attempts],
            "total_attempts": len(attempts),
            "successful_recovery": any(a.success for a in attempts),
        }

    def get_recovery_statistics(self) -> dict[str, Any]:
        """Get recovery statistics."""
        total_attempts = len(self.recovery_attempts)
        successful_recoveries = sum(1 for a in self.recovery_attempts if a.success)

        strategy_stats = {}
        for strategy in RecoveryStrategy:
            strategy_attempts = [
                a for a in self.recovery_attempts if a.strategy == strategy
            ]
            strategy_successes = sum(1 for a in strategy_attempts if a.success)
            strategy_stats[strategy.value] = {
                "attempts": len(strategy_attempts),
                "successes": strategy_successes,
                "success_rate": (
                    strategy_successes / len(strategy_attempts)
                    if strategy_attempts
                    else 0
                ),
            }

        return {
            "total_attempts": total_attempts,
            "successful_recoveries": successful_recoveries,
            "overall_success_rate": (
                successful_recoveries / total_attempts if total_attempts > 0 else 0
            ),
            "strategy_statistics": strategy_stats,
        }


class DocumentStateManager:
    """Manages document state transitions and validation."""

    def __init__(self, db: Session):
        self.db = db

    def validate_state_transition(
        self, current_status: DocumentStatus, new_status: DocumentStatus
    ) -> bool:
        """Validate if a state transition is allowed."""

        allowed_transitions = {
            DocumentStatus.UPLOADED: [DocumentStatus.PROCESSING, DocumentStatus.ERROR],
            DocumentStatus.PROCESSING: [
                DocumentStatus.PROCESSED,
                DocumentStatus.ERROR,
                DocumentStatus.REPROCESSING,
            ],
            DocumentStatus.PROCESSED: [
                DocumentStatus.REPROCESSING,
                DocumentStatus.ERROR,
            ],
            DocumentStatus.ERROR: [
                DocumentStatus.REPROCESSING,
                DocumentStatus.UPLOADED,
            ],
            DocumentStatus.REPROCESSING: [
                DocumentStatus.PROCESSED,
                DocumentStatus.ERROR,
            ],
        }

        return new_status in allowed_transitions.get(current_status, [])

    def can_rollback(self, document_id: str) -> bool:
        """Check if a document can be rolled back."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        # Can rollback if document has been processed or is in error state
        return document.status in [DocumentStatus.PROCESSED, DocumentStatus.ERROR]

    def create_rollback_point(self, document_id: str) -> str | None:
        """Create a rollback point for a document."""
        try:
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if not document:
                return None

            # Create backup of current state
            backup_data = {
                "status": document.status,
                "error_message": document.error_message,
                "processed_at": document.processed_at,
                "updated_at": document.updated_at,
            }

            # Store backup (in a real implementation, this would be in a separate table)
            # For now, we'll store it in the document's processing_options
            if not document.processing_options:
                document.processing_options = {}

            rollback_id = f"rollback_{int(time.time())}"
            document.processing_options["rollback_points"] = (
                document.processing_options.get("rollback_points", {})
            )
            document.processing_options["rollback_points"][rollback_id] = backup_data

            self.db.commit()
            return rollback_id

        except Exception as e:
            logger.error(f"Failed to create rollback point: {e}")
            return None

    def rollback_to_point(self, document_id: str, rollback_id: str) -> bool:
        """Rollback document to a specific point."""
        try:
            document = (
                self.db.query(Document).filter(Document.id == document_id).first()
            )
            if not document or not document.processing_options:
                return False

            rollback_points = document.processing_options.get("rollback_points", {})
            if rollback_id not in rollback_points:
                return False

            backup_data = rollback_points[rollback_id]

            # Restore state
            document.status = backup_data["status"]
            document.error_message = backup_data["error_message"]
            document.processed_at = backup_data["processed_at"]
            document.updated_at = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to rollback document: {e}")
            return False


# Global instances
_recovery_manager: DocumentRecoveryManager | None = None
_state_manager: DocumentStateManager | None = None


def get_recovery_manager(
    db: Session, error_handler: DocumentErrorHandler
) -> DocumentRecoveryManager:
    """Get or create recovery manager instance."""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = DocumentRecoveryManager(db, error_handler)
    return _recovery_manager


def get_state_manager(db: Session) -> DocumentStateManager:
    """Get or create state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = DocumentStateManager(db)
    return _state_manager
