"""
Batch operations and rate limiting for storage providers.

This module provides batch processing capabilities and rate limiting
to improve performance and prevent API throttling.
"""

import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from .base import StorageError


@dataclass
class BatchOperation:
    """Represents a batch operation."""

    operation_type: str
    file_path: str
    content: bytes | None = None
    metadata: dict[str, Any] | None = None
    callback: Callable | None = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class RateLimiter:
    """Rate limiter for storage operations."""

    def __init__(
        self,
        max_requests_per_second: int = 10,
        max_requests_per_minute: int = 600,
        burst_size: int = 20,
    ):
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_minute = max_requests_per_minute
        self.burst_size = burst_size

        self._request_times: deque = deque()
        self._last_request_time: datetime | None = None
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire permission to make a request."""
        async with self._lock:
            now = datetime.utcnow()

            # Remove old requests from tracking
            while self._request_times and (now - self._request_times[0]) > timedelta(
                minutes=1
            ):
                self._request_times.popleft()

            # Check rate limits
            if len(self._request_times) >= self.max_requests_per_minute:
                return False

            # Check burst limit
            recent_requests = sum(
                1 for t in self._request_times if (now - t) <= timedelta(seconds=1)
            )
            if recent_requests >= self.burst_size:
                return False

            # Add current request
            self._request_times.append(now)
            self._last_request_time = now

            return True

    async def wait_for_permission(self, timeout: float = 30.0) -> bool:
        """Wait for permission to make a request."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await self.acquire():
                return True

            # Wait before retrying
            await asyncio.sleep(0.1)

        return False

    def get_status(self) -> dict[str, Any]:
        """Get rate limiter status."""
        now = datetime.utcnow()
        recent_requests = sum(
            1 for t in self._request_times if (now - t) <= timedelta(seconds=1)
        )

        return {
            "max_requests_per_second": self.max_requests_per_second,
            "max_requests_per_minute": self.max_requests_per_minute,
            "burst_size": self.burst_size,
            "current_requests_per_minute": len(self._request_times),
            "current_requests_per_second": recent_requests,
            "last_request_time": self._last_request_time.isoformat()
            if self._last_request_time
            else None,
        }


