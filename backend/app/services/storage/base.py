"""
Base storage interface and error classes.

This module defines the abstract base class for storage providers
and custom exceptions for storage operations.
"""

from abc import ABC, abstractmethod
from typing import Any


class StorageError(Exception):
    """Base exception for storage operations."""

    def __init__(self, message: str, provider: str = None, operation: str = None):
        self.message = message
        self.provider = provider
        self.operation = operation
        super().__init__(self.message)


class StorageProvider(ABC):
    """Base interface for all storage providers."""

    def __init__(self, config: "StorageConfig"):
        self.config = config

    @abstractmethod
    async def upload_file(
        self, file_path: str, content: bytes, metadata: dict[str, Any] = None
    ) -> str:
        """
        Upload file and return storage path/URL.

        Args:
            file_path: Relative path where file should be stored
            content: File content as bytes
            metadata: Optional metadata dictionary

        Returns:
            Storage path/URL for the uploaded file

        Raises:
            StorageError: If upload fails
        """

    @abstractmethod
    async def download_file(self, storage_path: str) -> bytes:
        """
        Download file content.

        Args:
            storage_path: Storage path/URL of the file

        Returns:
            File content as bytes

        Raises:
            StorageError: If download fails
        """

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            storage_path: Storage path/URL of the file

        Returns:
            True if deletion was successful, False otherwise
        """

    @abstractmethod
    async def file_exists(self, storage_path: str) -> bool:
        """
        Check if file exists.

        Args:
            storage_path: Storage path/URL of the file

        Returns:
            True if file exists, False otherwise
        """

    @abstractmethod
    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Get presigned URL for file access.

        Args:
            storage_path: Storage path/URL of the file
            expires_in: URL expiration time in seconds

        Returns:
            Presigned URL for file access
        """

    @abstractmethod
    async def get_file_metadata(self, storage_path: str) -> dict[str, Any]:
        """
        Get file metadata.

        Args:
            storage_path: Storage path/URL of the file

        Returns:
            Dictionary containing file metadata
        """

    async def health_check(self) -> bool:
        """
        Check if storage provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to list files or perform a simple operation
            return await self._perform_health_check()
        except Exception:
            return False

    @abstractmethod
    async def _perform_health_check(self) -> bool:
        """Provider-specific health check implementation."""

    def get_provider_name(self) -> str:
        """Get the name of this storage provider."""
        return self.__class__.__name__.replace("StorageProvider", "").lower()
