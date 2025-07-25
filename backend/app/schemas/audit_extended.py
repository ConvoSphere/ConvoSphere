"""
Pydantic schemas for extended audit system.

This module provides comprehensive schemas for audit logging,
compliance reporting, and audit management.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.audit_extended import (
    AuditEventCategory,
    AuditEventType,
    AuditSeverity,
    ComplianceFramework,
    DataClassification,
)
from pydantic import BaseModel, Field, field_validator


# Base schemas
class AuditLogBase(BaseModel):
    """Base schema for audit log data."""

    event_type: AuditEventType
    event_category: AuditEventCategory
    severity: AuditSeverity = AuditSeverity.INFO
    resource_type: str | None = None
    resource_id: str | None = None
    resource_name: str | None = None
    action: str | None = None
    context: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None
    threat_level: str | None = None
    risk_score: int | None = Field(None, ge=0, le=100)
    security_impact: str | None = None
    organization_id: str | None = None
    department: str | None = None
    project: str | None = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log entries."""



class AuditLogUpdate(BaseModel):
    """Schema for updating audit log entries."""

    tags: list[str] | None = None
    context: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    legal_hold: bool | None = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""

    id: UUID
    event_id: str
    timestamp: datetime
    event_duration: int | None = None
    user_id: str | None = None
    username: str | None = None
    session_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    action_result: str | None = None
    error_message: str | None = None
    retention_period: int | None = None
    legal_hold: bool = False

    class Config:
        from_attributes = True


# Audit Policy schemas
class AuditPolicyBase(BaseModel):
    """Base schema for audit policy."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    resource_types: list[str] | None = None
    user_roles: list[str] | None = None
    enabled: bool = True
    log_success: bool = True
    log_failure: bool = True
    include_context: bool = True
    include_metadata: bool = True
    retention_days: int = Field(365, ge=1, le=3650)
    archive_after_days: int = Field(90, ge=1, le=365)
    legal_hold_retention: int = Field(2555, ge=1, le=3650)
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None


class AuditPolicyCreate(AuditPolicyBase):
    """Schema for creating audit policies."""



class AuditPolicyUpdate(BaseModel):
    """Schema for updating audit policies."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    resource_types: list[str] | None = None
    user_roles: list[str] | None = None
    enabled: bool | None = None
    log_success: bool | None = None
    log_failure: bool | None = None
    include_context: bool | None = None
    include_metadata: bool | None = None
    retention_days: int | None = Field(None, ge=1, le=3650)
    archive_after_days: int | None = Field(None, ge=1, le=365)
    legal_hold_retention: int | None = Field(None, ge=1, le=3650)
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None


class AuditPolicyResponse(AuditPolicyBase):
    """Schema for audit policy responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# Retention Rule schemas
class RetentionRuleBase(BaseModel):
    """Base schema for retention rules."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    severity_levels: list[str] | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None
    retention_days: int = Field(..., ge=1, le=3650)
    archive_days: int | None = Field(None, ge=1, le=365)
    legal_hold: bool = False
    action_on_expiry: str = Field("delete", regex="^(delete|archive|anonymize)$")
    notify_before_expiry: int | None = Field(None, ge=1, le=30)
    enabled: bool = True


class RetentionRuleCreate(RetentionRuleBase):
    """Schema for creating retention rules."""



class RetentionRuleUpdate(BaseModel):
    """Schema for updating retention rules."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    severity_levels: list[str] | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None
    retention_days: int | None = Field(None, ge=1, le=3650)
    archive_days: int | None = Field(None, ge=1, le=365)
    legal_hold: bool | None = None
    action_on_expiry: str | None = Field(None, regex="^(delete|archive|anonymize)$")
    notify_before_expiry: int | None = Field(None, ge=1, le=30)
    enabled: bool | None = None


class RetentionRuleResponse(RetentionRuleBase):
    """Schema for retention rule responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# Compliance Report schemas
