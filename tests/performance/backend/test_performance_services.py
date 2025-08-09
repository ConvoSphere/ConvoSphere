"""
Tests for the new modular performance monitoring system.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.app.monitoring import (
    Metric,
    MetricType,
    Alert,
    AlertSeverity,
    AlertChannel,
    MetricsCollector,
    AlertManager,
    SystemMonitor,
    DatabaseMonitor,
    get_performance_monitor,
)
from backend.app.services.performance_integration import (
    PerformanceConfig,
    PerformanceIntegration,
)


class TestMetricsCollector:
    """Test metrics collector functionality."""

    def setup_method(self):
        """Setup test method."""
        self.collector = MetricsCollector(max_metrics=100, retention_hours=1)

    def test_record_metric(self):
        """Test recording metrics."""
        # Record a gauge metric
        self.collector.record_metric(
            name="cpu_usage",
            value=75.5,
            metric_type=MetricType.GAUGE,
            tags={"component": "system"},
        )

        # Record a counter metric
        self.collector.record_metric(
            name="requests_total",
            value=1.0,
            metric_type=MetricType.COUNTER,
            tags={"endpoint": "/api/test"},
        )

        # Check metrics were recorded
        metrics = self.collector.get_metrics()
        assert len(metrics) == 2  # noqa: S101

        # Check metric values
        cpu_metric = next(m for m in metrics if m.name == "cpu_usage")
        assert cpu_metric.value == 75.5  # noqa: S101
        assert cpu_metric.metric_type == MetricType.GAUGE  # noqa: S101
        assert cpu_metric.tags["component"] == "system"  # noqa: S101

    def test_increment_counter(self):
        """Test counter increment."""
        self.collector.increment_counter("test_counter", value=5)
        self.collector.increment_counter("test_counter", value=3)

        metrics = self.collector.get_metrics(name="test_counter")
        assert len(metrics) == 2  # noqa: S101
        assert sum(m.value for m in metrics) == 8  # noqa: S101

    def test_set_gauge(self):
        """Test gauge setting."""
        self.collector.set_gauge("test_gauge", value=42.0)
        self.collector.set_gauge("test_gauge", value=84.0)

        metrics = self.collector.get_metrics(name="test_gauge")
        assert len(metrics) == 2  # noqa: S101
        assert metrics[-1].value == 84.0  # noqa: S101

    def test_record_timer(self):
        """Test timer recording."""
        self.collector.record_timer("test_timer", duration=1.5)
        self.collector.record_timer("test_timer", duration=2.5)

        metrics = self.collector.get_metrics(name="test_timer")
        assert len(metrics) == 2  # noqa: S101
        assert metrics[0].value == 1.5  # noqa: S101
        assert metrics[1].value == 2.5  # noqa: S101

    def test_get_statistics(self):
        """Test statistics calculation."""
        # Add some test data
        for i in range(10):
            self.collector.record_metric(
                name="test_stats",
                value=float(i),
                metric_type=MetricType.GAUGE,
            )

        stats = self.collector.get_statistics("test_stats", MetricType.GAUGE)
        assert stats["count"] == 10  # noqa: S101
        assert stats["min"] == 0.0  # noqa: S101
        assert stats["max"] == 9.0  # noqa: S101
        assert stats["mean"] == 4.5  # noqa: S101

    def test_export_metrics(self):
        """Test metrics export."""
        # Add test metric
        self.collector.record_metric(
            name="test_export",
            value=42.0,
            metric_type=MetricType.GAUGE,
            tags={"test": "true"},
        )

        # Export as JSON
        json_export = self.collector.export_metrics("json")
        assert "test_export" in json_export  # noqa: S101
        assert "42.0" in json_export  # noqa: S101

        # Export as Prometheus
        prometheus_export = self.collector.export_metrics("prometheus")
        assert "test_export" in prometheus_export  # noqa: S101


class TestAlertManager:
    """Test alert manager functionality."""

    def setup_method(self):
        """Setup test method."""
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector()

    def test_add_alert_rule(self):
        """Test adding alert rules."""
        self.alert_manager.add_alert_rule(
            name="high_cpu",
            metric_name="cpu_percent",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            condition="gt",
            tags={"component": "system"},
        )

        assert "high_cpu" in self.alert_manager.alert_rules  # noqa: S101
        rule = self.alert_manager.alert_rules["high_cpu"]
        assert rule["threshold"] == 80.0  # noqa: S101
        assert rule["severity"] == AlertSeverity.WARNING  # noqa: S101

    def test_check_alerts(self):
        """Test alert checking."""
        # Add alert rule
        self.alert_manager.add_alert_rule(
            name="high_cpu",
            metric_name="cpu_percent",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            condition="gt",
        )

        # Add metric that should trigger alert
        self.metrics_collector.record_metric(
            name="cpu_percent",
            value=85.0,
            metric_type=MetricType.GAUGE,
        )

        # Check alerts
        alerts = self.alert_manager.check_alerts(self.metrics_collector)
        assert len(alerts) == 1  # noqa: S101
        assert alerts[0].name == "high_cpu"  # noqa: S101
        assert alerts[0].current_value == 85.0  # noqa: S101

    def test_alert_suppression(self):
        """Test alert suppression."""
        # Add alert rule with suppression
        self.alert_manager.add_alert_rule(
            name="high_cpu",
            metric_name="cpu_percent",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            suppression_window=300,  # 5 minutes
        )

        # Add metric that should trigger alert
        self.metrics_collector.record_metric(
            name="cpu_percent",
            value=85.0,
            metric_type=MetricType.GAUGE,
        )

        # Check alerts - should trigger first time
        alerts = self.alert_manager.check_alerts(self.metrics_collector)
        assert len(alerts) == 1  # noqa: S101

        # Check alerts again - should be suppressed
        alerts = self.alert_manager.check_alerts(self.metrics_collector)
        assert len(alerts) == 0  # noqa: S101


class TestSystemMonitor:
    """Test system monitor functionality."""

    def setup_method(self):
        """Setup test method."""
        self.system_monitor = SystemMonitor()

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection."""
        # Mock system calls
        mock_cpu.return_value = 50.0
        mock_memory.return_value.percent = 60.0
        mock_memory.return_value.available = 4 * 1024**3  # 4GB
        mock_memory.return_value.used = 6 * 1024**3  # 6GB
        mock_memory.return_value.total = 10 * 1024**3  # 10GB
        mock_disk.return_value.percent = 70.0

        metrics = self.system_monitor.get_system_metrics()

        assert metrics["cpu_percent"] == 50.0  # noqa: S101
        assert metrics["memory_percent"] == 60.0  # noqa: S101
        assert metrics["disk_percent"] == 70.0  # noqa: S101
        assert metrics["memory_available_gb"] == 4.0  # noqa: S101
        assert metrics["memory_used_gb"] == 6.0  # noqa: S101
        assert metrics["memory_total_gb"] == 10.0  # noqa: S101


