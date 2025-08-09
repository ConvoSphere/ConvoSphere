"""
Storage service package for cloud storage integration.

This package provides a unified interface for different storage providers
including local filesystem, S3, MinIO, GCS, and Azure Blob Storage.
"""

from .base import StorageError, StorageProvider
from .config import StorageConfig
from .factory import StorageFactory
from .manager import StorageManager

__all__ = [
    "StorageProvider",
    "StorageError",
    "StorageFactory",
    "StorageManager",
    "StorageConfig",
]
