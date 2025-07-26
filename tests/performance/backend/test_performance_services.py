"""
Tests for Phase 3 Performance Services.

This module tests the caching, async processing, and monitoring services
implemented in Phase 3 of the Chat & Agent Logic Improvements.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from backend.app.services.async_processor import (
    AsyncProcessor,
    TaskInfo,
    TaskPriority,
    TaskRequest,
    TaskResult,
    TaskStatus,
    TaskType,
)
from backend.app.services.cache_service import (
    CacheConfig,
    CacheEntry,
    CacheKey,
)
from backend.app.services.performance_integration import (
    PerformanceConfig,
    PerformanceIntegration,
)
from backend.app.services.performance_monitor import (
    APIMetric,
    CacheMetric,
    DatabaseOptimizer,
    DatabaseQueryMetric,
    PerformanceAlert,
    PerformanceMetric,
    PerformanceMonitor,
)
from pydantic import ValidationError


class TestCacheService:
    """Test cache service functionality."""

    def test_cache_config_validation(self):
        """Test cache configuration validation."""
        # Valid config
        config = CacheConfig(
            redis_url="redis://localhost:6379",
            default_ttl=3600,
            max_connections=10,
        )
        assert config.redis_url == "redis://localhost:6379"  # noqa: S101
        assert config.default_ttl == 3600  # noqa: S101

        # Invalid Redis URL
        with pytest.raises(ValidationError) as exc_info:
            CacheConfig(redis_url="invalid-url")
        assert "Redis URL must start with redis:// or rediss://" in str(
            exc_info.value
        )  # noqa: S101

        # Invalid TTL
        with pytest.raises(ValidationError) as exc_info:
            CacheConfig(redis_url="redis://localhost:6379", default_ttl=30)
        assert "Input should be greater than or equal to 60" in str(
            exc_info.value
        )  # noqa: S101

    def test_cache_key_creation(self):
        """Test cache key creation and validation."""
        # Valid cache key
        cache_key = CacheKey(
            namespace="test",
            key="user:123",
            version="v1",
        )
        assert cache_key.to_string() == "test:v1:user:123"  # noqa: S101

        # Create from string
        parsed_key = CacheKey.from_string("test:v1:user:123")
        assert parsed_key.namespace == "test"  # noqa: S101
        assert parsed_key.key == "user:123"  # noqa: S101
        assert parsed_key.version == "v1"  # noqa: S101

        # Invalid key format
        with pytest.raises(ValueError, match="Invalid cache key format") as exc_info:
            CacheKey.from_string("invalid:key")
        assert "Invalid cache key format" in str(exc_info.value)  # noqa: S101

    def test_cache_entry_validation(self):
        """Test cache entry validation."""
        # Valid entry
        entry = CacheEntry(
            data={"test": "data"},
            created_at=datetime.now(tz=UTC),
            expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
        )
        assert entry.data == {"test": "data"}  # noqa: S101
        assert not entry.is_expired()  # noqa: S101

        # Expired entry
        expired_entry = CacheEntry(
            data={"test": "data"},
            created_at=datetime.now(tz=UTC) - timedelta(hours=2),
            expires_at=datetime.now(tz=UTC) - timedelta(hours=1),
        )
        assert expired_entry.is_expired()  # noqa: S101

        # Access tracking
        entry.increment_access()
        assert entry.access_count == 1  # noqa: S101
        assert entry.last_accessed > entry.created_at  # noqa: S101


class TestAsyncProcessor:
    """Test async processing functionality."""

    def test_task_request_validation(self):
        """Test task request validation."""
        # Valid task request
        task_request = TaskRequest(
            task_type=TaskType.MESSAGE_PROCESSING,
            priority=TaskPriority.HIGH,
            payload={"message": "test"},
            user_id="user123",
            conversation_id="conv123",
        )
        assert task_request.task_type == TaskType.MESSAGE_PROCESSING  # noqa: S101
        assert task_request.priority == TaskPriority.HIGH  # noqa: S101

        # Invalid task ID
        with pytest.raises(ValidationError) as exc_info:
            TaskRequest(
                task_id="",
                task_type=TaskType.MESSAGE_PROCESSING,
                payload={"message": "test"},
            )
        assert "Task ID cannot be empty" in str(exc_info.value)  # noqa: S101

        # Invalid payload
        with pytest.raises(ValidationError) as exc_info:
            TaskRequest(
                task_type=TaskType.MESSAGE_PROCESSING,
                payload="invalid",
            )
        assert "Payload must be a dictionary" in str(exc_info.value)  # noqa: S101

    def test_task_result_validation(self):
        """Test task result validation."""
        # Valid task result
        task_result = TaskResult(
            task_id="task123",
            status=TaskStatus.COMPLETED,
            result={"success": True},
            start_time=datetime.now(tz=UTC),
            end_time=datetime.now(tz=UTC),
            execution_time=1.5,
        )
        assert task_result.task_id == "task123"  # noqa: S101
        assert task_result.status == TaskStatus.COMPLETED  # noqa: S101
        assert task_result.execution_time == 1.5  # noqa: S101

        # Invalid execution time
        with pytest.raises(ValidationError) as exc_info:
            TaskResult(
                task_id="task123",
                status=TaskStatus.COMPLETED,
                execution_time=-1.0,
            )
        assert "Input should be greater than or equal to 0" in str(
            exc_info.value
        )  # noqa: S101

    def test_task_info_validation(self):
        """Test task info validation."""
        # Valid task info
        task_info = TaskInfo(
            task_id="task123",
            task_type=TaskType.AI_RESPONSE_GENERATION,
            priority=TaskPriority.URGENT,
            status=TaskStatus.RUNNING,
            created_at=datetime.now(tz=UTC),
            user_id="user123",
            conversation_id="conv123",
        )
        assert task_info.task_id == "task123"  # noqa: S101
        assert task_info.priority == TaskPriority.URGENT  # noqa: S101
        assert task_info.status == TaskStatus.RUNNING  # noqa: S101


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""

    def test_performance_metric_validation(self):
        """Test performance metric validation."""
        # Valid metric
        metric = PerformanceMetric(
            metric_name="api_response_time",
            metric_type="timer",
            value=1.5,
            unit="seconds",
            tags={"endpoint": "/api/chat"},
        )
        assert metric.metric_name == "api_response_time"  # noqa: S101
        assert metric.value == 1.5  # noqa: S101
        assert metric.unit == "seconds"  # noqa: S101

        # Invalid metric name
        with pytest.raises(ValidationError) as exc_info:
            PerformanceMetric(
                metric_name="",
                metric_type="timer",
                value=1.5,
            )
        assert "Metric name cannot be empty" in str(exc_info.value)  # noqa: S101

        # Invalid metric type
        with pytest.raises(ValidationError) as exc_info:
            PerformanceMetric(
                metric_name="test",
                metric_type="invalid",
                value=1.5,
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101

        # Invalid value (NaN)
        with pytest.raises(ValidationError) as exc_info:
            PerformanceMetric(
                metric_name="test",
                metric_type="timer",
                value=float("nan"),
            )
        assert "Metric value must be a valid number" in str(
            exc_info.value
        )  # noqa: S101

    def test_database_query_metric_validation(self):
        """Test database query metric validation."""
        # Valid query metric
        query_metric = DatabaseQueryMetric(
            query_type="select",
            table_name="conversations",
            execution_time=0.5,
            rows_affected=100,
            query_size=1024,
            connection_pool_size=10,
        )
        assert query_metric.query_type == "select"  # noqa: S101
        assert query_metric.table_name == "conversations"  # noqa: S101
        assert query_metric.execution_time == 0.5  # noqa: S101

        # Invalid query type
        with pytest.raises(ValidationError) as exc_info:
            DatabaseQueryMetric(
                query_type="invalid",
                table_name="conversations",
                execution_time=0.5,
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101

        # Invalid execution time
        with pytest.raises(ValidationError) as exc_info:
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=-0.1,
            )
        assert "Input should be greater than or equal to 0" in str(
            exc_info.value
        )  # noqa: S101

    def test_api_metric_validation(self):
        """Test API metric validation."""
        # Valid API metric
        api_metric = APIMetric(
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            response_time=0.8,
            user_id="user123",
            request_size=1024,
            response_size=2048,
        )
        assert api_metric.endpoint == "/api/chat"  # noqa: S101
        assert api_metric.method == "POST"  # noqa: S101
        assert api_metric.status_code == 200  # noqa: S101
        assert api_metric.response_time == 0.8  # noqa: S101

        # Invalid method
        with pytest.raises(ValidationError) as exc_info:
            APIMetric(
                endpoint="/api/chat",
                method="INVALID",
                status_code=200,
                response_time=0.8,
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101

        # Invalid status code
        with pytest.raises(ValidationError) as exc_info:
            APIMetric(
                endpoint="/api/chat",
                method="POST",
                status_code=999,
                response_time=0.8,
            )
        assert "Input should be less than or equal to 599" in str(
            exc_info.value
        )  # noqa: S101

    def test_cache_metric_validation(self):
        """Test cache metric validation."""
        # Valid cache metric
        cache_metric = CacheMetric(
            operation="get",
            namespace="conversation",
            key="conv123:data",
            operation_time=0.001,
            cache_hit=True,
            data_size=1024,
        )
        assert cache_metric.operation == "get"  # noqa: S101
        assert cache_metric.namespace == "conversation"  # noqa: S101
        assert cache_metric.cache_hit is True  # noqa: S101

        # Invalid operation
        with pytest.raises(ValidationError) as exc_info:
            CacheMetric(
                operation="invalid",
                namespace="conversation",
                key="conv123:data",
                operation_time=0.001,
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101

    def test_performance_alert_validation(self):
        """Test performance alert validation."""
        # Valid alert
        alert = PerformanceAlert(
            alert_type="threshold",
            metric_name="api_response_time",
            threshold=1.0,
            current_value=1.5,
            severity="high",
            created_at=datetime.now(tz=UTC),
            message="API response time exceeded threshold",
        )
        assert alert.alert_type == "threshold"  # noqa: S101
        assert alert.metric_name == "api_response_time"  # noqa: S101
        assert alert.threshold == 1.0  # noqa: S101
        assert alert.current_value == 1.5  # noqa: S101
        assert alert.severity == "high"  # noqa: S101

        # Invalid alert type
        with pytest.raises(ValidationError) as exc_info:
            PerformanceAlert(
                alert_type="invalid",
                metric_name="api_response_time",
                threshold=1.0,
                current_value=1.5,
                severity="high",
                message="Test alert",
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101

        # Invalid severity
        with pytest.raises(ValidationError) as exc_info:
            PerformanceAlert(
                alert_type="threshold",
                metric_name="api_response_time",
                threshold=1.0,
                current_value=1.5,
                severity="invalid",
                message="Test alert",
            )
        assert "String should match pattern" in str(exc_info.value)  # noqa: S101


class TestPerformanceIntegration:
    """Test performance integration service."""

    def test_performance_config_validation(self):
        """Test performance configuration validation."""
        # Valid config
        config = PerformanceConfig(
            enable_caching=True,
            enable_async_processing=True,
            enable_monitoring=True,
            cache_ttl=3600,
            max_async_workers=10,
            monitoring_interval=60,
        )
        assert config.enable_caching is True  # noqa: S101
        assert config.cache_ttl == 3600  # noqa: S101
        assert config.max_async_workers == 10  # noqa: S101

        # Invalid cache TTL
        with pytest.raises(ValidationError) as exc_info:
            PerformanceConfig(
                enable_caching=True,
                cache_ttl=30,  # Too low
            )
        assert "Input should be greater than or equal to 60" in str(
            exc_info.value
        )  # noqa: S101

        # Invalid max workers
        with pytest.raises(ValidationError) as exc_info:
            PerformanceConfig(
                enable_async_processing=True,
                max_async_workers=100,  # Too high
            )
        assert "Input should be less than or equal to 50" in str(
            exc_info.value
        )  # noqa: S101


class TestPerformanceMonitorFunctionality:
    """Test performance monitor functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.monitor = PerformanceMonitor()

    def test_record_metric(self):
        """Test recording performance metrics."""
        metric = PerformanceMetric(
            metric_name="test_metric",
            metric_type="gauge",
            value=42.0,
        )

        self.monitor.record_metric(metric)
        assert self.monitor.stats["total_metrics"] == 1  # noqa: S101

        # Test invalid metric
        with pytest.raises(
            ValueError,
            match=".*",
        ):  # match beliebig, da keine spezifische Fehlermeldung
            self.monitor.record_metric("invalid")

    def test_record_database_query(self):
        """Test recording database query metrics."""
        query_metric = DatabaseQueryMetric(
            query_type="select",
            table_name="conversations",
            execution_time=0.5,
        )

        self.monitor.record_database_query(query_metric)
        assert len(self.monitor.database_metrics) == 1  # noqa: S101

        # Test slow query alert
        slow_query = DatabaseQueryMetric(
            query_type="select",
            table_name="conversations",
            execution_time=1.0,  # Above threshold
        )

        self.monitor.record_database_query(slow_query)
        assert len(self.monitor.alerts) > 0  # noqa: S101

    def test_record_api_request(self):
        """Test recording API request metrics."""
        api_metric = APIMetric(
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            response_time=0.8,
        )

        self.monitor.record_api_request(api_metric)
        assert len(self.monitor.api_metrics) == 1  # noqa: S101

        # Test slow response alert
        slow_response = APIMetric(
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            response_time=2.0,  # Above threshold
        )

        self.monitor.record_api_request(slow_response)
        assert len(self.monitor.alerts) > 0  # noqa: S101

        # Test error alert
        error_response = APIMetric(
            endpoint="/api/chat",
            method="POST",
            status_code=500,
            response_time=0.1,
        )

        self.monitor.record_api_request(error_response)
        assert len(self.monitor.alerts) > 0  # noqa: S101

    def test_record_cache_operation(self):
        """Test recording cache operation metrics."""
        cache_metric = CacheMetric(
            operation="get",
            namespace="conversation",
            key="conv123:data",
            operation_time=0.001,
            cache_hit=True,
        )

        self.monitor.record_cache_operation(cache_metric)
        assert len(self.monitor.cache_metrics) == 1  # noqa: S101

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        # Add some test metrics
        self.monitor.record_api_request(
            APIMetric(
                endpoint="/api/chat",
                method="POST",
                status_code=200,
                response_time=0.5,
            ),
        )

        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=0.3,
            ),
        )

        summary = self.monitor.get_metrics_summary()
        assert "api_requests" in summary  # noqa: S101
        assert "database_queries" in summary  # noqa: S101
        assert summary["api_requests"]["total"] == 1  # noqa: S101
        assert summary["database_queries"]["total"] == 1  # noqa: S101

    def test_get_slow_queries(self):
        """Test getting slow queries."""
        # Add slow queries
        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=1.0,
            ),
        )

        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="messages",
                execution_time=2.0,
            ),
        )

        slow_queries = self.monitor.get_slow_queries(limit=5)
        assert len(slow_queries) == 2  # noqa: S101
        assert slow_queries[0].execution_time == 2.0  # Slowest first  # noqa: S101

    def test_get_slow_endpoints(self):
        """Test getting slow endpoints."""
        # Add slow endpoints
        self.monitor.record_api_request(
            APIMetric(
                endpoint="/api/chat",
                method="POST",
                status_code=200,
                response_time=1.0,
            ),
        )

        self.monitor.record_api_request(
            APIMetric(
                endpoint="/api/users",
                method="GET",
                status_code=200,
                response_time=2.0,
            ),
        )

        slow_endpoints = self.monitor.get_slow_endpoints(limit=5)
        assert len(slow_endpoints) == 2  # noqa: S101
        assert slow_endpoints[0].response_time == 2.0  # Slowest first  # noqa: S101

    def test_resolve_alert(self):
        """Test resolving alerts."""
        # Create an alert
        alert = PerformanceAlert(
            alert_type="threshold",
            metric_name="test_metric",
            threshold=1.0,
            current_value=1.5,
            severity="high",
            created_at=datetime.now(tz=UTC),
            message="Test alert",
        )

        self.monitor.alerts.append(alert)
        initial_active = self.monitor.stats["active_alerts"]

        # Resolve the alert
        success = self.monitor.resolve_alert(alert.alert_id)
        assert success is True  # noqa: S101
        assert alert.resolved is True  # noqa: S101
        assert self.monitor.stats["active_alerts"] == initial_active - 1  # noqa: S101

        # Try to resolve non-existent alert
        success = self.monitor.resolve_alert("non-existent")
        assert success is False  # noqa: S101


