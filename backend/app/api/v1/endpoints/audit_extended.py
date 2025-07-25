"""
Extended audit API endpoints.

This module provides comprehensive API endpoints for audit logging,
compliance reporting, and audit management.
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit_extended import (
    AuditAlert,
    AuditArchive,
    AuditEventCategory,
    AuditEventType,
    AuditPolicy,
    AuditRetentionRule,
    ComplianceFramework,
    ComplianceReport,
    DataClassification,
)
from app.models.user import User, UserRole
from app.schemas.audit_extended import (
    AuditAlertCreate,
    AuditAlertListResponse,
    AuditAlertResponse,
    AuditAlertUpdate,
    AuditArchiveListResponse,
    AuditArchiveResponse,
    AuditArchiveUpdate,
    AuditLogExportParams,
    AuditLogExportResponse,
    AuditLogListResponse,
    AuditLogUpdate,
    AuditPolicyCreate,
    AuditPolicyListResponse,
    AuditPolicyResponse,
    AuditPolicyUpdate,
    AuditStatisticsResponse,
    ComplianceReportCreate,
    ComplianceReportListResponse,
    ComplianceReportParams,
    ComplianceReportResponse,
    ComplianceReportUpdate,
    RetentionRuleCreate,
    RetentionRuleListResponse,
    RetentionRuleResponse,
    RetentionRuleUpdate,
)
from app.services.audit_service import get_audit_service
from app.utils.exceptions import AuditError, ComplianceError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


# Audit Log endpoints
@router.get("/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    user_id: str | None = Query(None, description="Filter by user ID"),
    event_type: AuditEventType | None = Query(
        None,
        description="Filter by event type",
    ),
    event_category: AuditEventCategory | None = Query(
        None,
        description="Filter by event category",
    ),
    severity: str | None = Query(None, description="Filter by severity level"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: str | None = Query(None, description="Filter by resource ID"),
    compliance_framework: ComplianceFramework | None = Query(
        None,
        description="Filter by compliance framework",
    ),
    data_classification: DataClassification | None = Query(
        None,
        description="Filter by data classification",
    ),
    start_date: datetime | None = Query(
        None,
        description="Start date for filtering",
    ),
    end_date: datetime | None = Query(None, description="End date for filtering"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    include_context: bool = Query(True, description="Include context in response"),
    include_metadata: bool = Query(True, description="Include metadata in response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit logs with filtering and pagination."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            # Regular users can only see their own audit logs
            user_id = str(current_user.id)

        audit_service = get_audit_service(db)

        # Convert severity string to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid severity level")

        return await audit_service.get_audit_logs(
            user_id=user_id,
            event_type=event_type,
            event_category=event_category,
            severity=severity_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            compliance_framework=compliance_framework,
            data_classification=data_classification,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size,
            include_context=include_context,
            include_metadata=include_metadata,
        )


    except AuditError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to get audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/logs/{log_id}", response_model=dict[str, Any])
async def get_audit_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific audit log by ID."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            # Regular users can only see their own audit logs
            from app.models.audit_extended import ExtendedAuditLog

            audit_log = (
                db.query(ExtendedAuditLog)
                .filter(
                    ExtendedAuditLog.id == log_id,
                    ExtendedAuditLog.user_id == str(current_user.id),
                )
                .first()
            )
        else:
            from app.models.audit_extended import ExtendedAuditLog

            audit_log = (
                db.query(ExtendedAuditLog).filter(ExtendedAuditLog.id == log_id).first()
            )

        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")

        return {
            "id": str(audit_log.id),
            "event_id": audit_log.event_id,
            "event_type": audit_log.event_type.value,
            "event_category": audit_log.event_category.value,
            "severity": audit_log.severity.value,
            "timestamp": audit_log.timestamp.isoformat(),
            "user_id": audit_log.user_id,
            "username": audit_log.username,
            "session_id": audit_log.session_id,
            "ip_address": audit_log.ip_address,
            "user_agent": audit_log.user_agent,
            "resource_type": audit_log.resource_type,
            "resource_id": audit_log.resource_id,
            "resource_name": audit_log.resource_name,
            "action": audit_log.action,
            "action_result": audit_log.action_result,
            "error_message": audit_log.error_message,
            "context": audit_log.context,
            "metadata": audit_log.metadata,
            "tags": audit_log.tags,
            "compliance_frameworks": audit_log.compliance_frameworks,
            "data_classification": (
                audit_log.data_classification.value
                if audit_log.data_classification
                else None
            ),
            "threat_level": audit_log.threat_level,
            "risk_score": audit_log.risk_score,
            "security_impact": audit_log.security_impact,
            "organization_id": audit_log.organization_id,
            "department": audit_log.department,
            "project": audit_log.project,
            "retention_period": audit_log.retention_period,
            "legal_hold": audit_log.legal_hold,
        }

    except Exception as e:
        logger.exception(f"Failed to get audit log: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/logs/{log_id}", response_model=dict[str, Any])
async def update_audit_log(
    log_id: UUID,
    log_update: AuditLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update audit log (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        from app.models.audit_extended import ExtendedAuditLog

        audit_log = (
            db.query(ExtendedAuditLog).filter(ExtendedAuditLog.id == log_id).first()
        )

        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")

        # Update fields
        if log_update.tags is not None:
            audit_log.tags = log_update.tags
        if log_update.context is not None:
            audit_log.context = log_update.context
        if log_update.metadata is not None:
            audit_log.metadata = log_update.metadata
        if log_update.legal_hold is not None:
            audit_log.legal_hold = log_update.legal_hold

        db.commit()
        db.refresh(audit_log)

        return {"message": "Audit log updated successfully", "id": str(audit_log.id)}

    except Exception as e:
        logger.exception(f"Failed to update audit log: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    start_date: datetime | None = Query(
        None,
        description="Start date for statistics",
    ),
    end_date: datetime | None = Query(None, description="End date for statistics"),
    organization_id: str | None = Query(
        None,
        description="Organization ID for filtering",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive audit statistics."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        audit_service = get_audit_service(db)

        # Regular users can only see statistics for their organization
        if current_user.role == UserRole.ADMIN:
            organization_id = str(current_user.organization_id)

        return await audit_service.get_audit_statistics(
            start_date=start_date,
            end_date=end_date,
            organization_id=organization_id,
        )


    except AuditError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to get audit statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/export", response_model=AuditLogExportResponse)
async def export_audit_logs(
    export_params: AuditLogExportParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export audit logs (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # This would implement actual export logic
        # For now, return a placeholder response
        export_id = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return AuditLogExportResponse(
            export_id=export_id,
            format=export_params.format,
            file_url=None,  # Would be set after actual export
            file_size=None,
            record_count=0,  # Would be calculated during export
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
        )

    except Exception as e:
        logger.exception(f"Failed to export audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Audit Policy endpoints
@router.get("/policies", response_model=AuditPolicyListResponse)
async def get_audit_policies(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit policies (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        policies = db.query(AuditPolicy).offset((page - 1) * size).limit(size).all()
        total = db.query(AuditPolicy).count()

        return AuditPolicyListResponse(
            policies=policies,
            total=total,
        )

    except Exception as e:
        logger.exception(f"Failed to get audit policies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/policies",
    response_model=AuditPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_policy(
    policy_data: AuditPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create audit policy (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        policy = AuditPolicy(**policy_data.dict())
        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    except Exception as e:
        logger.exception(f"Failed to create audit policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/policies/{policy_id}", response_model=AuditPolicyResponse)
async def get_audit_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific audit policy (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        policy = db.query(AuditPolicy).filter(AuditPolicy.id == policy_id).first()

        if not policy:
            raise HTTPException(status_code=404, detail="Audit policy not found")

        return policy

    except Exception as e:
        logger.exception(f"Failed to get audit policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/policies/{policy_id}", response_model=AuditPolicyResponse)
async def update_audit_policy(
    policy_id: UUID,
    policy_update: AuditPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update audit policy (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        policy = db.query(AuditPolicy).filter(AuditPolicy.id == policy_id).first()

        if not policy:
            raise HTTPException(status_code=404, detail="Audit policy not found")

        # Update fields
        update_data = policy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)

        db.commit()
        db.refresh(policy)

        return policy

    except Exception as e:
        logger.exception(f"Failed to update audit policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete audit policy (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        policy = db.query(AuditPolicy).filter(AuditPolicy.id == policy_id).first()

        if not policy:
            raise HTTPException(status_code=404, detail="Audit policy not found")

        db.delete(policy)
        db.commit()

    except Exception as e:
        logger.exception(f"Failed to delete audit policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Retention Rule endpoints
@router.get("/retention-rules", response_model=RetentionRuleListResponse)
async def get_retention_rules(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get retention rules (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        rules = db.query(AuditRetentionRule).offset((page - 1) * size).limit(size).all()
        total = db.query(AuditRetentionRule).count()

        return RetentionRuleListResponse(
            rules=rules,
            total=total,
        )

    except Exception as e:
        logger.exception(f"Failed to get retention rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/retention-rules",
    response_model=RetentionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_retention_rule(
    rule_data: RetentionRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create retention rule (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        rule = AuditRetentionRule(**rule_data.dict())
        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    except Exception as e:
        logger.exception(f"Failed to create retention rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/retention-rules/{rule_id}", response_model=RetentionRuleResponse)
async def get_retention_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific retention rule (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        rule = (
            db.query(AuditRetentionRule)
            .filter(AuditRetentionRule.id == rule_id)
            .first()
        )

        if not rule:
            raise HTTPException(status_code=404, detail="Retention rule not found")

        return rule

    except Exception as e:
        logger.exception(f"Failed to get retention rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/retention-rules/{rule_id}", response_model=RetentionRuleResponse)
async def update_retention_rule(
    rule_id: UUID,
    rule_update: RetentionRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update retention rule (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        rule = (
            db.query(AuditRetentionRule)
            .filter(AuditRetentionRule.id == rule_id)
            .first()
        )

        if not rule:
            raise HTTPException(status_code=404, detail="Retention rule not found")

        # Update fields
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        db.commit()
        db.refresh(rule)

        return rule

    except Exception as e:
        logger.exception(f"Failed to update retention rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/retention-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_retention_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete retention rule (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        rule = (
            db.query(AuditRetentionRule)
            .filter(AuditRetentionRule.id == rule_id)
            .first()
        )

        if not rule:
            raise HTTPException(status_code=404, detail="Retention rule not found")

        db.delete(rule)
        db.commit()

    except Exception as e:
        logger.exception(f"Failed to delete retention rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Compliance Report endpoints
@router.get("/compliance-reports", response_model=ComplianceReportListResponse)
async def get_compliance_reports(
    framework: ComplianceFramework | None = Query(
        None,
        description="Filter by framework",
    ),
    status: str | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance reports (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        query = db.query(ComplianceReport)

        if framework:
            query = query.filter(ComplianceReport.framework == framework)

        if status:
            query = query.filter(ComplianceReport.status == status)

        reports = query.offset((page - 1) * size).limit(size).all()
        total = query.count()

        return ComplianceReportListResponse(
            reports=reports,
            total=total,
        )

    except Exception as e:
        logger.exception(f"Failed to get compliance reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/compliance-reports",
    response_model=ComplianceReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_compliance_report(
    report_data: ComplianceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create compliance report (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = ComplianceReport(**report_data.dict())
        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    except Exception as e:
        logger.exception(f"Failed to create compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/compliance-reports/generate", response_model=ComplianceReportResponse)
async def generate_compliance_report(
    report_params: ComplianceReportParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate compliance report (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        audit_service = get_audit_service(db)

        return await audit_service.generate_compliance_report(
            framework=report_params.framework,
            report_type=report_params.report_type,
            report_period=report_params.report_period,
            start_date=report_params.start_date,
            end_date=report_params.end_date,
            user_id=report_params.user_id,
        )


    except ComplianceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to generate compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/compliance-reports/{report_id}", response_model=ComplianceReportResponse)
async def get_compliance_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific compliance report (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = (
            db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        )

        if not report:
            raise HTTPException(status_code=404, detail="Compliance report not found")

        return report

    except Exception as e:
        logger.exception(f"Failed to get compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/compliance-reports/{report_id}", response_model=ComplianceReportResponse)
async def update_compliance_report(
    report_id: UUID,
    report_update: ComplianceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update compliance report (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = (
            db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        )

        if not report:
            raise HTTPException(status_code=404, detail="Compliance report not found")

        # Update fields
        update_data = report_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        db.commit()
        db.refresh(report)

        return report

    except Exception as e:
        logger.exception(f"Failed to update compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/compliance-reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_compliance_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete compliance report (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = (
            db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        )

        if not report:
            raise HTTPException(status_code=404, detail="Compliance report not found")

        db.delete(report)
        db.commit()

    except Exception as e:
        logger.exception(f"Failed to delete compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Audit Alert endpoints
@router.get("/alerts", response_model=AuditAlertListResponse)
async def get_audit_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit alerts (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alerts = db.query(AuditAlert).offset((page - 1) * size).limit(size).all()
        total = db.query(AuditAlert).count()

        return AuditAlertListResponse(
            alerts=alerts,
            total=total,
        )

    except Exception as e:
        logger.exception(f"Failed to get audit alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/alerts",
    response_model=AuditAlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_alert(
    alert_data: AuditAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create audit alert (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alert = AuditAlert(**alert_data.dict())
        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    except Exception as e:
        logger.exception(f"Failed to create audit alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/alerts/{alert_id}", response_model=AuditAlertResponse)
async def get_audit_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific audit alert (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alert = db.query(AuditAlert).filter(AuditAlert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Audit alert not found")

        return alert

    except Exception as e:
        logger.exception(f"Failed to get audit alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/alerts/{alert_id}", response_model=AuditAlertResponse)
async def update_audit_alert(
    alert_id: UUID,
    alert_update: AuditAlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update audit alert (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alert = db.query(AuditAlert).filter(AuditAlert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Audit alert not found")

        # Update fields
        update_data = alert_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        db.commit()
        db.refresh(alert)

        return alert

    except Exception as e:
        logger.exception(f"Failed to update audit alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete audit alert (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        alert = db.query(AuditAlert).filter(AuditAlert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Audit alert not found")

        db.delete(alert)
        db.commit()

    except Exception as e:
        logger.exception(f"Failed to delete audit alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Audit Archive endpoints
@router.get("/archives", response_model=AuditArchiveListResponse)
async def get_audit_archives(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit archives (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        archives = db.query(AuditArchive).offset((page - 1) * size).limit(size).all()
        total = db.query(AuditArchive).count()

        return AuditArchiveListResponse(
            archives=archives,
            total=total,
        )

    except Exception as e:
        logger.exception(f"Failed to get audit archives: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/archives/{archive_id}", response_model=AuditArchiveResponse)
async def get_audit_archive(
    archive_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific audit archive (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        archive = db.query(AuditArchive).filter(AuditArchive.id == archive_id).first()

        if not archive:
            raise HTTPException(status_code=404, detail="Audit archive not found")

        return archive

    except Exception as e:
        logger.exception(f"Failed to get audit archive: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/archives/{archive_id}", response_model=AuditArchiveResponse)
async def update_audit_archive(
    archive_id: UUID,
    archive_update: AuditArchiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update audit archive (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        archive = db.query(AuditArchive).filter(AuditArchive.id == archive_id).first()

        if not archive:
            raise HTTPException(status_code=404, detail="Audit archive not found")

        # Update fields
        update_data = archive_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(archive, field, value)

        db.commit()
        db.refresh(archive)

        return archive

    except Exception as e:
        logger.exception(f"Failed to update audit archive: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Maintenance endpoints
@router.post("/maintenance/cleanup", response_model=dict[str, Any])
async def cleanup_expired_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clean up expired audit logs (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        audit_service = get_audit_service(db)
        cleaned_count = await audit_service.cleanup_expired_logs()

        return {
            "message": f"Successfully cleaned up {cleaned_count} expired audit logs",
            "cleaned_count": cleaned_count,
        }

    except AuditError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to cleanup expired logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/maintenance/health", response_model=dict[str, Any])
async def audit_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Health check for audit system (admin only)."""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Basic health checks
        from app.models.audit_extended import ExtendedAuditLog

        total_logs = db.query(ExtendedAuditLog).count()
        recent_logs = (
            db.query(ExtendedAuditLog)
            .filter(ExtendedAuditLog.timestamp >= datetime.now() - timedelta(hours=1))
            .count()
        )

        return {
            "status": "healthy",
            "total_logs": total_logs,
            "recent_logs_1h": recent_logs,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to perform health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
