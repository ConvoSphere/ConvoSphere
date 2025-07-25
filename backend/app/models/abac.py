"""
Attribute-Based Access Control (ABAC) model.

This module implements ABAC for dynamic permission evaluation based on
user attributes, resource attributes, and environmental conditions.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class AttributeType(str, Enum):
    """Attribute types for ABAC."""

    USER = "user"
    RESOURCE = "resource"
    ENVIRONMENT = "environment"
    ACTION = "action"


class OperatorType(str, Enum):
    """Comparison operators for ABAC rules."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class ABACRule(Base):
    """ABAC rule model for dynamic permission evaluation."""

    __tablename__ = "abac_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Rule definition
    resource_type = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)

    # Conditions (JSON structure)
    conditions = Column(JSON, nullable=False)  # List of condition objects

    # Effect
    effect = Column(String(10), nullable=False, default="allow")  # "allow" or "deny"

    # Priority (higher number = higher priority)
    priority = Column(Integer, default=0, nullable=False)

    # Rule settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<ABACRule(id={self.id}, name='{self.name}', effect='{self.effect}')>"

    def evaluate(
        self,
        user: "User",
        resource: Any = None,
        action: str = None,
        context: dict[str, Any] = None,
    ) -> bool:
        """Evaluate ABAC rule."""
        context = context or {}

        # Build attribute context
        attributes = {
            "user": self._extract_user_attributes(user),
            "resource": self._extract_resource_attributes(resource) if resource else {},
            "environment": self._extract_environment_attributes(context),
            "action": {"name": action} if action else {},
        }

        # Evaluate all conditions
        for condition in self.conditions:
            if not self._evaluate_condition(condition, attributes):
                return False

        return True

    def _extract_user_attributes(self, user: "User") -> dict[str, Any]:
        """Extract user attributes for ABAC evaluation."""
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "organization_id": (
                str(user.organization_id) if user.organization_id else None
            ),
            "department": user.department,
            "job_title": user.job_title,
            "employee_id": user.employee_id,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "language": user.language,
            "timezone": user.timezone,
            "groups": [
                {"id": str(group.id), "name": group.name} for group in user.groups
            ],
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

    def _extract_resource_attributes(self, resource: Any) -> dict[str, Any]:
        """Extract resource attributes for ABAC evaluation."""
        if not resource:
            return {}

        attributes = {
            "id": str(resource.id) if hasattr(resource, "id") else None,
            "type": resource.__class__.__name__.lower(),
        }

        # Extract common resource attributes
        if hasattr(resource, "creator_id"):
            attributes["creator_id"] = str(resource.creator_id)
        if hasattr(resource, "organization_id"):
            attributes["organization_id"] = str(resource.organization_id)
        if hasattr(resource, "is_public"):
            attributes["is_public"] = resource.is_public
        if hasattr(resource, "is_active"):
            attributes["is_active"] = resource.is_active
        if hasattr(resource, "created_at"):
            attributes["created_at"] = (
                resource.created_at.isoformat() if resource.created_at else None
            )
        if hasattr(resource, "updated_at"):
            attributes["updated_at"] = (
                resource.updated_at.isoformat() if resource.updated_at else None
            )

        return attributes

    def _extract_environment_attributes(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract environment attributes for ABAC evaluation."""
        return {
            "current_time": context.get("current_time", datetime.now().isoformat()),
            "ip_address": context.get("ip_address"),
            "user_agent": context.get("user_agent"),
            "session_id": context.get("session_id"),
            "request_method": context.get("request_method"),
            "request_path": context.get("request_path"),
            "timezone": context.get("timezone"),
            "locale": context.get("locale"),
        }

    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        attributes: dict[str, Any],
    ) -> bool:
        """Evaluate a single ABAC condition."""
        attribute_type = condition.get("attribute_type")
        attribute_name = condition.get("attribute_name")
        operator = condition.get("operator")
        value = condition.get("value")

        # Get the attribute value
        if attribute_type not in attributes:
            return False

        attribute_value = attributes[attribute_type].get(attribute_name)

        # Apply operator
        return self._apply_operator(operator, attribute_value, value)

    def _apply_operator(
        self,
        operator: str,
        attribute_value: Any,
        expected_value: Any,
    ) -> bool:
        """Apply comparison operator."""
        if operator == OperatorType.EQUALS:
            return attribute_value == expected_value
        if operator == OperatorType.NOT_EQUALS:
            return attribute_value != expected_value
        if operator == OperatorType.GREATER_THAN:
            return attribute_value > expected_value
        if operator == OperatorType.LESS_THAN:
            return attribute_value < expected_value
        if operator == OperatorType.GREATER_EQUAL:
            return attribute_value >= expected_value
        if operator == OperatorType.LESS_EQUAL:
            return attribute_value <= expected_value
        if operator == OperatorType.CONTAINS:
            return expected_value in attribute_value if attribute_value else False
        if operator == OperatorType.NOT_CONTAINS:
            return expected_value not in attribute_value if attribute_value else True
        if operator == OperatorType.IN:
            return (
                attribute_value in expected_value
                if isinstance(expected_value, (list, tuple))
                else False
            )
        if operator == OperatorType.NOT_IN:
            return (
                attribute_value not in expected_value
                if isinstance(expected_value, (list, tuple))
                else True
            )
        if operator == OperatorType.EXISTS:
            return attribute_value is not None
        if operator == OperatorType.NOT_EXISTS:
            return attribute_value is None
        if operator == OperatorType.REGEX:
            import re

            return (
                bool(re.match(expected_value, str(attribute_value)))
                if attribute_value
                else False
            )

        return False


class ABACPolicy(Base):
    """ABAC policy model for grouping related rules."""

    __tablename__ = "abac_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Policy settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    rules = relationship("ABACRule", backref="policy")

    def __repr__(self) -> str:
        return f"<ABACPolicy(id={self.id}, name='{self.name}')>"

    def evaluate(
        self,
        user: "User",
        resource: Any = None,
        action: str = None,
        context: dict[str, Any] = None,
    ) -> bool | None:
        """Evaluate ABAC policy (returns True for allow, False for deny, None for no match)."""
        if not self.is_active:
            return None

        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            if rule.is_active and rule.evaluate(user, resource, action, context):
                return rule.effect == "allow"

        return None  # No matching rules
