"""
audit service module.

This module provides audit functionality for the ConvoSphere platform.
"""

from .audit_service import AuditService
from ...core.database import get_db

def get_audit_service():
    """Get an audit service instance with database connection."""
    db = next(get_db())
    return AuditService(db)

__all__ = ["AuditService", "get_audit_service"]
