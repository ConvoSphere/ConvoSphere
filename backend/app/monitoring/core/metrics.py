"""
Core metrics functionality for performance monitoring.

This module provides the base Metric class and MetricsCollector for
collecting and managing performance metrics.
"""

import json
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


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


class MetricsCollector:
    """Collects and manages performance metrics."""

    def __init__(self, max_metrics: int = 10000, retention_hours: int = 24):
        """Initialize metrics collector."""
        self.max_metrics = max_metrics
        self.retention_hours = retention_hours
        self.metrics: deque[Metric] = deque(maxlen=max_metrics)
        self.aggregated_metrics: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = datetime.now()

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        tags: dict[str, str] | None = None,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a new metric."""
        try:
            metric = Metric(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.now(),
                tags=tags or {},
                description=description,
                metadata=metadata or {},
            )

            self.metrics.append(metric)
            self._aggregate_metric(metric)
            self._cleanup_old_metrics()

        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: dict[str, str] | None = None
    ) -> None:
        """Increment a counter metric."""
        self.record_metric(name, float(value), MetricType.COUNTER, tags)

    def set_gauge(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None
    ) -> None:
        """Set a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, tags)

    def record_histogram(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None
    ) -> None:
        """Record a histogram metric."""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)

    def record_timer(
        self,
        name: str,
        duration: float,
        tags: dict[str, str] | None = None
    ) -> None:
        """Record a timer metric."""
        self.record_metric(name, duration, MetricType.TIMER, tags)

    def get_metrics(
        self,
        name: str | None = None,
        metric_type: MetricType | None = None,
        since: datetime | None = None,
        tags: dict[str, str] | None = None,
        limit: int | None = None,
    ) -> list[Metric]:
        """Get metrics with optional filtering."""
        try:
            filtered_metrics = list(self.metrics)

            # Filter by name
            if name:
                filtered_metrics = [m for m in filtered_metrics if m.name == name]

            # Filter by metric type
            if metric_type:
                filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]

            # Filter by timestamp
            if since:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]

            # Filter by tags
            if tags:
                filtered_metrics = [
                    m for m in filtered_metrics
                    if all(m.tags.get(k) == v for k, v in tags.items())
                ]

            # Apply limit
            if limit:
                filtered_metrics = filtered_metrics[-limit:]

            return filtered_metrics

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []

    def get_statistics(self, name: str, metric_type: MetricType) -> dict[str, float]:
        """Get statistical summary for a metric."""
        try:
            metrics = self.get_metrics(name=name, metric_type=metric_type)
            if not metrics:
                return {}

            values = [m.value for m in metrics]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "sum": sum(values),
            }

        except Exception as e:
            logger.error(f"Failed to get statistics for {name}: {e}")
            return {}

    def get_metric_summary(self) -> dict[str, Any]:
        """Get summary of all metrics."""
        try:
            summary = {
                "total_metrics": len(self.metrics),
                "metric_types": defaultdict(int),
                "top_metrics": defaultdict(int),
                "recent_activity": 0,
            }

            # Count by metric type
            for metric in self.metrics:
                summary["metric_types"][metric.metric_type.value] += 1
                summary["top_metrics"][metric.name] += 1

            # Count recent activity (last hour)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            summary["recent_activity"] = len([
                m for m in self.metrics if m.timestamp >= one_hour_ago
            ])

            return dict(summary)

        except Exception as e:
            logger.error(f"Failed to get metric summary: {e}")
            return {}

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            
            # Remove old metrics from deque
            while self.metrics and self.metrics[0].timestamp < cutoff_time:
                self.metrics.popleft()

            # Clean up aggregated metrics
            for metric_name in list(self.aggregated_metrics.keys()):
                self.aggregated_metrics[metric_name] = [
                    v for v in self.aggregated_metrics[metric_name]
                    if v >= cutoff_time.timestamp()
                ]

        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")

    def _aggregate_metric(self, metric: Metric) -> None:
        """Aggregate metric for statistical analysis."""
        try:
            key = f"{metric.name}_{metric.metric_type.value}"
            self.aggregated_metrics[key].append(metric.timestamp.timestamp())

            # Keep only recent values for aggregation
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            self.aggregated_metrics[key] = [
                v for v in self.aggregated_metrics[key]
                if v >= cutoff_time.timestamp()
            ]

        except Exception as e:
            logger.error(f"Failed to aggregate metric: {e}")

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        try:
            if format.lower() == "json":
                return self._export_json_format()
            elif format.lower() == "prometheus":
                return self._export_prometheus_format()
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return ""

    def _export_json_format(self) -> str:
        """Export metrics in JSON format."""
        try:
            metrics_data = []
            for metric in self.metrics:
                metrics_data.append({
                    "name": metric.name,
                    "value": metric.value,
                    "type": metric.metric_type.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags,
                    "description": metric.description,
                    "metadata": metric.metadata,
                })

            return json.dumps(metrics_data, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to export JSON metrics: {e}")
            return "[]"

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        try:
            prometheus_lines = []
            
            for metric in self.metrics:
                # Convert metric name to Prometheus format
                prometheus_name = metric.name.replace(".", "_").replace("-", "_")
                
                # Build tags string
                tags_str = ""
                if metric.tags:
                    tag_pairs = [f'{k}="{v}"' for k, v in metric.tags.items()]
                    tags_str = "{" + ",".join(tag_pairs) + "}"
                
                # Format value based on metric type
                if metric.metric_type == MetricType.COUNTER:
                    prometheus_lines.append(f"{prometheus_name}_total{tags_str} {metric.value}")
                elif metric.metric_type == MetricType.GAUGE:
                    prometheus_lines.append(f"{prometheus_name}{tags_str} {metric.value}")
                elif metric.metric_type == MetricType.HISTOGRAM:
                    prometheus_lines.append(f"{prometheus_name}_bucket{tags_str} {metric.value}")
                elif metric.metric_type == MetricType.TIMER:
                    prometheus_lines.append(f"{prometheus_name}_seconds{tags_str} {metric.value}")
                
                # Add timestamp
                prometheus_lines.append(f"# {prometheus_name} {metric.timestamp.timestamp()}")

            return "\n".join(prometheus_lines)

        except Exception as e:
            logger.error(f"Failed to export Prometheus metrics: {e}")
            return ""