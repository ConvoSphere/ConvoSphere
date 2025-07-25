"""
Error handlers for FastAPI application.

This module provides centralized error handling for all API endpoints
with consistent error responses and proper logging.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError as PydanticValidationError

from .exceptions import ERROR_CODES, ChatError


async def chat_error_handler(request: Request, exc: ChatError) -> JSONResponse:
    """Handle ChatError exceptions."""
    logger.error(
        f"ChatError: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def validation_error_handler(
    request: Request,
    exc: PydanticValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            },
        )

    logger.warning(
        f"ValidationError: {len(errors)} validation errors",
        extra={
            "errors": errors,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": ERROR_CODES["VALIDATION_ERROR"],
                "message": "Validation error",
                "details": {"errors": errors},
            },
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle general exceptions."""
    logger.exception(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            },
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI application."""

    # Register ChatError handler
    app.add_exception_handler(ChatError, chat_error_handler)

    # Register Pydantic validation error handler
    app.add_exception_handler(PydanticValidationError, validation_error_handler)

    # Register general exception handler (should be last)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers registered successfully")


def create_error_response(
    error_code: str,
    message: str,
    details: dict[str, Any] = None,
    status_code: int = 500,
) -> dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
    }


def log_error(
    error: Exception,
    context: dict[str, Any] = None,
    level: str = "error",
) -> None:
    """Log an error with structured context."""
    log_data = {
        "exception_type": type(error).__name__,
        "message": str(error),
    }

    if context:
        log_data.update(context)

    if level == "error":
        logger.error(f"Error: {error}", extra=log_data)
    elif level == "warning":
        logger.warning(f"Warning: {error}", extra=log_data)
    elif level == "info":
        logger.info(f"Info: {error}", extra=log_data)
    else:
        logger.debug(f"Debug: {error}", extra=log_data)
