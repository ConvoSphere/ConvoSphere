"""
Integration tests for storage providers.

This module tests the storage provider implementations
including local filesystem and MinIO storage.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.app.services.storage.config import StorageConfig
from backend.app.services.storage.factory import StorageFactory
from backend.app.services.storage.manager import StorageManager
from backend.app.services.storage.base import StorageError


class TestStorageProviders:
    """Test storage provider implementations."""

    @pytest.fixture
    def local_config(self):
        """Create local storage configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(
                provider="local",
                bucket_name="test-bucket",
                local_base_path=temp_dir
            )
            yield config

    @pytest.fixture
    def minio_config(self):
        """Create MinIO storage configuration."""
        config = StorageConfig(
            provider="minio",
            bucket_name="test-bucket",
            minio_endpoint="localhost:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
            minio_secure=False
        )
        return config

    @pytest.mark.asyncio
    async def test_local_storage_provider(self, local_config):
        """Test local storage provider functionality."""
        # Create provider
        provider = StorageFactory.create_provider(local_config)
        
        # Test upload
        content = b"test content"
        storage_path = await provider.upload_file("test.txt", content, {"test": "metadata"})
        
        assert storage_path.startswith("local://")
        assert "test.txt" in storage_path
        
        # Test download
        downloaded_content = await provider.download_file(storage_path)
        assert downloaded_content == content
        
        # Test file exists
        assert await provider.file_exists(storage_path) is True
        
        # Test get metadata
        metadata = await provider.get_file_metadata(storage_path)
        assert metadata["size"] == len(content)
        assert metadata["provider"] == "local"
        
        # Test get URL
        url = await provider.get_file_url(storage_path)
        assert url.startswith("file://")
        
        # Test delete
        success = await provider.delete_file(storage_path)
        assert success is True
        
        # Test file doesn't exist after deletion
        assert await provider.file_exists(storage_path) is False

    @pytest.mark.asyncio
    async def test_local_storage_manager(self, local_config):
        """Test storage manager with local provider."""
        manager = StorageManager(local_config)
        
        # Test upload document
        file_id = "test-123"
        content = b"document content"
        metadata = {"title": "Test Document"}
        
        storage_path = await manager.upload_document(file_id, content, metadata)
        assert storage_path.startswith("local://")
        
        # Test download document
        downloaded_content = await manager.download_document(storage_path)
        assert downloaded_content == content
        
        # Test document exists
        assert await manager.document_exists(storage_path) is True
        
        # Test get document metadata
        doc_metadata = await manager.get_document_metadata(storage_path)
        assert doc_metadata["size"] == len(content)
        
        # Test delete document
        success = await manager.delete_document(storage_path)
        assert success is True

    @pytest.mark.asyncio
    async def test_storage_factory(self):
        """Test storage factory functionality."""
        # Test available providers
        providers = StorageFactory.get_available_providers()
        assert "local" in providers
        assert "minio" in providers
        
        # Test provider creation
        config = StorageConfig(provider="local", bucket_name="test")
        provider = StorageFactory.create_provider(config)
        assert provider.get_provider_name() == "local"
        
        # Test invalid provider
        with pytest.raises(StorageError):
            invalid_config = StorageConfig(provider="invalid", bucket_name="test")
            StorageFactory.create_provider(invalid_config)

    @pytest.mark.asyncio
    async def test_storage_config_validation(self):
        """Test storage configuration validation."""
        # Test valid local config
        valid_config = StorageConfig(
            provider="local",
            bucket_name="valid-bucket"
        )
        assert valid_config.validate_provider_config() is True
        
        # Test invalid bucket name
        with pytest.raises(ValueError):
            StorageConfig(
                provider="local",
                bucket_name=""  # Empty bucket name
            )
        
        # Test invalid provider
        with pytest.raises(ValueError):
            StorageConfig(
                provider="invalid-provider",
                bucket_name="test"
            )

    @pytest.mark.asyncio
    async def test_storage_error_handling(self, local_config):
        """Test storage error handling."""
        provider = StorageFactory.create_provider(local_config)
        
        # Test download non-existent file
        with pytest.raises(StorageError):
            await provider.download_file("local://test-bucket/non-existent.txt")
        
        # Test get metadata for non-existent file
        with pytest.raises(StorageError):
            await provider.get_file_metadata("local://test-bucket/non-existent.txt")

    @pytest.mark.asyncio
    async def test_storage_health_check(self, local_config):
        """Test storage health check functionality."""
        provider = StorageFactory.create_provider(local_config)
        
        # Test health check
        is_healthy = await provider.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_storage_info(self, local_config):
        """Test storage information retrieval."""
        provider = StorageFactory.create_provider(local_config)
        
        # Upload some test files
        await provider.upload_file("test1.txt", b"content1")
        await provider.upload_file("test2.txt", b"content2")
        
        # Get storage info
        info = provider.get_storage_info()
        assert info["provider"] == "local"
        assert info["total_files"] >= 2
        assert info["total_size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_storage_manager_health_check(self, local_config):
        """Test storage manager health check with caching."""
        manager = StorageManager(local_config)
        
        # Test health check
        is_healthy = await manager.health_check()
        assert is_healthy is True
        
        # Test cached health check
        is_healthy_cached = await manager.health_check()
        assert is_healthy_cached is True
        
        # Test forced health check
        is_healthy_forced = await manager.health_check(force=True)
        assert is_healthy_forced is True

    @pytest.mark.asyncio
    async def test_storage_manager_info(self, local_config):
        """Test storage manager information retrieval."""
        manager = StorageManager(local_config)
        
        # Upload test document
        await manager.upload_document("test-123", b"test content")
        
        # Get storage info
        info = await manager.get_storage_info()
        assert info["provider_name"] == "local"
        assert info["config_provider"] == "local"
        assert "health_check_time" in info

    @pytest.mark.asyncio
    async def test_storage_migration(self, local_config):
        """Test storage migration functionality."""
        # Create two different configs for migration
        source_config = StorageConfig(
            provider="local",
            bucket_name="source-bucket",
            local_base_path=tempfile.mkdtemp()
        )
        
        target_config = StorageConfig(
            provider="local",
            bucket_name="target-bucket",
            local_base_path=tempfile.mkdtemp()
        )
        
        # Create managers
        source_manager = StorageManager(source_config)
        target_manager = StorageManager(target_config)
        
        # Upload document to source
        storage_path = await source_manager.upload_document("test-123", b"migration content")
        
        # Test migration
        results = await source_manager.migrate_storage(
            source_config, target_config, [storage_path]
        )
        
        assert results["total"] == 1
        assert results["successful"] == 1
        assert results["failed"] == 0

    @pytest.mark.asyncio
    async def test_storage_cleanup(self, local_config):
        """Test storage cleanup functionality."""
        manager = StorageManager(local_config)
        
        # Test cleanup (basic implementation)
        results = await manager.cleanup_orphaned_files(["valid-path"])
        
        assert "total_checked" in results
        assert "deleted" in results
        assert "errors" in results

    def test_storage_config_provider_specific(self):
        """Test provider-specific configuration methods."""
        # Test local config
        local_config = StorageConfig(provider="local", bucket_name="test")
        local_provider_config = local_config.get_provider_config()
        assert local_provider_config["base_path"] == "./uploads"
        assert local_provider_config["bucket_name"] == "test"
        
        # Test MinIO config
        minio_config = StorageConfig(
            provider="minio",
            bucket_name="test",
            minio_endpoint="localhost:9000",
            minio_access_key="test-key",
            minio_secret_key="test-secret"
        )
        minio_provider_config = minio_config.get_provider_config()
        assert minio_provider_config["endpoint"] == "localhost:9000"
        assert minio_provider_config["access_key"] == "test-key"
        assert minio_provider_config["bucket_name"] == "test"

    @pytest.mark.asyncio
    async def test_storage_manager_provider_info(self, local_config):
        """Test storage manager provider information."""
        manager = StorageManager(local_config)
        
        assert manager.get_provider_name() == "local"
        assert manager.get_config() == local_config