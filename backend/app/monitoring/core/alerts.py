"""
Core alerts functionality for performance monitoring.

This module provides the Alert class and AlertManager for
managing performance alerts and notifications.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger

from .metrics import MetricsCollector, MetricType


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


class AlertManager:
    """Manages performance alerts and notifications."""

    def __init__(self):
        """Initialize alert manager."""
        self.alert_rules: dict[str, dict[str, Any]] = {}
        self.alert_handlers: dict[AlertChannel, list[Callable[[Alert], None]]] = {
            channel: [] for channel in AlertChannel
        }
        self.suppressed_alerts: dict[str, datetime] = {}
        self.alert_history: list[Alert] = []

    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        severity: AlertSeverity,
        condition: str = "gt",  # gt, lt, eq, gte, lte
        tags: dict[str, str] | None = None,
        channels: list[AlertChannel] | None = None,
        suppression_window: int | None = None,
    ) -> None:
        """Add a new alert rule."""
        try:
            self.alert_rules[name] = {
                "metric_name": metric_name,
                "threshold": threshold,
                "severity": severity,
                "condition": condition,
                "tags": tags or {},
                "channels": channels or [AlertChannel.LOG],
                "suppression_window": suppression_window,
                "created_at": datetime.now(),
            }
            logger.info(f"Added alert rule: {name}")

        except Exception as e:
            logger.error(f"Failed to add alert rule {name}: {e}")

    def check_alerts(self, metrics_collector: MetricsCollector) -> list[Alert]:
        """Check all alert rules and return triggered alerts."""
        try:
            triggered_alerts = []

            for rule_name, rule in self.alert_rules.items():
                # Check if alert is suppressed
                if self._is_alert_suppressed(rule_name, datetime.now()):
                    continue

                # Get current metric value
                current_value = self._get_current_metric_value(
                    metrics_collector,
                    rule["metric_name"],
                    rule["tags"]
                )

                if current_value is None:
                    continue

                # Check condition
                if self._check_condition(
                    current_value,
                    rule["threshold"],
                    rule["condition"]
                ):
                    # Create alert
                    alert = Alert(
                        name=rule_name,
                        message=f"Metric {rule['metric_name']} triggered alert: "
                               f"{current_value} {rule['condition']} {rule['threshold']}",
                        severity=rule["severity"],
                        timestamp=datetime.now(),
                        metric_name=rule["metric_name"],
                        threshold=rule["threshold"],
                        current_value=current_value,
                        tags=rule["tags"],
                        channel=rule["channels"][0] if rule["channels"] else AlertChannel.LOG,
                        metadata={"rule": rule},
                    )

                    triggered_alerts.append(alert)
                    self.alert_history.append(alert)

                    # Trigger alert handlers
                    self._trigger_alert_handlers(alert)

                    # Suppress alert if suppression window is set
                    if rule["suppression_window"]:
                        self._suppress_alert(rule_name, rule["suppression_window"])

            return triggered_alerts

        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []

    def add_alert_handler(
        self,
        channel: AlertChannel,
        handler: Callable[[Alert], None]
    ) -> None:
        """Add an alert handler for a specific channel."""
        try:
            self.alert_handlers[channel].append(handler)
            logger.info(f"Added alert handler for channel: {channel}")

        except Exception as e:
            logger.error(f"Failed to add alert handler: {e}")

    def _trigger_alert_handlers(self, alert: Alert) -> None:
        """Trigger all handlers for an alert."""
        try:
            # Trigger handlers for the alert's channel
            for handler in self.alert_handlers[alert.channel]:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")

            # Also trigger log handlers for all alerts
            if alert.channel != AlertChannel.LOG:
                for handler in self.alert_handlers[AlertChannel.LOG]:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Log alert handler failed: {e}")

        except Exception as e:
            logger.error(f"Failed to trigger alert handlers: {e}")

    def get_alerts(
        self,
        severity: AlertSeverity | None = None,
        since: datetime | None = None
    ) -> list[Alert]:
        """Get alert history with optional filtering."""
        try:
            filtered_alerts = list(self.alert_history)

            # Filter by severity
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a.severity == severity]

            # Filter by timestamp
            if since:
                filtered_alerts = [a for a in filtered_alerts if a.timestamp >= since]

            return filtered_alerts

        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []

    def get_alert_summary(self) -> dict[str, Any]:
        """Get summary of alert activity."""
        try:
            summary = {
                "total_alerts": len(self.alert_history),
                "active_rules": len(self.alert_rules),
                "severity_counts": {},
                "recent_alerts": 0,
                "suppressed_alerts": len(self.suppressed_alerts),
            }

            # Count by severity
            for alert in self.alert_history:
                severity = alert.severity.value
                summary["severity_counts"][severity] = summary["severity_counts"].get(severity, 0) + 1

            # Count recent alerts (last hour)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            summary["recent_alerts"] = len([
                a for a in self.alert_history if a.timestamp >= one_hour_ago
            ])

            return summary

        except Exception as e:
            logger.error(f"Failed to get alert summary: {e}")
            return {}

    def _is_alert_suppressed(self, rule_name: str, current_time: datetime) -> bool:
        """Check if an alert is currently suppressed."""
        if rule_name in self.suppressed_alerts:
            return self.suppressed_alerts[rule_name] > current_time
        return False

    def _suppress_alert(self, rule_name: str, suppression_window: int) -> None:
        """Suppress an alert for the specified window."""
        self.suppressed_alerts[rule_name] = datetime.now() + timedelta(seconds=suppression_window)

    def _get_current_metric_value(
        self,
        metrics_collector: MetricsCollector,
        metric_name: str,
        tags: dict[str, str]
    ) -> float | None:
        """Get the current value of a metric."""
        try:
            # Get the most recent metric matching the name and tags
            metrics = metrics_collector.get_metrics(
                name=metric_name,
                tags=tags,
                limit=1
            )

            if metrics:
                return metrics[-1].value

            return None

        except Exception as e:
            logger.error(f"Failed to get current metric value for {metric_name}: {e}")
            return None

    def _check_condition(
        self,
        value: float,
        threshold: float,
        condition: str
    ) -> bool:
        """Check if a value meets the alert condition."""
        try:
            if condition == "gt":
                return value > threshold
            elif condition == "lt":
                return value < threshold
            elif condition == "eq":
                return value == threshold
            elif condition == "gte":
                return value >= threshold
            elif condition == "lte":
                return value <= threshold
            else:
                logger.warning(f"Unknown condition: {condition}")
                return False

        except Exception as e:
            logger.error(f"Failed to check condition: {e}")
            return False