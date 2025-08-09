"""
Performance Integration Service.

This module provides integration between the new modular performance monitoring
system and existing services.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from backend.app.core.database import get_db
from backend.app.monitoring import (
    MetricType,
    get_performance_monitor,
)
from backend.app.services.cache_service import cache_service


class PerformanceConfig(BaseModel):
    """Performance configuration with validation."""

    enable_caching: bool = Field(default=True, description="Enable caching")
    enable_monitoring: bool = Field(
        default=True,
        description="Enable performance monitoring",
    )
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Default cache TTL",
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class PerformanceIntegration:
    """Main performance integration service."""

    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.initialized = False
        self.startup_time = datetime.now(UTC)

        # Service status
        self.services_status = {
            "cache": False,
            "monitoring": False,
        }

    async def initialize(self) -> None:
        """Initialize all performance services."""
        try:
            logger.info("Initializing performance integration services...")

            # Initialize cache service with graceful degradation
            if self.config.enable_caching:
                try:
                    await cache_service.initialize()
                    self.services_status["cache"] = True
                    logger.info("Cache service initialized")
                except Exception as e:
                    logger.warning(f"Cache service initialization failed: {e}")
                    self.services_status["cache"] = False

            # Initialize monitoring
            if self.config.enable_monitoring:
                try:
                    # Get database session for monitoring
                    db = next(get_db())
                    self.performance_monitor = get_performance_monitor(db)
                    await self.performance_monitor.start_monitoring()
                    self.services_status["monitoring"] = True
                    logger.info("Performance monitoring initialized")
                except Exception as e:
                    logger.warning(f"Performance monitoring initialization failed: {e}")
                    self.services_status["monitoring"] = False

            self.initialized = True
            logger.info("Performance integration services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize performance integration services: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown all performance services."""
        try:
            logger.info("Shutting down performance integration services...")

            # Stop monitoring
            if self.services_status["monitoring"]:
                try:
                    await self.performance_monitor.stop_monitoring()
                    logger.info("Performance monitoring stopped")
                except Exception as e:
                    logger.warning(f"Failed to stop performance monitoring: {e}")

            # Stop cache service
            if self.services_status["cache"]:
                try:
                    await cache_service.shutdown()
                    logger.info("Cache service stopped")
                except Exception as e:
                    logger.warning(f"Failed to stop cache service: {e}")

            logger.info("Performance integration services shut down successfully")

        except Exception as e:
            logger.error(f"Error during performance integration shutdown: {e}")

    def _ensure_initialized(self) -> None:
        """Ensure services are initialized."""
        if not self.initialized:
            raise RuntimeError("Performance integration services not initialized")

    async def get_cached_conversation(
        self,
        conversation_id: str,
    ) -> dict[str, Any] | None:
        """Get cached conversation data."""
        self._ensure_initialized()

        if not self.services_status["cache"]:
            return None

        try:
            return await cache_service.get(f"conversation:{conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to get cached conversation: {e}")
            return None

    async def cache_conversation(
        self,
        conversation_id: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """Cache conversation data."""
        self._ensure_initialized()

        if not self.services_status["cache"]:
            return False

        try:
            ttl = ttl or self.config.cache_ttl
            await cache_service.set(f"conversation:{conversation_id}", data, ttl)

            # Record cache operation metric
            if self.services_status["monitoring"]:
                self.performance_monitor.metrics_collector.record_metric(
                    name="cache_operation",
                    value=1.0,
                    metric_type=MetricType.COUNTER,
                    tags={
                        "operation": "set",
                        "namespace": "conversation",
                        "key": conversation_id,
                    },
                )

            return True
        except Exception as e:
            logger.warning(f"Failed to cache conversation: {e}")
            return False

    async def get_cached_ai_response(
        self,
        user_id: str,
        message: str,
        context: str | None = None,
    ) -> dict[str, Any] | None:
        """Get cached AI response."""
        self._ensure_initialized()

        if not self.services_status["cache"]:
            return None

        try:
            cache_key = f"ai_response:{user_id}:{hash(message + (context or ''))}"
            return await cache_service.get(cache_key)
        except Exception as e:
            logger.warning(f"Failed to get cached AI response: {e}")
            return None

    async def cache_ai_response(
        self,
        user_id: str,
        message: str,
        response: dict[str, Any],
        context: str | None = None,
        ttl: int | None = None,
    ) -> bool:
        """Cache AI response."""
        self._ensure_initialized()

        if not self.services_status["cache"]:
            return False

        try:
            ttl = ttl or self.config.cache_ttl
            cache_key = f"ai_response:{user_id}:{hash(message + (context or ''))}"
            await cache_service.set(cache_key, response, ttl)

            # Record cache operation metric
            if self.services_status["monitoring"]:
                self.performance_monitor.metrics_collector.record_metric(
                    name="cache_operation",
                    value=1.0,
                    metric_type=MetricType.COUNTER,
                    tags={
                        "operation": "set",
                        "namespace": "ai_response",
                        "user_id": user_id,
                    },
                )

            return True
        except Exception as e:
            logger.warning(f"Failed to cache AI response: {e}")
            return False

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: str | None = None,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """Record API request metrics."""
        self._ensure_initialized()

        if not self.services_status["monitoring"]:
            return

        try:
            # Record request metrics
            self.performance_monitor.metrics_collector.record_metric(
                name="api_requests_total",
                value=1.0,
                metric_type=MetricType.COUNTER,
                tags={
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code),
                },
            )

            # Record response time
            self.performance_monitor.metrics_collector.record_metric(
                name="api_response_time_seconds",
                value=response_time,
                metric_type=MetricType.TIMER,
                tags={
                    "endpoint": endpoint,
                    "method": method,
                },
            )

            # Record request/response sizes
            if request_size > 0:
                self.performance_monitor.metrics_collector.record_metric(
                    name="api_request_size_bytes",
                    value=float(request_size),
                    metric_type=MetricType.HISTOGRAM,
                    tags={"endpoint": endpoint},
                )

            if response_size > 0:
                self.performance_monitor.metrics_collector.record_metric(
                    name="api_response_size_bytes",
                    value=float(response_size),
                    metric_type=MetricType.HISTOGRAM,
                    tags={"endpoint": endpoint},
                )

        except Exception as e:
            logger.warning(f"Failed to record API request metrics: {e}")

    def record_database_query(
        self,
        query_type: str,
        table_name: str,
        execution_time: float,
        rows_affected: int = 0,
        query_size: int = 0,
        connection_pool_size: int = 0,
        error: str | None = None,
    ) -> None:
        """Record database query metrics."""
        self._ensure_initialized()

        if not self.services_status["monitoring"]:
            return

        try:
            # Record query metrics
            self.performance_monitor.metrics_collector.record_metric(
                name="database_queries_total",
                value=1.0,
                metric_type=MetricType.COUNTER,
                tags={
                    "query_type": query_type,
                    "table": table_name,
                    "error": str(error is not None),
                },
            )

            # Record execution time
            self.performance_monitor.metrics_collector.record_metric(
                name="database_query_time_seconds",
                value=execution_time,
                metric_type=MetricType.TIMER,
                tags={
                    "query_type": query_type,
                    "table": table_name,
                },
            )

            # Record rows affected
            if rows_affected > 0:
                self.performance_monitor.metrics_collector.record_metric(
                    name="database_rows_affected",
                    value=float(rows_affected),
                    metric_type=MetricType.HISTOGRAM,
                    tags={"query_type": query_type},
                )

        except Exception as e:
            logger.warning(f"Failed to record database query metrics: {e}")

    def record_performance_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        unit: str = "",
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record custom performance metric."""
        self._ensure_initialized()

        if not self.services_status["monitoring"]:
            return

        try:
            # Convert metric type string to enum
            type_mapping = {
                "counter": MetricType.COUNTER,
                "gauge": MetricType.GAUGE,
                "histogram": MetricType.HISTOGRAM,
                "timer": MetricType.TIMER,
            }

            metric_type_enum = type_mapping.get(metric_type.lower(), MetricType.GAUGE)

            # Add unit to tags if provided
            metric_tags = tags or {}
            if unit:
                metric_tags["unit"] = unit

            self.performance_monitor.metrics_collector.record_metric(
                name=metric_name,
                value=value,
                metric_type=metric_type_enum,
                tags=metric_tags,
            )

        except Exception as e:
            logger.warning(f"Failed to record performance metric: {e}")

    def get_performance_summary(
        self,
        time_range: timedelta = timedelta(hours=1),
    ) -> dict[str, Any]:
        """Get performance summary."""
        self._ensure_initialized()

        if not self.services_status["monitoring"]:
            return {"error": "Monitoring not available"}

        try:
            # Get performance snapshot
            snapshot = self.performance_monitor.get_performance_snapshot()

            # Get metrics summary
            metrics_summary = (
                self.performance_monitor.metrics_collector.get_metric_summary()
            )

            # Get alert summary
            alert_summary = self.performance_monitor.alert_manager.get_alert_summary()

            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "time_range_hours": time_range.total_seconds() / 3600,
                "system_metrics": {
                    "cpu_percent": snapshot.cpu_percent,
                    "memory_percent": snapshot.memory_percent,
                    "disk_usage_percent": snapshot.disk_usage_percent,
                },
                "database_metrics": {
                    "active_connections": snapshot.active_connections,
                    "slow_queries": snapshot.slow_queries,
                },
                "request_metrics": {
                    "request_count": snapshot.request_count,
                    "error_count": snapshot.error_count,
                    "avg_response_time": snapshot.avg_response_time,
                },
                "cache_metrics": {
                    "cache_hit_rate": snapshot.cache_hit_rate,
                },
                "metrics_summary": metrics_summary,
                "alert_summary": alert_summary,
                "services_status": self.services_status,
            }

        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of all services."""
        return {
            "initialized": self.initialized,
            "startup_time": self.startup_time.isoformat(),
            "uptime_seconds": (datetime.now(UTC) - self.startup_time).total_seconds(),
            "services_status": self.services_status,
            "config": self.config.model_dump(),
        }


# Global performance integration instance
performance_integration = PerformanceIntegration(
    PerformanceConfig(
        enable_caching=True,
        enable_monitoring=True,
        cache_ttl=3600,
    )
)
