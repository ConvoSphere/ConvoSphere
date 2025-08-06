import React from 'react';

/**
 * Frontend Performance Monitoring Utility
 * 
 * This module provides comprehensive performance monitoring for the React application,
 * including bundle analysis, runtime performance tracking, and user experience metrics.
 */

export interface PerformanceMetrics {
  // Navigation timing
  navigationStart: number;
  loadEventEnd: number;
  domContentLoadedEventEnd: number;
  
  // Resource loading
  resourceCount: number;
  resourceLoadTime: number;
  
  // React performance
  componentRenderTime: number;
  bundleSize: number;
  
  // User experience
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  
  // Memory usage
  memoryUsage: number;
  
  // Custom metrics
  customMetrics: Record<string, number>;
}

export interface PerformanceObserver {
  onMetricUpdate: (metrics: Partial<PerformanceMetrics>) => void;
  onError: (error: Error) => void;
}

class PerformanceMonitor {
  private observers: PerformanceObserver[] = [];
  private metrics: PerformanceMetrics;
  private isMonitoring = false;
  private performanceObserver: PerformanceObserver | null = null;
  private resourceObserver: PerformanceObserver | null = null;
  private paintObserver: PerformanceObserver | null = null;
  private layoutShiftObserver: PerformanceObserver | null = null;

  constructor() {
    this.metrics = this.initializeMetrics();
  }

  private initializeMetrics(): PerformanceMetrics {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    
    return {
      navigationStart: navigation?.startTime || 0,
      loadEventEnd: navigation?.loadEventEnd || 0,
      domContentLoadedEventEnd: navigation?.domContentLoadedEventEnd || 0,
      resourceCount: 0,
      resourceLoadTime: 0,
      componentRenderTime: 0,
      bundleSize: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      memoryUsage: 0,
      customMetrics: {},
    };
  }

  /**
   * Start performance monitoring
   */
  start(): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.setupObservers();
    this.trackBundleSize();
    this.trackMemoryUsage();
    
