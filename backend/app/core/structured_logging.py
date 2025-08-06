"""
Structured Logging Service for the AI Assistant Platform.

This module provides structured logging with OpenTelemetry integration,
log correlation, and standardized log formats.
"""

import json
import logging
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from backend.app.core.config import get_settings


class StructuredLogger:
    """Structured logger with OpenTelemetry integration."""

    def __init__(self):
        self.settings = get_settings()
        self._setup_loguru()
        self._setup_standard_logging()

    def _setup_loguru(self):
        """Setup Loguru with structured logging."""
        # Remove default handler
        logger.remove()

        # Add structured console handler
        logger.add(
            sys.stdout,
            format=self._format_log,
            level=self.settings.log_level,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )

        # Add file handler if configured
        if self.settings.log_file and self.settings.log_file != "./logs/app.log":
            logger.add(
                self.settings.log_file,
                format=self._format_log,
                level=self.settings.log_level,
                serialize=True,
                rotation="10 MB",
                retention="30 days",
                compression="gz",
            )

    def _setup_standard_logging(self):
        """Setup standard Python logging to work with Loguru."""
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    def _format_log(self, record):
        """Format log record with structured data."""
        # Get current span for correlation
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context() if current_span else None

        # Handle both Loguru and standard Python logging records
        if isinstance(record, dict):
            # Loguru record format (dictionary)
            if "time" in record and hasattr(record["time"], "timestamp"):
                timestamp = datetime.fromtimestamp(record["time"].timestamp(), tz=UTC).isoformat()
            else:
                timestamp = datetime.now(UTC).isoformat()
            level = record.get("level", {}).name if isinstance(record.get("level"), object) else str(record.get("level", "INFO"))
            logger_name = record.get("name", "unknown")
            message = record.get("message", "")
            module = record.get("module", "unknown")
            function = record.get("function", "unknown")
            line = record.get("line", 0)
        elif hasattr(record, "time") and hasattr(record.time, "timestamp"):
            # Loguru record format (object)
            timestamp = datetime.fromtimestamp(record.time.timestamp(), tz=UTC).isoformat()
            level = record.level.name
            logger_name = record.name
            message = record.message
            module = record.module
            function = record.function
            line = record.line
        else:
            # Standard Python logging record format
            timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat()
            level = record.levelname
            logger_name = record.name
            message = record.getMessage()
            module = record.module
            function = record.funcName
            line = record.lineno

        # Base log structure
        log_data = {
            "timestamp": timestamp,
            "level": level,
            "logger": logger_name,
            "message": message,
            "module": module,
            "function": function,
            "line": line,
        }

        # Add trace correlation if available
        if span_context and span_context.is_valid:
            log_data.update(
                {
                    "trace_id": format(span_context.trace_id, "032x"),
                    "span_id": format(span_context.span_id, "016x"),
                }
            )

        # Add extra fields from record
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)

        # Add exception info if present
        if hasattr(record, "exception") and record.exception:
            log_data["exception"] = {
                "type": record.exception.type.__name__,
                "value": str(record.exception.value),
                "traceback": record.exception.traceback,
            }

        return json.dumps(log_data, ensure_ascii=False, default=str)

    def log_event(
        self,
        level: str,
        message: str,
        event_type: str = None,
        user_id: str = None,
        session_id: str = None,
        request_id: str = None,
        endpoint: str = None,
        method: str = None,
        status_code: int = None,
        duration: float = None,
        extra: dict[str, Any] = None,
        **kwargs,
    ):
        """Log a structured event."""
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration": duration,
        }

        # Add extra data
        if extra:
            log_data.update(extra)

        # Add additional kwargs
        log_data.update(kwargs)

        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}

        # Log with structured data
        getattr(logger, level.lower())(message, extra=log_data)

    def log_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        user_id: str = None,
        request_id: str = None,
        request_size: int = None,
        response_size: int = None,
        error: str = None,
    ):
        """Log API request with structured data."""
        self.log_event(
            level="INFO",
            message=f"API Request: {method} {endpoint}",
            event_type="api_request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            user_id=user_id,
            request_id=request_id,
            request_size=request_size,
            response_size=response_size,
            error=error,
        )

    def log_database_query(
        self,
        query_type: str,
        table_name: str,
        duration: float,
        rows_affected: int = None,
        error: str = None,
    ):
        """Log database query with structured data."""
        self.log_event(
            level="DEBUG",
            message=f"Database Query: {query_type} on {table_name}",
            event_type="database_query",
            query_type=query_type,
            table_name=table_name,
            duration=duration,
            rows_affected=rows_affected,
            error=error,
        )

    def log_security_event(
        self,
        event_type: str,
        description: str,
        user_id: str = None,
        ip_address: str = None,
        severity: str = "INFO",
        details: dict[str, Any] = None,
    ):
        """Log security event with structured data."""
        self.log_event(
            level=severity.upper(),
            message=f"Security Event: {description}",
            event_type="security_event",
            security_event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
        )

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = None,
        tags: dict[str, str] = None,
    ):
        """Log performance metric with structured data."""
        self.log_event(
            level="INFO",
            message=f"Performance Metric: {metric_name}",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags,
        )

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        attributes: dict[str, Any] = None,
        user_id: str = None,
        request_id: str = None,
    ):
        """Context manager for tracing operations with logging."""
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(
            operation_name, attributes=attributes
        ) as span:
            try:
                # Log operation start
                self.log_event(
                    level="DEBUG",
                    message=f"Operation started: {operation_name}",
                    event_type="operation_start",
                    operation_name=operation_name,
                    user_id=user_id,
                    request_id=request_id,
                )

                yield span

                # Log operation success
                span.set_status(Status(StatusCode.OK))
                self.log_event(
                    level="DEBUG",
                    message=f"Operation completed: {operation_name}",
                    event_type="operation_success",
                    operation_name=operation_name,
                    user_id=user_id,
                    request_id=request_id,
                )

            except Exception as e:
                # Log operation error
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                self.log_event(
                    level="ERROR",
                    message=f"Operation failed: {operation_name}",
                    event_type="operation_error",
                    operation_name=operation_name,
                    user_id=user_id,
                    request_id=request_id,
                    error=str(e),
                )
                raise


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to Loguru."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Global structured logger instance (disabled to avoid conflicts)
# structured_logger = StructuredLogger()
structured_logger = None


