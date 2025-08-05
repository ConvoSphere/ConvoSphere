"""
Storage factory for creating storage providers.

This module provides a factory pattern for creating different storage providers
based on configuration.
"""

from loguru import logger

from .base import StorageError, StorageProvider
from .config import StorageConfig
from .local import LocalStorageProvider
from .minio import MinIOStorageProvider


class StorageFactory:
    """Factory for creating storage providers."""

    _providers: dict[str, type[StorageProvider]] = {
        "local": LocalStorageProvider,
        "minio": MinIOStorageProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: type[StorageProvider]):
        """
        Register a custom storage provider.

        Args:
            name: Provider name
            provider_class: Storage provider class
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered storage provider: {name}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available storage providers."""
        return list(cls._providers.keys())

    @classmethod
    def create_provider(cls, config: StorageConfig) -> StorageProvider:
        """
        Create storage provider based on configuration.

        Args:
            config: Storage configuration

        Returns:
            Configured storage provider instance

        Raises:
            StorageError: If provider creation fails
        """
        try:
            # Validate configuration
            config.validate_provider_config()

            # Get provider class
            provider_name = config.provider.lower()
            provider_class = cls._providers.get(provider_name)

            if not provider_class:
                available = ", ".join(cls.get_available_providers())
                raise StorageError(
                    f"Unsupported storage provider: {provider_name}. "
                    f"Available providers: {available}",
                    provider=provider_name,
                    operation="create"
                )

            # Create provider instance
            provider = provider_class(config)

            logger.info(f"Created storage provider: {provider_name}")
            return provider

        except Exception as e:
            if isinstance(e, StorageError):
                raise
            raise StorageError(
                f"Failed to create storage provider: {str(e)}",
                provider=config.provider,
                operation="create"
            )

    @classmethod
    def create_provider_from_dict(cls, config_dict: dict) -> StorageProvider:
        """
        Create storage provider from dictionary configuration.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Configured storage provider instance
        """
        config = StorageConfig(**config_dict)
        return cls.create_provider(config)

    @classmethod
    def test_provider(cls, config: StorageConfig) -> bool:
        """
        Test if a storage provider can be created and is healthy.

        Args:
            config: Storage configuration

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            provider = cls.create_provider(config)
            return provider.health_check()
        except Exception as e:
            logger.error(f"Storage provider test failed: {e}")
            return False


# Register additional providers when available
def _register_cloud_providers():
    """Register cloud storage providers if available."""

    # S3 Provider
    try:
        from .s3 import S3StorageProvider
        StorageFactory.register_provider("s3", S3StorageProvider)
        logger.info("Registered S3 storage provider")
    except ImportError:
        logger.debug("S3 storage provider not available")

    # GCS Provider
    try:
        from .gcs import GCSStorageProvider
        StorageFactory.register_provider("gcs", GCSStorageProvider)
        logger.info("Registered GCS storage provider")
    except ImportError:
        logger.debug("GCS storage provider not available")

    # Azure Provider
    try:
        from .azure import AzureBlobStorageProvider
        StorageFactory.register_provider("azure", AzureBlobStorageProvider)
        logger.info("Registered Azure Blob storage provider")
    except ImportError:
        logger.debug("Azure Blob storage provider not available")


# Initialize cloud providers
_register_cloud_providers()
