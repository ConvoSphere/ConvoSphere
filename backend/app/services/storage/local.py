"""
Local filesystem storage provider.

This module provides local filesystem storage implementation
as a fallback and for development environments.
"""

import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from .base import StorageError, StorageProvider
from .config import StorageConfig


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider."""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.local_base_path or "./uploads")
        self.bucket_path = self.base_path / config.bucket_name

        # Ensure directories exist
        self.bucket_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized local storage provider at {self.bucket_path}")

    async def upload_file(self, file_path: str, content: bytes, metadata: dict[str, Any] = None) -> str:
        """Upload file to local filesystem."""
        try:
            # Create full path
            full_path = self.bucket_path / file_path

            # Ensure parent directories exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            with open(full_path, "wb") as f:
                f.write(content)

            # Set file permissions (readable by owner and group)
            os.chmod(full_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)

            # Store metadata if provided
            if metadata:
                metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
                with open(metadata_path, "w") as f:
                    import json
                    json.dump(metadata, f)

            storage_path = f"local://{self.config.bucket_name}/{file_path}"
            logger.debug(f"Uploaded file to {storage_path}")

            return storage_path

        except Exception as e:
            raise StorageError(
                f"Failed to upload file {file_path}: {str(e)}",
                provider="local",
                operation="upload"
            )

    async def download_file(self, storage_path: str) -> bytes:
        """Download file from local filesystem."""
        try:
            # Extract file path from storage path
            file_path = self._extract_file_path(storage_path)
            full_path = self.bucket_path / file_path

            if not full_path.exists():
                raise StorageError(
                    f"File not found: {file_path}",
                    provider="local",
                    operation="download"
                )

            with open(full_path, "rb") as f:
                content = f.read()

            logger.debug(f"Downloaded file from {storage_path}")
            return content

        except Exception as e:
            if isinstance(e, StorageError):
                raise
            raise StorageError(
                f"Failed to download file {storage_path}: {str(e)}",
                provider="local",
                operation="download"
            )

    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            file_path = self._extract_file_path(storage_path)
            full_path = self.bucket_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found for deletion: {file_path}")
                return False

            # Delete main file
            full_path.unlink()

            # Delete metadata file if it exists
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
            if metadata_path.exists():
                metadata_path.unlink()

            logger.debug(f"Deleted file {storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {str(e)}")
            return False

    async def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in local filesystem."""
        try:
            file_path = self._extract_file_path(storage_path)
            full_path = self.bucket_path / file_path
            return full_path.exists()
        except Exception:
            return False

    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get file URL for local filesystem."""
        # For local storage, return the file path
        file_path = self._extract_file_path(storage_path)
        full_path = self.bucket_path / file_path

        if not full_path.exists():
            raise StorageError(
                f"File not found: {file_path}",
                provider="local",
                operation="get_url"
            )

        return f"file://{full_path.absolute()}"

    async def get_file_metadata(self, storage_path: str) -> dict[str, Any]:
        """Get file metadata from local filesystem."""
        try:
            file_path = self._extract_file_path(storage_path)
            full_path = self.bucket_path / file_path

            if not full_path.exists():
                raise StorageError(
                    f"File not found: {file_path}",
                    provider="local",
                    operation="get_metadata"
                )

            stat_info = full_path.stat()

            metadata = {
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:],
                "provider": "local",
                "storage_path": storage_path
            }

            # Try to load additional metadata if it exists
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
            if metadata_path.exists():
                try:
                    import json
                    with open(metadata_path) as f:
                        additional_metadata = json.load(f)
                    metadata.update(additional_metadata)
                except Exception as e:
                    logger.warning(f"Failed to load metadata file: {e}")

            return metadata

        except Exception as e:
            if isinstance(e, StorageError):
                raise
            raise StorageError(
                f"Failed to get metadata for {storage_path}: {str(e)}",
                provider="local",
                operation="get_metadata"
            )

    async def _perform_health_check(self) -> bool:
        """Perform health check for local storage."""
        try:
            # Check if base directory is writable
            test_file = self.bucket_path / ".health_check"

            # Try to write a test file
            test_file.write_text("health_check")

            # Try to read it back
            content = test_file.read_text()

            # Clean up
            test_file.unlink()

            return content == "health_check"

        except Exception as e:
            logger.error(f"Local storage health check failed: {e}")
            return False

    def _extract_file_path(self, storage_path: str) -> str:
        """Extract file path from storage path."""
        if storage_path.startswith("local://"):
            # Remove "local://bucket_name/" prefix
            parts = storage_path.split("/", 3)
            if len(parts) >= 4:
                return parts[3]

        # If it's already a relative path, return as is
        return storage_path

    def get_storage_info(self) -> dict[str, Any]:
        """Get storage information."""
        try:
            total_size = 0
            file_count = 0

            for file_path in self.bucket_path.rglob("*"):
                if file_path.is_file() and not file_path.name.endswith(".meta"):
                    total_size += file_path.stat().st_size
                    file_count += 1

            return {
                "provider": "local",
                "base_path": str(self.base_path),
                "bucket_path": str(self.bucket_path),
                "total_files": file_count,
                "total_size_bytes": total_size,
                "available_space": shutil.disk_usage(self.base_path).free
            }
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {
                "provider": "local",
                "base_path": str(self.base_path),
                "bucket_path": str(self.bucket_path),
                "error": str(e)
            }
