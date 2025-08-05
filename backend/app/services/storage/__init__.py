"""
Storage service package for cloud storage integration.

This package provides a unified interface for different storage providers
including local filesystem, S3, MinIO, GCS, and Azure Blob Storage.
"""

from .base import StorageProvider, StorageError
from .factory import StorageFactory
from .manager import StorageManager
from .config import StorageConfig

__all__ = [
    "StorageProvider",
    "StorageError", 
    "StorageFactory",
    "StorageManager",
    "StorageConfig"
]