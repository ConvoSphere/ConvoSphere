"""
Performance monitoring middleware.

This module provides FastAPI middleware for monitoring HTTP request/response
performance and collecting request metrics.
"""

from .performance_middleware import PerformanceMiddleware

__all__ = [
    "PerformanceMiddleware",
]
