"""
Storage manager for high-level storage operations.

This module provides a unified interface for storage operations
regardless of the underlying storage provider.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .factory import StorageFactory
from .base import StorageProvider, StorageError
from .config import StorageConfig


class StorageManager:
    """Central storage management service."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self._provider: Optional[StorageProvider] = None
        self._health_check_time: Optional[datetime] = None
        self._health_check_interval = 300  # 5 minutes
    
    @property
    def provider(self) -> StorageProvider:
        """Get or create storage provider."""
        if self._provider is None:
            self._provider = StorageFactory.create_provider(self.config)
        return self._provider
    
    async def upload_document(self, file_id: str, content: bytes, metadata: Dict[str, Any] = None) -> str:
        """
        Upload document to storage.
        
        Args:
            file_id: Unique file identifier
            content: File content as bytes
            metadata: Optional metadata dictionary
            
        Returns:
            Storage path/URL for the uploaded file
        """
        try:
            # Create file path
            file_path = f"documents/{file_id}"
            
            # Add default metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_id": file_id,
                "content_length": len(content)
            })
            
            # Upload file
            storage_path = await self.provider.upload_file(file_path, content, metadata)
            
            logger.info(f"Uploaded document {file_id} to {storage_path}")
            return storage_path
            
        except Exception as e:
            logger.error(f"Failed to upload document {file_id}: {e}")
            raise
    
    async def download_document(self, storage_path: str) -> bytes:
        """
        Download document from storage.
        
        Args:
            storage_path: Storage path/URL of the file
            
        Returns:
            File content as bytes
        """
        try:
            content = await self.provider.download_file(storage_path)
            logger.debug(f"Downloaded document from {storage_path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to download document from {storage_path}: {e}")
            raise
    
    async def delete_document(self, storage_path: str) -> bool:
        """
        Delete document from storage.
        
        Args:
            storage_path: Storage path/URL of the file
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            success = await self.provider.delete_file(storage_path)
            if success:
                logger.info(f"Deleted document {storage_path}")
            else:
                logger.warning(f"Failed to delete document {storage_path}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document {storage_path}: {e}")
            return False
    
    async def get_document_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Get presigned URL for document access.
        
        Args:
            storage_path: Storage path/URL of the file
            expires_in: URL expiration time in seconds
            
        Returns:
            Presigned URL for document access
        """
        try:
            url = await self.provider.get_file_url(storage_path, expires_in)
            logger.debug(f"Generated presigned URL for {storage_path}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {storage_path}: {e}")
            raise
    
    async def get_document_metadata(self, storage_path: str) -> Dict[str, Any]:
        """
        Get document metadata.
        
        Args:
            storage_path: Storage path/URL of the file
            
        Returns:
            Document metadata dictionary
        """
        try:
            metadata = await self.provider.get_file_metadata(storage_path)
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {storage_path}: {e}")
            raise
    
    async def document_exists(self, storage_path: str) -> bool:
        """
        Check if document exists in storage.
        
        Args:
            storage_path: Storage path/URL of the file
            
        Returns:
            True if document exists, False otherwise
        """
        try:
            return await self.provider.file_exists(storage_path)
        except Exception as e:
            logger.error(f"Error checking document existence {storage_path}: {e}")
            return False
    
    async def health_check(self, force: bool = False) -> bool:
        """
        Check if storage provider is healthy.
        
        Args:
            force: Force health check regardless of cache
            
        Returns:
            True if healthy, False otherwise
        """
        # Check cache first
        if not force and self._health_check_time:
            time_diff = (datetime.utcnow() - self._health_check_time).total_seconds()
            if time_diff < self._health_check_interval:
                return True
        
        try:
            is_healthy = await self.provider.health_check()
            self._health_check_time = datetime.utcnow()
            
            if is_healthy:
                logger.debug("Storage health check passed")
            else:
                logger.warning("Storage health check failed")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Storage health check error: {e}")
            return False
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information and statistics.
        
        Returns:
            Storage information dictionary
        """
        try:
            info = self.provider.get_storage_info()
            info.update({
                "provider_name": self.provider.get_provider_name(),
                "config_provider": self.config.provider,
                "health_check_time": self._health_check_time.isoformat() if self._health_check_time else None
            })
            return info
            
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {
                "error": str(e),
                "provider_name": self.provider.get_provider_name(),
                "config_provider": self.config.provider
            }
    
    async def migrate_storage(self, from_config: StorageConfig, to_config: StorageConfig, 
                            document_paths: List[str]) -> Dict[str, Any]:
        """
        Migrate documents between storage providers.
        
        Args:
            from_config: Source storage configuration
            to_config: Target storage configuration
            document_paths: List of document storage paths to migrate
            
        Returns:
            Migration results dictionary
        """
        try:
            from_manager = StorageManager(from_config)
            to_manager = StorageManager(to_config)
            
            results = {
                "total": len(document_paths),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for storage_path in document_paths:
                try:
                    # Download from source
                    content = await from_manager.download_document(storage_path)
                    
                    # Get metadata
                    metadata = await from_manager.get_document_metadata(storage_path)
                    
                    # Extract file path from storage path
                    file_path = self._extract_file_path(storage_path)
                    
                    # Upload to target
                    new_storage_path = await to_manager.provider.upload_file(file_path, content, metadata)
                    
                    # Delete from source (optional)
                    # await from_manager.delete_document(storage_path)
                    
                    results["successful"] += 1
                    logger.info(f"Migrated document {storage_path} to {new_storage_path}")
                    
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Failed to migrate {storage_path}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Migration completed: {results['successful']}/{results['total']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def _extract_file_path(self, storage_path: str) -> str:
        """Extract file path from storage path."""
        # Remove provider prefix
        for prefix in ["local://", "minio://", "s3://", "gcs://", "azure://"]:
            if storage_path.startswith(prefix):
                # Remove prefix and bucket name
                parts = storage_path.split("/", 3)
                if len(parts) >= 4:
                    return parts[3]
        
        return storage_path
    
    async def cleanup_orphaned_files(self, valid_storage_paths: List[str]) -> Dict[str, Any]:
        """
        Clean up orphaned files in storage.
        
        Args:
            valid_storage_paths: List of valid storage paths
            
        Returns:
            Cleanup results dictionary
        """
        try:
            # This is a basic implementation - providers may need specific logic
            results = {
                "total_checked": 0,
                "deleted": 0,
                "errors": []
            }
            
            # For now, just return basic info
            # Full implementation would require listing all files and comparing
            logger.info("Cleanup operation not fully implemented for this provider")
            
            return results
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "error": str(e),
                "total_checked": 0,
                "deleted": 0,
                "errors": [str(e)]
            }
    
    def get_provider_name(self) -> str:
        """Get the name of the current storage provider."""
        return self.provider.get_provider_name()
    
    def get_config(self) -> StorageConfig:
        """Get the current storage configuration."""
        return self.config