class ComplianceReportBase(BaseModel):
    """Base schema for compliance reports."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    framework: ComplianceFramework
    report_type: str = Field(..., min_length=1, max_length=100)
    report_period: str | None = None


class ComplianceReportCreate(ComplianceReportBase):
    """Schema for creating compliance reports."""



class ComplianceReportUpdate(BaseModel):
    """Schema for updating compliance reports."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    report_type: str | None = Field(None, min_length=1, max_length=100)
    report_period: str | None = None
    status: str | None = Field(None, regex="^(draft|review|approved|archived)$")
    findings: list[dict[str, Any]] | None = None
    recommendations: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None


class ComplianceReportResponse(ComplianceReportBase):
    """Schema for compliance report responses."""

    id: UUID
    findings: list[dict[str, Any]] | None = None
    recommendations: list[dict[str, Any]] | None = None
    metrics: dict[str, Any] | None = None
    status: str
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    generated_at: datetime | None = None

    class Config:
        from_attributes = True


# Audit Alert schemas
class AuditAlertBase(BaseModel):
    """Base schema for audit alerts."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    severity_levels: list[str] | None = None
    threshold_count: int = Field(1, ge=1, le=1000)
    threshold_period: int = Field(3600, ge=60, le=86400)  # 1 minute to 24 hours
    notification_channels: list[str] | None = None
    notification_recipients: list[str] | None = None
    escalation_rules: dict[str, Any] | None = None
    enabled: bool = True


class AuditAlertCreate(AuditAlertBase):
    """Schema for creating audit alerts."""



class AuditAlertUpdate(BaseModel):
    """Schema for updating audit alerts."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    event_types: list[str] | None = None
    severity_levels: list[str] | None = None
    threshold_count: int | None = Field(None, ge=1, le=1000)
    threshold_period: int | None = Field(None, ge=60, le=86400)
    notification_channels: list[str] | None = None
    notification_recipients: list[str] | None = None
    escalation_rules: dict[str, Any] | None = None
    enabled: bool | None = None


class AuditAlertResponse(AuditAlertBase):
    """Schema for audit alert responses."""

    id: UUID
    last_triggered: datetime | None = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# Audit Archive schemas
class AuditArchiveBase(BaseModel):
    """Base schema for audit archives."""

    archive_name: str = Field(..., min_length=1, max_length=255)
    archive_period: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    storage_location: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    compression_ratio: float | None = None
    record_count: int | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None


class AuditArchiveCreate(AuditArchiveBase):
    """Schema for creating audit archives."""



class AuditArchiveUpdate(BaseModel):
    """Schema for updating audit archives."""

    archive_name: str | None = Field(None, min_length=1, max_length=255)
    storage_location: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    compression_ratio: float | None = None
    status: str | None = Field(None, regex="^(archiving|completed|failed)$")
    archived_at: datetime | None = None
    retention_expiry: datetime | None = None


class AuditArchiveResponse(AuditArchiveBase):
    """Schema for audit archive responses."""

    id: UUID
    status: str
    archived_at: datetime | None = None
    retention_expiry: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# Search and Filter schemas
class AuditLogSearchParams(BaseModel):
    """Schema for audit log search parameters."""

    user_id: str | None = None
    event_type: AuditEventType | None = None
    event_category: AuditEventCategory | None = None
    severity: AuditSeverity | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    compliance_framework: ComplianceFramework | None = None
    data_classification: DataClassification | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    page: int = Field(1, ge=1)
    size: int = Field(100, ge=1, le=1000)
    include_context: bool = True
    include_metadata: bool = True


class AuditStatisticsParams(BaseModel):
    """Schema for audit statistics parameters."""

    start_date: datetime | None = None
    end_date: datetime | None = None
    organization_id: str | None = None


class ComplianceReportParams(BaseModel):
    """Schema for compliance report generation parameters."""

    framework: ComplianceFramework
    report_type: str = "audit"
    report_period: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    user_id: str | None = None