class BatchProcessor:
    """Batch processor for storage operations."""

    def __init__(
        self,
        batch_size: int = 10,
        batch_timeout: float = 5.0,
        max_concurrent_batches: int = 5,
    ):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_concurrent_batches = max_concurrent_batches

        self._pending_operations: deque = deque()
        self._active_batches: dict[str, list[BatchOperation]] = {}
        self._batch_results: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._processing_task: asyncio.Task | None = None

        # Start processing task
        self._start_processing_task()

    def _start_processing_task(self):
        """Start background processing task."""
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_batches())

    async def _process_batches(self):
        """Process batches in background."""
        while True:
            try:
                await asyncio.sleep(0.1)  # Check frequently
                await self._process_pending_operations()
            except Exception as e:
                logger.error(f"Batch processing error: {e}")

    async def _process_pending_operations(self):
        """Process pending operations."""
        async with self._lock:
            if len(self._pending_operations) >= self.batch_size:
                batch_id = f"batch_{int(time.time())}"
                batch_operations = []

                # Create batch
                for _ in range(self.batch_size):
                    if self._pending_operations:
                        batch_operations.append(self._pending_operations.popleft())

                if batch_operations:
                    self._active_batches[batch_id] = batch_operations
                    # Process batch asynchronously
                    asyncio.create_task(self._execute_batch(batch_id, batch_operations))

    async def _execute_batch(self, batch_id: str, operations: list[BatchOperation]):
        """Execute a batch of operations."""
        try:
            results = {}

            # Group operations by type
            upload_ops = [op for op in operations if op.operation_type == "upload"]
            download_ops = [op for op in operations if op.operation_type == "download"]
            delete_ops = [op for op in operations if op.operation_type == "delete"]

            # Execute operations in parallel
            tasks = []

            # Upload operations
            if upload_ops:
                tasks.append(self._execute_upload_batch(upload_ops))

            # Download operations
            if download_ops:
                tasks.append(self._execute_download_batch(download_ops))

            # Delete operations
            if delete_ops:
                tasks.append(self._execute_delete_batch(delete_ops))

            # Wait for all operations to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine results
            for result in batch_results:
                if isinstance(result, dict):
                    results.update(result)

            # Store results
            self._batch_results[batch_id] = results

            # Call callbacks
            for operation in operations:
                if operation.callback:
                    try:
                        result = results.get(operation.file_path)
                        await operation.callback(result)
                    except Exception as e:
                        logger.error(f"Callback error for {operation.file_path}: {e}")

            logger.info(f"Completed batch {batch_id} with {len(operations)} operations")

        except Exception as e:
            logger.error(f"Batch execution error for {batch_id}: {e}")
            self._batch_results[batch_id] = {"error": str(e)}
        finally:
            # Clean up
            if batch_id in self._active_batches:
                del self._active_batches[batch_id]

    async def _execute_upload_batch(
        self, operations: list[BatchOperation]
    ) -> dict[str, Any]:
        """Execute batch upload operations."""
        # This would be implemented by the specific storage provider
        # For now, return placeholder
        return {op.file_path: {"status": "uploaded"} for op in operations}

    async def _execute_download_batch(
        self, operations: list[BatchOperation]
    ) -> dict[str, Any]:
        """Execute batch download operations."""
        # This would be implemented by the specific storage provider
        # For now, return placeholder
        return {op.file_path: {"status": "downloaded"} for op in operations}

    async def _execute_delete_batch(
        self, operations: list[BatchOperation]
    ) -> dict[str, Any]:
        """Execute batch delete operations."""
        # This would be implemented by the specific storage provider
        # For now, return placeholder
        return {op.file_path: {"status": "deleted"} for op in operations}

    async def add_operation(
        self,
        operation_type: str,
        file_path: str,
        content: bytes | None = None,
        metadata: dict[str, Any] | None = None,
        callback: Callable | None = None,
    ) -> str:
        """Add operation to batch queue."""
        operation = BatchOperation(
            operation_type=operation_type,
            file_path=file_path,
            content=content,
            metadata=metadata,
            callback=callback,
        )

        async with self._lock:
            self._pending_operations.append(operation)

        return operation.file_path

    async def get_batch_status(self) -> dict[str, Any]:
        """Get batch processor status."""
        async with self._lock:
            return {
                "pending_operations": len(self._pending_operations),
                "active_batches": len(self._active_batches),
                "batch_size": self.batch_size,
                "batch_timeout": self.batch_timeout,
                "max_concurrent_batches": self.max_concurrent_batches,
            }

    async def wait_for_completion(self, timeout: float = 30.0) -> bool:
        """Wait for all pending operations to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            async with self._lock:
                if not self._pending_operations and not self._active_batches:
                    return True

            await asyncio.sleep(0.1)

        return False


class StorageBatchManager:
    """Storage batch operation manager."""

    def __init__(self):
        self._processors: dict[str, BatchProcessor] = {}
        self._rate_limiters: dict[str, RateLimiter] = {}
        self._default_config = {
            "batch_size": 10,
            "batch_timeout": 5.0,
            "max_concurrent_batches": 5,
            "max_requests_per_second": 10,
            "max_requests_per_minute": 600,
            "burst_size": 20,
        }

    def get_processor(
        self, provider_name: str, config: dict[str, Any] = None
    ) -> BatchProcessor:
        """Get or create batch processor for provider."""
        if provider_name not in self._processors:
            processor_config = {**self._default_config, **(config or {})}
            self._processors[provider_name] = BatchProcessor(
                batch_size=processor_config["batch_size"],
                batch_timeout=processor_config["batch_timeout"],
                max_concurrent_batches=processor_config["max_concurrent_batches"],
            )

        return self._processors[provider_name]

    def get_rate_limiter(
        self, provider_name: str, config: dict[str, Any] = None
    ) -> RateLimiter:
        """Get or create rate limiter for provider."""
        if provider_name not in self._rate_limiters:
            limiter_config = {**self._default_config, **(config or {})}
            self._rate_limiters[provider_name] = RateLimiter(
                max_requests_per_second=limiter_config["max_requests_per_second"],
                max_requests_per_minute=limiter_config["max_requests_per_minute"],
                burst_size=limiter_config["burst_size"],
            )

        return self._rate_limiters[provider_name]

    async def execute_with_rate_limit(
        self, provider_name: str, operation: Callable, *args, **kwargs
    ) -> Any:
        """Execute operation with rate limiting."""
        rate_limiter = self.get_rate_limiter(provider_name)

        # Wait for permission
        if not await rate_limiter.wait_for_permission():
            raise StorageError("Rate limit exceeded")

        # Execute operation
        return await operation(*args, **kwargs)

    async def add_batch_operation(
        self,
        provider_name: str,
        operation_type: str,
        file_path: str,
        content: bytes | None = None,
        metadata: dict[str, Any] | None = None,
        callback: Callable | None = None,
    ) -> str:
        """Add operation to batch queue."""
        processor = self.get_processor(provider_name)
        return await processor.add_operation(
            operation_type, file_path, content, metadata, callback
        )

    def get_all_status(self) -> dict[str, dict[str, Any]]:
        """Get status from all processors and rate limiters."""
        status = {}

        for provider, processor in self._processors.items():
            status[provider] = {
                "processor": processor.get_batch_status(),
                "rate_limiter": self._rate_limiters[provider].get_status(),
            }

        return status


# Global batch manager
storage_batch_manager = StorageBatchManager()
