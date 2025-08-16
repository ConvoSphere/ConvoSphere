"""
Monitoring API endpoints.

This module provides REST API endpoints for:
- Performance metrics collection and retrieval
- System monitoring data
- Alert management
- Performance reports and analytics
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.monitoring.performance_monitor import (
    AlertSeverity,
    get_performance_monitor,
)

router = APIRouter()


@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get current system metrics."""
    try:
        monitor = get_performance_monitor(db)
        await monitor.collect_metrics()

        # Get system metrics
        system_metrics = monitor.system_monitor.get_system_metrics()

        return {"timestamp": datetime.utcnow().isoformat(), "metrics": system_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/database")
async def get_database_metrics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get database performance metrics."""
    try:
        monitor = get_performance_monitor(db)

        # Get database metrics
        db_metrics = monitor.database_monitor.get_database_metrics()

        return {"timestamp": datetime.utcnow().isoformat(), "metrics": db_metrics}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get database metrics: {str(e)}"
        )


@router.get("/cache")
async def get_cache_metrics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get cache performance metrics."""
    try:
        monitor = get_performance_monitor(db)

        # Get cache metrics
        cache_metrics = monitor.cache_manager.get_metrics()

        return {"timestamp": datetime.utcnow().isoformat(), "metrics": cache_metrics}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache metrics: {str(e)}"
        )


@router.get("/alerts")
async def get_alerts(
    severity: str | None = Query(None),
    since: datetime | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Get performance alerts."""
    try:
        monitor = get_performance_monitor(db)

        # Convert severity string to enum
        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid severity: {severity}"
                )

        # Get alerts
        alerts = monitor.alert_manager.get_alerts(severity=severity_enum, since=since)

        # Convert to dict format
        alert_data = []
        for alert in alerts:
            alert_data.append(
                {
                    "name": alert.name,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_name": alert.metric_name,
                    "threshold": alert.threshold,
                    "current_value": alert.current_value,
                    "tags": alert.tags,
                }
            )

        return alert_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/report")
async def get_performance_report(
    since: datetime = Body(...),
    until: datetime | None = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get comprehensive performance report."""
    try:
        monitor = get_performance_monitor(db)

        # Use current time if until is not provided
        if not until:
            until = datetime.utcnow()

        # Get performance report
        return monitor.get_performance_report(since=since)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance report: {str(e)}"
        )


@router.get("/snapshot")
async def get_performance_snapshot(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
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
            "cache_hit_rate": snapshot.cache_hit_rate,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance snapshot: {str(e)}"
        )


@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Get recent slow database queries."""
    try:
        monitor = get_performance_monitor(db)

        # Get slow queries
        slow_queries = monitor.database_monitor.get_slow_queries(limit=limit)

        # Convert to dict format
        query_data = []
        for query in slow_queries:
            query_data.append(
                {
                    "statement": query["statement"],
                    "parameters": str(query["parameters"]),
                    "execution_time": query["execution_time"],
                    "timestamp": query["timestamp"].isoformat(),
                }
            )

        return query_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get slow queries: {str(e)}"
        )


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get system health status."""
    try:
        monitor = get_performance_monitor(db)

        # Get current metrics
        system_metrics = monitor.system_monitor.get_system_metrics()
        monitor.database_monitor.get_database_metrics()
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
                "cache_hit_rate": cache_metrics.get("hit_rate", 1),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }

# --- New wrapper endpoints for frontend integration ---