class TestDatabaseOptimizer:
    """Test database optimizer functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.monitor = PerformanceMonitor()
        self.optimizer = DatabaseOptimizer(self.monitor)

    def test_analyze_query_performance(self):
        """Test query performance analysis."""
        # Add some test queries
        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=0.8,  # Slow query
            ),
        )

        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=0.3,
            ),
        )

        analysis = self.optimizer.analyze_query_performance()
        assert "total_queries" in analysis  # noqa: S101
        assert "slow_queries" in analysis  # noqa: S101
        assert "optimization_suggestions" in analysis  # noqa: S101
        assert analysis["total_queries"] == 2  # noqa: S101
        assert len(analysis["slow_queries"]) == 1  # noqa: S101

    def test_get_connection_pool_stats(self):
        """Test connection pool statistics."""
        # Add queries with pool size info
        self.monitor.record_database_query(
            DatabaseQueryMetric(
                query_type="select",
                table_name="conversations",
                execution_time=0.3,
                connection_pool_size=10,
            ),
        )

        stats = self.optimizer.get_connection_pool_stats()
        assert "average_pool_size" in stats  # noqa: S101
        assert "total_queries" in stats  # noqa: S101
        assert "avg_query_time" in stats  # noqa: S101
        assert stats["average_pool_size"] == 10.0  # noqa: S101


class TestAsyncProcessorFunctionality:
    """Test async processor functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.processor = AsyncProcessor(max_workers=2, max_queue_size=10)

    async def test_register_handler(self):
        """Test handler registration."""

        async def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        self.processor.register_handler(
            TaskType.MESSAGE_PROCESSING,
            test_handler,
            max_concurrent=1,
        )

        assert TaskType.MESSAGE_PROCESSING in self.processor.task_handlers  # noqa: S101

    async def test_submit_task(self):
        """Test task submission."""

        async def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        self.processor.register_handler(
            TaskType.MESSAGE_PROCESSING,
            test_handler,
        )

        await self.processor.start()

        task_request = TaskRequest(
            task_type=TaskType.MESSAGE_PROCESSING,
            payload={"message": "test"},
        )

        task_id = await self.processor.submit_task(task_request)
        assert task_id is not None  # noqa: S101

        # Wait for task to complete
        await asyncio.sleep(0.1)

        stats = self.processor.get_stats()
        assert stats["tasks_processed"] > 0  # noqa: S101

        await self.processor.stop()

    async def test_task_priority(self):
        """Test task priority handling."""

        async def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        self.processor.register_handler(
            TaskType.MESSAGE_PROCESSING,
            test_handler,
        )

        await self.processor.start()

        # Submit tasks with different priorities
        low_priority = TaskRequest(
            task_type=TaskType.MESSAGE_PROCESSING,
            priority=TaskPriority.LOW,
            payload={"message": "low"},
        )

        high_priority = TaskRequest(
            task_type=TaskType.MESSAGE_PROCESSING,
            priority=TaskPriority.HIGH,
            payload={"message": "high"},
        )

        await self.processor.submit_task(low_priority)
        await self.processor.submit_task(high_priority)

        # Wait for tasks to complete
        await asyncio.sleep(0.1)

        stats = self.processor.get_stats()
        assert stats["tasks_processed"] >= 2  # noqa: S101

        await self.processor.stop()

    async def test_queue_full(self):
        """Test queue full handling."""

        async def slow_handler() -> dict[str, Any]:
            await asyncio.sleep(0.1)  # Slow handler
            return {"result": "success"}

        self.processor.register_handler(
            TaskType.MESSAGE_PROCESSING,
            slow_handler,
        )

        await self.processor.start()

        # Fill the queue
        for i in range(15):  # More than max_queue_size
            task_request = TaskRequest(
                task_type=TaskType.MESSAGE_PROCESSING,
                payload={"message": f"test{i}"},
            )

            if i < 10:  # Should succeed
                task_id = await self.processor.submit_task(task_request)
                assert task_id is not None  # noqa: S101
            else:  # Should fail
                with pytest.raises(RuntimeError):
                    await self.processor.submit_task(task_request)

        await self.processor.stop()