def get_logger(name: str = None) -> StructuredLogger:
    """Get structured logger instance."""
    return structured_logger


def log_event(
    level: str,
    message: str,
    event_type: str = None,
    user_id: str = None,
    session_id: str = None,
    request_id: str = None,
    endpoint: str = None,
    method: str = None,
    status_code: int = None,
    duration: float = None,
    extra: dict[str, Any] = None,
    **kwargs,
):
    """Log a structured event."""
    if structured_logger is not None:
        structured_logger.log_event(
            level=level,
            message=message,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration=duration,
            extra=extra,
            **kwargs,
        )
    else:
        # Fallback to basic logging
        logger.log(level.upper(), message)


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    request_id: str = None,
    request_size: int = None,
    response_size: int = None,
    error: str = None,
):
    """Log API request with structured data."""
    structured_logger.log_api_request(
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration=duration,
        user_id=user_id,
        request_id=request_id,
        request_size=request_size,
        response_size=response_size,
        error=error,
    )


def log_database_query(
    query_type: str,
    table_name: str,
    duration: float,
    rows_affected: int = None,
    error: str = None,
):
    """Log database query with structured data."""
    structured_logger.log_database_query(
        query_type=query_type,
        table_name=table_name,
        duration=duration,
        rows_affected=rows_affected,
        error=error,
    )


def log_security_event(
    event_type: str,
    description: str,
    user_id: str = None,
    ip_address: str = None,
    severity: str = "INFO",
    details: dict[str, Any] = None,
):
    """Log security event with structured data."""
    structured_logger.log_security_event(
        event_type=event_type,
        description=description,
        user_id=user_id,
        ip_address=ip_address,
        severity=severity,
        details=details,
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = None,
    tags: dict[str, str] = None,
):
    """Log performance metric with structured data."""
    structured_logger.log_performance_metric(
        metric_name=metric_name,
        value=value,
        unit=unit,
        tags=tags,
    )


def trace_operation(
    operation_name: str,
    attributes: dict[str, Any] = None,
    user_id: str = None,
    request_id: str = None,
):
    """Context manager for tracing operations with logging."""
    return structured_logger.trace_operation(
        operation_name=operation_name,
        attributes=attributes,
        user_id=user_id,
        request_id=request_id,
    )
