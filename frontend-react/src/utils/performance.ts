// Performance Monitoring Utilities

export interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
  domLoad: number; // DOM Content Loaded
  windowLoad: number; // Window Load
  jsHeapSize: number; // JavaScript Heap Size
  jsHeapUsed: number; // JavaScript Heap Used
}

export interface NavigationTiming {
  navigationStart: number;
  fetchStart: number;
  domainLookupStart: number;
  domainLookupEnd: number;
  connectStart: number;
  connectEnd: number;
  requestStart: number;
  responseStart: number;
  responseEnd: number;
  domLoading: number;
  domInteractive: number;
  domContentLoadedEventStart: number;
  domContentLoadedEventEnd: number;
  domComplete: number;
  loadEventStart: number;
  loadEventEnd: number;
}

class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private observers: PerformanceObserver[] = [];
  private isInitialized = false;

  init() {
    if (this.isInitialized) return;

    this.setupWebVitals();
    this.setupMemoryMonitoring();
    this.setupNavigationTiming();
    this.setupErrorTracking();

    this.isInitialized = true;
    console.log("Performance Monitor initialized");
  }

  private setupWebVitals() {
    // First Contentful Paint
    if ("PerformanceObserver" in window) {
      try {
        const fcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find(
            (entry) => entry.name === "first-contentful-paint",
          );
          if (fcpEntry) {
            this.metrics.fcp = fcpEntry.startTime;
            this.logMetric("FCP", fcpEntry.startTime);
          }
        });
        fcpObserver.observe({ entryTypes: ["paint"] });
        this.observers.push(fcpObserver);
      } catch (e) {
        console.warn("FCP observer failed:", e);
      }

      // Largest Contentful Paint
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (lastEntry) {
            this.metrics.lcp = lastEntry.startTime;
            this.logMetric("LCP", lastEntry.startTime);
          }
        });
        lcpObserver.observe({ entryTypes: ["largest-contentful-paint"] });
        this.observers.push(lcpObserver);
      } catch (e) {
        console.warn("LCP observer failed:", e);
      }

      // First Input Delay
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry) => {
            const fidEntry = entry as any;
            this.metrics.fid = fidEntry.processingStart - fidEntry.startTime;
            this.logMetric("FID", this.metrics.fid);
          });
        });
        fidObserver.observe({ entryTypes: ["first-input"] });
        this.observers.push(fidObserver);
      } catch (e) {
        console.warn("FID observer failed:", e);
      }

      // Cumulative Layout Shift
      try {
        const clsObserver = new PerformanceObserver((list) => {
          let clsValue = 0;
          const entries = list.getEntries();
          entries.forEach((entry) => {
            const clsEntry = entry as any;
            if (!clsEntry.hadRecentInput) {
              clsValue += clsEntry.value;
            }
          });
          this.metrics.cls = clsValue;
          this.logMetric("CLS", clsValue);
        });
        clsObserver.observe({ entryTypes: ["layout-shift"] });
        this.observers.push(clsObserver);
      } catch (e) {
        console.warn("CLS observer failed:", e);
      }
    }
  }

  private setupMemoryMonitoring() {
    if ("memory" in performance) {
      const updateMemoryMetrics = () => {
        const memory = (performance as any).memory;
        this.metrics.jsHeapSize = memory.usedJSHeapSize;
        this.metrics.jsHeapUsed = memory.usedJSHeapSize;

        // Log memory usage every 30 seconds
        this.logMetric("Memory", memory.usedJSHeapSize / 1024 / 1024, "MB");
      };

      updateMemoryMetrics();
      setInterval(updateMemoryMetrics, 30000);
    }
  }

  private setupNavigationTiming() {
    window.addEventListener("load", () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType(
          "navigation",
        )[0] as PerformanceNavigationTiming;
        if (navigation) {
          this.metrics.ttfb =
            navigation.responseStart - navigation.requestStart;
          this.metrics.domLoad =
            navigation.domContentLoadedEventEnd -
            (navigation as any).navigationStart;
          this.metrics.windowLoad =
            navigation.loadEventEnd - (navigation as any).navigationStart;

          this.logMetric("TTFB", this.metrics.ttfb);
          this.logMetric("DOM Load", this.metrics.domLoad);
          this.logMetric("Window Load", this.metrics.windowLoad);
        }
      }, 0);
    });
  }

  private setupErrorTracking() {
    window.addEventListener("error", (event) => {
      this.logError("JavaScript Error", {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack,
      });
    });

    window.addEventListener("unhandledrejection", (event) => {
      this.logError("Unhandled Promise Rejection", {
        reason: event.reason,
        promise: event.promise,
      });
    });
  }

  private logMetric(name: string, value: number, unit = "ms") {
    const metric = {
      name,
      value,
      unit,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };

    console.log(`📊 ${name}: ${value}${unit}`);

    // Store in localStorage for debugging
    try {
      const existingMetrics = JSON.parse(
        localStorage.getItem("app-metrics") || "[]",
      );
      existingMetrics.push(metric);
      localStorage.setItem(
        "app-metrics",
        JSON.stringify(existingMetrics.slice(-50)),
      ); // Keep last 50 metrics
    } catch (e) {
      console.warn("Could not save metric to localStorage:", e);
    }

    // Send to analytics service
    this.sendToAnalytics("metric", metric);
  }

  // Make logError public
  logError(type: string, data: any) {
    const error = {
      type,
      data,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };

    console.error(`🚨 ${type}:`, data);

    // Send to analytics service
    this.sendToAnalytics("error", error);
  }

  private sendToAnalytics(type: "metric" | "error", data: any) {
    // In a real app, you would send this to your analytics service
    // Example: Google Analytics, Mixpanel, etc.

    if (process.env.NODE_ENV === "development") {
      console.log(`📡 Sending ${type} to analytics:`, data);
    }

    // Simulate sending to analytics
    setTimeout(() => {
      // This would be your actual analytics call
      // gtag('event', 'performance_metric', data);
    }, 0);
  }

  getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }

  getNavigationTiming(): NavigationTiming | null {
    const navigation = performance.getEntriesByType(
      "navigation",
    )[0] as PerformanceNavigationTiming;
    if (!navigation) return null;

    return {
      navigationStart: (navigation as any).navigationStart,
      fetchStart: navigation.fetchStart,
      domainLookupStart: navigation.domainLookupStart,
      domainLookupEnd: navigation.domainLookupEnd,
      connectStart: navigation.connectStart,
      connectEnd: navigation.connectEnd,
      requestStart: navigation.requestStart,
      responseStart: navigation.responseStart,
      responseEnd: navigation.responseEnd,
      domLoading: (navigation as any).domLoading,
      domInteractive: navigation.domInteractive,
      domContentLoadedEventStart: navigation.domContentLoadedEventStart,
      domContentLoadedEventEnd: navigation.domContentLoadedEventEnd,
      domComplete: navigation.domComplete,
      loadEventStart: navigation.loadEventStart,
      loadEventEnd: navigation.loadEventEnd,
    };
  }

  measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    return fn().finally(() => {
      const duration = performance.now() - start;
      this.logMetric(name, duration);
    });
  }

  measureSync<T>(name: string, fn: () => T): T {
    const start = performance.now();
    try {
      return fn();
    } finally {
      const duration = performance.now() - start;
      this.logMetric(name, duration);
    }
  }

  mark(name: string) {
    performance.mark(name);
  }

  measure(name: string, startMark: string, endMark: string) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      if (measure) {
        this.logMetric(name, measure.duration);
      }
    } catch (e) {
      console.warn(`Could not measure ${name}:`, e);
    }
  }

  disconnect() {
    this.observers.forEach((observer) => observer.disconnect());
    this.observers = [];
    this.isInitialized = false;
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Auto-initialize in development
if (process.env.NODE_ENV === "development") {
  performanceMonitor.init();
}

export default performanceMonitor;
