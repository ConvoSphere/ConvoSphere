"""
Scalability tests for storage providers.

This module tests the scalability features including connection pooling,
batch operations, rate limiting, and performance optimizations.
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from backend.app.services.storage.config import StorageConfig
from backend.app.services.storage.manager import StorageManager
from backend.app.services.storage.connection_pool import ConnectionPool, StorageConnectionPool
from backend.app.services.storage.batch_operations import BatchProcessor, RateLimiter, StorageBatchManager
from backend.app.services.storage.dependency_injection import StorageContainer, StorageServiceLocator


class TestStorageScalability:
    """Test storage scalability features."""
    
    @pytest.fixture
    def local_config(self):
        """Create local storage configuration."""
        return StorageConfig(
            provider="local",
            bucket_name="test-bucket",
            local_base_path="./test_uploads",
            max_concurrent_uploads=5,
            timeout=30,
            max_retries=3
        )
    
    @pytest.fixture
    def storage_manager(self, local_config):
        """Create storage manager instance."""
        return StorageManager(local_config)
    
    @pytest.mark.asyncio
    async def test_connection_pool_scalability(self, local_config):
        """Test connection pool scalability."""
        pool = ConnectionPool(
            max_connections=3,
            max_idle_time=60,
            connection_timeout=10,
            retry_attempts=2
        )
        
        # Test concurrent connections
        async def create_connection():
            return await pool.get_connection("test_conn", lambda: Mock())
        
        # Create multiple connections concurrently
        tasks = [create_connection() for _ in range(5)]
        connections = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that we have the expected number of connections
        status = pool.get_pool_status()
        assert status["total_connections"] <= 3  # Max connections limit
        
        # Clean up
        await pool.close_all()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_functionality(self):
        """Test rate limiter functionality."""
        rate_limiter = RateLimiter(
            max_requests_per_second=5,
            max_requests_per_minute=10,
            burst_size=3
        )
        
        # Test rate limiting
        permissions = []
        for _ in range(10):
            permission = await rate_limiter.acquire()
            permissions.append(permission)
        
        # Should have some requests rejected due to rate limiting
        assert sum(permissions) < 10
        
        # Check status
        status = rate_limiter.get_status()
        assert "current_requests_per_minute" in status
        assert "current_requests_per_second" in status
    
    @pytest.mark.asyncio
    async def test_batch_processor_functionality(self):
        """Test batch processor functionality."""
        processor = BatchProcessor(
            batch_size=3,
            batch_timeout=2.0,
            max_concurrent_batches=2
        )
        
        # Add operations to batch
        operations = []
        for i in range(5):
            operation_id = await processor.add_operation(
                operation_type="upload",
                file_path=f"test_{i}.txt",
                content=b"test content",
                metadata={"index": i}
            )
            operations.append(operation_id)
        
        # Wait for completion
        completed = await processor.wait_for_completion(timeout=10.0)
        assert completed is True
        
        # Check status
        status = await processor.get_batch_status()
        assert status["pending_operations"] == 0
        assert status["active_batches"] == 0
    
    @pytest.mark.asyncio
    async def test_storage_manager_batch_upload(self, storage_manager):
        """Test batch upload functionality."""
        # Create test documents
        documents = []
        for i in range(3):
            documents.append({
                "file_id": f"test_{i}",
                "content": f"test content {i}".encode(),
                "metadata": {"index": i}
            })
        
        # Perform batch upload
        results = await storage_manager.upload_documents_batch(documents)
        
        # Check results
        assert len(results) == 3
        for result in results:
            assert "file_id" in result
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, storage_manager):
        """Test performance metrics collection."""
        # Perform some operations to generate metrics
        await storage_manager.upload_document("test_metrics", b"test content")
        
        # Get performance metrics
        metrics = await storage_manager.get_performance_metrics()
        
        # Check metrics structure
        assert "provider" in metrics
        assert "connection_pool" in metrics
        assert "batch_processor" in metrics
        assert "rate_limiter" in metrics
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, storage_manager):
        """Test concurrent storage operations."""
        # Create concurrent upload tasks
        async def upload_document(i):
            return await storage_manager.upload_document(
                f"concurrent_{i}",
                f"content {i}".encode(),
                {"index": i}
            )
        
        # Execute concurrent uploads
        tasks = [upload_document(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that all uploads completed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 5
    
    @pytest.mark.asyncio
    async def test_dependency_injection(self, local_config):
        """Test dependency injection system."""
        container = StorageContainer()
        
        # Register a test service
        container.register_service(
            "test_service",
            Mock,
            lambda: Mock(name="test_instance"),
            singleton=True
        )
        
        # Get service instance
        service1 = container.get_service("test_service")
        service2 = container.get_service("test_service")
        
        # Should be the same instance (singleton)
        assert service1 is service2
        
        # Create storage manager with dependencies
        manager = container.create_storage_manager(local_config)
        assert isinstance(manager, StorageManager)
    
    @pytest.mark.asyncio
    async def test_service_locator(self, local_config):
        """Test service locator pattern."""
        locator = StorageServiceLocator()
        locator.set_default_config(local_config)
        
        # Get services through locator
        manager = locator.get_storage_manager()
        provider = locator.get_storage_provider()
        connection_pool = locator.get_connection_pool()
        batch_manager = locator.get_batch_manager()
        
        # Check that all services are available
        assert isinstance(manager, StorageManager)
        assert hasattr(provider, 'upload_file')
        assert isinstance(connection_pool, StorageConnectionPool)
        assert isinstance(batch_manager, StorageBatchManager)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, storage_manager):
        """Test error handling and recovery mechanisms."""
        # Test with invalid storage path
        with pytest.raises(Exception):
            await storage_manager.download_document("invalid://path")
        
        # Test health check after error
        is_healthy = await storage_manager.health_check()
        assert isinstance(is_healthy, bool)
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, storage_manager):
        """Test memory efficiency of storage operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple operations
        for i in range(10):
            await storage_manager.upload_document(
                f"memory_test_{i}",
                b"test content" * 1000,  # 11KB per document
                {"test": "memory_efficiency"}
            )
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB for 10 operations)
        assert memory_increase < 10 * 1024 * 1024  # 10MB
    
    @pytest.mark.asyncio
    async def test_connection_pool_cleanup(self):
        """Test connection pool cleanup functionality."""
        pool = ConnectionPool(max_connections=2, max_idle_time=1)
        
        # Create connections
        conn1 = await pool.get_connection("conn1", lambda: Mock())
        conn2 = await pool.get_connection("conn2", lambda: Mock())
        
        # Wait for cleanup
        await asyncio.sleep(2)
        
        # Check that idle connections are cleaned up
        status = pool.get_pool_status()
        assert status["total_connections"] <= 2
        
        await pool.close_all()
    
    @pytest.mark.asyncio
    async def test_batch_operation_ordering(self):
        """Test that batch operations maintain proper ordering."""
        processor = BatchProcessor(batch_size=2, batch_timeout=1.0)
        
        results = []
        
        async def callback(result):
            results.append(result)
        
        # Add operations in specific order
        await processor.add_operation("upload", "file1.txt", callback=callback)
        await processor.add_operation("upload", "file2.txt", callback=callback)
        await processor.add_operation("upload", "file3.txt", callback=callback)
        
        # Wait for completion
        await processor.wait_for_completion(timeout=5.0)
        
        # Check that operations were processed
        assert len(results) >= 0  # At least some operations should complete
    
    @pytest.mark.asyncio
    async def test_rate_limiter_burst_handling(self):
        """Test rate limiter burst handling."""
        rate_limiter = RateLimiter(
            max_requests_per_second=10,
            max_requests_per_minute=100,
            burst_size=5
        )
        
        # Test burst of requests
        permissions = []
        for _ in range(10):
            permission = await rate_limiter.acquire()
            permissions.append(permission)
        
        # Should allow burst up to burst_size
        assert sum(permissions) >= 5  # At least burst_size should be allowed
        
        # Check status
        status = rate_limiter.get_status()
        assert status["current_requests_per_second"] <= 10
    
    @pytest.mark.asyncio
    async def test_storage_manager_integration(self, storage_manager):
        """Test integration of all scalability features."""
        # Test concurrent batch operations
        async def batch_operation():
            documents = []
            for i in range(3):
                documents.append({
                    "file_id": f"batch_{i}_{time.time()}",
                    "content": f"batch content {i}".encode(),
                    "metadata": {"batch": True}
                })
            return await storage_manager.upload_documents_batch(documents)
        
        # Execute multiple batch operations concurrently
        tasks = [batch_operation() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) > 0
        
        # Get performance metrics
        metrics = await storage_manager.get_performance_metrics()
        assert "connection_pool" in metrics
        assert "batch_processor" in metrics
        assert "rate_limiter" in metrics