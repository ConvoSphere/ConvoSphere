"""
Performance Monitoring System.

This module provides a comprehensive performance monitoring system with
modular components for metrics collection, alerting, and reporting.
"""

from .performance_monitor import PerformanceMonitor, get_performance_monitor, monitor_performance
from .core import MetricsCollector, AlertManager, Metric, Alert, MetricType, AlertSeverity, AlertChannel
from .system import SystemMonitor
from .database import DatabaseMonitor
from .middleware import PerformanceMiddleware
from .types import (
    PerformanceSnapshot,
    SystemMetrics,
    DatabaseMetrics,
    RequestMetrics,
    PerformanceReport,
    MonitoringConfig,
    QueryInfo,
    AlertRule,
    MetricSummary,
    AlertSummary,
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