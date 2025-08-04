"""
Enhanced Performance monitoring system.

This module provides comprehensive performance monitoring including:
- Request/response time tracking
- Database query performance
- Cache performance metrics
- Memory and CPU usage monitoring
- Custom metrics collection
- Alerting system with multiple channels
- Performance analytics and reporting
- Integration with external monitoring systems
"""

import asyncio
import json
import statistics
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
from fastapi import Request
from loguru import logger
from sqlalchemy import event
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.caching import get_cache_manager
from backend.app.core.config import get_settings
from backend.app.core.database import get_db


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels."""

    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"


@dataclass
class Metric:
    """Performance metric."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Performance alert."""

    name: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metric_name: str
    threshold: float
    current_value: float
    tags: Dict[str, str] = field(default_factory=dict)
    channel: AlertChannel = AlertChannel.LOG
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """System performance snapshot."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float
    cache_hit_rate: float
    database_connections: int
    slow_queries: int
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class MetricsCollector:
    """Enhanced metrics collector with persistence and aggregation."""

    def __init__(self, max_metrics: int = 10000, retention_hours: int = 24):
        self.max_metrics = max_metrics
        self.retention_hours = retention_hours
        self.metrics: deque = deque(maxlen=max_metrics)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.aggregation_interval = 60  # seconds
        self.last_aggregation = time.time()

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        tags: Optional[Dict[str, str]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a metric with enhanced metadata."""
        if tags is None:
            tags = {}
        if metadata is None:
            metadata = {}

        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags,
            description=description,
            metadata=metadata,
        )

        self.metrics.append(metric)

        # Update internal aggregations
        if metric_type == MetricType.COUNTER:
            self.counters[name] += int(value)
        elif metric_type == MetricType.GAUGE:
            self.gauges[name] = value
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[name].append(value)
        elif metric_type == MetricType.TIMER:
            self.timers[name].append(value)

        # Cleanup old data
        self._cleanup_old_metrics()

        # Periodic aggregation
        current_time = time.time()
        if current_time - self.last_aggregation > self.aggregation_interval:
            self._aggregate_metrics()
            self.last_aggregation = current_time

    def increment_counter(
        self, 
        name: str, 
        value: int = 1, 
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        self.record_metric(name, value, MetricType.COUNTER, tags)

    def set_gauge(
        self, 
        name: str, 
        value: float, 
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, tags)

    def record_histogram(
        self, 
        name: str, 
        value: float, 
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram metric."""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)

    def record_timer(
        self, 
        name: str, 
        duration: float, 
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a timer metric."""
        self.record_metric(name, duration, MetricType.TIMER, tags)

    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        since: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> List[Metric]:
        """Get metrics with filtering and pagination."""
        filtered_metrics = []

        for metric in self.metrics:
            # Filter by name
            if name and metric.name != name:
                continue

            # Filter by type
            if metric_type and metric.metric_type != metric_type:
                continue

            # Filter by time
            if since and metric.timestamp < since:
                continue

            # Filter by tags
            if tags and not all(
                metric.tags.get(k) == v for k, v in tags.items()
            ):
                continue

            filtered_metrics.append(metric)

        # Sort by timestamp (newest first)
        filtered_metrics.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit
        if limit:
            filtered_metrics = filtered_metrics[:limit]

        return filtered_metrics

    def get_statistics(self, name: str, metric_type: MetricType) -> Dict[str, float]:
        """Get statistical summary for a metric."""
        metrics = self.get_metrics(name=name, metric_type=metric_type)
        
        if not metrics:
            return {}

        values = [m.value for m in metrics]
        
        stats = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
        }

        if len(values) > 1:
            stats["std_dev"] = statistics.stdev(values)
            stats["variance"] = statistics.variance(values)

        # Add percentiles
        sorted_values = sorted(values)
        stats["p50"] = sorted_values[len(sorted_values) // 2]
        stats["p90"] = sorted_values[int(len(sorted_values) * 0.9)]
        stats["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
        stats["p99"] = sorted_values[int(len(sorted_values) * 0.99)]

        return stats

    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            "total_metrics": len(self.metrics),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {name: len(values) for name, values in self.histograms.items()},
            "timers": {name: len(values) for name, values in self.timers.items()},
        }

        # Add recent activity
        recent_metrics = self.get_metrics(since=datetime.now() - timedelta(minutes=5))
        summary["recent_activity"] = len(recent_metrics)

        return summary

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        # Remove old metrics from deque
        while self.metrics and self.metrics[0].timestamp < cutoff_time:
            self.metrics.popleft()

        # Clean up histograms and timers
        for name in list(self.histograms.keys()):
            self.histograms[name] = [
                v for v in self.histograms[name]
                if v > cutoff_time.timestamp()
            ]
            if not self.histograms[name]:
                del self.histograms[name]

        for name in list(self.timers.keys()):
            self.timers[name] = [
                v for v in self.timers[name]
                if v > cutoff_time.timestamp()
            ]
            if not self.timers[name]:
                del self.timers[name]

    def _aggregate_metrics(self) -> None:
        """Aggregate metrics for better performance."""
        # This could include:
        # - Computing rolling averages
        # - Downsampling old data
        # - Computing percentiles
        # - Sending aggregated data to external systems
        pass

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in various formats."""
        if format == "json":
            return json.dumps(self.get_metric_summary(), default=str)
        elif format == "prometheus":
            return self._export_prometheus_format()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Counters
        for name, value in self.counters.items():
            lines.append(f"# HELP {name} Counter metric")
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            lines.append(f"# HELP {name} Gauge metric")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Histograms
        for name, values in self.histograms.items():
            if values:
                lines.append(f"# HELP {name} Histogram metric")
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
                lines.append(f"{name}_bucket{{le=\"+Inf\"}} {len(values)}")
        
        return "\n".join(lines)


class AlertManager:
    """Enhanced alert manager with multiple notification channels."""

    def __init__(self):
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Alert] = []
        self.alert_handlers: Dict[AlertChannel, List[Callable]] = defaultdict(list)
        self.alert_history: deque = deque(maxlen=1000)
        self.suppression_rules: Dict[str, datetime] = {}
        self.suppression_window = 300  # 5 minutes

    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        severity: AlertSeverity,
        condition: str = "gt",  # gt, lt, eq, gte, lte
        tags: Optional[Dict[str, str]] = None,
        channels: Optional[List[AlertChannel]] = None,
        suppression_window: Optional[int] = None,
    ) -> None:
        """Add an alert rule with enhanced configuration."""
        if tags is None:
            tags = {}
        if channels is None:
            channels = [AlertChannel.LOG]

        self.alert_rules[name] = {
            "name": name,
            "metric_name": metric_name,
            "threshold": threshold,
            "severity": severity,
            "condition": condition,
            "tags": tags,
            "channels": channels,
            "suppression_window": suppression_window or self.suppression_window,
        }

        logger.info(f"Added alert rule: {name} for {metric_name}")

    def check_alerts(self, metrics_collector: MetricsCollector) -> List[Alert]:
        """Check all alert rules and generate alerts."""
        new_alerts = []
        current_time = datetime.now()

        for rule_name, rule in self.alert_rules.items():
            # Check if alert is suppressed
            if self._is_alert_suppressed(rule_name, current_time):
                continue

            # Get current metric value
            metric_value = self._get_current_metric_value(
                metrics_collector, rule["metric_name"], rule["tags"]
            )

            if metric_value is None:
                continue

            # Check condition
            should_alert = self._check_condition(
                metric_value, rule["threshold"], rule["condition"]
            )

            if should_alert:
                alert = Alert(
                    name=rule_name,
                    message=f"{rule['metric_name']} = {metric_value} {rule['condition']} {rule['threshold']}",
                    severity=rule["severity"],
                    timestamp=current_time,
                    metric_name=rule["metric_name"],
                    threshold=rule["threshold"],
                    current_value=metric_value,
                    tags=rule["tags"],
                    channel=rule["channels"][0],  # Use first channel
                    metadata={
                        "condition": rule["condition"],
                        "channels": [c.value for c in rule["channels"]],
                    },
                )

                new_alerts.append(alert)
                self.alerts.append(alert)
                self.alert_history.append(alert)

                # Suppress future alerts for this rule
                self._suppress_alert(rule_name, rule["suppression_window"])

                # Trigger alert handlers
                self._trigger_alert_handlers(alert)

        return new_alerts

    def add_alert_handler(
        self, 
        channel: AlertChannel, 
        handler: Callable[[Alert], None]
    ) -> None:
        """Add an alert handler for a specific channel."""
        self.alert_handlers[channel].append(handler)
        logger.info(f"Added alert handler for channel: {channel.value}")

    def _trigger_alert_handlers(self, alert: Alert) -> None:
        """Trigger all handlers for an alert."""
        for channel in alert.metadata.get("channels", [alert.channel.value]):
            try:
                channel_enum = AlertChannel(channel)
                for handler in self.alert_handlers[channel_enum]:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler failed: {e}")
            except ValueError:
                logger.warning(f"Unknown alert channel: {channel}")

    def get_alerts(
        self, 
        severity: Optional[AlertSeverity] = None, 
        since: Optional[datetime] = None
    ) -> List[Alert]:
        """Get alerts with filtering."""
        filtered_alerts = []

        for alert in self.alerts:
            if severity and alert.severity != severity:
                continue
            if since and alert.timestamp < since:
                continue
            filtered_alerts.append(alert)

        return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alerts."""
        total_alerts = len(self.alerts)
        recent_alerts = len(self.get_alerts(since=datetime.now() - timedelta(hours=1)))
        
        severity_counts = defaultdict(int)
        for alert in self.alerts:
            severity_counts[alert.severity.value] += 1

        return {
            "total_alerts": total_alerts,
            "recent_alerts": recent_alerts,
            "severity_counts": dict(severity_counts),
            "active_rules": len(self.alert_rules),
            "suppressed_alerts": len(self.suppression_rules),
        }

    def _is_alert_suppressed(self, rule_name: str, current_time: datetime) -> bool:
        """Check if an alert is currently suppressed."""
        suppression_end = self.suppression_rules.get(rule_name)
        if suppression_end and current_time < suppression_end:
            return True
        return False

    def _suppress_alert(self, rule_name: str, suppression_window: int) -> None:
        """Suppress an alert for a specified window."""
        self.suppression_rules[rule_name] = datetime.now() + timedelta(seconds=suppression_window)

    def _get_current_metric_value(
        self, 
        metrics_collector: MetricsCollector, 
        metric_name: str, 
        tags: Dict[str, str]
    ) -> Optional[float]:
        """Get the current value of a metric."""
        recent_metrics = metrics_collector.get_metrics(
            name=metric_name, 
            tags=tags, 
            limit=1
        )
        
        if recent_metrics:
            return recent_metrics[0].value
        return None

    def _check_condition(
        self, 
        value: float, 
        threshold: float, 
        condition: str
    ) -> bool:
        """Check if a condition is met."""
        if condition == "gt":
            return value > threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return value == threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False


class SystemMonitor:
    """Enhanced system monitor with detailed metrics."""

    def __init__(self):
        self.last_network_io = psutil.net_io_counters()
        self.last_network_time = time.time()

    def get_system_metrics(self) -> Dict[str, float]:
        """Get comprehensive system metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        current_network_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_network_time
        
        network_sent_rate = (current_network_io.bytes_sent - self.last_network_io.bytes_sent) / time_diff
        network_recv_rate = (current_network_io.bytes_recv - self.last_network_io.bytes_recv) / time_diff
        
        self.last_network_io = current_network_io
        self.last_network_time = current_time

        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()

        metrics = {
            # CPU
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else 0,
            
            # Memory
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            
            # Disk
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3),
            "disk_used_gb": disk.used / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
            
            # Network
            "network_sent_rate_mbps": network_sent_rate * 8 / (1024**2),
            "network_recv_rate_mbps": network_recv_rate * 8 / (1024**2),
            "network_sent_total_mb": current_network_io.bytes_sent / (1024**2),
            "network_recv_total_mb": current_network_io.bytes_recv / (1024**2),
            
            # Process
            "process_memory_mb": process_memory.rss / (1024**2),
            "process_cpu_percent": process_cpu,
            "process_threads": process.num_threads(),
            "process_open_files": len(process.open_files()),
            "process_connections": len(process.connections()),
        }

        return metrics

    def get_detailed_system_info(self) -> Dict[str, Any]:
        """Get detailed system information."""
        return {
            "platform": {
                "system": psutil.sys.platform,
                "release": psutil.sys.getwindowsversion() if hasattr(psutil.sys, 'getwindowsversion') else "Unknown",
                "version": psutil.sys.version,
            },
            "cpu": {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                "min_frequency": psutil.cpu_freq().min if psutil.cpu_freq() else 0,
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "free": psutil.virtual_memory().free,
            },
            "disk": {
                "partitions": [
                    {
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "usage": psutil.disk_usage(p.mountpoint)._asdict() if p.mountpoint else None,
                    }
                    for p in psutil.disk_partitions()
                ],
            },
            "network": {
                "interfaces": psutil.net_if_addrs(),
                "connections": len(psutil.net_connections()),
            },
        }


class DatabaseMonitor:
    """Enhanced database monitor with query analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.query_times: List[float] = []
        self.slow_queries: List[Dict[str, Any]] = []
        self.query_count = 0
        self.error_count = 0
        self._setup_query_monitoring()

    def _setup_query_monitoring(self):
        """Set up database query monitoring."""
        @event.listens_for(self.db, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()

        @event.listens_for(self.db, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_time = time.time() - context._query_start_time
            self.query_times.append(query_time)
            self.query_count += 1

            # Track slow queries
            if query_time > 1.0:  # Queries taking more than 1 second
                self.slow_queries.append({
                    "statement": statement,
                    "parameters": parameters,
                    "execution_time": query_time,
                    "timestamp": datetime.now(),
                })

            # Keep only recent slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

    def get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        if not self.query_times:
            return {
                "query_count": 0,
                "error_count": 0,
                "avg_query_time": 0,
                "slow_query_count": 0,
                "total_query_time": 0,
            }

        return {
            "query_count": self.query_count,
            "error_count": self.error_count,
            "avg_query_time": statistics.mean(self.query_times),
            "max_query_time": max(self.query_times),
            "min_query_time": min(self.query_times),
            "slow_query_count": len(self.slow_queries),
            "total_query_time": sum(self.query_times),
            "query_per_second": self.query_count / max(1, (time.time() - self.query_times[0] if self.query_times else 1)),
        }

    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries."""
        return sorted(
            self.slow_queries, 
            key=lambda x: x["execution_time"], 
            reverse=True
        )[:limit]

    def reset_metrics(self) -> None:
        """Reset database metrics."""
        self.query_times.clear()
        self.slow_queries.clear()
        self.query_count = 0
        self.error_count = 0


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Enhanced performance middleware with detailed metrics."""

    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.request_count = 0
        self.error_count = 0

    async def dispatch(self, request: Request, call_next):
        """Process request with performance monitoring."""
        start_time = time.time()
        self.request_count += 1

        # Record request start
        self.metrics_collector.increment_counter(
            "http_requests_total",
            tags={
                "method": request.method,
                "path": request.url.path,
                "status": "started",
            }
        )

        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record successful request
            self.metrics_collector.record_timer(
                "http_request_duration_seconds",
                response_time,
                tags={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": str(response.status_code),
                }
            )
            
            self.metrics_collector.increment_counter(
                "http_requests_total",
                tags={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "success",
                    "status_code": str(response.status_code),
                }
            )

            # Record response size
            if hasattr(response, 'body'):
                response_size = len(response.body) if response.body else 0
                self.metrics_collector.record_histogram(
                    "http_response_size_bytes",
                    response_size,
                    tags={
                        "method": request.method,
                        "path": request.url.path,
                    }
                )

            return response

        except Exception as e:
            # Record error
            self.error_count += 1
            response_time = time.time() - start_time
            
            self.metrics_collector.increment_counter(
                "http_requests_total",
                tags={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "error",
                }
            )
            
            self.metrics_collector.record_timer(
                "http_request_duration_seconds",
                response_time,
                tags={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "error",
                }
            )
            
            logger.error(f"Request failed: {request.method} {request.url.path} - {e}")
            raise


class PerformanceMonitor:
    """Enhanced performance monitor with comprehensive monitoring."""

    def __init__(self, db: Session):
        self.db = db
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor(db)
        self.monitoring_enabled = get_settings().performance_monitoring_enabled
        self.monitoring_interval = get_settings().performance_monitoring_interval
        self.alert_thresholds = get_settings().performance_alert_thresholds
        
        self._setup_default_alerts()
        self._setup_alert_handlers()
        self._monitoring_task: Optional[asyncio.Task] = None

    def _setup_default_alerts(self):
        """Set up default performance alerts."""
        default_alerts = {
            "high_cpu": {
                "metric": "cpu_percent",
                "threshold": 80.0,
                "condition": "gt",
                "severity": AlertSeverity.WARNING,
            },
            "high_memory": {
                "metric": "memory_percent",
                "threshold": 85.0,
                "condition": "gt",
                "severity": AlertSeverity.WARNING,
            },
            "high_disk": {
                "metric": "disk_percent",
                "threshold": 90.0,
                "condition": "gt",
                "severity": AlertSeverity.WARNING,
            },
            "slow_response": {
                "metric": "http_request_duration_seconds",
                "threshold": 5.0,
                "condition": "gt",
                "severity": AlertSeverity.WARNING,
            },
            "high_error_rate": {
                "metric": "http_requests_total",
                "threshold": 0.1,  # 10% error rate
                "condition": "gt",
                "severity": AlertSeverity.ERROR,
            },
        }

        for alert_name, config in default_alerts.items():
            self.alert_manager.add_alert_rule(
                name=alert_name,
                metric_name=config["metric"],
                threshold=config["threshold"],
                severity=config["severity"],
                condition=config["condition"],
            )

    def _setup_alert_handlers(self):
        """Set up alert handlers."""
        def log_alert(alert: Alert):
            log_level = {
                AlertSeverity.INFO: logger.info,
                AlertSeverity.WARNING: logger.warning,
                AlertSeverity.ERROR: logger.error,
                AlertSeverity.CRITICAL: logger.critical,
            }.get(alert.severity, logger.warning)
            
            log_level(
                f"Performance Alert: {alert.name} - {alert.message} "
                f"(Value: {alert.current_value}, Threshold: {alert.threshold})"
            )

        self.alert_manager.add_alert_handler(AlertChannel.LOG, log_alert)

    async def start_monitoring(self):
        """Start the monitoring task."""
        if not self.monitoring_enabled:
            logger.info("Performance monitoring is disabled")
            return

        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring task is already running")
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring task."""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def collect_metrics(self):
        """Collect all performance metrics."""
        # System metrics
        system_metrics = self.system_monitor.get_system_metrics()
        for name, value in system_metrics.items():
            self.metrics_collector.set_gauge(f"system_{name}", value)

        # Database metrics
        db_metrics = self.database_monitor.get_database_metrics()
        for name, value in db_metrics.items():
            self.metrics_collector.set_gauge(f"database_{name}", value)

        # Cache metrics
        try:
            cache_manager = get_cache_manager()
            if cache_manager:
                cache_stats = cache_manager.get_stats()
                for name, value in cache_stats.items():
                    self.metrics_collector.set_gauge(f"cache_{name}", value)
        except Exception as e:
            logger.debug(f"Could not collect cache metrics: {e}")

        # Check alerts
        alerts = self.alert_manager.check_alerts(self.metrics_collector)
        if alerts:
            logger.info(f"Generated {len(alerts)} performance alerts")

    def get_performance_snapshot(self) -> PerformanceSnapshot:
        """Get a comprehensive performance snapshot."""
        system_metrics = self.system_monitor.get_system_metrics()
        db_metrics = self.database_monitor.get_database_metrics()
        
        # Get recent request metrics
        recent_requests = self.metrics_collector.get_metrics(
            name="http_requests_total",
            since=datetime.now() - timedelta(minutes=5)
        )
        
        recent_response_times = self.metrics_collector.get_metrics(
            name="http_request_duration_seconds",
            since=datetime.now() - timedelta(minutes=5)
        )

        return PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=system_metrics.get("cpu_percent", 0),
            memory_percent=system_metrics.get("memory_percent", 0),
            disk_usage_percent=system_metrics.get("disk_percent", 0),
            network_io={
                "sent_mbps": system_metrics.get("network_sent_rate_mbps", 0),
                "recv_mbps": system_metrics.get("network_recv_rate_mbps", 0),
            },
            active_connections=system_metrics.get("process_connections", 0),
            request_count=len(recent_requests),
            error_count=self.metrics_collector.counters.get("http_requests_total", 0),
            avg_response_time=statistics.mean([m.value for m in recent_response_times]) if recent_response_times else 0,
            cache_hit_rate=0,  # Would need cache manager integration
            database_connections=db_metrics.get("query_count", 0),
            slow_queries=db_metrics.get("slow_query_count", 0),
        )

    def get_performance_report(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get a comprehensive performance report."""
        if since is None:
            since = datetime.now() - timedelta(hours=1)

        # Get metrics for the time period
        metrics = self.metrics_collector.get_metrics(since=since)
        
        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.name].append(metric)

        # Calculate statistics for each metric group
        report = {
            "period": {
                "start": since.isoformat(),
                "end": datetime.now().isoformat(),
                "duration_hours": (datetime.now() - since).total_seconds() / 3600,
            },
            "system": {
                "cpu_avg": statistics.mean([m.value for m in metric_groups.get("system_cpu_percent", [])]),
                "memory_avg": statistics.mean([m.value for m in metric_groups.get("system_memory_percent", [])]),
                "disk_avg": statistics.mean([m.value for m in metric_groups.get("system_disk_percent", [])]),
            },
            "requests": {
                "total": len(metric_groups.get("http_requests_total", [])),
                "avg_response_time": statistics.mean([m.value for m in metric_groups.get("http_request_duration_seconds", [])]) if metric_groups.get("http_request_duration_seconds") else 0,
                "max_response_time": max([m.value for m in metric_groups.get("http_request_duration_seconds", [])]) if metric_groups.get("http_request_duration_seconds") else 0,
            },
            "database": {
                "total_queries": sum([m.value for m in metric_groups.get("database_query_count", [])]),
                "avg_query_time": statistics.mean([m.value for m in metric_groups.get("database_avg_query_time", [])]) if metric_groups.get("database_avg_query_time") else 0,
                "slow_queries": sum([m.value for m in metric_groups.get("database_slow_query_count", [])]),
            },
            "alerts": self.alert_manager.get_alert_summary(),
            "recommendations": self._generate_recommendations(metric_groups),
        }

        return report

    def _generate_recommendations(self, metric_groups: Dict[str, List[Metric]]) -> List[str]:
        """Generate performance recommendations based on metrics."""
        recommendations = []

        # CPU recommendations
        cpu_metrics = metric_groups.get("system_cpu_percent", [])
        if cpu_metrics:
            avg_cpu = statistics.mean([m.value for m in cpu_metrics])
            if avg_cpu > 80:
                recommendations.append("High CPU usage detected. Consider scaling up or optimizing CPU-intensive operations.")
            elif avg_cpu < 20:
                recommendations.append("Low CPU usage. Consider scaling down to reduce costs.")

        # Memory recommendations
        memory_metrics = metric_groups.get("system_memory_percent", [])
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics])
            if avg_memory > 85:
                recommendations.append("High memory usage detected. Consider increasing memory or optimizing memory usage.")

        # Response time recommendations
        response_time_metrics = metric_groups.get("http_request_duration_seconds", [])
        if response_time_metrics:
            avg_response_time = statistics.mean([m.value for m in response_time_metrics])
            if avg_response_time > 2:
                recommendations.append("Slow response times detected. Consider optimizing database queries or caching.")

        # Database recommendations
        slow_query_metrics = metric_groups.get("database_slow_query_count", [])
        if slow_query_metrics:
            total_slow_queries = sum([m.value for m in slow_query_metrics])
            if total_slow_queries > 10:
                recommendations.append("Multiple slow queries detected. Review and optimize database queries.")

        return recommendations

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in various formats."""
        return self.metrics_collector.export_metrics(format)

    def get_alert_history(self) -> List[Alert]:
        """Get alert history."""
        return list(self.alert_manager.alert_history)


# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor(db: Session) -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor(db)
    return performance_monitor


def monitor_performance(func: Callable):
    """Decorator to monitor function performance."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record metric
            if performance_monitor:
                performance_monitor.metrics_collector.record_timer(
                    f"function_{func.__name__}_duration_seconds",
                    execution_time,
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record error metric
            if performance_monitor:
                performance_monitor.metrics_collector.increment_counter(
                    f"function_{func.__name__}_errors_total",
                )
            
            raise
    return wrapper
