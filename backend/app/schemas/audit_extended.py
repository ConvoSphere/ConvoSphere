"""
Pydantic schemas for extended audit system.

This module provides comprehensive schemas for audit logging,
compliance reporting, and audit management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.audit_extended import (
    AuditEventCategory,
    AuditEventType,
    AuditSeverity,
    ComplianceFramework,
    DataClassification,
)


# Base schemas
class AuditLogBase(BaseModel):
    """Base schema for audit log data."""
    event_type: AuditEventType
    event_category: AuditEventCategory
    severity: AuditSeverity = AuditSeverity.INFO
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    action: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None
    threat_level: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    security_impact: Optional[str] = None
    organization_id: Optional[str] = None
    department: Optional[str] = None
    project: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log entries."""
    pass


class AuditLogUpdate(BaseModel):
    """Schema for updating audit log entries."""
    tags: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    legal_hold: Optional[bool] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    id: UUID
    event_id: str
    timestamp: datetime
    event_duration: Optional[int] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action_result: Optional[str] = None
    error_message: Optional[str] = None
    retention_period: Optional[int] = None
    legal_hold: bool = False
    
    class Config:
        from_attributes = True


# Audit Policy schemas
class AuditPolicyBase(BaseModel):
    """Base schema for audit policy."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    user_roles: Optional[List[str]] = None
    enabled: bool = True
    log_success: bool = True
    log_failure: bool = True
    include_context: bool = True
    include_metadata: bool = True
    retention_days: int = Field(365, ge=1, le=3650)
    archive_after_days: int = Field(90, ge=1, le=365)
    legal_hold_retention: int = Field(2555, ge=1, le=3650)
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None


class AuditPolicyCreate(AuditPolicyBase):
    """Schema for creating audit policies."""
    pass


class AuditPolicyUpdate(BaseModel):
    """Schema for updating audit policies."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    user_roles: Optional[List[str]] = None
    enabled: Optional[bool] = None
    log_success: Optional[bool] = None
    log_failure: Optional[bool] = None
    include_context: Optional[bool] = None
    include_metadata: Optional[bool] = None
    retention_days: Optional[int] = Field(None, ge=1, le=3650)
    archive_after_days: Optional[int] = Field(None, ge=1, le=365)
    legal_hold_retention: Optional[int] = Field(None, ge=1, le=3650)
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None


class AuditPolicyResponse(AuditPolicyBase):
    """Schema for audit policy responses."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Retention Rule schemas
class RetentionRuleBase(BaseModel):
    """Base schema for retention rules."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None
    retention_days: int = Field(..., ge=1, le=3650)
    archive_days: Optional[int] = Field(None, ge=1, le=365)
    legal_hold: bool = False
    action_on_expiry: str = Field("delete", regex="^(delete|archive|anonymize)$")
    notify_before_expiry: Optional[int] = Field(None, ge=1, le=30)
    enabled: bool = True


class RetentionRuleCreate(RetentionRuleBase):
    """Schema for creating retention rules."""
    pass


class RetentionRuleUpdate(BaseModel):
    """Schema for updating retention rules."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None
    retention_days: Optional[int] = Field(None, ge=1, le=3650)
    archive_days: Optional[int] = Field(None, ge=1, le=365)
    legal_hold: Optional[bool] = None
    action_on_expiry: Optional[str] = Field(None, regex="^(delete|archive|anonymize)$")
    notify_before_expiry: Optional[int] = Field(None, ge=1, le=30)
    enabled: Optional[bool] = None


class RetentionRuleResponse(RetentionRuleBase):
    """Schema for retention rule responses."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Compliance Report schemas
class ComplianceReportBase(BaseModel):
    """Base schema for compliance reports."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    framework: ComplianceFramework
    report_type: str = Field(..., min_length=1, max_length=100)
    report_period: Optional[str] = None


class ComplianceReportCreate(ComplianceReportBase):
    """Schema for creating compliance reports."""
    pass


class ComplianceReportUpdate(BaseModel):
    """Schema for updating compliance reports."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: Optional[str] = Field(None, min_length=1, max_length=100)
    report_period: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(draft|review|approved|archived)$")
    findings: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None


class ComplianceReportResponse(ComplianceReportBase):
    """Schema for compliance report responses."""
    id: UUID
    findings: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Audit Alert schemas
