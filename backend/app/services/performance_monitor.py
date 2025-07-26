"""
Performance Monitoring Service for metrics collection and optimization.

This module provides comprehensive performance monitoring with
metrics collection, database optimization, and performance analytics.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class PerformanceMetric(BaseModel):
    """Performance metric with validation."""

    metric_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique metric ID",
    )
    metric_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Metric name",
    )
    metric_type: str = Field(
        ...,
        pattern="^(counter|gauge|histogram|timer)$",
        description="Metric type",
    )
    value: int | float = Field(..., description="Metric value")
    unit: str = Field(default="", max_length=20, description="Metric unit")
    tags: dict[str, str] = Field(default_factory=dict, description="Metric tags")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Metric timestamp",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        """Validate metric name."""
        if not v or not v.strip():
            raise ValueError("Metric name cannot be empty")
        return v.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> int | float:
        """Validate metric value."""
        if isinstance(v, int | float) and not (
            isinstance(v, float) and (v != v or v == float("inf") or v == float("-inf"))
        ):
            return v
        raise ValueError("Metric value must be a valid number")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class DatabaseQueryMetric(BaseModel):
    """Database query performance metric."""

    query_id: str = Field(default_factory=lambda: str(uuid4()), description="Query ID")
    query_type: str = Field(
        ...,
        pattern="^(select|insert|update|delete|create|drop)$",
        description="Query type",
    )
    table_name: str = Field(..., min_length=1, max_length=100, description="Table name")
    execution_time: float = Field(..., ge=0, description="Execution time in seconds")
    rows_affected: int = Field(default=0, ge=0, description="Rows affected")
    query_size: int = Field(default=0, ge=0, description="Query size in bytes")
    connection_pool_size: int = Field(
        default=0,
        ge=0,
        description="Connection pool size",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Query timestamp",
    )
    error: str | None = Field(None, description="Query error")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class APIMetric(BaseModel):
    """API performance metric."""

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Request ID",
    )
    endpoint: str = Field(..., min_length=1, max_length=200, description="API endpoint")
    method: str = Field(
        ...,
        pattern="^(GET|POST|PUT|DELETE|PATCH)$",
        description="HTTP method",
    )
    status_code: int = Field(..., ge=100, le=599, description="HTTP status code")
    response_time: float = Field(..., ge=0, description="Response time in seconds")
    request_size: int = Field(default=0, ge=0, description="Request size in bytes")
    response_size: int = Field(default=0, ge=0, description="Response size in bytes")
    user_id: str | None = Field(None, description="User ID")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Request timestamp",
    )
    error: str | None = Field(None, description="Request error")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class CacheMetric(BaseModel):
    """Cache performance metric."""

    cache_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Cache operation ID",
    )
    operation: str = Field(
        ...,
        pattern="^(get|set|delete|clear)$",
        description="Cache operation",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Cache namespace",
    )
    key: str = Field(..., min_length=1, max_length=200, description="Cache key")
    operation_time: float = Field(..., ge=0, description="Operation time in seconds")
    cache_hit: bool = Field(
        default=False,
        description="Whether operation was a cache hit",
    )
    data_size: int = Field(default=0, ge=0, description="Data size in bytes")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Operation timestamp",
    )
    error: str | None = Field(None, description="Operation error")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class PerformanceAlert(BaseModel):
    """Performance alert with thresholds."""

    alert_id: str = Field(default_factory=lambda: str(uuid4()), description="Alert ID")
    alert_type: str = Field(
        ...,
        pattern="^(threshold|anomaly|trend)$",
        description="Alert type",
    )
    metric_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Metric name",
    )
    threshold: int | float = Field(..., description="Alert threshold")
    current_value: int | float = Field(..., description="Current metric value")
    severity: str = Field(
        ...,
        pattern="^(low|medium|high|critical)$",
        description="Alert severity",
    )
    message: str = Field(..., min_length=1, max_length=500, description="Alert message")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Alert timestamp",
    )
    resolved: bool = Field(default=False, description="Whether alert is resolved")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class PerformanceMonitor:
    """Main performance monitoring service."""

    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.monitoring_enabled = True
        self.metrics_history: list[PerformanceMetric] = []
        self.database_metrics: list[DatabaseQueryMetric] = []
        self.api_metrics: list[APIMetric] = []
        self.cache_metrics: list[CacheMetric] = []
        self.alerts: list[PerformanceAlert] = []

        # Performance thresholds
        self.thresholds = {
            "api_response_time": 1.0,  # seconds
            "database_query_time": 0.5,  # seconds
            "cache_operation_time": 0.1,  # seconds
            "memory_usage": 80.0,  # percentage
            "cpu_usage": 80.0,  # percentage
            "error_rate": 5.0,  # percentage
        }

        # Alert rules
        self.alert_rules = {
            "api_response_time": {"threshold": 1.0, "severity": "medium"},
            "database_query_time": {"threshold": 0.5, "severity": "high"},
            "cache_hit_rate": {"threshold": 70.0, "severity": "low"},
            "error_rate": {"threshold": 5.0, "severity": "critical"},
        }

        # Statistics
        self.stats = {
            "total_metrics": 0,
            "total_alerts": 0,
            "active_alerts": 0,
            "last_cleanup": datetime.now(UTC),
        }

    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        self.monitoring_enabled = True
        logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring_enabled = False
        logger.info("Performance monitoring stopped")

    def record_metric(self, metric: PerformanceMetric) -> None:
        """Record a performance metric."""
        try:
            # Validate metric
            if not isinstance(metric, PerformanceMetric):
                raise ValueError("Invalid metric object")

            # Add to history
            self.metrics_history.append(metric)
            self.stats["total_metrics"] += 1

            # Check for alerts
            self._check_alerts(metric)

            # Cleanup old metrics
            self._cleanup_old_metrics()

            logger.debug(f"Recorded metric: {metric.metric_name} = {metric.value}")

        except Exception as e:
            logger.error(f"Failed to record metric: {e}")

    def record_database_query(self, query_metric: DatabaseQueryMetric) -> None:
        """Record database query performance."""
        try:
            self.database_metrics.append(query_metric)

            # Check for slow queries
            if query_metric.execution_time > self.thresholds["database_query_time"]:
                alert = PerformanceAlert(
                    alert_type="threshold",
                    metric_name="database_query_time",
                    threshold=self.thresholds["database_query_time"],
                    current_value=query_metric.execution_time,
                    severity="high",
                    message=f"Slow database query detected: {query_metric.execution_time:.3f}s on table {query_metric.table_name}",
                )
                self._add_alert(alert)

            logger.debug(
                f"Recorded database query: {query_metric.query_type} on {query_metric.table_name} in {query_metric.execution_time:.3f}s",
            )

        except Exception as e:
            logger.error(f"Failed to record database query: {e}")

    def record_api_request(self, api_metric: APIMetric) -> None:
        """Record API request performance."""
        try:
            self.api_metrics.append(api_metric)

            # Check for slow responses
            if api_metric.response_time > self.thresholds["api_response_time"]:
                alert = PerformanceAlert(
                    alert_type="threshold",
                    metric_name="api_response_time",
                    threshold=self.thresholds["api_response_time"],
                    current_value=api_metric.response_time,
                    severity="medium",
                    message=f"Slow API response: {api_metric.method} {api_metric.endpoint} took {api_metric.response_time:.3f}s",
                )
                self._add_alert(alert)

            # Check for errors
            if api_metric.status_code >= 400:
                alert = PerformanceAlert(
                    alert_type="threshold",
                    metric_name="api_error_rate",
                    threshold=0,
                    current_value=1,
                    severity="high",
                    message=f"API error: {api_metric.status_code} on {api_metric.method} {api_metric.endpoint}",
                )
                self._add_alert(alert)

            logger.debug(
                f"Recorded API request: {api_metric.method} {api_metric.endpoint} - {api_metric.status_code} in {api_metric.response_time:.3f}s",
            )

        except Exception as e:
            logger.error(f"Failed to record API request: {e}")

    def record_cache_operation(self, cache_metric: CacheMetric) -> None:
        """Record cache operation performance."""
        try:
            self.cache_metrics.append(cache_metric)

            # Check for slow cache operations
            if cache_metric.operation_time > self.thresholds["cache_operation_time"]:
                alert = PerformanceAlert(
                    alert_type="threshold",
                    metric_name="cache_operation_time",
                    threshold=self.thresholds["cache_operation_time"],
                    current_value=cache_metric.operation_time,
                    severity="low",
                    message=f"Slow cache operation: {cache_metric.operation} took {cache_metric.operation_time:.3f}s",
                )
                self._add_alert(alert)

            logger.debug(
                f"Recorded cache operation: {cache_metric.operation} on {cache_metric.namespace}:{cache_metric.key} in {cache_metric.operation_time:.3f}s",
            )

        except Exception as e:
            logger.error(f"Failed to record cache operation: {e}")

    def _check_alerts(self, metric: PerformanceMetric) -> None:
        """Check for performance alerts based on metric."""
        if metric.metric_name in self.alert_rules:
            rule = self.alert_rules[metric.metric_name]
            threshold = rule["threshold"]
            severity = rule["severity"]

            # Check if threshold is exceeded
            if metric.value > threshold:
                alert = PerformanceAlert(
                    alert_type="threshold",
                    metric_name=metric.metric_name,
                    threshold=threshold,
                    current_value=metric.value,
                    severity=severity,
                    message=f"Performance threshold exceeded: {metric.metric_name} = {metric.value} (threshold: {threshold})",
                )
                self._add_alert(alert)

    def _add_alert(self, alert: PerformanceAlert) -> None:
        """Add performance alert."""
        self.alerts.append(alert)
        self.stats["total_alerts"] += 1
        self.stats["active_alerts"] += 1

        logger.warning(f"Performance alert: {alert.severity.upper()} - {alert.message}")

    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory issues."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)  # Keep last 24 hours

        # Cleanup metrics history
        self.metrics_history = [
            m for m in self.metrics_history if m.timestamp > cutoff_time
        ]

        # Cleanup database metrics
        self.database_metrics = [
            m for m in self.database_metrics if m.timestamp > cutoff_time
        ]

        # Cleanup API metrics
        self.api_metrics = [m for m in self.api_metrics if m.timestamp > cutoff_time]

        # Cleanup cache metrics
        self.cache_metrics = [
            m for m in self.cache_metrics if m.timestamp > cutoff_time
        ]

        # Cleanup resolved alerts
        self.alerts = [
            a for a in self.alerts if not a.resolved or a.timestamp > cutoff_time
        ]

        self.stats["last_cleanup"] = datetime.now(UTC)

    def get_metrics_summary(
        self,
        time_range: timedelta = timedelta(hours=1),
    ) -> dict[str, Any]:
        """Get metrics summary for the specified time range."""
        cutoff_time = datetime.now(UTC) - time_range

        # Filter metrics by time range
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]

        recent_db_metrics = [
            m for m in self.database_metrics if m.timestamp > cutoff_time
        ]

        recent_api_metrics = [m for m in self.api_metrics if m.timestamp > cutoff_time]

        recent_cache_metrics = [
            m for m in self.cache_metrics if m.timestamp > cutoff_time
        ]

        # Calculate statistics
        return {
            "time_range": str(time_range),
            "total_metrics": len(recent_metrics),
            "database_queries": {
                "total": len(recent_db_metrics),
                "avg_execution_time": self._calculate_average(
                    [m.execution_time for m in recent_db_metrics],
                ),
                "slow_queries": len(
                    [
                        m
                        for m in recent_db_metrics
                        if m.execution_time > self.thresholds["database_query_time"]
                    ],
                ),
            },
            "api_requests": {
                "total": len(recent_api_metrics),
                "avg_response_time": self._calculate_average(
                    [m.response_time for m in recent_api_metrics],
                ),
                "error_rate": self._calculate_error_rate(recent_api_metrics),
                "status_codes": self._count_status_codes(recent_api_metrics),
            },
            "cache_operations": {
                "total": len(recent_cache_metrics),
                "avg_operation_time": self._calculate_average(
                    [m.operation_time for m in recent_cache_metrics],
                ),
                "hit_rate": self._calculate_cache_hit_rate(recent_cache_metrics),
            },
            "alerts": {
                "total": len([a for a in self.alerts if a.timestamp > cutoff_time]),
                "active": len(
                    [
                        a
                        for a in self.alerts
                        if not a.resolved and a.timestamp > cutoff_time
                    ],
                ),
                "by_severity": self._count_alerts_by_severity(cutoff_time),
            },
        }

    def _calculate_average(self, values: list[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _calculate_error_rate(self, api_metrics: list[APIMetric]) -> float:
        """Calculate API error rate."""
        if not api_metrics:
            return 0.0
        error_count = len([m for m in api_metrics if m.status_code >= 400])
        return (error_count / len(api_metrics)) * 100

    def _calculate_cache_hit_rate(self, cache_metrics: list[CacheMetric]) -> float:
        """Calculate cache hit rate."""
        if not cache_metrics:
            return 0.0
        hit_count = len([m for m in cache_metrics if m.cache_hit])
        return (hit_count / len(cache_metrics)) * 100

    def _count_status_codes(self, api_metrics: list[APIMetric]) -> dict[int, int]:
        """Count API status codes."""
        status_counts = {}
        for metric in api_metrics:
            status_counts[metric.status_code] = (
                status_counts.get(metric.status_code, 0) + 1
            )
        return status_counts

    def _count_alerts_by_severity(self, cutoff_time: datetime) -> dict[str, int]:
        """Count alerts by severity."""
        recent_alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        severity_counts = {}
        for alert in recent_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        return severity_counts

    def get_slow_queries(self, limit: int = 10) -> list[DatabaseQueryMetric]:
        """Get slowest database queries."""
        sorted_queries = sorted(
            self.database_metrics,
            key=lambda x: x.execution_time,
            reverse=True,
        )
        return sorted_queries[:limit]

    def get_slow_endpoints(self, limit: int = 10) -> list[APIMetric]:
        """Get slowest API endpoints."""
        sorted_endpoints = sorted(
            self.api_metrics,
            key=lambda x: x.response_time,
            reverse=True,
        )
        return sorted_endpoints[:limit]

    def get_active_alerts(self) -> list[PerformanceAlert]:
        """Get active (unresolved) alerts."""
        return [a for a in self.alerts if not a.resolved]

    def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.stats["active_alerts"] -= 1
                logger.info(f"Alert {alert_id} marked as resolved")
                return True
        return False

    def set_threshold(self, metric_name: str, threshold: float) -> None:
        """Set performance threshold."""
        self.thresholds[metric_name] = threshold
        logger.info(f"Set threshold for {metric_name}: {threshold}")

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self.stats,
            "current_metrics": len(self.metrics_history),
            "current_alerts": len(self.alerts),
            "thresholds": self.thresholds,
        }


class DatabaseOptimizer:
    """Database optimization service."""

    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.optimization_rules = {
            "slow_queries": {
                "threshold": 0.5,  # seconds
                "action": "suggest_index",
            },
            "frequent_queries": {
                "threshold": 100,  # queries per hour
                "action": "suggest_cache",
            },
            "large_result_sets": {
                "threshold": 1000,  # rows
                "action": "suggest_pagination",
            },
        }

    def analyze_query_performance(self) -> dict[str, Any]:
        """Analyze database query performance and suggest optimizations."""
        recent_queries = [
            q
            for q in self.performance_monitor.database_metrics
            if q.timestamp > datetime.now(UTC) - timedelta(hours=1)
        ]

        analysis = {
            "total_queries": len(recent_queries),
            "slow_queries": [],
            "frequent_queries": [],
            "optimization_suggestions": [],
        }

        # Analyze slow queries
        slow_queries = [
            q
            for q in recent_queries
            if q.execution_time > self.optimization_rules["slow_queries"]["threshold"]
        ]
        analysis["slow_queries"] = slow_queries

        # Analyze frequent queries
        query_counts = {}
        for query in recent_queries:
            key = f"{query.query_type}:{query.table_name}"
            query_counts[key] = query_counts.get(key, 0) + 1

        frequent_queries = [
            {"query": key, "count": count}
            for key, count in query_counts.items()
            if count > self.optimization_rules["frequent_queries"]["threshold"]
        ]
        analysis["frequent_queries"] = frequent_queries

        # Generate optimization suggestions
        suggestions = []

        # Suggest indexes for slow queries
        for query in slow_queries:
            suggestions.append(
                {
                    "type": "index",
                    "table": query.table_name,
                    "query_type": query.query_type,
                    "reason": f"Query took {query.execution_time:.3f}s",
                    "priority": "high" if query.execution_time > 1.0 else "medium",
                },
            )

        # Suggest caching for frequent queries
        for query_info in frequent_queries:
            suggestions.append(
                {
                    "type": "cache",
                    "query": query_info["query"],
                    "count": query_info["count"],
                    "reason": f"Query executed {query_info['count']} times in the last hour",
                    "priority": "medium",
                },
            )

        analysis["optimization_suggestions"] = suggestions

        return analysis

    def get_connection_pool_stats(self) -> dict[str, Any]:
        """Get database connection pool statistics."""
        recent_queries = [
            q
            for q in self.performance_monitor.database_metrics
            if q.timestamp > datetime.now(UTC) - timedelta(minutes=5)
        ]

        if not recent_queries:
            return {"error": "No recent database queries"}

        avg_pool_size = self.performance_monitor._calculate_average(
            [q.connection_pool_size for q in recent_queries],
        )

        return {
            "average_pool_size": avg_pool_size,
            "total_queries": len(recent_queries),
            "avg_query_time": self.performance_monitor._calculate_average(
                [q.execution_time for q in recent_queries],
            ),
        }


# Add missing attributes to PerformanceMonitor class
PerformanceMonitor.db = None
PerformanceMonitor.redis_client = None
PerformanceMonitor.weaviate_client = None

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
database_optimizer = DatabaseOptimizer(performance_monitor)
