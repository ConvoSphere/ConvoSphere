"""
Performance monitoring middleware.

This module provides FastAPI middleware for monitoring HTTP request/response
performance and collecting request metrics.
"""

import time
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.metrics import MetricsCollector, MetricType


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring HTTP request/response performance."""

    def __init__(self, app, metrics_collector: MetricsCollector):
        """Initialize performance middleware."""
        super().__init__(app)
        self.metrics_collector = metrics_collector

    async def dispatch(self, request: Request, call_next):
        """Process request and collect performance metrics."""
        start_time = time.time()
        
        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = str(request.query_params)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Record request start
        self.metrics_collector.increment_counter(
            "http_requests_total",
            tags={
                "method": method,
                "path": path,
                "status": "started"
            }
        )

        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record successful request metrics
            self._record_request_metrics(
                method=method,
                path=path,
                status_code=response.status_code,
                response_time=response_time,
                client_ip=client_ip,
                user_agent=user_agent,
                success=True
            )
            
            return response

        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time
            
            # Record failed request metrics
            self._record_request_metrics(
                method=method,
                path=path,
                status_code=500,  # Assume 500 for exceptions
                response_time=response_time,
                client_ip=client_ip,
                user_agent=user_agent,
                success=False,
                error=str(e)
            )
            
            # Re-raise the exception
            raise

    def _record_request_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        client_ip: str,
        user_agent: str,
        success: bool,
        error: str | None = None
    ) -> None:
        """Record comprehensive request metrics."""
        try:
            # Basic request metrics
            self.metrics_collector.increment_counter(
                "http_requests_total",
                tags={
                    "method": method,
                    "path": path,
                    "status_code": str(status_code),
                    "success": str(success).lower()
                }
            )

            # Response time metrics
            self.metrics_collector.record_timer(
                "http_request_duration_seconds",
                response_time,
                tags={
                    "method": method,
                    "path": path,
                    "status_code": str(status_code)
                }
            )

            # Response time histogram
            self.metrics_collector.record_histogram(
                "http_request_duration_histogram",
                response_time,
                tags={
                    "method": method,
                    "path": path
                }
            )

            # Status code metrics
            self.metrics_collector.increment_counter(
                "http_responses_total",
                tags={
                    "status_code": str(status_code),
                    "status_class": f"{status_code // 100}xx"
                }
            )

            # Error metrics
            if not success or status_code >= 400:
                self.metrics_collector.increment_counter(
                    "http_errors_total",
                    tags={
                        "method": method,
                        "path": path,
                        "status_code": str(status_code),
                        "error_type": "exception" if not success else "http_error"
                    }
                )

                if error:
                    self.metrics_collector.increment_counter(
                        "http_error_details",
                        tags={
                            "error": error[:100],  # Truncate long error messages
                            "method": method,
                            "path": path
                        }
                    )

            # Client metrics
            self.metrics_collector.increment_counter(
                "http_client_requests",
                tags={
                    "client_ip": client_ip,
                    "user_agent": self._categorize_user_agent(user_agent)
                }
            )

            # Path-specific metrics
            self.metrics_collector.increment_counter(
                "http_path_requests",
                tags={
                    "path": path,
                    "method": method
                }
            )

            # Performance alerts for slow requests
            if response_time > 5.0:  # Alert for requests over 5 seconds
                self.metrics_collector.increment_counter(
                    "http_slow_requests",
                    tags={
                        "method": method,
                        "path": path,
                        "duration_range": "5s+"
                    }
                )

            elif response_time > 1.0:  # Track requests over 1 second
                self.metrics_collector.increment_counter(
                    "http_slow_requests",
                    tags={
                        "method": method,
                        "path": path,
                        "duration_range": "1s-5s"
                    }
                )

        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        try:
            # Check for forwarded headers first
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()

            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip

            # Fallback to direct connection
            if hasattr(request, "client") and request.client:
                return request.client.host

            return "unknown"

        except Exception:
            return "unknown"

    def _categorize_user_agent(self, user_agent: str) -> str:
        """Categorize user agent string."""
        try:
            user_agent_lower = user_agent.lower()
            
            if "bot" in user_agent_lower or "crawler" in user_agent_lower:
                return "bot"
            elif "mobile" in user_agent_lower:
                return "mobile"
            elif "chrome" in user_agent_lower:
                return "chrome"
            elif "firefox" in user_agent_lower:
                return "firefox"
            elif "safari" in user_agent_lower:
                return "safari"
            elif "edge" in user_agent_lower:
                return "edge"
            elif "postman" in user_agent_lower or "insomnia" in user_agent_lower:
                return "api_client"
            else:
                return "other"

        except Exception:
            return "unknown"

    def get_request_statistics(self, time_window_minutes: int = 60) -> dict[str, Any]:
        """Get request statistics for a time window."""
        try:
            # Get metrics from the last time window
            from datetime import datetime, timedelta
            since = datetime.now() - timedelta(minutes=time_window_minutes)
            
            # Get request metrics
            request_metrics = self.metrics_collector.get_metrics(
                name="http_requests_total",
                since=since
            )
            
            # Get response time metrics
            response_time_metrics = self.metrics_collector.get_metrics(
                name="http_request_duration_seconds",
                since=since
            )
            
            # Get error metrics
            error_metrics = self.metrics_collector.get_metrics(
                name="http_errors_total",
                since=since
            )
            
            # Calculate statistics
            total_requests = len(request_metrics)
            total_errors = len(error_metrics)
            
            avg_response_time = 0.0
            if response_time_metrics:
                avg_response_time = sum(m.value for m in response_time_metrics) / len(response_time_metrics)
            
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
            requests_per_minute = total_requests / time_window_minutes if time_window_minutes > 0 else 0.0
            
            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": error_rate,
                "avg_response_time_seconds": avg_response_time,
                "requests_per_minute": requests_per_minute,
                "time_window_minutes": time_window_minutes,
            }

        except Exception as e:
            logger.error(f"Failed to get request statistics: {e}")
            return {}