# Integration tests
class TestPerformanceIntegrationFunctionality:
    """Test performance integration functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_caching=False,  # Disable for testing
            enable_async_processing=False,  # Disable for testing
            enable_monitoring=True,
        )
        self.integration = PerformanceIntegration(self.config)

    def test_record_api_request(self):
        """Test recording API requests through integration."""
        self.integration.record_api_request(
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            response_time=0.5,
            user_id="user123",
        )

        # Check that metric was recorded
        summary = self.integration.get_performance_summary()
        assert summary["api_requests"]["total"] == 1  # noqa: S101

    def test_record_database_query(self):
        """Test recording database queries through integration."""
        self.integration.record_database_query(
            query_type="select",
            table_name="conversations",
            execution_time=0.3,
            rows_affected=100,
        )

        # Check that metric was recorded
        summary = self.integration.get_performance_summary()
        assert summary["database_queries"]["total"] == 1  # noqa: S101

    def test_record_performance_metric(self):
        """Test recording custom performance metrics through integration."""
        self.integration.record_performance_metric(
            metric_name="custom_metric",
            value=42.0,
            metric_type="gauge",
            unit="count",
            tags={"service": "test"},
        )

        # Check that metric was recorded
        summary = self.integration.get_performance_summary()
        assert summary["total_metrics"] == 1  # noqa: S101

    def test_get_health_status(self):
        """Test health status reporting."""
        health_status = self.integration.get_health_status()

        assert "overall" in health_status  # noqa: S101
        assert "services" in health_status  # noqa: S101
        assert "uptime" in health_status  # noqa: S101
        assert "initialized" in health_status  # noqa: S101

        # Should be uninitialized since we didn't call initialize()
        assert health_status["overall"] == "uninitialized"  # noqa: S101
        assert health_status["initialized"] is False  # noqa: S101

    def test_get_slow_queries(self):
        """Test getting slow queries through integration."""
        # Add some slow queries
        self.integration.record_database_query(
            query_type="select",
            table_name="conversations",
            execution_time=1.0,
        )

        self.integration.record_database_query(
            query_type="select",
            table_name="messages",
            execution_time=2.0,
        )

        slow_queries = self.integration.get_slow_queries(limit=5)
        assert len(slow_queries) == 2  # noqa: S101
        assert slow_queries[0]["execution_time"] == 2.0  # Slowest first  # noqa: S101

    def test_get_slow_endpoints(self):
        """Test getting slow endpoints through integration."""
        # Add some slow endpoints
        self.integration.record_api_request(
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            response_time=1.0,
        )

        self.integration.record_api_request(
            endpoint="/api/users",
            method="GET",
            status_code=200,
            response_time=2.0,
        )

        slow_endpoints = self.integration.get_slow_endpoints(limit=5)
        assert len(slow_endpoints) == 2  # noqa: S101
        assert slow_endpoints[0]["response_time"] == 2.0  # Slowest first  # noqa: S101

    def test_get_active_alerts(self):
        """Test getting active alerts through integration."""
        # Add a slow query to trigger an alert
        self.integration.record_database_query(
            query_type="select",
            table_name="conversations",
            execution_time=1.0,  # Above threshold
        )

        active_alerts = self.integration.get_active_alerts()
        assert len(active_alerts) > 0  # noqa: S101
        assert active_alerts[0]["severity"] == "high"  # noqa: S101

    def test_resolve_alert(self):
        """Test resolving alerts through integration."""
        # Add a slow query to trigger an alert
        self.integration.record_database_query(
            query_type="select",
            table_name="conversations",
            execution_time=1.0,  # Above threshold
        )

        active_alerts = self.integration.get_active_alerts()
        assert len(active_alerts) > 0  # noqa: S101

        # Resolve the alert
        alert_id = active_alerts[0]["alert_id"]
        success = self.integration.resolve_alert(alert_id)
        assert success is True  # noqa: S101

        # Check that alert is resolved
        active_alerts_after = self.integration.get_active_alerts()
        assert len(active_alerts_after) < len(active_alerts)  # noqa: S101


if __name__ == "__main__":
    pytest.main([__file__])