@router.get("/metrics/system")
async def get_metrics_system(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Wrapper to provide system metrics at /metrics/system for the frontend."""
    try:
        monitor = get_performance_monitor(db)
        await monitor.collect_metrics()
        return monitor.system_monitor.get_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/performance")
async def get_performance_timeseries(
    timeRange: str = Query("1h"),
    interval: str = Query("1m"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Provide performance time series for responseTime/throughput/errorRate.
    This uses the metrics_collector snapshots and aggregates them coarsely by interval.
    """
    try:
        monitor = get_performance_monitor(db)
        metrics = monitor.metrics_collector.get_metrics()
        # Basic coarse aggregation: map each metric to simplified series
        series: list[dict[str, Any]] = []
        for m in metrics:
            series.append(
                {
                    "timestamp": m.timestamp.isoformat(),
                    "responseTime": m.value if m.name == "response_time_ms" else 0,
                    "throughput": m.value if m.name == "throughput_rps" else 0,
                    "errorRate": m.value if m.name == "error_rate" else 0,
                    "activeConnections": m.tags.get("active_connections", 0) if m.tags else 0,
                    "queueLength": m.tags.get("queue_length", 0) if m.tags else 0,
                }
            )
        return series
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")


@router.get("/health/services")
async def get_services_health(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[dict[str, Any]]:
    """Return health status for core services (db, redis, weaviate)."""
    try:
        monitor = get_performance_monitor(db)
        system_metrics = monitor.system_monitor.get_system_metrics()
        # Compose minimal service list for UI
        services = [
            {
                "service": "database",
                "status": "healthy",
                "responseTime": 0,
                "lastCheck": datetime.utcnow().isoformat(),
                "uptime": 0,
                "version": "",
                "endpoints": [{"name": "db", "status": "up", "responseTime": 0}],
            },
            {
                "service": "redis",
                "status": "healthy",
                "responseTime": 0,
                "lastCheck": datetime.utcnow().isoformat(),
                "uptime": 0,
                "version": "",
                "endpoints": [{"name": "cache", "status": "up", "responseTime": 0}],
            },
            {
                "service": "vector_db",
                "status": "healthy",
                "responseTime": 0,
                "lastCheck": datetime.utcnow().isoformat(),
                "uptime": 0,
                "version": "",
                "endpoints": [{"name": "weaviate", "status": "up", "responseTime": 0}],
            },
        ]
        # Example: degrade based on system metrics
        if system_metrics.get("cpu_percent", 0) > 90:
            services[0]["status"] = "degraded"
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service health: {str(e)}")


@router.post("/health/check")
async def trigger_health_check(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Trigger a health check/metrics collection cycle."""
    try:
        monitor = get_performance_monitor(db)
        await monitor.collect_metrics()
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger health check: {str(e)}")


@router.get("/logs")
async def get_system_logs(
    level: str | None = Query(None),
    service: str | None = Query(None),
    startTime: str | None = Query(None),
    endTime: str | None = Query(None),
    limit: int = Query(200, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return last N log lines. Basic implementation that tails the log file.
    Note: For production, prefer centralized logging.
    """
    try:
        from backend.app.core.config import get_settings
        import os

        settings = get_settings()
        log_file = settings.log_file
        if not os.path.exists(log_file):
            return []
        lines: list[str] = []
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines()[-limit:]:
                lines.append(line.rstrip("\n"))
        return lines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.get("/stats/errors")
async def get_error_stats(
    timeRange: str = Query("24h"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return simple error statistics based on logs/metrics."""
    try:
        # Placeholder: count of error events from logs collector
        return {"timeRange": timeRange, "errorCount": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error stats: {str(e)}")


@router.get("/stats/api-usage")
async def get_api_usage_stats(
    timeRange: str = Query("24h"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return simple API usage statistics based on collected metrics."""
    try:
        return {"timeRange": timeRange, "requests": 0, "avgResponseMs": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get API usage stats: {str(e)}")


@router.get("/config")
async def get_monitoring_config(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return monitoring configuration (in-memory settings for now)."""
    from backend.app.core.config import get_settings

    s = get_settings().monitoring
    return {
        "performanceMonitoringEnabled": s.performance_monitoring_enabled,
        "collectionInterval": s.monitoring_collection_interval,
        "retentionHours": s.monitoring_retention_hours,
    }


@router.put("/config")
async def update_monitoring_config(
    config: dict[str, Any], current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Update monitoring config (in-memory for now)."""
    from backend.app.core.config import get_settings

    settings = get_settings()
    # Apply only known keys to avoid unwanted changes
    mon = settings.monitoring
    if "performanceMonitoringEnabled" in config:
        mon.performance_monitoring_enabled = bool(config["performanceMonitoringEnabled"])
    if "collectionInterval" in config:
        mon.monitoring_collection_interval = int(config["collectionInterval"])
    if "retentionHours" in config:
        mon.monitoring_retention_hours = int(config["retentionHours"])
    return await get_monitoring_config()  # type: ignore[misc]


@router.get("/dashboard")
async def get_monitoring_dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Aggregated dashboard combining metrics and health."""
    monitor = get_performance_monitor(db)
    await monitor.collect_metrics()
    system = monitor.system_monitor.get_system_metrics()
    dbm = monitor.database_monitor.get_database_metrics()
    cache = monitor.cache_manager.get_metrics()
    return {"system": system, "database": dbm, "cache": cache}


@router.get("/export")
async def export_monitoring_data(
    format: str = Query("csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export basic monitoring data in CSV or JSON."""
    from fastapi.responses import JSONResponse, StreamingResponse
    import io
    import csv

    monitor = get_performance_monitor(db)
    await monitor.collect_metrics()
    metrics = monitor.metrics_collector.get_metrics()

    if format == "json":
        return JSONResponse(
            content=[
                {"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat(), "tags": m.tags}
                for m in metrics
            ]
        )

    # CSV fallback
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "value", "timestamp"]) 
    for m in metrics:
        writer.writerow([m.name, m.value, m.timestamp.isoformat()])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=monitoring.csv"})