class TestPerformanceIntegration:
    """Test performance integration functionality."""

    def setup_method(self):
        """Setup test method."""
        self.config = PerformanceConfig(
            enable_caching=True,
            enable_monitoring=True,
            cache_ttl=3600,
        )
        self.integration = PerformanceIntegration(self.config)

    @patch('backend.app.services.cache_service.cache_service')
    @patch('backend.app.monitoring.get_performance_monitor')
    async def test_initialize(self, mock_get_monitor, mock_cache_service):
        """Test integration initialization."""
        # Mock dependencies
        mock_monitor = Mock()
        mock_get_monitor.return_value = mock_monitor
        mock_cache_service.initialize.return_value = None

        await self.integration.initialize()

        assert self.integration.initialized  # noqa: S101
        assert self.integration.services_status["cache"]  # noqa: S101
        assert self.integration.services_status["monitoring"]  # noqa: S101

    def test_record_api_request(self):
        """Test API request recording."""
        # Mock monitoring
        self.integration.services_status["monitoring"] = True
        self.integration.performance_monitor = Mock()
        self.integration.performance_monitor.metrics_collector = Mock()

        self.integration.record_api_request(
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time=0.5,
            user_id="user123",
        )

        # Check that metrics were recorded
        assert self.integration.performance_monitor.metrics_collector.record_metric.called  # noqa: S101

    def test_record_database_query(self):
        """Test database query recording."""
        # Mock monitoring
        self.integration.services_status["monitoring"] = True
        self.integration.performance_monitor = Mock()
        self.integration.performance_monitor.metrics_collector = Mock()

        self.integration.record_database_query(
            query_type="select",
            table_name="users",
            execution_time=0.1,
            rows_affected=100,
        )

        # Check that metrics were recorded
        assert self.integration.performance_monitor.metrics_collector.record_metric.called  # noqa: S101

    def test_get_health_status(self):
        """Test health status."""
        status = self.integration.get_health_status()

        assert "initialized" in status  # noqa: S101
        assert "startup_time" in status  # noqa: S101
        assert "services_status" in status  # noqa: S101
        assert "config" in status  # noqa: S101


class TestPerformanceMonitor:
    """Test main performance monitor functionality."""

    @patch('backend.app.core.database.get_db')
    def test_get_performance_monitor(self, mock_get_db):
        """Test getting performance monitor instance."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        monitor = get_performance_monitor(mock_db)

        assert monitor is not None  # noqa: S101
        assert hasattr(monitor, 'metrics_collector')  # noqa: S101
        assert hasattr(monitor, 'alert_manager')  # noqa: S101
        assert hasattr(monitor, 'system_monitor')  # noqa: S101
        assert hasattr(monitor, 'database_monitor')  # noqa: S101

    @patch('backend.app.core.database.get_db')
    async def test_monitoring_lifecycle(self, mock_get_db):
        """Test monitoring start/stop lifecycle."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        monitor = get_performance_monitor(mock_db)

        # Start monitoring
        await monitor.start_monitoring()
        assert monitor.is_monitoring  # noqa: S101

        # Stop monitoring
        await monitor.stop_monitoring()
        assert not monitor.is_monitoring  # noqa: S101

    @patch('backend.app.core.database.get_db')
    def test_get_performance_snapshot(self, mock_get_db):
        """Test performance snapshot generation."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        monitor = get_performance_monitor(mock_db)

        # Mock system monitor
        monitor.system_monitor.get_system_metrics = Mock(return_value={
            "cpu_percent": 50.0,
            "memory_percent": 60.0,
            "disk_percent": 70.0,
        })

        # Mock database monitor
        monitor.database_monitor.get_database_metrics = Mock(return_value={
            "connection": {"checked_out": 5},
            "queries": {"slow_queries": 2},
        })

        snapshot = monitor.get_performance_snapshot()

        assert snapshot.cpu_percent == 50.0  # noqa: S101
        assert snapshot.memory_percent == 60.0  # noqa: S101
        assert snapshot.disk_usage_percent == 70.0  # noqa: S101
        assert snapshot.active_connections == 5  # noqa: S101
        assert snapshot.slow_queries == 2  # noqa: S101
