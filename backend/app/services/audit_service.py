"""
Comprehensive audit service for detailed logging and compliance.

This service provides advanced audit logging, compliance reporting,
retention management, and real-time alerts for enterprise environments.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import redis
from backend.app.core.config import settings
from backend.app.models.audit_extended import (
    AuditAlert,
    AuditArchive,
    AuditEventCategory,
    AuditEventType,
    AuditPolicy,
    AuditRetentionRule,
    AuditSeverity,
    ComplianceFramework,
    ComplianceReport,
    DataClassification,
    ExtendedAuditLog,
)
from backend.app.models.user import User
from backend.app.utils.exceptions import AuditError, ComplianceError
from fastapi import Request
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuditContext:
    """Context manager for audit logging."""

    def __init__(self, audit_service, **kwargs):
        self.audit_service = audit_service
        self.start_time = time.time()
        self.context_data = kwargs
        self.event_id = str(uuid4())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = int(
            (time.time() - self.start_time) * 1000,
        )  # Convert to milliseconds
        self.context_data["event_duration"] = duration
        self.context_data["event_id"] = self.event_id

        if exc_type:
            self.context_data["action_result"] = "failure"
            self.context_data["error_message"] = str(exc_val)
            self.context_data["severity"] = AuditSeverity.ERROR
        else:
            self.context_data["action_result"] = "success"

        await self.audit_service.log_event(**self.context_data)


class AuditService:
    """Comprehensive audit service for enterprise environments."""

    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_AUDIT_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.alert_prefix = "audit_alert:"
        self.cache_prefix = "audit_cache:"

    async def log_event(
        self,
        event_type: AuditEventType,
        event_category: AuditEventCategory,
        user: User | None = None,
        request: Request | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        resource_name: str | None = None,
        action: str | None = None,
        action_result: str = "success",
        error_message: str | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        compliance_frameworks: list[ComplianceFramework] | None = None,
        data_classification: DataClassification | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        threat_level: str | None = None,
        risk_score: int | None = None,
        security_impact: str | None = None,
        organization_id: str | None = None,
        department: str | None = None,
        project: str | None = None,
        event_id: str | None = None,
        event_duration: int | None = None,
        **kwargs,
    ) -> ExtendedAuditLog:
        """Log an audit event with comprehensive details."""
        try:
            # Check if event should be logged based on policies
            if not await self._should_log_event(event_type, event_category, user):
                return None

            # Extract request information
            ip_address = None
            user_agent = None
            session_id = None

            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                session_id = request.headers.get("x-session-id")

            # Create audit log entry
            audit_log = ExtendedAuditLog(
                event_id=event_id or str(uuid4()),
                event_type=event_type,
                event_category=event_category,
                severity=severity,
                timestamp=datetime.now(),
                event_duration=event_duration,
                user_id=str(user.id) if user else None,
                username=user.username if user else None,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                action=action,
                action_result=action_result,
                error_message=error_message,
                context=context or {},
                metadata=metadata or {},
                tags=tags or [],
                compliance_frameworks=(
                    [f.value for f in compliance_frameworks]
                    if compliance_frameworks
                    else None
                ),
                data_classification=data_classification,
                threat_level=threat_level,
                risk_score=risk_score,
                security_impact=security_impact,
                organization_id=organization_id,
                department=department,
                project=project,
            )

            # Apply retention rules
            await self._apply_retention_rules(audit_log)

            # Save to database
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)

            # Check for alerts
            await self._check_alerts(audit_log)

            # Cache for performance
            await self._cache_audit_event(audit_log)

            logger.info(
                f"Audit event logged: {event_type} for user {user.username if user else 'anonymous'}",
            )
            return audit_log

        except Exception as e:
            logger.exception(f"Failed to log audit event: {str(e)}")
            raise AuditError(f"Failed to log audit event: {str(e)}")

    def audit_context(
        self,
        event_type: AuditEventType,
        event_category: AuditEventCategory,
        user: User | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> AuditContext:
        """Create an audit context for automatic logging."""
        return AuditContext(
            self,
            event_type=event_type,
            event_category=event_category,
            user=user,
            request=request,
            **kwargs,
        )

    async def get_audit_logs(
        self,
        user_id: str | None = None,
        event_type: AuditEventType | None = None,
        event_category: AuditEventCategory | None = None,
        severity: AuditSeverity | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        compliance_framework: ComplianceFramework | None = None,
        data_classification: DataClassification | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        size: int = 100,
        include_context: bool = True,
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Get audit logs with filtering and pagination."""
        try:
            query = self.db.query(ExtendedAuditLog)

            # Apply filters
            if user_id:
                query = query.filter(ExtendedAuditLog.user_id == user_id)

            if event_type:
                query = query.filter(ExtendedAuditLog.event_type == event_type)

            if event_category:
                query = query.filter(ExtendedAuditLog.event_category == event_category)

            if severity:
                query = query.filter(ExtendedAuditLog.severity == severity)

            if resource_type:
                query = query.filter(ExtendedAuditLog.resource_type == resource_type)

            if resource_id:
                query = query.filter(ExtendedAuditLog.resource_id == resource_id)

            if compliance_framework:
                query = query.filter(
                    ExtendedAuditLog.compliance_frameworks.contains(
                        [compliance_framework.value],
                    ),
                )

            if data_classification:
                query = query.filter(
                    ExtendedAuditLog.data_classification == data_classification,
                )

            if start_date:
                query = query.filter(ExtendedAuditLog.timestamp >= start_date)

            if end_date:
                query = query.filter(ExtendedAuditLog.timestamp <= end_date)

            # Count total
            total = query.count()

            # Apply pagination
            offset = (page - 1) * size
            audit_logs = (
                query.order_by(desc(ExtendedAuditLog.timestamp))
                .offset(offset)
                .limit(size)
                .all()
            )

            # Process results
            results = []
            for log in audit_logs:
                log_data = {
                    "id": str(log.id),
                    "event_id": log.event_id,
                    "event_type": log.event_type.value,
                    "event_category": log.event_category.value,
                    "severity": log.severity.value,
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": log.user_id,
                    "username": log.username,
                    "ip_address": log.ip_address,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "resource_name": log.resource_name,
                    "action": log.action,
                    "action_result": log.action_result,
                    "error_message": log.error_message,
                    "tags": log.tags,
                    "compliance_frameworks": log.compliance_frameworks,
                    "data_classification": (
                        log.data_classification.value
                        if log.data_classification
                        else None
                    ),
                    "threat_level": log.threat_level,
                    "risk_score": log.risk_score,
                    "security_impact": log.security_impact,
                    "organization_id": log.organization_id,
                    "department": log.department,
                    "project": log.project,
                }

                if include_context and log.context:
                    log_data["context"] = log.context

                if include_metadata and log.metadata:
                    log_data["metadata"] = log.metadata

                results.append(log_data)

            return {
                "audit_logs": results,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            }

        except Exception as e:
            logger.exception(f"Failed to get audit logs: {str(e)}")
            raise AuditError(f"Failed to get audit logs: {str(e)}")

    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        report_type: str = "audit",
        report_period: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: str | None = None,
    ) -> ComplianceReport:
        """Generate compliance report for specified framework."""
        try:
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Get relevant audit logs
            query = self.db.query(ExtendedAuditLog).filter(
                and_(
                    ExtendedAuditLog.compliance_frameworks.contains([framework.value]),
                    ExtendedAuditLog.timestamp >= start_date,
                    ExtendedAuditLog.timestamp <= end_date,
                ),
            )

            if user_id:
                query = query.filter(ExtendedAuditLog.user_id == user_id)

            audit_logs = query.all()

            # Generate findings
            findings = await self._analyze_compliance_findings(audit_logs, framework)

            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                findings,
                framework,
            )

            # Calculate metrics
            metrics = await self._calculate_compliance_metrics(audit_logs, framework)

            # Create compliance report
            report = ComplianceReport(
                name=f"{framework.value.upper()} {report_type.title()} Report - {report_period or 'Custom Period'}",
                description=f"Compliance report for {framework.value.upper()} framework",
                framework=framework,
                report_type=report_type,
                report_period=report_period,
                findings=findings,
                recommendations=recommendations,
                metrics=metrics,
                status="draft",
                generated_at=datetime.now(),
            )

            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)

            logger.info(f"Generated compliance report: {report.name}")
            return report

        except Exception as e:
            logger.exception(f"Failed to generate compliance report: {str(e)}")
            raise ComplianceError(f"Failed to generate compliance report: {str(e)}")

    async def cleanup_expired_logs(self) -> int:
        """Clean up expired audit logs based on retention rules."""
        try:
            cleaned_count = 0

            # Get all retention rules
            retention_rules = (
                self.db.query(AuditRetentionRule)
                .filter(AuditRetentionRule.enabled)
                .all()
            )

            for rule in retention_rules:
                # Calculate expiry date
                expiry_date = datetime.now() - timedelta(days=rule.retention_days)

                # Build query based on rule criteria
                query = self.db.query(ExtendedAuditLog).filter(
                    ExtendedAuditLog.timestamp < expiry_date,
                )

                if rule.event_types:
                    query = query.filter(
                        ExtendedAuditLog.event_type.in_(rule.event_types),
                    )

                if rule.event_categories:
                    query = query.filter(
                        ExtendedAuditLog.event_category.in_(rule.event_categories),
                    )

                if rule.severity_levels:
                    query = query.filter(
                        ExtendedAuditLog.severity.in_(rule.severity_levels),
                    )

                if rule.compliance_frameworks:
                    query = query.filter(
                        ExtendedAuditLog.compliance_frameworks.overlap(
                            rule.compliance_frameworks,
                        ),
                    )

                if rule.data_classification:
                    query = query.filter(
                        ExtendedAuditLog.data_classification
                        == rule.data_classification,
                    )

                # Exclude logs under legal hold
                query = query.filter(not ExtendedAuditLog.legal_hold)

                # Get logs to delete
                logs_to_delete = query.all()

                # Apply action based on rule
                if rule.action_on_expiry == "delete":
                    for log in logs_to_delete:
                        self.db.delete(log)
                        cleaned_count += 1
                elif rule.action_on_expiry == "archive":
                    await self._archive_logs(logs_to_delete, rule)
                    cleaned_count += len(logs_to_delete)
                elif rule.action_on_expiry == "anonymize":
                    for log in logs_to_delete:
                        log.username = "ANONYMIZED"
                        log.ip_address = "ANONYMIZED"
                        log.user_agent = "ANONYMIZED"
                        log.context = {}
                        log.metadata = {}
                        cleaned_count += 1

            self.db.commit()
            logger.info(f"Cleaned up {cleaned_count} expired audit logs")
            return cleaned_count

        except Exception as e:
            logger.exception(f"Failed to cleanup expired logs: {str(e)}")
            raise AuditError(f"Failed to cleanup expired logs: {str(e)}")

    async def get_audit_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        """Get comprehensive audit statistics."""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Base query
            query = self.db.query(ExtendedAuditLog).filter(
                and_(
                    ExtendedAuditLog.timestamp >= start_date,
                    ExtendedAuditLog.timestamp <= end_date,
                ),
            )

            if organization_id:
                query = query.filter(
                    ExtendedAuditLog.organization_id == organization_id,
                )

            # Total events
            total_events = query.count()

            # Events by category
            events_by_category = {}
            for category in AuditEventCategory:
                count = query.filter(
                    ExtendedAuditLog.event_category == category,
                ).count()
                if count > 0:
                    events_by_category[category.value] = count

            # Events by severity
            events_by_severity = {}
            for severity in AuditSeverity:
                count = query.filter(ExtendedAuditLog.severity == severity).count()
                if count > 0:
                    events_by_severity[severity.value] = count

            # Top users by activity
            top_users = (
                self.db.query(
                    ExtendedAuditLog.username,
                    func.count(ExtendedAuditLog.id).label("event_count"),
                )
                .filter(
                    and_(
                        ExtendedAuditLog.timestamp >= start_date,
                        ExtendedAuditLog.timestamp <= end_date,
                        ExtendedAuditLog.username.isnot(None),
                    ),
                )
                .group_by(ExtendedAuditLog.username)
                .order_by(desc("event_count"))
                .limit(10)
                .all()
            )

            # Compliance statistics
            compliance_stats = {}
            for framework in ComplianceFramework:
                count = query.filter(
                    ExtendedAuditLog.compliance_frameworks.contains([framework.value]),
                ).count()
                if count > 0:
                    compliance_stats[framework.value] = count

            # Security incidents
            security_incidents = query.filter(
                ExtendedAuditLog.event_category == AuditEventCategory.SECURITY,
            ).count()

            # Failed actions
            failed_actions = query.filter(
                ExtendedAuditLog.action_result == "failure",
            ).count()

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "total_events": total_events,
                "events_by_category": events_by_category,
                "events_by_severity": events_by_severity,
                "top_users": [
                    {"username": user.username, "event_count": user.event_count}
                    for user in top_users
                ],
                "compliance_stats": compliance_stats,
                "security_incidents": security_incidents,
                "failed_actions": failed_actions,
                "success_rate": (
                    ((total_events - failed_actions) / total_events * 100)
                    if total_events > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.exception(f"Failed to get audit statistics: {str(e)}")
            raise AuditError(f"Failed to get audit statistics: {str(e)}")

    # Private methods
    async def _should_log_event(
        self,
        event_type: AuditEventType,
        event_category: AuditEventCategory,
        user: User | None,
    ) -> bool:
        """Check if event should be logged based on audit policies."""
        try:
            # Get applicable policies
            policies = (
                self.db.query(AuditPolicy).filter(AuditPolicy.enabled).all()
            )

            for policy in policies:
                # Check if policy applies to this event
                if policy.event_types and event_type.value not in policy.event_types:
                    continue

                if (
                    policy.event_categories
                    and event_category.value not in policy.event_categories
                ):
                    continue

                if policy.user_roles and user and user.role not in policy.user_roles:
                    continue

                # Policy applies, check if we should log
                return True

            # Default: log if no policies or no policies apply
            return True

        except Exception as e:
            logger.exception(f"Failed to check audit policy: {str(e)}")
            return True  # Default to logging on error

    async def _apply_retention_rules(self, audit_log: ExtendedAuditLog) -> None:
        """Apply retention rules to audit log."""
        try:
            rules = (
                self.db.query(AuditRetentionRule)
                .filter(AuditRetentionRule.enabled)
                .all()
            )

            for rule in rules:
                # Check if rule applies
                if (
                    rule.event_types
                    and audit_log.event_type.value not in rule.event_types
                ):
                    continue

                if (
                    rule.event_categories
                    and audit_log.event_category.value not in rule.event_categories
                ):
                    continue

                if (
                    rule.severity_levels
                    and audit_log.severity.value not in rule.severity_levels
                ):
                    continue

                if rule.compliance_frameworks and audit_log.compliance_frameworks:
                    if not any(
                        fw in rule.compliance_frameworks
                        for fw in audit_log.compliance_frameworks
                    ):
                        continue

                if (
                    rule.data_classification
                    and audit_log.data_classification != rule.data_classification
                ):
                    continue

                # Rule applies, set retention period
                audit_log.retention_period = rule.retention_days
                audit_log.legal_hold = rule.legal_hold
                break

        except Exception as e:
            logger.exception(f"Failed to apply retention rules: {str(e)}")

    async def _check_alerts(self, audit_log: ExtendedAuditLog) -> None:
        """Check if audit log triggers any alerts."""
        try:
            alerts = self.db.query(AuditAlert).filter(AuditAlert.enabled).all()

            for alert in alerts:
                # Check if alert criteria match
                if (
                    alert.event_types
                    and audit_log.event_type.value not in alert.event_types
                ):
                    continue

                if (
                    alert.severity_levels
                    and audit_log.severity.value not in alert.severity_levels
                ):
                    continue

                # Check threshold
                key = f"{self.alert_prefix}{alert.id}"
                current_count = self.redis_client.get(key)

                current_count = 0 if current_count is None else int(current_count)

                current_count += 1

                # Set/update counter with expiry
                self.redis_client.setex(key, alert.threshold_period, current_count)

                # Check if threshold exceeded
                if current_count >= alert.threshold_count:
                    await self._trigger_alert(alert, audit_log, current_count)

        except Exception as e:
            logger.exception(f"Failed to check alerts: {str(e)}")

    async def _trigger_alert(
        self,
        alert: AuditAlert,
        audit_log: ExtendedAuditLog,
        count: int,
    ) -> None:
        """Trigger an audit alert."""
        try:
            # Update alert statistics
            alert.last_triggered = datetime.now()
            alert.trigger_count += 1
            self.db.commit()

            # Send notifications (placeholder for actual implementation)
            logger.warning(
                f"Audit alert triggered: {alert.name} - {count} events in {alert.threshold_period}s",
            )

            # Here you would implement actual notification logic:
            # - Email notifications
            # - Slack webhooks
            # - SMS alerts
            # - Webhook calls

        except Exception as e:
            logger.exception(f"Failed to trigger alert: {str(e)}")

    async def _cache_audit_event(self, audit_log: ExtendedAuditLog) -> None:
        """Cache audit event for performance."""
        try:
            key = f"{self.cache_prefix}{audit_log.event_id}"
            data = {
                "event_type": audit_log.event_type.value,
                "user_id": audit_log.user_id,
                "timestamp": audit_log.timestamp.isoformat(),
                "severity": audit_log.severity.value,
            }

            # Cache for 1 hour
            self.redis_client.setex(key, 3600, json.dumps(data))

        except Exception as e:
            logger.exception(f"Failed to cache audit event: {str(e)}")

    async def _analyze_compliance_findings(
        self,
        audit_logs: list[ExtendedAuditLog],
        framework: ComplianceFramework,
    ) -> list[dict[str, Any]]:
        """Analyze audit logs for compliance findings."""
        findings = []

        # Example findings analysis (customize based on framework requirements)
        failed_actions = [log for log in audit_logs if log.action_result == "failure"]
        security_events = [
            log
            for log in audit_logs
            if log.event_category == AuditEventCategory.SECURITY
        ]
        high_severity_events = [log for log in audit_logs if log.is_high_severity]

        if failed_actions:
            findings.append(
                {
                    "type": "failed_actions",
                    "severity": "medium",
                    "description": f"{len(failed_actions)} failed actions detected",
                    "count": len(failed_actions),
                    "recommendation": "Review failed actions and investigate root causes",
                },
            )

        if security_events:
            findings.append(
                {
                    "type": "security_events",
                    "severity": "high",
                    "description": f"{len(security_events)} security events detected",
                    "count": len(security_events),
                    "recommendation": "Investigate security events and implement additional controls",
                },
            )

        if high_severity_events:
            findings.append(
                {
                    "type": "high_severity_events",
                    "severity": "critical",
                    "description": f"{len(high_severity_events)} high severity events detected",
                    "count": len(high_severity_events),
                    "recommendation": "Immediate attention required for high severity events",
                },
            )

        return findings

    async def _generate_compliance_recommendations(
        self,
        findings: list[dict[str, Any]],
        framework: ComplianceFramework,
    ) -> list[dict[str, Any]]:
        """Generate compliance recommendations based on findings."""
        recommendations = []

        for finding in findings:
            if finding["severity"] in ["high", "critical"]:
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "immediate_review",
                        "description": finding["recommendation"],
                        "deadline": "immediate",
                    },
                )
            elif finding["severity"] == "medium":
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "scheduled_review",
                        "description": finding["recommendation"],
                        "deadline": "within_30_days",
                    },
                )

        return recommendations

    async def _calculate_compliance_metrics(
        self,
        audit_logs: list[ExtendedAuditLog],
        framework: ComplianceFramework,
    ) -> dict[str, Any]:
        """Calculate compliance metrics."""
        total_events = len(audit_logs)
        failed_events = len(
            [log for log in audit_logs if log.action_result == "failure"],
        )
        security_events = len(
            [
                log
                for log in audit_logs
                if log.event_category == AuditEventCategory.SECURITY
            ],
        )

        return {
            "total_events": total_events,
            "failed_events": failed_events,
            "security_events": security_events,
            "success_rate": (
                ((total_events - failed_events) / total_events * 100)
                if total_events > 0
                else 0
            ),
            "security_incident_rate": (
                (security_events / total_events * 100) if total_events > 0 else 0
            ),
        }

    async def _archive_logs(
        self,
        logs: list[ExtendedAuditLog],
        rule: AuditRetentionRule,
    ) -> None:
        """Archive audit logs for long-term storage."""
        try:
            # Create archive entry
            archive = AuditArchive(
                archive_name=f"audit_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                archive_period=f"{logs[0].timestamp.strftime('%Y-%m')} to {logs[-1].timestamp.strftime('%Y-%m')}",
                start_date=logs[0].timestamp,
                end_date=logs[-1].timestamp,
                record_count=len(logs),
                status="archiving",
            )

            self.db.add(archive)
            self.db.commit()

            # Here you would implement actual archiving logic:
            # - Export to file (CSV, JSON, etc.)
            # - Upload to cloud storage (S3, etc.)
            # - Compress data
            # - Update archive status

            logger.info(f"Archived {len(logs)} audit logs")

        except Exception as e:
            logger.exception(f"Failed to archive logs: {str(e)}")
            raise AuditError(f"Failed to archive logs: {str(e)}")


# Global audit service instance
audit_service = None


def get_audit_service(db: Session) -> AuditService:
    """Get audit service instance."""
    global audit_service
    if audit_service is None:
        audit_service = AuditService(db)
    return audit_service
