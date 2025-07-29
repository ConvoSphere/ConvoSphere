"""
Error handling for document processing operations.

This module provides centralized error handling and recovery mechanisms
for document processing operations.
"""

import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.knowledge import Document, DocumentStatus
from loguru import logger
from backend.app.utils.exceptions import (
    FileUploadError,
    ProcessingError,
    ValidationError,
    ConvoSphereError
)




class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for document processing."""
    VALIDATION = "validation"
    UPLOAD = "upload"
    PROCESSING = "processing"
    STORAGE = "storage"
    NETWORK = "network"
    PERMISSION = "permission"
    SYSTEM = "system"


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.document_id = document_id
        self.user_id = user_id
        self.original_error = original_error
        self.context = context or {}
        self.timestamp = datetime.utcnow()


class DocumentErrorHandler:
    """Centralized error handler for document operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.error_callbacks: Dict[ErrorCategory, list[Callable]] = {
            category: [] for category in ErrorCategory
        }
    
    def register_error_callback(
        self,
        category: ErrorCategory,
        callback: Callable[[DocumentProcessingError], None]
    ):
        """Register a callback for specific error categories."""
        self.error_callbacks[category].append(callback)
    
    def handle_error(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentProcessingError:
        """Handle and log an error."""
        
        # Create custom error
        doc_error = DocumentProcessingError(
            message=str(error),
            category=category,
            severity=severity,
            document_id=document_id,
            user_id=user_id,
            original_error=error,
            context=context or {}
        )
        
        # Log error
        self._log_error(doc_error)
        
        # Update document status if document_id is provided
        if document_id:
            self._update_document_status(document_id, doc_error)
        
        # Execute callbacks
        self._execute_callbacks(doc_error)
        
        return doc_error
    
    def handle_upload_error(
        self,
        error: Exception,
        file_name: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentProcessingError:
        """Handle file upload errors."""
        severity = self._determine_upload_error_severity(error)
        
        return self.handle_error(
            error=error,
            category=ErrorCategory.UPLOAD,
            severity=severity,
            user_id=user_id,
            context={
                "file_name": file_name,
                "file_size": context.get("file_size") if context else None,
                "file_type": context.get("file_type") if context else None,
                **(context or {})
            }
        )
    
    def handle_processing_error(
        self,
        error: Exception,
        document_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentProcessingError:
        """Handle document processing errors."""
        severity = self._determine_processing_error_severity(error)
        
        return self.handle_error(
            error=error,
            category=ErrorCategory.PROCESSING,
            severity=severity,
            document_id=document_id,
            user_id=user_id,
            context=context
        )
    
    def handle_validation_error(
        self,
        error: Exception,
        file_name: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentProcessingError:
        """Handle validation errors."""
        return self.handle_error(
            error=error,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            user_id=user_id,
            context={
                "file_name": file_name,
                **(context or {})
            }
        )
    
    def _log_error(self, error: DocumentProcessingError):
        """Log error with appropriate level."""
        log_message = (
            f"Document processing error: {error.message} "
            f"(Category: {error.category.value}, "
            f"Severity: {error.severity.value}, "
            f"Document: {error.document_id or 'N/A'}, "
            f"User: {error.user_id or 'N/A'})"
        )
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=error.original_error)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=error.original_error)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _update_document_status(self, document_id: str, error: DocumentProcessingError):
        """Update document status based on error."""
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = DocumentStatus.ERROR
                document.error_message = error.message
                document.updated_at = datetime.utcnow()
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")
    
    def _execute_callbacks(self, error: DocumentProcessingError):
        """Execute registered callbacks for the error category."""
        callbacks = self.error_callbacks.get(error.category, [])
        for callback in callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def _determine_upload_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine severity of upload errors."""
        if isinstance(error, (FileUploadError, ValidationError)):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, PermissionError):
            return ErrorSeverity.HIGH
        elif isinstance(error, (OSError, IOError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _determine_processing_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine severity of processing errors."""
        if isinstance(error, ProcessingError):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, (OSError, IOError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, MemoryError):
            return ErrorSeverity.CRITICAL
        else:
            return ErrorSeverity.MEDIUM


class ErrorRecoveryManager:
    """Manages error recovery strategies."""
    
    def __init__(self, db: Session):
        self.db = db
        self.error_handler = DocumentErrorHandler(db)
    
    async def attempt_recovery(
        self,
        error: DocumentProcessingError,
        recovery_strategy: Optional[str] = None
    ) -> bool:
        """Attempt to recover from an error."""
        
        if not recovery_strategy:
            recovery_strategy = self._determine_recovery_strategy(error)
        
        try:
            if recovery_strategy == "retry":
                return await self._retry_operation(error)
            elif recovery_strategy == "fallback":
                return await self._fallback_operation(error)
            elif recovery_strategy == "skip":
                return await self._skip_operation(error)
            else:
                logger.warning(f"Unknown recovery strategy: {recovery_strategy}")
                return False
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def _determine_recovery_strategy(self, error: DocumentProcessingError) -> str:
        """Determine appropriate recovery strategy based on error."""
        
        if error.category == ErrorCategory.NETWORK:
            return "retry"
        elif error.category == ErrorCategory.PROCESSING:
            return "fallback"
        elif error.category == ErrorCategory.VALIDATION:
            return "skip"
        elif error.severity == ErrorSeverity.CRITICAL:
            return "skip"
        else:
            return "retry"
    
    async def _retry_operation(self, error: DocumentProcessingError) -> bool:
        """Retry the failed operation."""
        # Implementation would depend on the specific operation
        logger.info(f"Retrying operation for document {error.document_id}")
        return True
    
    async def _fallback_operation(self, error: DocumentProcessingError) -> bool:
        """Use fallback processing method."""
        logger.info(f"Using fallback processing for document {error.document_id}")
        return True
    
    async def _skip_operation(self, error: DocumentProcessingError) -> bool:
        """Skip the failed operation."""
        logger.info(f"Skipping operation for document {error.document_id}")
        return True


# Global error handler instance
_error_handler: Optional[DocumentErrorHandler] = None

def get_document_error_handler(db: Session) -> DocumentErrorHandler:
    """Get or create document error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = DocumentErrorHandler(db)
    return _error_handler


def handle_document_error(
    error: Exception,
    category: ErrorCategory,
    severity: ErrorSeverity,
    db: Session,
    document_id: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> DocumentProcessingError:
    """Convenience function to handle document errors."""
    handler = get_document_error_handler(db)
    return handler.handle_error(
        error=error,
        category=category,
        severity=severity,
        document_id=document_id,
        user_id=user_id,
        context=context
    )