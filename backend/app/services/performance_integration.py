"""
Performance Integration Service for Phase 3.

This module integrates all Phase 3 services (caching, async processing, monitoring)
into a unified interface for easy use throughout the application.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from backend.app.core.exceptions import ConfigurationError
from backend.app.services.async_processor import (
    TaskPriority,
    TaskRequest,
    TaskType,
    async_processor,
    initialize_default_handlers,
)
from backend.app.services.cache_service import (
    ai_response_cache,
    cache_service,
    conversation_cache,
    tool_result_cache,
)
from backend.app.services.performance_monitor import (
    APIMetric,
    CacheMetric,
    DatabaseQueryMetric,
    PerformanceMetric,
    database_optimizer,
    performance_monitor,
)


class PerformanceConfig(BaseModel):
    """Performance configuration with validation."""

    enable_caching: bool = Field(default=True, description="Enable caching")
    enable_async_processing: bool = Field(
        default=True,
        description="Enable async processing",
    )
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
    max_async_workers: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum async workers",
    )
    monitoring_interval: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Monitoring interval in seconds",
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
            "async_processor": False,
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
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Cache service initialization failed (connection error): {e}")
                    self.services_status["cache"] = False
                except ValueError as e:
                    logger.warning(f"Cache service initialization failed (configuration error): {e}")
                    self.services_status["cache"] = False
                except Exception as e:
                    logger.warning(f"Cache service initialization failed (unexpected error): {e}")
                    self.services_status["cache"] = False

            # Initialize async processor
            if self.config.enable_async_processing:
                try:
                    initialize_default_handlers()
                    await async_processor.start()
                    self.services_status["async_processor"] = True
                    logger.info("Async processor initialized")
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Async processor initialization failed (connection error): {e}")
                    self.services_status["async_processor"] = False
                except ValueError as e:
                    logger.warning(f"Async processor initialization failed (configuration error): {e}")
                    self.services_status["async_processor"] = False
                except Exception as e:
                    logger.warning(f"Async processor initialization failed (unexpected error): {e}")
                    self.services_status["async_processor"] = False

            # Initialize monitoring
            if self.config.enable_monitoring:
                self.services_status["monitoring"] = True
                logger.info("Performance monitoring initialized")

            self.initialized = True
            logger.info("Performance integration services initialized successfully")

        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to initialize performance services (connection error): {e}")
            raise ConfigurationError(f"Performance initialization failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Failed to initialize performance services (configuration error): {e}")
            raise ConfigurationError(f"Performance initialization failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize performance services (unexpected error): {e}")
            raise ConfigurationError(f"Performance initialization failed: {str(e)}")

    async def shutdown(self) -> None:
        """Shutdown all performance services."""
        try:
            logger.info("Shutting down performance integration services...")

            # Shutdown async processor
            if self.services_status["async_processor"]:
                try:
                    await async_processor.stop()
                    self.services_status["async_processor"] = False
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Async processor shutdown failed (connection error): {e}")
                except Exception as e:
                    logger.warning(f"Async processor shutdown failed (unexpected error): {e}")

            # Shutdown cache service
            if self.services_status["cache"]:
                try:
                    await cache_service.close()
                    self.services_status["cache"] = False
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Cache service shutdown failed (connection error): {e}")
                except Exception as e:
                    logger.warning(f"Cache service shutdown failed (unexpected error): {e}")

            self.initialized = False
            logger.info("Performance integration services shut down successfully")

        except Exception as e:
            logger.error(f"Error during performance services shutdown: {e}")

    def _ensure_initialized(self) -> None:
        """Ensure services are initialized."""
        if not self.initialized:
            raise ConfigurationError("Performance integration services not initialized")

    # Cache Integration Methods

    async def get_cached_conversation(
        self,
        conversation_id: str,
    ) -> dict[str, Any] | None:
        """Get cached conversation data."""
        if not self.config.enable_caching:
            return None

        try:
            return await conversation_cache.get_conversation(conversation_id)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to get cached conversation (connection error): {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to get cached conversation (invalid data): {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get cached conversation (unexpected error): {e}")
            return None

    async def cache_conversation(
        self,
        conversation_id: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """Cache conversation data."""
        if not self.config.enable_caching:
            return False

        try:
            success = await conversation_cache.set_conversation(
                conversation_id,
                data,
                ttl or self.config.cache_ttl,
            )

            # Record cache metric
            if self.config.enable_monitoring:
                cache_metric = CacheMetric(
                    operation="set",
                    namespace="conversation",
                    key=f"{conversation_id}:data",
                    operation_time=0.001,  # Approximate
                    cache_hit=False,
                    data_size=len(str(data)),
                )
                performance_monitor.record_cache_operation(cache_metric)

            return success
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to cache conversation (connection error): {e}")
            return False
        except ValueError as e:
            logger.error(f"Failed to cache conversation (invalid data): {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to cache conversation (unexpected error): {e}")
            return False

    async def get_cached_ai_response(
        self,
        user_id: str,
        message: str,
        context: str | None = None,
    ) -> dict[str, Any] | None:
        """Get cached AI response."""
        if not self.config.enable_caching:
            return None

        try:
            response = await ai_response_cache.get_response(user_id, message, context)

            # Record cache metric
            if self.config.enable_monitoring:
                cache_metric = CacheMetric(
                    operation="get",
                    namespace="ai_response",
                    key=f"{user_id}:{hash(message + (context or ''))}",
                    operation_time=0.001,  # Approximate
                    cache_hit=response is not None,
                    data_size=len(str(response)) if response else 0,
                )
                performance_monitor.record_cache_operation(cache_metric)

            return response
        except Exception as e:
            logger.error(f"Failed to get cached AI response: {e}")
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
        if not self.config.enable_caching:
            return False

        try:
            success = await ai_response_cache.set_response(
                user_id,
                message,
                response,
                context,
                ttl or self.config.cache_ttl,
            )

            # Record cache metric
            if self.config.enable_monitoring:
                cache_metric = CacheMetric(
                    operation="set",
                    namespace="ai_response",
                    key=f"{user_id}:{hash(message + (context or ''))}",
                    operation_time=0.001,  # Approximate
                    cache_hit=False,
                    data_size=len(str(response)),
                )
                performance_monitor.record_cache_operation(cache_metric)

            return success
        except Exception as e:
            logger.error(f"Failed to cache AI response: {e}")
            return False

    async def get_cached_tool_result(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any | None:
        """Get cached tool result."""
        if not self.config.enable_caching:
            return None

        try:
            result = await tool_result_cache.get_result(tool_name, arguments)

            # Record cache metric
            if self.config.enable_monitoring:
                cache_metric = CacheMetric(
                    operation="get",
                    namespace="tool_result",
                    key=f"{tool_name}:{hash(str(arguments))}",
                    operation_time=0.001,  # Approximate
                    cache_hit=result is not None,
                    data_size=len(str(result)) if result else 0,
                )
                performance_monitor.record_cache_operation(cache_metric)

            return result
        except Exception as e:
            logger.error(f"Failed to get cached tool result: {e}")
            return None

    async def cache_tool_result(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        ttl: int | None = None,
    ) -> bool:
        """Cache tool result."""
        if not self.config.enable_caching:
            return False

        try:
            success = await tool_result_cache.set_result(
                tool_name,
                arguments,
                result,
                ttl or self.config.cache_ttl,
            )

            # Record cache metric
            if self.config.enable_monitoring:
                cache_metric = CacheMetric(
                    operation="set",
                    namespace="tool_result",
                    key=f"{tool_name}:{hash(str(arguments))}",
                    operation_time=0.001,  # Approximate
                    cache_hit=False,
                    data_size=len(str(result)),
                )
                performance_monitor.record_cache_operation(cache_metric)

            return success
        except Exception as e:
            logger.error(f"Failed to cache tool result: {e}")
            return False

    # Async Processing Integration Methods

    async def submit_message_processing_task(
        self,
        message: str,
        user_id: str,
        conversation_id: str,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Submit message processing task."""
        if not self.config.enable_async_processing:
            raise ConfigurationError("Async processing is disabled")

        task_request = TaskRequest(
            task_type=TaskType.MESSAGE_PROCESSING,
            priority=priority,
            payload={
                "message": message,
                "user_id": user_id,
                "conversation_id": conversation_id,
            },
            user_id=user_id,
            conversation_id=conversation_id,
        )

        return await async_processor.submit_task(task_request)

    async def submit_ai_response_task(
        self,
        message: str,
        user_id: str,
        conversation_id: str,
        model: str = "gpt-4",
        priority: TaskPriority = TaskPriority.HIGH,
    ) -> str:
        """Submit AI response generation task."""
        if not self.config.enable_async_processing:
            raise ConfigurationError("Async processing is disabled")

        task_request = TaskRequest(
            task_type=TaskType.AI_RESPONSE_GENERATION,
            priority=priority,
            payload={
                "message": message,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "model": model,
            },
            user_id=user_id,
            conversation_id=conversation_id,
        )

        return await async_processor.submit_task(task_request)

    async def submit_tool_execution_task(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_id: str,
        conversation_id: str,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Submit tool execution task."""
        if not self.config.enable_async_processing:
            raise ConfigurationError("Async processing is disabled")

        task_request = TaskRequest(
            task_type=TaskType.TOOL_EXECUTION,
            priority=priority,
            payload={
                "tool_name": tool_name,
                "arguments": arguments,
                "user_id": user_id,
                "conversation_id": conversation_id,
            },
            user_id=user_id,
            conversation_id=conversation_id,
        )

        return await async_processor.submit_task(task_request)

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get task status."""
        if not self.config.enable_async_processing:
            return None

        task_info = async_processor.get_task_status(task_id)
        if task_info:
            return task_info.dict()
        return None

    # Monitoring Integration Methods

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
        """Record API request performance."""
        if not self.config.enable_monitoring:
            return

        try:
            api_metric = APIMetric(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                user_id=user_id,
                request_size=request_size,
                response_size=response_size,
            )
            performance_monitor.record_api_request(api_metric)
        except Exception as e:
            logger.error(f"Failed to record API request: {e}")

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
        """Record database query performance."""
        if not self.config.enable_monitoring:
            return

        try:
            query_metric = DatabaseQueryMetric(
                query_type=query_type,
                table_name=table_name,
                execution_time=execution_time,
                rows_affected=rows_affected,
                query_size=query_size,
                connection_pool_size=connection_pool_size,
                error=error,
            )
            performance_monitor.record_database_query(query_metric)
        except Exception as e:
            logger.error(f"Failed to record database query: {e}")

    def record_performance_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        unit: str = "",
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record custom performance metric."""
        if not self.config.enable_monitoring:
            return

        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                metric_type=metric_type,
                value=value,
                unit=unit,
                tags=tags or {},
            )
            performance_monitor.record_metric(metric)
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")

    # Analytics and Reporting Methods

    def get_performance_summary(
        self,
        time_range: timedelta = timedelta(hours=1),
    ) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.config.enable_monitoring:
            return {"error": "Performance monitoring is disabled"}

        try:
            summary = performance_monitor.get_metrics_summary(time_range)

            # Add service status
            summary["services"] = self.services_status

            # Add cache statistics
            if self.config.enable_caching:
                cache_stats = cache_service.get_stats()
                summary["cache"] = cache_stats

            # Add async processor statistics
            if self.config.enable_async_processing:
                async_stats = async_processor.get_stats()
                summary["async_processor"] = async_stats

            # Add database optimization suggestions
            db_analysis = database_optimizer.analyze_query_performance()
            summary["database_optimization"] = db_analysis

            return summary
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}

    def get_slow_queries(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get slowest database queries."""
        if not self.config.enable_monitoring:
            return []

        try:
            slow_queries = performance_monitor.get_slow_queries(limit)
            return [query.dict() for query in slow_queries]
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []

    def get_slow_endpoints(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get slowest API endpoints."""
        if not self.config.enable_monitoring:
            return []

        try:
            slow_endpoints = performance_monitor.get_slow_endpoints(limit)
            return [endpoint.dict() for endpoint in slow_endpoints]
        except Exception as e:
            logger.error(f"Failed to get slow endpoints: {e}")
            return []

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get active performance alerts."""
        if not self.config.enable_monitoring:
            return []

        try:
            active_alerts = performance_monitor.get_active_alerts()
            return [alert.dict() for alert in active_alerts]
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve performance alert."""
        if not self.config.enable_monitoring:
            return False

        try:
            return performance_monitor.resolve_alert(alert_id)
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False

    # Health Check Methods

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of all performance services."""
        health_status = {
            "overall": "healthy",
            "services": {},
            "uptime": (datetime.now(UTC) - self.startup_time).total_seconds(),
            "initialized": self.initialized,
        }

        # Check cache service
        if self.config.enable_caching:
            try:
                cache_stats = cache_service.get_stats()
                health_status["services"]["cache"] = {
                    "status": (
                        "healthy" if self.services_status["cache"] else "unhealthy"
                    ),
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "total_requests": cache_stats.get("total_requests", 0),
                }
            except Exception as e:
                health_status["services"]["cache"] = {
                    "status": "error",
                    "error": str(e),
                }

        # Check async processor
        if self.config.enable_async_processing:
            try:
                async_stats = async_processor.get_stats()
                health_status["services"]["async_processor"] = {
                    "status": (
                        "healthy"
                        if self.services_status["async_processor"]
                        else "unhealthy"
                    ),
                    "active_workers": async_stats.get("active_workers", 0),
                    "total_workers": async_stats.get("total_workers", 0),
                    "tasks_processed": async_stats.get("tasks_processed", 0),
                }
            except Exception as e:
                health_status["services"]["async_processor"] = {
                    "status": "error",
                    "error": str(e),
                }

        # Check monitoring
        if self.config.enable_monitoring:
            try:
                monitor_stats = performance_monitor.get_stats()
                health_status["services"]["monitoring"] = {
                    "status": (
                        "healthy" if self.services_status["monitoring"] else "unhealthy"
                    ),
                    "total_metrics": monitor_stats.get("total_metrics", 0),
                    "active_alerts": monitor_stats.get("active_alerts", 0),
                }
            except Exception as e:
                health_status["services"]["monitoring"] = {
                    "status": "error",
                    "error": str(e),
                }

        # Determine overall status
        if not self.initialized:
            health_status["overall"] = "uninitialized"
        elif any(
            service.get("status") == "error"
            for service in health_status["services"].values()
        ):
            health_status["overall"] = "unhealthy"
        elif any(
            service.get("status") == "unhealthy"
            for service in health_status["services"].values()
        ):
            health_status["overall"] = "degraded"

        return health_status


# Global performance integration instance
performance_config = PerformanceConfig(
    enable_caching=True,
    enable_async_processing=True,
    enable_monitoring=True,
    cache_ttl=3600,
    max_async_workers=10,
    monitoring_interval=60,
)

performance_integration = PerformanceIntegration(performance_config)
