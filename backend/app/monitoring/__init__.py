"""
Performance Monitoring System.

This module provides a comprehensive performance monitoring system with
modular components for metrics collection, alerting, and reporting.
"""

from .core import (
    Alert,
    AlertChannel,
    AlertManager,
    AlertSeverity,
    Metric,
    MetricsCollector,
    MetricType,
)
from .database import DatabaseMonitor
from .middleware import PerformanceMiddleware
from .performance_monitor import (
    PerformanceMonitor,
    get_performance_monitor,
    monitor_performance,
)
from .system import SystemMonitor
from .types import (
    AlertRule,
    AlertSummary,
    DatabaseMetrics,
    MetricSummary,
    MonitoringConfig,
    PerformanceReport,
    PerformanceSnapshot,
    QueryInfo,
    RequestMetrics,
    SystemMetrics,
)

__all__ = [
    # Main classes
    "PerformanceMonitor",
    "get_performance_monitor",
    "monitor_performance",
    # Core components
    "MetricsCollector",
    "AlertManager",
    "Metric",
    "Alert",
    "MetricType",
    "AlertSeverity",
    "AlertChannel",
    # Monitoring components
    "SystemMonitor",
    "DatabaseMonitor",
    "PerformanceMiddleware",
    # Types and data structures
    "PerformanceSnapshot",
    "SystemMetrics",
    "DatabaseMetrics",
    "RequestMetrics",
    "PerformanceReport",
    "MonitoringConfig",
    "QueryInfo",
    "AlertRule",
    "MetricSummary",
    "AlertSummary",
]
