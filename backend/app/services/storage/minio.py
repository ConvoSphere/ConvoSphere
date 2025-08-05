"""
MinIO storage provider.

This module provides MinIO storage implementation using the S3-compatible API.
MinIO is included by default and provides object storage functionality.
"""

import json
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, Any
from loguru import logger

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    logger.warning("MinIO client not available. Install with: pip install minio")

from .base import StorageProvider, StorageError
from .config import StorageConfig


class MinIOStorageProvider(StorageProvider):
    """MinIO storage provider (S3-compatible)."""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        
        if not MINIO_AVAILABLE:
            raise StorageError(
                "MinIO client not available. Install with: pip install minio",
                provider="minio",
                operation="init"
            )
        
        # Parse endpoint
        endpoint = config.minio_endpoint or "localhost:9000"
        if "://" not in endpoint:
            endpoint = f"{'https' if config.minio_secure else 'http'}://{endpoint}"
        
        # Initialize MinIO client
        self.client = Minio(
            endpoint=endpoint.replace("https://", "").replace("http://", ""),
            access_key=config.minio_access_key or "minioadmin",
            secret_key=config.minio_secret_key or "minioadmin",
            secure=config.minio_secure,
            region=config.s3_region
        )
        
        self.bucket_name = config.bucket_name
        self._ensure_bucket_exists()
        
        logger.info(f"Initialized MinIO storage provider for bucket: {self.bucket_name}")
    
    def _ensure_bucket_exists(self):
        """Ensure bucket exists, create if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            raise StorageError(
                f"Failed to ensure bucket exists: {str(e)}",
                provider="minio",
                operation="init"
            )
    
    async def upload_file(self, file_path: str, content: bytes, metadata: Dict[str, Any] = None) -> str:
        """Upload file to MinIO."""
        try:
            # Convert metadata to MinIO format
            minio_metadata = {}
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        minio_metadata[key] = str(value)
                    else:
                        minio_metadata[f"x-amz-meta-{key}"] = json.dumps(value)
            
            # Create content stream
            content_stream = BytesIO(content)
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=content_stream,
                length=len(content),
                metadata=minio_metadata
            )
            
            storage_path = f"minio://{self.bucket_name}/{file_path}"
            logger.debug(f"Uploaded file to {storage_path}")
            
            return storage_path
            
        except S3Error as e:
            raise StorageError(
                f"MinIO upload failed: {str(e)}",
                provider="minio",
                operation="upload"
            )
        except Exception as e:
            raise StorageError(
                f"Unexpected error during MinIO upload: {str(e)}",
                provider="minio",
                operation="upload"
            )
    
    async def download_file(self, storage_path: str) -> bytes:
        """Download file from MinIO."""
        try:
            object_name = self._extract_object_name(storage_path)
            
            # Get object from MinIO
            response = self.client.get_object(self.bucket_name, object_name)
            
            # Read content
            content = response.read()
            response.close()
            response.release_conn()
            
            logger.debug(f"Downloaded file from {storage_path}")
            return content
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise StorageError(
                    f"File not found: {object_name}",
                    provider="minio",
                    operation="download"
                )
            raise StorageError(
                f"MinIO download failed: {str(e)}",
                provider="minio",
                operation="download"
            )
        except Exception as e:
            raise StorageError(
                f"Unexpected error during MinIO download: {str(e)}",
                provider="minio",
                operation="download"
            )
    
    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from MinIO."""
        try:
            object_name = self._extract_object_name(storage_path)
            
            # Remove object from MinIO
            self.client.remove_object(self.bucket_name, object_name)
            
            logger.debug(f"Deleted file {storage_path}")
            return True
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"File not found for deletion: {object_name}")
                return False
            logger.error(f"MinIO delete failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during MinIO delete: {str(e)}")
            return False
    
    async def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            object_name = self._extract_object_name(storage_path)
            
            # Try to get object info
            self.client.stat_object(self.bucket_name, object_name)
            return True
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            # For other errors, assume file doesn't exist
            return False
        except Exception:
            return False
    
    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get presigned URL for MinIO file access."""
        try:
            object_name = self._extract_object_name(storage_path)
            
            # Generate presigned URL
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=timedelta(seconds=expires_in)
            )
            
            return url
            
        except S3Error as e:
            raise StorageError(
                f"Failed to generate presigned URL: {str(e)}",
                provider="minio",
                operation="get_url"
            )
    
    async def get_file_metadata(self, storage_path: str) -> Dict[str, Any]:
        """Get file metadata from MinIO."""
        try:
            object_name = self._extract_object_name(storage_path)
            
            # Get object info
            stat = self.client.stat_object(self.bucket_name, object_name)
            
            metadata = {
                "size": stat.size,
                "modified": stat.last_modified.isoformat(),
                "etag": stat.etag,
                "content_type": stat.content_type,
                "provider": "minio",
                "storage_path": storage_path,
                "bucket": self.bucket_name,
                "object_name": object_name
            }
            
            # Add custom metadata
            if hasattr(stat, 'metadata') and stat.metadata:
                for key, value in stat.metadata.items():
                    if key.startswith('x-amz-meta-'):
                        # Parse JSON metadata
                        try:
                            metadata[key[11:]] = json.loads(value)  # Remove 'x-amz-meta-' prefix
                        except json.JSONDecodeError:
                            metadata[key[11:]] = value
                    else:
                        metadata[key] = value
            
            return metadata
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise StorageError(
                    f"File not found: {object_name}",
                    provider="minio",
                    operation="get_metadata"
                )
            raise StorageError(
                f"Failed to get MinIO metadata: {str(e)}",
                provider="minio",
                operation="get_metadata"
            )
    
    async def _perform_health_check(self) -> bool:
        """Perform health check for MinIO."""
        try:
            # Try to list objects in bucket
            objects = list(self.client.list_objects(self.bucket_name, max_keys=1))
            return True
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return False
    
    def _extract_object_name(self, storage_path: str) -> str:
        """Extract object name from storage path."""
        if storage_path.startswith("minio://"):
            # Remove "minio://bucket_name/" prefix
            parts = storage_path.split("/", 3)
            if len(parts) >= 4:
                return parts[3]
        
        # If it's already a relative path, return as is
        return storage_path
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get MinIO storage information."""
        try:
            total_size = 0
            file_count = 0
            
            # List all objects and calculate stats
            objects = list(self.client.list_objects(self.bucket_name, recursive=True))
            
            for obj in objects:
                total_size += obj.size
                file_count += 1
            
            return {
                "provider": "minio",
                "bucket_name": self.bucket_name,
                "endpoint": self.client._endpoint_url,
                "total_files": file_count,
                "total_size_bytes": total_size,
                "bucket_exists": self.client.bucket_exists(self.bucket_name)
            }
        except Exception as e:
            logger.error(f"Failed to get MinIO storage info: {e}")
            return {
                "provider": "minio",
                "bucket_name": self.bucket_name,
                "error": str(e)
            }
    
    async def list_files(self, prefix: str = "", max_keys: int = 1000) -> list[Dict[str, Any]]:
        """List files in MinIO bucket."""
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                if len(files) >= max_keys:
                    break
                
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "modified": obj.last_modified.isoformat(),
                    "etag": obj.etag
                })
            
            return files
            
        except S3Error as e:
            logger.error(f"Failed to list MinIO files: {e}")
            return []