    console.log('Performance monitoring started');
  }

  /**
   * Stop performance monitoring
   */
  stop(): void {
    if (!this.isMonitoring) return;
    
    this.isMonitoring = false;
    this.disconnectObservers();
    
    console.log('Performance monitoring stopped');
  }

  /**
   * Add performance observer
   */
  addObserver(observer: PerformanceObserver): void {
    this.observers.push(observer);
  }

  /**
   * Remove performance observer
   */
  removeObserver(observer: PerformanceObserver): void {
    const index = this.observers.indexOf(observer);
    if (index > -1) {
      this.observers.splice(index, 1);
    }
  }

  /**
   * Get current performance metrics
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * Add custom metric
   */
  addCustomMetric(name: string, value: number): void {
    this.metrics.customMetrics[name] = value;
    this.notifyObservers({ customMetrics: this.metrics.customMetrics });
  }

  /**
   * Track component render time
   */
  trackComponentRender(componentName: string, renderTime: number): void {
    this.metrics.componentRenderTime = renderTime;
    this.addCustomMetric(`${componentName}_render_time`, renderTime);
  }

  /**
   * Setup performance observers
   */
  private setupObservers(): void {
    // Navigation timing
    if ('PerformanceObserver' in window) {
      // Resource timing
      this.resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        this.metrics.resourceCount = entries.length;
        this.metrics.resourceLoadTime = entries.reduce((total, entry) => {
          return total + (entry.duration || 0);
        }, 0);
        this.notifyObservers({
          resourceCount: this.metrics.resourceCount,
          resourceLoadTime: this.metrics.resourceLoadTime,
        });
      });
      this.resourceObserver.observe({ entryTypes: ['resource'] });

      // Paint timing
      this.paintObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            this.metrics.firstContentfulPaint = entry.startTime;
            this.notifyObservers({ firstContentfulPaint: this.metrics.firstContentfulPaint });
          }
          if (entry.name === 'largest-contentful-paint') {
            this.metrics.largestContentfulPaint = entry.startTime;
            this.notifyObservers({ largestContentfulPaint: this.metrics.largestContentfulPaint });
          }
        });
      });
      this.paintObserver.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });

      // Layout shift
      this.layoutShiftObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        this.metrics.cumulativeLayoutShift = entries.reduce((total, entry: any) => {
          return total + (entry.value || 0);
        }, 0);
        this.notifyObservers({ cumulativeLayoutShift: this.metrics.cumulativeLayoutShift });
      });
      this.layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
    }
  }

  /**
   * Disconnect all observers
   */
  private disconnectObservers(): void {
    if (this.resourceObserver) {
      this.resourceObserver.disconnect();
      this.resourceObserver = null;
    }
    if (this.paintObserver) {
      this.paintObserver.disconnect();
      this.paintObserver = null;
    }
    if (this.layoutShiftObserver) {
      this.layoutShiftObserver.disconnect();
      this.layoutShiftObserver = null;
    }
  }

  /**
   * Track bundle size
   */
  private trackBundleSize(): void {
    // Estimate bundle size from performance entries
    const resources = performance.getEntriesByType('resource');
    const scriptResources = resources.filter(entry => 
      entry.name.includes('.js') || entry.name.includes('chunk')
    );
    
    this.metrics.bundleSize = scriptResources.reduce((total, entry) => {
      return total + (entry.transferSize || 0);
    }, 0);
    
    this.notifyObservers({ bundleSize: this.metrics.bundleSize });
  }

  /**
   * Track memory usage
   */
  private trackMemoryUsage(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      this.metrics.memoryUsage = memory.usedJSHeapSize;
      this.notifyObservers({ memoryUsage: this.metrics.memoryUsage });
    }
  }

  /**
   * Notify all observers
   */
  private notifyObservers(metrics: Partial<PerformanceMetrics>): void {
    this.observers.forEach(observer => {
      try {
        observer.onMetricUpdate(metrics);
      } catch (error) {
        observer.onError(error as Error);
      }
    });
  }

  /**
   * Generate performance report
   */
  generateReport(): string {
    const metrics = this.getMetrics();
    const report = {
      timestamp: new Date().toISOString(),
      metrics,
      recommendations: this.generateRecommendations(metrics),
    };
    
    return JSON.stringify(report, null, 2);
  }

  /**
   * Generate performance recommendations
   */
  private generateRecommendations(metrics: PerformanceMetrics): string[] {
    const recommendations: string[] = [];
    
    if (metrics.bundleSize > 500000) { // 500KB
      recommendations.push('Consider code splitting to reduce bundle size');
    }
    
    if (metrics.largestContentfulPaint > 2500) { // 2.5s
      recommendations.push('Optimize Largest Contentful Paint for better user experience');
    }
    
    if (metrics.cumulativeLayoutShift > 0.1) {
      recommendations.push('Reduce Cumulative Layout Shift by fixing layout shifts');
    }
    
    if (metrics.memoryUsage > 50000000) { // 50MB
      recommendations.push('Monitor memory usage and optimize memory leaks');
    }
    
    return recommendations;
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// Auto-start monitoring in development
if (process.env.NODE_ENV === 'development') {
  performanceMonitor.start();
}

export default performanceMonitor;

// React performance hooks
export const usePerformanceTracking = (componentName: string) => {
  const startTime = React.useRef(performance.now());
  
  React.useEffect(() => {
    const endTime = performance.now();
    const renderTime = endTime - startTime.current;
    performanceMonitor.trackComponentRender(componentName, renderTime);
  });
};

// Performance decorator for class components
export const withPerformanceTracking = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
) => {
  const displayName = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component';
  
  const WithPerformanceTracking = React.forwardRef<any, P>((props, ref) => {
    usePerformanceTracking(displayName);
    return <WrappedComponent {...props} ref={ref} />;
  });
  
  WithPerformanceTracking.displayName = `withPerformanceTracking(${displayName})`;
  return WithPerformanceTracking;
};