class AuditAlertBase(BaseModel):
    """Base schema for audit alerts."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    threshold_count: int = Field(1, ge=1, le=1000)
    threshold_period: int = Field(3600, ge=60, le=86400)  # 1 minute to 24 hours
    notification_channels: Optional[List[str]] = None
    notification_recipients: Optional[List[str]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    enabled: bool = True


class AuditAlertCreate(AuditAlertBase):
    """Schema for creating audit alerts."""
    pass


class AuditAlertUpdate(BaseModel):
    """Schema for updating audit alerts."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    threshold_count: Optional[int] = Field(None, ge=1, le=1000)
    threshold_period: Optional[int] = Field(None, ge=60, le=86400)
    notification_channels: Optional[List[str]] = None
    notification_recipients: Optional[List[str]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class AuditAlertResponse(AuditAlertBase):
    """Schema for audit alert responses."""
    id: UUID
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Audit Archive schemas
class AuditArchiveBase(BaseModel):
    """Base schema for audit archives."""
    archive_name: str = Field(..., min_length=1, max_length=255)
    archive_period: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    storage_location: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    record_count: Optional[int] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None


class AuditArchiveCreate(AuditArchiveBase):
    """Schema for creating audit archives."""
    pass


class AuditArchiveUpdate(BaseModel):
    """Schema for updating audit archives."""
    archive_name: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_location: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    status: Optional[str] = Field(None, regex="^(archiving|completed|failed)$")
    archived_at: Optional[datetime] = None
    retention_expiry: Optional[datetime] = None


class AuditArchiveResponse(AuditArchiveBase):
    """Schema for audit archive responses."""
    id: UUID
    status: str
    archived_at: Optional[datetime] = None
    retention_expiry: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search and Filter schemas
class AuditLogSearchParams(BaseModel):
    """Schema for audit log search parameters."""
    user_id: Optional[str] = None
    event_type: Optional[AuditEventType] = None
    event_category: Optional[AuditEventCategory] = None
    severity: Optional[AuditSeverity] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    compliance_framework: Optional[ComplianceFramework] = None
    data_classification: Optional[DataClassification] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(100, ge=1, le=1000)
    include_context: bool = True
    include_metadata: bool = True


class AuditStatisticsParams(BaseModel):
    """Schema for audit statistics parameters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organization_id: Optional[str] = None


class ComplianceReportParams(BaseModel):
    """Schema for compliance report generation parameters."""
    framework: ComplianceFramework
    report_type: str = "audit"
    report_period: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None


# Response schemas
class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list responses."""
    audit_logs: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


class AuditStatisticsResponse(BaseModel):
    """Schema for audit statistics responses."""
    period: Dict[str, str]
    total_events: int
    events_by_category: Dict[str, int]
    events_by_severity: Dict[str, int]
    top_users: List[Dict[str, Any]]
    compliance_stats: Dict[str, int]
    security_incidents: int
    failed_actions: int
    success_rate: float


class AuditPolicyListResponse(BaseModel):
    """Schema for audit policy list responses."""
    policies: List[AuditPolicyResponse]
    total: int


class RetentionRuleListResponse(BaseModel):
    """Schema for retention rule list responses."""
    rules: List[RetentionRuleResponse]
    total: int


class ComplianceReportListResponse(BaseModel):
    """Schema for compliance report list responses."""
    reports: List[ComplianceReportResponse]
    total: int


class AuditAlertListResponse(BaseModel):
    """Schema for audit alert list responses."""
    alerts: List[AuditAlertResponse]
    total: int


class AuditArchiveListResponse(BaseModel):
    """Schema for audit archive list responses."""
    archives: List[AuditArchiveResponse]
    total: int


# Export schemas
class AuditLogExportParams(BaseModel):
    """Schema for audit log export parameters."""
    format: str = Field("json", regex="^(json|csv|xml)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    event_categories: Optional[List[AuditEventCategory]] = None
    severity_levels: Optional[List[AuditSeverity]] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    include_context: bool = True
    include_metadata: bool = True


class AuditLogExportResponse(BaseModel):
    """Schema for audit log export responses."""
    export_id: str
    format: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    record_count: int
    created_at: datetime
    expires_at: datetime


# Notification schemas
class AuditNotificationConfig(BaseModel):
    """Schema for audit notification configuration."""
    email_enabled: bool = False
    email_recipients: Optional[List[str]] = None
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    sms_enabled: bool = False
    sms_recipients: Optional[List[str]] = None


class AuditNotification(BaseModel):
    """Schema for audit notifications."""
    alert_id: UUID
    alert_name: str
    event_count: int
    threshold_period: int
    triggered_at: datetime
    events: List[Dict[str, Any]]
    notification_channels: List[str]
    recipients: List[str]


# Validation schemas
class AuditLogValidation(BaseModel):
    """Schema for audit log validation."""
    event_type: AuditEventType
    event_category: AuditEventCategory
    severity: AuditSeverity
    resource_type: Optional[str] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification: Optional[DataClassification] = None
    
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
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    user_roles: Optional[List[str]] = None
    
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