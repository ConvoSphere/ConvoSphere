"""
Performance monitoring types and data structures.

This module contains all the data structures, enums, and types used
across the performance monitoring system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    tags: dict[str, str] = field(default_factory=dict)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


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
    tags: dict[str, str] = field(default_factory=dict)
    channel: AlertChannel = AlertChannel.LOG
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """System performance snapshot."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: dict[str, float]
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float
    cache_hit_rate: float
    database_connections: int
    slow_queries: int
    custom_metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System-level metrics."""

    cpu_percent: float
    cpu_count: int
    cpu_freq_mhz: float
    load_avg_1min: float
    load_avg_5min: float
    load_avg_15min: float
    memory_percent: float
    memory_available_gb: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_free_gb: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: float
    network_bytes_recv: float
    network_packets_sent: float
    network_packets_recv: float
    network_send_rate_bps: float
    network_recv_rate_bps: float


@dataclass
class DatabaseMetrics:
    """Database performance metrics."""

    engine_name: str
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    total_queries: int
    slow_queries: int
    avg_query_time: float
    max_query_time: float
    min_query_time: float
    recent_avg_time: float
    query_count_by_type: dict[str, int]
    slow_query_percentage: float
    queries_per_minute: float


@dataclass
class RequestMetrics:
    """HTTP request metrics."""

    total_requests: int
    total_errors: int
    error_rate_percent: float
    avg_response_time_seconds: float
    requests_per_minute: float
    time_window_minutes: int


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""

    timestamp: datetime
    system_metrics: SystemMetrics
    database_metrics: DatabaseMetrics
    request_metrics: RequestMetrics
    alerts: list[Alert]
    recommendations: list[str]
    summary: dict[str, Any]


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    enabled: bool = True
    collection_interval_seconds: int = 60
    retention_hours: int = 24
    max_metrics: int = 10000
    alert_check_interval_seconds: int = 30
    slow_query_threshold_seconds: float = 1.0
    slow_request_threshold_seconds: float = 5.0
    export_formats: list[str] = field(default_factory=lambda: ["json", "prometheus"])
    alert_channels: list[AlertChannel] = field(
        default_factory=lambda: [AlertChannel.LOG]
    )


@dataclass
class QueryInfo:
    """Database query information."""

    statement: str
    parameters: str | None
    execution_time: float
    timestamp: float
    executemany: bool


@dataclass
class AlertRule:
    """Alert rule configuration."""

    name: str
    metric_name: str
    threshold: float
    severity: AlertSeverity
    condition: str  # gt, lt, eq, gte, lte
    tags: dict[str, str]
    channels: list[AlertChannel]
    suppression_window: int | None
    created_at: datetime


@dataclass
class MetricSummary:
    """Metric summary statistics."""

    total_metrics: int
    metric_types: dict[str, int]
    top_metrics: dict[str, int]
    recent_activity: int


@dataclass
class AlertSummary:
    """Alert summary statistics."""

    total_alerts: int
    active_rules: int
    severity_counts: dict[str, int]
    recent_alerts: int
    suppressed_alerts: int
