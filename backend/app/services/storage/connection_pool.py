"""
Connection pool management for storage providers.

This module provides connection pooling and performance optimization
for storage operations to improve scalability.
"""

import asyncio
import contextlib
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger

from .base import StorageError


@dataclass
class ConnectionMetrics:
    """Connection performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    last_used: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ConnectionPool:
    """Connection pool for storage providers."""

    def __init__(
        self,
        max_connections: int = 10,
        max_idle_time: int = 300,  # 5 minutes
        connection_timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.connection_timeout = connection_timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        self._connections: dict[str, Any] = {}
        self._metrics: dict[str, ConnectionMetrics] = defaultdict(ConnectionMetrics)
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

        # Start cleanup task
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_idle_connections())

    async def _cleanup_idle_connections(self):
        """Clean up idle connections periodically."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._remove_idle_connections()
            except Exception as e:
                logger.error(f"Connection cleanup error: {e}")

    async def _remove_idle_connections(self):
        """Remove idle connections."""
        async with self._lock:
            current_time = datetime.utcnow()
            idle_connections = []

            for conn_id in self._connections:
                metrics = self._metrics[conn_id]
                if (
                    metrics.last_used
                    and (current_time - metrics.last_used).total_seconds()
                    > self.max_idle_time
                ):
                    idle_connections.append(conn_id)

            for conn_id in idle_connections:
                await self._close_connection(conn_id)
                logger.debug(f"Removed idle connection: {conn_id}")

    async def _close_connection(self, conn_id: str):
        """Close a specific connection."""
        if conn_id in self._connections:
            try:
                conn = self._connections[conn_id]
                if hasattr(conn, "close"):
                    await conn.close()
                elif hasattr(conn, "close"):
                    conn.close()
            except Exception as e:
                logger.warning(f"Error closing connection {conn_id}: {e}")
            finally:
                del self._connections[conn_id]
                if conn_id in self._metrics:
                    del self._metrics[conn_id]

    async def get_connection(self, conn_id: str, factory: Callable) -> Any:
        """Get or create a connection."""
        async with self._lock:
            # Check if connection exists and is valid
            if conn_id in self._connections:
                conn = self._connections[conn_id]
                if await self._is_connection_valid(conn):
                    self._metrics[conn_id].last_used = datetime.utcnow()
                    return conn

            # Check if we can create a new connection
            if len(self._connections) >= self.max_connections:
                # Remove oldest connection
                oldest_conn_id = min(
                    self._connections.keys(),
                    key=lambda x: self._metrics[x].last_used or datetime.min,
                )
                await self._close_connection(oldest_conn_id)

            # Create new connection
            try:
                conn = await factory()
                self._connections[conn_id] = conn
                self._metrics[conn_id] = ConnectionMetrics()
                logger.debug(f"Created new connection: {conn_id}")
                return conn
            except Exception as e:
                logger.error(f"Failed to create connection {conn_id}: {e}")
                raise StorageError(f"Connection creation failed: {e}")

    async def _is_connection_valid(self, conn: Any) -> bool:
        """Check if connection is still valid."""
        try:
            # Try to perform a simple operation to test connection
            if hasattr(conn, "ping"):
                await conn.ping()
            elif hasattr(conn, "health_check"):
                await conn.health_check()
            return True
        except Exception:
            return False

    async def execute_with_retry(
        self, conn_id: str, factory: Callable, operation: Callable, *args, **kwargs
    ) -> Any:
        """Execute operation with connection pooling and retry logic."""
        start_time = time.time()
        last_exception = None

        for attempt in range(self.retry_attempts):
            try:
                # Get connection from pool
                conn = await self.get_connection(conn_id, factory)

                # Execute operation
                result = await operation(conn, *args, **kwargs)

                # Update metrics
                response_time = time.time() - start_time
                metrics = self._metrics[conn_id]
                metrics.total_requests += 1
                metrics.successful_requests += 1
                metrics.total_response_time += response_time
                metrics.average_response_time = (
                    metrics.total_response_time / metrics.total_requests
                )
                metrics.last_used = datetime.utcnow()

                return result

            except Exception as e:
                last_exception = e
                metrics = self._metrics[conn_id]
                metrics.total_requests += 1
                metrics.failed_requests += 1

                # Remove failed connection
                if conn_id in self._connections:
                    await self._close_connection(conn_id)

                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(
                        self.retry_delay * (2**attempt)
                    )  # Exponential backoff
                    logger.warning(
                        f"Retry {attempt + 1}/{self.retry_attempts} for {conn_id}: {e}"
                    )

        # All retries failed
        logger.error(f"All retries failed for {conn_id}: {last_exception}")
        raise last_exception

    async def close_all(self):
        """Close all connections."""
        async with self._lock:
            for conn_id in list(self._connections.keys()):
                await self._close_connection(conn_id)

            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._cleanup_task

    def get_metrics(self) -> dict[str, ConnectionMetrics]:
        """Get connection pool metrics."""
        return dict(self._metrics)

    def get_pool_status(self) -> dict[str, Any]:
        """Get connection pool status."""
        return {
            "total_connections": len(self._connections),
            "max_connections": self.max_connections,
            "available_connections": self.max_connections - len(self._connections),
            "metrics": self.get_metrics(),
        }


class StorageConnectionPool:
    """Storage-specific connection pool manager."""

    def __init__(self):
        self._pools: dict[str, ConnectionPool] = {}
        self._default_config = {
            "max_connections": 10,
            "max_idle_time": 300,
            "connection_timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1.0,
        }

    def get_pool(
        self, provider_name: str, config: dict[str, Any] = None
    ) -> ConnectionPool:
        """Get or create connection pool for provider."""
        if provider_name not in self._pools:
            pool_config = {**self._default_config, **(config or {})}
            self._pools[provider_name] = ConnectionPool(**pool_config)

        return self._pools[provider_name]

    async def close_all_pools(self):
        """Close all connection pools."""
        for pool in self._pools.values():
            await pool.close_all()
        self._pools.clear()

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics from all pools."""
        return {
            provider: pool.get_pool_status() for provider, pool in self._pools.items()
        }


# Global connection pool manager
storage_connection_pool = StorageConnectionPool()
