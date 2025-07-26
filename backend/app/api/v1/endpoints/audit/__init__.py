"""
Audit API endpoints module.

This module provides comprehensive audit functionality including:
- Audit logs management
- Audit policies
- Compliance reporting
- Audit alerts
- Retention rules
- Audit archives
"""

from fastapi import APIRouter

from .alerts import router as alerts_router
from .archives import router as archives_router
from .compliance import router as compliance_router
from .logs import router as logs_router
from .maintenance import router as maintenance_router
from .policies import router as policies_router
from .retention import router as retention_router

# Create main audit router
router = APIRouter(prefix="/audit", tags=["audit"])

# Include all sub-routers
router.include_router(logs_router, prefix="/logs", tags=["audit-logs"])
router.include_router(policies_router, prefix="/policies", tags=["audit-policies"])
router.include_router(compliance_router, prefix="/compliance", tags=["audit-compliance"])
router.include_router(alerts_router, prefix="/alerts", tags=["audit-alerts"])
router.include_router(retention_router, prefix="/retention", tags=["audit-retention"])
router.include_router(archives_router, prefix="/archives", tags=["audit-archives"])
router.include_router(maintenance_router, prefix="/maintenance", tags=["audit-maintenance"])
