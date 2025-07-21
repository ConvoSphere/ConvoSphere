"""
Performance monitoring service.

This module provides comprehensive performance monitoring for the AI Assistant Platform,
including metrics collection, monitoring, and alerting capabilities.
"""

import json
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import psutil
from loguru import logger

from app.core.config import settings


class MetricType(Enum):
    """Metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert level enumeration."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data structure."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    name: str
    message: str
    level: AlertLevel
    timestamp: datetime
    metric_name: str
    threshold: float
    current_value: float
    resolved: bool = False
    resolved_at: datetime | None = None


@dataclass
class PerformanceSnapshot:
    """Performance snapshot data."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: dict[str, float]
    active_connections: int
    request_rate: float
    error_rate: float
    avg_response_time: float


class PerformanceMonitor:
    """Performance monitoring service."""

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: list[Alert] = []
        self.alert_handlers: list[Callable[[Alert], None]] = []

        # Monitoring configuration
        self.monitoring_enabled = settings.performance_monitoring_enabled
        self.monitoring_interval = settings.performance_monitoring_interval
        self.alert_thresholds = settings.performance_alert_thresholds

        # System metrics
        self.system_metrics = {}
        self.performance_snapshots: deque = deque(maxlen=100)

        # Service-specific metrics
        self.service_metrics = {
            "ai_service": defaultdict(lambda: deque(maxlen=100)),
            "knowledge_service": defaultdict(lambda: deque(maxlen=100)),
            "assistant_engine": defaultdict(lambda: deque(maxlen=100)),
            "websocket_service": defaultdict(lambda: deque(maxlen=100)),
        }

        # Request tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts: deque = deque(maxlen=1000)
        self.active_requests = 0

        # Monitoring thread
        self.monitoring_thread = None
        self.stop_monitoring = False

        if self.monitoring_enabled:
            self.start_monitoring()

    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return

        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True,
        )
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring_service(self):
        """Stop performance monitoring."""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while not self.stop_monitoring:
            try:
                self._collect_system_metrics()
                self._collect_service_metrics()
                self._check_alerts()
                self._cleanup_old_data()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying

    def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu_percent", cpu_percent, MetricType.GAUGE)

            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric(
                "system.memory_percent", memory.percent, MetricType.GAUGE,
            )
            self.record_metric(
                "system.memory_used_mb", memory.used / (1024 * 1024), MetricType.GAUGE,
            )

            # Disk usage
            disk = psutil.disk_usage("/")
            self.record_metric("system.disk_percent", disk.percent, MetricType.GAUGE)

            # Network I/O
            network = psutil.net_io_counters()
            self.record_metric(
                "system.network_bytes_sent", network.bytes_sent, MetricType.COUNTER,
            )
            self.record_metric(
                "system.network_bytes_recv", network.bytes_recv, MetricType.COUNTER,
            )

            # Create performance snapshot
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                },
                active_connections=self.active_requests,
                request_rate=self._calculate_request_rate(),
                error_rate=self._calculate_error_rate(),
                avg_response_time=self._calculate_avg_response_time(),
            )

            self.performance_snapshots.append(snapshot)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _collect_service_metrics(self):
        """Collect service-specific metrics."""
        # This would be populated by individual services
        # For now, we'll collect basic service health metrics

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        labels: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Record a metric."""
        if not self.monitoring_enabled:
            return

        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            labels=labels or {},
            metadata=metadata or {},
        )

        self.metrics[name].append(metric)

        # Check for alerts
        self._check_metric_alerts(metric)

    def record_service_metric(
        self,
        service_name: str,
        metric_name: str,
        value: float,
        metric_type: MetricType,
        labels: dict[str, str] | None = None,
    ):
        """Record a service-specific metric."""
        full_name = f"{service_name}.{metric_name}"
        self.record_metric(full_name, value, metric_type, labels)

        # Store in service-specific metrics
        if service_name in self.service_metrics:
            self.service_metrics[service_name][metric_name].append(
                {
                    "value": value,
                    "timestamp": datetime.now(),
                    "labels": labels or {},
                },
            )

    def record_request_time(self, duration: float, endpoint: str = "unknown"):
        """Record request processing time."""
        self.request_times.append(
            {
                "duration": duration,
                "timestamp": datetime.now(),
                "endpoint": endpoint,
            },
        )

        self.record_metric(
            "requests.duration",
            duration,
            MetricType.HISTOGRAM,
            labels={"endpoint": endpoint},
        )

    def record_error(self, error_type: str, service: str = "unknown"):
        """Record an error occurrence."""
        self.error_counts.append(
            {
                "error_type": error_type,
                "timestamp": datetime.now(),
                "service": service,
            },
        )

        self.record_metric(
            "errors.count",
            1,
            MetricType.COUNTER,
            labels={"error_type": error_type, "service": service},
        )

    def increment_active_requests(self):
        """Increment active request counter."""
        self.active_requests += 1
        self.record_metric("requests.active", self.active_requests, MetricType.GAUGE)

    def decrement_active_requests(self):
        """Decrement active request counter."""
        self.active_requests = max(0, self.active_requests - 1)
        self.record_metric("requests.active", self.active_requests, MetricType.GAUGE)

    def _check_metric_alerts(self, metric: Metric):
        """Check if a metric triggers an alert."""
        threshold_key = metric.name

        if threshold_key not in self.alert_thresholds:
            return

        threshold = self.alert_thresholds[threshold_key]
        current_value = metric.value

        # Check different threshold types
        if "max" in threshold and current_value > threshold["max"]:
            self._create_alert(
                name=f"{metric.name}_high",
                message=f"{metric.name} exceeded maximum threshold: {current_value} > {threshold['max']}",
                level=AlertLevel.WARNING
                if threshold.get("level") == "warning"
                else AlertLevel.ERROR,
                metric_name=metric.name,
                threshold=threshold["max"],
                current_value=current_value,
            )

        if "min" in threshold and current_value < threshold["min"]:
            self._create_alert(
                name=f"{metric.name}_low",
                message=f"{metric.name} below minimum threshold: {current_value} < {threshold['min']}",
                level=AlertLevel.WARNING
                if threshold.get("level") == "warning"
                else AlertLevel.ERROR,
                metric_name=metric.name,
                threshold=threshold["min"],
                current_value=current_value,
            )

    def _create_alert(
        self,
        name: str,
        message: str,
        level: AlertLevel,
        metric_name: str,
        threshold: float,
        current_value: float,
    ):
        """Create a new alert."""
        alert = Alert(
            id=f"alert_{len(self.alerts)}_{int(time.time())}",
            name=name,
            message=message,
            level=level,
            timestamp=datetime.now(),
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
        )

        self.alerts.append(alert)

        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

        logger.warning(f"Performance alert: {message}")

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler."""
        self.alert_handlers.append(handler)

    def _check_alerts(self):
        """Check for alert conditions."""
        # This is called periodically to check for sustained conditions

    def _cleanup_old_data(self):
        """Clean up old metrics and alerts."""
        # Remove alerts older than 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]

        # Clean up old metrics (keep last 1000 for each metric)
        for metric_name in list(self.metrics.keys()):
            if len(self.metrics[metric_name]) > 1000:
                # Keep only the most recent 1000 metrics
                recent_metrics = list(self.metrics[metric_name])[-1000:]
                self.metrics[metric_name] = deque(recent_metrics, maxlen=1000)

    def _calculate_request_rate(self) -> float:
        """Calculate requests per second."""
        if not self.request_times:
            return 0.0

        # Calculate rate over last minute
        cutoff_time = datetime.now() - timedelta(minutes=1)
        recent_requests = [
            req for req in self.request_times if req["timestamp"] > cutoff_time
        ]

        return len(recent_requests) / 60.0  # requests per second

    def _calculate_error_rate(self) -> float:
        """Calculate error rate."""
        if not self.error_counts:
            return 0.0

        # Calculate rate over last minute
        cutoff_time = datetime.now() - timedelta(minutes=1)
        recent_errors = [
            error for error in self.error_counts if error["timestamp"] > cutoff_time
        ]

        return len(recent_errors) / 60.0  # errors per second

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self.request_times:
            return 0.0

        # Calculate average over last minute
        cutoff_time = datetime.now() - timedelta(minutes=1)
        recent_requests = [
            req for req in self.request_times if req["timestamp"] > cutoff_time
        ]

        if not recent_requests:
            return 0.0

        total_time = sum(req["duration"] for req in recent_requests)
        return total_time / len(recent_requests)

    def get_metrics(
        self,
        metric_name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, list[Metric]]:
        """Get metrics for a specific time range."""
        if not start_time:
            start_time = datetime.now() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.now()

        result = {}

        if metric_name:
            if metric_name in self.metrics:
                filtered_metrics = [
                    metric
                    for metric in self.metrics[metric_name]
                    if start_time <= metric.timestamp <= end_time
                ]
                result[metric_name] = filtered_metrics
        else:
            for name, metrics in self.metrics.items():
                filtered_metrics = [
                    metric
                    for metric in metrics
                    if start_time <= metric.timestamp <= end_time
                ]
                result[name] = filtered_metrics

        return result

    def get_performance_summary(self) -> dict[str, Any]:
        """Get a performance summary."""
        if not self.performance_snapshots:
            return {}

        latest_snapshot = self.performance_snapshots[-1]

        # Calculate trends (comparing with 5 minutes ago)
        trend_snapshots = [
            snap
            for snap in self.performance_snapshots
            if snap.timestamp > datetime.now() - timedelta(minutes=5)
        ]

        if len(trend_snapshots) > 1:
            oldest = trend_snapshots[0]
            newest = trend_snapshots[-1]

            cpu_trend = newest.cpu_percent - oldest.cpu_percent
            memory_trend = newest.memory_percent - oldest.memory_percent
        else:
            cpu_trend = 0.0
            memory_trend = 0.0

        return {
            "current": {
                "cpu_percent": latest_snapshot.cpu_percent,
                "memory_percent": latest_snapshot.memory_percent,
                "memory_used_mb": latest_snapshot.memory_used_mb,
                "disk_usage_percent": latest_snapshot.disk_usage_percent,
                "active_connections": latest_snapshot.active_connections,
                "request_rate": latest_snapshot.request_rate,
                "error_rate": latest_snapshot.error_rate,
                "avg_response_time": latest_snapshot.avg_response_time,
            },
            "trends": {
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
            },
            "alerts": {
                "active": len([alert for alert in self.alerts if not alert.resolved]),
                "total": len(self.alerts),
            },
            "timestamp": latest_snapshot.timestamp.isoformat(),
        }

    def get_alerts(
        self,
        level: AlertLevel | None = None,
        resolved: bool | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts

        if level:
            alerts = [alert for alert in alerts if alert.level == level]

        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]

        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)

        return alerts[:limit]

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                break

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            data = {
                "metrics": {},
                "performance_snapshots": [],
                "alerts": [],
            }

            for metric_name, metrics in self.metrics.items():
                data["metrics"][metric_name] = [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "metric_type": metric.metric_type.value,
                        "timestamp": metric.timestamp.isoformat(),
                        "labels": metric.labels,
                        "metadata": metric.metadata,
                    }
                    for metric in metrics
                ]

            for snapshot in self.performance_snapshots:
                data["performance_snapshots"].append(
                    {
                        "timestamp": snapshot.timestamp.isoformat(),
                        "cpu_percent": snapshot.cpu_percent,
                        "memory_percent": snapshot.memory_percent,
                        "memory_used_mb": snapshot.memory_used_mb,
                        "disk_usage_percent": snapshot.disk_usage_percent,
                        "network_io": snapshot.network_io,
                        "active_connections": snapshot.active_connections,
                        "request_rate": snapshot.request_rate,
                        "error_rate": snapshot.error_rate,
                        "avg_response_time": snapshot.avg_response_time,
                    },
                )

            for alert in self.alerts:
                data["alerts"].append(
                    {
                        "id": alert.id,
                        "name": alert.name,
                        "message": alert.message,
                        "level": alert.level.value,
                        "timestamp": alert.timestamp.isoformat(),
                        "metric_name": alert.metric_name,
                        "threshold": alert.threshold,
                        "current_value": alert.current_value,
                        "resolved": alert.resolved,
                        "resolved_at": alert.resolved_at.isoformat()
                        if alert.resolved_at
                        else None,
                    },
                )

            return json.dumps(data, indent=2)

        raise ValueError(f"Unsupported export format: {format}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
