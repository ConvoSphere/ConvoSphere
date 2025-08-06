"""
Standardized error response formats for the AI Assistant Platform.

This module provides consistent error response structures and helper functions
for handling various types of errors across the API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: Optional[str] = None
    message: str
    code: Optional[str] = None
    value: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    
    success: bool = False
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime
    path: Optional[str] = None
    method: Optional[str] = None
    status_code: int
    request_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseModel):
    """Standardized success response format."""
    
    success: bool = True
    data: Any
    message: Optional[str] = None
    timestamp: datetime
    status_code: int = 200
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def create_error_response(
    error: str,
    message: str,
    status_code: int = 400,
    details: Optional[List[ErrorDetail]] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    Create a standardized error response.
    
    Args:
        error: Error type/code
        message: Human-readable error message
        status_code: HTTP status code
        details: List of detailed error information
        path: Request path
        method: HTTP method
        request_id: Unique request identifier
        
    Returns:
        ErrorResponse: Standardized error response
    """
    return ErrorResponse(
        error=error,
        message=message,
        status_code=status_code,
        details=details,
        timestamp=datetime.utcnow(),
        path=path,
        method=method,
        request_id=request_id,
    )


def create_success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200,
) -> SuccessResponse:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        
    Returns:
        SuccessResponse: Standardized success response
    """
    return SuccessResponse(
        data=data,
        message=message,
        status_code=status_code,
        timestamp=datetime.utcnow(),
    )


# Predefined error responses
class CommonErrors:
    """Common error responses for frequently occurring errors."""
    
    @staticmethod
    def validation_error(
        message: str = "Validation error",
        details: Optional[List[ErrorDetail]] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create a validation error response."""
        return create_error_response(
            error="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def authentication_error(
        message: str = "Authentication required",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create an authentication error response."""
        return create_error_response(
            error="AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def authorization_error(
        message: str = "Insufficient permissions",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create an authorization error response."""
        return create_error_response(
            error="AUTHORIZATION_ERROR",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def not_found_error(
        message: str = "Resource not found",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create a not found error response."""
        return create_error_response(
            error="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def conflict_error(
        message: str = "Resource conflict",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create a conflict error response."""
        return create_error_response(
            error="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def rate_limit_error(
        message: str = "Rate limit exceeded",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create a rate limit error response."""
        return create_error_response(
            error="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create an internal server error response."""
        return create_error_response(
            error="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            path=path,
            method=method,
            request_id=request_id,
        )
    
    @staticmethod
    def service_unavailable_error(
        message: str = "Service temporarily unavailable",
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorResponse:
        """Create a service unavailable error response."""
        return create_error_response(
            error="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            path=path,
            method=method,
            request_id=request_id,
        )


def handle_validation_errors(validation_errors: List[Dict[str, Any]]) -> List[ErrorDetail]:
    """
    Convert Pydantic validation errors to standardized error details.
    
    Args:
        validation_errors: List of validation errors from Pydantic
        
    Returns:
        List[ErrorDetail]: Standardized error details
    """
    details = []
    for error in validation_errors:
        detail = ErrorDetail(
            field=error.get("loc", [None])[-1] if error.get("loc") else None,
            message=error.get("msg", "Validation error"),
            code=error.get("type"),
            value=error.get("input"),
        )
        details.append(detail)
    return details


def raise_http_exception(
    status_code: int,
    error: str,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
) -> None:
    """
    Raise a standardized HTTP exception.
    
    Args:
        status_code: HTTP status code
        error: Error type/code
        message: Human-readable error message
        details: List of detailed error information
        
    Raises:
        HTTPException: FastAPI HTTP exception
    """
    error_response = create_error_response(
        error=error,
        message=message,
        status_code=status_code,
        details=details,
    )
    raise HTTPException(
        status_code=status_code,
        detail=error_response.dict(),
    )