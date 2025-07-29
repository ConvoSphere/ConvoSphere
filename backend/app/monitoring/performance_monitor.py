"""
Performance monitoring system.

This module provides comprehensive performance monitoring including:
- Request/response time tracking
- Database query performance
- Cache performance metrics
- Memory and CPU usage monitoring
- Custom metrics collection
- Alerting system
- Performance analytics and reporting
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics

from sqlalchemy import event
from sqlalchemy.orm import Session
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.database import get_db
from backend.app.core.caching import get_cache_manager
from loguru import logger
from backend.app.core.config import get_settings




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


@dataclass
class Metric:
    """Performance metric."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


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


class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self):
        self.metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        tags: Dict[str, str] = None,
        description: str = ""
    ):
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            description=description
        )
        
        self.metrics.append(metric)
        
        # Update specific metric storage
        if metric_type == MetricType.COUNTER:
            self.counters[name] += int(value)
        elif metric_type == MetricType.GAUGE:
            self.gauges[name] = value
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[name].append(value)
        elif metric_type == MetricType.TIMER:
            self.timers[name].append(value)
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        self.record_metric(name, value, MetricType.COUNTER, tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric."""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timer metric."""
        self.record_metric(name, duration, MetricType.TIMER, tags)
    
    def get_metrics(
        self,
        name: str = None,
        metric_type: MetricType = None,
        since: datetime = None,
        tags: Dict[str, str] = None
    ) -> List[Metric]:
        """Get metrics with optional filtering."""
        filtered_metrics = list(self.metrics)
        
        if name:
            filtered_metrics = [m for m in filtered_metrics if m.name == name]
        
        if metric_type:
            filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
        
        if since:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
        
        if tags:
            for key, value in tags.items():
                filtered_metrics = [m for m in filtered_metrics if m.tags.get(key) == value]
        
        return filtered_metrics
    
    def get_statistics(self, name: str, metric_type: MetricType) -> Dict[str, float]:
        """Get statistics for a metric."""
        metrics = self.get_metrics(name, metric_type)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }


class AlertManager:
    """Manages performance alerts."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
    
    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        severity: AlertSeverity,
        condition: str = "gt",  # gt, lt, eq, gte, lte
        tags: Dict[str, str] = None
    ):
        """Add an alert rule."""
        self.alert_rules[name] = {
            "metric_name": metric_name,
            "threshold": threshold,
            "severity": severity,
            "condition": condition,
            "tags": tags or {}
        }
    
    def check_alerts(self, metrics_collector: MetricsCollector):
        """Check metrics against alert rules."""
        for rule_name, rule in self.alert_rules.items():
            metrics = metrics_collector.get_metrics(
                name=rule["metric_name"],
                tags=rule["tags"]
            )
            
            if not metrics:
                continue
            
            # Get latest metric value
            latest_metric = max(metrics, key=lambda m: m.timestamp)
            current_value = latest_metric.value
            
            # Check condition
            should_alert = False
            if rule["condition"] == "gt" and current_value > rule["threshold"]:
                should_alert = True
            elif rule["condition"] == "lt" and current_value < rule["threshold"]:
                should_alert = True
            elif rule["condition"] == "eq" and current_value == rule["threshold"]:
                should_alert = True
            elif rule["condition"] == "gte" and current_value >= rule["threshold"]:
                should_alert = True
            elif rule["condition"] == "lte" and current_value <= rule["threshold"]:
                should_alert = True
            
            if should_alert:
                alert = Alert(
                    name=rule_name,
                    message=f"Metric {rule['metric_name']} ({current_value}) {rule['condition']} {rule['threshold']}",
                    severity=rule["severity"],
                    timestamp=datetime.utcnow(),
                    metric_name=rule["metric_name"],
                    threshold=rule["threshold"],
                    current_value=current_value,
                    tags=rule["tags"]
                )
                
                self.alerts.append(alert)
                self._trigger_alert_handlers(alert)
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler."""
        self.alert_handlers.append(handler)
    
    def _trigger_alert_handlers(self, alert: Alert):
        """Trigger all alert handlers."""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def get_alerts(
        self,
        severity: AlertSeverity = None,
        since: datetime = None
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        filtered_alerts = list(self.alerts)
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if since:
            filtered_alerts = [a for a in filtered_alerts if a.timestamp >= since]
        
        return filtered_alerts


class SystemMonitor:
    """Monitors system resources."""
    
    def __init__(self):
        self.last_network_io = psutil.net_io_counters()
        self.last_network_time = time.time()
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network I/O
        current_network_io = psutil.net_io_counters()
        current_time = time.time()
        
        time_diff = current_time - self.last_network_time
        bytes_sent_per_sec = (current_network_io.bytes_sent - self.last_network_io.bytes_sent) / time_diff
        bytes_recv_per_sec = (current_network_io.bytes_recv - self.last_network_io.bytes_recv) / time_diff
        
        self.last_network_io = current_network_io
        self.last_network_time = current_time
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "network_bytes_sent_per_sec": bytes_sent_per_sec,
            "network_bytes_recv_per_sec": bytes_recv_per_sec,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }


