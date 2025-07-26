"""
Main audit service for the ConvoSphere platform.

This service provides the main interface for audit functionality.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from .audit_alerts import AlertManager
from .audit_compliance import ComplianceChecker
from .audit_logger import AuditLogger
from .audit_policy import AuditPolicyManager
from .audit_retention import RetentionManager


class AuditService:
    """Main audit service that coordinates all audit functionality."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = AuditLogger(db)
        self.policy_manager = AuditPolicyManager(db)
        self.compliance_checker = ComplianceChecker(db)
        self.alert_manager = AlertManager(db)
        self.retention_manager = RetentionManager(db)

    def log_event(self, event_type: str, user_id: int, details: dict[str, Any]) -> bool:
        """Log an audit event."""
        return self.logger.log_event(event_type, user_id, details)

    def check_compliance(self, action: str, user_id: int) -> bool:
        """Check if an action complies with audit policies."""
        return self.compliance_checker.check_compliance(action, user_id)

    def create_alert(self, alert_type: str, message: str, severity: str) -> bool:
        """Create an audit alert."""
        return self.alert_manager.create_alert(alert_type, message, severity)

    def apply_retention_policies(self) -> int:
        """Apply retention policies to audit logs."""
        return self.retention_manager.apply_policies()

    def get_audit_report(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Generate an audit report for the specified period."""
        return self.logger.generate_report(start_date, end_date)