# Response schemas
class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list responses."""

    audit_logs: list[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


class AuditStatisticsResponse(BaseModel):
    """Schema for audit statistics responses."""

    period: dict[str, str]
    total_events: int
    events_by_category: dict[str, int]
    events_by_severity: dict[str, int]
    top_users: list[dict[str, Any]]
    compliance_stats: dict[str, int]
    security_incidents: int
    failed_actions: int
    success_rate: float


class AuditPolicyListResponse(BaseModel):
    """Schema for audit policy list responses."""

    policies: list[AuditPolicyResponse]
    total: int


class RetentionRuleListResponse(BaseModel):
    """Schema for retention rule list responses."""

    rules: list[RetentionRuleResponse]
    total: int


class ComplianceReportListResponse(BaseModel):
    """Schema for compliance report list responses."""

    reports: list[ComplianceReportResponse]
    total: int


class AuditAlertListResponse(BaseModel):
    """Schema for audit alert list responses."""

    alerts: list[AuditAlertResponse]
    total: int


class AuditArchiveListResponse(BaseModel):
    """Schema for audit archive list responses."""

    archives: list[AuditArchiveResponse]
    total: int


# Export schemas
class AuditLogExportParams(BaseModel):
    """Schema for audit log export parameters."""

    format: str = Field("json", regex="^(json|csv|xml)$")
    start_date: datetime | None = None
    end_date: datetime | None = None
    event_types: list[AuditEventType] | None = None
    event_categories: list[AuditEventCategory] | None = None
    severity_levels: list[AuditSeverity] | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    include_context: bool = True
    include_metadata: bool = True


class AuditLogExportResponse(BaseModel):
    """Schema for audit log export responses."""

    export_id: str
    format: str
    file_url: str | None = None
    file_size: int | None = None
    record_count: int
    created_at: datetime
    expires_at: datetime


# Notification schemas
class AuditNotificationConfig(BaseModel):
    """Schema for audit notification configuration."""

    email_enabled: bool = False
    email_recipients: list[str] | None = None
    slack_enabled: bool = False
    slack_webhook_url: str | None = None
    webhook_enabled: bool = False
    webhook_url: str | None = None
    sms_enabled: bool = False
    sms_recipients: list[str] | None = None


class AuditNotification(BaseModel):
    """Schema for audit notifications."""

    alert_id: UUID
    alert_name: str
    event_count: int
    threshold_period: int
    triggered_at: datetime
    events: list[dict[str, Any]]
    notification_channels: list[str]
    recipients: list[str]


# Validation schemas
class AuditLogValidation(BaseModel):
    """Schema for audit log validation."""

    event_type: AuditEventType
    event_category: AuditEventCategory
    severity: AuditSeverity
    resource_type: str | None = None
    compliance_frameworks: list[ComplianceFramework] | None = None
    data_classification: DataClassification | None = None

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, v):
        if v and len(v) > 100:
            raise ValueError("Resource type must be 100 characters or less")
        return v

    @field_validator("compliance_frameworks")
    @classmethod
    def validate_compliance_frameworks(cls, v):
        if v and len(v) > 10:
            raise ValueError("Maximum 10 compliance frameworks allowed")
        return v


class AuditPolicyValidation(BaseModel):
    """Schema for audit policy validation."""

    name: str
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    user_roles: list[str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 255:
            raise ValueError("Name must be between 1 and 255 characters")
        return v

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, v):
        if v:
            valid_types = [e.value for e in AuditEventType]
            for event_type in v:
                if event_type not in valid_types:
                    raise ValueError(f"Invalid event type: {event_type}")
        return v

    @field_validator("event_categories")
    @classmethod
    def validate_event_categories(cls, v):
        if v:
            valid_categories = [c.value for c in AuditEventCategory]
            for category in v:
                if category not in valid_categories:
                    raise ValueError(f"Invalid event category: {category}")
        return v
