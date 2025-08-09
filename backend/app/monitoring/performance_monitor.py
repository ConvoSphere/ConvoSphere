"""
Modular Performance Monitor.

This module provides a comprehensive performance monitoring system that
orchestrates metrics collection, alerting, and reporting across system,
database, and application layers.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.core.caching import get_cache_manager
from backend.app.core.config import get_settings

from .core import AlertChannel, AlertManager, AlertSeverity, MetricsCollector
from .database import DatabaseMonitor
from .system import SystemMonitor
from .types import (
    DatabaseMetrics,
    PerformanceReport,
    PerformanceSnapshot,
    RequestMetrics,
    SystemMetrics,
)


class PerformanceMonitor:
    """Modular performance monitoring system."""

    def __init__(self, db: Session):
        """Initialize performance monitor with all components."""
        self.db = db
        self.settings = get_settings()

        # Initialize monitoring components
        self.metrics_collector = MetricsCollector(
            max_metrics=self.settings.monitoring_max_metrics,
            retention_hours=self.settings.monitoring_retention_hours,
        )
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor(db)

        # Monitoring state
        self.monitoring_task: asyncio.Task | None = None
        self.is_monitoring = False

        # Cache manager
        self.cache_manager = get_cache_manager()

        # Setup default alerts and handlers
        self._setup_default_alerts()
        self._setup_alert_handlers()

    def _setup_default_alerts(self):
        """Setup default alert rules."""
        try:
            # System alerts
            self.alert_manager.add_alert_rule(
                name="high_cpu_usage",
                metric_name="cpu_percent",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                condition="gt",
                tags={"component": "system"},
                channels=[AlertChannel.LOG],
                suppression_window=300,  # 5 minutes
            )

            self.alert_manager.add_alert_rule(
                name="high_memory_usage",
                metric_name="memory_percent",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                condition="gt",
                tags={"component": "system"},
                channels=[AlertChannel.LOG],
                suppression_window=300,
            )

            self.alert_manager.add_alert_rule(
                name="high_disk_usage",
                metric_name="disk_percent",
                threshold=90.0,
                severity=AlertSeverity.ERROR,
                condition="gt",
                tags={"component": "system"},
                channels=[AlertChannel.LOG],
                suppression_window=600,  # 10 minutes
            )

            # Database alerts
            self.alert_manager.add_alert_rule(
                name="high_slow_query_rate",
                metric_name="slow_query_percentage",
                threshold=10.0,
                severity=AlertSeverity.WARNING,
                condition="gt",
                tags={"component": "database"},
                channels=[AlertChannel.LOG],
                suppression_window=300,
            )

            # Request alerts
            self.alert_manager.add_alert_rule(
                name="high_error_rate",
                metric_name="error_rate_percent",
                threshold=5.0,
                severity=AlertSeverity.WARNING,
                condition="gt",
                tags={"component": "requests"},
                channels=[AlertChannel.LOG],
                suppression_window=300,
            )

            self.alert_manager.add_alert_rule(
                name="slow_response_time",
                metric_name="avg_response_time_seconds",
                threshold=2.0,
                severity=AlertSeverity.WARNING,
                condition="gt",
                tags={"component": "requests"},
                channels=[AlertChannel.LOG],
                suppression_window=300,
            )

            logger.info("Default alert rules configured")

        except Exception as e:
            logger.error(f"Failed to setup default alerts: {e}")

    def _setup_alert_handlers(self):
        """Setup alert handlers for different channels."""
        try:

            def log_alert(alert: Alert):
                """Log alert to logger."""
                log_level = {
                    AlertSeverity.INFO: logger.info,
                    AlertSeverity.WARNING: logger.warning,
                    AlertSeverity.ERROR: logger.error,
                    AlertSeverity.CRITICAL: logger.critical,
                }.get(alert.severity, logger.warning)

                log_level(
                    f"ALERT [{alert.severity.value.upper()}] {alert.name}: {alert.message} "
                    f"(Metric: {alert.metric_name}, Value: {alert.current_value}, "
                    f"Threshold: {alert.threshold})"
                )

            # Register log handler
            self.alert_manager.add_alert_handler(AlertChannel.LOG, log_alert)

            logger.info("Alert handlers configured")

        except Exception as e:
            logger.error(f"Failed to setup alert handlers: {e}")

    async def start_monitoring(self):
        """Start the monitoring loop."""
        try:
            if self.is_monitoring:
                logger.warning("Monitoring is already running")
                return

            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Performance monitoring started")

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.is_monitoring = False

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        try:
            if not self.is_monitoring:
                return

            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            logger.info("Performance monitoring stopped")

        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_monitoring:
                await self.collect_metrics()
                await asyncio.sleep(self.settings.monitoring_collection_interval)

        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            self.is_monitoring = False

    async def collect_metrics(self):
        """Collect metrics from all monitoring components."""
        try:
            # Collect system metrics
            system_metrics = self.system_monitor.get_system_metrics()
            for name, value in system_metrics.items():
                self.metrics_collector.set_gauge(
                    name, value, tags={"component": "system"}
                )

            # Collect database metrics
            db_metrics = self.database_monitor.get_database_metrics()
            if db_metrics:
                for category, metrics in db_metrics.items():
                    if isinstance(metrics, dict):
                        for name, value in metrics.items():
                            if isinstance(value, (int, float)):
                                self.metrics_collector.set_gauge(
                                    f"db_{category}_{name}",
                                    float(value),
                                    tags={
                                        "component": "database",
                                        "category": category,
                                    },
                                )

            # Collect cache metrics if available
            if hasattr(self.cache_manager, "get_stats"):
                try:
                    cache_stats = self.cache_manager.get_stats()
                    for name, value in cache_stats.items():
                        if isinstance(value, (int, float)):
                            self.metrics_collector.set_gauge(
                                f"cache_{name}",
                                float(value),
                                tags={"component": "cache"},
                            )
                except Exception as e:
                    logger.debug(f"Failed to collect cache metrics: {e}")

            # Check alerts
            triggered_alerts = self.alert_manager.check_alerts(self.metrics_collector)
            if triggered_alerts:
                logger.info(f"Triggered {len(triggered_alerts)} alerts")

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")

    def get_performance_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot."""
        try:
            # Get system metrics
            system_metrics = self.system_monitor.get_system_metrics()

            # Get database metrics
            db_metrics = self.database_monitor.get_database_metrics()

            # Get request statistics
            request_stats = self._get_request_statistics()

            # Calculate cache hit rate
            cache_hit_rate = 0.0
            if hasattr(self.cache_manager, "get_stats"):
                try:
                    cache_stats = self.cache_manager.get_stats()
                    cache_hit_rate = cache_stats.get("hit_rate", 0.0)
                except Exception:
                    pass

            return PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=system_metrics.get("cpu_percent", 0.0),
                memory_percent=system_metrics.get("memory_percent", 0.0),
                disk_usage_percent=system_metrics.get("disk_percent", 0.0),
                network_io={
                    "bytes_sent": system_metrics.get("network_bytes_sent", 0.0),
                    "bytes_recv": system_metrics.get("network_bytes_recv", 0.0),
                    "packets_sent": system_metrics.get("network_packets_sent", 0.0),
                    "packets_recv": system_metrics.get("network_packets_recv", 0.0),
                },
                active_connections=db_metrics.get("connection", {}).get(
                    "checked_out", 0
                ),
                request_count=request_stats.get("total_requests", 0),
                error_count=request_stats.get("total_errors", 0),
                avg_response_time=request_stats.get("avg_response_time_seconds", 0.0),
                cache_hit_rate=cache_hit_rate,
                database_connections=db_metrics.get("connection", {}).get(
                    "pool_size", 0
                ),
                slow_queries=db_metrics.get("queries", {}).get("slow_queries", 0),
                custom_metrics={},
            )

        except Exception as e:
            logger.error(f"Failed to get performance snapshot: {e}")
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                active_connections=0,
                request_count=0,
                error_count=0,
                avg_response_time=0.0,
                cache_hit_rate=0.0,
                database_connections=0,
                slow_queries=0,
            )

    def get_performance_report(
        self, since: datetime | None = None
    ) -> PerformanceReport:
        """Get comprehensive performance report."""
        try:
            if since is None:
                since = datetime.now() - timedelta(hours=1)

            # Get current metrics
            system_metrics = self.system_monitor.get_system_metrics()
            db_metrics = self.database_monitor.get_database_metrics()
            request_stats = self._get_request_statistics()

            # Get alerts
            alerts = self.alert_manager.get_alerts(since=since)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                system_metrics, db_metrics, request_stats
            )

            # Create summary
            summary = {
                "system_health": self._calculate_system_health(system_metrics),
                "database_health": self._calculate_database_health(db_metrics),
                "application_health": self._calculate_application_health(request_stats),
                "overall_health": "healthy",  # Will be calculated
            }

            # Calculate overall health
            health_scores = [
                summary["system_health"],
                summary["database_health"],
                summary["application_health"],
            ]
            avg_health = sum(health_scores) / len(health_scores)

            if avg_health >= 0.8:
                summary["overall_health"] = "healthy"
            elif avg_health >= 0.6:
                summary["overall_health"] = "warning"
            else:
                summary["overall_health"] = "critical"

            return PerformanceReport(
                timestamp=datetime.now(),
                system_metrics=SystemMetrics(**system_metrics),
                database_metrics=DatabaseMetrics(**db_metrics) if db_metrics else None,
                request_metrics=RequestMetrics(**request_stats),
                alerts=alerts,
                recommendations=recommendations,
                summary=summary,
            )

        except Exception as e:
            logger.error(f"Failed to get performance report: {e}")
            return None

    def _get_request_statistics(self) -> dict[str, Any]:
        """Get request statistics from middleware."""
        try:
            # This would typically come from the middleware
            # For now, return basic stats
            return {
                "total_requests": 0,
                "total_errors": 0,
                "error_rate_percent": 0.0,
                "avg_response_time_seconds": 0.0,
                "requests_per_minute": 0.0,
                "time_window_minutes": 60,
            }

        except Exception as e:
            logger.error(f"Failed to get request statistics: {e}")
            return {}

    def _generate_recommendations(
        self,
        system_metrics: dict[str, float],
        db_metrics: dict[str, Any],
        request_stats: dict[str, Any],
    ) -> list[str]:
        """Generate performance recommendations."""
        recommendations = []

        try:
            # System recommendations
            if system_metrics.get("cpu_percent", 0) > 80:
                recommendations.append(
                    "High CPU usage detected. Consider scaling up or optimizing CPU-intensive operations."
                )

            if system_metrics.get("memory_percent", 0) > 85:
                recommendations.append(
                    "High memory usage detected. Consider increasing memory or optimizing memory usage."
                )

            if system_metrics.get("disk_percent", 0) > 90:
                recommendations.append(
                    "High disk usage detected. Consider cleaning up disk space or expanding storage."
                )

            # Database recommendations
            if db_metrics:
                slow_query_pct = db_metrics.get("queries", {}).get(
                    "slow_query_percentage", 0
                )
                if slow_query_pct > 10:
                    recommendations.append(
                        f"High slow query rate ({slow_query_pct:.1f}%). Consider optimizing database queries."
                    )

                avg_query_time = db_metrics.get("queries", {}).get("avg_query_time", 0)
                if avg_query_time > 1.0:
                    recommendations.append(
                        f"High average query time ({avg_query_time:.2f}s). Consider database optimization."
                    )

            # Request recommendations
            error_rate = request_stats.get("error_rate_percent", 0)
            if error_rate > 5:
                recommendations.append(
                    f"High error rate ({error_rate:.1f}%). Investigate application errors."
                )

            avg_response_time = request_stats.get("avg_response_time_seconds", 0)
            if avg_response_time > 2.0:
                recommendations.append(
                    f"Slow response times ({avg_response_time:.2f}s). Consider performance optimization."
                )

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")

        return recommendations

    def _calculate_system_health(self, system_metrics: dict[str, float]) -> float:
        """Calculate system health score (0-1)."""
        try:
            cpu_score = 1.0 - (system_metrics.get("cpu_percent", 0) / 100.0)
            memory_score = 1.0 - (system_metrics.get("memory_percent", 0) / 100.0)
            disk_score = 1.0 - (system_metrics.get("disk_percent", 0) / 100.0)

            return (cpu_score + memory_score + disk_score) / 3.0

        except Exception:
            return 0.5

    def _calculate_database_health(self, db_metrics: dict[str, Any]) -> float:
        """Calculate database health score (0-1)."""
        try:
            if not db_metrics:
                return 0.5

            slow_query_score = 1.0 - (
                db_metrics.get("queries", {}).get("slow_query_percentage", 0) / 100.0
            )
            avg_query_score = max(
                0.0,
                1.0 - (db_metrics.get("queries", {}).get("avg_query_time", 0) / 5.0),
            )

            return (slow_query_score + avg_query_score) / 2.0

        except Exception:
            return 0.5

    def _calculate_application_health(self, request_stats: dict[str, Any]) -> float:
        """Calculate application health score (0-1)."""
        try:
            error_score = 1.0 - (request_stats.get("error_rate_percent", 0) / 100.0)
            response_score = max(
                0.0, 1.0 - (request_stats.get("avg_response_time_seconds", 0) / 5.0)
            )

            return (error_score + response_score) / 2.0

        except Exception:
            return 0.5

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        return self.metrics_collector.export_metrics(format)

    def get_alert_history(self) -> list[Any]:
        """Get alert history."""
        return self.alert_manager.get_alerts()


def get_performance_monitor(db: Session) -> PerformanceMonitor:
    """Get performance monitor instance."""
    return PerformanceMonitor(db)


def monitor_performance(func):
    """Decorator to monitor function performance."""

    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            # This would typically use a global metrics collector
            logger.debug(f"Function {func.__name__} took {duration:.3f}s")

    return wrapper
