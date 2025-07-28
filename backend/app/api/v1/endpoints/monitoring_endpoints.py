"""
Monitoring API endpoints.

This module provides REST API endpoints for:
- Performance metrics collection and retrieval
- System monitoring data
- Alert management
- Performance reports and analytics
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.monitoring.performance_monitor import (
    get_performance_monitor,
    PerformanceMonitor,
    AlertSeverity
)
from backend.app.models.user import User

router = APIRouter()


@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current system metrics."""
    try:
        monitor = get_performance_monitor(db)
        await monitor.collect_metrics()
        
        # Get system metrics
        system_metrics = monitor.system_monitor.get_system_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": system_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/database")
async def get_database_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get database performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get database metrics
        db_metrics = monitor.database_monitor.get_database_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": db_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database metrics: {str(e)}")


@router.get("/cache")
async def get_cache_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get cache performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get cache metrics
        cache_metrics = monitor.cache_manager.get_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": cache_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache metrics: {str(e)}")


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get performance alerts."""
    try:
        monitor = get_performance_monitor(db)
        
        # Convert severity string to enum
        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Get alerts
        alerts = monitor.alert_manager.get_alerts(
            severity=severity_enum,
            since=since
        )
        
        # Convert to dict format
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "name": alert.name,
                "message": alert.message,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp.isoformat(),
                "metric_name": alert.metric_name,
                "threshold": alert.threshold,
                "current_value": alert.current_value,
                "tags": alert.tags
            })
        
        return alert_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/report")
async def get_performance_report(
    since: datetime = Body(...),
    until: Optional[datetime] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    try:
        monitor = get_performance_monitor(db)
        
        # Use current time if until is not provided
        if not until:
            until = datetime.utcnow()
        
        # Get performance report
        report = monitor.get_performance_report(since=since)
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance report: {str(e)}")


@router.get("/snapshot")
async def get_performance_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current performance snapshot."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get performance snapshot
        snapshot = monitor.get_performance_snapshot()
        
        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "cpu_percent": snapshot.cpu_percent,
            "memory_percent": snapshot.memory_percent,
            "disk_usage_percent": snapshot.disk_usage_percent,
            "network_io": snapshot.network_io,
            "active_connections": snapshot.active_connections,
            "request_count": snapshot.request_count,
            "error_count": snapshot.error_count,
            "avg_response_time": snapshot.avg_response_time,
            "cache_hit_rate": snapshot.cache_hit_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance snapshot: {str(e)}")


@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get recent slow database queries."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get slow queries
        slow_queries = monitor.database_monitor.get_slow_queries(limit=limit)
        
        # Convert to dict format
        query_data = []
        for query in slow_queries:
            query_data.append({
                "statement": query["statement"],
                "parameters": str(query["parameters"]),
                "execution_time": query["execution_time"],
                "timestamp": query["timestamp"].isoformat()
            })
        
        return query_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slow queries: {str(e)}")


@router.post("/alerts/rules")
async def add_alert_rule(
    name: str = Body(...),
    metric_name: str = Body(...),
    threshold: float = Body(...),
    severity: str = Body(...),
    condition: str = Body("gt"),
    tags: Optional[Dict[str, str]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Add a new alert rule."""
    try:
        monitor = get_performance_monitor(db)
        
        # Convert severity string to enum
        try:
            severity_enum = AlertSeverity(severity.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Add alert rule
        monitor.alert_manager.add_alert_rule(
            name=name,
            metric_name=metric_name,
            threshold=threshold,
            severity=severity_enum,
            condition=condition,
            tags=tags
        )
        
        return {"message": f"Alert rule '{name}' added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add alert rule: {str(e)}")


@router.get("/alerts/rules")
async def get_alert_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all alert rules."""
    try:
        monitor = get_performance_monitor(db)
        
        return {
            "rules": monitor.alert_manager.alert_rules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert rules: {str(e)}")


@router.delete("/alerts/rules/{rule_name}")
async def delete_alert_rule(
    rule_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete an alert rule."""
    try:
        monitor = get_performance_monitor(db)
        
        if rule_name not in monitor.alert_manager.alert_rules:
            raise HTTPException(status_code=404, detail=f"Alert rule '{rule_name}' not found")
        
        # Delete alert rule
        del monitor.alert_manager.alert_rules[rule_name]
        
        return {"message": f"Alert rule '{rule_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert rule: {str(e)}")


@router.get("/metrics/{metric_name}")
async def get_metric_statistics(
    metric_name: str,
    metric_type: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get statistics for a specific metric."""
    try:
        monitor = get_performance_monitor(db)
        
        # Convert metric type string to enum if provided
        metric_type_enum = None
        if metric_type:
            from backend.app.monitoring.performance_monitor import MetricType
            try:
                metric_type_enum = MetricType(metric_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
        
        # Get metric statistics
        if metric_type_enum:
            stats = monitor.metrics_collector.get_statistics(metric_name, metric_type_enum)
        else:
            # Get all metrics for the name
            metrics = monitor.metrics_collector.get_metrics(name=metric_name, since=since)
            stats = {
                "count": len(metrics),
                "metrics": [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "tags": m.tags
                    }
                    for m in metrics
                ]
            }
        
        return {
            "metric_name": metric_name,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metric statistics: {str(e)}")


@router.post("/cache/warmup")
async def warmup_cache(
    patterns: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Warm up cache with specified patterns."""
    try:
        monitor = get_performance_monitor(db)
        
        # Warm up cache
        await monitor.cache_manager.warmup_cache(patterns)
        
        return {"message": "Cache warmup completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to warm up cache: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(
    pattern: str = Body("*"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clear cache entries matching pattern."""
    try:
        monitor = get_performance_monitor(db)
        
        # Clear cache
        deleted_count = await monitor.cache_manager.clear(pattern)
        
        return {
            "message": f"Cache cleared successfully",
            "deleted_count": deleted_count,
            "pattern": pattern
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get system health status."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get current metrics
        system_metrics = monitor.system_monitor.get_system_metrics()
        db_metrics = monitor.database_monitor.get_database_metrics()
        cache_metrics = monitor.cache_manager.get_metrics()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        # Check CPU usage
        if system_metrics["cpu_percent"] > 90:
            health_status = "critical"
            issues.append("High CPU usage")
        elif system_metrics["cpu_percent"] > 80:
            health_status = "warning"
            issues.append("Elevated CPU usage")
        
        # Check memory usage
        if system_metrics["memory_percent"] > 95:
            health_status = "critical"
            issues.append("Critical memory usage")
        elif system_metrics["memory_percent"] > 85:
            health_status = "warning"
            issues.append("High memory usage")
        
        # Check disk usage
        if system_metrics["disk_percent"] > 95:
            health_status = "critical"
            issues.append("Critical disk usage")
        elif system_metrics["disk_percent"] > 90:
            health_status = "warning"
            issues.append("High disk usage")
        
        # Check cache hit rate
        if cache_metrics.get("hit_rate", 1) < 0.5:
            health_status = "warning"
            issues.append("Low cache hit rate")
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "issues": issues,
            "metrics": {
                "cpu_percent": system_metrics["cpu_percent"],
                "memory_percent": system_metrics["memory_percent"],
                "disk_percent": system_metrics["disk_percent"],
                "cache_hit_rate": cache_metrics.get("hit_rate", 1)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }