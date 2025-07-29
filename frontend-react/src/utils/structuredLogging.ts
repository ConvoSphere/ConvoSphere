/**
 * Structured Logging Service for the Frontend
 * 
 * This module provides structured logging with OpenTelemetry integration,
 * error tracking, and performance monitoring for the React application.
 */

export interface LogLevel {
  DEBUG: 'debug';
  INFO: 'info';
  WARN: 'warn';
  ERROR: 'error';
}

export interface LogEvent {
  timestamp: string;
  level: keyof LogLevel;
  message: string;
  eventType?: string;
  userId?: string;
  sessionId?: string;
  requestId?: string;
  endpoint?: string;
  method?: string;
  statusCode?: number;
  duration?: number;
  error?: string;
  traceId?: string;
  spanId?: string;
  extra?: Record<string, any>;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  unit?: string;
  tags?: Record<string, string>;
}

export interface ErrorInfo {
  code?: string;
  message: string;
  stack?: string;
  context?: string;
  userAction?: string;
}

class StructuredLogger {
  private sessionId: string;
  private userId?: string;
  private isInitialized = false;
  private logBuffer: LogEvent[] = [];
  private maxBufferSize = 100;
  private flushInterval = 30000; // 30 seconds
  private flushTimer?: NodeJS.Timeout;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.initialize();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initialize(): void {
    if (this.isInitialized) return;

    // Setup periodic flush
    this.flushTimer = setInterval(() => {
      this.flushLogs();
    }, this.flushInterval);

    // Setup error handlers
    this.setupErrorHandlers();

    // Setup performance monitoring
    this.setupPerformanceMonitoring();

    this.isInitialized = true;
    this.log('info', 'Structured Logger initialized', { eventType: 'logger_init' });
  }

  private setupErrorHandlers(): void {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.log('error', 'Global error caught', {
        eventType: 'global_error',
        error: event.error?.message || event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.log('error', 'Unhandled promise rejection', {
        eventType: 'unhandled_rejection',
        error: event.reason?.message || String(event.reason),
      });
    });
  }

