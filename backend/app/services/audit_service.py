"""
Comprehensive audit service for logging system activities and security events.

This service provides centralized audit logging functionality for compliance,
security monitoring, and system debugging.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.audit import AuditLog, AuditEventType, AuditSeverity
from backend.app.models.user import User


class AuditService:
    """Centralized audit service for comprehensive activity logging."""

    def __init__(self):
        self._queue = asyncio.Queue()
        self._worker_task = None
        self._enabled = True
        self._batch_size = 50
        self._flush_interval = 30  # seconds

    async def start(self):
        """Start the audit service worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("Audit service started")

    async def stop(self):
        """Stop the audit service worker."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
            logger.info("Audit service stopped")

    async def _worker(self):
        """Background worker for processing audit events."""
        batch = []
        last_flush = datetime.now(timezone.utc)

        while True:
            try:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(
                        self._queue.get(), timeout=self._flush_interval
                    )
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass

                # Flush batch if full or timeout reached
                current_time = datetime.now(timezone.utc)
                if (
                    len(batch) >= self._batch_size
                    or (batch and (current_time - last_flush).seconds >= self._flush_interval)
                ):
                    if batch:
                        await self._flush_batch(batch)
                        batch = []
                        last_flush = current_time

            except Exception as e:
                logger.error(f"Error in audit worker: {e}")
                await asyncio.sleep(1)

    async def _flush_batch(self, batch: list[Dict[str, Any]]):
        """Flush a batch of audit events to the database."""
        try:
            db = next(get_db())
            try:
                for event_data in batch:
                    audit_log = AuditLog(**event_data)
                    db.add(audit_log)
                
                db.commit()
                logger.debug(f"Flushed {len(batch)} audit events")
            except Exception as e:
                db.rollback()
                logger.error(f"Error flushing audit batch: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting database session for audit: {e}")

    async def log_event(
        self,
        event_type: AuditEventType,
        description: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ):
        """Log an audit event asynchronously."""
        if not self._enabled:
            return

        event_data = {
            "id": uuid.uuid4(),
            "event_type": event_type,
            "severity": severity,
            "user_id": uuid.UUID(user_id) if user_id else None,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "description": description,
            "details": details,
            "created_at": datetime.now(timezone.utc),
        }

        await self._queue.put(event_data)

    def log_event_sync(
        self,
        event_type: AuditEventType,
        description: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ):
        """Log an audit event synchronously (for immediate logging)."""
        if not self._enabled:
            return

        try:
            db = next(get_db())
            try:
                audit_log = AuditLog(
                    event_type=event_type,
                    severity=severity,
                    user_id=uuid.UUID(user_id) if user_id else None,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    description=description,
                    details=details,
                )
                db.add(audit_log)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error logging audit event synchronously: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting database session for sync audit: {e}")

    # Convenience methods for common events
    async def log_user_login(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        session_id: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log user login event."""
        event_type = AuditEventType.USER_LOGIN
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING
        description = f"User login {'successful' if success else 'failed'}"
        
        if details is None:
            details = {}
        details["success"] = success

        await self.log_event(
            event_type=event_type,
            description=description,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=severity,
        )

    async def log_user_logout(
        self,
        user_id: str,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log user logout event."""
        await self.log_event(
            event_type=AuditEventType.USER_LOGOUT,
            description="User logout",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_permission_denied(
        self,
        user_id: Optional[str],
        resource_type: str,
        resource_id: str,
        ip_address: str,
        user_agent: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log permission denied event."""
        await self.log_event(
            event_type=AuditEventType.PERMISSION_DENIED,
            description=f"Permission denied for {resource_type} {resource_id}",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            severity=AuditSeverity.WARNING,
        )

    async def log_rate_limit_exceeded(
        self,
        user_id: Optional[str],
        ip_address: str,
        endpoint: str,
        limit: int,
        window: int,
    ):
        """Log rate limit exceeded event."""
        await self.log_event(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            description=f"Rate limit exceeded for endpoint {endpoint}",
            user_id=user_id,
            ip_address=ip_address,
            resource_type="endpoint",
            resource_id=endpoint,
            details={
                "limit": limit,
                "window": window,
                "endpoint": endpoint,
            },
            severity=AuditSeverity.WARNING,
        )

    async def log_suspicious_activity(
        self,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        activity_type: str,
        details: Dict[str, Any],
    ):
        """Log suspicious activity event."""
        await self.log_event(
            event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
            description=f"Suspicious activity detected: {activity_type}",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=AuditSeverity.ERROR,
        )

    async def log_system_event(
        self,
        event_type: AuditEventType,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ):
        """Log system event."""
        await self.log_event(
            event_type=event_type,
            description=description,
            details=details,
            severity=severity,
        )

    async def log_api_usage(
        self,
        user_id: Optional[str],
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        ip_address: str,
        user_agent: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log API usage for monitoring and analytics."""
        severity = AuditSeverity.INFO
        if status_code >= 400:
            severity = AuditSeverity.WARNING
        if status_code >= 500:
            severity = AuditSeverity.ERROR

        if details is None:
            details = {}
        details.update({
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
        })

        await self.log_event(
            event_type=AuditEventType.SYSTEM_MAINTENANCE,  # Using system event for API usage
            description=f"API {method} {endpoint} - {status_code}",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="api_endpoint",
            resource_id=endpoint,
            details=details,
            severity=severity,
        )

    def get_audit_logs(
        self,
        db: Session,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Get audit logs with filtering."""
        query = db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if severity:
            query = query.filter(AuditLog.severity == severity)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    def get_security_events(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get security-related audit events."""
        query = db.query(AuditLog).filter(AuditLog.is_security_event == True)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    def get_high_severity_events(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get high severity audit events."""
        query = db.query(AuditLog).filter(AuditLog.is_high_severity == True)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @asynccontextmanager
    async def audit_context(
        self,
        event_type: AuditEventType,
        description: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """Context manager for auditing operations with automatic success/failure logging."""
        start_time = datetime.now(timezone.utc)
        success = False
        
        try:
            yield
            success = True
        except Exception as e:
            # Log the error
            await self.log_event(
                event_type=event_type,
                description=f"{description} - FAILED: {str(e)}",
                user_id=user_id,
                details={"error": str(e), "success": False},
                severity=AuditSeverity.ERROR,
                **kwargs
            )
            raise
        finally:
            # Log the operation result
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self.log_event(
                event_type=event_type,
                description=f"{description} - {'SUCCESS' if success else 'FAILED'}",
                user_id=user_id,
                details={
                    "success": success,
                    "duration_seconds": duration,
                },
                severity=AuditSeverity.INFO if success else AuditSeverity.ERROR,
                **kwargs
            )


# Global audit service instance
audit_service = AuditService()


# Convenience functions for easy access
async def log_audit_event(
    event_type: AuditEventType,
    description: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Convenience function to log audit events."""
    await audit_service.log_event(event_type, description, user_id=user_id, **kwargs)


def log_audit_event_sync(
    event_type: AuditEventType,
    description: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Convenience function to log audit events synchronously."""
    audit_service.log_event_sync(event_type, description, user_id=user_id, **kwargs)