class DatabaseMonitor:
    """Monitors database performance."""
    
    def __init__(self, db: Session):
        self.db = db
        self.query_times: List[float] = []
        self.slow_queries: List[Dict[str, Any]] = []
        self._setup_query_monitoring()
    
    def _setup_query_monitoring(self):
        """Setup SQLAlchemy query monitoring."""
        @event.listens_for(self.db, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.db, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if hasattr(context, '_query_start_time'):
                query_time = time.time() - context._query_start_time
                self.query_times.append(query_time)
                
                # Track slow queries (> 1 second)
                if query_time > 1.0:
                    self.slow_queries.append({
                        "statement": statement,
                        "parameters": parameters,
                        "execution_time": query_time,
                        "timestamp": datetime.utcnow()
                    })
    
    def get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        if not self.query_times:
            return {
                "avg_query_time": 0,
                "max_query_time": 0,
                "total_queries": 0,
                "slow_queries_count": 0
            }
        
        return {
            "avg_query_time": statistics.mean(self.query_times),
            "max_query_time": max(self.query_times),
            "total_queries": len(self.query_times),
            "slow_queries_count": len(self.slow_queries)
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries."""
        return sorted(
            self.slow_queries,
            key=lambda x: x["execution_time"],
            reverse=True
        )[:limit]


class PerformanceMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for performance monitoring."""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Record request start
        self.metrics_collector.increment_counter(
            "http_requests_total",
            tags={"method": request.method, "path": request.url.path}
        )
        
        try:
            response = await call_next(request)
            
            # Record successful response
            duration = time.time() - start_time
            self.metrics_collector.record_timer(
                "http_request_duration_seconds",
                duration,
                tags={"method": request.method, "path": request.url.path, "status": response.status_code}
            )
            
            self.metrics_collector.increment_counter(
                "http_responses_total",
                tags={"method": request.method, "path": request.url.path, "status": response.status_code}
            )
            
            return response
            
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            self.metrics_collector.record_timer(
                "http_request_duration_seconds",
                duration,
                tags={"method": request.method, "path": request.url.path, "status": "error"}
            )
            
            self.metrics_collector.increment_counter(
                "http_errors_total",
                tags={"method": request.method, "path": request.url.path, "error": str(type(e).__name__)}
            )
            
            raise


class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self, db: Session):
        self.db = db
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor(db)
        self.cache_manager = get_cache_manager()
        
        # Setup default alert rules
        self._setup_default_alerts()
        
        # Setup alert handlers
        self._setup_alert_handlers()
    
    def _setup_default_alerts(self):
        """Setup default performance alert rules."""
        # High CPU usage
        self.alert_manager.add_alert_rule(
            "high_cpu_usage",
            "cpu_percent",
            80.0,
            AlertSeverity.WARNING,
            "gt"
        )
        
        # High memory usage
        self.alert_manager.add_alert_rule(
            "high_memory_usage",
            "memory_percent",
            85.0,
            AlertSeverity.WARNING,
            "gt"
        )
        
        # High disk usage
        self.alert_manager.add_alert_rule(
            "high_disk_usage",
            "disk_percent",
            90.0,
            AlertSeverity.WARNING,
            "gt"
        )
        
        # Slow response times
        self.alert_manager.add_alert_rule(
            "slow_response_time",
            "http_request_duration_seconds",
            5.0,
            AlertSeverity.WARNING,
            "gt"
        )
        
        # High error rate
        self.alert_manager.add_alert_rule(
            "high_error_rate",
            "http_errors_total",
            10.0,
            AlertSeverity.ERROR,
            "gt"
        )
    
    def _setup_alert_handlers(self):
        """Setup alert handlers."""
        def log_alert(alert: Alert):
            log_level = {
                AlertSeverity.INFO: logger.info,
                AlertSeverity.WARNING: logger.warning,
                AlertSeverity.ERROR: logger.error,
                AlertSeverity.CRITICAL: logger.critical
            }
            
            log_func = log_level.get(alert.severity, logger.warning)
            log_func(f"Performance Alert: {alert.message}")
        
        self.alert_manager.add_alert_handler(log_alert)
    
    async def collect_metrics(self):
        """Collect all performance metrics."""
        # System metrics
        system_metrics = self.system_monitor.get_system_metrics()
        for name, value in system_metrics.items():
            self.metrics_collector.set_gauge(name, value)
        
        # Database metrics
        db_metrics = self.database_monitor.get_database_metrics()
        for name, value in db_metrics.items():
            if isinstance(value, (int, float)):
                self.metrics_collector.set_gauge(f"db_{name}", value)
        
        # Cache metrics
        cache_metrics = self.cache_manager.get_metrics()
        for name, value in cache_metrics.items():
            if isinstance(value, (int, float)):
                self.metrics_collector.set_gauge(f"cache_{name}", value)
        
        # Check alerts
        self.alert_manager.check_alerts(self.metrics_collector)
    
    def get_performance_snapshot(self) -> PerformanceSnapshot:
        """Get a complete performance snapshot."""
        system_metrics = self.system_monitor.get_system_metrics()
        db_metrics = self.database_monitor.get_database_metrics()
        cache_metrics = self.cache_manager.get_metrics()
        
        # Get request metrics
        request_metrics = self.metrics_collector.get_metrics("http_requests_total")
        error_metrics = self.metrics_collector.get_metrics("http_errors_total")
        response_time_metrics = self.metrics_collector.get_metrics("http_request_duration_seconds")
        
        request_count = sum(m.value for m in request_metrics)
        error_count = sum(m.value for m in error_metrics)
        
        avg_response_time = 0
        if response_time_metrics:
            avg_response_time = statistics.mean(m.value for m in response_time_metrics)
        
        return PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=system_metrics["cpu_percent"],
            memory_percent=system_metrics["memory_percent"],
            disk_usage_percent=system_metrics["disk_percent"],
            network_io={
                "bytes_sent_per_sec": system_metrics["network_bytes_sent_per_sec"],
                "bytes_recv_per_sec": system_metrics["network_bytes_recv_per_sec"]
            },
            active_connections=db_metrics.get("total_queries", 0),
            request_count=request_count,
            error_count=error_count,
            avg_response_time=avg_response_time,
            cache_hit_rate=cache_metrics.get("hit_rate", 0)
        )
    
    def get_performance_report(
        self,
        since: datetime = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        if since is None:
            since = datetime.utcnow() - timedelta(hours=1)
        
        # Get metrics for the time period
        metrics = self.metrics_collector.get_metrics(since=since)
        
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in metrics:
            metrics_by_name[metric.name].append(metric)
        
        # Calculate statistics for each metric
        report = {
            "period": {
                "start": since.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "system_metrics": {},
            "application_metrics": {},
            "database_metrics": {},
            "cache_metrics": {},
            "alerts": [alert.__dict__ for alert in self.alert_manager.get_alerts(since=since)]
        }
        
        # Process metrics
        for name, metric_list in metrics_by_name.items():
            values = [m.value for m in metric_list]
            
            if name.startswith("cpu_") or name.startswith("memory_") or name.startswith("disk_"):
                report["system_metrics"][name] = {
                    "current": values[-1] if values else 0,
                    "average": statistics.mean(values) if values else 0,
                    "max": max(values) if values else 0
                }
            elif name.startswith("http_"):
                report["application_metrics"][name] = {
                    "total": sum(values),
                    "average": statistics.mean(values) if values else 0,
                    "max": max(values) if values else 0
                }
            elif name.startswith("db_"):
                report["database_metrics"][name] = {
                    "current": values[-1] if values else 0,
                    "average": statistics.mean(values) if values else 0,
                    "max": max(values) if values else 0
                }
            elif name.startswith("cache_"):
                report["cache_metrics"][name] = {
                    "current": values[-1] if values else 0,
                    "average": statistics.mean(values) if values else 0,
                    "max": max(values) if values else 0
                }
        
        return report


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor(db: Session) -> PerformanceMonitor:
    """Get or create performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(db)
    return _performance_monitor


def monitor_performance(func: Callable):
    """Decorator to monitor function performance."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record metric
            monitor = get_performance_monitor(get_db())
            monitor.metrics_collector.record_timer(
                f"function_{func.__name__}_duration",
                duration
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metric
            monitor = get_performance_monitor(get_db())
            monitor.metrics_collector.increment_counter(
                f"function_{func.__name__}_errors"
            )
            
            raise
    
    return wrapper