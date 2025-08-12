"""
Storage management API endpoints.

This module provides endpoints for managing storage providers,
monitoring storage health, and configuring storage settings.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from backend.app.core.auth import get_current_user
from backend.app.core.config import get_settings
from backend.app.models.user import User
from backend.app.services.storage.config import StorageConfig
from backend.app.services.storage.factory import StorageFactory
from backend.app.services.storage.manager import StorageManager

router = APIRouter(prefix="/storage", tags=["storage"])


def get_storage_manager() -> StorageManager:
    """Get storage manager instance."""
    settings = get_settings()
    storage_config = StorageConfig(
        provider=settings.storage_provider,
        bucket_name=settings.storage_bucket_name,
        minio_endpoint=settings.minio_endpoint,
        minio_access_key=settings.minio_access_key,
        minio_secret_key=settings.minio_secret_key,
        minio_secure=settings.minio_secure,
        s3_endpoint_url=settings.s3_endpoint_url,
        s3_access_key_id=settings.s3_access_key_id,
        s3_secret_access_key=settings.s3_secret_access_key,
        s3_region=settings.s3_region,
        gcs_project_id=settings.gcs_project_id,
        gcs_credentials_file=settings.gcs_credentials_file,
        azure_account_name=settings.azure_account_name,
        azure_account_key=settings.azure_account_key,
        azure_connection_string=settings.azure_connection_string,
        local_base_path=settings.upload_dir,
    )
    return StorageManager(storage_config)


@router.get("/health")
async def get_storage_health(
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Get storage health status.

    Returns:
        Health status of the storage provider
    """
    try:
        is_healthy = await storage_manager.health_check()
        return {
            "healthy": is_healthy,
            "provider": storage_manager.get_provider_name(),
            "message": (
                "Storage is healthy" if is_healthy else "Storage health check failed"
            ),
        }
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage health check failed: {str(e)}",
        )


@router.get("/info")
async def get_storage_info(
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Get storage information and statistics.

    Returns:
        Storage information including provider, statistics, and configuration
    """
    try:
        info = await storage_manager.get_storage_info()
        metrics = await storage_manager.get_performance_metrics()

        return {"success": True, "data": {**info, "performance_metrics": metrics}}
    except Exception as e:
        logger.error(f"Failed to get storage info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage info: {str(e)}",
        )


@router.get("/providers")
async def get_available_providers(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get list of available storage providers.

    Returns:
        List of available storage providers
    """
    try:
        providers = StorageFactory.get_available_providers()
        return {
            "success": True,
            "providers": providers,
            "current_provider": get_settings().storage_provider,
        }
    except Exception as e:
        logger.error(f"Failed to get available providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available providers: {str(e)}",
        )


@router.post("/test")
async def test_storage_config(
    config: dict[str, Any], current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Test storage configuration.

    Args:
        config: Storage configuration to test

    Returns:
        Test results
    """
    try:
        storage_config = StorageConfig(**config)
        is_valid = StorageFactory.test_provider(storage_config)

        return {
            "success": True,
            "valid": is_valid,
            "message": (
                "Configuration is valid" if is_valid else "Configuration test failed"
            ),
        }
    except Exception as e:
        logger.error(f"Storage configuration test failed: {e}")
        return {"success": False, "valid": False, "error": str(e)}


@router.get("/config")
async def get_storage_config(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get current storage configuration.

    Returns:
        Current storage configuration (without sensitive data)
    """
    try:
        settings = get_settings()
        config = {
            "provider": settings.storage_provider,
            "bucket_name": settings.storage_bucket_name,
            "minio_endpoint": settings.minio_endpoint,
            "minio_secure": settings.minio_secure,
            "s3_region": settings.s3_region,
            "gcs_project_id": settings.gcs_project_id,
            "azure_account_name": settings.azure_account_name,
        }

        return {"success": True, "config": config}
    except Exception as e:
        logger.error(f"Failed to get storage config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage config: {str(e)}",
        )


@router.post("/migrate")
async def migrate_storage(
    source_config: dict[str, Any],
    target_config: dict[str, Any],
    document_paths: list[str],
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Migrate documents between storage providers.

    Args:
        source_config: Source storage configuration
        target_config: Target storage configuration
        document_paths: List of document paths to migrate

    Returns:
        Migration results
    """
    try:
        # Create storage managers
        source_storage_config = StorageConfig(**source_config)
        target_storage_config = StorageConfig(**target_config)

        source_manager = StorageManager(source_storage_config)

        # Perform migration
        results = await source_manager.migrate_storage(
            source_storage_config, target_storage_config, document_paths
        )

        return {"success": True, "migration_results": results}
    except Exception as e:
        logger.error(f"Storage migration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage migration failed: {str(e)}",
        )


@router.post("/cleanup")
async def cleanup_orphaned_files(
    valid_storage_paths: list[str],
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Clean up orphaned files in storage.

    Args:
        valid_storage_paths: List of valid storage paths

    Returns:
        Cleanup results
    """
    try:
        results = await storage_manager.cleanup_orphaned_files(valid_storage_paths)

        return {"success": True, "cleanup_results": results}
    except Exception as e:
        logger.error(f"Storage cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage cleanup failed: {str(e)}",
        )


@router.post("/batch-upload")
async def batch_upload_documents(
    documents: List[dict[str, Any]],
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Upload multiple documents in batch.

    Args:
        documents: List of document dictionaries with file_id, content, metadata

    Returns:
        Batch upload results
    """
    try:
        results = await storage_manager.upload_documents_batch(documents)

        return {
            "success": True,
            "results": results,
            "total_documents": len(documents),
            "successful_uploads": len(
                [r for r in results if r.get("result", {}).get("status") == "uploaded"]
            ),
        }
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch upload failed: {str(e)}",
        )


@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Get detailed performance metrics.

    Returns:
        Performance metrics including connection pool, batch processor, and rate limiter
    """
    try:
        metrics = await storage_manager.get_performance_metrics()

        return {"success": True, "metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}",
        )


@router.get("/document/{document_id}/url")
async def get_document_url(
    document_id: str,
    expires_in: int = 3600,
    current_user: User = Depends(get_current_user),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> dict[str, Any]:
    """
    Get presigned URL for document access.

    Args:
        document_id: Document ID
        expires_in: URL expiration time in seconds

    Returns:
        Presigned URL for document access
    """
    try:
        # This would typically require looking up the document in the database
        # For now, we'll return a placeholder
        return {
            "success": True,
            "message": "Document URL generation not implemented yet",
            "document_id": document_id,
            "expires_in": expires_in,
        }
    except Exception as e:
        logger.error(f"Failed to generate document URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate document URL: {str(e)}",
        )
