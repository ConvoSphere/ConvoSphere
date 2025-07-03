"""
Performance manager for monitoring and optimizing application performance.

This module provides performance monitoring, caching, and optimization
features for the frontend application.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class PerformanceMetric(Enum):
    """Performance metric types."""
    API_REQUEST = "api_request"
    UI_RENDER = "ui_render"
    DATA_LOAD = "data_load"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    MEMORY_USAGE = "memory_usage"
    NETWORK_LATENCY = "network_latency"


@dataclass
class PerformanceData:
    """Performance data point."""
    metric: PerformanceMetric
    value: float
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


class PerformanceManager:
    """Performance monitoring and optimization manager."""
    
    def __init__(self):
        """Initialize performance manager."""
        self.metrics: List[PerformanceData] = []
        self.max_metrics = 1000
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.default_ttl = 300  # 5 minutes
        self.performance_handlers: List[Callable] = []
        
        # Performance thresholds
        self.thresholds = {
            PerformanceMetric.API_REQUEST: 2000,  # 2 seconds
            PerformanceMetric.UI_RENDER: 100,     # 100ms
            PerformanceMetric.DATA_LOAD: 1000,    # 1 second
            PerformanceMetric.NETWORK_LATENCY: 500  # 500ms
        }
    
    def record_metric(
        self,
        metric: PerformanceMetric,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric."""
        data = PerformanceData(
            metric=metric,
            value=value,
            timestamp=time.time(),
            context=context or {}
        )
        
        self.metrics.append(data)
        
        # Limit metrics history
        if len(self.metrics) > self.max_metrics:
            self.metrics.pop(0)
        
        # Check thresholds
        self._check_threshold(data)
        
        # Notify handlers
        self._notify_handlers(data)
    
    def _check_threshold(self, data: PerformanceData):
        """Check if metric exceeds threshold."""
        threshold = self.thresholds.get(data.metric)
        if threshold and data.value > threshold:
            print(f"Performance warning: {data.metric.value} = {data.value}ms (threshold: {threshold}ms)")
    
    def _notify_handlers(self, data: PerformanceData):
        """Notify performance handlers."""
        for handler in self.performance_handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"Error in performance handler: {e}")
    
    def on_performance_issue(self, handler: Callable):
        """Register performance issue handler."""
        self.performance_handlers.append(handler)
    
    # Caching functionality
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value."""
        self.cache[key] = value
        self.cache_ttl[key] = time.time() + (ttl or self.default_ttl)
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        if key not in self.cache:
            self.record_metric(PerformanceMetric.CACHE_MISS, 0, {"key": key})
            return None
        
        # Check TTL
        if time.time() > self.cache_ttl.get(key, 0):
            del self.cache[key]
            del self.cache_ttl[key]
            self.record_metric(PerformanceMetric.CACHE_MISS, 0, {"key": key})
            return None
        
        self.record_metric(PerformanceMetric.CACHE_HIT, 0, {"key": key})
        return self.cache[key]
    
    def cache_clear(self, pattern: Optional[str] = None):
        """Clear cache entries."""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
                del self.cache_ttl[key]
        else:
            self.cache.clear()
            self.cache_ttl.clear()
    
    # Performance decorators
    def monitor(self, metric: PerformanceMetric):
        """Decorator to monitor function performance."""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    self.record_metric(metric, duration, {"function": func.__name__})
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    self.record_metric(metric, duration, {
                        "function": func.__name__,
                        "error": str(e)
                    })
                    raise
            
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    self.record_metric(metric, duration, {"function": func.__name__})
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    self.record_metric(metric, duration, {
                        "function": func.__name__,
                        "error": str(e)
                    })
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator
    
    def cache_result(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """Decorator to cache function results."""
        def decorator(func):
            def get_cache_key(*args, **kwargs):
                if key_func:
                    return key_func(*args, **kwargs)
                return f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            async def async_wrapper(*args, **kwargs):
                cache_key = get_cache_key(*args, **kwargs)
                cached_result = self.cache_get(cache_key)
                
                if cached_result is not None:
                    return cached_result
                
                result = await func(*args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result
            
            def sync_wrapper(*args, **kwargs):
                cache_key = get_cache_key(*args, **kwargs)
                cached_result = self.cache_get(cache_key)
                
                if cached_result is not None:
                    return cached_result
                
                result = func(*args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator
    
    # Analytics and reporting
    def get_metrics_summary(self, metric: Optional[PerformanceMetric] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        filtered_metrics = self.metrics
        if metric:
            filtered_metrics = [m for m in self.metrics if m.metric == metric]
        
        if not filtered_metrics:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        
        values = [m.value for m in filtered_metrics]
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "recent": values[-10:] if len(values) > 10 else values
        }
    
    def get_slow_operations(self, threshold: Optional[float] = None) -> List[PerformanceData]:
        """Get operations that exceeded threshold."""
        if threshold is None:
            threshold = 1000  # 1 second default
        
        return [m for m in self.metrics if m.value > threshold]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = len([m for m in self.metrics if m.metric in [PerformanceMetric.CACHE_HIT, PerformanceMetric.CACHE_MISS]])
        cache_hits = len([m for m in self.metrics if m.metric == PerformanceMetric.CACHE_HIT])
        
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "cache_hits": cache_hits,
            "cache_misses": total_requests - cache_hits,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }
    
    def clear_metrics(self):
        """Clear all performance metrics."""
        self.metrics.clear()
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export metrics for external analysis."""
        return [
            {
                "metric": m.metric.value,
                "value": m.value,
                "timestamp": m.timestamp,
                "context": m.context
            }
            for m in self.metrics
        ]


# Global performance manager instance
performance_manager = PerformanceManager()


# Convenience functions
def monitor_performance(metric: PerformanceMetric):
    """Convenience decorator for performance monitoring."""
    return performance_manager.monitor(metric)


def cache_result(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Convenience decorator for result caching."""
    return performance_manager.cache_result(ttl, key_func)


def record_metric(metric: PerformanceMetric, value: float, context: Optional[Dict[str, Any]] = None):
    """Convenience function to record metrics."""
    performance_manager.record_metric(metric, value, context) 