  private setupPerformanceMonitoring(): void {
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      // First Contentful Paint
      try {
        const fcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
          if (fcpEntry) {
            this.logPerformanceMetric('FCP', fcpEntry.startTime, 'ms');
          }
        });
        fcpObserver.observe({ entryTypes: ['paint'] });
      } catch (e) {
        this.log('warn', 'Failed to setup FCP observer', { error: String(e) });
      }

      // Largest Contentful Paint
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (lastEntry) {
            this.logPerformanceMetric('LCP', lastEntry.startTime, 'ms');
          }
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        this.log('warn', 'Failed to setup LCP observer', { error: String(e) });
      }

      // First Input Delay
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            const fid = entry.processingStart - entry.startTime;
            this.logPerformanceMetric('FID', fid, 'ms');
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        this.log('warn', 'Failed to setup FID observer', { error: String(e) });
      }
    }
  }

  private getTraceContext(): { traceId?: string; spanId?: string } {
    // Try to get trace context from OpenTelemetry if available
    if (typeof window !== 'undefined' && (window as any).otel) {
      const tracer = (window as any).otel.trace.getTracer('frontend');
      const span = tracer.getCurrentSpan();
      if (span) {
        const context = span.getSpanContext();
        return {
          traceId: context.traceId,
          spanId: context.spanId,
        };
      }
    }
    return {};
  }

  private createLogEvent(
    level: keyof LogLevel,
    message: string,
    extra?: Record<string, any>
  ): LogEvent {
    const { traceId, spanId } = this.getTraceContext();
    
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      sessionId: this.sessionId,
      userId: this.userId,
      traceId,
      spanId,
      ...extra,
    };
  }

  private addToBuffer(event: LogEvent): void {
    this.logBuffer.push(event);
    
    // Flush if buffer is full
    if (this.logBuffer.length >= this.maxBufferSize) {
      this.flushLogs();
    }
  }

  private async flushLogs(): Promise<void> {
    if (this.logBuffer.length === 0) return;

    const logsToFlush = [...this.logBuffer];
    this.logBuffer = [];

    try {
      // Send logs to backend
      await this.sendLogsToBackend(logsToFlush);
    } catch (error) {
      // Fallback to console if backend is unavailable
      console.warn('Failed to send logs to backend, falling back to console:', error);
      logsToFlush.forEach(event => {
        console.log(`[${event.level.toUpperCase()}] ${event.message}`, event);
      });
    }
  }

  private async sendLogsToBackend(logs: LogEvent[]): Promise<void> {
    const response = await fetch('/api/v1/logs/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ logs }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send logs: ${response.status}`);
    }
  }

  public setUserId(userId: string): void {
    this.userId = userId;
    this.log('info', 'User ID set', { eventType: 'user_set', userId });
  }

  public log(
    level: keyof LogLevel,
    message: string,
    extra?: Record<string, any>
  ): void {
    const event = this.createLogEvent(level, message, extra);
    
    // Add to buffer for batch processing
    this.addToBuffer(event);
    
    // Also log to console in development
    if (process.env.NODE_ENV === 'development') {
      const consoleMethod = level === 'error' ? 'error' : 
                           level === 'warn' ? 'warn' : 
                           level === 'info' ? 'info' : 'log';
      console[consoleMethod](`[${level.toUpperCase()}] ${message}`, extra);
    }
  }

  public logApiRequest(
    method: string,
    endpoint: string,
    statusCode: number,
    duration: number,
    requestId?: string,
    requestSize?: number,
    responseSize?: number,
    error?: string
  ): void {
    this.log('info', `API Request: ${method} ${endpoint}`, {
      eventType: 'api_request',
      method,
      endpoint,
      statusCode,
      duration,
      requestId,
      requestSize,
      responseSize,
      error,
    });
  }

  public logDatabaseQuery(
    queryType: string,
    tableName: string,
    duration: number,
    rowsAffected?: number,
    error?: string
  ): void {
    this.log('debug', `Database Query: ${queryType} on ${tableName}`, {
      eventType: 'database_query',
      queryType,
      tableName,
      duration,
      rowsAffected,
      error,
    });
  }

  public logSecurityEvent(
    eventType: string,
    description: string,
    userId?: string,
    ipAddress?: string,
    severity: keyof LogLevel = 'info',
    details?: Record<string, any>
  ): void {
    this.log(severity, `Security Event: ${description}`, {
      eventType: 'security_event',
      securityEventType: eventType,
      userId,
      ipAddress,
      details,
    });
  }

  public logPerformanceMetric(
    name: string,
    value: number,
    unit?: string,
    tags?: Record<string, string>
  ): void {
    this.log('info', `Performance Metric: ${name}`, {
      eventType: 'performance_metric',
      metricName: name,
      value,
      unit,
      tags,
    });
  }

  public logError(
    error: Error | string,
    context?: string,
    userAction?: string
  ): void {
    const errorInfo: ErrorInfo = {
      message: typeof error === 'string' ? error : error.message,
      stack: typeof error === 'string' ? undefined : error.stack,
      context,
      userAction,
    };

    this.log('error', `Error: ${errorInfo.message}`, {
      eventType: 'error',
      error: errorInfo,
    });
  }

  public async traceOperation<T>(
    operationName: string,
    operation: () => Promise<T>,
    attributes?: Record<string, any>
  ): Promise<T> {
    const startTime = performance.now();
    
    try {
      this.log('debug', `Operation started: ${operationName}`, {
        eventType: 'operation_start',
        operationName,
        ...attributes,
      });

      const result = await operation();
      
      const duration = performance.now() - startTime;
      this.log('debug', `Operation completed: ${operationName}`, {
        eventType: 'operation_success',
        operationName,
        duration,
        ...attributes,
      });

      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      this.log('error', `Operation failed: ${operationName}`, {
        eventType: 'operation_error',
        operationName,
        duration,
        error: error instanceof Error ? error.message : String(error),
        ...attributes,
      });
      throw error;
    }
  }

  public destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flushLogs();
  }
}

// Global logger instance
export const structuredLogger = new StructuredLogger();

// Convenience functions
export const log = (level: keyof LogLevel, message: string, extra?: Record<string, any>) => {
  structuredLogger.log(level, message, extra);
};

export const logApiRequest = (
  method: string,
  endpoint: string,
  statusCode: number,
  duration: number,
  requestId?: string,
  requestSize?: number,
  responseSize?: number,
  error?: string
) => {
  structuredLogger.logApiRequest(method, endpoint, statusCode, duration, requestId, requestSize, responseSize, error);
};

export const logError = (error: Error | string, context?: string, userAction?: string) => {
  structuredLogger.logError(error, context, userAction);
};

export const logPerformanceMetric = (name: string, value: number, unit?: string, tags?: Record<string, string>) => {
  structuredLogger.logPerformanceMetric(name, value, unit, tags);
};

export const traceOperation = <T>(
  operationName: string,
  operation: () => Promise<T>,
  attributes?: Record<string, any>
) => {
  return structuredLogger.traceOperation(operationName, operation, attributes);
};

export const setUserId = (userId: string) => {
  structuredLogger.setUserId(userId);
};

// Cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    structuredLogger.destroy();
  });
}