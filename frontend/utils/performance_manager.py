"""
Performance management system for the AI Assistant Platform.

This module provides comprehensive performance optimization including
code splitting, lazy loading, caching, and monitoring.
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import weakref

from nicegui import ui


class PerformanceMetric(Enum):
    """Performance metric types."""
    LOAD_TIME = "load_time"
    RENDER_TIME = "render_time"
    API_RESPONSE_TIME = "api_response_time"
    MEMORY_USAGE = "memory_usage"
    BUNDLE_SIZE = "bundle_size"
    CACHE_HIT_RATE = "cache_hit_rate"


@dataclass
class PerformanceData:
    """Performance data point."""
    metric: PerformanceMetric
    value: float
    timestamp: datetime
    component: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheEntry:
    """Cache entry for data caching."""
    key: str
    data: Any
    timestamp: datetime
    ttl: timedelta
    access_count: int = 0
    last_accessed: datetime = None


class PerformanceManager:
    """Performance management system."""
    
    def __init__(self):
        """Initialize performance manager."""
        self.metrics: List[PerformanceData] = []
        self.cache: Dict[str, CacheEntry] = {}
        self.lazy_loaded_components: Set[str] = set()
        self.performance_callbacks: List[Callable[[PerformanceData], None]] = []
        self.monitoring_enabled = True
        self.cache_enabled = True
        self.lazy_loading_enabled = True
        
        # Performance thresholds
        self.thresholds = {
            PerformanceMetric.LOAD_TIME: 1000,  # 1 second
            PerformanceMetric.RENDER_TIME: 100,  # 100ms
            PerformanceMetric.API_RESPONSE_TIME: 500,  # 500ms
            PerformanceMetric.MEMORY_USAGE: 50 * 1024 * 1024,  # 50MB
        }
        
        # Initialize performance monitoring
        self.initialize_monitoring()
    
    def initialize_monitoring(self):
        """Initialize performance monitoring."""
        # Add performance monitoring CSS
        self.add_performance_css()
        
        # Start background monitoring
        asyncio.create_task(self.background_monitoring())
    
    def add_performance_css(self):
        """Add performance-related CSS."""
        css = """
        /* Performance optimizations */
        .lazy-load {
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }
        
        .lazy-load.loaded {
            opacity: 1;
        }
        
        /* Loading indicators */
        .loading-skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Virtual scrolling */
        .virtual-scroll-container {
            height: 100%;
            overflow-y: auto;
            position: relative;
        }
        
        .virtual-scroll-item {
            position: absolute;
            width: 100%;
        }
        
        /* Image optimization */
        .lazy-image {
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .lazy-image.loaded {
            opacity: 1;
        }
        """
        
        ui.add_head_html(f"<style>{css}</style>")
    
    async def background_monitoring(self):
        """Background performance monitoring."""
        while self.monitoring_enabled:
            try:
                # Monitor memory usage
                await self.monitor_memory_usage()
                
                # Clean up expired cache entries
                await self.cleanup_cache()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # 30 seconds
                
            except Exception as e:
                print(f"Error in background monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def monitor_memory_usage(self):
        """Monitor memory usage."""
        try:
            # This would get actual memory usage
            # For now, we'll use a placeholder
            memory_usage = 0  # Placeholder
            
            self.record_metric(
                PerformanceMetric.MEMORY_USAGE,
                memory_usage,
                metadata={"type": "background_monitoring"}
            )
            
        except Exception as e:
            print(f"Error monitoring memory usage: {e}")
    
    def record_metric(self, metric: PerformanceMetric, value: float, component: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a performance metric."""
        if not self.monitoring_enabled:
            return
        
        performance_data = PerformanceData(
            metric=metric,
            value=value,
            timestamp=datetime.now(),
            component=component,
            metadata=metadata
        )
        
        self.metrics.append(performance_data)
        
        # Check if threshold is exceeded
        self.check_threshold(performance_data)
        
        # Notify callbacks
        for callback in self.performance_callbacks:
            try:
                callback(performance_data)
            except Exception as e:
                print(f"Error in performance callback: {e}")
    
    def check_threshold(self, performance_data: PerformanceData):
        """Check if performance threshold is exceeded."""
        threshold = self.thresholds.get(performance_data.metric)
        
        if threshold and performance_data.value > threshold:
            print(f"Performance threshold exceeded: {performance_data.metric.value} = {performance_data.value}ms (threshold: {threshold}ms)")
            
            # This would trigger performance alerts
            self.trigger_performance_alert(performance_data)
    
    def trigger_performance_alert(self, performance_data: PerformanceData):
        """Trigger performance alert."""
        # This would implement performance alerting
        print(f"Performance alert: {performance_data.metric.value} exceeded threshold")
    
    def start_timer(self, metric: PerformanceMetric, component: Optional[str] = None) -> Callable:
        """Start a performance timer."""
        start_time = time.time()
        
        def end_timer(metadata: Optional[Dict[str, Any]] = None):
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.record_metric(metric, duration, component, metadata)
        
        return end_timer
    
    def measure_load_time(self, component: str):
        """Measure component load time."""
        return self.start_timer(PerformanceMetric.LOAD_TIME, component)
    
    def measure_render_time(self, component: str):
        """Measure component render time."""
        return self.start_timer(PerformanceMetric.RENDER_TIME, component)
    
    def measure_api_call(self, endpoint: str):
        """Measure API call performance."""
        return self.start_timer(PerformanceMetric.API_RESPONSE_TIME, endpoint)
    
    # Caching system
    def cache_set(self, key: str, data: Any, ttl: timedelta = timedelta(minutes=5)):
        """Set cache entry."""
        if not self.cache_enabled:
            return
        
        self.cache[key] = CacheEntry(
            key=key,
            data=data,
            timestamp=datetime.now(),
            ttl=ttl,
            last_accessed=datetime.now()
        )
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache entry."""
        if not self.cache_enabled:
            return None
        
        entry = self.cache.get(key)
        
        if entry is None:
            return None
        
        # Check if entry is expired
        if datetime.now() - entry.timestamp > entry.ttl:
            del self.cache[key]
            return None
        
        # Update access statistics
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        return entry.data
    
    def cache_delete(self, key: str):
        """Delete cache entry."""
        if key in self.cache:
            del self.cache[key]
    
    def cache_clear(self):
        """Clear all cache entries."""
        self.cache.clear()
    
    async def cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache:
            return {"total_entries": 0, "total_size": 0}
        
        total_access_count = sum(entry.access_count for entry in self.cache.values())
        avg_access_count = total_access_count / len(self.cache) if self.cache else 0
        
        return {
            "total_entries": len(self.cache),
            "total_access_count": total_access_count,
            "average_access_count": avg_access_count,
            "oldest_entry": min(entry.timestamp for entry in self.cache.values()).isoformat(),
            "newest_entry": max(entry.timestamp for entry in self.cache.values()).isoformat()
        }
    
    # Lazy loading system
    def lazy_load_component(self, component_name: str, loader_func: Callable, placeholder=None):
        """Lazy load a component."""
        if not self.lazy_loading_enabled:
            return loader_func()
        
        if component_name in self.lazy_loaded_components:
            return loader_func()
        
        # Create placeholder
        if placeholder is None:
            placeholder = self.create_loading_placeholder()
        
        # Mark as loading
        self.lazy_loaded_components.add(component_name)
        
        # Load component asynchronously
        asyncio.create_task(self.load_component_async(component_name, loader_func, placeholder))
        
        return placeholder
    
    async def load_component_async(self, component_name: str, loader_func: Callable, placeholder):
        """Load component asynchronously."""
        try:
            # Measure load time
            end_timer = self.measure_load_time(component_name)
            
            # Load component
            component = loader_func()
            
            # Replace placeholder with component
            if hasattr(placeholder, 'clear'):
                placeholder.clear()
                with placeholder:
                    component
            
            # Record load time
            end_timer({"component": component_name})
            
        except Exception as e:
            print(f"Error loading component {component_name}: {e}")
            # Show error state
            if hasattr(placeholder, 'clear'):
                placeholder.clear()
                with placeholder:
                    ui.label(f"Fehler beim Laden von {component_name}").classes("text-red-500")
    
    def create_loading_placeholder(self):
        """Create a loading placeholder."""
        container = ui.element("div").classes("loading-skeleton p-4 rounded")
        with container:
            ui.element("div").classes("h-4 bg-gray-200 rounded mb-2")
            ui.element("div").classes("h-4 bg-gray-200 rounded mb-2 w-3/4")
            ui.element("div").classes("h-4 bg-gray-200 rounded w-1/2")
        return container
    
    # Virtual scrolling
    def create_virtual_scroll(self, items: List[Any], item_height: int, container_height: int, render_item: Callable):
        """Create virtual scrolling container."""
        container = ui.element("div").classes("virtual-scroll-container")
        container.style(f"height: {container_height}px")
        
        # Calculate visible items
        visible_count = container_height // item_height
        total_height = len(items) * item_height
        
        # Create scroll container
        scroll_container = ui.element("div")
        scroll_container.style(f"height: {total_height}px; position: relative;")
        
        def on_scroll(event):
            # Calculate visible range
            scroll_top = event.target.scrollTop
            start_index = int(scroll_top // item_height)
            end_index = min(start_index + visible_count + 2, len(items))
            
            # Update visible items
            self.update_virtual_items(scroll_container, items, start_index, end_index, item_height, render_item)
        
        # Initial render
        self.update_virtual_items(scroll_container, items, 0, visible_count, item_height, render_item)
        
        return container
    
    def update_virtual_items(self, container, items: List[Any], start_index: int, end_index: int, item_height: int, render_item: Callable):
        """Update virtual scroll items."""
        # Clear container
        container.clear()
        
        # Render visible items
        for i in range(start_index, end_index):
            if i < len(items):
                item_container = ui.element("div").classes("virtual-scroll-item")
                item_container.style(f"top: {i * item_height}px; height: {item_height}px")
                
                with item_container:
                    render_item(items[i], i)
    
    # Image optimization
    def create_lazy_image(self, src: str, alt: str = "", placeholder: str = "", **kwargs):
        """Create a lazy loading image."""
        img = ui.image(src, alt=alt, **kwargs)
        img.classes("lazy-image")
        
        # Add loading logic
        asyncio.create_task(self.load_image_async(img, src, placeholder))
        
        return img
    
    async def load_image_async(self, img_element, src: str, placeholder: str = ""):
        """Load image asynchronously."""
        try:
            # Set placeholder if provided
            if placeholder:
                img_element.src = placeholder
            
            # Load actual image
            # This would implement actual image loading logic
            await asyncio.sleep(0.1)  # Simulate loading time
            
            # Update image source
            img_element.src = src
            img_element.classes("loaded")
            
        except Exception as e:
            print(f"Error loading image {src}: {e}")
    
    # Performance reporting
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        if not self.metrics:
            return {"message": "No performance data available"}
        
        # Group metrics by type
        metrics_by_type = {}
        for metric in self.metrics:
            metric_type = metric.metric.value
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric.value)
        
        # Calculate statistics
        report = {
            "total_metrics": len(self.metrics),
            "metrics_by_type": {},
            "cache_stats": self.get_cache_stats(),
            "lazy_loaded_components": list(self.lazy_loaded_components),
            "monitoring_enabled": self.monitoring_enabled,
            "cache_enabled": self.cache_enabled,
            "lazy_loading_enabled": self.lazy_loading_enabled
        }
        
        for metric_type, values in metrics_by_type.items():
            report["metrics_by_type"][metric_type] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else None
            }
        
        return report
    
    def export_performance_data(self) -> str:
        """Export performance data as JSON."""
        report = self.get_performance_report()
        return json.dumps(report, indent=2, default=str)
    
    def clear_performance_data(self):
        """Clear all performance data."""
        self.metrics.clear()
    
    def on_performance_event(self, callback: Callable[[PerformanceData], None]):
        """Register performance event callback."""
        self.performance_callbacks.append(callback)
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable or disable performance monitoring."""
        self.monitoring_enabled = enabled
    
    def enable_caching(self, enabled: bool = True):
        """Enable or disable caching."""
        self.cache_enabled = enabled
    
    def enable_lazy_loading(self, enabled: bool = True):
        """Enable or disable lazy loading."""
        self.lazy_loading_enabled = enabled


# Global performance manager instance
performance_manager = PerformanceManager() 