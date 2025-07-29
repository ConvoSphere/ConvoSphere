"""
Logs API endpoints for receiving structured logs from frontend and other services.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.app.core.auth import get_current_user_optional
from backend.app.core.structured_logging import log_event, structured_logger
from backend.app.models.user import User

router = APIRouter()


class LogEvent(BaseModel):
    """Frontend log event model."""

    timestamp: str
    level: str
    message: str
    eventType: str = None
    userId: str = None
    sessionId: str = None
    requestId: str = None
    endpoint: str = None
    method: str = None
    statusCode: int = None
    duration: float = None
    error: str = None
    traceId: str = None
    spanId: str = None
    extra: dict = None


class BatchLogRequest(BaseModel):
    """Batch log request model."""

    logs: list[LogEvent]


@router.post("/batch")
async def receive_batch_logs(
    request: BatchLogRequest,
    current_request: Request,
    current_user: User = Depends(get_current_user_optional),
):
    """Receive batch logs from frontend or other services."""
    try:
        # Get client IP

        # Process each log event
        for log_event_data in request.logs:
            # Map frontend log level to backend level
            level_mapping = {
                "debug": "DEBUG",
                "info": "INFO",
                "warn": "WARN",
                "error": "ERROR",
            }
            level = level_mapping.get(log_event_data.level.lower(), "INFO")

            # Create extra data
            extra = {}
            if log_event_data.extra:
                extra.update(log_event_data.extra)

            # Add trace correlation if available
            if log_event_data.traceId:
                extra["trace_id"] = log_event_data.traceId
            if log_event_data.spanId:
                extra["span_id"] = log_event_data.spanId

            # Log the event
            log_event(
                level=level,
                message=log_event_data.message,
                event_type=log_event_data.eventType,
                user_id=log_event_data.userId
                or (current_user.id if current_user else None),
                session_id=log_event_data.sessionId,
                request_id=log_event_data.requestId,
                endpoint=log_event_data.endpoint,
                method=log_event_data.method,
                status_code=log_event_data.statusCode,
                duration=log_event_data.duration,
                extra=extra,
            )

        return {"status": "success", "processed_logs": len(request.logs)}

    except Exception as e:
        # Log the error but don't fail the request
        structured_logger.log_event(
            level="ERROR",
            message=f"Failed to process batch logs: {str(e)}",
            event_type="log_processing_error",
            user_id=current_user.id if current_user else None,
            extra={"error": str(e), "logs_count": len(request.logs)},
        )

        # Return success to avoid retries from frontend
        return {
            "status": "success",
            "processed_logs": 0,
            "warning": "Some logs may not have been processed",
        }


@router.post("/single")
async def receive_single_log(
    log_event_data: LogEvent,
    current_request: Request,
    current_user: User = Depends(get_current_user_optional),
):
    """Receive a single log event from frontend or other services."""
    try:
        # Get client IP

        # Map frontend log level to backend level
        level_mapping = {
            "debug": "DEBUG",
            "info": "INFO",
            "warn": "WARN",
            "error": "ERROR",
        }
        level = level_mapping.get(log_event_data.level.lower(), "INFO")

        # Create extra data
        extra = {}
        if log_event_data.extra:
            extra.update(log_event_data.extra)

        # Add trace correlation if available
        if log_event_data.traceId:
            extra["trace_id"] = log_event_data.traceId
        if log_event_data.spanId:
            extra["span_id"] = log_event_data.spanId

        # Log the event
        log_event(
            level=level,
            message=log_event_data.message,
            event_type=log_event_data.eventType,
            user_id=log_event_data.userId
            or (current_user.id if current_user else None),
            session_id=log_event_data.sessionId,
            request_id=log_event_data.requestId,
            endpoint=log_event_data.endpoint,
            method=log_event_data.method,
            status_code=log_event_data.statusCode,
            duration=log_event_data.duration,
            extra=extra,
        )

        return {"status": "success"}

    except Exception as e:
        # Log the error but don't fail the request
        structured_logger.log_event(
            level="ERROR",
            message=f"Failed to process single log: {str(e)}",
            event_type="log_processing_error",
            user_id=current_user.id if current_user else None,
            extra={"error": str(e)},
        )

        # Return success to avoid retries from frontend
        return {"status": "success", "warning": "Log may not have been processed"}


@router.get("/health")
async def logs_health_check():
    """Health check endpoint for logs service."""
    return {"status": "healthy", "service": "logs", "timestamp": "2024-01-01T00:00:00Z"}
